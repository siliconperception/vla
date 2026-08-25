#!/usr/bin/env python3
# pythia.py -- train EleutherAI/pythia-31m FROM SCRATCH on VLA's exact token stream.
# Silicon Perception Inc.
#
# WHY THIS EXISTS
#   exp/pythia_ref.py scores the PUBLISHED pythia-31m, which saw ~300B tokens of the Pile.
#   Comparing a VLA run that has seen 1B tokens against that is not a comparison of
#   architectures, it is a comparison of training budgets.  This trains the same
#   architecture from random init on the same corpus, the same tokenizer, the same clip
#   framing and the same token budget, so the only remaining variable is the model.
#
# HOW "SAME DATA" IS GUARANTEED
#   Not by reimplementing the pipeline -- by importing it.  exp/memtest.load_vla_defs()
#   execs vla.py down to the worker boundary, which is BELOW clip_text, HFTokenizer,
#   _TEXT_DATASETS, _init_one_dataset and _make_iter.  This script therefore streams the
#   corpus through vla.py's own loader and frames every document with vla.py's own
#   clip_text, at the same --seed shuffle.  Held-out eval comes from the same shared
#   heldout_docs() that exp/score.py and exp/pythia_ref.py use, and reports clean / median
#   / runaway% by the same per-token criterion, so an EVAL line here and an EVAL line from
#   a VLA run are the same measurement on the same documents.
#
# THE FAIRNESS DECISION YOU MUST MAKE: --embed
#   VLA does not train its embeddings.  It borrows pythia-31m's PRETRAINED wte (25.76M
#   parameters, 84.5% of "31M", learned from ~300B tokens) and freezes it, training only
#   30.36M convolution parameters on top.
#     --embed frozen   (default) load those same pretrained embeddings and freeze them, so
#                      both models get the identical head start and only their
#                      compute-bearing parts learn from the budget.  This is the
#                      like-for-like comparison and the reason it is the default.
#     --embed scratch  everything random.  A literal "from scratch" run, but it hands VLA
#                      a 300B-token advantage on 84.5% of the parameters and will look
#                      worse for a reason that has nothing to do with the architecture.
#   Whichever you use, SAY WHICH.  They are not comparable to each other.
#
# BUDGET, NOT STEPS.  --tokens is the axis: a transformer sees --seq * --batch tokens per
# step while VLA sees --batch tokens per step, so step counts are meaningless across the
# two.  1B tokens == a 4M-step VLA run at batch 250.
#
#   python pythia.py --dataset pile --streaming --tokens 1000000000 \
#       --embed frozen --seq 512 --batch 16 --lr 0.001 \
#       --eval_interval 20000000 --log log/py.p1 --save checkpoint/py_p1.pt

import argparse, math, os, sys, time
import numpy as np
import torch, torch.nn.functional as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp'))
from memtest import load_vla_defs, heldout_docs

REPO = 'EleutherAI/pythia-31m'
_EVAL_THRESH = 20.0          # per-token nats; a doc with ANY token above this is runaway
_EVAL_MINLEN, _EVAL_MAXLEN = 512, 1024      # exp/score.py's protocol, do not drift

p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
p.add_argument('--dataset', default='pile', help='vla.py corpus name (tiny|c4|web|pile|...)')
p.add_argument('--streaming', action='store_true', help='stream the corpus (needed for pile)')
p.add_argument('--shards', type=int, default=None)
p.add_argument('--tokens', type=int, default=1_000_000_000,
               help='TOKEN budget, the axis that compares across architectures. 1e9 == a '
                    '4M-step VLA run at --batch 250')
p.add_argument('--seq', type=int, default=512, help='sequence length per row')
p.add_argument('--batch', type=int, default=16,
               help='rows per step, one forward. Memory here is dominated by the LOGITS, '
                    'not the model: batch x seq x 50304 in fp32, plus as much again inside '
                    'cross_entropy. At 16x512 that is ~1.65GB per copy, which coexists with '
                    'a concurrent VLA run on a 24GB card; 32 does not reliably')
