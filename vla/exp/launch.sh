#!/bin/bash
# usage: launch.sh <driver.sh> [args...]
#
# Runs a FROZEN SNAPSHOT of the driver, never the file itself.
#
# Why: bash reads a script incrementally by byte offset.  Editing a running
# driver shifts every offset after the edit, and bash resumes at the shifted
# position -- it can skip inserted lines and re-run old ones.  On 2026-08-23 that
# silently ran the E31/E32/E33 block instead of the E37/E38 block I had just
# inserted, then reported COMPLETE and left the GPU idle for 90 minutes.
# With this wrapper, editing the source while a job runs is harmless: the running
# job is executing a copy, and the edit takes effect on the NEXT launch.
set -u
cd /proj/devices/vla
SRC=$1; shift
[ -f "$SRC" ] || { echo "launch: no such driver: $SRC" >&2; exit 1; }
SNAP=exp/.run/$(basename "$SRC" .sh).$(date +%Y%m%d-%H%M%S).sh
cp "$SRC" "$SNAP"; chmod +x "$SNAP"
echo "launch: running frozen snapshot $SNAP (source $SRC may be edited freely)"
exec "$SNAP" "$@"
