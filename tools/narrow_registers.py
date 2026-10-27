"""Rewrite a vla.py checkpoint so its registers are c_context wide (n_hidden = c_context) with a
K x K linout, as the same function up to one constant.

usage: python tools/narrow_registers.py SRC DST [--linout_kernel 3]

Every register is linear in o = linout(h) = W h + b, W [n_hidden, c_context]: it is W a + c b, a in
the c_context-wide space and c a data-independent scalar of the cascade. So the registers can hold a
instead, with the new linout the identity (centre tap, other taps zero) plus bias W+ b, and W folded
into everything that reads them: ctx_cat's register blocks (rescaled to the new running read RMS) and
the first conv of each decoder (unpadded, so the leftover b_perp = b - W W+ b folds exactly into its
bias). What is dropped: b_perp as ctx_cat reads it, through the registers. The optimizer state is kept
only if empty (plain SGD); --weight_ema averages are dropped."""
import argparse
import math
import torch

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('dst')
ap.add_argument('--linout_kernel', type=int, default=3)
a = ap.parse_args()

ck = torch.load(a.src, map_location='cpu', weights_only=True)
sd, sa = ck['state_dict'], dict(ck['saved_args'])
W = sd['linout.weight'].double()
assert W.shape[2:] == (1, 1), 'src linout must be 1x1'
W = W[:, :, 0, 0]                                       # [n_hidden, c_context]
b = sd['linout.bias'].double()
N, C = W.shape
K = len(str(sa['ctx_ema']).split(','))
Wp = torch.linalg.pinv(W)                               # [C, N]
beta = Wp @ b
b_perp = b - W @ beta
print(f'linout {N}x{C}: |W|_F {W.norm():.3f}, singular values {torch.linalg.svdvals(W)[[0, -1]].tolist()}, '
      f'|b| {b.norm():.4f}, |b_perp| {b_perp.norm():.4f}')

lk = a.linout_kernel
w = torch.zeros(C, C, lk, lk, dtype=torch.float64)
w[:, :, lk // 2, lk // 2] = torch.eye(C, dtype=torch.float64)
sd['linout.weight'], sd['linout.bias'] = w.float(), beta.float()

# ctx_cat: the K register blocks are its last K*N input channels; each reads r_k / rms_k
cw = sd['ctx_cat.weight'].double()
rms = sd['ctx_read_rms'].double()
g = W.norm() / math.sqrt(N)                             # rms(W a) / rms(a) for isotropic a
rms_new = rms / g
off = cw.shape[1] - K * N
blocks = [cw[:, off + k * N: off + (k + 1) * N, 0, 0] @ W * (rms_new[k] / rms[k]) for k in range(K)]
sd['ctx_cat.weight'] = torch.cat([cw[:, :off, 0, 0]] + blocks, 1)[:, :, None, None].float()
sd['ctx_read_rms'] = rms_new.float()

# decoders: unpadded first conv over o = W o' + b_perp
for d in ('text_dec', 'voc_dec', 'img_dec'):
    kw = f'{d}.tree.0.weight'
    if kw not in sd:
        continue
    t = sd[kw].double()
    sd[kw] = torch.einsum('oikl,ij->ojkl', t, W).float()
    sd[f'{d}.tree.0.bias'] = (sd[f'{d}.tree.0.bias'].double()
                              + torch.einsum('oikl,i->o', t, b_perp)).float()

sa['n_hidden'], sa['linout_kernel'] = C, lk
ck['state_dict'], ck['saved_args'] = sd, sa
ck['weight_ema'] = {}
if (ck.get('optimizer') or {}).get('state'):
    ck['optimizer'] = None
torch.save(ck, a.dst)
print(f'{a.src} -> {a.dst}: registers {K} x {N} -> {K} x {C}, linout {lk}x{lk}')
