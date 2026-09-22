#!/usr/bin/env python
"""Reach probe with warm-up held constant.

memtest.py measures excess(c) by RESETTING the DFF to its --init seed and feeding c tokens.
That conflates two things:

  (1) genuine use of information older than c tokens   <- what we want
  (2) time for the recurrent state to warm up from the seed, which scales with the slowest
      layer's write period                             <- a confound

A --clock fixed model whose layer 7 writes every 64 steps needs a couple of hundred tokens
just to leave its seed, so it looks like it "uses" long context when it is only warming up.

This probe removes (2). Instead of resetting, it SPLICES: each row is a long concatenation
of P-token chunks taken from unrelated documents, with the state reset only at t=0. At
offset c inside a chunk the state is fully warm -- it has seen hundreds of tokens -- but only
c of them belong to the current document. Every scored token is paired against the SAME
token scored with its true full document history, so

    excess(c) = extra nats from having only c tokens of RELEVANT context, warm-up held equal

  python exp/reach.py --load checkpoint.pt.sexp --periods 8,32,128
"""
import argparse, json, os, sys
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# stable_load lives in memtest (import-safe); score.py parses argv at module
# level, so importing it from here would hijack this script's arguments.
from memtest import load_vla_defs, stable_load, heldout_docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--load', required=True)
    ap.add_argument('--docs', type=int, default=500)
    ap.add_argument('--batch', type=int, default=250)
    ap.add_argument('--rows', type=int, default=500, help='spliced rows to score')
    ap.add_argument('--len', type=int, default=384, help='length of each spliced row')
    ap.add_argument('--maxlen', type=int, default=384)
    ap.add_argument('--minlen', type=int, default=96)
    ap.add_argument('--periods', default='8,32,128')
    ap.add_argument('--corpus', default='tiny', choices=['tiny', 'web', 'pile', 'c4'],
                    help="corpus to splice from, shared with exp/score.py. Use the one the "
                         "checkpoint TRAINED on: reach measures how much a model exploits "
                         "its own context, and probing off-domain measures how badly it "
                         "handles unfamiliar text instead")
    ap.add_argument('--device', default='cuda')
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    ck = stable_load(a.load)
    saved = ck.get('saved_args', {})
    g = load_vla_defs(saved)
    VLAModel, clip_text = g['VLAModel'], g['clip_text']
    torch.manual_seed(a.seed)
    # VLAModel's signature, as of the --ema_ladder rewrite: the --clock era kwargs
    # (clock, accumulate, clock_base/max/ends) are GONE, and c_context is now separate from
    # n_hidden, so a checkpoint with c_context != n_hidden rebuilds at the wrong interior
    # width and load_state_dict fails. Keep this list in step with vla.py VLAModel.__init__.
    kw = dict(n_hidden=saved['n_hidden'], depth=saved['depth'], kernel=saved['kernel'],
              S=saved['context'], c_text=saved['c_text'], n_layers=saved['n_layers'],
              c_context=saved.get('c_context'),
              ema=saved.get('ema'), qproj=saved.get('qproj', 'none'),
              tap=saved.get('tap', False), tokenizer=saved['tokenizer'],
              head_norm=saved.get('head_norm', 'none'))
    # forward EVERY architecture key the checkpoint carries; omitting one rebuilds a
    # different model and the state_dict will not load (see score.py).
    for k in ('clip_dff', 'norm', 'norm_groups', 'dff_norm', 'bn_track', 'bn_affine',
              'bn_momentum', 'bn_eps'):
        if k in saved and saved[k] is not None: kw[k] = saved[k]
    model = VLAModel(**kw)
    model.load_state_dict(ck['state_dict'])
    model.init_mode = saved.get('init', 'relu')
    model = model.to(a.device).eval()
    g['_tokenizer'] = model.tok
    print(f'{a.load}: step {ck.get("step")} n_layers {saved["n_layers"]} '
          f'depth {saved["depth"]} n_hidden {saved["n_hidden"]} c_context {saved.get("c_context")} '
          f'ema {model.ema} (ema_ladder {saved.get("ema_ladder")})', flush=True)

    # shared selector (exp/memtest.heldout_docs), same as score.py / pythia_ref.py /
    # ngram.py, so a reach number and a loss number describe the same documents.
    docs = heldout_docs(g, a.corpus, a.docs, a.minlen, a.maxlen)   # g['_tokenizer'] set above
    T = max(len(d) for d in docs)
    dev = a.device
    print(f'{len(docs)} documents, mean length {np.mean([len(d) for d in docs]):.0f}', flush=True)

    # ── pass A: true full-document history, per (doc, position) ──
    ce_full = np.full((len(docs), T), np.nan)
    for s in range(0, len(docs), a.batch):
        ch = docs[s:s + a.batch]; B = len(ch); Tb = max(len(c) for c in ch)
        X = torch.zeros((B, Tb), dtype=torch.long); Y = torch.zeros((B, Tb), dtype=torch.long)
        M = torch.zeros((B, Tb), dtype=torch.bool)
        for r, st in enumerate(ch):
            X[r, :len(st)] = torch.tensor([x for x, _ in st])
            Y[r, :len(st)] = torch.tensor([y for _, y in st])
            M[r, :len(st)] = True
        X, Y, M = X.to(dev), Y.to(dev), M.to(dev)
        model.dff = None
        torch.manual_seed(a.seed)
        with torch.no_grad():
            for t in range(Tb):
                lg, _ = model(X[:, t])
                ce = F.cross_entropy(lg, Y[:, t], reduction='none')
                v = ce.cpu().numpy(); m = M[:, t].cpu().numpy()
                ce_full[s:s + B, t] = np.where(m, v, np.nan)
    _cf = ce_full[np.isfinite(ce_full)]
    print(f'full-history: clean mean {_cf[_cf <= 20].mean():8.5f}  '
          f'median {np.median(_cf):8.5f}  '
          f'runaway {100.0 * (_cf > 20).mean():4.1f}% of scored tokens', flush=True)

    # ── pass B: spliced rows, state warm but context irrelevant ──
    rng = np.random.default_rng(a.seed)
    res = {}
    for P in [int(p) for p in a.periods.split(',')]:
        K = a.len // P                       # chunks per row
        exc = np.zeros(P); cnt = np.zeros(P); nbad = np.zeros(P)
        elig = [i for i, d in enumerate(docs) if len(d) >= P]
        for s in range(0, a.rows, a.batch):
            B = min(a.batch, a.rows - s)
            # plan: row r, chunk k -> (doc, start). Fixed rng, so identical for every model.
            plan = [[(int(rng.choice(elig)), 0) for k in range(K)] for _ in range(B)]
            plan = [[(d, int(rng.integers(0, len(docs[d]) - P + 1))) for d, _ in row]
                    for row in plan]
            X = torch.zeros((B, K * P), dtype=torch.long)
            Y = torch.zeros((B, K * P), dtype=torch.long)
            for r, row in enumerate(plan):
                for k, (d, st) in enumerate(row):
                    seg = docs[d][st:st + P]
                    X[r, k*P:(k+1)*P] = torch.tensor([x for x, _ in seg])
                    Y[r, k*P:(k+1)*P] = torch.tensor([y for _, y in seg])
            X, Y = X.to(dev), Y.to(dev)
            model.dff = None                 # reset ONCE, at the very start of the row
            torch.manual_seed(a.seed)
            with torch.no_grad():
                for t in range(K * P):
                    lg, _ = model(X[:, t])
                    ce = F.cross_entropy(lg, Y[:, t], reduction='none').cpu().numpy()
                    k, c = divmod(t, P)
                    if k == 0:
                        continue             # first chunk is not warm yet
                    for r in range(B):
                        d, st = plan[r][k]
                        ref = ce_full[d, st + c]
                        # Drop runaway rows. A recurrence with eval-mode gain slightly over 1
                        # blows up on ~1% of streams, reaching 1e6-1e13; including those in a
                        # mean makes it report nine orders of magnitude and tells you nothing
                        # about the other 99%. Counted separately as a rate, not averaged in.
                        if not (np.isfinite(ref) and np.isfinite(ce[r])):
                            nbad[c] += 1; continue
                        if ce[r] > 20.0 or ref > 20.0:
                            nbad[c] += 1; continue
                        exc[c] += ce[r] - ref; cnt[c] += 1
        curve = exc / np.maximum(cnt, 1)
        # Stability gate. The spliced pass runs the recurrence over K*P continuous real
        # tokens with a single reset at t=0, which is a harsher test than memtest's
        # per-document framing (~196 tokens then a reset). A recurrence whose eval-mode gain
        # slightly exceeds 1 survives 200 steps and blows up by 400, so it passes memtest and
        # fails here. This is the gate the study ranks on.
        rate = 100.0 * nbad.sum() / max(nbad.sum() + cnt.sum(), 1)
        if False:
            bad = int((np.abs(curve) > 20.0).sum())
            print(f'  *** DIVERGED at P={P}: {bad}/{P} offsets over 20 nats, '
                  f'max |excess| {np.nanmax(np.abs(curve)):.3g} -- the recurrence is not '
                  f'contractive over {K*P} continuous tokens', flush=True)
        res[P] = {'curve': [float(x) for x in curve], 'n': [float(x) for x in cnt],
                  'mean': float(exc.sum() / max(cnt.sum(), 1))}
        # print out to the full window, not just the first 128: the P=512 pass measures
        # reach to c=511 and truncating the display at 127 hid document-scale behaviour
        # (wfix236 was still paying +0.15 nats at c=256 and read as a ~100-token model).
        pts = [c for c in (0, 1, 2, 4, 8, 16, 32, 64, 96, 128, 192, 256, 320, 384,
                           448, 511) if c < P]
        print(f'  P={P:4d} mean {res[P]["mean"]:+7.4f} runaway {rate:4.1f}% | ' +
              '  '.join(f'c{c}:{curve[c]:+6.3f}' for c in pts), flush=True)

    out = a.out or f'exp/reach.{os.path.basename(a.load).replace("checkpoint.pt.","")}.json'
    json.dump({'load': a.load, 'step': ck.get('step'),
               'full_loss': float(np.nanmean(ce_full)),
               'periods': {str(k): v for k, v in res.items()}}, open(out, 'w'))
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
