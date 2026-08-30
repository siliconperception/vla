#!/usr/bin/env python
"""Is a run's free-running GEN text COHERENT? Scored, not eyeballed.

Handing pp1's weights to k1 requires two things: the loss curve has turned its knee
(exp/knee.py) AND generation is coherent. "Coherent" is not a judgement we should be making
by reading samples -- a model can emit fluent-looking word salad, and reading three samples
is how earlier scalar readings got overturned.

Coherence here = how surprised a REFERENCE language model is by the text, in nats/token.
Two anchors make the number mean something, computed from the run's own corpus:
    FLOOR    real corpus sentences        -- as coherent as this corpus gets
    CEILING  the same sentences, words shuffled -- the same words, no syntax
A sample is reported as a 0-100% score placed between those two anchors, so 0% is
word-salad and 100% is indistinguishable from real corpus text. The reference model is
frozen and unrelated to the model under test, so this cannot be gamed by the run.

usage: exp/coherence.py log/exp.pp1_bvocab_e10s --corpus basic_dict_e10.txt [--tail 8]
"""
import argparse, random, re
import numpy as np, torch

ap = argparse.ArgumentParser()
ap.add_argument('log')
ap.add_argument('--corpus', default='basic_dict_e10.txt')
ap.add_argument('--model', default='EleutherAI/pythia-70m')
ap.add_argument('--device', default='cpu')
ap.add_argument('--tail', type=int, default=8, help='score the last N GEN samples')
ap.add_argument('--anchor', type=int, default=60, help='corpus lines for the anchors')
a = ap.parse_args()

from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained(a.model)
ref = AutoModelForCausalLM.from_pretrained(a.model).to(a.device).eval()

@torch.no_grad()
def nll(text):
    ids = tok(text, return_tensors='pt').input_ids.to(a.device)
    if ids.shape[1] < 2:
        return None
    out = ref(ids, labels=ids)
    return float(out.loss)

def words(s): return re.findall(r"[A-Za-z']+", s)

lines = [l.strip() for l in open(a.corpus) if l.strip()]
random.seed(0)
sample = random.sample(lines, min(a.anchor, len(lines)))
real = [x for x in (nll(s.split(':', 1)[-1].strip()) for s in sample) if x is not None]
shuf = []
for s in sample:
    w = words(s.split(':', 1)[-1]); random.shuffle(w)
    v = nll(' '.join(w))
    if v is not None: shuf.append(v)
FLOOR, CEIL = float(np.mean(real)), float(np.mean(shuf))
print(f'reference {a.model}   anchors from {a.corpus} ({len(real)} lines)')
print(f'  FLOOR   real corpus text     {FLOOR:6.3f} nats/token   -> 100%')
print(f'  CEILING words shuffled       {CEIL:6.3f} nats/token   ->   0%')

pat = re.compile(r'^GEN step\s+(\d+)\s+\[([^\]]*)\]:\s*(.*)$')
rows = []
for line in open(a.log):
    m = pat.match(line.rstrip('\n'))
    if m:
        t = m.group(3).replace('\\n', ' ').replace('<STX>', ' ').replace('<ETX>', ' ').strip()
        if len(words(t)) >= 4:
            rows.append((int(m.group(1)), m.group(2), t))
rows = rows[-a.tail:]
print(f'\n{"step":>10} {"prompt":<10} {"nats/tok":>9} {"coherence":>10}')
for step, prompt, text in rows:
    v = nll(text)
    if v is None: continue
    score = (CEIL - v) / (CEIL - FLOOR)
    bar = '#' * max(0, min(20, int(round(score * 20))))
    print(f'{step:10,} {prompt:<10} {v:9.3f} {score:9.1%}  {bar}')
    print(f'           {text[:110]}')
