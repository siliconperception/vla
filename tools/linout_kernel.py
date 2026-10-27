"""Give a vla.py checkpoint a K x K linout, as the same function: the old 1x1 weights become the
centre tap, the other taps zero (as --linout_kernel initializes a new model).

usage: python tools/linout_kernel.py SRC DST [--linout_kernel 3]"""
import argparse
import torch

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('dst')
ap.add_argument('--linout_kernel', type=int, default=3)
a = ap.parse_args()

ck = torch.load(a.src, map_location='cpu', weights_only=True)
w = ck['state_dict']['linout.weight']
assert w.shape[2:] == (1, 1), 'src linout must be 1x1'
lk = a.linout_kernel
w2 = w.new_zeros(w.shape[0], w.shape[1], lk, lk)
w2[:, :, lk // 2, lk // 2] = w[:, :, 0, 0]
ck['state_dict']['linout.weight'] = w2
ck['saved_args'] = dict(ck['saved_args'], linout_kernel=lk)
ck['weight_ema'] = {}
torch.save(ck, a.dst)
print(f'{a.src} -> {a.dst}: linout {tuple(w.shape)} -> {tuple(w2.shape)}')
