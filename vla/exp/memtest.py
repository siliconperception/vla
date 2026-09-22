#!/usr/bin/env python
"""Long-range dependency probe for vla.py checkpoints.

Measures loss as a function of how many tokens of context the recurrent DFF state has
actually seen, by forcing a context reset every P steps while streaming held-out
documents.  Within a window, the token at offset c is predicted from exactly c tokens of
history, so mean CE at offset c is L(c): the model's loss given c tokens of memory.
P=0 means "never reset inside a document" -- the natural framing, the ceiling.

Everything is paired: the same documents, the same absolute positions, the same target
tokens for every P and every checkpoint, so differences are not confounded by which
tokens got scored.

  python exp/memtest.py --load checkpoint.pt.foo --docs 500 --periods 0,4,16,64
"""
import argparse, json, math, os, sys, time, itertools
import numpy as np
import torch
import torch.nn.functional as F

VLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vla.py')
# Exec vla.py through the last definition before the data worker. Located by marker, not
# by line number: a hard-coded offset silently goes stale the moment vla.py gains a line.
CUT_MARK = '# \u2500\u2500 worker '


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


# ── held-out corpora ───────────────────────────────────────────────────────────
# One definition, imported by BOTH exp/score.py and exp/pythia_ref.py, so a VLA
# checkpoint and an HF transformer are provably scored on the same documents in the
# same order.  They used to select docs with duplicated inline loops; the moment
# Phase 2 added a second corpus that duplication became a way to compare two models
# on two different held-out sets and not notice.
#
#   web   openwebtext train[-3000:]  -- the Phase 1 held-out.  Comparable to every
#         number in PLAN.txt's reference table.  CROSS-DOMAIN for a Pile-trained
#         model (both VLA-on-pile and pythia).
#   pile  the Pile's official validation split (mit-han-lab/pile-val-backup; neither
#         Pile re-release on the hub carries one).  IN-DOMAIN for pythia and for a
#         --dataset pile VLA run, which is what makes a VLA-vs-pythia comparison on
#         it a like-for-like one.
#   tiny  TinyStories validation.
#   c4    Google's Colossal Clean Crawled Corpus, T5's training set -- a second,
#         INDEPENDENT crawl-derived corpus. Worth noting for gpt2-teacher experiments:
#         GPT-2 was trained on WebText, not C4, and the open replication of WebText is
#         Skylion007/openwebtext == 'web'. So 'web' probes what a gpt2 teacher's text
#         resembles and 'c4' deliberately does not.
_HELDOUT = {
    'tiny': ('roneneldan/TinyStories',      None, 'validation'),
    'web':  ('Skylion007/openwebtext',      None, 'train[-3000:]'),
    'pile': ('mit-han-lab/pile-val-backup', None, 'validation'),
    'c4':   ('allenai/c4',                  'en', 'validation'),
}


def heldout_docs(g, corpus, docs, minlen, maxlen):
    """First `docs` documents of `corpus` that tokenize to >= minlen steps, each clipped
    to maxlen.  `g` is a load_vla_defs() globals dict, used for its clip_text/_tokenizer,
    so the documents are the exact (x, y) step pairs the model is trained on."""
    from datasets import load_dataset
    if corpus not in _HELDOUT:
        raise SystemExit(f'unknown held-out corpus: {corpus}')
    hf, cfg, split = _HELDOUT[corpus]
    d = []
    for ex in load_dataset(hf, cfg, split=split):
        t = ex.get('text', '') or ''
        if not t.strip():
            continue
        st, _ = g['clip_text'](t)
        if len(st) >= minlen:
            d.append(st[:maxlen])
        if len(d) >= docs:
            break
    return d


