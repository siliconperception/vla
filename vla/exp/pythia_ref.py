#!/usr/bin/env python
"""Reference point: what a comparable HF transformer scores on OUR held-out set.

Evaluated on exactly the documents exp/score.py uses (openwebtext train[-3000:], minlen
512, maxlen 1024, first --docs) and exactly the same (x,y) pairs clip_text emits, so the
number is directly comparable to a VLA checkpoint's "clean"/"median", and to the bigram
floor from exp/ngram.py.

Read the result with two caveats in view, both of which favour VLA:
  * --corpus web: pythia was trained on the Pile, not openwebtext, so that set is
    CROSS-DOMAIN for it and in-domain for a web-trained VLA.  Its true openwebtext number
    would be lower than what we measure.  --corpus pile removes this caveat entirely and
    is the honest comparison for a --dataset pile VLA run: in-domain for both models.
  * parameter counts are not comparable in the way the names suggest.  pythia-31m is
    ~31M TOTAL including a 12.9M embedding table (50304x256) tied at both ends; its
    transformer body is only ~4.7M.  VLA has 30.4M TRAINABLE convolution parameters on
    top of the same 25.8M frozen pythia embeddings.  So VLA carries roughly 6x more
    compute-bearing parameters than the transformer it is being compared against.
Both caveats mean: if the transformer wins, the gap understates how much it wins by.
"""
import argparse, os, sys
import numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memtest import load_vla_defs, stable_load, heldout_docs

ap = argparse.ArgumentParser()
ap.add_argument('--models', nargs='+', default=['EleutherAI/pythia-31m'])
ap.add_argument('--corpus', default='web', choices=['tiny', 'web', 'pile', 'c4'],
                help="held-out set, shared with exp/score.py. 'web' reproduces PLAN.txt's "
                     "reference table and is CROSS-DOMAIN for pythia (Pile-trained); 'pile' "
                     "is the Pile's own validation split, in-domain for pythia AND for a "
                     "--dataset pile VLA run, which removes the cross-domain caveat from "
                     "both sides of the comparison")
ap.add_argument('--docs', type=int, default=400)
ap.add_argument('--minlen', type=int, default=512)
ap.add_argument('--maxlen', type=int, default=1024)
ap.add_argument('--thresh', type=float, default=20.0)
ap.add_argument('--device', default='cuda')
ap.add_argument('--ckpt', default='checkpoint/b5_long.final.pt')
a = ap.parse_args()

ck = stable_load(a.ckpt); sa = ck['saved_args']; g = load_vla_defs(sa)
g['_tokenizer'] = g['HFTokenizer']('EleutherAI/pythia-31m', 50304)

# shared with exp/score.py so the transformer and the VLA checkpoint are provably scored
# on the same documents in the same order -- the entire point of this reference.
docs = heldout_docs(g, a.corpus, a.docs, a.minlen, a.maxlen)
print(f'corpus {a.corpus}: {len(docs)} held-out docs, {sum(len(d) for d in docs)} tokens',
      flush=True)

from transformers import AutoModelForCausalLM
print(f'{"model":26} {"params":>10} {"body":>9} {"clean":>8} {"median":>8} {"runaway%":>9}')
print('-'*76)
for name in a.models:
    m = AutoModelForCausalLM.from_pretrained(name).to(a.device).eval()
    tot = sum(p.numel() for p in m.parameters())
    emb = sum(p.numel() for n_,p in m.named_parameters() if 'embed' in n_ or 'wte' in n_)
    per = []
    with torch.no_grad():
        for st in docs:
            x = torch.tensor([[i for i,_ in st]], device=a.device)
            y = torch.tensor([[j for _,j in st]], device=a.device)
            lg = m(x).logits.float()
            ce = F.cross_entropy(lg[0], y[0], reduction='none')
            per.append(float(ce.mean()))
    per = np.array(per); bad = per > a.thresh
    clean = per[~bad].mean() if (~bad).any() else float('nan')
    print(f'{name:26} {tot/1e6:9.1f}M {(tot-emb)/1e6:8.1f}M {clean:8.4f} '
          f'{np.median(per):8.4f} {100*bad.mean():9.1f}')
