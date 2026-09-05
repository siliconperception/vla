#!/usr/bin/env python
"""Measure the REAL per-layer DFF time constant of a checkpoint.

    python exp/emadecay.py checkpoint/v11_fwedu100.pt [steps]

WHY. --ema_ladder documents its windows as ~1/ema tokens, which assumes each register is an
EMA of an external signal. It is not: _layers feeds the register back into its own layer's
input (x = _fb(li, dff[li]) + o), so the register's pole is

    p_i = 1 - a_i*(1 - G_i)      tau_i = -1/ln(p_i)

where G_i is that layer's effective linear gain (conv + BN + linout) on its own state. The
nominal window 1/a_i is the G_i = 0 case and is a LOWER BOUND; as G_i -> 1 the register
becomes an integrator no matter what a_i is. G_i is a property of the trained weights, so it
has to be measured rather than assumed.

METHOD. Perturbation decay, which needs no notion of a "zero" input. Two rows of one batch
are driven by an IDENTICAL token stream; after the state settles, ONE layer's register is
perturbed in one row only, and ||delta s_i[t]|| is tracked. Inputs stay identical from then
on, so the difference evolves under the system's own dynamics and its decay rate IS the
pole. Only layer i is perturbed per pass because the stack is feed-forward -- nothing
propagates DOWN -- so layer i's own mode is measured without contamination from below.

eval() + bn_track makes BatchNorm a frozen affine map, so the two rows do not interact
through batch statistics (see exp/batchdep.py) and the measurement is a pure per-row
property. The perturbation is small by construction, which keeps it in the linear regime
the pole describes.
"""
import os, sys, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs, stable_load

CK    = sys.argv[1]
T     = int(sys.argv[2]) if len(sys.argv) > 2 else 2500
SETTLE, EPS = 400, 1e-3

ck = stable_load(CK); sa = ck['saved_args']; g = load_vla_defs(sa)
kw = dict(n_hidden=sa['n_hidden'], depth=sa['depth'], kernel=sa['kernel'], S=sa['context'],
          c_text=sa['c_text'], n_layers=sa['n_layers'], clock=sa.get('clock', 'sync'),
          accumulate=sa.get('accumulate', False), ema=sa.get('ema'),
          qproj=sa.get('qproj', 'none'), tap=sa.get('tap', False),
          tokenizer=sa['tokenizer'], head_norm=sa.get('head_norm', 'none'))
for k in ('clock_base', 'clock_max', 'clock_ends', 'clip_dff', 'norm', 'norm_groups',
          'dff_norm', 'bn_track', 'bn_affine', 'bn_momentum', 'bn_eps'):
    if k in sa and sa[k] is not None: kw[k] = sa[k]
torch.manual_seed(1234)
m = g['VLAModel'](**kw); m.load_state_dict(ck['state_dict'])
m.init_mode = sa.get('init', 'relu')
# THE LADDER IS NOT IN saved_args['ema'] -- that stays the scalar. Only ema_ladder carries
# the per-layer rates (vla.py: "Only a SCALAR ema syncs back"), so rebuild the clock from it
# or the model under test is not the model that was trained.
m.set_clock(clock=sa.get('clock'), accumulate=sa.get('accumulate'), ema=sa.get('ema'),
            clock_base=sa.get('clock_base'), ema_ladder=sa.get('ema_ladder'))
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
m = m.to(dev).eval()
g['_tokenizer'] = m.tok
alphas = list(m.ema) if isinstance(m.ema, (list, tuple)) else [m.ema] * sa['n_layers']
print(f'{CK}  step {ck.get("step")}  ema_ladder {sa.get("ema_ladder")}  '
      f'rates {[round(a,5) for a in alphas]}')

# a real token stream, so the operating point is the one the model actually runs at
from datasets import load_dataset
toks = []
for ex in load_dataset('HuggingFaceFW/fineweb-edu', 'sample-10BT', split='train',
                       streaming=True):
    toks += g['_tokenizer'].encode(ex.get('text', '') or '')
    if len(toks) >= T + SETTLE + 8: break
toks = toks[:T + SETTLE + 8]

@torch.no_grad()
def decay(layer):
    """||delta s_layer[t]|| after perturbing ONLY that layer, one row of two."""
    m.dff = None
    x0 = torch.tensor([toks[0], toks[0]], dtype=torch.long, device=dev)
    m(x0, flag=torch.ones(2, dtype=torch.bool, device=dev))       # fresh state, both rows
    for t in range(1, SETTLE):                                     # settle to the attractor
        m(torch.tensor([toks[t]] * 2, dtype=torch.long, device=dev))
    s = m.dff[layer]
    print(f'  layer {layer+1}: ||s|| = {s[0].norm().item():.4e} before perturbation')
    m.dff = [d.clone() for d in m.dff]
    m.dff[layer][1] += EPS * s[0].norm() / max(s[0].numel() ** 0.5, 1) * torch.randn_like(s[0])
    out = []
    for t in range(SETTLE, SETTLE + T):
        m(torch.tensor([toks[t]] * 2, dtype=torch.long, device=dev))
        d = (m.dff[layer][1] - m.dff[layer][0]).norm().item()
        out.append(d)
        if d == 0.0 or not np.isfinite(d): break
    return np.array(out)

# The perturbation does NOT decay to zero: it falls fast, then sits on a PERSISTENT FLOOR
# that never decays further. Two components, and they must be reported separately:
#   * a contracting transient -- the register's leak, whose rate is the tau the ladder sets;
#   * a residue that never dies -- the marginal (integrator) direction, where s[t] = s[t-1]
#     + a*(input) has unit gain and a displacement is kept forever. Fitting the tail measures
#     only the residue and reports tau = inf for every layer, which says nothing about the
#     ladder. So the floor is estimated first and the fit runs on the EXCESS above it.
print(f'\n{"layer":>5} {"rate a_i":>9} {"nominal 1/a":>12} {"measured tau":>13} '
      f'{"pole p":>9} {"implied G":>10} {"kept forever":>13}')
taus = []
for li in range(sa['n_layers']):
    h = decay(li)
    floor  = float(np.median(h[int(0.75 * len(h)):]))     # the non-decaying residue
    excess = h - floor
    keep   = excess > 0.12 * max(excess[0], 1e-30)        # transient, before it hits the floor
    n      = int(np.argmin(keep)) if (~keep).any() else len(h)
    seg    = excess[:max(n, 3)]; ok = seg > 0
    if ok.sum() < 4:
        print(f'{li+1:>5}  transient too short to fit'); taus.append(np.nan); continue
    slope = np.polyfit(np.arange(len(seg))[ok], np.log(seg[ok]), 1)[0]
    p   = float(np.exp(slope))
    tau = (-1.0 / slope) if slope < 0 else np.inf
    G   = 1 - (1 - p) / alphas[li] if alphas[li] else np.nan
    taus.append(tau)
    print(f'{li+1:>5} {alphas[li]:9.5f} {1/alphas[li]:12.1f} {tau:13.1f} {p:9.6f} '
          f'{G:10.4f} {floor/h[0]*100:12.1f}%')
    # the raw curve, so a flat line (no decay) is never confused with a noise floor
    idx = [0, 10, 50, 100, 250, 500, 1000, 1500, 2000, len(h) - 1]
    print('        ||dS|| ' + '  '.join(f't{i}={h[i]:.3e}' for i in idx if i < len(h)))
fin = [t for t in taus if np.isfinite(t)]
if len(fin) > 1:
    print(f'\nspan across layers: {max(fin)/min(fin):.1f}x  '
          f'(tau {min(fin):.0f} -> {max(fin):.0f} tokens)')
