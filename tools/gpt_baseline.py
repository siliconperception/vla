"""A transformer baseline for vla.py's token efficiency: about as many trainable weights as a vla.py
model, trained on the same FineWeb shards with the same tokenizer and the same frozen Pythia-31m
embedding and lm_head, scored on vla.py's held-out documents by its EVAL rule.

usage: python tools/gpt_baseline.py NAME --docs DUMP [--d 512 --layers 7 --heads 8 --T 1024 --batch 1
       --lr 3e-4 --tokens 300e6 --shards 14]

DUMP comes from `vla.py --eval --eval_corpora fineweb --eval_dump DUMP`. Training rows are FineWeb's
sample-10BT parquet files (vla.py's first --shards of them), less vla.py's held-out 1/32 (crc32 of the
first 512 characters), each opened by <|endoftext|> and packed into --T token windows, --batch windows
a step. Pre-LN GPT: token -> frozen embedding (256) -> RMSnorm -> Linear 256->d + learned positions ->
--layers x (causal attention, GELU MLP 4d) -> LayerNorm -> Linear d->256 -> frozen lm_head. AdamW,
linear warmup then cosine to lr/10 at --tokens, gradient clipped at 1 (the standard recipe).
Writes log/exp.NAME (STEP and EVAL lines) and checkpoint/NAME.pt. EVAL: as tools/hf_eval.py --
each document after one <|endoftext|>, any token over 20 nats makes it runaway; clean, median, nats/char,
and the loss by position band."""
import argparse
import glob
import math
import os
import random
import time
import zlib
import numpy as np
import pyarrow.parquet as pq
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument('name')
ap.add_argument('--docs', required=True)
ap.add_argument('--d', type=int, default=512)
ap.add_argument('--layers', type=int, default=7)
ap.add_argument('--heads', type=int, default=8)
ap.add_argument('--T', type=int, default=1024)
ap.add_argument('--batch', type=int, default=1)
ap.add_argument('--lr', type=float, default=3e-4)
ap.add_argument('--warmup', type=int, default=2000)
ap.add_argument('--weight_decay', type=float, default=0.1)
ap.add_argument('--tokens', type=float, default=300e6)
ap.add_argument('--evals', default='5e6,10e6,20e6,50e6,75e6,100e6,125e6,155e6,200e6,250e6,300e6')
ap.add_argument('--shards', type=int, default=14)
ap.add_argument('--monitor', type=int, default=1000)
ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
ap.add_argument('--log', default=None)
ap.add_argument('--save', default=None)
a = ap.parse_args()
torch.manual_seed(a.seed)
torch.backends.cuda.matmul.allow_tf32 = True
dev = a.device
log = open(a.log or f'log/exp.{a.name}', 'a')


def emit(s):
    print(s, flush=True)
    log.write(s + '\n')
    log.flush()


# ── model ─────────────────────────────────────────────────────────────────────

REPO = 'EleutherAI/pythia-31m'
tok = AutoTokenizer.from_pretrained(REPO)
EOS = tok.eos_token_id
_lm = AutoModelForCausalLM.from_pretrained(REPO, dtype=torch.float32)


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.h = h
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
        self.fc, self.out = nn.Linear(d, 4 * d), nn.Linear(4 * d, d)

    def forward(self, x):
        B, T, D = x.shape
        q, k, v = self.qkv(self.ln1(x)).view(B, T, 3, self.h, D // self.h).permute(2, 0, 3, 1, 4)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        x = x + self.proj(y.transpose(1, 2).reshape(B, T, D))
        return x + self.out(F.gelu(self.fc(self.ln2(x))))


class GPT(nn.Module):
    def __init__(self, d, layers, heads, T):
        super().__init__()
        self.tok_embed = _lm.get_input_embeddings()                     # frozen, 50304 x 256
        self.lmhead = _lm.get_output_embeddings()                       # frozen, 256 -> 50304
        for p in list(self.tok_embed.parameters()) + list(self.lmhead.parameters()):
            p.requires_grad_(False)
        e = self.tok_embed.weight.shape[1]
        self.inp = nn.Linear(e, d)
        self.pos = nn.Parameter(torch.randn(T, d) * 0.02)
        self.blocks = nn.ModuleList(Block(d, heads) for _ in range(layers))
        self.ln_f = nn.LayerNorm(d)
        self.outp = nn.Linear(d, e)
        for n, p in self.named_parameters():
            if p.requires_grad and p.dim() == 2 and n != 'pos':
                nn.init.normal_(p, std=0.02 / (math.sqrt(2 * layers) if n.endswith(('proj.weight',
                                                                                     'out.weight')) else 1))
            elif p.requires_grad and n.endswith('bias'):
                nn.init.zeros_(p)

    def forward(self, idx):
        x = self.tok_embed(idx)
        x = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + 1e-6)      # RMSnorm, as vla.py's token grid
        x = self.inp(x) + self.pos[:idx.shape[1]]
        for b in self.blocks:
            x = b(x)
        return self.lmhead(self.outp(self.ln_f(x)))


