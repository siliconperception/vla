#!/usr/bin/env python3
"""Is the checkpoint written at STEP `step` worth keeping?  exit 0 = healthy, 1 = blown,
2 = cannot tell yet (no STEP line at that step in the log).

    python3 exp/ckpt_health.py log/exp.<mnemonic> <step>

Readability is not health.  v111 (lr sqrt2) wrote its step-245000 checkpoint with a FINITE
loss of 17.27 and a dff_std of 1.4e7 -- the state had already exploded, the NaN only arrived
seven steps later -- and every longrun resume loaded that file and died within seconds.  So
the test is the STEP line the trainer logged AT the checkpoint's step, against the 50 lines
before it: loss and dff_std must be finite, loss at most 1.5x the trailing median and dff_std
at most 3x.  Ordinary jitter is a few percent of either; a blow-up is orders of magnitude
(v111: loss 3.5x, dff_std 2e7x; v115's lr jump: dff_std 6e7x), so the thresholds are not
delicate.  Fewer than 10 prior lines (the first checkpoint of a run) is too early to judge
and passes -- there is nothing older to fall back to anyway.  stdlib only, no torch: this
runs once a minute alongside the trainer."""
import math, sys

log, step = sys.argv[1], int(sys.argv[2])
try:
    lines = open(log).read().splitlines()
except OSError as e:
    print(f'ckpt_health: cannot read {log}: {e}')
    sys.exit(2)
rows = []
for l in lines:
    if not l.startswith('STEP'):
        continue
    p = l.split()
    s = int(p[1])
    if s > step:
        break
    try:
        rows.append((s, float(p[p.index('loss') + 1]), float(p[p.index('dff_std') + 1])))
    except ValueError:                      # 'nan' parses; anything stranger is a bad line
        rows.append((s, math.nan, math.nan))

if not rows or rows[-1][0] != step:
    print(f'ckpt_health: no STEP line at {step}')
    sys.exit(2)
_, loss, std = rows[-1]
prev = rows[-51:-1]
if not (math.isfinite(loss) and math.isfinite(std)):
    print(f'ckpt_health: step {step} non-finite (loss {loss}, dff_std {std})')
    sys.exit(1)
if len(prev) < 10:
    sys.exit(0)
med = lambda xs: sorted(xs)[len(xs) // 2]
ml, ms = med([r[1] for r in prev]), med([r[2] for r in prev])
if loss > 1.5 * ml:
    print(f'ckpt_health: step {step} loss {loss:.3f} > 1.5 x trailing median {ml:.3f}')
    sys.exit(1)
if std > 3.0 * ms:
    print(f'ckpt_health: step {step} dff_std {std:.4g} > 3 x trailing median {ms:.4g}')
    sys.exit(1)
sys.exit(0)