p.add_argument('--lr', type=float, default=1e-3)
p.add_argument('--warmup', type=int, default=2000, help='steps of linear lr warmup')
p.add_argument('--schedule', default='cosine', choices=['cosine', 'const'])
p.add_argument('--weight_decay', type=float, default=0.01)
p.add_argument('--grad_clip', type=float, default=1.0)
p.add_argument('--amp', default='bf16', choices=['bf16', 'off'],
               help='bf16 autocast for the forward/backward. Master weights stay fp32 '
                    'either way. bf16 needs no GradScaler (unlike fp16) and is ~2x faster '
                    'on a 4090; eval always runs in fp32 so EVAL numbers never depend on it')
p.add_argument('--eval_interval', type=int, default=20_000_000,
               help='held-out eval every N TOKENS (0 disables). 2e7 gives ~50 points at 1e9')
p.add_argument('--eval_docs', type=int, default=400)
p.add_argument('--monitor', type=int, default=100, help='STEP line every N steps')
p.add_argument('--seed', type=int, default=None, help='default: drawn from os.urandom')
p.add_argument('--device', default=None)
p.add_argument('--log', default=None)
p.add_argument('--save', default='checkpoint/pythia31m.pt')
p.add_argument('--load', default=None)
a = p.parse_args()

if a.device is None:
    a.device = 'cuda' if torch.cuda.is_available() else 'cpu'
if a.seed is None:
    a.seed = int.from_bytes(os.urandom(4), byteorder='big')
    print('seed', a.seed)
torch.manual_seed(a.seed)
if a.log is None:
    a.log = os.devnull

def logline(s):
    print(s, flush=True)
    if a.log != os.devnull:
        with open(a.log, 'a') as f:
            print(s, file=f)

logline(f'ARGS {vars(a)}')

# ── vla.py's own data path ────────────────────────────────────────────────────
# A minimal saved_args: load_vla_defs only needs enough to exec vla.py's head. The
# architecture keys are irrelevant here -- we want its tokenizer and loader, not its model.
g = load_vla_defs({'tokenizer': 'pythia31m', 'dataset': a.dataset, 'context': 16,
                   'n_hidden': 256, 'c_text': 1, 'n_layers': 3, 'depth': 17, 'kernel': 3,
                   'init': 'zero', 'clock': 'fixed'})
g['_tokenizer'] = g['HFTokenizer'](REPO, 50304)
clip_text = g['clip_text']

# RE-SEED.  load_vla_defs() execs vla.py's head, and that head resolves its own --seed --
# drawing one from os.urandom when absent -- and calls torch.manual_seed with it.  So by
# this line the global RNG carries VLA's seed, not ours, and the model built below would be
# initialised from an unlogged value while --seed silently governed nothing but the data
# shuffle.  (It shows up as a second, unexplained 'seed N' line in the log.)
torch.manual_seed(a.seed)

# ── model ─────────────────────────────────────────────────────────────────────
from transformers import AutoConfig, AutoModelForCausalLM
cfg = AutoConfig.from_pretrained(REPO)
model = AutoModelForCausalLM.from_config(cfg)     # random init, exact pythia-31m shape
# pythia-31m's published config carries torch_dtype float16, so from_config() hands back an
# FP16 model.  Training that with AdamW and no GradScaler produces nan on the first step --
# it did, silently, and every EVAL read 100% runaway.  Master weights are fp32 here; speed
# comes from bf16 autocast (--amp), which has fp32's exponent range and needs no scaler.
model = model.float()

