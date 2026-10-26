#!/bin/bash
# CPU smoke test: build a tiny model, train it 30 steps on TinyStories (streamed), save, export it the way
# --push does (locally, nothing uploaded), load it back with --pretrained and generate.
# usage: tests/smoke.sh [python]      (needs network access to the Hugging Face hub)
set -euo pipefail
PY=${1:-python}
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
TINY="--context 7 --n_hidden 32 --c_context 32 --depth 2 --dec_width 32 --batch 4 --device cpu"
$PY vla.py $TINY --dataset tiny --streaming --workers 1 --run_steps 30 --monitor 10 \
    --save "$T/smoke.pt" --log "$T/log" > "$T/train.out" 2>&1 || { tail -20 "$T/train.out"; exit 1; }
grep -q '^STEP' "$T/log" || { echo 'FAIL: no STEP lines'; exit 1; }
test -f "$T/smoke.pt" || { echo 'FAIL: no checkpoint'; exit 1; }
$PY vla.py --load "$T/smoke.pt" --push --hub_repo - --push_dir "$T/export" --device cpu > "$T/push.out" 2>&1 \
    || { tail -20 "$T/push.out"; exit 1; }
out=$($PY vla.py --pretrained "$T/export" --generate --n 20 --prompt 'Once upon a time' --device cpu \
      --log /dev/null 2>/dev/null | tail -1)
[ -n "$out" ] || { echo 'FAIL: no generation'; exit 1; }
echo "generated: $out"
echo PASS
