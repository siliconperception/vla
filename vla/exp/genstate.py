#!/usr/bin/env python
"""Track the DFF state per token during FREE-RUNNING generation.

Tests whether the degenerate generation attractors coincide with a state explosion. Training
telemetry only ever reports dff_max under teacher forcing, where the model is fed ground-truth
tokens; generation is the loop where the model eats its own output, and that is where the
collapse appears. This prints per-token dff_max/dff_std alongside the emitted token, so a
state blow-up and the onset of a repeating cycle can be lined up in time.
"""
import os, sys
import numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs

ck_path, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 90
ck = torch.load(ck_path, map_location='cpu', weights_only=False); sa = ck['saved_args']
g = load_vla_defs(sa)
kw = dict(n_hidden=sa['n_hidden'], depth=sa['depth'], kernel=sa['kernel'], S=sa['context'],
          c_text=sa['c_text'], n_layers=sa['n_layers'], clock=sa.get('clock','sync'),
          accumulate=sa.get('accumulate',False), ema=sa.get('ema'),
          qproj=sa.get('qproj','none'), tap=sa.get('tap',False),
          tokenizer=sa['tokenizer'], head_norm=sa.get('head_norm','none'))
for k in ('clock_base','clock_max','clock_ends'):
    if k in sa: kw[k] = sa[k]
torch.manual_seed(1234)
m = g['VLAModel'](**kw); m.load_state_dict(ck['state_dict'])
m.init_mode = sa.get('init','relu'); m = m.cuda().eval()
tok = m.tok
print(f'{ck_path}  step {ck.get("step")}  clock {sa.get("clock")} base {sa.get("clock_base",2.0)}')

dff = m._new_dff(1, 'cuda'); clk = m._new_clock(1, 'cuda')
b = tok.start_id; out = []
print(f'{"tok":>4} {"dff_max":>11} {"dff_std":>8}  emitted')
with torch.no_grad():
    for t in range(n):
        bi = torch.tensor([b], dtype=torch.long, device='cuda')
        tg = m.tok_embed(bi).view(1, m.c_text, 1, 1).expand(-1, -1, m.S, m.S)
        stack, ctx = m._layers(dff, tg, clk)
        dff = [d.detach().clone() for d in stack]
        logits = m.readout(m.decoder(ctx))
        dmax = max(float(d.abs().max()) for d in dff)
        dstd = float(torch.cat([d.flatten() for d in dff]).std())
        p = F.softmax(logits[0] / 1.0, dim=-1)
        b = int(torch.multinomial(p, 1).item())
        out.append(b)
        if t % 5 == 0 or t > n - 6:
            s = tok.decode([b]) if hasattr(tok, 'decode') else str(b)
            print(f'{t:4d} {dmax:11.4g} {dstd:8.3f}  {s!r}')
