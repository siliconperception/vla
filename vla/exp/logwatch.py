"""Surprise digest of a run's log: what changed since the last look.

usage: python exp/logwatch.py RUN [--since STEP] [--mark] [--lineage] [--quote N]

Reads log/exp.RUN (this launch only, i.e. after its last ARGS line, unless --lineage) and prints
  1. metrics: every numeric field of every metric line (STEP, EVAL <corpus>, EVALH, EVALL, EVALM,
     GENSCORE, ...), the new values against the earlier ones in a rolling median +- MAD; flags
     single-value outliers (|z| >= 3), shifts of the new median (|z| >= 3 on the median), and run
     records;
  2. GEN text: features of the new samples against the earlier ones (pronoun person, questions,
     dialogue, boilerplate, lists, repetition), the topic words that rose most, and the best,
     worst and a random sample quoted.
"New" means steps after --since, else after the step stored by the last --mark (log/notes/RUN.watch),
else the last 50K steps. --mark stores the latest step so the next digest starts there."""
import argparse, collections, json, math, os, random, re
from datetime import datetime

ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--since', type=int, default=None)
ap.add_argument('--mark', action='store_true')
ap.add_argument('--lineage', action='store_true', help='read the whole file (earlier launches too)')
ap.add_argument('--quote', type=int, default=400, help='characters quoted per sample')
ap.add_argument('--base', type=int, default=30, help='earlier values in the baseline window')
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

lines = open(f'log/exp.{a.run}', errors='replace').read().split('\n')
if not a.lineage:
    last = max((i for i, l in enumerate(lines) if l.startswith('ARGS ')), default=0)
    lines = lines[last:]

STATE = f'log/notes/{a.run}.watch'
NUM = re.compile(r'([A-Za-z_][\w/~-]*)\s+([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)*)(%|M|s)?(?=\s|$|,|\))')
SKIP = {'step', 'wall', 'docs', 'streams', 'tokens', 'samples', 'nrun', 'ppl', 'lr', 'n', 'ex_t', 'ep_t', 'stories', 'prompts', 'rows'}
SKIP_KINDS = {'GENV', 'GENV-deaf', 'GENV-blind', 'GENW', 'REF', 'INFO', 'TEXT', 'EVALR', 'EVALI'}  # EVALR/EVALI: per-band/per-pair fields
STEP_RE = re.compile(r'^(\S+)\s+(?:step\s+)?(\d+)\b')

series = collections.defaultdict(list)        # (line kind, field) -> [(step, value)]
gens, scores, walls = {}, {}, []
for l in lines:
    m = STEP_RE.match(l)
    if not m:
        continue
    kind, step = m.group(1), int(m.group(2))
    rest = l[m.end():]
    if kind == 'GEN':
        gens[step] = rest.split(':', 1)[1].strip() if ':' in rest else rest
        continue
    if kind in SKIP_KINDS:
        continue
    if kind == 'STEP':
        w = re.search(r'wall (\S+ \S+)', rest)
        if w:
            walls.append((step, datetime.fromisoformat(w.group(1))))
    if kind == 'EVAL':
        c = re.search(r'corpus (\S+)', rest)
        if not c or '~' in c.group(1):
            continue                              # weight-EMA copies log as <corpus>~emaNK
        kind = f'EVAL {c.group(1)}'
    for sec in rest.split('|'):
        sec = sec.strip()
        lead = re.match(r'([a-z]\w*) n\d+ ', sec)  # EVALM: "blimp n1005 acc ..." -> blimp.acc
        pre = lead.group(1) + '.' if lead else ''
        for k, v, u in NUM.findall(sec):
            if k in SKIP or k.startswith('nats/'):
                continue
            vs = [float(x) for x in v.split('/')]
            if len(vs) > 1:                        # EVALL fluency windows a/b/c/d/e
                series[(kind, pre + k + '.first')].append((step, vs[0]))
                series[(kind, pre + k + '.last')].append((step, vs[-1]))
            else:
                series[(kind, pre + k)].append((step, vs[0]))
    if kind == 'GENSCORE':
        f = re.search(r'fluency (-?\d+)%', rest)
        if f:
            scores[step] = int(f.group(1))

