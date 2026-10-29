"""Rewrite a vla.py checkpoint keeping only some of its registers, e.g. the terms EVALI ablation
shows unused.

usage: python tools/drop_registers.py SRC DST --keep 1,2,5,6,7,8,9

--keep lists the registers to keep, 1-based in --ctx_ema order (as EVALI numbers them). ctx_cat's
read blocks of the dropped registers are deleted, and with them their running read RMS; --ctx_ema and
--ctx_tau shrink to the kept windows. --lmu: a Legendre memory's terms are coupled (every term's update
reads all the others), so only its trailing terms can go -- the kept ones must be terms 0..d-1. The
order-d memory then approximates the order-D one's leading terms (term 0 almost exactly, term 1 at
correlation ~0.9 and ~0.7 of the scale); their running read RMS is reset so it is measured afresh.
Not the same function, then, unless only whole groups go. The optimizer state is kept only if empty
(plain SGD); --weight_ema averages are dropped."""
import argparse
import torch

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('dst')
ap.add_argument('--keep', required=True)
a = ap.parse_args()

ck = torch.load(a.src, map_location='cpu', weights_only=True)
sd, sa = ck['state_dict'], dict(ck['saved_args'])
wins = [float(w) for w in str(sa['ctx_ema']).split(',')]
K, N = len(wins), int(sa['n_hidden'])
keep = sorted({int(k) - 1 for k in a.keep.split(',') if k.strip()})
if not keep or keep[0] < 0 or keep[-1] >= K:
    raise SystemExit(f'--keep {a.keep}: registers are 1..{K}')

reset = []
if sa.get('lmu'):
    for w in sorted({w for w in wins if w > 1}):
        group = [k for k in range(K) if wins[k] == w]
        kept = [k for k in group if k in keep]
        if kept != group[:len(kept)]:
            raise SystemExit(f'--lmu window {w:g}: registers {[k + 1 for k in group]} are terms '
                             f'0..{len(group) - 1}; only trailing ones can go, not {[k + 1 for k in kept]}')
        if kept and len(kept) < len(group):
            reset += kept
            print(f'window {w:g}: order {len(group)} -> {len(kept)}')

cw = sd['ctx_cat.weight']
off = cw.shape[1] - K * N
sd['ctx_cat.weight'] = torch.cat([cw[:, :off]] + [cw[:, off + k * N: off + (k + 1) * N] for k in keep], 1)
rms = sd['ctx_read_rms'].clone()
rms[reset] = 0                                          # 0 = not measured yet
sd['ctx_read_rms'] = rms[keep]

sa['ctx_ema'] = ','.join(f'{wins[k]:g}' for k in keep)
if sa.get('ctx_tau'):
    taus = [t for t in str(sa['ctx_tau']).split(',') if t.strip()]     # the windows over 1, then ',1'
    sa['ctx_tau'] = ','.join(taus[k] for k in keep if k < len(taus))
ck['state_dict'], ck['saved_args'] = sd, sa
ck['weight_ema'] = {}
if (ck.get('optimizer') or {}).get('state'):
    ck['optimizer'] = None
torch.save(ck, a.dst)
print(f'{a.src} -> {a.dst}: registers {K} -> {len(keep)} (kept {[k + 1 for k in keep]}), '
      f'ctx_ema {sa["ctx_ema"]}, ctx_tau {sa.get("ctx_tau")}')