# Embeddings are ALWAYS pretrained and frozen -- not a flag, a fixed part of the protocol.
# VLA borrows pythia-31m's pretrained wte (25.76M parameters, 84.5% of "31M", learned from
# ~300B tokens) and trains none of it.  Giving this model random embeddings to learn from a
# 1B-token budget would hand VLA a 300B-token advantage on 84.5% of the parameters and make
# the transformer look worse for a reason that has nothing to do with architecture.  Frozen
# pretrained embeddings put both models on the same footing: identical head start, and only
# the compute-bearing part learns from the budget.  That is the comparison this file exists
# to make, so there is deliberately no way to ask for anything else.
ref = AutoModelForCausalLM.from_pretrained(REPO)
ref_sd, own_sd = ref.state_dict(), model.state_dict()
took = [k for k in own_sd if ('embed' in k or 'wte' in k) and k in ref_sd
        and ref_sd[k].shape == own_sd[k].shape]
assert took, 'no embedding tensors matched -- refusing to train against random embeddings'
model.load_state_dict({**own_sd, **{k: ref_sd[k].float() for k in took}})
emb_frozen = 0
for n_, prm in model.named_parameters():
    if 'embed' in n_ or 'wte' in n_:
        prm.requires_grad_(False); emb_frozen += prm.numel()
del ref
logline(f'embed: loaded {len(took)} pretrained tensor(s), {emb_frozen/1e6:.2f}M parameters '
        f'FROZEN -- mirrors VLA, which trains none of its embeddings')

model = model.to(a.device)
tot = sum(prm.numel() for prm in model.parameters())
trn = sum(prm.numel() for prm in model.parameters() if prm.requires_grad)
logline(f'params total {tot/1e6:.2f}M  trainable {trn/1e6:.2f}M  frozen {(tot-trn)/1e6:.2f}M'
        f'   (VLA for contrast: 30.36M trainable + 25.8M frozen embeddings)')

start_tok, start_step = 0, 0
if a.load and os.path.exists(a.load):
    ck = torch.load(a.load, map_location='cpu', weights_only=False)
    model.load_state_dict(ck['state_dict'])
    start_tok, start_step = ck.get('tokens', 0), ck.get('step', 0)
    logline(f'resumed {a.load} at {start_tok/1e6:.1f}M tokens, step {start_step}')

opt = torch.optim.AdamW([prm for prm in model.parameters() if prm.requires_grad],
                        lr=a.lr, weight_decay=a.weight_decay, betas=(0.9, 0.95))