steps = [s for v in series.values() for s, _ in v]
if not steps:
    raise SystemExit(f'no metric lines in log/exp.{a.run}')
top = max(steps)
since = a.since
if since is None and os.path.exists(STATE):
    since = json.load(open(STATE))['step']
if since is None:
    since = top - 50000
print(f'# logwatch {a.run}: steps {since + 1} .. {top}' + ('' if a.lineage else ' (this launch)'))
if len(walls) > 1:
    new_w = [x for x in walls if x[0] > since] or walls[-2:]
    w0, w1 = (new_w[0], new_w[-1]) if len(new_w) > 1 else (walls[-2], walls[-1])
    dt = (w1[1] - w0[1]).total_seconds()
    if dt > 0:
        print(f'speed {(w1[0] - w0[0]) / dt:.1f} steps/s over the new span; last STEP at {walls[-1][1]:%m-%d %H:%M}')


def med(x):
    x = sorted(x)
    n = len(x)
    return (x[n // 2] + x[(n - 1) // 2]) / 2


def mad(x, m):
    return 1.4826 * med([abs(v - m) for v in x])


# 1. metrics
flags, table = [], []
for (kind, k), v in sorted(series.items()):
    new = [x for s, x in v if s > since]
    old = [x for s, x in v if s <= since][-a.base:]
    if not new:
        continue
    if len(new) > 50:                              # STEP-like: compare block means over equal spans, so
        B = len(new) // 20                         # autocorrelation doesn't inflate z
        old = [x for s, x in v if s <= since][-len(new):]
        blk = lambda x: [sum(x[i:i + B]) / B for i in range(0, len(x) - B + 1, B)]
        new_b, old_b = blk(new), blk(old)
    else:
        new_b, old_b = new, old
    allv = [x for _, x in v]
    if max(allv) == min(allv):
        continue                                   # constant: a count or a fixed reference value
    row = f'{kind:16s} {k:18s} n {len(new):5d}  latest {new[-1]:10.4g}'
    if 0 < len(old) < 5:
        row += '  earlier ' + ', '.join(f'{x:.4g}' for x in old[-4:])
    if len(old_b) >= 5:
        m0, d0 = med(old_b), mad(old_b, med(old_b))
        d0 = d0 or (abs(m0) * 1e-3 + 1e-9)
        m1 = med(new_b)
        zs = (m1 - m0) / (d0 / math.sqrt(len(new_b)))
        row += f'  median {m1:10.4g} vs {m0:10.4g} ({m1 - m0:+.4g}, z {zs:+.1f})'
        if abs(zs) >= 3:
            flags.append((abs(zs), f'SHIFT  {kind} {k}: median {m0:.4g} -> {m1:.4g} (z {zs:+.1f}, {len(new)} new vs {len(old)} earlier'
                                       + (f', in blocks of {B})' if len(new) > 50 else ')')))
        out = [(s, x) for s, x in v if s > since and abs(x - m0) / d0 >= 3] if len(new) <= 50 else []
        if out and len(new) <= 50:              # per-value outliers only where values are few (evals)
            s, x = max(out, key=lambda t: abs(t[1] - m0))
            flags.append((abs(x - m0) / d0, f'OUTLIER {kind} {k}: {x:.4g} at step {s} (baseline {m0:.4g} +- {d0:.3g}, {len(out)} of {len(new)} new beyond 3)'))
        if len(allv) >= 10 and len(new) <= 50:
            if new[-1] == max(allv) or new[-1] == min(allv):
                flags.append((3, f'RECORD {kind} {k}: {new[-1]:.4g} is the launch {"max" if new[-1] == max(allv) else "min"} ({len(allv)} values)'))
    table.append(row)
print('\n## flags')
flags.sort(key=lambda f: -f[0])
print('\n'.join(f for _, f in flags[:15]) if flags else '(none)')
if len(flags) > 15:
    print(f'... and {len(flags) - 15} weaker flags')
print('\n## metrics (new values vs the earlier ones)')
print('\n'.join(table))

# 2. GEN text
WORD = re.compile(r"[A-Za-z][A-Za-z']*")
P1, P2 = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours', "i'm", "i've", "i'd", "i'll", "we're"}, {'you', 'your', 'yours', "you're"}
P3 = {'he', 'him', 'his', 'she', 'her', 'hers', 'they', 'them', 'their', 'theirs'}
BOILER = re.compile(r'https?:|www\.|\.com\b|©|copyright|all rights reserved|click|subscribe|e-?mail|phone|\bterms\b|'
                    r'privacy|cookie|\$\d|\d{3}[-. ]\d{3}[-. ]\d{4}|posted (?:on|by)|read more|log ?in|sign up|newsletter|'
                    r'\bshop\b|discount|free shipping|\bcall\b|contact us', re.I)
STOP = set('''that this with from have were been they their there which what when where will would about into than then them
these those your some more most also just only other such very each could should after before over under while being does
done like here many much make made well even back still because through between both same where whose upon every one two
first last next said says time year years people know think going really things thing want need good great best'''.split())


def feats(t):
    t = t.replace('\\n', '\n')
    w = [x.lower() for x in WORD.findall(t)]
    n = max(len(w), 1)
    grams = [tuple(w[i:i + 4]) for i in range(len(w) - 3)]
    return {'1st person /100w': 100 * sum(x in P1 for x in w) / n, '2nd person /100w': 100 * sum(x in P2 for x in w) / n,
            '3rd person /100w': 100 * sum(x in P3 for x in w) / n, 'questions /100w': 100 * t.count('?') / n,
            'quotes /100w': 100 * t.count('"') / n, 'boilerplate /100w': 100 * len(BOILER.findall(t)) / n,
            'newlines /100w': 100 * t.count('\n') / n, 'digits /100w': 100 * len(re.findall(r'\d+', t)) / n,
            'repeated 4-grams %': 100 * (1 - len(set(grams)) / max(len(grams), 1))}


new = {s: t for s, t in gens.items() if s > since}
old = {s: t for s, t in gens.items() if s <= since}
print(f'\n## GEN text: {len(new)} new samples vs {len(old)} earlier')
if new and old:
    fn, fo = [feats(t) for t in new.values()], [feats(t) for t in old.values()]
    for k in fn[0]:
        xn, xo = [f[k] for f in fn], [f[k] for f in fo]
        mn, mo = sum(xn) / len(xn), sum(xo) / len(xo)
        sd = math.sqrt(sum((x - mo) ** 2 for x in xo) / max(len(xo) - 1, 1)) or 1e-9
        z = (mn - mo) / (sd / math.sqrt(len(xn)))
        mark = '  <--' if abs(z) >= 3 else ''
        print(f'{k:20s} {mn:7.2f} vs {mo:7.2f}  (z {z:+.1f}){mark}')

    def counts(texts):
        c = collections.Counter()
        for t in texts:
            c.update(set(x.lower() for x in WORD.findall(t) if len(x) >= 4 and x.lower() not in STOP))
        return c                                   # documents containing the word
    cn, co = counts(new.values()), counts(old.values())
    Nn, No = len(new), len(old)
    lo = {w: math.log((cn[w] + .5) / (Nn + 1)) - math.log((co[w] + .5) / (No + 1)) for w in cn if cn[w] >= 3}
    up = sorted(lo, key=lo.get, reverse=True)[:15]
    print('topic words up: ' + ', '.join(f'{w} ({cn[w]}/{Nn} vs {co[w]}/{No})' for w in up))
if new:
    q = lambda s: f'[step {s}, fluency {scores.get(s, "?")}%] ' + new[s].replace('\\n', ' / ')[:a.quote]
    sc = [s for s in new if s in scores]
    if sc:
        print('\nbest:   ' + q(max(sc, key=scores.get)))
        print('worst:  ' + q(min(sc, key=scores.get)))
    print('random: ' + q(random.Random(top).choice(sorted(new))))
    print('latest: ' + q(max(new)))

if a.mark:
    os.makedirs('log/notes', exist_ok=True)
    json.dump({'step': top}, open(STATE, 'w'))
    print(f'\n(marked step {top}: the next digest starts after it)')
