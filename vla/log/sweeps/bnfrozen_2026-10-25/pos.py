"""Loss by position in the document, per checkpoint, minus the first file's (paired by document).
usage: python pos.py base.jsonl a.jsonl b.jsonl ..."""
import json, sys
import numpy as np
runs = [[json.loads(l) for l in open(f)] for f in sys.argv[1:]]
names = [f.rsplit('/', 1)[-1].removesuffix('.jsonl') for f in sys.argv[1:]]
edges = [0, 4, 16, 64, 256, 1024, 2048]
rng = np.random.default_rng(0)
for kind in ('heldout', 'train'):
    docs = [[r for r in run if r['kind'] == kind] for run in runs]
    print(f'{kind}: {len(docs[0])} documents; nats/token by position (base {names[0]}; others as change vs base, +- s.e.)')
    print(f'{"position":>12} {"tokens":>7} ' + ' '.join(f'{n:>16}' for n in names))
    for lo, hi in zip(edges, edges[1:]):
        # per document: mean over its tokens in [lo, hi); documents shorter than lo drop out
        per = [np.array([np.mean(d['ce'][lo:hi]) for d in run if len(d['ce']) > lo]) for run in docs]
        if not len(per[0]):
            continue
        cols = [f'{per[0].mean():16.3f}']
        for p in per[1:]:
            dd = p - per[0]
            cols.append(f'{dd.mean():+9.3f} +-{dd.std() / len(dd) ** .5:.3f}')
        ntok = sum(min(len(d['ce']), hi) - lo for d in docs[0] if len(d['ce']) > lo)
        print(f'{lo:5d}-{hi:<6d} {ntok:7d} ' + ' '.join(cols))
    print()
