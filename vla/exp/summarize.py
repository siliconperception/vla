#!/usr/bin/env python
"""Collect study results: training-loss tail + long-range memory metrics.

  tail   mean training loss over the last 15% of the run's monitor lines
  L_full held-out loss on 250-500 TinyStories validation docs, full document context
  exc@c  extra nats the model pays at a position where the DFF state has only c tokens
         of history, paired against the same position with full history (P=128 probe)
  horiz  smallest c at which that excess falls below 0.05 nats == effective memory horizon
"""
import glob, json, os, re, sys
import numpy as np

def tail_loss(path, frac=0.15):
    steps, loss, dstd = [], [], []
    for ln in open(path, errors='ignore'):
        m = re.match(r'STEP\s+(\d+).*loss\s+([\d.]+).*dff_std\s+([\d.naif-]+)', ln)
        if m:
            steps.append(int(m.group(1))); loss.append(float(m.group(2)))
            try: dstd.append(float(m.group(3)))
            except ValueError: dstd.append(float('nan'))
    if not steps: return None
    n = max(1, int(len(loss) * frac))
    # Two tail windows. Each monitor line is already a 20-step mean, so single-line noise is
    # ~0.06; averaging 10 lines gets SE to ~0.02 and 75 to ~0.007. The wide window is the
    # lower-variance estimate but sits ~0.04 high, since loss is still falling ~0.05-0.08
    # nats/1k steps and it averages 1500 steps back -- near-identical across configs, so it
    # shifts rows together rather than reordering them. slope is carried so a config that is
    # still descending cannot pass as a converged one.
    t10 = float(np.mean(loss[-10:]))
    slope = float(np.polyfit(steps[-n:], loss[-n:], 1)[0] * 1000) if n > 2 else float('nan')
    # breakthrough: first step whose 20-step mean loss drops under the corpus unigram
    # entropy (5.996 nats, TinyStories/pythia31m). Above that the model has learned nothing
    # a frequency table would not give for free; the crossing is sharp and is the honest
    # way to compare configs whose stacks organize at different rates.
    # Sustained crossing, not first touch: each monitor line is a 20-step mean carrying
    # ~+-0.05 of noise, so a bare threshold test fires on whichever line dips under first
    # and bounces back (sbase touched at 1180, bounced at 1200 and 1260, held from 1280).
    # That jitter is ~100 steps, the same size as the differences being measured.
    bt = next((steps[i] for i in range(len(loss))
               if all(l < 5.996 for l in loss[i:])), None)
    return dict(step=steps[-1], tail=float(np.mean(loss[-n:])), t10=t10, slope=slope,
                sd=float(np.std(loss[-n:])), dff_std=float(np.mean(dstd[-n:])), bt=bt)

def memjson(m):
    p = f'exp/mem.{m}.json'
    if not os.path.exists(p): return {}
    d = json.load(open(p)); out = {}
    P = d.get('periods', {}); pa = d.get('paired', {})
    if '0' in P:
        out['L_full'] = P['0']['loss']
        out['div'] = P['0'].get('diverged', 0)
    big = str(max((int(k) for k in pa), default=0))
    if big in pa:
        cur = np.array(pa[big]['curve']); n = np.array(pa[big]['n'])
        out['exc_mean'] = pa[big]['mean_excess']
        for c in (1, 4, 8, 16, 32, 64, 96):
            if c < len(cur) and n[c] > 0: out[f'e{c}'] = float(cur[c])
        ok = [c for c in range(1, len(cur)) if n[c] > 0 and cur[c] < 0.05]
        # horizon: first c past which the excess stays under 0.05
        h = None
        for c in range(1, len(cur)):
            if n[c] > 0 and all(cur[k] < 0.05 for k in range(c, len(cur)) if n[k] > 0):
                h = c; break
        out['horizon'] = h
    return out

mnems = sys.argv[1:] or sorted({os.path.basename(p)[4:] for p in glob.glob('log/exp.*')
                                if not p.endswith(('.out', '.mem'))})
rows = []
for m in mnems:
    p = f'log/exp.{m}'
    if not os.path.exists(p): continue
    t = tail_loss(p)
    if t: rows.append((m, t, memjson(m)))
rows.sort(key=lambda r: r[1]['tail'])

hdr = (f'{"mnem":7} {"step":>6} {"break":>6} {"tail":>7} {"mean10":>7} {"slope":>7} {"dffsd":>7} | {"L_full":>7} '
       f'{"excmean":>7} {"e1":>6} {"e4":>6} {"e8":>6} {"e16":>6} {"e32":>6} {"e64":>6} '
       f'{"e96":>6} {"horiz":>5}')
print(hdr); print('-' * len(hdr))
for m, t, x in rows:
    def g(k, f='{:6.3f}'):
        v = x.get(k)
        return f.format(v) if isinstance(v, (float, int)) and v is not None else ' ' * len(f.format(0))
    print(f'{m:7} {t["step"]:6d} {("-" if t["bt"] is None else t["bt"]):>6} '
          f'{t["tail"]:7.4f} {t["t10"]:7.4f} {t["slope"]:+7.3f} {t["dff_std"]:7.2f} | '
          f'{("DIVERGED" if x.get("div") else g("L_full","{:7.4f}")):>8} {g("exc_mean","{:7.3f}")} {g("e1")} {g("e4")} {g("e8")} '
          f'{g("e16")} {g("e32")} {g("e64")} {g("e96")} {g("horizon","{:5.0f}")}')
