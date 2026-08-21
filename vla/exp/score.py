#!/usr/bin/env python
"""Robust held-out scoring: quality AND runaway rate, as two separate numbers.

A mean over per-token cross-entropy is not a usable statistic here. A recurrent model with
eval-mode gain slightly over 1 runs away on a small fraction of documents, reaching losses of
1e6-1e13, and three such rows out of 250 move the mean by nine orders of magnitude. The mean
then reports a model as catastrophically broken when it is fine on 98.8% of documents.

So report both:
  clean   mean loss over documents that never exceed --thresh nats  (quality)
  runaway percentage of documents that do                           (reliability)
  median  per-document median loss, which no outlier can move       (cross-check)

  python exp/score.py checkpoint.pt.sexp checkpoint.pt.xrep ...
"""
import argparse, json, os, sys, time
import numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs

def stable_load(path, quiet=3.0, timeout=600):
    """torch.load a checkpoint only once the file has stopped changing, then verify it.

    The training loop writes checkpoints with torch.save every --checkpoint steps, and that is
    NOT atomic: a reader opening the file mid-write gets a truncated or half-updated tensor
    set. Crucially it does not raise -- it loads, and scores as a catastrophically broken
    model. On 2026-08-21 this produced a 100%-runaway / nan reading for wclip.60000 that
    rescored to 0.0% once the write had finished, and a training run was cancelled on the
    strength of that reading.

    Two guards: wait until size and mtime hold steady for `quiet` seconds, then reject any
    checkpoint carrying non-finite parameters. A partially written file usually trips the
    second check even if it slips past the first.
    """
    t0, last = time.time(), None
    while time.time() - t0 < timeout:
        try:
            st = os.stat(path)
        except FileNotFoundError:
            time.sleep(0.5)
            continue
        sig = (st.st_size, st.st_mtime_ns)
        if sig == last:
            break
        last = sig
        time.sleep(quiet)
    else:
        raise SystemExit(f'{path}: still being written after {timeout}s')
    ck = torch.load(path, map_location='cpu', weights_only=False)
    sd = ck.get('state_dict', {})
    bad = [k for k, v in sd.items()
           if torch.is_tensor(v) and v.is_floating_point() and not torch.isfinite(v).all()]
    if bad:
        raise SystemExit(f'{path}: {len(bad)} non-finite parameter tensors '
                         f'(e.g. {bad[:3]}) -- file is corrupt or the run diverged; '
                         f'refusing to score it')
    return ck


ap = argparse.ArgumentParser()
ap.add_argument('ckpts', nargs='+')
ap.add_argument('--docs', type=int, default=250)
ap.add_argument('--maxlen', type=int, default=384)
ap.add_argument('--minlen', type=int, default=96)
ap.add_argument('--thresh', type=float, default=20.0)
ap.add_argument('--corpus', default='tiny', choices=['tiny', 'web'])
ap.add_argument('--seed', type=int, default=1234)
ap.add_argument('--device', default='cuda')
ap.add_argument('--clip_dff', type=float, default=None,
                help='override the checkpoint\'s --clip_dff (0 disables). Needed to tell '
                     'apart "clipping during TRAINING kept the recurrence contractive" from '
                     '"clipping at INFERENCE masks a recurrence that is not": the probe '
                     'otherwise inherits the trained value and measures the masked case.')
a = ap.parse_args()

_docs = None
def get_docs(g):
    global _docs
    if _docs is not None: return _docs
    from datasets import load_dataset
    rows = (load_dataset('roneneldan/TinyStories', split='validation') if a.corpus == 'tiny'
            else load_dataset('Skylion007/openwebtext', split='train[-3000:]'))
    d = []
    for ex in rows:
        t = ex.get('text','') or ''
        if not t.strip(): continue
        st, _ = g['clip_text'](t)
        if len(st) >= a.minlen: d.append(st[:a.maxlen])
        if len(d) >= a.docs: break
    _docs = d
    return d

print(f'{"checkpoint":14} {"step":>6} {"clean":>8} {"median":>8} {"runaway%":>9} {"nrun":>5} '
      f'{"first":>6} {"naive_mean":>11}')
print('-' * 76)
out = {}
for c in a.ckpts:
    if not os.path.exists(c):
        continue
    ck = stable_load(c)
    sa = ck['saved_args']; g = load_vla_defs(sa)
    kw = dict(n_hidden=sa['n_hidden'], depth=sa['depth'], kernel=sa['kernel'], S=sa['context'],
              c_text=sa['c_text'], n_layers=sa['n_layers'], clock=sa.get('clock','sync'),
              accumulate=sa.get('accumulate',False), ema=sa.get('ema'),
              qproj=sa.get('qproj','none'), tap=sa.get('tap',False),
              tokenizer=sa['tokenizer'], head_norm=sa.get('head_norm','none'))
    for k in ('clock_base','clock_max','clock_ends','clip_dff'):
        if k in sa: kw[k] = sa[k]
    if a.clip_dff is not None:
        kw['clip_dff'] = a.clip_dff
    torch.manual_seed(a.seed)
    m = g['VLAModel'](**kw); m.load_state_dict(ck['state_dict'])
    m.init_mode = sa.get('init','relu'); m = m.to(a.device).eval()
    g['_tokenizer'] = m.tok
    docs = get_docs(g)
    B = len(docs); T = max(len(d) for d in docs)
    X = torch.zeros((B,T),dtype=torch.long); Y = torch.zeros((B,T),dtype=torch.long)
    M = torch.zeros((B,T),dtype=torch.bool)
    for r, st in enumerate(docs):
        X[r,:len(st)] = torch.tensor([x for x,_ in st])
        Y[r,:len(st)] = torch.tensor([y for _,y in st]); M[r,:len(st)] = True
    X,Y,M = X.to(a.device), Y.to(a.device), M.to(a.device)
    m.dff = None; torch.manual_seed(a.seed)
    rs = np.zeros(B); rn = np.zeros(B); rmax = np.zeros(B); fb = np.full(B,-1)
    with torch.no_grad():
        for t in range(T):
            lg, _ = m(X[:,t])
            ce = F.cross_entropy(lg, Y[:,t], reduction='none').cpu().numpy()
            msk = M[:,t].cpu().numpy().astype(bool)
            ce = np.where(np.isfinite(ce), ce, 1e30)
            rs += np.where(msk, ce, 0); rn += msk
            rmax = np.maximum(rmax, np.where(msk, ce, 0))
            new = msk & (ce > a.thresh) & (fb < 0)
            fb[new] = t
    per = rs / np.maximum(rn,1)
    bad = fb >= 0
    clean = float(per[~bad].mean()) if (~bad).any() else float('nan')
    res = dict(step=int(ck.get('step',-1)), clean=clean, median=float(np.median(per)),
               runaway=float(100*bad.mean()), nrun=int(bad.sum()),
               first=int(np.min(fb[bad])) if bad.any() else -1, naive=float(per.mean()))
    out[os.path.basename(c).replace('checkpoint.pt.','')] = res
    print(f'{os.path.basename(c)[14:]:14} {res["step"]:6d} {clean:8.4f} {res["median"]:8.4f} '
          f'{res["runaway"]:9.1f} {res["nrun"]:5d} {res["first"]:6d} {res["naive"]:11.4g}')
json.dump(out, open('exp/score.json','w'), indent=1)
