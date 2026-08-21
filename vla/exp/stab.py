#!/usr/bin/env python
"""Stabilization summary: per-run detail plus per-arm replicate scoring.

settle = first step after which dff_max stays under 100 for the rest of the run
         (the healthy reference sits at dff_max ~25; the bad basin runs 1e2-1e5)
"""
import glob, os, re, sys
import numpy as np

ARMS = {'pA': 'adamw (0.9,0.9) lr1e-3  [baseline]',
        'pB': 'adamw --beta2 0.999',
        'pC': 'adamw + warmup 300',
        'pD': 'no --tap',
        'pE': 'sgd+nesterov (lr ladder)'}

def read(p):
    st, ls, dmx, dsd, gr = [], [], [], [], []
    for ln in open(p, errors='ignore'):
        f = ln.split()
        if f and f[0] == 'STEP':
            try:
                st.append(int(f[1])); ls.append(float(f[6])); gr.append(float(f[8]))
                dsd.append(float(f[14])); dmx.append(float(f[16]))
            except (ValueError, IndexError): pass
    if not st: return None
    return tuple(map(np.array, (st, ls, dmx, dsd, gr)))

pats = sys.argv[1:] or ['p[A-E]*']
names = sorted({os.path.basename(p)[4:] for q in pats for p in glob.glob(f'log/exp.{q}')
                if not p.endswith(('.out', '.mem'))})
rows = []
for m in names:
    r = read(f'log/exp.{m}')
    if r is None: continue
    st, ls, dmx, dsd, gr = r
    settle = next((int(st[i]) for i in range(len(st)) if (dmx[i:] < 100).all()), None)
    late = st >= st[-1] * 0.8
    rows.append(dict(m=m, arm=m[:2], step=int(st[-1]), loss=float(ls[late].mean()),
                     settle=settle, dmax=float(dmx[late].max()), dsd=float(dsd[late].mean()),
                     grad=float(gr[late].mean())))

print(f'{"run":6} {"step":>5} {"tail_loss":>10} {"settle":>7} {"dff_max":>9} {"dff_std":>8} {"grad":>8}')
print('-' * 58)
for r in sorted(rows, key=lambda r: (r['arm'], r['m'])):
    print(f'{r["m"]:6} {r["step"]:5d} {r["loss"]:10.4f} '
          f'{("never" if r["settle"] is None else r["settle"]):>7} '
          f'{r["dmax"]:9.1f} {r["dsd"]:8.2f} {r["grad"]:8.3f}')

print(f'\n{"arm":6} {"n":>2} {"in_basin":>9} {"mean_loss":>10} {"best":>8} {"worst":>8}  description')
print('-' * 90)
for a in sorted({r['arm'] for r in rows}):
    g = [r for r in rows if r['arm'] == a]
    # basin classifier: the two known trajectories separate cleanly by tail loss
    # (healthy ~5.42 at step 1200, stalled ~6.29), which is a more direct read than settle
    ok = sum(1 for r in g if r['loss'] < 5.9)
    L = [r['loss'] for r in g]
    print(f'{a:6} {len(g):2d} {f"{ok}/{len(g)}":>8} {np.mean(L):10.4f} {min(L):8.4f} '
          f'{max(L):8.4f}  {ARMS.get(a,"")}')