model = GPT(a.d, a.layers, a.heads, a.T).to(dev)


def graph():
    """The model graph and parameter table, laid out as vla.py's startup log."""
    d, e, T, h, V = a.d, model.tok_embed.weight.shape[1], a.T, a.heads, model.tok_embed.weight.shape[0]
    n = lambda m: sum(p.numel() for p in m.parameters())
    rows = [('tok_embed', 'Embedding', f'token -> {e}', f'{n(model.tok_embed):,} frozen'),
            ('(token)', 'RMSnorm', f'{e} -> {e}', ''),
            ('inp', 'Linear', f'{e} -> {d}', f'{n(model.inp):,}'),
            ('pos', f'Add learned position (T {T})', f'{d}x{T} -> {d}x{T}', f'{model.pos.numel():,}')]
    for i, b in enumerate(model.blocks):
        rows += [(f'blocks.{i}.ln1', 'LayerNorm', f'{d}x{T} -> {d}x{T}', f'{n(b.ln1):,}'),
                 (f'blocks.{i}.qkv', 'Linear', f'{d}x{T} -> {3 * d}x{T}', f'{n(b.qkv):,}'),
                 (f'blocks.{i} (attention)', f'causal softmax attention, {h} heads of {d // h}',
                  f'{3 * d}x{T} -> {d}x{T}', ''),
                 (f'blocks.{i}.proj', 'Linear, + residual', f'{d}x{T} -> {d}x{T}', f'{n(b.proj):,}'),
                 (f'blocks.{i}.ln2', 'LayerNorm', f'{d}x{T} -> {d}x{T}', f'{n(b.ln2):,}'),
                 (f'blocks.{i}.fc', 'Linear+GELU', f'{d}x{T} -> {4 * d}x{T}', f'{n(b.fc):,}'),
                 (f'blocks.{i}.out', 'Linear, + residual', f'{4 * d}x{T} -> {d}x{T}', f'{n(b.out):,}')]
    rows += [('ln_f', 'LayerNorm', f'{d}x{T} -> {d}x{T}', f'{n(model.ln_f):,}'),
             ('outp', 'Linear', f'{d}x{T} -> {e}x{T}', f'{n(model.outp):,}'),
             ('lmhead', 'Linear', f'{e} -> {V}', f'{n(model.lmhead):,} frozen')]
    out = ['── model graph (one window of T tokens, execution order) ──',
           f'  #  {"module":34} {"op":46} {"in    out":>28} {"params":>24}']
    for i, (m, op, io, p) in enumerate(rows, 1):
        out.append(f'{i:3}  {m:34} {op:46} {io:>28} {p:>24}')
    groups = [('tok_embed', [model.tok_embed]), ('inp+pos', [model.inp]), ('blocks', [model.blocks]),
              ('ln_f+outp', [model.ln_f, model.outp]), ('lmhead', [model.lmhead])]
    out.append(f'PARAMS  {"module":10} {"trainable":>14} {"frozen":>14} {"total":>14}')
    tt = tf = 0
    for g, ms in groups:
        tr = sum(p.numel() for m in ms for p in m.parameters() if p.requires_grad)
        fr = sum(p.numel() for m in ms for p in m.parameters() if not p.requires_grad)
        tr += model.pos.numel() if g == 'inp+pos' else 0
        tt, tf = tt + tr, tf + fr
        out.append(f'PARAMS  {g:10} {tr:14,} {fr:14,} {tr + fr:14,}')
    out += ['PARAMS  ' + '-' * 55, f'PARAMS  {"TOTAL":10} {tt:14,} {tf:14,} {tt + tf:14,}',
            f'PARAMS  total {(tt + tf) / 1e6:.3f} M ({tt / 1e6:.3f} M trainable, {tf / 1e6:.3f} M frozen), '
            f'weights {(tt + tf) * 4 / 2 ** 20:.1f} MiB at fp32']
    return out


emit(f'ARGS {vars(a)}')
for line in graph():
    emit(line)

# ── data ──────────────────────────────────────────────────────────────────────

home = os.environ.get('HF_HOME') or os.path.expanduser('~/.cache/huggingface')
files = sorted(glob.glob(os.path.join(home, 'hub', 'datasets--HuggingFaceFW--fineweb', 'snapshots', '*',
                                      'sample', '10BT', '*.parquet')))[:a.shards]
if not files:
    raise SystemExit('no FineWeb sample-10BT parquet files in the HF cache')
emit(f'DATA {len(files)} files: {files[0]} ...')