total_steps = max(1, a.tokens // (a.seq * a.batch))

def lr_at(step):
    if step < a.warmup:
        return a.lr * (step + 1) / a.warmup
    if a.schedule == 'const':
        return a.lr
    prog = min(1.0, (step - a.warmup) / max(1, total_steps - a.warmup))
    return 0.5 * a.lr * (1 + math.cos(math.pi * prog))

# ── held-out eval, identical protocol to exp/score.py ─────────────────────────
_eval_docs = None
def heldout(tokens_seen, step):
    global _eval_docs
    if _eval_docs is None:
        _eval_docs = heldout_docs(g, a.dataset if a.dataset in ('web', 'pile', 'tiny')
                                  else 'pile', a.eval_docs, _EVAL_MINLEN, _EVAL_MAXLEN)
        logline(f'eval set: {len(_eval_docs)} docs, '
                f'{sum(len(d) for d in _eval_docs)} tokens')
    was = model.training
    model.eval()
    t0, per, bad = time.time(), [], []
    with torch.no_grad():
        for st in _eval_docs:
            x = torch.tensor([[i for i, _ in st]], device=a.device)
            y = torch.tensor([[j for _, j in st]], device=a.device)
            ce = F.cross_entropy(model(x).logits.float()[0], y[0], reduction='none')
            ce = torch.where(torch.isfinite(ce), ce, torch.full_like(ce, 1e30))
            per.append(float(ce.mean()))
            bad.append(bool((ce > _EVAL_THRESH).any()))   # ANY token, as score.py counts it
    if was:
        model.train()
    per, bad = np.array(per), np.array(bad)
    clean = float(per[~bad].mean()) if (~bad).any() else float('nan')
    logline('EVAL tokens {:12d} step {:9d} clean {:11.6f} ppl {:12.4f} median {:11.6f} '
            'runaway {:6.2f}% nrun {:4d} docs {:5d} wall {:7.1f}s'.format(
                tokens_seen, step, clean,
                math.exp(min(clean, 700)) if clean == clean else float('nan'),
                float(np.median(per)), 100.0 * float(bad.mean()), int(bad.sum()),
                len(per), time.time() - t0))

# ── token stream: vla.py's loader + clip framing, packed into fixed blocks ────
def token_stream():
    """vla.py's documents, framed by vla.py's clip_text, concatenated across boundaries --
    the same continuous stream a VLA run consumes, just chunked for a transformer."""
    ds = g['_init_one_dataset'](a.dataset, a.streaming, a.shards)
    col = g['_TEXT_DATASETS'][a.dataset][3]
    while True:
        for ex in g['_make_iter'](ds, g['_split_for_name'](a.dataset), a.streaming, a.seed):
            txt = (ex.get(col) or ex.get('text') or '') if hasattr(ex, 'get') else ''
            if not txt.strip():
                continue
            steps, _ = clip_text(txt)
            if not steps:
                continue
            yield [x for x, _ in steps] + [steps[-1][1]]   # inputs plus the final target

def blocks():
    need, buf = a.seq + 1, []
    for toks in token_stream():
        buf.extend(toks)
        while len(buf) >= need:
            yield buf[:need]; buf = buf[need:]

logline(f'target {a.tokens/1e9:.3f}B tokens = {total_steps} steps at {a.seq}x{a.batch} '
        f'= {a.seq*a.batch} tokens/step')

it = blocks()
tokens_seen, step = start_tok, start_step
next_eval = tokens_seen + a.eval_interval if a.eval_interval else float('inf')
losses, t0 = [], time.time()
model.train()
try:
    while tokens_seen < a.tokens:
        rows = [next(it) for _ in range(a.batch)]
        b = torch.tensor(rows, dtype=torch.long, device=a.device)
        x, y = b[:, :-1], b[:, 1:]
        for grp in opt.param_groups:
            grp['lr'] = lr_at(step)
        with torch.autocast(device_type=a.device.split(':')[0], dtype=torch.bfloat16,
                            enabled=(a.amp == 'bf16' and a.device.startswith('cuda'))):
            logits = model(x).logits
        # cross-entropy in fp32 regardless: the log-sum-exp over 50304 classes is where
        # reduced precision actually costs accuracy, and it is a trivial part of the cost.
        loss = F.cross_entropy(logits.float().reshape(-1, cfg.vocab_size), y.reshape(-1))
        if not torch.isfinite(loss):
            logline(f'*** HALT: non-finite loss at step {step}, {tokens_seen} tokens ***')
            break
        opt.zero_grad(set_to_none=True)
        loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(
            [prm for prm in model.parameters() if prm.requires_grad], a.grad_clip)
        opt.step()
        losses.append(float(loss)); step += 1; tokens_seen += a.seq * a.batch

        if step % a.monitor == 0:
            logline('STEP {:9d} tokens {:12d} loss {:9.6f} grad {:9.4f} lr {:11.9f} '
                    'tok/s {:9.0f}'.format(step, tokens_seen, float(np.mean(losses)),
                                           float(gn), lr_at(step),
                                           (tokens_seen - start_tok) / (time.time() - t0)))
            losses = []
        if tokens_seen >= next_eval:
            heldout(tokens_seen, step)
            next_eval += a.eval_interval
            torch.save({'saved_args': vars(a), 'state_dict': model.state_dict(),
                        'tokens': tokens_seen, 'step': step}, a.save)
except KeyboardInterrupt:
    pass

if a.eval_interval:
    heldout(tokens_seen, step)
torch.save({'saved_args': vars(a), 'state_dict': model.state_dict(),
            'tokens': tokens_seen, 'step': step}, a.save)
logline(f'DONE {tokens_seen} tokens, {step} steps, {(time.time()-t0)/3600:.2f}h')
