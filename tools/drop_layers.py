"""Rewrite a --layers checkpoint to keep only its first L layers (default 1).

usage: python tools/drop_layers.py SRC DST [--keep 1]

Each upper layer adds its addend d to the output (o = o1 + d2 + ...), so dropping the top layers
is the model with those addends at zero. Their weights (up.<i>.*) go, the saved args say
--layers L, and with L = 1 the upper windows (up_ema, the up_rate buffer) go too. The optimizer
state is dropped (its parameter list no longer matches; plain SGD at momentum 0 keeps none) and so
are --weight_ema averages. vla.py restores --layers from a checkpoint, so this is the way to shrink
one."""
import argparse
import torch

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('dst')
ap.add_argument('--keep', type=int, default=1, help='layers to keep (>= 1)')
a = ap.parse_args()

ck = torch.load(a.src, map_location='cpu', weights_only=False)
sa = dict(ck['saved_args'])
L = int(sa.get('layers') or 1)
if not 1 <= a.keep < L:
    raise SystemExit(f'{a.src} has {L} layer(s): --keep must be 1..{L - 1}')
sd = ck['state_dict']
gone = [k for k in sd if k.startswith('up.') and int(k.split('.')[1]) >= a.keep - 1]
if a.keep == 1:
    gone += [k for k in sd if k == 'up_rate']
for k in gone:
    del sd[k]
sa['layers'] = a.keep
if a.keep == 1:
    sa['up_ema'] = None
ck['saved_args'] = sa
ck['optimizer'] = None
ck['weight_ema'] = {}
torch.save(ck, a.dst)
print(f'{a.src}: {L} -> {a.keep} layer(s), {len(gone)} tensors dropped, step {ck.get("step")}, wrote {a.dst}')
