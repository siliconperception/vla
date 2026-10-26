"""EVALM's minimal pairs (BLiMP / ComVE / Winogrande, as vla.py --eval_pairs builds them) scored
by a reference HF causal LM, each sentence from a bare document start, for calibration.
usage: python exp/pairs_ref.py MODEL [N] [--trust] (--trust: the model's own code from its repo)"""
import sys, collections
import numpy as np, torch
from datasets import get_dataset_config_names, load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

trust = '--trust' in sys.argv
argv = [a for a in sys.argv if a != '--trust']
name, N = argv[1], int(argv[2]) if len(argv) > 2 else 1000
tok = AutoTokenizer.from_pretrained(name, trust_remote_code=trust)
lm = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32, trust_remote_code=trust).cuda().eval()
n_all = sum(p.numel() for p in lm.parameters())
emb = {id(m.weight): m.weight.numel() for m in (lm.get_input_embeddings(), lm.get_output_embeddings()) if m is not None}
params = f'params {n_all / 1e6:.1f}M, {(n_all - sum(emb.values())) / 1e6:.1f}M without token embedding/lm_head'

bos = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
enc = lambda t: tok.encode(t, add_special_tokens=False)


def sentence(t):
    t = t.strip().rstrip('.').strip()
    return t[:1].upper() + t[1:] + '.'


sets = collections.defaultdict(list)          # (ids a, ids b, scored from, group)
cfgs = get_dataset_config_names('nyu-mll/blimp')
for c in cfgs:
    for ex in load_dataset('nyu-mll/blimp', c, split='train').select(range(-(-N // len(cfgs)))):
        sets['blimp'].append(([bos] + enc(ex['sentence_good']), [bos] + enc(ex['sentence_bad']), 1, ex['field']))
for ex in load_dataset('tasksource/ComVE', split='test').select(range(min(N, 999))):
    ch = [sentence(t) for t in ex['choices_list']]
    sets['comve'].append(([bos] + enc(ch[ex['labels']]), [bos] + enc(ch[1 - ex['labels']]), 1, 'comve'))
rows = load_dataset('allenai/winogrande', 'winogrande_xl', split='validation')
for ex in rows.select(range(min(N, len(rows)))):
    pre, post = ex['sentence'].split('_', 1)
    o = [[bos] + enc(pre + ex[f'option{k}']) for k in (1, 2)]
    r = int(ex['answer']) - 1
    sets['wino'].append((o[r] + enc(post), o[1 - r] + enc(post), (len(o[r]), len(o[1 - r])), 'wino'))


@torch.no_grad()
def ce(q):
    x = torch.tensor([q]).cuda()
    o = lm(x)
    lp = torch.log_softmax((o.logits if hasattr(o, 'logits') else o[0])[0, :-1].float(), -1)
    return (-lp.gather(1, x[0, 1:, None])[:, 0]).cpu().numpy()


out = []
for s, pairs in sets.items():
    right, tk, mg, grp = [], [], [], collections.defaultdict(list)
    for a, b, f, g in pairs:
        fa, fb = (f, f) if isinstance(f, int) else f
        ca, cb = ce(a)[fa - 1:], ce(b)[fb - 1:]
        right.append(ca.sum() < cb.sum()); tk.append(ca.mean() < cb.mean()); mg.append(cb.mean() - ca.mean())
        grp[g].append(right[-1])
    o = f'{s} n{len(pairs)} acc {100 * np.mean(right):.1f}% acc_tok {100 * np.mean(tk):.1f}% margin {np.mean(mg):+.4f}'
    if s == 'blimp':
        o += ' (' + ' '.join(f'{g} {100 * np.mean(v):.1f}' for g, v in sorted(grp.items())) + ')'
    out.append(o)
print(f'REF {name} ({params}): ' + ' | '.join(out))
