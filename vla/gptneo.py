#!/usr/bin/env python3
# gptneo.py -- HuggingFace causal-LM baseline for the VLA comparison
# Silicon Perception Inc.
#
# Loads a pretrained transformer from the hub (default roneneldan/TinyStories-8M, a
# GPT-Neo trained on the same TinyStories corpus as VLA) and generates from it, so the
# two can be compared sample-for-sample. Same --pretrained/--generate CLI shape as
# vla.py. Inference only: no training loop.
#
# --eval adds the other half of the comparison: teacher-forced cross-entropy over a
# held-out split, framed exactly the way vla.py frames a clip.
#
# Parameter counts are printed split embedding / non-embedding. TinyStories-8M is "8M"
# by its non-embedding weights; its wte is 50257x256 = 12.9M more, so the count that
# lines up with VLA's 8.3M byte-vocabulary model is the non-embedding one.

import math
import time
import torch ; print('torch', torch.__version__)
import torch.nn.functional as F
import argparse
import itertools
import os

# Short dataset names, mirroring vla.py's _TEXT_DATASETS, but pointing at the held-out
# split where the corpus has one: name -> (hub repo, config, split, text column).
# Anything not listed is taken as a hub repo id directly (see _eval_source).
_EVAL_DATASETS = {
    'tiny': ('roneneldan/TinyStories',  None, 'validation', 'text'),
    'c4':   ('allenai/c4',              'en', 'validation', 'text'),
    'web':  ('Skylion007/openwebtext',  None, 'train',      'text'),   # train-only corpus
}

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--pretrained',   default='roneneldan/TinyStories-8M', nargs='?',
                    metavar='REPO', const='roneneldan/TinyStories-8M',
                    help='HuggingFace hub repo id to load (weights + config + tokenizer)')
parser.add_argument('--revision',     default=None,
                    help='hub branch, tag or commit (default: main)')
parser.add_argument('--generate',     default=False, action='store_true',
                    help='one-shot: load the model, generate from BOS+prompt, print, exit. '
                         'Without it the script only loads and reports the model')
parser.add_argument('--n',            default=200,   type=int,
                    help='tokens to generate for --generate')
parser.add_argument('--prompt',       default='',
                    help='generation prompt; BOS is always prepended, so leave empty to '
                         'generate from BOS alone')
parser.add_argument('--temperature',  default=1.0,   type=float,
                    help='sampling temperature for --generate (0 = argmax)')
# evaluation
parser.add_argument('--eval',         default=False, action='store_true',
                    help='compute teacher-forced validation loss over --dataset/--split '
                         'and report it. Each document is framed [BOS] tokens [EOS] and '
                         'every position after the first is scored, which is exactly the '
                         'clip framing and the gradient target vla.py trains on, so the '
                         'nats/token number is directly comparable to a VLA run at the '
                         'same tokenizer. Runs before --generate; the two are independent')
parser.add_argument('--dataset',      default='tiny',
                    help='--eval corpus: a short name (tiny | c4 | web) or any hub dataset '
                         'repo id')
parser.add_argument('--split',        default=None,
                    help="--eval split; default is the corpus's held-out split "
                         "(validation for tiny/c4), or 'validation' for a bare repo id")
parser.add_argument('--column',       default=None,
                    help='--eval text column (default: the corpus default, else "text")')
parser.add_argument('--streaming',    default=False, action='store_true',
                    help='--eval: stream the split instead of downloading it')
parser.add_argument('--examples',     default=0,     type=int,
                    help='--eval: stop after this many documents (0 = the whole split)')
parser.add_argument('--batch',        default=8,     type=int,
                    help='--eval documents per forward pass. Peak memory is '
                         'batch x longest-document x 50257 logits, so lower it for corpora '
                         'with documents near the 2048-token context')
parser.add_argument('--monitor',      default=100,   type=int,
                    help='--eval: print the running totals every N batches')
parser.add_argument('--seed',         default=None,  type=int)
parser.add_argument('--device',       default=None)
parser.add_argument('--verbose',      default=False, action='store_true',
                    help='print the torchinfo model summary')
args = parser.parse_args()

if args.device is None:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
if args.seed is None:
    args.seed = int.from_bytes(os.urandom(4), byteorder='big')
    print('seed', args.seed)

torch.manual_seed(args.seed)
print(args)

# ── model ─────────────────────────────────────────────────────────────────────

from transformers import AutoModelForCausalLM, AutoTokenizer

print(f'loading {args.pretrained} from the hub...')
tokenizer = AutoTokenizer.from_pretrained(args.pretrained, revision=args.revision)
model     = AutoModelForCausalLM.from_pretrained(args.pretrained, revision=args.revision)
model     = model.to(args.device).eval()
print('config', model.config)

if args.verbose:
    import torchinfo
    print(torchinfo.summary(model, col_names=['input_size', 'output_size', 'num_params'],
                            input_data=torch.zeros(1, 8, dtype=torch.long,
                                                   device=args.device), verbose=0))

# Embedding params = input embedding + (untied) output head. Both are vocab-sized, and a
# byte model has no comparable cost, so they are reported apart from the transformer body.
_emb  = set()
for _m in (model.get_input_embeddings(), model.get_output_embeddings()):
    if _m is not None:
        _emb.update(id(p) for p in _m.parameters())
_all  = sum(p.numel() for p in model.parameters())
_embn = sum(p.numel() for p in model.parameters() if id(p) in _emb)
print(f'{_all / 1e6:.6f} M params total, {_embn / 1e6:.6f} M embedding, '
      f'{(_all - _embn) / 1e6:.6f} M non-embedding')

# ── eval ──────────────────────────────────────────────────────────────────────

