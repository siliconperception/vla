#!/usr/bin/env python
"""Unigram / bigram cross-entropy of a corpus under the pythia31m tokenizer (--corpus).

Why: b5 scores 5.7528 nats/token held-out, against a 7.5491-nat unigram entropy, and its
reach probe says context is worth only +0.09 of that ~1.8-nat gain.  That raises the
question of whether the model is doing anything a bigram table does not.  This measures
the bigram floor on EXACTLY the documents exp/score.py evaluates, over EXACTLY the same
(x, y) pairs -- clip_text emits (input, target), so P(y|x) IS a bigram -- so the numbers
are directly comparable to the model's, not merely similar in spirit.

Fitting set is a disjoint slice (train[:N]); held-out is train[-3000:], the same tail
score.py uses.  Interpolated with unigram, P(y|x) = L*c(x,y)/c(x) + (1-L)*Puni(y), since
an unsmoothed bigram assigns zero to unseen pairs and scores infinity.  L is tuned on the
held-out set itself, which makes the reported bigram entropy OPTIMISTIC -- deliberately,
because the point is to establish a floor the model must beat, and an optimistic floor is
the conservative choice for that argument.

  python exp/ngram.py --fit 20000 --docs 400
"""
import argparse, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs, stable_load, heldout_docs

ap = argparse.ArgumentParser()
ap.add_argument('--fit', type=int, default=20000, help='docs from train[:fit] to fit on')
ap.add_argument('--docs', type=int, default=400, help='held-out docs (matches score.py)')
ap.add_argument('--minlen', type=int, default=512)
ap.add_argument('--maxlen', type=int, default=1024)
ap.add_argument('--ckpt', default='checkpoint/b5_long.final.pt')
ap.add_argument('--corpus', default='web', choices=['web', 'pile'],
                help="which corpus's floor to measure. Held-out comes from the shared "
                     "heldout_docs(), so it is the same set exp/score.py and "
                     "exp/pythia_ref.py score on. PLAN.txt's 5.3017 bigram floor is a WEB "
                     "number and does not transfer -- a corpus has its own information "
                     "floor, and a model score can only be read against its own corpus's.")
ap.add_argument('--streaming', action='store_true', default=None,
                help='stream the fit corpus (forced on for pile, which is 600GB+)')
a = ap.parse_args()

ck = stable_load(a.ckpt); sa = ck['saved_args']; g = load_vla_defs(sa)
# clip_text needs vla.py's OWN wrapper (start_id/end_id/encode), not the raw HF one
_repo = 'EleutherAI/pythia-31m'
g['_tokenizer'] = g['HFTokenizer'](_repo, 50304)
V = 50304
from datasets import load_dataset

def pairs(rows, limit=None, minlen=0, maxlen=None, want=None):
    """-> list of (x,y) int arrays, one per doc, via the same clip_text score.py uses."""
    out = []
    for ex in rows:
        t = ex.get('text','') or ''
        if not t.strip(): continue
        st, _ = g['clip_text'](t)
        if len(st) < minlen: continue
        if maxlen: st = st[:maxlen]
        out.append((np.fromiter((x for x,_ in st), dtype=np.int64, count=len(st)),
                    np.fromiter((y for _,y in st), dtype=np.int64, count=len(st))))
        if want and len(out) >= want: break
    return out

print(f'loading held-out ({a.corpus}, minlen {a.minlen}, first {a.docs} docs)...', flush=True)
# shared with exp/score.py / exp/pythia_ref.py, so the floor and the models it bounds are
# measured on identical documents in identical order.
_ho = heldout_docs(g, a.corpus, a.docs, a.minlen, a.maxlen)
ho = [(np.fromiter((x for x, _ in st), dtype=np.int64, count=len(st)),
       np.fromiter((y for _, y in st), dtype=np.int64, count=len(st))) for st in _ho]
print(f'  {len(ho)} docs, {sum(len(x) for x,_ in ho)} tokens', flush=True)

# The fit set must be DISJOINT from the held-out set or the bigram table has memorised the
# answer. web: train[:N] vs the train[-3000:] tail. pile: different repos entirely -- the
# deduplicated train re-release vs the Pile's official validation split -- which is a
# cleaner separation than web's, though it rests on EleutherAI's split being honest and is
# not independently verified here.
if a.corpus == 'pile':
    print(f'loading fit set (the_pile_deduplicated train, first {a.fit} docs, streaming)...',
          flush=True)
    _rows = load_dataset('EleutherAI/the_pile_deduplicated', split='train', streaming=True)
else:
    print(f'loading fit set (openwebtext train[:{a.fit}])...', flush=True)
    _rows = load_dataset('Skylion007/openwebtext', split=f'train[:{a.fit}]')
fit = pairs(_rows, want=a.fit)
FX = np.concatenate([x for x,_ in fit]); FY = np.concatenate([y for _,y in fit])
print(f'  {len(fit)} docs, {len(FX)} tokens', flush=True)

HX = np.concatenate([x for x,_ in ho]); HY = np.concatenate([y for _,y in ho])

def entropies(FX, FY, tag):
    cy = np.bincount(FY, minlength=V).astype(np.float64)          # unigram over targets
    cx = np.bincount(FX, minlength=V).astype(np.float64)          # context counts
    alpha = 0.1
    puni = (cy + alpha) / (cy.sum() + alpha*V)
    key = FX * np.int64(V) + FY
    key.sort()
    uk, uc = np.unique(key, return_counts=True)
    hk = HX * np.int64(V) + HY
    idx = np.searchsorted(uk, hk)
    idx = np.clip(idx, 0, len(uk)-1)
    hit = uk[idx] == hk
    cxy = np.where(hit, uc[idx], 0).astype(np.float64)
    cxh = cx[HX]
    pb = np.where(cxh > 0, cxy / np.maximum(cxh, 1), 0.0)          # raw bigram MLE
    pu = puni[HY]
    # score.py reports a mean of PER-DOCUMENT means ("clean"), not a token-level mean.
    # Report both, so the bigram number is comparable to the model's on its own terms.
    bnd = np.cumsum([0] + [len(x) for x, _ in ho])
    def perdoc(v):
        c = np.concatenate([[0.0], np.cumsum(v)])
        return (c[bnd[1:]] - c[bnd[:-1]]) / np.diff(bnd)
    uni_nats = float(-np.log(pu).mean())
    uni_doc  = float(perdoc(-np.log(pu)).mean())
    best = None
    for L in np.arange(0.0, 1.0, 0.02):
        p = L*pb + (1-L)*pu
        nl = -np.log(np.maximum(p, 1e-300))
        n = float(nl.mean())
        if best is None or n < best[1]:
            d = perdoc(nl); best = (L, n, float(d.mean()), float(np.median(d)))
    print(f'{tag}: fit {len(FX)/1e6:.1f}M tokens, {len(uk)/1e6:.2f}M distinct bigrams, '
          f'{100*hit.mean():.1f}% of held-out bigrams seen')
    print(f'{tag}: unigram tok {uni_nats:.4f} doc {uni_doc:.4f} | '
          f'bigram(L={best[0]:.2f}) tok {best[1]:.4f} doc {best[2]:.4f} median {best[3]:.4f}')
    return uni_nats, best[1]

# learning curve: is the bigram estimate data-limited, or converged?
for frac in (0.125, 0.25, 0.5, 1.0):
    n = int(len(FX)*frac)
    entropies(FX[:n], FY[:n], f'  {frac:.0%} of fit')
