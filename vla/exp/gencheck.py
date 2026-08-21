#!/usr/bin/env python
"""Free-running generation health.

Held-out cross-entropy is teacher-forced: the model is fed ground-truth tokens every step and
never has to survive its own output. Free-running generation is a different dynamical system,
and a recurrent model can score well on the first while having a degenerate attractor in the
second -- which is what wfix236 developed between 40K and 50K. So generation health needs its
own metric rather than a glance at one sample.

  cycle  strongest periodic self-similarity over the last half of the sample, periods 1..8.
         1.00 = perfectly locked into a repeating cycle; healthy text is ~0.05-0.25.
  uniq   distinct tokens / total. Healthy text is high; a collapsed sample is near zero.
"""
import os, subprocess, sys, re, collections
import numpy as np

ck, n, reps = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 80, \
              int(sys.argv[3]) if len(sys.argv) > 3 else 3
cyc, unq, texts = [], [], []
for _ in range(reps):
    # cwd is pinned: vla.py resolves --load and its dataset paths relative to the repo root,
    # and the caller may invoke this from anywhere.
    r = subprocess.run([sys.executable, 'vla.py', '--generate',
                        '--load', ck, '--n', str(n), '--temperature', '1.0',
                        '--log', os.devnull], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.abspath(__file__)) + '/..',
                       # spawning python from a process that already loaded numpy/MKL trips
                       # "MKL_THREADING_LAYER=INTEL is incompatible with libgomp"; the child
                       # needs the GNU layer or it exits rc=1 with no stdout
                       env={**os.environ, 'MKL_THREADING_LAYER': 'GNU'})
    out = r.stdout
    if not out.strip():
        sys.stderr.write(f'gencheck: no stdout (rc={r.returncode}) {r.stderr[-200:]}\n')
    m = [l for l in out.split('\n') if l.startswith('<STX>')]
    if not m:
        continue
    t = m[0]
    texts.append(t)
    # character-level is enough to catch a locked cycle and needs no tokenizer
    s = t[5:]
    half = s[len(s) // 2:]
    best = 0.0
    for p in range(1, 9):
        if len(half) > p:
            match = sum(1 for i in range(p, len(half)) if half[i] == half[i - p])
            best = max(best, match / (len(half) - p))
    cyc.append(best)
    unq.append(len(set(s)) / max(len(s), 1))
if cyc:
    print(f'   gen health: cycle {np.mean(cyc):.2f} (max {max(cyc):.2f})  '
          f'uniq {np.mean(unq):.2f}  n={len(cyc)}'
          + ('   *** DEGENERATE ***' if np.mean(cyc) > 0.6 else ''))
    print(f'   sample: {texts[0][:200]}')
else:
    print('   gen health: no output')
