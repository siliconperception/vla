#!/usr/bin/env python3
# vla.py -- Vision-Language-Action recurrent CNN (text-only core)
# Silicon Perception Inc.
#
# Each step the current token is embedded, broadcast over an SxS grid and concatenated with
# the K DFF registers; one 1x1 conv (ctx_cat) reads that concat into a conv chain
# (ContextCNN), a 1x1 (linout) projects the result back to register width, and the registers
# are written as a Laplacian-pyramid cascade: register k blends toward what registers 1..k-1
# missed, at its own rate 1/W_k. The text decoder reads the layer output to next-token logits
# through a frozen, borrowed lm_head. No attention, no positional encoding.
#
# Images: a frozen ResNet-50 turns a 224x224 crop of the image into a [2048, 7, 7] feature map
# that is concatenated with the token grid. An image-caption example is <STX> caption <ETX>
# with the image present at every token, seen through a fresh random 224x224 crop each token:
# a close-up at native resolution (only an image with a side under 224 is scaled up, uniformly,
# to fill the crop) or, for --full_crops of them, a full view of the whole image scaled so its
# shorter side is 224; text-only rows get a zero image map.
#
# Built to be extended: the input side is a LIST of grids concatenated in front of ctx_cat, and
# the text readout is a self-contained decoder module that other decoders (e.g. actions) can
# sit beside.

import argparse
import collections
import datetime
import glob
import io
import itertools
import json
import math
import os
import queue
import random
import re
import sys
import threading
import time
import zlib

import numpy as np
import torch ; print('torch', torch.__version__)
import torch.nn as nn
from torch.nn import functional as F

STX_TEXT = '<STX>'          # how the document-start token renders
ETX_TEXT = '<ETX>'          # how the document-end token renders
DOT_TEXT = '\xb7'           # how any other unprintable character renders
_ESCAPES = {'\n': '\\n', '\t': '\\t', '\r': '\\r'}

_GEN_SAMPLE = 200           # tokens in each periodic GEN sample (--n is for --generate)

# Held-out eval protocol constants (exp/score.py and PLAN.txt's reference table use the same
# selection). Pinned, not exposed: changing one makes EVAL lines incomparable with history.
_EVAL_MINLEN = 512          # documents shorter than this (in tokens) are skipped ...
_EVAL_MINLEN_SHORT = {'simplestories': 128}   # ... except on short-document corpora
_EVAL_MAXLEN = 1024         # and each is clipped to this many
_EVAL_BATCH = 400           # rows per eval forward chunk
_EVAL_THRESH = 20.0         # a document with ANY token above this many nats is "runaway"


def _eval_minlen(corpus):
    if corpus in _IMAGE_DATASETS:
        return 1                    # captions are short; every held-out caption counts
    return _EVAL_MINLEN_SHORT.get(corpus, _EVAL_MINLEN)


# Image-caption corpora: a local directory of parquet files (see exp/img_prep.py) with an
# encoded 'image', an 'id' and the caption column.
_IMAGE_DATASETS = {
    'imagenet21k': dict(dir='/data/imagenet21k_recap', caption='recaption'),
}

_IMAGE_ENCODERS = {'resnet50': 'timm/resnet50.a1_in1k'}   # frozen; [3,224,224] -> [2048,7,7]
_IMG_BANK = 1024            # image canvas side; larger images keep their central 1024x1024
_IMG_IN = 224               # crop side = encoder input side
_IMG_MEAN = (0.485, 0.456, 0.406)
_IMG_STD = (0.229, 0.224, 0.225)


# ── tokenizer ─────────────────────────────────────────────────────────────────
# The vocabulary, token embedding and lm_head are borrowed from a pretrained causal LM and
# frozen; the CNN meets them through the ctx_cat read on the way in and the decoder on the
# way out.

_TOKENIZERS = {
    'pythia14m':  'EleutherAI/pythia-14m',       # hidden 128, vocab 50304
    'pythia31m':  'EleutherAI/pythia-31m',       # hidden 256, vocab 50304
    'pythia70m':  'EleutherAI/pythia-70m',       # hidden 512, vocab 50304
    'pythia160m': 'EleutherAI/pythia-160m',      # hidden 768, vocab 50304
    'tiny8m':     'roneneldan/TinyStories-8M',   # hidden 256, vocab 50257 (tied embed/head)
}


class HFTokenizer:
    """A pretrained BPE tokenizer. GPT-NeoX/Neo have one <|endoftext|> id, so START and END
    are the same token and a clip is [EOT] text [EOT]."""

    def __init__(self, repo, vocab_size):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(repo)
        self.tok.model_max_length = int(1e12)   # recurrent: no context window, never truncate
        eot = self.tok.eos_token_id
        self.end_id = eot if eot is not None else self.tok.bos_token_id
        bos = self.tok.bos_token_id
        self.start_id = bos if bos is not None else self.end_id
        self.vocab_size = vocab_size            # the embedding's rows, not len(tokenizer)

    def encode(self, text): return self.tok.encode(text, add_special_tokens=False)
    def decode(self, ids):  return self.tok.decode(ids)


_tokenizer = None           # bound to model.tok once the model is built


def _printable(s):
    """Escape whitespace and mask unprintable characters for one-line display."""
    return ''.join(_ESCAPES.get(c, c if c.isprintable() else DOT_TEXT) for c in s)


def _decode_plain(ids):
    """Token ids -> plain text with the framing markers dropped (what a judge LM reads)."""
    body = [t for t in ids if t not in (_tokenizer.start_id, _tokenizer.end_id)]
    return _tokenizer.decode(body) if body else ''


def _render(ids):
    """Token ids -> display text. The marker shows as <STX> when it opens the sequence,
    <ETX> at the end, and <ETX><STX> at a document boundary in the middle."""
    out, run = [], []
    for n, t in enumerate(ids):
        if t in (_tokenizer.start_id, _tokenizer.end_id):
            if run:
                out.append(_printable(_tokenizer.decode(run)))
                run = []
            out.append(STX_TEXT if n == 0 else
                       ETX_TEXT + STX_TEXT if n < len(ids) - 1 else ETX_TEXT)
        else:
            run.append(t)
    if run:
        out.append(_printable(_tokenizer.decode(run)))
    return ''.join(out)


# ── args ──────────────────────────────────────────────────────────────────────
# Defaults are the v395 baseline.

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# architecture (restored from a checkpoint on --load)
parser.add_argument('--context',    default=8,    type=int, help='DFF grid side S (SxS)')
parser.add_argument('--n_hidden',   default=512,  type=int, help='channels per DFF register')
parser.add_argument('--c_context',  default=384,  type=int,
                    help='ContextCNN width: ctx_cat reads the concat down to it and linout '
                         'projects it back up to --n_hidden')
parser.add_argument('--depth',      default=8,    type=int, help='ContextCNN conv layers')
parser.add_argument('--kernel',     default=3,    type=int, help='ContextCNN kernel (odd)')
parser.add_argument('--tokenizer',  default='pythia31m', choices=sorted(_TOKENIZERS),
                    help='borrowed vocabulary, token embedding and lm_head (frozen)')
parser.add_argument('--ctx_ema',    default='256,64,16,4,1', metavar='W1,W2,...',
                    help='register windows in tokens, slowest first: register k blends at '
                         'rate 1/W_k toward the layer output minus registers 1..k-1, so with a '
                         'last window of 1 the registers sum exactly to the output')
parser.add_argument('--ctx_read_norm', default=1.0, type=float, metavar='S',
                    help='read each register scaled to RMS S, using a running RMS per '
                         'register (momentum 0.01, updated in training only); 0 = off')
parser.add_argument('--dec_tree_kernels', default='3,3,3', metavar='K1,K2,...',
                    help='text decoder: unpadded linear convs; all but the last run at '
                         '--dec_width, the last maps to the embedding width; whatever grid is '
                         'left is average-pooled. sum(k-1) <= S-1')
parser.add_argument('--dec_width',  default=256,  type=int, help='text decoder tree width')
parser.add_argument('--bn_momentum', default=0.1, type=float,
                    help='ContextCNN BatchNorm running-statistics momentum (0 = cumulative)')
parser.add_argument('--init',       default='zero', choices=['zero', 'gaussian', 'relu'],
                    help='DFF register value at every document start')
parser.add_argument('--image_encoder', default=None, choices=['none'] + sorted(_IMAGE_ENCODERS),
                    help='frozen image encoder whose feature map joins the input concat; '
                         'default: resnet50 if --mix or --eval_corpora names an image corpus, '
                         'else none')
# data
parser.add_argument('--dataset',    default='smolfwedu', help='training corpus (see _TEXT_DATASETS)')
parser.add_argument('--mix',        default=None, metavar='NAME:FRAC,...',
                    help='several corpora, each given an exact share of the --batch slots '
                         '(largest remainder), e.g. smolfwedu:0.5,imagenet21k:0.5. Overrides '
                         '--dataset. Image corpora: see _IMAGE_DATASETS')
parser.add_argument('--full_crops', default=0.5, type=float, metavar='P',
                    help='share of image crops that are full views: the whole image scaled '
                         '(aspect kept) so its shorter side is 224, cropped to 224x224 at a '
                         'random offset along the longer side, no padding; the rest are '
                         'native-resolution close-ups. Resuming a checkpoint from before this '
                         'option keeps 0 unless the flag is given')
parser.add_argument('--image',      default=None, metavar='PATH',
                    help='--generate/--vis: condition on this image (caption it)')
parser.add_argument('--shards',     default=None, type=int, help='load only the first N parquet shards')
parser.add_argument('--streaming',  default=False, action='store_true')
parser.add_argument('--shuffle',    default=True, action=argparse.BooleanOptionalAction,
                    help='--no-shuffle reads the corpus in file order; with --seed and '
                         '--workers 1 that makes two runs bit-identical')
parser.add_argument('--workers',    default=12,   type=int, help='clip-builder threads')
parser.add_argument('--batch',      default=250,  type=int, help='independent document streams')
# optimization
parser.add_argument('--lr_max',     default=0.01, type=float, help='peak / constant lr')
parser.add_argument('--lr_min',     default=1e-4, type=float, help='coswarm start lr')
parser.add_argument('--lr_period',  default=20000, type=int, help='coswarm rise length in steps')
parser.add_argument('--schedule',   default='coswarm', choices=['const', 'coswarm'],
                    help='const: --lr_max throughout. coswarm: half-cosine rise from --lr_min '
                         'to --lr_max over --lr_period global steps, then hold')
parser.add_argument('--momentum',   default=0.0,  type=float, help='SGD momentum')
parser.add_argument('--weight_decay', default=0.0, type=float, help='SGD weight decay')
parser.add_argument('--run_steps',  default=None, type=int, help='stop after N steps of this run')
parser.add_argument('--seed',       default=None, type=int)
parser.add_argument('--device',     default=None)
# checkpoint / log
parser.add_argument('--load',       default=None, help='resume from a checkpoint')
parser.add_argument('--save',       default='checkpoint.pt')
parser.add_argument('--checkpoint', default=4000, type=int, help='save every N steps')
parser.add_argument('--log',        default=None)
parser.add_argument('--monitor',    default=100,  type=int, help='STEP line every N steps')
# periodic generation
parser.add_argument('--gen_interval', default=4000, type=int, help='GEN sample every N steps')
parser.add_argument('--gen_score',  default=None, nargs='?', const='EleutherAI/pythia-70m',
                    metavar='MODEL',
                    help='score GEN samples for fluency with a frozen reference LM (CPU), '
                         'anchored between real corpus text (100%%) and the same text with its '
                         'words shuffled (0%%); read it with rep1, never alone')
parser.add_argument('--prompt',     default='', help='extra GEN prompt; prompt for --generate/--vis')
parser.add_argument('--temperature', default=1.0, type=float, help='sampling temperature')
parser.add_argument('--gen_images', default=8, type=int, metavar='N',
                    help='image models: caption N held-out images at every GEN for the --gen_vis '
                         'panel, a new random set every --eval_interval steps; the log gets one '
                         'GENI/REF pair per GEN, taking the set in turn; 0 = off')
parser.add_argument('--gen_vis', default=True, action=argparse.BooleanOptionalAction,
                    help='image models: a window (top-left quarter of the screen) showing the '
                         'GEN image captions, redrawn at every GEN; also saved as <log>.gen.png')
parser.add_argument('--sample_vis', default=True, action=argparse.BooleanOptionalAction,
                    help='image models: a window (top-right quarter) showing one training '
                         'image example recorded after every GEN -- the image, its caption, '
                         'and the crop seen at each token with that token; also saved as '
                         '<log>.sample.png')
# periodic held-out eval
parser.add_argument('--eval_interval', default=20000, type=int,
                    help='held-out EVAL every N steps (0 = off)')
parser.add_argument('--eval_corpora', default=None, help='comma-separated; default --dataset')
parser.add_argument('--eval_docs',  default=400,  type=int, help='held-out documents per corpus')
parser.add_argument('--eval_bands', default='1024,8192', metavar='R1,R2,...',
                    help='EVALB: held-out loss split by target-token frequency rank ("" = off)')
parser.add_argument('--eval_info',  default=0,    type=int, metavar='N',
                    help='EVALI on N documents: register rms/rank/overlap and read ablations')
parser.add_argument('--eval_gen',   default=0,    type=int, metavar='N',
                    help='EVALG on N prompts: continuations judged by --eval_gen_judge')
parser.add_argument('--eval_gen_judge', default='EleutherAI/pythia-410m', metavar='MODEL')
parser.add_argument('--eval_gen_prompt', default=32, type=int, metavar='P', help='prompt tokens')
parser.add_argument('--eval_gen_len', default=96, type=int, metavar='C', help='continuation tokens')
parser.add_argument('--eval_reach', default=0,    type=int, metavar='N',
                    help='EVALX on N spliced rows: excess loss from losing history older than c')
parser.add_argument('--eval_reach_period', default=256, type=int, metavar='P')
# one-shot modes (no training)
parser.add_argument('--generate',   default=False, action='store_true',
                    help='load, generate --n tokens from <STX>+--prompt, print, exit')
parser.add_argument('--n',          default=200,  type=int, help='--generate length')
parser.add_argument('--eval',       default=False, action='store_true',
                    help='load, run the held-out eval protocol (EVAL lines + table), exit')
parser.add_argument('--eval_json',  default=None, help='--eval: also write results as JSON')
parser.add_argument('--vis',        default=False, action='store_true',
                    help='live generation view: layer output and registers (std across '
                         'channels per grid cell) and P(next token); x exits')
parser.add_argument('--delay',      default=0.1,  type=float, help='--vis seconds per frame')
parser.add_argument('--cmap',       default='viridis', help='--vis colormap')
parser.add_argument('--push',       default=False, action='store_true',
                    help='push the --load checkpoint to the hub as --hub_repo, exit')
