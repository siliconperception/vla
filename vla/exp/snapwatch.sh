#!/bin/bash
# usage: exp/snapwatch.sh <mnemonic> [every]   (every defaults to 100000 steps)
# Watches checkpoint/<mnemonic>.pt and, each time it is rewritten at a step that is a multiple of
# <every>, copies it to checkpoint/<mnemonic>.step<N>.pt -- snapshots for paired forgetting curves
# (vla.py --doc_score at several steps). The step comes from the newest "EVAL step" line in
# log/exp.<mnemonic>, written just before the save at the same step. Exits when the trainer
# for <mnemonic> is gone.
M=$1; E=${2:-100000}
cd /proj/devices/vla
C=checkpoint/$M.pt
last=$(stat -c %Y $C 2>/dev/null || echo 0)
while pgrep -f "vla.py .*--save checkpoint/$M.pt" >/dev/null; do
  sleep 30
  now=$(stat -c %Y $C 2>/dev/null || echo 0)
  [ "$now" -gt "$last" ] || continue
  sleep 60                                  # let torch.save finish
  [ "$(stat -c %Y $C)" -eq "$now" ] || continue
  last=$now
  S=$(tail -c 3000000 log/exp.$M | grep '^EVAL step' | tail -1 | awk '{print $3}')
  [ -n "$S" ] && [ $((S % E)) -eq 0 ] && [ ! -f checkpoint/$M.step$S.pt ] &&
    cp $C checkpoint/$M.step$S.pt && echo "$(date '+%F %T') snapshot $M step $S"
done
echo "$(date '+%F %T') trainer for $M gone; snapwatch exits"