def _eval_source():
    """(repo, config, split, column) for --dataset, with --split/--column overriding."""
    if args.dataset in _EVAL_DATASETS:
        repo, cfg, split, col = _EVAL_DATASETS[args.dataset]
    else:
        repo, cfg, split, col = args.dataset, None, 'validation', 'text'
    return repo, cfg, (args.split or split), (args.column or col)


def _batched(it, n):
    it = iter(it)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


if args.eval:
    from datasets import load_dataset

    repo, cfg, split, col = _eval_source()
    print(f'loading {repo}' + (f' [{cfg}]' if cfg else '') + f' split {split} ...')
    rows = load_dataset(repo, cfg, split=split, streaming=args.streaming)
    if args.examples:
        rows = itertools.islice(rows, args.examples)

    # GPT-Neo has no separate BOS and no PAD: bos_token_id and eos_token_id are both
    # <|endoftext|>, which is also what the padding slots are filled with (they are
    # masked out of the loss, so their value only has to be a valid id).
    eot = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else tokenizer.bos_token_id
    bos = tokenizer.bos_token_id if tokenizer.bos_token_id is not None else eot
    max_len = getattr(model.config, 'max_position_embeddings', None) or 2048

    nll = 0.0            # summed cross-entropy over every scored position, in nats
    ntok = nbyte = 0     # scored positions, and utf-8 bytes of the text they cover
    nex = ntrunc = 0
    t0 = time.time()

    def _report(tag):
        # loss is the token-weighted mean over everything scored so far, not a mean of
        # per-batch means: documents differ in length, so those are not the same number.
        per_tok = nll / max(ntok, 1)
        print(f'{tag} examples {nex:8d} tokens {ntok:10d} bytes {nbyte:11d} '
              f'loss {per_tok:11.6f} ppl {math.exp(min(per_tok, 700)):12.4f} '
              f'bpb {nll / max(nbyte, 1) / math.log(2):9.6f} '
              f'wall {time.time() - t0:8.1f}s')

    for bi, chunk in enumerate(_batched(rows, args.batch)):
        seqs, texts = [], []
        for ex in chunk:
            text = ex.get(col) or ''
            if not text.strip():
                continue
            ids = tokenizer.encode(text)
            if len(ids) > max_len - 2:          # leave room for the BOS/EOS framing
                ids = ids[:max_len - 2]
                ntrunc += 1
            seqs.append([bos] + ids + [eot])
            # bytes actually scored -- decoding back is exact for BPE and stays honest
            # when a long document was truncated above
            texts.append(tokenizer.decode(ids))
        if not seqs:
            continue

        T   = max(len(s) for s in seqs)
        inp = torch.full((len(seqs), T), eot, dtype=torch.long)
        msk = torch.zeros((len(seqs), T), dtype=torch.long)
        for r, s in enumerate(seqs):
            inp[r, :len(s)] = torch.tensor(s, dtype=torch.long)
            msk[r, :len(s)] = 1
        inp, msk = inp.to(args.device), msk.to(args.device)

        # Right padding: the pad slots sit after every real token and attention is causal,
        # so nothing real can see them; they are dropped from the loss by `valid` below.
        with torch.no_grad():
            logits = model(input_ids=inp, attention_mask=msk).logits

        tgt   = inp[:, 1:]                      # position t is predicted from logits at t-1
        valid = msk[:, 1:].bool()
        ce    = F.cross_entropy(logits[:, :-1].reshape(-1, logits.size(-1)),
                                tgt.reshape(-1), reduction='none').view(tgt.shape)
        nll   += float((ce * valid).sum())
        ntok  += int(valid.sum())
        nbyte += sum(len(t.encode('utf-8')) for t in texts)
        nex   += len(seqs)

        if args.monitor and (bi % args.monitor) == 0:
            _report('EVAL')

    if ntok:
        _report('EVAL')
        print(f'\n{args.pretrained} on {repo} [{split}]:')
        print(f'  loss {nll / ntok:.6f} nats/token   ppl {math.exp(min(nll / ntok, 700)):.4f}')
        # bits per byte normalizes out the tokenizer, so it is the number that compares
        # against a byte-vocabulary VLA run (vla.py --tokenizer char) rather than only
        # against a run on this same BPE vocabulary.
        print(f'  bpb  {nll / nbyte / math.log(2):.6f} bits/byte '
              f'over {nex} documents, {ntok} tokens, {nbyte} bytes')
        if ntrunc:
            print(f'  note: {ntrunc} document(s) truncated to the {max_len}-token context')
    else:
        print('EVAL: no usable documents')

# ── generate ──────────────────────────────────────────────────────────────────

if args.generate:
    # BOS is prepended the way vla.py prepends START, so an empty --prompt still has
    # something to condition on and the sample starts at a document boundary.
    bos = tokenizer.bos_token_id
    if bos is None:
        bos = model.config.bos_token_id
    ids = [bos] + (tokenizer(args.prompt)['input_ids'] if args.prompt else [])
    ids = torch.tensor([ids], dtype=torch.long, device=args.device)

    # temperature 0 means argmax, which here is do_sample=False. Sampling is left
    # unfiltered (top_k=0, top_p=1) so it is the plain softmax the model was trained
    # for -- the same thing vla.py's sampler does.
    kw = ({'do_sample': True, 'temperature': args.temperature, 'top_k': 0, 'top_p': 1.0}
          if args.temperature > 0 else {'do_sample': False})
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=args.n,
                             pad_token_id=tokenizer.eos_token_id, **kw)
    print(tokenizer.decode(out[0], skip_special_tokens=False))
    raise SystemExit(0)
