#!/usr/bin/env python
"""Find the KNEE of a training-loss curve: where fast descent turns into slow grind.

Used to decide when a curriculum stage has learned the STRUCTURE of its corpus and is
starting to merely memorize it -- the point at which its weights are the most transferable
warm start for the next stage.

Method, and why not something fancier: training loss is noisy at the monitor cadence, so
the curve is first binned and MEDIANED (a mean lets one spike move a slope). Slope is then
measured per 10k steps between consecutive bins and smoothed again. The knee is the first
bin where |slope| has fallen below --frac of the post-warmup PEAK |slope| and STAYS there
for --persist consecutive bins; requiring persistence is what stops a single flat stretch
in a still-descending curve from being called a knee. --skip discards the initial
init-transient, whose slope is enormous and would otherwise set an unreachable peak.

usage: exp/knee.py log/exp.pp1_bvocab_e10s [--bin 2000] [--frac 0.25] [--persist 3]
                                           [--steps-per-epoch 375]
"""
import argparse, re
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('log')
ap.add_argument('--bin', type=int, default=2000)
ap.add_argument('--skip', type=int, default=2000, help='ignore steps below this (init transient)')
ap.add_argument('--frac', type=float, default=0.25, help='knee when |slope| < frac * peak |slope|')
ap.add_argument('--persist', type=int, default=3, help='bins it must stay below to count')
ap.add_argument('--smooth', type=int, default=3, help='bins in the slope-smoothing window')
ap.add_argument('--steps-per-epoch', type=float, default=0.0)
a = ap.parse_args()

pat = re.compile(r'^STEP\s+(\d+).*?loss\s+([\d.]+)')
S, L = [], []
for line in open(a.log):
    m = pat.match(line)
    if m:
        S.append(int(m.group(1))); L.append(float(m.group(2)))
S, L = np.array(S), np.array(L)
keep = S >= a.skip
S, L = S[keep], L[keep]
if len(S) < 10:
    raise SystemExit(f'{a.log}: only {len(S)} points after --skip {a.skip}; too early to judge')

edges = np.arange(S.min(), S.max() + a.bin, a.bin)
idx   = np.digitize(S, edges) - 1
bs, bl = [], []
for b in range(idx.max() + 1):
    sel = idx == b
    if sel.sum() >= 3:
        bs.append(S[sel].mean()); bl.append(np.median(L[sel]))
bs, bl = np.array(bs), np.array(bl)
if len(bs) < 5:
    raise SystemExit(f'{a.log}: only {len(bs)} bins; run longer or lower --bin')

slope = np.diff(bl) / (np.diff(bs) / 10000.0)          # loss per 10k steps
k = max(1, a.smooth)
sm = np.convolve(slope, np.ones(k) / k, mode='valid')
sstep = bs[1:][k - 1:]

peak = np.abs(sm).max(); pk_at = sstep[np.abs(sm).argmax()]
thr  = a.frac * peak
print(f'{a.log}')
print(f'  points {len(S):,}  bins {len(bs)}  span {S.min():,}-{S.max():,}')
print(f'  peak descent {peak:.4f} loss/10k steps at step {pk_at:,.0f}   knee threshold {thr:.4f}')
ep = (lambda s: f'{s/a.steps_per_epoch:8.0f}') if a.steps_per_epoch else (lambda s: '       -')
print(f'\n{"step":>10} {"epoch":>8} {"loss":>8} {"loss/10k":>10}  {"% of peak":>9}')
for s, l, v in zip(sstep, bl[1:][k - 1:], sm):
    print(f'{s:10,.0f} {ep(s)} {l:8.4f} {v:10.4f}  {100*abs(v)/peak:8.1f}%')

below = np.abs(sm) < thr
knee = None
for i in range(len(below) - a.persist + 1):
    if below[i:i + a.persist].all():
        knee = sstep[i]; break
print()
if knee is None:
    cur = abs(sm[-1]) / peak
    print(f'NO KNEE YET. Current descent is {100*cur:.0f}% of peak '
          f'(knee needs <{100*a.frac:.0f}% for {a.persist} consecutive bins).')
    print('The curve is still in its fast phase; stopping here would cut it short.')
else:
    print(f'KNEE at step {knee:,.0f}' + (f'  (epoch ~{knee/a.steps_per_epoch:,.0f})' if a.steps_per_epoch else ''))