def load_vla_defs(saved):
    """Exec the head of vla.py (tokenizers, DFFClock, VLAModel, clip_text) with an argv
    that reproduces the checkpoint's architecture, and hand back its globals."""
    argv = ['vla.py', '--log', os.devnull, '--device', 'cpu']
    for k in ('tokenizer', 'head_norm', 'context', 'n_hidden', 'c_context', 'c_text',
              'n_layers', 'depth', 'kernel', 'qproj', 'clock', 'init', 'dataset',
              'linout_kernel'):
        if saved.get(k) is not None:
            argv += [f'--{k}', str(saved[k])]
    if saved.get('ema') is not None:
        argv += ['--ema', str(saved['ema'])]
    if saved.get('accumulate'):
        argv += ['--accumulate']
    if saved.get('tap'):
        argv += ['--tap']
    # --linout is NOT a VLAModel kwarg: it is read off the module-level `args` at construction
    # (vla.py "getattr(args, 'linout', False)"), so it has to arrive through argv or the
    # rebuilt model has deep_proj where the checkpoint has linout and load_state_dict fails.
    if saved.get('linout'):
        argv += ['--linout']
    # ema_ladder likewise: saved_args['ema'] keeps only the SCALAR, so without this the
    # per-layer rates are silently replaced by that scalar.
    if saved.get('ema_ladder') is not None:
        argv += ['--ema_ladder', str(saved['ema_ladder'])]
    lines = open(VLA).read().split('\n')
    cut = next(i for i, l in enumerate(lines) if l.startswith(CUT_MARK))
    src = lines[:cut]
    g = {'__name__': '__vla_defs__', '__file__': VLA}
    old = sys.argv
    sys.argv = argv
    try:
        exec(compile('\n'.join(src), VLA, 'exec'), g)
    finally:
        sys.argv = old
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--load', required=True)
    ap.add_argument('--docs', type=int, default=500, help='held-out documents to score')
    ap.add_argument('--batch', type=int, default=250)
    ap.add_argument('--maxlen', type=int, default=512, help='truncate documents to N tokens')
    ap.add_argument('--minlen', type=int, default=128, help='skip documents shorter than this')
    ap.add_argument('--periods', default='0,2,4,8,16,32,64,128',
                    help='forced-reset periods; 0 = never reset inside a document')
    ap.add_argument('--device', default='cuda')
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--corpus', default='tiny', choices=['tiny', 'web'],
                    help='held-out documents to probe on. tiny = TinyStories validation '
                         '(~211 tokens/doc, so it cannot resolve a horizon past ~200). '
                         'web = the last 3000 documents of openwebtext, held out from the '
                         'shuffled stream training reads (median 752 tokens, 36%% over 1024)')
    ap.add_argument('--out', default=None, help='write json here')
    a = ap.parse_args()

    ck = torch.load(a.load, map_location='cpu', weights_only=False)
    saved = ck.get('saved_args', {})
    g = load_vla_defs(saved)
    VLAModel, clip_text = g['VLAModel'], g['clip_text']

    torch.manual_seed(a.seed)
    model = VLAModel(
        n_hidden=saved['n_hidden'], depth=saved['depth'], kernel=saved['kernel'],
        S=saved['context'], c_text=saved['c_text'], n_layers=saved['n_layers'],
        clock=saved.get('clock', 'sync'), accumulate=saved.get('accumulate', False),
        ema=saved.get('ema'), qproj=saved.get('qproj', 'none'), tap=saved.get('tap', False),
        tokenizer=saved['tokenizer'], head_norm=saved.get('head_norm', 'none'))
    model.load_state_dict(ck['state_dict'])
    model.init_mode = saved.get('init', 'relu')
    model = model.to(a.device).eval()
    g['_tokenizer'] = model.tok           # clip_text() reads the module-level tokenizer
    step = ck.get('step', -1)
    print(f'corpus {a.corpus}')
    print(f'{a.load}: step {step} n_layers {saved["n_layers"]} depth {saved["depth"]} '
          f'clock {saved.get("clock")} tap {saved.get("tap")} ema {saved.get("ema")} '
          f'accum {saved.get("accumulate")} init {saved.get("init")}', flush=True)

    # ── held-out documents, identical for every checkpoint (no shuffling, fixed order) ──
    from datasets import load_dataset
    if a.corpus == 'tiny':
        rows = load_dataset('roneneldan/TinyStories', split='validation')
    else:
        rows = load_dataset('Skylion007/openwebtext', split='train[-3000:]')
    clips = []
    for ex in rows:
        text = ex.get('text', '') or ''
        if not text.strip():
            continue
        steps, _ = clip_text(text)
        if len(steps) >= a.minlen:
            clips.append(steps[:a.maxlen])
        if len(clips) >= a.docs:
            break
    T = max(len(c) for c in clips)
    print(f'{len(clips)} documents, token length min {min(len(c) for c in clips)} '
          f'max {T} mean {np.mean([len(c) for c in clips]):.0f}', flush=True)

    periods = [int(p) for p in a.periods.split(',')]
    dev = a.device
    res = {}

    for P in periods:
        t0 = time.time()
        # per absolute position and per within-window offset accumulators
        ce_pos = np.zeros(T); n_pos = np.zeros(T)
        ce_off = np.zeros(T); n_off = np.zeros(T)
        for s in range(0, len(clips), a.batch):
            chunk = clips[s:s + a.batch]
            B = len(chunk); Tb = max(len(c) for c in chunk)
            X = torch.zeros((B, Tb), dtype=torch.long)
            Y = torch.zeros((B, Tb), dtype=torch.long)
            M = torch.zeros((B, Tb), dtype=torch.bool)
            for r, steps in enumerate(chunk):
                X[r, :len(steps)] = torch.tensor([x for x, _ in steps])
                Y[r, :len(steps)] = torch.tensor([y for _, y in steps])
                M[r, :len(steps)] = True
            X, Y, M = X.to(dev), Y.to(dev), M.to(dev)
            model.dff = None                       # fresh state for the document
            torch.manual_seed(a.seed)              # same --init noise draw for every P
            allrows = torch.ones(B, dtype=torch.bool, device=dev)
            with torch.no_grad():
                for t in range(Tb):
                    flag = allrows if (P and t and t % P == 0) else None
                    logits, _ = model(X[:, t], flag=flag)
                    ce = F.cross_entropy(logits, Y[:, t], reduction='none') * M[:, t]
                    c = float(ce.sum()); n = float(M[:, t].sum())
                    ce_pos[t] += c; n_pos[t] += n
                    off = (t % P) if P else t
                    ce_off[off] += c; n_off[off] += n
        # Divergence check. With frozen weights and frozen BatchNorm running statistics the
        # recurrence can run away -- a state the stats do not cover is mis-normalized and
        # amplified through n_layers*depth BatchNorms. It shows up as a few positions with
        # astronomical loss, which would otherwise poison every mean in this report, so it
        # is flagged and the summary means are computed on a clipped copy.
        Lpos_raw = ce_pos / np.maximum(n_pos, 1)
        bad = int(((Lpos_raw > 20.0) & (n_pos > 0)).sum())
        if bad:
            first = int(np.argmax((Lpos_raw > 20.0) & (n_pos > 0)))
            print(f'  *** DIVERGED: {bad} of {int((n_pos>0).sum())} positions over 20 nats, '
                  f'first at position {first}, max {Lpos_raw.max():.3g} -- this model is '
                  f'unstable under long-horizon inference; horizon numbers below are void',
                  flush=True)
        Lpos = ce_pos / np.maximum(n_pos, 1)
        Loff = ce_off / np.maximum(n_off, 1)
        tot = ce_pos.sum() / max(n_pos.sum(), 1)
        res[P] = {'loss': float(tot), 'diverged': bad,
                  'by_offset': [float(x) for x in Loff[:(P or T)]],
                  'n_offset': [float(x) for x in n_off[:(P or T)]],
                  'by_pos': [float(x) for x in Lpos],
                  'n_pos': [float(x) for x in n_pos]}
        tag = 'no-reset' if P == 0 else f'reset/{P}'
        print(f'  P {tag:>10}  mean loss {tot:8.5f}   {time.time()-t0:6.1f}s', flush=True)

    # ── summary ──
    # Paired excess: for reset period P, compare every scored position against the SAME
    # position scored with the full document history.  Restricted to t >= P, so the first
    # window -- which contains the trivially predictable story opening -- is excluded and
    # every offset c is averaged over comparable absolute positions.
    #   excess(c) = extra nats the model pays at a position it can only see c tokens back
    # It starts high (no memory) and decays to ~0 at the model's effective memory horizon.
    def paired(P):
        if 0 not in res or P == 0:
            return None
        b0 = np.array(res[0]['by_pos']); n0 = np.array(res[0]['n_pos'])
        bp = np.array(res[P]['by_pos']); npp = np.array(res[P]['n_pos'])
        exc = np.zeros(P); cnt = np.zeros(P)
        for t in range(P, len(bp)):
            if npp[t] <= 0 or n0[t] <= 0:
                continue
            c = t % P
            exc[c] += (bp[t] - b0[t]) * npp[t]; cnt[c] += npp[t]
        tot = float((exc.sum()) / max(cnt.sum(), 1))
        return exc / np.maximum(cnt, 1), cnt, tot

    print('\nPAIRED EXCESS  extra nats vs full history, at a position with only c tokens '
          'of memory\n(windows past the first only, so the story opening is excluded):')
    summ = {}
    for P in periods:
        pr = paired(P)
        if pr is None:
            continue
        curve, cnt, tot = pr
        summ[P] = {'curve': [float(x) for x in curve], 'n': [float(x) for x in cnt],
                   'mean_excess': tot}
        pts = [c for c in (0, 1, 2, 4, 8, 16, 32, 64, 96, 127) if c < P and cnt[c] > 0]
        print(f'  P={P:4d}  mean excess {tot:+7.4f} | ' +
              '  '.join(f'c{c}:{curve[c]:+6.3f}' for c in pts))

    print('\nmean loss vs forced-reset period (all scored tokens):')
    base = res.get(0, {}).get('loss')
    for P in periods:
        d = res[P]['loss'] - (base if base is not None else 0)
        print(f'   P {("inf" if P==0 else P):>5}   loss {res[P]["loss"]:8.5f}   '
              f'excess over no-reset {d:+8.5f}')

    out = a.out or f'exp/mem.{os.path.basename(a.load).replace("checkpoint.pt.","")}.json'
    with open(out, 'w') as f:
        json.dump({'load': a.load, 'step': step, 'saved_args': {k: saved.get(k) for k in
                   ('n_layers','depth','clock','tap','ema','accumulate','init')},
                   'periods': {str(k): v for k, v in res.items()},
                   'paired': {str(k): v for k, v in summ.items()}}, f)
    print(f'\nwrote {out}')


if __name__ == '__main__':
    main()
