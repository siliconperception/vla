#!/usr/bin/env python
"""How much of a free-running GEN sample is VERBATIM training text?

The success criterion for a memorization run (pp1, b1, d1) is that generation eventually
reproduces the corpus, and "does that look like the training set?" is not a measurement.
This scores every GEN line in a log against the corpus and reports the longest run of
consecutive words that appears in it verbatim, plus what fraction of the sample is covered
by runs of >= --min words.

Why word runs and not characters or an edit distance: a model that has learned the STYLE of
a corpus scores high on character overlap while reproducing nothing, and edit distance is
dominated by length. A contiguous 8-word match is not something a 30M-parameter model emits
by accident on an 8,480-sentence corpus -- it is recall.

usage: exp/verbatim.py log/exp.pp1_bvocab_e10s basic_dict_e10.txt [--min 5] [--every 1]
"""
import argparse, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('log'); ap.add_argument('corpus')
ap.add_argument('--min', type=int, default=5, help='word-run length counted as recall')
ap.add_argument('--every', type=int, default=1, help='report every Nth GEN line')
ap.add_argument('--tail', type=int, default=0, help='only the last N GEN lines')
a = ap.parse_args()

def words(s):
    return re.findall(r"[A-Za-z']+", s.lower())

corp = words(open(a.corpus).read())
# every n-gram of the corpus, n = 1..MAXN, as a set of tuples for O(1) lookup
MAXN = 24
grams = [set() for _ in range(MAXN + 1)]
for n in range(1, MAXN + 1):
    g = grams[n]
    for i in range(len(corp) - n + 1):
        g.add(tuple(corp[i:i + n]))

gen_pat = re.compile(r'^GEN step\s+(\d+)\s+\[([^\]]*)\]:\s*(.*)$')
rows = []
for line in open(a.log):
    m = gen_pat.match(line.rstrip('\n'))
    if not m:
        continue
    step, prompt, text = int(m.group(1)), m.group(2), m.group(3)
    text = text.replace('\\n', ' ').replace('<STX>', ' ').replace('<ETX>', ' ')
    w = words(text)
    if not w:
        continue
    longest, covered = 0, [False] * len(w)
    for i in range(len(w)):
        for n in range(min(MAXN, len(w) - i), 0, -1):
            if tuple(w[i:i + n]) in grams[n]:
                if n > longest:
                    longest = n
                if n >= a.min:
                    for k in range(i, i + n):
                        covered[k] = True
                break
    rows.append((step, prompt, len(w), longest, sum(covered) / len(w), ' '.join(w)))

if a.tail:
    rows = rows[-a.tail:]
rows = rows[::a.every]
print(f'corpus {a.corpus}: {len(corp):,} words   log {a.log}: {len(rows)} GEN samples shown')
print(f'{"step":>9}  {"prompt":<12} {"words":>5} {"longest":>7} {"cov>=" + str(a.min):>7}')
for step, prompt, nw, lg, cov, _ in rows:
    bar = '#' * int(round(cov * 20))
    print(f'{step:9,}  {prompt:<12} {nw:5} {lg:7} {cov:6.1%}  {bar}')
if rows:
    best = max(rows, key=lambda r: r[3])
    print(f'\nlongest verbatim run: {best[3]} words at step {best[0]:,}')
    print(f'  {best[5][:300]}')
