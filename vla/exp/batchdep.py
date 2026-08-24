#!/usr/bin/env python
"""Does inference depend on BATCH COMPOSITION?  --no-bn_track says it must.

With track_running_stats=True, eval-mode BatchNorm uses FROZEN running stats: it is a
per-channel affine map, foldable into the preceding conv, and the model is a pure function
of one sequence.  With track_running_stats=False, PyTorch sets bn_training = (running_mean
is None) even in .eval(), so BatchNorm normalizes by the CURRENT BATCH at inference too.
That makes the prediction for one document a function of the other documents beside it,
and at batch 1 it degenerates to InstanceNorm over the SxS grid.

This measures the size of that effect: identical documents scored (a) together in one
batch, (b) one at a time.  For a bn_track model the two must agree to float noise.
"""
import os, sys, numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs, stable_load

NDOC = int(sys.argv[2]) if len(sys.argv) > 2 else 16
ck = stable_load(sys.argv[1]); sa = ck['saved_args']; g = load_vla_defs(sa)
kw = dict(n_hidden=sa['n_hidden'], depth=sa['depth'], kernel=sa['kernel'], S=sa['context'],
          c_text=sa['c_text'], n_layers=sa['n_layers'], clock=sa.get('clock','sync'),
          accumulate=sa.get('accumulate',False), ema=sa.get('ema'),
          qproj=sa.get('qproj','none'), tap=sa.get('tap',False),
          tokenizer=sa['tokenizer'], head_norm=sa.get('head_norm','none'))
for k in ('clock_base','clock_max','clock_ends','clip_dff','norm','norm_groups',
          'dff_norm','bn_track','bn_affine','bn_momentum','bn_eps'):
    if k in sa and sa[k] is not None: kw[k] = sa[k]
torch.manual_seed(1234)
m = g['VLAModel'](**kw); m.load_state_dict(ck['state_dict'])
m.init_mode = sa.get('init','relu'); m = m.cuda().eval()
g['_tokenizer'] = m.tok

from datasets import load_dataset
docs = []
for ex in load_dataset('Skylion007/openwebtext', split='train[-3000:]'):
    t = ex.get('text','') or ''
    if not t.strip(): continue
    st, _ = g['clip_text'](t)
    if len(st) < 512: continue
    docs.append(st[:512])
    if len(docs) >= NDOC: break

def run(sel):
    """mean nats per doc for the given subset, scored as ONE batch."""
    B = len(sel); T = max(len(d) for d in sel)
    X = torch.zeros((B,T),dtype=torch.long); Y = torch.zeros((B,T),dtype=torch.long)
    M = torch.zeros((B,T),dtype=torch.bool)
    for r, st in enumerate(sel):
        X[r,:len(st)] = torch.tensor([x for x,_ in st])
        Y[r,:len(st)] = torch.tensor([y for _,y in st]); M[r,:len(st)] = True
    X,Y,M = X.cuda(), Y.cuda(), M.cuda()
    m.dff = None; torch.manual_seed(1234)
    rs = np.zeros(B); rn = np.zeros(B)
    with torch.no_grad():
        for t in range(T):
            lg,_ = m(X[:,t])
            ce = F.cross_entropy(lg, Y[:,t], reduction='none').cpu().numpy()
            k = M[:,t].cpu().numpy().astype(bool)
            rs += np.where(k, ce, 0); rn += k
    return rs/np.maximum(rn,1)

full = run(docs)                       # all NDOC together
solo = np.array([run([d])[0] for d in docs])   # one at a time (batch 1)
half = np.concatenate([run(docs[:NDOC//2]), run(docs[NDOC//2:])])
print(f'bn_track={sa.get("bn_track", True)}  n_hidden={sa["n_hidden"]} S={sa["context"]}')
print(f'{"doc":>4} {"batch"+str(NDOC):>10} {"batch1":>10} {"diff":>9} {"batch"+str(NDOC//2):>10}')
for i in range(min(NDOC,10)):
    print(f'{i:4d} {full[i]:10.4f} {solo[i]:10.4f} {solo[i]-full[i]:+9.4f} {half[i]:10.4f}')
print(f'MEAN {full.mean():10.4f} {solo.mean():10.4f} {solo.mean()-full.mean():+9.4f} '
      f'{half.mean():10.4f}')
print(f'max |batch{NDOC} - batch1| per doc: {np.abs(solo-full).max():.4f}')