parser.add_argument('--hub_repo',   default='siliconperception/VLA')
parser.add_argument('--private',    default=False, action='store_true', help='--push: private repo')
parser.add_argument('--pretrained', default=None, nargs='?', const='siliconperception/VLA',
                    metavar='REPO', help='load weights + architecture from a hub repo')
parser.add_argument('--revision',   default=None, help='--pretrained: branch, tag or commit')
parser.add_argument('--verbose',    default=False, action='store_true',
                    help='print the model graph and parameter table in one-shot modes too')
args = parser.parse_args()

_ONESHOT = args.generate or args.eval or args.vis or args.push

# ── checkpoint ────────────────────────────────────────────────────────────────

_ARCH_ARGS = ('context', 'n_hidden', 'c_context', 'depth', 'kernel', 'tokenizer', 'ctx_ema',
              'ctx_read_norm', 'dec_tree_kernels', 'dec_width', 'bn_momentum', 'init',
              'image_encoder')


def _parse_mix():
    """[(corpus, slots)] summing to --batch: --mix shares by largest remainder, else --dataset."""
    if not args.mix:
        return [(args.dataset, args.batch)]
    names, w = [], []
    for part in args.mix.split(','):
        n, _, f = part.partition(':')
        names.append(n.strip())
        w.append(float(f) if f else 1.0)
    exact = [x / sum(w) * args.batch for x in w]
    cnt = [int(e) for e in exact]
    for i in sorted(range(len(names)), key=lambda i: exact[i] - cnt[i], reverse=True):
        if sum(cnt) < args.batch:
            cnt[i] += 1
    if 0 in cnt:
        raise SystemExit(f'--mix {args.mix}: {names[cnt.index(0)]} gets 0 of {args.batch} slots')
    return list(zip(names, cnt))


_MIX = _parse_mix()          # batch rows are assigned to corpora in this order
_IMAGE_ROWS = [r for r, (n, k) in enumerate(_MIX) for _ in range(k)]
_IMAGE_ROWS = [r for r, ci in enumerate(_IMAGE_ROWS) if _MIX[ci][0] in _IMAGE_DATASETS]
if args.image_encoder is None:     # on --load the checkpoint's value replaces this
    _names = [n for n, _ in _MIX] + (args.eval_corpora or '').split(',')
    args.image_encoder = 'resnet50' if any(n.strip() in _IMAGE_DATASETS for n in _names) else 'none'

# Checkpoints from before this rewrite carry every option the old script had. Those listed
# here are now fixed behaviour, so a checkpoint is loadable only if it used these values,
# i.e. if it is v395-type (or later, where the key is absent).
_FIXED_ARCH = dict(n_layers=1, linout=True, linout_kernel=1, linin=False, ctx_mix='none',
                   ctx_first='blend', ctx_resid=True, ctx_resid_mode='sum', ctx_chain=False,
                   ctx_cat_in=True, ctx_cat_narrow=True, ctx_cat_kernel=1, ctx_cat_spatial=False,
                   no_text_proj=True, tok_norm=True, tok_gain=1.0, ctx_read_norm_mode='running',
                   ctx_read_gain='none', ctx_read_gate=False, ctx_learn_win=False,
                   ctx_warm=False, ctx_adapt=False, ctx_every=None, dff_write_scale=1.0,
                   dec_tree=True, dec_tree_linear=True, dec_depth=0, head_norm='none',
                   norm='batch', bn_affine=False, bn_track=True, bn_eps=1e-5, dff_norm='none',
                   qproj='none', tap=False, clip_dff=0.0, char_onehot=False)

_loaded_ckpt = None
_start_step = 0
_start_exs = 0
_start_exs_by = {}            # corpus -> examples trained, for the STEP ex_/ep_ columns
if args.pretrained and args.load:
    print(f'--pretrained overrides --load {args.load}')
    args.load = None
if args.load:
    _loaded_ckpt = torch.load(args.load, map_location='cpu', weights_only=True)
    _saved = _loaded_ckpt['saved_args']
    _bad = {k: _saved[k] for k, v in _FIXED_ARCH.items() if k in _saved and _saved[k] != v}
    if _bad:
        raise SystemExit(f'{args.load} is not a v395-type checkpoint: {_bad}')
    for k in _ARCH_ARGS:
        if k in _saved:
            setattr(args, k, _saved[k])
    if 'full_crops' not in _saved and not any(a.startswith('--full_crops') for a in sys.argv):
        args.full_crops = 0.0         # trained before full views existed: keep its crops
    _start_step = int(_loaded_ckpt.get('step', 0))
    _start_exs = int(_loaded_ckpt.get('examples', 0))
    _start_exs_by = dict(_loaded_ckpt.get('examples_by', {}))


def _upgrade_state_dict(sd):
    """Rename a pre-rewrite (v395) state_dict to this model's module names."""
    out = {}
    for k, v in sd.items():
        k = re.sub(r'^(ctx_cat|linout)\.0\.', r'\1.', k)
        k = re.sub(r'^dec_tree\.layers\.(\d+)\.0\.', r'text_dec.tree.\1.', k)
        k = re.sub(r'^decoder\.proj\.', 'text_dec.proj.', k)
        k = re.sub(r'^lmhead\.', 'text_dec.lmhead.', k)
        if k == 'ctx_read_rms' and v.dim() == 2:
            v = v[0]
        out[k] = v
    return out


# ── log / device / seed ───────────────────────────────────────────────────────

if args.log is None:
    if _ONESHOT:
        args.log = os.devnull
    else:
        os.makedirs('log', exist_ok=True)
        stem = 'log/log.' + datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
        args.log, n = stem, 1
        while os.path.exists(args.log):        # never interleave two runs in one file
            args.log, n = f'{stem}.{n}', n + 1
if args.device is None:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
if args.seed is None:
    args.seed = int.from_bytes(os.urandom(4), byteorder='big')
    print('seed', args.seed)
torch.manual_seed(args.seed)
print(args)
# a resumed run's log starts with the checkpoint's log, so chart.py sees one sequence
if _loaded_ckpt is not None and args.log != os.devnull and _loaded_ckpt.get('log'):
    with open(args.log, 'a') as f:
        f.write(_loaded_ckpt['log'].rstrip('\n') + '\n')


def _emit(line, stdout=True):
    """One line to stdout and the log."""
    if stdout:
        print(line, flush=True)
    with open(args.log, 'a') as f:
        print(line, file=f)


_emit(f'ARGS {args}', stdout=False)


