"""Paired forgetting curve: each recorded training document scored before it was read (pre) and now,
minus the same change on held-out documents. usage: python pair.py score_pre.jsonl score_now.jsonl"""
import json, sys
import numpy as np
pre, now = ([json.loads(l) for l in open(f)] for f in sys.argv[1:3])
T = now[0]['step']
held = np.array([a['nats'] - b['nats'] for a, b in zip(pre, now) if a['kind'] == 'heldout'])
tr = [(T - b['end'], a['nats'] - b['nats'], a['nats']) for a, b in zip(pre, now) if a['kind'] == 'train']
print(f'pre step {pre[0]["step"]}, now step {T}; held-out improvement {held.mean():+.4f} +- {held.std() / len(held) ** .5:.4f} '
      f'(n {len(held)}); memory = training doc improvement - held-out improvement, nats/token')
rng = np.random.default_rng(0)
edges = [0, 10_000, 30_000, 100_000, 300_000, 10 ** 9]
for lo, hi in zip(edges, edges[1:]):
    d = np.array([x for a, x, _ in tr if lo <= a < hi])
    if not len(d):
        continue
    m = d - held.mean()
    bs = [rng.choice(d, len(d)).mean() - rng.choice(held, len(held)).mean() for _ in range(2000)]
    ages = [a for a, _, _ in tr if lo <= a < hi]
    print(f'age {lo // 1000:4d}K-{min(hi, T) // 1000 if hi < 10 ** 9 else "":>4}{"K" if hi < 10 ** 9 else "+  "} n {len(d):4d} '
          f'mean age {np.mean(ages) / 1000:6.1f}K  memory {m.mean():+.4f} +- {np.std(bs):.4f}')
