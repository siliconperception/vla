#!/bin/bash
# GPU idle watchdog.  Emits one line per idle episode; a Monitor turns those into
# notifications.  Catches ANY cause of a stall -- a driver that exited early, a
# crashed trainer, a chain whose predecessor never signalled -- not just the
# edit-a-running-script bug that motivated it.
cd /proj/devices/vla
IDLE=0
while true; do
  if pgrep -f "^python (vla|exp/score|exp/reach|exp/gencheck|exp/memtest|exp/genstate)" > /dev/null; then
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
