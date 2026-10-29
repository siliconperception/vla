"""Score Hugging Face causal LMs (e.g. the Pythia checkpoint series) on documents dumped by
`vla.py --eval --eval_dump FILE`, by vla.py's EVAL rule, for loss-against-tokens comparisons.

usage: python tools/hf_eval.py DUMP --models EleutherAI/pythia-70m --revs step64,step128,main
       [--corpus fineweb] [--out results.jsonl]

Each document is scored after one <|endoftext|> (Pythia's BOS, as vla.py's _NULL opens its rows),
all of its tokens at once (they are at most 1024). As vla.py: a document with any token over 20 nats is
runaway and left out; clean = mean over the rest of each document's mean loss; nats/char over the
clean documents. Also the mean loss by position band (0-63, 64-255, 256-1023), where a model's use
of context shows. Pythia step N has seen N x 2,097,152 tokens (1024 sequences of 2048)."""
import argparse
import json
import time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument('dump')
ap.add_argument('--models', required=True)
ap.add_argument('--revs', default='main')
ap.add_argument('--corpus', default='fineweb')
ap.add_argument('--batch', type=int, default=2)
ap.add_argument('--out', default=None)
a = ap.parse_args()

THRESH, BANDS = 20.0, ((0, 64), (64, 256), (256, 1024))
docs = json.load(open(a.dump))[a.corpus]
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
tok = AutoTokenizer.from_pretrained(a.models.split(',')[0])
nchar = np.array([len(tok.decode(d)) for d in docs], dtype=np.float64)
ntok = np.array([len(d) for d in docs], dtype=np.float64)
L = max(len(d) for d in docs)
for name in a.models.split(','):
    for rev in a.revs.split(','):
        t0 = time.time()
        m = AutoModelForCausalLM.from_pretrained(name, revision=rev, dtype=torch.float32).to(dev).eval()
        per, bad = np.zeros(len(docs)), np.zeros(len(docs), dtype=bool)
        bsum, bcnt = np.zeros(len(BANDS)), np.zeros(len(BANDS))
        with torch.no_grad():
            for i in range(0, len(docs), a.batch):
                chunk = docs[i:i + a.batch]
                X = torch.zeros(len(chunk), L + 1, dtype=torch.long)
                M = torch.zeros(len(chunk), L, dtype=torch.bool)
                for j, d in enumerate(chunk):
                    X[j, 1:len(d) + 1] = torch.tensor(d)
                    M[j, :len(d)] = True
                X, M = X.to(dev), M.to(dev)
                logits = m(X[:, :-1]).logits.float()
                ce = torch.nn.functional.cross_entropy(logits.transpose(1, 2), X[:, 1:],
                                                       reduction='none') * M
                per[i:i + len(chunk)] = (ce.sum(1) / M.sum(1)).cpu().numpy()
                bad[i:i + len(chunk)] = ((ce > THRESH) & M).any(1).cpu().numpy()
                for k, (lo, hi) in enumerate(BANDS):
                    ok = M[:, lo:hi] & ~((ce > THRESH) & M).any(1, keepdim=True)
                    bsum[k] += float((ce[:, lo:hi] * ok).sum())
                    bcnt[k] += float(ok.sum())
        clean = float(per[~bad].mean())
        npc = float((per * ntok)[~bad].sum() / nchar[~bad].sum())
        step = int(rev[4:]) if rev.startswith('step') else 143000 if rev == 'main' else None
        r = dict(model=name, rev=rev, tokens=step * 2097152 if step is not None else None,
                 clean=clean, median=float(np.median(per)), nrun=int(bad.sum()), docs=len(docs),
                 nats_per_char=npc, bands={f'{lo}-{hi - 1}': bsum[k] / max(1, bcnt[k])
                                           for k, (lo, hi) in enumerate(BANDS)})
        print(f'HFEVAL {name:26} {rev:>9} tokens {r["tokens"] or 0:>15,} clean {clean:8.4f} '
              f'median {r["median"]:8.4f} nrun {r["nrun"]:3d} nats/char {npc:.4f} | '
              + ' '.join(f'{b} {v:.3f}' for b, v in r['bands'].items())
              + f' | {time.time() - t0:5.1f}s', flush=True)
        if a.out:
            with open(a.out, 'a') as f:
                f.write(json.dumps(r) + '\n')
        del m
        torch.cuda.empty_cache()
