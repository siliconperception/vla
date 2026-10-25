"""Paired forgetting curve with age in TOKENS (steps x batch): each recorded training document scored before it was
read (pre) and after the run (now), minus the held-out change. usage: python pair_tokens.py pre.jsonl now.jsonl BATCH"""
import json, sys
import numpy as np
pre, now = ([json.loads(l) for l in open(f)] for f in sys.argv[1:3])
B, T = int(sys.argv[3]), now[0]['step']
held = np.array([a['nats'] - b['nats'] for a, b in zip(pre, now) if a['kind'] == 'heldout'])
tr = [((T - b['end']) * B, a['nats'] - b['nats']) for a, b in zip(pre, now) if a['kind'] == 'train']
print(f'batch {B}, pre step {pre[0]["step"]}, now step {T}; {len(tr)} training docs; held-out improvement '
      f'{held.mean():+.4f} +- {held.std() / len(held) ** .5:.4f}')
rng = np.random.default_rng(0)
edges = [0, 30_000, 100_000, 300_000, 10 ** 12]
for lo, hi in zip(edges, edges[1:]):
    d = np.array([x for a, x in tr if lo <= a < hi])
    if len(d) < 3:
        continue
    bs = [rng.choice(d, len(d)).mean() - rng.choice(held, len(held)).mean() for _ in range(2000)]
    print(f'age {lo / 1e3:5.0f}K-{hi / 1e3 if hi < 10 ** 12 else float("inf"):5.0f}K tokens  n {len(d):5d}  '
          f'memory {d.mean() - held.mean():+.4f} +- {np.std(bs):.4f}')