def _viewer(inbox, stem, show, parent):
    """--gen_vis / --sample_vis, in their own process so the windows stay responsive between
    GEN steps. Two windows side by side across the top half of the screen (the bottom half
    is left for the log): GEN captions top-left, the training sample top-right. Each message
    redraws its window in place and saves it as <stem>.gen.png / <stem>.sample.png. Exits
    when the trainer does."""
    import textwrap
    if show:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'         # XWayland: Qt may position windows
    import matplotlib
    if not show:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')                  # the same look as --vis
    plt.rcParams['text.parse_math'] = False           # generated text may contain '$'
    plt.ion()
    figs = {}
    slot = {'gen': 0, 'sample': 1}
    title = {'gen': 'GEN captions', 'sample': 'TRAIN sample'}
    cut = lambda t, n: t if len(t) <= n else t[:n - 3] + '...'

    def figure(kind):
        fig = figs.get(kind)
        if fig is not None and (not show or plt.fignum_exists(fig.number)):
            fig.clf()
            return fig
        fig = figs[kind] = plt.figure(figsize=(12.45, 6.6), dpi=100)    # a quarter screen
        fig.canvas.manager.set_window_title(f'{title[kind]} -- {args.log}')
        if show:
            plt.show(block=False)
            try:                                      # top half, side by side
                win = fig.canvas.manager.window
                g = win.screen().availableGeometry()
                w, h = g.width() // 2, g.height() // 2 - 40
                win.setGeometry(g.x() + slot[kind] * w, g.y(), w, h)
            except Exception:
                pass
        return fig

    def draw_gen(fig, step, items):
        cols = min(4, len(items))
        rows = math.ceil(len(items) / cols)
        gs = fig.add_gridspec(2 * rows, cols, height_ratios=[2.6, 2.2] * rows, left=0.01,
                              right=0.99, top=0.93, bottom=0.01, wspace=0.06, hspace=0.2)
        for k, (img, name, cap, ref) in enumerate(items):
            r, c = divmod(k, cols)
            ax = fig.add_subplot(gs[2 * r, c])
            ax.imshow(img)
            ax.set_axis_off()
            ax.set_title(name, fontsize=8)
            tx = fig.add_subplot(gs[2 * r + 1, c])
            tx.set_axis_off()
            tx.text(0, 1, textwrap.fill(cut(cap, 150), 42), va='top', fontsize=8,
                    color='white', transform=tx.transAxes, clip_on=True)
            tx.text(0, 0, textwrap.fill('REF: ' + cut(ref, 130), 42), va='bottom', fontsize=8,
                    color='limegreen', transform=tx.transAxes, clip_on=True)
        fig.suptitle(f'GEN step {step}   {args.log}', family='monospace', fontsize=8)

    def draw_sample(fig, step, img, name, crops, toks):
        """The full image and caption, then one cell per token: the 224x224 crop the model
        saw at that step, labelled with the token it was reading."""
        n = len(crops)
        cols = max(1, min(n, math.ceil(math.sqrt(n * 2.2))))
        rows = math.ceil(n / cols)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.6], width_ratios=[1, 2.4], left=0.01,
                              right=0.99, top=0.93, bottom=0.04, wspace=0.03, hspace=0.06)
        ax = fig.add_subplot(gs[0, 0])
        ax.imshow(img)
        ax.set_axis_off()
        ax.set_title(name, fontsize=8)
        tx = fig.add_subplot(gs[0, 1])
        tx.set_axis_off()
        tx.text(0, 1, textwrap.fill(cut(''.join(toks[1:]), 600), 110), va='top', fontsize=8,
                color='limegreen', transform=tx.transAxes, clip_on=True)
        sub = gs[1, :].subgridspec(rows, cols, wspace=0.04, hspace=0.35)
        for k, (crop, tok) in enumerate(zip(crops, toks)):
            a = fig.add_subplot(sub[k // cols, k % cols])
            a.imshow(crop)
            a.set_xticks([])
            a.set_yticks([])
            a.set_xlabel(tok.replace(' ', '·') or '∅', fontsize=8, labelpad=1,
                         family='monospace')
        fig.suptitle(f'TRAIN sample step {step}   {n} tokens   {args.log}', family='monospace',
                     fontsize=8)

    while os.getppid() == parent:
        try:
            msg = inbox.get(timeout=0.1)
        except queue.Empty:
            if show:
                for kind, fig in list(figs.items()):
                    if plt.fignum_exists(fig.number):
                        fig.canvas.flush_events()
                    else:
                        del figs[kind]                # closed by the user: reopen next time
            continue
        if msg is None:
            return
        kind = msg[0]
        try:
            fig = figure(kind)
            (draw_gen if kind == 'gen' else draw_sample)(fig, *msg[1:])
            if stem:
                fig.savefig(f'{stem}.{kind}.png', dpi=100)
            if show:
                fig.canvas.draw()
                fig.canvas.flush_events()
        except Exception as e:                        # never lose the viewer to one panel
            print(f'viewer: {kind} panel failed: {e!r}', flush=True)


_gen_inbox = _gen_proc = None

if (not _ONESHOT and args.image_encoder != 'none'
        and ((args.gen_vis and args.gen_images) or args.sample_vis)):
    import multiprocessing
    _ctx = multiprocessing.get_context('fork')     # before CUDA and the data threads exist
    _gen_inbox = _ctx.Queue(maxsize=4)
    _gen_proc = _ctx.Process(target=_viewer, daemon=True, args=(
        _gen_inbox, None if args.log == os.devnull else args.log,
        bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')), os.getpid()))
    _gen_proc.start()

# ── model ─────────────────────────────────────────────────────────────────────


class ContextCNN(nn.Module):
    """The state update: depth x (conv -> BatchNorm(affine=False) -> ReLU) at constant width."""

    def __init__(self, width, depth, kernel, bn_momentum=0.1):
        super().__init__()
        self.layers = nn.ModuleList(
            nn.Sequential(nn.Conv2d(width, width, kernel, padding=kernel // 2),
                          nn.BatchNorm2d(width, affine=False, momentum=bn_momentum or None),
                          nn.ReLU())
            for _ in range(depth))

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


def _linear_init(conv):
    """Variance-preserving init for a conv with nothing after it to rescale."""
    nn.init.kaiming_normal_(conv.weight, mode='fan_in', nonlinearity='linear')
    nn.init.zeros_(conv.bias)
    return conv


class TextDecoder(nn.Module):
    """Layer output [B, C, S, S] -> logits [B, vocab]. A linear tree of unpadded convs
    shrinks the grid, the last conv maps to the embedding width, whatever grid remains is
    average-pooled, and the borrowed (frozen) lm_head produces the logits."""

    def __init__(self, c_in, S, kernels, width, lmhead):
        super().__init__()
        red = sum(k - 1 for k in kernels)
        if not kernels or min(kernels) < 1 or red > S - 1:
            raise SystemExit(f'--dec_tree_kernels {kernels}: need sum(k-1) <= S-1 = {S - 1}')
        c_out = lmhead.in_features
        self.proj = _linear_init(nn.Conv2d(width if len(kernels) > 1 else c_in, c_out,
                                           kernels[-1]))
        self.tree = nn.ModuleList(_linear_init(nn.Conv2d(c_in if i == 0 else width, width, k))
                                  for i, k in enumerate(kernels[:-1]))
        self.pool = nn.AvgPool2d(S - red) if S - red > 1 else nn.Identity()
        self.lmhead = lmhead

    def forward(self, x):
        for conv in self.tree:
            x = conv(x)
        return self.lmhead(self.pool(self.proj(x)).squeeze(-1).squeeze(-1))


class ImageEncoder(nn.Module):
    """Frozen pretrained ResNet-50 trunk (timm weights, torchvision layout): normalized
    [N, 3, 224, 224] -> [N, 2048, 7, 7], run in bf16, always in eval mode."""

    def __init__(self, name):
        super().__init__()
        import torchvision
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        net = torchvision.models.resnet50()
        net.load_state_dict(load_file(hf_hub_download(_IMAGE_ENCODERS[name], 'model.safetensors')))
        self.net = nn.Sequential(*list(net.children())[:-2]).to(memory_format=torch.channels_last)
        self.width = 2048
        for p in self.parameters():
            p.requires_grad_(False)
        self.eval()

    def train(self, mode=True):
        return super().train(False)

    @torch.no_grad()
    def forward(self, x):
        if x.is_cuda and '_fast' not in self.__dict__:
            # ~1.6x on the ResNet. Kept out of the module registry, so it adds no state_dict keys
            self.__dict__['_fast'] = torch.compile(self.net)
        net = self.__dict__['_fast'] if x.is_cuda else self.net
        with torch.autocast(x.device.type, dtype=torch.bfloat16, enabled=x.is_cuda):
            return net(x.contiguous(memory_format=torch.channels_last)).float()


def _prep_image(img):
    """PIL image -> uint8 [3, h, w] at native resolution, except that an image with a side
    under _IMG_IN is scaled up uniformly (pixel aspect 1:1) until its shorter side is _IMG_IN,
    so every crop is filled. A side longer than _IMG_BANK keeps its central _IMG_BANK pixels."""
    img = img.convert('RGB')
    w, h = img.size
    if min(w, h) < _IMG_IN:
        s = _IMG_IN / min(w, h)
        w, h = max(_IMG_IN, round(w * s)), max(_IMG_IN, round(h * s))
        img = img.resize((w, h), 3)                     # 3 = BICUBIC
    x0, y0 = max(0, (w - _IMG_BANK) // 2), max(0, (h - _IMG_BANK) // 2)
    img = img.crop((x0, y0, x0 + min(w, _IMG_BANK), y0 + min(h, _IMG_BANK)))
    return torch.from_numpy(np.asarray(img).copy()).permute(2, 0, 1)


def _fit(im):
    """uint8 [3, h, w] -> uint8 [3, _IMG_IN, L]: the whole image scaled (antialiased, aspect
    kept) so its shorter side is _IMG_IN, stored with the long side across -- a tall image is
    transposed -- and L capped at _IMG_BANK by keeping the centre."""
    if im.shape[1] > im.shape[2]:
        im = im.transpose(1, 2)
    h, w = im.shape[1:]
    L = max(_IMG_IN, round(w * _IMG_IN / h))
    x = F.interpolate(im[None].float(), size=(_IMG_IN, L), mode='bilinear', antialias=True,
                      align_corners=False)[0].round().clamp(0, 255).to(torch.uint8)
    c = max(0, (L - _IMG_BANK) // 2)
    return x[:, :, c:c + _IMG_BANK]


def _bank_put(bank, hw, fit, j, im):
    """Load image im (uint8 [3, h, w], on the bank's device) into slot j: native pixels in the
    top-left of bank[j], its full view (see _fit) in fit[j], and hw[j] = (h, w, full-view L)."""
    h, w = im.shape[1:]
    bank[j, :, :h, :w] = im
    f = _fit(im)
    fit[j, :, :, :f.shape[2]] = f
    hw[j, 0], hw[j, 1], hw[j, 2] = h, w, f.shape[2]


def _bank(imgs, device):
    """uint8 [3, h, w] images -> (bank [N, 3, _IMG_BANK, _IMG_BANK] uint8, sizes [N, 3]
    (h, w, L), full views [N, 3, _IMG_IN, _IMG_BANK] uint8), the arguments of _views."""
    bank = torch.zeros(len(imgs), 3, _IMG_BANK, _IMG_BANK, dtype=torch.uint8, device=device)
    fit = torch.zeros(len(imgs), 3, _IMG_IN, _IMG_BANK, dtype=torch.uint8, device=device)
    hw = torch.zeros(len(imgs), 3, device=device)
    for j, im in enumerate(imgs):
        _bank_put(bank, hw, fit, j, im.to(device))
    return bank, hw, fit


def _views(bank, hw, fit, gen=None, start=None):
    """One random 224x224 crop per image, normalized for the encoder: a native-resolution
    close-up copied pixel for pixel (images are at least 224 on each side, see _prep_image)
    or, with probability --full_crops, a full view -- the whole image scaled so its shorter
    side is 224, at a random offset along the longer side (see _fit). start: bool [N], rows
    reading <STX>; with --full_crops > 0 they always get the centred full view, so an example
    opens on the whole image. gen: a torch.Generator on the bank's device, for reproducible
    crops (eval)."""
    N, dev = bank.shape[0], bank.device
    ar = torch.arange(_IMG_IN, device=dev)
    rows = torch.arange(N, device=dev)[:, None, None]
    H, W = hw[:, 0].long(), hw[:, 1].long()
    oy = (torch.rand(N, device=dev, generator=gen) * (H - _IMG_IN + 1)).long()
    ox = (torch.rand(N, device=dev, generator=gen) * (W - _IMG_IN + 1)).long()
    x = bank[rows, :, (oy[:, None] + ar)[:, :, None], (ox[:, None] + ar)[:, None, :]]
    if args.full_crops > 0:                       # skipped at 0, keeping the old random stream
        L = hw[:, 2].long()
        of = (torch.rand(N, device=dev, generator=gen) * (L - _IMG_IN + 1)).long()
        if start is not None:
            of = torch.where(start, (L - _IMG_IN) // 2, of)
        full = fit[rows, :, ar[None, :, None], (of[:, None] + ar)[:, None, :]]
        full = torch.where((H > W)[:, None, None, None], full.transpose(1, 2), full)
        pick = torch.rand(N, device=dev, generator=gen) < args.full_crops
        if start is not None:
            pick = pick | start
        x = torch.where(pick[:, None, None, None], full, x)
    x = x.permute(0, 3, 1, 2).float() / 255.0                           # [N, 3, 224, 224]
    mean = torch.tensor(_IMG_MEAN, device=dev).view(1, 3, 1, 1)
    std = torch.tensor(_IMG_STD, device=dev).view(1, 3, 1, 1)
    return (x - mean) / std


# PyTorchModelHubMixin adds save_pretrained/push_to_hub/from_pretrained (--push,
# --pretrained) and records the __init__ kwargs as the hub config.
try:
    from huggingface_hub import PyTorchModelHubMixin as _HubMixin
except ImportError:                                  # pragma: no cover
    class _HubMixin:
        pass


class VLAModel(nn.Module, _HubMixin):
    """One recurrent layer with K DFF registers, held concatenated as one
    [B, K*n_hidden, S, S] tensor (self.dff, detached every step: gradient horizon 1 token).

    step:  inputs   token grid                                        [c_text, S, S]
                    image feature map (zeros for text-only rows)      [2048, S, S]
           read     K registers, each scaled to RMS --ctx_read_norm   K x [n_hidden, S, S]
           x      = ctx_cat(concat(inputs, reads))                    [c_context, S, S]
           o      = linout(ContextCNN(x))                             [n_hidden, S, S]
           write    r_k <- r_k + a_k * (o - sum_{j<k} r_j[t] - r_k),  a_k = 1/W_k
           logits = text_dec(o)
    """

    def __init__(self, S=8, n_hidden=512, c_context=384, depth=8, kernel=3,
                 tokenizer='pythia31m', windows=(256, 64, 16, 4, 1), read_norm=1.0,
                 dec_kernels=(3, 3, 3), dec_width=256, bn_momentum=0.1, init='zero',
                 image_encoder='none'):
        super().__init__()
        from transformers import AutoModelForCausalLM
        repo = _TOKENIZERS[tokenizer]
        lm = AutoModelForCausalLM.from_pretrained(repo)
        self.S, self.n_hidden, self.c_context = S, n_hidden, c_context
        self.windows = [float(w) for w in windows]
        if not self.windows or min(self.windows) < 1:
            raise SystemExit(f'--ctx_ema {windows}: windows must be >= 1 token')
        self.K = len(self.windows)
        self.read_norm = float(read_norm)
        self.init_mode = init
        self.vocab, self.c_text = lm.config.vocab_size, lm.config.hidden_size
        self.tok = HFTokenizer(repo, self.vocab)
        self.start_id, self.end_id = self.tok.start_id, self.tok.end_id

        self.tok_embed = lm.get_input_embeddings()                      # frozen
        self.context = ContextCNN(c_context, depth, kernel, bn_momentum)
        self.text_dec = TextDecoder(n_hidden, S, list(dec_kernels), dec_width,
                                    lm.get_output_embeddings())         # lm_head frozen
        for p in self.pretrained_params():
            p.requires_grad_(False)

        # ctx_cat reads [input grids..., registers...]. It starts as [I, I, ..., I] onto the
        # first outputs each block fits, i.e. the plain sum of the sources -- except the image
        # block, which starts at zero, so an image model starts out as the text-only function
        # and learns to read the image.
        self.image_encoder = image_encoder or 'none'
        self.img_width = 2048 if self.image_encoder != 'none' else 0
        self.in_widths = [self.c_text] + ([self.img_width] if self.img_width else [])
        widths = self.in_widths + [n_hidden] * self.K
        self.ctx_cat = nn.Conv2d(sum(widths), c_context, 1)
        with torch.no_grad():
            self.ctx_cat.weight.zero_()
            o = 0
            for i, w in enumerate(widths):
                if not (self.img_width and i == 1):
                    n = min(w, c_context)
                    self.ctx_cat.weight[:n, o:o + n, 0, 0] = torch.eye(n)
                o += w
            self.ctx_cat.bias.zero_()

        # linout: c_context -> n_hidden, semi-orthogonal (norm-preserving, dense and signed)
        self.linout = nn.Conv2d(c_context, n_hidden, 1)
        with torch.no_grad():
            self.linout.weight.copy_(
                nn.init.orthogonal_(torch.empty(n_hidden, c_context)).view(n_hidden, c_context, 1, 1))
            self.linout.bias.zero_()

        self.img_enc = ImageEncoder(self.image_encoder) if self.img_width else None   # frozen

        self.register_buffer('ctx_read_rms', torch.zeros(self.K))       # 0 = not measured yet
        self.register_buffer('rate', torch.tensor([min(1.0, 1.0 / w) for w in self.windows]),
                             persistent=False)
        self.dff = None              # [B, K*n_hidden, S, S], detached; None until first step
        self._ablate = None          # --eval_info: registers read as their mean ...
        self._read_mean = None       # ... which is this [1, K*n_hidden, S, S] tensor

    def pretrained_params(self):
        """The borrowed embedding and lm_head, deduplicated (tiny8m ties them)."""
        seen, out = set(), []
        for m in (self.tok_embed, self.text_dec.lmhead):
            for p in m.parameters():
                if id(p) not in seen:
                    seen.add(id(p))
                    out.append(p)
        return out

    def new_state(self, B, device):
        shape = (B, self.n_hidden * self.K, self.S, self.S)
        if self.init_mode == 'gaussian':
            return torch.randn(shape, device=device)
        if self.init_mode == 'relu':
            return torch.randn(shape, device=device).relu()
        return torch.zeros(shape, device=device)

    def image_grid(self, views):
        """Encoder views [N, 3, 224, 224] -> image grid [N, 2048, S, S], each position
        RMS-normalized over channels (as the token embedding is)."""
        f = self.img_enc(views)
        if f.shape[-1] != self.S:
            f = F.adaptive_avg_pool2d(f, self.S)
        return f * torch.rsqrt(f.pow(2).mean(dim=1, keepdim=True) + 1e-12)

    def _inputs(self, idx, img):
        """The input grids, in self.in_widths order: the RMS-normalized token embedding
        broadcast over the grid, then (image model) the image grid, zeros where img is None."""
        B = idx.shape[0]
        tok = self.tok_embed(idx)
        tok = tok * torch.rsqrt(tok.pow(2).mean(dim=1, keepdim=True) + 1e-12)
        grids = [tok.view(B, self.c_text, 1, 1).expand(-1, -1, self.S, self.S)]
        if self.img_width:
            grids.append(img if img is not None else
                         tok.new_zeros(B, self.img_width, self.S, self.S))
        return grids

    def _read(self, dff):
        """The K registers as ctx_cat reads them."""
        regs = list(dff.chunk(self.K, dim=1))
        if self._ablate:
            mu = self._read_mean.chunk(self.K, dim=1)
            regs = [mu[k].expand_as(r) if k in self._ablate else r for k, r in enumerate(regs)]
        if self.read_norm > 0:
            run = self.ctx_read_rms
            if self.training or bool((run == 0).any()):
                with torch.no_grad():
                    b = torch.stack([r.float().pow(2).mean() for r in regs]).sqrt()
                    if self.training:
                        run.copy_(torch.where(run == 0, b, 0.99 * run + 0.01 * b))
                    sc = torch.where(run == 0, b, run)
            else:
                sc = run
            regs = [r * (self.read_norm / (sc[k] + 1e-12)) for k, r in enumerate(regs)]
        return regs

    def _write(self, o, dff):
        """Laplacian-pyramid cascade: register k blends toward o minus registers 1..k-1 as
        just written."""
        new = []
        for k, p in enumerate(dff.chunk(self.K, dim=1)):
            inp = o - sum(new) if k else o
            new.append(p + self.rate[k] * (inp - p))
        return torch.cat(new, dim=1)

    def step(self, idx, dff, img=None):
        """One token for every row: -> (new registers, layer output). No detach."""
        x = self.ctx_cat(torch.cat(self._inputs(idx, img) + self._read(dff), dim=1))
        o = self.linout(self.context(x))
        return self._write(o, dff), o

    def forward(self, idx, targets=None, flag=None, img=None):
        """idx [B] current tokens; targets [B] next tokens or None; flag [B] rows starting a
        document (their registers reset); img [B, 2048, S, S] image grid or None (zeros).
        Advances self.dff by one step."""
        B, dev = idx.shape[0], idx.device
        if self.dff is None or self.dff.shape[0] != B or self.dff.device != dev:
            self.dff = self.new_state(B, dev)
        if flag is not None and flag.any():
            self.dff = self.dff.clone()
            self.dff[flag] = self.new_state(int(flag.sum()), dev)
        new, o = self.step(idx, self.dff, img)
        self.dff = new.detach().clone()
        logits = self.text_dec(o)
        loss = F.cross_entropy(logits, targets.long()) if targets is not None else None
        return logits, loss

    @torch.no_grad()
    def generate(self, prompt_ids, n_tokens, temperature=1.0, image=None):
        """Sample n_tokens after prompt_ids on a private state. An END is kept in the output
        and, if the budget is not filled, the state resets and the prompt is fed again, as
        at a training document boundary (at most 20 sequences). Short only on NaN/Inf.
        image: uint8 [3, h, w], seen through a fresh random 224x224 crop every token (as
        in training); None = text-only."""
        self.eval()
        dev = next(self.parameters()).device
        bank = _bank([image], dev) if image is not None else None

        def feed(b, dff):
            img = (self.image_grid(_views(*bank, start=torch.tensor([b == self.start_id],
                                                                    device=dev)))
                   if bank is not None else None)
            new, o = self.step(torch.tensor([b], device=dev), dff, img)
            logits = self.text_dec(o)
            if not (new.isfinite().all() and logits.isfinite().all()):
                print('generate: NaN/Inf')
                return None, None
            return logits, new

        out = []
        for _ in range(20):
            dff, logits = self.new_state(1, dev), None
            for b in prompt_ids:
                logits, dff = feed(b, dff)
                if logits is None:
                    return out
            while len(out) < n_tokens:
                prob = F.softmax(logits[0] / max(temperature, 1e-6), dim=-1)
                b = torch.multinomial(prob, 1).item()
                out.append(b)
                if b == self.end_id:
                    break
                logits, dff = feed(b, dff)
                if logits is None:
                    return out
            if len(out) >= n_tokens:
                break
        return out


# ── data ──────────────────────────────────────────────────────────────────────

# name -> (hub repo, config, split, text column)
_TEXT_DATASETS = {
    'tiny':          ('roneneldan/TinyStories', None, 'train', 'text'),
    'c4':            ('allenai/c4', 'en', 'train', 'text'),
    'web':           ('Skylion007/openwebtext', None, 'train', 'text'),
    'pile':          ('EleutherAI/the_pile_deduplicated', None, 'train', 'text'),
    'pile_nc':       ('monology/pile-uncopyrighted', None, 'train', 'text'),
    'swiki':         ('wikimedia/wikipedia', '20231101.simple', 'train', 'text'),
    'fwedu':         ('HuggingFaceFW/fineweb-edu', 'sample-10BT', 'train', 'text'),
    'fineweb':       ('HuggingFaceFW/fineweb', 'sample-10BT', 'train', 'text'),
    'fwcrawl':       ('HuggingFaceFW/fineweb', 'CC-MAIN-2025-26', 'train', 'text'),
    'cosmo':         ('HuggingFaceTB/cosmopedia', 'stories', 'train', 'text'),
    'cosmoweb':      ('HuggingFaceTB/cosmopedia', 'web_samples_v2', 'train', 'text'),
    'smolcosmo':     ('HuggingFaceTB/smollm-corpus', 'cosmopedia-v2', 'train', 'text'),
    'smolfwedu':     ('HuggingFaceTB/smollm-corpus', 'fineweb-edu-dedup', 'train', 'text'),
    'dclmedu':       ('HuggingFaceTB/dclm-edu', None, 'train', 'text'),
    'strangetb':     ('nampdn-ai/tiny-strange-textbooks', None, 'train', 'text'),
    'tinytb':        ('nampdn-ai/tiny-textbooks', None, 'train', 'textbook'),
    'sebooks':       ('Nelathan/standardebooks', None, 'train', 'text'),
    'simplestories': ('SimpleStories/SimpleStories', None, 'train', 'story'),
    'littlec':       ('littlelearner/LittleCurriculum', None, 'train', 'text'),
}

# Repos too large to resolve on demand: only the shards already in the hub cache are read,
# from (repo, subdirectory).
_HUB_SUBSET = {
    'smolcosmo': ('HuggingFaceTB/smollm-corpus', 'cosmopedia-v2'),
    'smolfwedu': ('HuggingFaceTB/smollm-corpus', 'fineweb-edu-dedup'),
    'dclmedu':   ('HuggingFaceTB/dclm-edu', 'data'),
    'fineweb':   ('HuggingFaceFW/fineweb', 'sample/10BT'),
    'fwcrawl':   ('HuggingFaceFW/fineweb', 'data/CC-MAIN-2025-26'),
}

# Train-only corpora: a fixed 1/_HOLDOUT_MOD of documents, chosen by a hash of the text, is
# held out for eval and skipped in training (deterministic, streaming-compatible).
_HASH_HOLDOUT = {'swiki', 'fwedu', 'fineweb', 'fwcrawl', 'cosmo', 'cosmoweb', 'smolcosmo',
                 'smolfwedu', 'strangetb', 'sebooks', 'dclmedu', 'littlec', 'simplestories'}
_HOLDOUT_MOD = 32

# Corpora with a real held-out split; a triple is a held-out set in another repo.
_EVAL_SPLITS = {
    'tinytb':  'test',
    'tiny':    'validation',
    'c4':      'validation',
    'web':     'train[-3000:]',       # the tail exp/score.py holds out
    'pile':    ('mit-han-lab/pile-val-backup', None, 'validation'),
    'pile_nc': ('mit-han-lab/pile-val-backup', None, 'validation'),
}
_STREAM_EVAL = {'c4'}                  # always streamed for eval (the config is huge)


def _is_heldout(text):
    # crc32, not hash(): stable across processes and Python versions
    return zlib.crc32(text[:512].encode('utf-8', 'ignore')) % _HOLDOUT_MOD == 0


def _corpus_text(name, example):
    col = _TEXT_DATASETS[name][3] if name in _TEXT_DATASETS else 'text'
    return example.get(col, example.get('text', '')) or ''


def _hub_subset_files(name):
    repo, sub = _HUB_SUBSET[name]
    home = os.environ.get('HF_HOME') or os.path.expanduser('~/.cache/huggingface')
    root = os.path.join(home, 'hub', 'datasets--' + repo.replace('/', '--'), 'snapshots')
    return sorted(glob.glob(os.path.join(root, '*', sub, '*.parquet')))


def _shard_files(hf, cfg, n):
    """First n train shard paths of a hub dataset repo (config subdir cfg if any)."""
    from huggingface_hub import HfApi
    exts = ('.parquet', '.jsonl.zst', '.json.zst', '.jsonl.gz', '.json.gz', '.jsonl')
    sib = [s.rfilename for s in HfApi().repo_info(hf, repo_type='dataset').siblings]
    par = sorted(f for f in sib if f.endswith(exts) and 'train' in f)
    if cfg:
        par = [f for f in par if f'/{cfg}/' in f or f.startswith(f'{cfg}/')]
    return par[:n]


def _load_corpus(name, streaming, shards=None):
    from datasets import load_dataset, DownloadConfig
    if name in _HUB_SUBSET:
        files = _hub_subset_files(name)
        if not files:
            raise SystemExit(f'{name}: no downloaded parquet files under HF_HOME for '
                             f'{_HUB_SUBSET[name]}; fetch a subset first')
        files = files[:shards] if shards else files
        print(f'{name}: {len(files)} local parquet file(s) from the hub cache', flush=True)
        return load_dataset('parquet', data_files={'train': files}, streaming=streaming)
    if name not in _TEXT_DATASETS:
        raise SystemExit(f'unknown dataset: {name}')
    hf, cfg, _, _ = _TEXT_DATASETS[name]
    if streaming:
        return load_dataset(hf, cfg, streaming=True)
    files = _shard_files(hf, cfg, shards) if shards else []
    if files:
        print(f'{name}: --shards {shards} -> {len(files)} shard(s)')
        load = lambda dlc: load_dataset(hf, data_files={'train': files}, download_config=dlc,
                                        verification_mode='no_checks')
    else:
        load = lambda dlc: load_dataset(hf, cfg, download_config=dlc)
    dlc = DownloadConfig(num_proc=4, max_retries=8)
    while True:                       # ride out HF 429 rate limits; cached shards persist
        try:
            return load(dlc)
        except Exception as e:
            if '429' not in str(e) and 'Too Many Requests' not in str(e):
                raise
            print(f'HF 429 rate-limit on {name}; cooling down 300s ...', flush=True)
            time.sleep(300)


def _make_iter(ds, streaming, seed, shuffle=True):
    split = ds['train']
    if not shuffle:
        return iter(split)
    if streaming:
        return iter(split.shuffle(buffer_size=10000, seed=seed))
    if (getattr(split, 'dataset_size', None) or 1 << 31) <= 1 << 30:
        return iter(split.shuffle(seed=seed))       # small: a true permutation
    # large and on disk: never Dataset.shuffle() (random access across the arrow file reads
    # ~400x the data); read shards sequentially through a shuffle buffer instead
    return iter(split.to_iterable_dataset(num_shards=64).shuffle(buffer_size=10000, seed=seed))


def clip_text(text):
    """A document as (input, target) pairs over [START] tokens [END]."""
    full = [_tokenizer.start_id] + _tokenizer.encode(text) + [_tokenizer.end_id]
    return [(full[i], full[i + 1]) for i in range(len(full) - 1)]


def _id_heldout(key):
    """Image corpora: the held-out 1/_HOLDOUT_MOD, by a hash of the example id."""
    return zlib.crc32(key.encode('utf-8', 'ignore')) % _HOLDOUT_MOD == 0


def _decode_image(row):
    from PIL import Image, PngImagePlugin
    # Some PNGs carry metadata chunks over Pillow's 1 MB decompression cap (ValueError
    # "Decompressed data too large"); the text is ignored, so allow it rather than drop the image.
    PngImagePlugin.MAX_TEXT_CHUNK = 64 << 20
    im = row['image']                    # encoded bytes (or an HF image struct)
    return _prep_image(Image.open(io.BytesIO(im['bytes'] if isinstance(im, dict) else im)))


class _ImageSource:
    """Random training rows of a local image-caption corpus. Each source shard holds only a
    few classes, so whole row groups of random files are poured into a pool of rows and
    rows are drawn from the pool at random: at any time the draws mix ~POOL/100 shards."""
    POOL = 4000

    def __init__(self, name, seed):
        import pyarrow.parquet as pq
        self.pq, cfg = pq, _IMAGE_DATASETS[name]
        self.files = sorted(glob.glob(os.path.join(cfg['dir'], '*.parquet')))
        if not self.files:
            raise SystemExit(f'{name}: no parquet files in {cfg["dir"]} (see exp/img_prep.py)')
        self.cap, self.rng = cfg['caption'], random.Random(seed)
        self.pool, self.lock = [], threading.Lock()
        print(f'{name}: {len(self.files)} local parquet files in {cfg["dir"]}', flush=True)

    def _fill(self):
        with self.lock:
            f = self.rng.choice(self.files)
        pf = self.pq.ParquetFile(f)
        with self.lock:
            g = self.rng.randrange(pf.metadata.num_row_groups)
        rows = pf.read_row_group(g, columns=['image', 'id', 'class', self.cap]).to_pylist()
        rows = [r for r in rows if not _id_heldout(r['id'])]
        with self.lock:
            self.pool.extend(rows)

    def next(self):
        """-> (caption, image row)."""
        while True:
            with self.lock:
                if len(self.pool) >= self.POOL:
                    i = self.rng.randrange(len(self.pool))
                    row, self.pool[i] = self.pool[i], self.pool[-1]
                    self.pool.pop()
                    return (row[self.cap] or '').strip(), row
            self._fill()


# Worker -> training-loop tallies, per corpus: documents/tokens since the last TEXT line, the
# latest document (TXT lines) and epochs; plus the first text documents (GENSCORE anchors).
_text_lock = threading.Lock()
_text_stats = {n: {'examples': 0, 'tokens': 0, 'sample': ''} for n, _ in _MIX}
_anchors = []
_epoch = {n: 1 for n, _ in _MIX}


def _text_tally(name, n_tokens, sample):
    with _text_lock:
        st = _text_stats[name]
        st['examples'] += 1
        st['tokens'] += n_tokens
        st['sample'] = sample
        if name not in _IMAGE_DATASETS and len(_anchors) < 24:
            _anchors.append(sample)


def _text_drain():
    """-> {corpus: (examples, tokens)} since the last call."""
    with _text_lock:
        out = {n: (st['examples'], st['tokens']) for n, st in _text_stats.items()}
        for st in _text_stats.values():
            st['examples'] = st['tokens'] = 0
    return out


def _sample_window(text, n=240):
    """A random window of a document (its opening would repeat on long documents)."""
    if len(text) <= n:
        return text
    i = random.randrange(0, len(text) - n)
    return ('...' + text[i:i + n]) if i else text[:n]


class _Slot:
    """One batch row: the document it is currently reading."""
    __slots__ = ['steps', 'pos']

    def __init__(self):
        self.steps, self.pos = [], 0

    def load(self, steps):
        self.steps, self.pos = steps, 0


def worker(stop, q, datasets):
    """Per corpus, builder threads turn documents (and images) into clips on that corpus's
    queue; this loop advances every slot one token per step and puts (x_list, y_list,
    start_flags, new_images) on q. Slots are assigned to corpora in _MIX order; new_images
    lists (row, (uint8 image, name)) for image rows that started a new example this step."""
    clip_qs = {}

    def text_builder(name, ds, cq):
        it, lock = [_make_iter(ds, args.streaming, args.seed, args.shuffle)], threading.Lock()

        def next_example():
            with lock:
                try:
                    return next(it[0])
                except StopIteration:
                    _epoch[name] += 1
                    print(f'EPOCH {name} -> {_epoch[name]} (reshuffle seed '
                          f'{args.seed + _epoch[name]})', flush=True)
                    it[0] = _make_iter(ds, args.streaming, args.seed + _epoch[name], args.shuffle)
                    return next(it[0])

        def build():
            text = _corpus_text(name, next_example())
            if not text or (name in _HASH_HOLDOUT and _is_heldout(text)):
                return None
            return text, None
        return build

    def image_builder(name, cq):
        src = _ImageSource(name, args.seed)

        def build():
            text, row = src.next()
            name = f'{(row.get("class") or "").split(",")[0]}  ({row["id"]})'
            return (text, (_decode_image(row), name)) if text else None
        return build

    def run(name, build, cq):
        while not stop.is_set():
            try:
                got = build()
            except Exception as e:
                print(f'builder {name}: {e!r}')
                continue
            if got is None:
                continue
            steps = clip_text(got[0])
            _text_tally(name, len(steps), got[0])
            while not stop.is_set():
                try:
                    cq.put((steps, got[1]), timeout=0.5)
                    break
                except queue.Full:
                    pass

    for name in dict.fromkeys(n for n, _ in _MIX):
        cq = clip_qs[name] = queue.Queue(maxsize=2 * max(1, args.workers))
        build = (image_builder(name, cq) if name in _IMAGE_DATASETS
                 else text_builder(name, datasets[name], cq))
        for _ in range(max(1, args.workers)):
            threading.Thread(target=run, args=(name, build, cq), daemon=True).start()

    names = [n for n, k in _MIX for _ in range(k)]
    slots = [_Slot() for _ in names]
    while not stop.is_set():
        new_imgs = []
        for r, slot in enumerate(slots):
            while slot.pos >= len(slot.steps):
                try:
                    steps, img = clip_qs[names[r]].get(timeout=0.5)
                except queue.Empty:
                    if stop.is_set():
                        return
                    continue
                slot.load(steps)
                if img is not None:
                    new_imgs.append((r, img))
        flags = [slot.pos == 0 for slot in slots]
        xy = [slot.steps[slot.pos] for slot in slots]
        for slot in slots:
            slot.pos += 1
        q.put(([x for x, _ in xy], [y for _, y in xy], flags, new_imgs))


hf_datasets = {}
if not _ONESHOT:
    print('loading datasets...')
    for name in dict.fromkeys(n for n, _ in _MIX):
        if name not in _IMAGE_DATASETS:
            hf_datasets[name] = _load_corpus(name, args.streaming, args.shards)
    print('datasets ready')


def _corpus_size(name):
    """Training examples in one pass over a corpus, for the STEP ep_ columns; None if unknown
    (streaming). An image corpus is counted as its file count times the rows of its first file
    (exp/img_prep.py writes the same number per file -- reading every footer takes minutes),
    less the held-out 1/_HOLDOUT_MOD."""
    if name in _IMAGE_DATASETS:
        import pyarrow.parquet as pq
        files = sorted(glob.glob(os.path.join(_IMAGE_DATASETS[name]['dir'], '*.parquet')))
        if not files:
            return None
        return len(files) * pq.ParquetFile(files[0]).metadata.num_rows * (1 - 1 / _HOLDOUT_MOD)
    try:
        return len(hf_datasets[name]['train']) or None
    except (KeyError, TypeError):
        return None

# ── build / load the model ────────────────────────────────────────────────────

if args.pretrained:
    if not hasattr(VLAModel, 'from_pretrained'):
        raise SystemExit('--pretrained requires huggingface_hub')
    print(f'loading {args.pretrained} from the hub...')
    model = VLAModel.from_pretrained(args.pretrained, revision=args.revision)
    args.context, args.n_hidden, args.c_context = model.S, model.n_hidden, model.c_context
    args.ctx_ema = ','.join(f'{w:g}' for w in model.windows)
    args.ctx_read_norm, args.init = model.read_norm, model.init_mode
    args.image_encoder = model.image_encoder
    _emit(f'ARGS (pretrained) {args}')
else:
    model = VLAModel(S=args.context, n_hidden=args.n_hidden, c_context=args.c_context,
                     depth=args.depth, kernel=args.kernel, tokenizer=args.tokenizer,
                     windows=[float(w) for w in str(args.ctx_ema).split(',') if w.strip()],
                     read_norm=args.ctx_read_norm,
                     dec_kernels=[int(k) for k in str(args.dec_tree_kernels).split(',') if k.strip()],
                     dec_width=args.dec_width, bn_momentum=args.bn_momentum, init=args.init,
                     image_encoder=args.image_encoder)
    if _loaded_ckpt is not None:
        model.load_state_dict(_upgrade_state_dict(_loaded_ckpt['state_dict']))
model = model.to(args.device)
_tokenizer = model.tok


def _model_graph(model):
    """One token step as a table, modules in execution order (conv rows absorb their
    BN/ReLU/pool), with marker rows for the tensor ops between modules."""
    names = {m: n for n, m in model.named_modules()}
    rows = []

    def shape(t):
        t = t[0] if isinstance(t, (tuple, list)) else t
        return 'x'.join(str(d) for d in t.shape[1:]) if t.dim() > 1 else 'token'

    def hook(m, inp, out):
        n = names[m]
        tr = sum(p.numel() for p in m.parameters(recurse=False) if p.requires_grad)
        fr = sum(p.numel() for p in m.parameters(recurse=False) if not p.requires_grad)
        if isinstance(m, (nn.BatchNorm2d, nn.ReLU, nn.AvgPool2d)) and rows:
            rows[-1]['op'] += '+' + type(m).__name__.replace('BatchNorm2d', 'BN')
            rows[-1]['out'] = shape(out)
            return
        op = (f'Conv2d {m.kernel_size[0]}x{m.kernel_size[1]}' if isinstance(m, nn.Conv2d)
              else type(m).__name__)
        rows.append(dict(name=n, op=op, inp=shape(inp), out=shape(out), tr=tr, fr=fr))

    hooks = [m.register_forward_hook(hook) for n, m in model.named_modules()
             if not list(m.children()) and not isinstance(m, nn.Identity)
             and not n.startswith('img_enc')]
    was = model.training
    model.eval()
    try:
        with torch.no_grad():
            dev = next(model.parameters()).device
            new, o = model.step(torch.zeros(1, dtype=torch.long, device=dev),
                                model.new_state(1, dev))
            model.text_dec(o)
    finally:
        for h in hooks:
            h.remove()
        model.train(was)

    S, H = model.S, f'{model.n_hidden}x{model.S}x{model.S}'
    regs = [f'DFF_{k + 1}' for k in range(model.K)]
    out = []
    for r in rows:
        if r['name'] == 'ctx_cat':
            srcs = ['(token grid)'] + [f'{g}[t-1]' for g in regs]
            if model.img_enc is not None:
                out.append(dict(name='img_enc -> (image grid)', op=f'ResNet-50 (frozen), RMSnorm',
                                inp=f'3x{_IMG_IN}x{_IMG_IN}', out=f'{model.img_width}x{S}x{S}', tr=0,
                                fr=sum(p.numel() for p in model.img_enc.parameters())))
                srcs.insert(1, '(image grid)')
            out.append(dict(name=', '.join(srcs), op='Concat (channels)',
                            inp=f'{"+".join(map(str, model.in_widths))}+{model.K}x{model.n_hidden} x{S}x{S}',
                            out=r['inp'], tr=0, fr=0))
        out.append(r)
        if r['name'] == 'tok_embed':
            out.append(dict(name='(token grid)', op=f'RMSnorm, replicate 1x1 -> {S}x{S}',
                            inp=r['out'], out=f'{r["out"]}x{S}x{S}', tr=0, fr=0))
        if r['name'] == 'linout':
            for k, (g, w) in enumerate(zip(regs, model.windows)):
                src = 'linout' + (f' - ({" + ".join(f"{q}[t]" for q in regs[:k])})' if k else '')
                out.append(dict(name=f'{g}[t] <- {src}',
                                op='Write (replace)' if w <= 1 else f'Write (EMA w={w:g})',
                                inp=H, out=H, tr=0, fr=0))
    w = max(len(r['name']) for r in out)
    wo = max(len(r['op']) for r in out)
    ws = max(max(len(r['inp']), len(r['out'])) for r in out)
    lines = [f'{"#":>3}  {"module":<{w}}  {"op":<{wo}}  {"in":>{ws}}    {"out":<{ws}}  {"params":>12}']
    for n, r in enumerate(out, 1):
        p = r['tr'] + r['fr']
        ps = '' if not p else f'{p:,}' + (' frozen' if r['fr'] and not r['tr'] else '')
        lines.append(f'{n:>3}  {r["name"]:<{w}}  {r["op"]:<{wo}}  {r["inp"]:>{ws}} -> '
                     f'{r["out"]:<{ws}}  {ps:>12}')
    return lines


def _param_summary(model):
    """Trainable/frozen parameter counts per top-level module, and the total."""
    seen, rows = set(), []
    for name, mod in model.named_children():
        tr = fr = 0
        for p in mod.parameters():
            if id(p) not in seen:
                seen.add(id(p))
                tr, fr = (tr + p.numel(), fr) if p.requires_grad else (tr, fr + p.numel())
        if tr or fr:
            rows.append((name, tr, fr))
    w = max(len(r[0]) for r in rows)
    out = [f'PARAMS  {"module":<{w}}  {"trainable":>13}  {"frozen":>13}  {"total":>13}']
    out += [f'PARAMS  {n:<{w}}  {tr:>13,}  {fr:>13,}  {tr + fr:>13,}' for n, tr, fr in rows]
    t_tr, t_fr = sum(r[1] for r in rows), sum(r[2] for r in rows)
    out.append('PARAMS  ' + '-' * (w + 46))
    out.append(f'PARAMS  {"TOTAL":<{w}}  {t_tr:>13,}  {t_fr:>13,}  {t_tr + t_fr:>13,}')
    out.append(f'PARAMS  total {(t_tr + t_fr) / 1e6:.3f} M ({t_tr / 1e6:.3f} M trainable, '
               f'{t_fr / 1e6:.3f} M frozen), weights {(t_tr + t_fr) * 4 / 2**20:.1f} MiB at fp32')
    return out


if not _ONESHOT or args.verbose:
    for line in ['── model graph (one token step, execution order) ──'] + _model_graph(model):
        print(line)
        _emit(f'INFO {line}', stdout=False)
    for line in _param_summary(model):
        _emit(line)

# ── generation helpers ────────────────────────────────────────────────────────


def _prompt_ids(text=''):
    """A prompt as ids, opened with START like every training document."""
    return [_tokenizer.start_id] + (_tokenizer.encode(text) if text else [])


def _rep1(text):
    """Share of the text taken by its most common word or non-space character (the larger):
    a high fluency score next to a high rep1 is a collapsed model, not a fluent one."""
    w = text.split()
    ch = [c for c in text if not c.isspace()]
    return max(max(collections.Counter(w).values()) / len(w) if w else 0.0,
               max(collections.Counter(ch).values()) / len(ch) if ch else 0.0)


class _GenScorer:
    """--gen_score: nats/token of a GEN sample under a frozen reference LM on the CPU,
    placed between anchors computed once from this run's corpus: FLOOR real text (100%),
    CEILING the same text with its words shuffled (0%)."""

    def __init__(self, repo):
        self.repo, self.ref, self.tok = repo, None, None
        self.floor = self.ceil = None
        self.failed = False

    def _load(self):
        if self.ref is not None or self.failed:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tok = AutoTokenizer.from_pretrained(self.repo)
            self.ref = AutoModelForCausalLM.from_pretrained(self.repo).to('cpu').eval()
            print(f'--gen_score: reference model {self.repo} loaded on cpu', flush=True)
        except Exception as e:                     # never take the training run down
            print(f'--gen_score: DISABLED, could not load {self.repo}: {e}', flush=True)
            self.failed = True

    @torch.no_grad()
    def _nll(self, text):
        ids = self.tok(text, return_tensors='pt', truncation=True, max_length=512).input_ids
        if ids.shape[1] < 2:
            return None
        v = float(self.ref(ids, labels=ids).loss)
        return v if math.isfinite(v) else None

    def _anchor(self):
        if self.floor is not None:
            return True
        with _text_lock:
            docs = [d for d in _anchors if len(d.split()) >= 24][:12]
        if len(docs) < 4:
            return False
        rng = random.Random(1234)
        lo, hi = [], []
        for d in docs:
            w = d.split()[:256]
            a = self._nll(' '.join(w))
            sw = w[:]
            rng.shuffle(sw)
            b = self._nll(' '.join(sw))
            if a is not None and b is not None:
                lo.append(a)
                hi.append(b)
        if len(lo) < 4 or np.mean(hi) - np.mean(lo) < 1e-6:
            return False
        self.floor, self.ceil = float(np.mean(lo)), float(np.mean(hi))
        print(f'--gen_score: anchors from {len(lo)} corpus documents -- FLOOR {self.floor:.3f} '
              f'(real text) CEILING {self.ceil:.3f} (words shuffled)', flush=True)
        return True

    def score(self, text):
        """-> 'nats 4.812 fluency 63% rep1 0.07', or '' if unavailable."""
        self._load()
        text = text.strip()
        if self.failed or len(text) < 16:
            return ''
        words = text.split()
        n = self._nll(' '.join(words[:256]) if words else text[:1024])
        if n is None:
            return ''
        rep1 = _rep1(text)
        if not self._anchor():
            return f'nats {n:.3f} fluency n/a (no anchors yet) rep1 {rep1:.2f}'
        pct = 100.0 * (self.ceil - n) / (self.ceil - self.floor)
        return f'nats {n:.3f} fluency {max(-999.0, min(999.0, pct)):.0f}% rep1 {rep1:.2f}'


_gen_scorer = _GenScorer(args.gen_score) if args.gen_score else None

_image = None                 # --image, as uint8 [3, h, w]
if args.image:
    if model.img_enc is None:
        raise SystemExit('--image needs a model with an image encoder')
    from PIL import Image
    _image = _prep_image(Image.open(args.image))

# ── one-shot: push / generate / vis ───────────────────────────────────────────

if args.push:
    if args.load is None and args.pretrained is None:
        raise SystemExit('--push requires --load (nothing to push but random weights)')
    local = os.path.basename(args.hub_repo)
    print(f'saving {args.load or args.pretrained} to ./{local} ...')
    model.to('cpu').save_pretrained(local)
    print(f'pushing to https://huggingface.co/{args.hub_repo} ...')
    model.push_to_hub(args.hub_repo, private=args.private or None)
    print('done')
    raise SystemExit(0)

if args.generate:
    if args.load is None and args.pretrained is None:
        print('WARNING: --generate without --load/--pretrained is running an untrained model')
    prompt = _prompt_ids(args.prompt)
    print(_render(prompt + model.generate(prompt, args.n, temperature=args.temperature,
                                          image=_image)))
    raise SystemExit(0)

if args.vis:
    import matplotlib.pyplot as plt
    _VIS_WIN = 180                                   # ticker width in characters
    plt.style.use('dark_background')
    plt.ion()
    rows = 1 + model.K
    fig = plt.figure(figsize=(max(7.5, _VIS_WIN * 7 * 0.602 / 72 * 1.05), 2.6 * rows + 1.2))
    gs = fig.add_gridspec(rows, 2, width_ratios=[1, 1.5], top=0.84, bottom=0.04, left=0.03,
                          right=0.98, hspace=0.25, wspace=0.10)
    axes = [fig.add_subplot(gs[r, 0]) for r in range(rows)]
    ax_p = fig.add_subplot(gs[:, 1])
    for r, ax in enumerate(axes):
        ax.set_title('output' if r == 0 else f'DFF {r}: {model.windows[r - 1]:g}-token window',
                     fontsize=9, pad=3)
    ax_p.set_title('P(next token)', fontsize=9, pad=3)
    for ax in axes + [ax_p]:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.text(0.03, 0.008, f'maps: std across the {model.n_hidden} channels at each of the '
             f'{model.S}x{model.S} positions', fontsize=8, color='0.7', va='bottom')
    header = fig.text(0.01, 0.99, '', family='monospace', fontsize=7, va='top', ha='left')
    PR = int(math.ceil(math.sqrt(model.vocab)))
    PC = int(math.ceil(model.vocab / PR))
    _exit = [False]
    fig.canvas.mpl_connect('key_press_event',
                           lambda e: _exit.__setitem__(0, _exit[0] or e.key in ('x', 'X')))

    model.eval()
    dev = next(model.parameters()).device
    prompt = _prompt_ids(args.prompt)
    pending, b = list(prompt[1:]), prompt[0]
    hist, cur = '', list(prompt)                     # finished episodes, current episode ids
    dff = model.new_state(1, dev)
    bank = _bank([_image], dev) if _image is not None else None
    imgs, vmax, img_p, nstep = [None] * rows, [None] * rows, None, 0
    while not _exit[0] and plt.fignum_exists(fig.number):
        with torch.no_grad():
            img = (model.image_grid(_views(*bank, start=torch.tensor([b == model.start_id],
                                                                     device=dev)))
                   if bank is not None else None)
            dff, o = model.step(torch.tensor([b], device=dev), dff, img)
            prob = F.softmax(model.text_dec(o)[0] / max(args.temperature, 1e-6), dim=-1)
        nstep += 1
        if pending:
            b = pending.pop(0)
        else:
            b = int(torch.multinomial(prob, 1).item())
            if b == model.end_id:                    # episode over: reset, prompt again
                hist = (hist + _render(cur) + ETX_TEXT)[-4096:]
                cur, dff = list(prompt), model.new_state(1, dev)
                pending, b = list(prompt[1:]), prompt[0]
            else:
                cur.append(b)
        maps = [o] + list(dff.chunk(model.K, dim=1))
        for r, t in enumerate(maps):
            m = t[0].std(dim=0).float().cpu().numpy()
            vmax[r] = float(m.max()) if vmax[r] is None else max(float(m.max()), 0.98 * vmax[r])
            if imgs[r] is None:
                imgs[r] = axes[r].matshow(m, cmap=args.cmap)
            imgs[r].set_data(m)
            imgs[r].set_clim(0.0, vmax[r] or 1e-9)
        pg = np.zeros(PR * PC, dtype=np.float32)
        pg[:model.vocab] = prob.cpu().numpy()
        pg = pg.reshape(PR, PC)
        if img_p is None:
            img_p = ax_p.matshow(pg, cmap=args.cmap)
        img_p.set_data(pg)
        img_p.set_clim(0, float(pg.max()) or 1e-9)
        ticker = ''.join(DOT_TEXT if c in '$\\' else c for c in hist + _render(cur))[-_VIS_WIN:]
        header.set_text(f'step {nstep:8d}  dff_std {float(dff.std()):6.4f}  dff_max '
                        f'{float(dff.abs().max()):7.3f}  p_max {float(prob.max()):5.3f}  '
                        f'T {args.temperature:.2f}\ngen: {ticker}')
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(args.delay)
    raise SystemExit(0)

# ── held-out eval ─────────────────────────────────────────────────────────────
# Each held-out set is built once and reused, so successive EVAL lines differ only by the
# weights. Every eval runs on a fresh state and restores the training state afterwards.

_eval_docs_cache = {}        # corpus -> [[(x, y), ...], ...]
_eval_imgs = {}              # image corpus -> [uint8 image] aligned with its eval docs
_eval_meta = {}              # image corpus -> [(id, class, caption)] aligned likewise
_eval_results = {}           # corpus[~kind] -> last result, for --eval's table / JSON
_eval_failed = {}            # corpus -> True once it has raised


def _eval_corpus_names():
    names = args.eval_corpora.split(',') if args.eval_corpora else dict.fromkeys(n for n, _ in _MIX)
    return [c.strip() for c in names if c.strip()]


def _eval_source(name):
    """(repo, config, split, column) of a corpus's held-out set; a name not in the table is
    taken as a hub repo id with a 'validation' split."""
    if name not in _TEXT_DATASETS:
        return name, None, 'validation', 'text'
    hf, cfg, split, col = _TEXT_DATASETS[name]
    held = _EVAL_SPLITS.get(name, split)
    if isinstance(held, tuple):
        hf, cfg, split = held
    else:
        split = held
    return hf, cfg, split, col


def _build_image_eval(corpus):
    """--eval_docs held-out captions of an image corpus, one from each of --eval_docs files
    spread over the (synset-sorted) shards, with their images; sorted by length."""
    import pyarrow.parquet as pq
    cfg = _IMAGE_DATASETS[corpus]
    files = sorted(glob.glob(os.path.join(cfg['dir'], '*.parquet')))
    items = []
    for f in files[::max(1, len(files) // max(1, args.eval_docs))]:
        rows = pq.ParquetFile(f).read_row_group(0, columns=['image', 'id', 'class', cfg['caption']])
        for r in rows.to_pylist():
            cap = (r[cfg['caption']] or '').strip()
            if cap and _id_heldout(r['id']):
                items.append((clip_text(cap)[:_EVAL_MAXLEN], _decode_image(r),
                              (r['id'], r['class'], cap)))
                break
        if len(items) >= args.eval_docs:
            break
    items.sort(key=lambda it: len(it[0]))
    _eval_imgs[corpus] = [it[1] for it in items]
    _eval_meta[corpus] = [it[2] for it in items]
    docs = [it[0] for it in items]
    print(f'eval set: {corpus} {len(docs)} held-out captions with images from {len(files)} '
          f'files, {sum(len(d) for d in docs)} tokens', flush=True)
    return docs


def _build_eval_docs(corpus):
    """The first --eval_docs held-out documents of `corpus`, framed like training clips,
    clipped to _EVAL_MAXLEN, sorted by length."""
    from datasets import load_dataset
    if corpus in _IMAGE_DATASETS:
        return _build_image_eval(corpus)
    hf, cfg, split, col = _eval_source(corpus)
    hashed = corpus in _HASH_HOLDOUT
    if hashed and corpus in _HUB_SUBSET:
        files = _hub_subset_files(corpus)
        files = files[:args.shards] if args.shards else files    # the training subset
        rows = load_dataset('parquet', data_files={'train': files}, split='train', streaming=True)
    else:
        if not hashed and corpus not in _EVAL_SPLITS:
            print(f'WARNING: no held-out split configured for "{corpus}"; scoring "{split}"')
        stream = (hashed or args.streaming or corpus in _STREAM_EVAL) and '[' not in split
        rows = load_dataset(hf, cfg, split=split, streaming=stream)
    print(f'eval set: {corpus} ({hf}' + (f' [{cfg}]' if cfg else '') +
          (f', hashed 1/{_HOLDOUT_MOD}' if hashed else f' {split}') + ') ...', flush=True)
    docs, seen = [], 0
    for ex in rows:
        seen += 1
        text = _corpus_text(corpus, ex) if corpus in _TEXT_DATASETS else ex.get(col, '') or ''
        if not text.strip() or (hashed and not _is_heldout(text)):
            continue
        steps = clip_text(text)
        if len(steps) >= _eval_minlen(corpus):
            docs.append(steps[:_EVAL_MAXLEN])
        if len(docs) >= args.eval_docs:
            break
    docs.sort(key=len)
    print(f'eval set: {len(docs)} documents, {sum(len(d) for d in docs)} tokens '
          f'(scanned {seen})', flush=True)
    return docs


def _eval_docs(corpus):
    if corpus not in _eval_docs_cache:
        _eval_docs_cache[corpus] = _build_eval_docs(corpus)
    return _eval_docs_cache[corpus]


def _doc_tokens(d):
    """A framed eval document as its token list, <STX> ... <ETX>."""
    return [x for x, _ in d] + [d[-1][1]]


class _EvalState:
    """Context manager: eval mode on a fresh state, training state and mode restored."""

    def __enter__(self):
        self.dff, self.was = model.dff, model.training
        model.eval()

    def __exit__(self, *exc):
        model.dff = self.dff
        model.train(self.was)


def _batches(rows):
    """[(inputs, targets)] -> padded (X, Y, M) device tensors per _EVAL_BATCH chunk."""
    dev = next(model.parameters()).device
    for c in range(0, len(rows), _EVAL_BATCH):
        chunk = rows[c:c + _EVAL_BATCH]
        B, T = len(chunk), max(len(xs) for xs, _ in chunk)
        X = torch.zeros((B, T), dtype=torch.long)
        Y = torch.zeros((B, T), dtype=torch.long)
        M = torch.zeros((B, T), dtype=torch.bool)
        for r, (xs, ys) in enumerate(chunk):
            X[r, :len(xs)] = torch.tensor(xs)
            Y[r, :len(ys)] = torch.tensor(ys)
            M[r, :len(xs)] = True
        yield chunk, X.to(dev), Y.to(dev), M.to(dev)


def _doc_rows(docs):
    return [([x for x, _ in d], [y for _, y in d]) for d in docs]


_band_cache = {}


def _token_bands(dev):
    """[V] long: each token id's --eval_bands band by frequency rank over the held-out
    targets of every eval corpus; ids never seen fall in the rarest band."""
    if 'b' not in _band_cache:
        cnt = collections.Counter()
        for c in _eval_corpus_names():
            for d in _eval_docs(c) or []:
                cnt.update(y for _, y in d)
        V = max(model.vocab, max(cnt) + 1 if cnt else 1)
        edges = [int(e) for e in args.eval_bands.split(',') if e.strip()]
        band = torch.full((V,), len(edges), dtype=torch.long)
        for r, (tid, _) in enumerate(cnt.most_common()):
            band[tid] = sum(r >= e for e in edges)
        _band_cache['b'] = band
        print(f'--eval_bands: ranks from {sum(cnt.values())} held-out tokens, {len(cnt)} '
              f'distinct; edges {edges}', flush=True)
    return _band_cache['b'].to(dev)


def _score(step, corpus, docs, imgs=None, tag=None):
    """EVAL (clean / median / runaway%) and EVALB (loss by frequency band) lines, tagged
    `tag` (default corpus). imgs: one image per doc, seen through a fresh random crop every
    token from a fixed-seed generator, so successive evals see the same crops."""
    tag = tag or corpus
    t0 = time.time()
    dev = next(model.parameters()).device
    band_of = _token_bands(dev) if args.eval_bands else None
    nb = int(band_of.max()) + 1 if band_of is not None else 0
    per_doc, bad_doc, band_sum, band_cnt = [], [], [], []
    with _EvalState(), torch.no_grad():
        c = 0
        gen = torch.Generator(device=dev).manual_seed(1234)
        for chunk, X, Y, M in _batches(_doc_rows(docs)):
            B, T = X.shape
            bank = _bank(imgs[c:c + B], dev) if imgs is not None else None
            c += B
            model.dff = None
            rs = torch.zeros(B, device=dev)
            bad = torch.zeros(B, dtype=torch.bool, device=dev)
            if nb:
                bsum = torch.zeros(B, nb, device=dev)
                bcnt = torch.zeros(B, nb, device=dev)
            for t in range(T):
                img = (model.image_grid(_views(*bank, gen, start=X[:, t] == model.start_id))
                       if bank is not None else None)
                logits, _ = model(X[:, t], img=img)
                ce = F.cross_entropy(logits, Y[:, t], reduction='none')
                # a diverged row is counted as runaway rather than poisoning the sums
                ce = torch.where(torch.isfinite(ce), ce, torch.full_like(ce, 1e30))
                if nb:
                    oh = F.one_hot(band_of[Y[:, t].clamp(max=band_of.numel() - 1)],
                                   nb).float() * M[:, t, None]
                    bsum += oh * ce[:, None]
                    bcnt += oh
                rs += ce * M[:, t]
                bad |= M[:, t] & (ce > _EVAL_THRESH)     # ANY token over: exp/score.py's rule
            per_doc.append((rs / M.sum(dim=1).clamp(min=1)).cpu().numpy())
            bad_doc.append(bad.cpu().numpy())
            if nb:
                band_sum.append(bsum.cpu().numpy())
                band_cnt.append(bcnt.cpu().numpy())
    per, bad = np.concatenate(per_doc), np.concatenate(bad_doc)
    clean = float(per[~bad].mean()) if (~bad).any() else float('nan')
    # nats per character over the clean documents: comparable across tokenizers
    nt = np.array([len(d) for d in docs], dtype=np.float64)
    nc = np.array([max(1, len(_decode_plain(_doc_tokens(d)))) for d in docs], dtype=np.float64)
    npc = float((per * nt)[~bad].sum() / nc[~bad].sum()) if (~bad).any() else float('nan')
    ppl = math.exp(min(clean, 700)) if clean == clean else float('nan')
    _eval_results[tag] = dict(corpus=tag, step=int(step), clean=clean,
                                 median=float(np.median(per)), ppl=ppl,
                                 runaway_pct=100.0 * float(bad.mean()), nrun=int(bad.sum()),
                                 docs=int(len(per)), tokens=int(nt.sum()))
    _emit(f'EVAL step {step:10} corpus {tag:8} clean {clean:11.6f} ppl {ppl:12.4f} '
          f'median {float(np.median(per)):11.6f} runaway {100.0 * float(bad.mean()):6.2f}% '
          f'nrun {int(bad.sum()):4d} docs {len(per):5d} wall {time.time() - t0:7.1f}s '
          f'nats/char {npc:.4f}')
    if nb and (~bad).any():
        bs = np.concatenate(band_sum)[~bad].sum(0)
        bc = np.concatenate(band_cnt)[~bad].sum(0)
        edges = [0] + [int(e) for e in args.eval_bands.split(',') if e.strip()]
        lbl = [f'r{a}-{b}' for a, b in zip(edges, edges[1:])] + [f'r{edges[-1]}+']
        _eval_results[f'{tag}~bands'] = dict(zip(lbl, (bs / np.maximum(bc, 1)).tolist()))
        _emit(f'EVALB step {step:10} corpus {tag:8} ' + ' '.join(
            f'{l} {bs[k] / bc[k]:.4f} ({100.0 * bc[k] / bc.sum():.0f}%)' if bc[k] else f'{l} n/a'
            for k, l in enumerate(lbl)))


def _ce_pairs(rows):
    """Per-position loss for rows of (inputs, targets), each from a fresh state; losses
    clamped to 30 nats."""
    out = []
    with _EvalState(), torch.no_grad():
        for chunk, X, Y, M in _batches(rows):
            model.dff = None
            ce = torch.zeros(X.shape, device=X.device)
            for t in range(X.shape[1]):
                logits, _ = model(X[:, t])
                v = F.cross_entropy(logits, Y[:, t], reduction='none')
                ce[:, t] = torch.where(torch.isfinite(v), v, torch.full_like(v, 30.0)).clamp(max=30.0)
            ce = ce.cpu().numpy()
            out += [ce[r, :len(xs)] for r, (xs, _) in enumerate(chunk)]
    return out


_reach_plan = {}             # corpus -> fixed splice plan, so every eval is paired
_REACH_CHUNKS = 4            # chunks per spliced row; the first is warm-up and not scored


def _reach_eval(step, corpus, docs):
    """EVALX: rows of _REACH_CHUNKS chunks of P tokens cut from random held-out documents,
    one reset per row. At offset c into a chunk only c+1 tokens of history belong to its
    document, so excess(c) = loss(spliced) - loss(same token, whole document) is the value
    of history older than c. Runaway tokens (>= 20 nats on either side) are dropped."""
    t0 = time.time()
    P, K = args.eval_reach_period, _REACH_CHUNKS
    pool = [_doc_tokens(d) for d in docs]
    elig = [i for i, q in enumerate(pool) if len(q) >= P + 2]
    if not elig:
        return
    if corpus not in _reach_plan:
        rng = random.Random(4321)
        _reach_plan[corpus] = [[(i, rng.randint(1, len(pool[i]) - 1 - P))
                                for i in (rng.choice(elig) for _ in range(K))]
                               for _ in range(args.eval_reach)]
    plan = _reach_plan[corpus]
    need = sorted({i for row in plan for i, _ in row[1:]})
    full = dict(zip(need, _ce_pairs([(pool[i][:-1], pool[i][1:]) for i in need])))
    spl = _ce_pairs([([t for i, st in row for t in pool[i][st:st + P]],
                      [t for i, st in row for t in pool[i][st + 1:st + P + 1]]) for row in plan])
    exc, cnt, bad = np.zeros(P), np.zeros(P), 0
    for r, row in enumerate(plan):
        for k in range(1, K):
            i, st = row[k]
            a, b = spl[r][k * P:(k + 1) * P], full[i][st:st + P]
            ok = (a < 20.0) & (b < 20.0)
            exc[ok] += (a - b)[ok]
            cnt[ok] += 1
            bad += int((~ok).sum())
    edges = [e for e in (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024) if e < P] + [P]
    parts, buckets = [], {}
    for lo, hi in zip(edges, edges[1:]):
        lbl = f'c{lo}' if hi == lo + 1 else f'c{lo}-{hi - 1}'
        buckets[lbl] = float(exc[lo:hi].sum() / max(cnt[lo:hi].sum(), 1))
        parts.append(f'{lbl} {buckets[lbl]:+.3f}')
    mean = float(exc.sum() / max(cnt.sum(), 1))
    tail = float(exc[64:].sum() / max(cnt[64:].sum(), 1)) if P > 64 else float('nan')
    rate = 100.0 * bad / max(bad + cnt.sum(), 1)
    _eval_results[f'{corpus}~reach'] = dict(mean=mean, tail64=tail, runaway=rate, **buckets)
    _emit(f'EVALX step {step:10} corpus {corpus:8} P {P} rows {len(plan)} runaway {rate:.1f}% '
          f'| mean {mean:+.4f} tail64 {tail:+.4f} | ' + ' '.join(parts)
          + f' | wall {time.time() - t0:.1f}s')


def _info_eval(step, corpus, docs):
    """EVALI: how much the K registers overlap and what each is worth, on --eval_info
    documents. Pass 1 accumulates the covariance of the K*C register channels over tokens
    and grid positions (position means removed):
      rms      sqrt(mean channel variance) per register
      rank     participation ratio of each register's eigenvalues; 'cat' for the K
               concatenated at equal total variance, against their sum
      MI ij    Gaussian mutual information (nats) from canonical correlations
      rho1     largest canonical correlation; n>.9 how many exceed 0.9
      TC       Gaussian total correlation
    Then registers are read as their mean instead of their value (each alone, then all; every
    subset when K <= 3) and the loss rise d<set> over the base is reported; red ij = d ij -
    d i - d j is positive when i and j carry the same useful information."""
    K, C, S = model.K, model.n_hidden, model.S
    D = K * C
    dev = next(model.parameters()).device
    t0 = time.time()
    sel = docs[:args.eval_info]

    def run(stats):
        tot, ntok = torch.zeros((), dtype=torch.float64, device=dev), 0
        if stats:
            s2 = torch.zeros(D, D, dtype=torch.float64, device=dev)
            ps = torch.zeros(S * S, D, dtype=torch.float64, device=dev)
        for chunk, X, Y, M in _batches(_doc_rows(sel)):
            model.dff = None
            for t in range(X.shape[1]):
                logits, _ = model(X[:, t])
                m = M[:, t]
                ce = F.cross_entropy(logits, Y[:, t], reduction='none')
                ce = torch.where(torch.isfinite(ce), ce, torch.full_like(ce, 30.0)).clamp(max=30.0)
                tot += (ce * m).sum().double()
                ntok += int(m.sum())
                if stats and m.any():
                    z = model.dff[m].permute(0, 2, 3, 1).float()          # [b, S, S, D]
                    ps += z.sum(0).reshape(S * S, D).double()
                    z = z.reshape(-1, D)
                    s2 += (z.T @ z).double()
        out = {'loss': float(tot) / max(ntok, 1), 'ntok': ntok}
        if stats:
            mu = ps / max(ntok, 1)
            out['cov'] = s2 / max(ntok * S * S, 1) - mu.T @ mu / (S * S)
            out['mean'] = mu.float().T.reshape(1, D, S, S)
        return out

    try:
        with _EvalState(), torch.no_grad():
            base = run(True)
            cov = base['cov']
            cov = (cov + cov.T) / 2
            blk = [cov[i * C:(i + 1) * C, i * C:(i + 1) * C] for i in range(K)]
            ridge = [1e-4 * float(torch.trace(b)) / C + 1e-30 for b in blk]
            rms = [math.sqrt(max(float(torch.trace(b)) / C, 0.0)) for b in blk]

            def pr(m):
                l = torch.linalg.eigvalsh(m).clamp(min=0)
                return float(l.sum() ** 2 / (l.pow(2).sum() + 1e-300))
            rank = [pr(b) for b in blk]
            sc = torch.cat([torch.full((C,), 1.0 / math.sqrt(max(float(torch.trace(b)), 1e-300)),
                                       dtype=torch.float64, device=dev) for b in blk])
            rank_cat = pr(cov * sc[:, None] * sc[None, :])

            def isqrt(m, r):
                l, v = torch.linalg.eigh(m + r * torch.eye(C, dtype=m.dtype, device=m.device))
                return (v * l.clamp(min=r).rsqrt()) @ v.T
            W = [isqrt(b, r) for b, r in zip(blk, ridge)]
            mi, rho1, n9 = {}, {}, {}
            for i in range(K):
                for j in range(i + 1, K):
                    rho = torch.linalg.svdvals(W[i] @ cov[i * C:(i + 1) * C, j * C:(j + 1) * C] @ W[j])
                    rho = rho.clamp(max=1 - 1e-9)
                    mi[(i, j)] = float(-0.5 * torch.log1p(-rho.pow(2)).sum())
                    rho1[(i, j)], n9[(i, j)] = float(rho[0]), int((rho > 0.9).sum())
            rI = torch.cat([torch.full((C,), r, dtype=torch.float64, device=dev) for r in ridge])
            ld = lambda m: float(torch.linalg.slogdet(m)[1])
            tc = 0.5 * (sum(ld(b + r * torch.eye(C, dtype=b.dtype, device=dev))
                            for b, r in zip(blk, ridge)) - ld(cov + torch.diag(rI)))
            model._read_mean = base['mean'].to(dev)
            dl = {}
            for r in range(1, K + 1):
                if K > 3 and 1 < r < K:              # 2^K passes is too many: singles and all
                    continue
                for sub in itertools.combinations(range(K), r):
                    model._ablate = set(sub)
                    dl[sub] = run(False)['loss'] - base['loss']
    finally:
        model._ablate = model._read_mean = None

    n = lambda sub: ''.join(str(k + 1) for k in sub)
    pairs = [(i, j) for i in range(K) for j in range(i + 1, K)]
    line = (f'EVALI step {step:10} corpus {corpus:8} docs {len(sel)} tokens {base["ntok"]} | '
            'win ' + '/'.join(f'{w:.1f}' for w in model.windows) +
            ' | rms ' + '/'.join(f'{v:.4f}' for v in rms) +
            ' | rank ' + '/'.join(f'{v:.1f}' for v in rank))
    if pairs:
        line += (f' cat {rank_cat:.1f} (sum {sum(rank):.1f}) | MI ' +
                 ' '.join(f'{n(p)} {mi[p]:.1f}' for p in pairs) + f' TC {tc:.1f} | rho1 ' +
                 ' '.join(f'{n(p)} {rho1[p]:.3f}' for p in pairs) + ' n>.9 ' +
                 ' '.join(f'{n(p)} {n9[p]}' for p in pairs))
    line += (f' | base {base["loss"]:.4f} d ' + ' '.join(f'{n(s)} {v:+.4f}' for s, v in dl.items()))
    if pairs:
        line += ' | red ' + ' '.join(f'{n(p)} {dl[p] - dl[(p[0],)] - dl[(p[1],)]:+.4f}'
                                     for p in pairs if p in dl)
    line += f' | wall {time.time() - t0:.1f}s'
    _eval_results[f'{corpus}~info'] = dict(rms=rms, rank=rank, rank_cat=rank_cat,
                                           mi={n(p): v for p, v in mi.items()}, tc=tc,
                                           base=base['loss'], d={n(k): v for k, v in dl.items()})
    _emit(line)


class _Judge:
    """EVALG's frozen judge LM: bf16 on the training GPU, else fp32 on the CPU."""

    def __init__(self, repo):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        md = next(model.parameters()).device
        self.dev = md if md.type == 'cuda' else torch.device('cpu')
        dt = torch.bfloat16 if self.dev.type == 'cuda' else torch.float32
        self.tok = AutoTokenizer.from_pretrained(repo)
        self.lm = AutoModelForCausalLM.from_pretrained(repo, dtype=dt).to(self.dev).eval()
        for p in self.lm.parameters():
            p.requires_grad_(False)
        print(f'--eval_gen: judge {repo} loaded on {self.dev} ({dt})', flush=True)

    @torch.no_grad()
    def cond_nll(self, prompt, cont):
        """Mean nats/token of cont after prompt (prompt tokens not scored)."""
        p = self.tok(prompt).input_ids
        full = self.tok(prompt + cont, truncation=True, max_length=1024).input_ids
        if len(full) - len(p) < 2:
            return None
        ids = torch.tensor([full], device=self.dev)
        lab = ids.clone()
        lab[0, :len(p)] = -100
        v = float(self.lm(ids, labels=lab).loss.float())
        return v if math.isfinite(v) else None


_judge = None
_gen_anchor = {}             # corpus -> [(prompt ids, prompt text, real nats, shuffled nats)]


def _gen_eval(step, corpus, docs):
    """EVALG: continue held-out prompts; the judge scores the continuation given the prompt,
    against the document's real continuation (floor) and its words shuffled (ceiling)."""
    global _judge
    t0 = time.time()
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    P, C = args.eval_gen_prompt, args.eval_gen_len
    if corpus not in _gen_anchor:
        rng, items = random.Random(1234), []
        for d in docs:
            q = _doc_tokens(d)
            if len(q) < 1 + P + C:
                continue
            ptxt, real = _decode_plain(q[:1 + P]), _decode_plain(q[1 + P:1 + P + C])
            sw = real.split()
            rng.shuffle(sw)
            a, b = _judge.cond_nll(ptxt, real), _judge.cond_nll(ptxt, ' ' + ' '.join(sw))
            if a is not None and b is not None:
                items.append((q[:1 + P], ptxt, a, b))
            if len(items) >= args.eval_gen:
                break
        _gen_anchor[corpus] = items
    g_n, r_n, s_n, reps, d2s = [], [], [], [], []
    dev = next(model.parameters()).device
    with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
        for prompt, ptxt, a, b in _gen_anchor[corpus]:
            out = model.generate(prompt, C, temperature=args.temperature)
            if _tokenizer.end_id in out:                  # one continuation, not a new doc
                out = out[:out.index(_tokenizer.end_id)]
            ctxt = _decode_plain(out)
            n = _judge.cond_nll(ptxt, ctxt) if ctxt.strip() else None
            if n is None:
                continue
            w = ctxt.split()
            bg = list(zip(w, w[1:]))
            g_n.append(n); r_n.append(a); s_n.append(b)
            reps.append(_rep1(ctxt)); d2s.append(len(set(bg)) / len(bg) if bg else 0.0)
    if not g_n:
        return
    g, r, s = float(np.mean(g_n)), float(np.mean(r_n)), float(np.mean(s_n))
    flu = 100.0 * (s - g) / (s - r) if s > r else float('nan')
    _eval_results[f'{corpus}~gen'] = dict(nats=g, real=r, shuf=s, fluency=flu,
                                          rep1=float(np.mean(reps)), distinct2=float(np.mean(d2s)))
    _emit(f'EVALG step {step:10} corpus {corpus:8} prompts {len(g_n)} nats {g:.4f} '
          f'real {r:.4f} shuf {s:.4f} fluency {flu:.1f}% rep1 {np.mean(reps):.3f} '
          f'distinct2 {np.mean(d2s):.3f} wall {time.time() - t0:.1f}s')


def _heldout_eval(step):
    """Every eval corpus: EVAL/EVALB, then for text corpora EVALX, EVALG and EVALI (first
    text corpus only). An image corpus is scored with its images and again blind (image grid
    zeroed); the gap is what the model takes from the image. Failures are reported and
    never take the training run down."""
    text = [c for c in _eval_corpus_names() if c not in _IMAGE_DATASETS]
    for corpus in _eval_corpus_names():
        if _eval_failed.get(corpus):
            continue
        try:
            docs = _eval_docs(corpus)
            if not docs:
                print(f'WARNING: no usable held-out documents for "{corpus}"; skipping it')
                continue
            if corpus in _IMAGE_DATASETS:
                _score(step, corpus, docs, _eval_imgs[corpus])
                _score(step, corpus, docs, tag=f'{corpus}-blind')
                continue
            _score(step, corpus, docs)
        except Exception as e:
            print(f'WARNING: eval failed at step {step} on "{corpus}": {e!r}; disabling it',
                  flush=True)
            _eval_failed[corpus] = True
            continue
        for fn, on in ((_reach_eval, args.eval_reach), (_gen_eval, args.eval_gen),
                       (_info_eval, args.eval_info and corpus == text[0])):
            if on:
                try:
                    fn(step, corpus, docs)
                except Exception as e:
                    print(f'WARNING: {fn.__name__} failed at step {step} on "{corpus}": {e!r}',
                          flush=True)


if args.eval:
    if args.load is None and args.pretrained is None:
        print('WARNING: --eval without --load/--pretrained is measuring an untrained model')
    _heldout_eval(_start_step)
    ck = args.load or args.pretrained or '(untrained)'
    print(f'\n{"=" * 93}\nPROTOCOL EVAL  {ck}  step {_start_step}\n{"=" * 93}')
    print(f'{"corpus":17} {"clean":>10} {"ppl":>11} {"median":>10} {"runaway%":>9} '
          f'{"nrun":>5} {"docs":>6} {"tokens":>9}')
    print('-' * 93)
    for c in [k for n in _eval_corpus_names()
              for k in ((n, f'{n}-blind') if n in _IMAGE_DATASETS else (n,))]:
        r = _eval_results.get(c)
        if r is None:
            print(f'{c:17} {"(failed or empty -- see WARNING above)":>50}')
        else:
            print(f'{c:17} {r["clean"]:10.4f} {r["ppl"]:11.2f} {r["median"]:10.4f} '
                  f'{r["runaway_pct"]:9.2f} {r["nrun"]:5d} {r["docs"]:6d} {r["tokens"]:9d}')
    print('-' * 93)
    print('note: compare a corpus across checkpoints, never across corpora')
    if args.eval_json:
        with open(args.eval_json, 'w') as f:
            json.dump({'checkpoint': ck, 'step': int(_start_step), 'eval_docs': args.eval_docs,
                       'minlen': _EVAL_MINLEN, 'maxlen': _EVAL_MAXLEN, 'thresh': _EVAL_THRESH,
                       'results': _eval_results}, f, indent=1)
        print(f'wrote {args.eval_json}')
    raise SystemExit(0)

# ── optimizer / schedule ──────────────────────────────────────────────────────

_trainable = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(_trainable, lr=args.lr_max, momentum=args.momentum,
                            weight_decay=args.weight_decay)
if _loaded_ckpt is not None and _loaded_ckpt.get('optimizer'):
    osd = optimizer.state_dict()
    ck = _loaded_ckpt['optimizer']
    if [len(g['params']) for g in ck['param_groups']] == [len(g['params']) for g in osd['param_groups']]:
        osd['state'] = ck['state']
        optimizer.load_state_dict(osd)
        print(f'optimizer state restored ({len(osd["state"])} tensors)', flush=True)
    else:
        print('WARNING: optimizer state NOT restored: parameter groups differ', flush=True)
_loaded_ckpt = None


def _lr_factor(step):
    """lr / lr_max at a global step."""
    if args.schedule == 'const':
        return 1.0
    f = (1.0 - math.cos(math.pi * min(step / max(1, args.lr_period), 1.0))) / 2.0
    return (args.lr_min + (args.lr_max - args.lr_min) * f) / args.lr_max


scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=_lr_factor)
if _start_step:              # resume: fast-forward the schedule to the checkpoint's step
    scheduler.last_epoch = _start_step
    lrs = [base * _lr_factor(_start_step) for base in scheduler.base_lrs]
    for g, lr in zip(optimizer.param_groups, lrs):
        g['lr'] = lr
    scheduler._last_lr = lrs

# ── training loop ─────────────────────────────────────────────────────────────

stop = threading.Event()
q = queue.Queue(maxsize=args.batch)
w = threading.Thread(target=worker, args=(stop, q, hf_datasets))
w.start()

# Image rows: each holds its current image in a GPU canvas, and every step a fresh random
# 224x224 crop of it goes through the encoder. Text rows get a zero image grid.
_img_rows = torch.tensor(_IMAGE_ROWS, dtype=torch.long, device=args.device)
_bank_of = {r: j for j, r in enumerate(_IMAGE_ROWS)}
img_bank = torch.zeros(len(_IMAGE_ROWS), 3, _IMG_BANK, _IMG_BANK, dtype=torch.uint8,
                       device=args.device)
img_fit = torch.zeros(len(_IMAGE_ROWS), 3, _IMG_IN, _IMG_BANK, dtype=torch.uint8,
                      device=args.device)
img_hw = torch.full((len(_IMAGE_ROWS), 3), float(_IMG_BANK), device=args.device)
if _IMAGE_ROWS and model.img_enc is None:
    raise SystemExit('--mix has an image corpus but the model has no image encoder')
# rows of each corpus, for the per-corpus loss columns of a mixed run
_rows_of, _r = {}, 0
for _n, _k in _MIX:
    _rows_of.setdefault(_n, []).extend(range(_r, _r + _k))
    _r += _k
_text_names = [n for n in _rows_of if n not in _IMAGE_DATASETS]


def _grad_norm():
    return sum(p.grad.detach().norm(2).item() ** 2
               for p in model.parameters() if p.grad is not None and p.requires_grad) ** 0.5


def _save(i, n_examples):
    if not all(torch.isfinite(t).all() for t in model.state_dict().values()
               if t.is_floating_point()):
        print(f'WARNING: non-finite params at step {i}; skipping checkpoint save')
        return
    log = open(args.log).read() if os.path.exists(args.log) else ''
    torch.save({'saved_args': vars(args), 'state_dict': model.state_dict(), 'log': log,
                'step': i, 'examples': n_examples, 'examples_by': dict(_n_by),
                'lr': optimizer.param_groups[0]['lr'],
                'optimizer': optimizer.state_dict()}, args.save)


def _gen_lines(i):
    """GEN samples (text-only, from <STX> and --prompt), captions of --gen_images held-out
    images per image eval corpus for the --gen_vis panel (one GENI/REF pair of them in the
    log), and a recent training text per corpus."""
    lines = []
    for p in dict.fromkeys(['', args.prompt]):
        prompt = _prompt_ids(p)
        out = model.generate(prompt, _GEN_SAMPLE, temperature=args.temperature)
        lines.append(f'GEN step {i:10} [{p or STX_TEXT}]: {_render(prompt + out)}')
        sc = _gen_scorer.score(_decode_plain(out)) if _gen_scorer else ''
        if sc:
            lines.append(f'GENSCORE step {i:10} [{p or STX_TEXT}]: {sc}')
    panel = []
    for c in _eval_corpus_names():
        if c not in _IMAGE_DATASETS or model.img_enc is None or not args.gen_images:
            continue
        n = len(_eval_docs(c))
        if not n:
            continue
        # a new random set of held-out images every --eval_interval steps, keyed by the step
        # block alone so a resume redraws the same set and runs see the same images at the
        # same step; the log gets one pair per GEN, cycling through the set
        blk = i // args.eval_interval if args.eval_interval else 0
        ks = random.Random(f'{c}:{blk}').sample(range(n), min(n, args.gen_images))
        logk = ks[(i // args.gen_interval) % len(ks)] if args.gen_interval else ks[0]
        for k in ks if args.gen_vis and _gen_inbox is not None else [logk]:
            prompt = _prompt_ids()
            out = model.generate(prompt, _GEN_SAMPLE, temperature=args.temperature,
                                 image=_eval_imgs[c][k])
            out = out[:out.index(model.end_id) + 1] if model.end_id in out else out
            iid, cls, cap = _eval_meta[c][k]
            if k == logk:
                lines.append(f'GENI step {i:10} [{iid} {cls.split(",")[0]}]: '
                             f'{_render(prompt + out)}')
                lines.append(f'REF  step {i:10} [{iid}]: {_printable(cap[:400])}')
            panel.append((_eval_imgs[c][k].permute(1, 2, 0).numpy(),
                          f'{cls.split(",")[0]}  ({iid})', _decode_plain(out), cap))
    if panel and _gen_inbox is not None and args.gen_vis:
        try:
            _gen_inbox.put_nowait(('gen', i, panel))
        except queue.Full:
            pass                                  # viewer busy: skip this panel
    with _text_lock:
        samples = {n: st['sample'] for n, st in _text_stats.items() if st['sample']}
    for n, smp in samples.items():
        lab = 'SAMPLE' if n == (_text_names or [None])[0] else n
        lines.append(f'TXT-{lab}: {_printable(_sample_window(smp))}')
    return lines


def _thumb(x, side):
    """uint8 [3, h, w] (GPU) -> uint8 HWC numpy with its longer side `side`."""
    s = side / max(x.shape[1:])
    size = (max(1, round(x.shape[1] * s)), max(1, round(x.shape[2] * s)))
    t = F.interpolate(x[None].float(), size=size, mode='area')[0]
    return t.round().clamp(0, 255).byte().permute(1, 2, 0).cpu().numpy()


_sample = None                # --sample_vis: {'row', 'rec'} while recording one example
_img_name = {}                # bank index -> 'class (id)' of the image it holds
_IMG_MEAN_T = torch.tensor(_IMG_MEAN, device=args.device).view(3, 1, 1)
_IMG_STD_T = torch.tensor(_IMG_STD, device=args.device).view(3, 1, 1)


def _record_sample(i, x_list, flag_list, views):
    """--sample_vis: from the next start of an example on the recorded row until the next
    one, keep each step's crop (as the encoder saw it) and the token read with it; then send
    the example to the viewer."""
    global _sample
    r = _sample['row']
    j = _bank_of[r]
    if flag_list[r]:
        if _sample['rec'] is not None:                # the recorded example just ended
            rec = _sample['rec']
            try:
                _gen_inbox.put_nowait(('sample', rec['step'], rec['img'], rec['name'],
                                       rec['crops'], rec['toks']))
            except queue.Full:
                pass
            _sample = None
            return
        h, w = int(img_hw[j, 0]), int(img_hw[j, 1])
        _sample['rec'] = {'step': i, 'img': _thumb(img_bank[j, :, :h, :w], 360),
                          'name': _img_name.get(j, ''), 'crops': [], 'toks': []}
    rec = _sample['rec']
    if rec is not None and len(rec['crops']) < 160:
        crop = ((views[j] * _IMG_STD_T + _IMG_MEAN_T) * 255.0).clamp(0, 255)
        rec['crops'].append(_thumb(crop, 96))
        rec['toks'].append(_tokenizer.decode([x_list[r]]) if x_list[r] != model.start_id
                           else STX_TEXT)


larr, garr = [], []
carr = {n: [] for n in _rows_of} if len(_rows_of) > 1 else {}
i, n_examples = _start_step, _start_exs
_n_by = {n: int(_start_exs_by.get(n, 0)) for n in _rows_of}     # examples trained per corpus
# STEP columns ex_t/ep_t (text corpora pooled) and ex_i/ep_i (image corpora pooled): examples
# trained and passes over the data (examples / corpus size; a streaming text corpus, whose
# size is unknown, reports its reshuffle count instead)
_kinds = [(k, ns, [_corpus_size(n) for n in ns]) for k, ns in
          (('t', _text_names), ('i', [n for n in _rows_of if n in _IMAGE_DATASETS])) if ns]


def _abbr(n):
    """A count in 6 characters: 9999, 437.4K, 2.544M, 25.44M, 254.4M, 2.544G."""
    if n < 10000:
        return f'{n:6d}'
    for div, unit in ((1e3, 'K'), (1e6, 'M'), (1e9, 'G')):
        v = n / div
        if v < 999.95 or unit == 'G':
            return f'{v:.{3 if v < 9.9995 else 2 if v < 99.995 else 1}f}{unit}'.rjust(6)


def _ex_ep():
    out = ''
    for k, ns, sizes in _kinds:
        ex = sum(_n_by[n] for n in ns)
        ep = (ex / sum(sizes) if all(sizes) else
              float(sum(_epoch[n] for n in ns)) / len(ns))
        out += f' ex_{k} {_abbr(ex)} ep_{k} {ep:6.3f}'
    return out


try:
    while True:
        if i % args.checkpoint == 0:
            _save(i, n_examples)
            counts = _text_drain()
            te, tt = sum(e for e, _ in counts.values()), sum(t for _, t in counts.values())
            if te:
                ep = ' '.join(f'{n}={_epoch[n]}' for n in _text_names)
                per = (' | ' + ' '.join(f'{n} {e}/{t}' for n, (e, t) in counts.items())
                       if len(counts) > 1 else '')
                _emit(f'TEXT step {i:10} examples {te} tokens {tt} epoch {ep}{per}')

        # after the save, so an EVAL line describes weights that exist on disk; not at step
        # 0, where it would only measure ln(vocab)
        if args.eval_interval and i > 0 and i % args.eval_interval == 0:
            _heldout_eval(i)

        if args.gen_interval and i % args.gen_interval == 0:
            _emit('\n' + '\n'.join(_gen_lines(i)) + '\n')
            if _gen_inbox is not None and args.sample_vis and _IMAGE_ROWS:
                _sample = {'row': _IMAGE_ROWS[0], 'rec': None}     # record the next example

        x_list, y_list, flag_list, new_imgs = q.get()
        n_examples += sum(flag_list)
        for n, rows in _rows_of.items():
            _n_by[n] += sum(flag_list[r] for r in rows)
        x = torch.tensor(x_list, dtype=torch.long).to(args.device)
        y = torch.tensor(y_list, dtype=torch.long).to(args.device)
        flag = torch.tensor(flag_list, dtype=torch.bool).to(args.device)
        img = None
        if _IMAGE_ROWS:
            for r, (im, name) in new_imgs:
                j = _bank_of[r]
                _bank_put(img_bank, img_hw, img_fit, j, im.to(args.device, non_blocking=True))
                _img_name[j] = name
            views = _views(img_bank, img_hw, img_fit, start=flag[_img_rows])
            img = torch.zeros(len(x_list), model.img_width, model.S, model.S, device=args.device)
            img[_img_rows] = model.image_grid(views)
            if _sample is not None:
                _record_sample(i, x_list, flag_list, views)

        dff_prev = model.dff
        model.train()
        logits, loss = model(x, targets=y, flag=flag, img=img)
        if not torch.isfinite(loss):         # keep the last good checkpoint on disk
            print(f'\n*** HALT: non-finite loss at step {i}: {loss.item()} dff_max '
                  f'{float(model.dff.abs().max())} logit_max {float(logits.detach().abs().max())}')
            break
        loss.backward()
        gnorm = _grad_norm()
        garr.append(gnorm)
        if not math.isfinite(gnorm):
            print(f'\n*** HALT: non-finite grad at step {i}')
            break
        optimizer.step()
        # recompute this step's state with the updated weights (eval-mode BatchNorm), so the
        # state carried forward is the one the model would compute at inference
        model.dff = dff_prev
        model.eval()
        with torch.no_grad():
            model(x, flag=flag, img=img)

        larr.append(loss.item())
        if carr:
            with torch.no_grad():
                ce = F.cross_entropy(logits.detach(), y, reduction='none')
                for n, rows in _rows_of.items():
                    carr[n].append(float(ce[rows].mean()))
        if i % args.monitor == 0:
            flat = model.dff.reshape(-1)
            line = ('STEP {:10} wall {} loss {:12.9f} grad {:12.6f} lr {:10.9f} dff_mean {:12.5f} '
                    'dff_std {:12.5f} dff_max {:11.3f}'
                    ).format(i, datetime.datetime.now(), np.mean(larr[-args.monitor:]),
                             np.mean(garr[-args.monitor:]), optimizer.param_groups[0]['lr'],
                             flat.mean().item(), flat.std().item(), flat.abs().max().item())
            line += _ex_ep()
            line += ''.join(f' loss_{n} {np.mean(a[-args.monitor:]):12.9f}' for n, a in carr.items())
            _emit(line)
            del larr[:-args.monitor], garr[:-args.monitor]   # keep host RAM flat
            for a in carr.values():
                del a[:-args.monitor]

        scheduler.step()
        optimizer.zero_grad()
        i += 1
        if args.run_steps is not None and i - _start_step >= args.run_steps:
            break
except KeyboardInterrupt:
    pass

print('\nSTOPPING THREADS')
stop.set()
if _gen_proc is not None:
    _gen_proc.terminate()
while not q.empty():
    q.get()
w.join()
print('EXIT MAIN')
# Hard exit: streaming datasets keep native threads whose teardown can crash Python's
# finalization. Everything is already saved.
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