def rows():
    """Training texts, row groups in a seeded random order (all files), shuffled within each."""
    rng = random.Random(a.seed)
    groups = [(f, g) for f in files for g in range(pq.ParquetFile(f).num_row_groups)]
    while True:
        rng.shuffle(groups)
        for f, g in groups:
            texts = pq.ParquetFile(f).read_row_group(g, columns=['text']).column('text').to_pylist()
            rng.shuffle(texts)
            for t in texts:
                if t and t.strip() and zlib.crc32(t[:512].encode('utf-8', 'ignore')) % 32 != 0:
                    yield t


def windows():
    buf, src, n = [], rows(), a.batch * (a.T + 1)
    while True:
        while len(buf) < n:
            texts = [next(src) for _ in range(64)]
            for ids in tok(texts)['input_ids']:
                buf += [EOS] + ids
        yield torch.tensor(buf[:n]).view(a.batch, a.T + 1)
        buf = buf[n:]


# ── eval ──────────────────────────────────────────────────────────────────────

import json
DOCS = json.load(open(a.docs))['fineweb']
NTOK = np.array([len(d) for d in DOCS], dtype=np.float64)
NCHAR = np.array([len(tok.decode(d)) for d in DOCS], dtype=np.float64)
BANDS = ((0, 64), (64, 256), (256, 1024))


def evaluate(seen):
    model.eval()
    per, bad = np.zeros(len(DOCS)), np.zeros(len(DOCS), dtype=bool)
    bsum, bcnt = np.zeros(len(BANDS)), np.zeros(len(BANDS))
    t0 = time.time()
    with torch.no_grad():
        for i, d in enumerate(DOCS):
            x = torch.tensor([EOS] + d, device=dev)[None]
            ce = F.cross_entropy(model(x[:, :-1])[0].float(), x[0, 1:], reduction='none')
            per[i], bad[i] = float(ce.mean()), bool((ce > 20.0).any())
            if not bad[i]:
                for k, (lo, hi) in enumerate(BANDS):
                    bsum[k] += float(ce[lo:hi].sum())
                    bcnt[k] += len(ce[lo:hi])
    model.train()
    clean = float(per[~bad].mean())
    npc = float((per * NTOK)[~bad].sum() / NCHAR[~bad].sum())
    emit(f'EVAL tokens {seen:13,} corpus fineweb clean {clean:9.6f} median {float(np.median(per)):9.6f} '
         f'nrun {int(bad.sum()):3d} docs {len(DOCS)} nats/char {npc:.4f} | '
         + ' '.join(f'{lo}-{hi - 1} {bsum[k] / max(1, bcnt[k]):.3f}' for k, (lo, hi) in enumerate(BANDS))
         + f' | wall {time.time() - t0:.1f}s')


# ── train ─────────────────────────────────────────────────────────────────────

decay = [p for n, p in model.named_parameters() if p.requires_grad and p.dim() == 2 and n != 'pos']
other = [p for n, p in model.named_parameters() if p.requires_grad and not (p.dim() == 2 and n != 'pos')]
opt = torch.optim.AdamW([{'params': decay, 'weight_decay': a.weight_decay},
                         {'params': other, 'weight_decay': 0.0}], lr=a.lr, betas=(0.9, 0.95), fused=dev == 'cuda')
per_step = a.batch * a.T
steps = int(a.tokens // per_step)
marks = sorted(int(float(t)) for t in a.evals.split(',') if t.strip())


def lr_at(s):
    if s < a.warmup:
        return a.lr * (s + 1) / a.warmup
    p = min(1.0, (s - a.warmup) / max(1, steps - a.warmup))
    return a.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * p)))


emit(f'TRAIN {steps:,} steps of {per_step:,} tokens ({a.batch} x {a.T}) = {steps * per_step:,} tokens; '
     f'evals at {marks}')
evaluate(0)
data, t0, run_loss, k = windows(), time.time(), 0.0, 0
for s in range(steps):
    xy = next(data).to(dev)
    for g in opt.param_groups:
        g['lr'] = lr_at(s)
    loss = F.cross_entropy(model(xy[:, :-1]).flatten(0, 1), xy[:, 1:].flatten())
    opt.zero_grad(set_to_none=True)
    loss.backward()
    gn = float(torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0))
    opt.step()
    run_loss, k = run_loss + float(loss), k + 1
    seen = (s + 1) * per_step
    if (s + 1) % a.monitor == 0:
        emit(f'STEP {s + 1:9} tokens {seen:13,} loss {run_loss / k:8.4f} grad {gn:8.3f} lr {lr_at(s):.2e} '
             f'{(s + 1) / (time.time() - t0):6.1f} steps/s')
        run_loss, k = 0.0, 0
    if marks and seen >= marks[0]:
        while marks and seen >= marks[0]:
            marks.pop(0)
        evaluate(seen)
        torch.save({'state_dict': {n: p for n, p in model.state_dict().items()
                                   if not n.startswith(('tok_embed', 'lmhead'))},
                    'args': vars(a), 'tokens': seen}, a.save or f'checkpoint/{a.name}.pt')
emit('DONE')
