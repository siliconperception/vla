#!/usr/bin/env python3
# vla.py -- Vision-Language-Audio CNN model (text-only core)
# Silicon Perception Inc.
#
# Recurrent CNN core: a per-token ContextCNN DFF loop + DecoderCNN. The current
# token is embedded, broadcast over an S×S grid, projected and summed into the
# recurrent DFF state; the decoder reads the state out to next-token logits.
# Image and audio conditioning will be added back incrementally.
#
# Vocabulary: 256 (raw bytes) by default, or a borrowed pretrained BPE vocabulary and its
# embedding/readout -- TinyStories or Pile-trained pythia -- with --tokenizer (see
# _TOKENIZERS). No attention, no positional encoding.

import math
import torch ; print('torch', torch.__version__)
import torch.nn as nn
from torch.nn import functional as F
import torchinfo
import numpy as np
import argparse
import collections
import itertools
import re
import glob
import json
import zlib
import os
import queue
import threading
import subprocess
import datetime
import time
import random
import matplotlib.pyplot as plt

NULL      = 0x00
START     = 0x02
END       = 0x03

# length of the GEN sample printed each --gen_interval steps during training. Fixed, not
# --n: --n is the length of a one-shot --generate run and nothing else.
_GEN_SAMPLE = 200

# In-training held-out eval (--eval_interval). These are protocol constants, not knobs:
# they are exactly the document selection exp/score.py and exp/pythia_ref.py use for every
# number in PLAN.txt's reference table (first --eval_docs documents of the held-out split
# that tokenize to >= _EVAL_MINLEN steps, each clipped to _EVAL_MAXLEN). Changing one
# silently makes the EVAL line incomparable to that table and to the pythia references,
# which is the whole reason the eval exists -- so they are pinned here rather than exposed.
_EVAL_MINLEN = 512
_EVAL_MAXLEN = 1024
_EVAL_BATCH  = 400    # rows per forward chunk. Cost here is dominated by SEQUENTIAL steps
                      # (51 conv launches each), not by batch width, so one wide chunk beats
                      # several narrow ones even though it pads every row out to the longest.
                      # exp/score.py scores all 400 documents as a single batch for the same
                      # reason. Safe to lower if a bigger --eval_docs ever runs out of memory:
                      # eval-mode BatchNorm uses running stats with --bn_track, so per-document
                      # results are batch-invariant to 1e-4 and chunking changes nothing.
_EVAL_THRESH = 20.0   # per-document nats above which a document is counted "runaway"

STX_TEXT  = '<STX>'   # how START renders in displayed text
ETX_TEXT  = '<ETX>'   # how END renders in displayed text


DOT_TEXT  = '\xb7'    # how any other unprintable byte renders
NULL_TEXT = '_'       # how NULL renders

_ESCAPES  = {'\n': '\\n', '\t': '\\t', '\r': '\\r'}


def _printable(s):
    """Render model text for display: START/END as <STX>/<ETX>, NULL as '_',
    whitespace escaped, any other unprintable character as '·'. Matches _vc(),
    the --vis renderer, so all three modes display the same markers."""
    out = []
    for c in s:
        o = ord(c)
        if   o == START:      out.append(STX_TEXT)
        elif o == END:        out.append(ETX_TEXT)
        elif o == NULL:       out.append(NULL_TEXT)
        elif c in _ESCAPES:   out.append(_ESCAPES[c])
        elif c.isprintable(): out.append(c)
        else:                 out.append(DOT_TEXT)
    return ''.join(out)


# ── tokenizers ────────────────────────────────────────────────────────────────
# --tokenizer selects the vocabulary the whole script runs on: the clip builder emits
# ids from it, the model embeds/decodes them, and every display path renders them.
# 'char' is the raw-byte default; every other name pulls a pretrained BPE tokenizer
# together with that model's embedding and lm_head (see VLAModel).

_TOKENIZERS = {
    'char':       None,
    'tiny1m':     'roneneldan/TinyStories-1M',   # GPT-Neo,  hidden 64,  vocab 50257
    'tiny8m':     'roneneldan/TinyStories-8M',   # GPT-Neo,  hidden 256, vocab 50257
    'pythia14m':  'EleutherAI/pythia-14m',       # GPT-NeoX, hidden 128, vocab 50304
    'pythia31m':  'EleutherAI/pythia-31m',       # GPT-NeoX, hidden 256, vocab 50304
    'pythia70m':  'EleutherAI/pythia-70m',       # GPT-NeoX, hidden 512, vocab 50304
    'pythia160m': 'EleutherAI/pythia-160m',      # GPT-NeoX, hidden 768, vocab 50304
}

# The TinyStories models are trained on a deliberately simple corpus, so most of their
# 50257 embedding rows never receive gradient: 41% of TinyStories-8M's rows sit at their
# random init, and 7-9% of OpenWebText/dolma3 tokens land on one. Frozen, those tokens are
# unrepresentable on input and unpredictable on output. The pythia* models are trained on
# the Pile (300B tokens) and have no untrained rows, so they are the ones to reach for on a
# web-scale --dataset; tiny* remain the right choice for --dataset tiny.

# --head_norm ln_f borrows the source model's own final norm, the one it applies
# immediately before its unembedding. Probed in order; the first hit wins.
_FINAL_NORM_PATHS = (
    'transformer.ln_f',               # gpt_neo, gpt2
    'gpt_neox.final_layer_norm',      # gpt_neox (pythia)
    'model.norm',                     # llama, mistral
    'model.decoder.final_layer_norm', # opt
)


def _final_norm(lm):
    """The pretrained final norm layer of a causal LM, or (None, None) if the family is
    unknown -- --head_norm ln_f then warns and falls back to no normalization."""
    for path in _FINAL_NORM_PATHS:
        m = lm
        for part in path.split('.'):
            m = getattr(m, part, None)
            if m is None:
                break
        if isinstance(m, nn.Module):
            return path, m
    return None, None


_tokenizer = None   # the live tokenizer, bound to model.tok once the model is built


class ByteTokenizer:
    """Raw bytes: the vocabulary is the 256 byte values and START/END/NULL are the
    0x02/0x03/0x00 control bytes, so a clip is literally [START] utf-8 bytes [END]."""
    is_char    = True
    vocab_size = 256
    start_id, end_id, null_id = START, END, NULL

    def encode(self, text): return list(text.encode('utf-8', errors='replace'))
    def decode(self, ids):  return bytes(ids).decode('utf-8', errors='replace')


class HFTokenizer:
    """A pretrained BPE tokenizer from the hub. GPT-Neo has no separate BOS token --
    bos_token_id and eos_token_id are both <|endoftext|> (50256) -- so START and END are
    the same id here and a clip is [EOT] tokens [EOT], the framing the TinyStories models
    were trained with. There is no NULL equivalent (id 0 is an ordinary token), so
    null_id is None and nothing is ever filtered out of the output."""
    is_char = False
    null_id = None

    def __init__(self, repo, vocab_size):
        from transformers import AutoTokenizer
        self.tok        = AutoTokenizer.from_pretrained(repo)
        # A recurrent model has no context window, and we never truncate; without this the
        # tokenizer warns about every document longer than the source model's 2048 tokens.
        self.tok.model_max_length = int(1e12)
        eot             = self.tok.eos_token_id
        self.end_id     = eot if eot is not None else self.tok.bos_token_id
        bos             = self.tok.bos_token_id
        self.start_id   = bos if bos is not None else self.end_id
        # the model's embedding rows, not len(tokenizer): the logits are that wide
        self.vocab_size = vocab_size

    def encode(self, text): return self.tok.encode(text)
    def decode(self, ids):  return self.tok.decode(ids)


def _decode_plain(ids):
    """Token ids -> plain text, framing markers dropped. What _render() shows is for a
    human (escaped whitespace, <STX>/<ETX> markers); a reference LM must see the text the
    model actually generated, so this decodes and drops the markers instead."""
    body = [t for t in ids if t not in (_tokenizer.start_id, _tokenizer.end_id)]
    if not body:
        return ''
    if _tokenizer.is_char:
        return bytes(body).decode('utf-8', errors='replace')
    return _tokenizer.decode(body)


def _render(ids):
    """Render a token-id sequence for display. Byte mode decodes UTF-8 and hands the
    string to _printable(); BPE mode decodes runs of ordinary tokens the same way and
    renders the document marker itself. Since START and END are one id in BPE mode, the
    marker shows as <STX> when it opens the sequence and <ETX> anywhere after -- which is
    exactly the role it plays in the [START] text [END] framing. A marker with more
    tokens after it is a document boundary -- generate() resets the state and re-feeds
    the prompt there, and a corpus stream starts its next document there -- so it renders
    as <ETX><STX>: without the <STX> the text after it reads as a continuation."""
    if _tokenizer.is_char:
        return _printable(bytes(ids).decode('utf-8', errors='replace'))
    out, run = [], []
    for n, t in enumerate(ids):
        if t in (_tokenizer.start_id, _tokenizer.end_id):
            if run:
                out.append(_printable(_tokenizer.decode(run)))
                run = []
            if n == 0:
                out.append(STX_TEXT)
            else:
                out.append(ETX_TEXT + STX_TEXT if n < len(ids) - 1 else ETX_TEXT)
        else:
            run.append(t)
    if run:
        out.append(_printable(_tokenizer.decode(run)))
    return ''.join(out)


# ── DFF write clock (--clock) ─────────────────────────────────────────────────
# How often each recurrent layer commits its new state; see DFFClock for the mechanism.
# These modes take no numeric arguments -- the rates below are the whole parameterization.

_QPROJ_MODES = ('none', 'read')   # where the 1x1 state projection sits (--qproj)
# 'write' (a frozen random orthogonal 1x1 between the layer output and the register) was
# removed: its only path to the loss is through the DFF, which forward() detaches every step,
# so it could never receive gradient and was permanently random. It answered a narrow question
# about signed-vs-rectified state and cost a live option to keep around.

# The DFF write rule. There is only one: every register is written every step, blended by
# --ema / --ema_ladder. The clock that used to gate writes per layer (sync/fixed/incr/
# dither/exp, with --accumulate to average a hold) is gone -- an EMA every step spans the
# same timescales continuously, and the ladders it needed are now expressed directly as
# per-register blend rates.

# ── args ──────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# architecture
parser.add_argument('--context',       default=7,     type=int,
                    help='spatial size S of the DFF grid (S×S)')
parser.add_argument('--n_hidden',      default=512,   type=int,
                    help='DFF state channel depth: the state carried between steps is '
                         '[n_hidden, context, context], and every module that touches it '
                         '(text_proj, deep_proj, linout, qproj, tap, decoder) is sized by '
                         'it. ContextCNN\'s INTERIOR width is --c_context, which defaults '
                         'to this')
parser.add_argument('--c_context',     default=None,  type=int,
                    help='ContextCNN INTERIOR conv width, independent of --n_hidden '
                         '(default: n_hidden, which is the historical behavior and builds '
                         'a byte-identical state_dict). The module\'s contract is fixed by '
                         'the DFF it updates -- [n_hidden, S, S] in, the same out -- so '
                         'only the interior is free: conv 1 widens n_hidden -> c_context, '
                         'convs 2..depth-1 run c_context -> c_context, and the last conv '
                         'narrows back to n_hidden. This decouples the two things '
                         'n_hidden used to set at once: how much state is CARRIED between '
                         'tokens, and how much width is spent COMPUTING the update. Cost '
                         'is quadratic in the interior: a depth-D layer is '
                         '(D-2)*c_context^2 + 2*n_hidden*c_context weights per kernel tap '
                         'against D*n_hidden^2 before, so c_context < n_hidden is the '
                         'cheaper-update knob and c_context > n_hidden the wider-update '
                         'one, neither of which changes the state size or the DFF shapes. '
                         'At --depth 1 there is no interior -- the single conv must be '
                         'n_hidden -> n_hidden -- and this is ignored with a warning.\n'
                         'WITH --linout the last conv does NOT widen: the chain stays at '
                         'c_context throughout and linout projects c_context -> n_hidden, so '
                         'the cost is (depth-1)*c_context^2 + n_hidden*c_context per layer '
                         'and the final ReLU is at c_context. Without --linout nothing '
                         'downstream can widen, so the last conv is c_context -> n_hidden '
                         'and the ReLU is at n_hidden.')
parser.add_argument('--c_text',        default=1,     type=int,
                    help='token embedding channels (None → n_hidden). Ignored by every '
                         'pretrained --tokenizer, which takes it from that model\'s '
                         'embedding width (tiny1m 64, tiny8m/pythia31m 256, pythia14m 128, '
                         'pythia70m 512, pythia160m 768)')
parser.add_argument('--tokenizer',     default='char', choices=sorted(_TOKENIZERS),
                    help='vocabulary and token embedding/readout: "char" is the raw 256-byte '
                         'default (learned embedding, decoder straight to 256 logits). Every '
                         'other value borrows a pretrained BPE tokenizer, token embedding '
                         'and lm_head, and adapts the CNN to them with the linear '
                         '1x1 conv2d already in text_proj (embedding width → n_hidden) and in '
                         'the decoder (n_hidden → embedding width, then lm_head → '
                         'logits). "tiny1m"/"tiny8m" take roneneldan/TinyStories-1M / -8M '
                         '(50257-token vocabulary, but trained on simple English: ~41%% of '
                         'tiny8m embedding rows are still at their random init, so prefer '
                         'these only with --dataset tiny). "pythia14m".."pythia160m" take the '
                         'Pile-trained EleutherAI/pythia-* (50304-token vocabulary, no '
                         'untrained rows -- the ones to use with --dataset web|c4|dolma3). '
                         'The pretrained weights are frozen unless --unfreeze')
parser.add_argument('--head_norm',     default='none',
                    choices=('none', 'ln_f', 'layer', 'rms', 'batch', 'batch2d'),
                    help='normalize the decoder output before the borrowed lm_head. That '
                         'head was trained downstream of a final norm, so it only ever saw '
                         'unit-scale input, while decoder.proj emits whatever scale it '
                         'likes. Ignored with --tokenizer char (there is no borrowed head). '
                         '"none" (default) feeds lm_head directly. "ln_f" reuses the source '
                         'model\'s own final norm, frozen with the rest of the borrowed '
                         'weights (--unfreeze trains it). The rest are fresh and trained '
                         'with the CNN: "layer" LayerNorm and "rms" RMSNorm normalize each '
                         'token\'s readout vector across c_text (the axis a transformer '
                         'normalizes); "batch" BatchNorm1d and "batch2d" BatchNorm2d '
                         'normalize per channel across the batch instead, which fixes the '
                         'average scale but not each vector. batch2d sits inside the decoder '
                         'between proj and the pool, matching the Conv->BatchNorm2d idiom in '
                         'ContextCNN, and folds into the conv at inference')
parser.add_argument('--unfreeze',      default=False, action='store_true',
                    help='train the borrowed token embedding and lm_head too '
                         '(any --tokenizer but char); by default they are frozen and only '
                         'the CNN and its two adapters are trained. Note the scale: the two '
                         'pythia70m matrices are 51.5M params against an ~8M CNN')
parser.add_argument('--depth',         default=7,     type=int,
                    help='ContextCNN conv layer count')
parser.add_argument('--n_layers',      default=3,     type=int,
                    help='stack N (ContextCNN + feedback) recurrent layers in series between '
                         'the thin encoder and decoder; each layer keeps its own DFF state. '
                         '1 = original single-layer behavior')
parser.add_argument('--clock',       default=None,
                             help='DEPRECATED, ACCEPTED AND IGNORED. The DFF write clock is gone: every\n'
                                  'register is written every step and the timescale is the --ema/\n'
                                  '--ema_ladder blend rate, which spans the same spans continuously.\n'
                                  'Kept parseable so the command lines in ./doit still run.')
parser.add_argument('--bn_track',      default=True, action=argparse.BooleanOptionalAction,
                    help='--norm batch: track_running_stats.  Default on, the historical '
                         'behavior.  --no-bn_track makes BatchNorm use BATCH statistics in '
                         'EVAL as well as train, which removes the train/eval discrepancy -- '
                         'the source of every train/held-out blowup in this model -- and drops '
                         'the running-statistics buffers, while KEEPING the cross-batch '
                         'pooling over 250 document streams that per-sample normalizers '
                         '(group, softmax, std) all failed without.  Caveat: inference '
                         'statistics then come from whatever batch is fed, and at batch 1 '
                         'BatchNorm2d degenerates to InstanceNorm over the SxS grid')
parser.add_argument('--bn_affine',     default=False, action=argparse.BooleanOptionalAction,
                    help='--norm batch: learnable per-channel scale and shift.  Default off, '
                         'the historical behavior.  On costs 2*n_hidden per layer (~26K over '
                         '51 layers, 0.09%% of the model) and lets the network partly undo '
                         'normalization where it hurts -- the same BatchNorm sits on 51 '
                         'layers with very different roles')
parser.add_argument('--bn_momentum',   default=0.1,   type=float, metavar='M',
                    help='--norm batch: running-statistics update rate, running = '
                         '(1-M)*running + M*batch.  Default 0.1 is a ~10-step window, which '
                         'is why the running statistics lag the weights and why eval-mode '
                         'behavior can diverge from train.  0.01 gives ~100 steps; 0 selects '
                         'a cumulative average over every batch seen (torch momentum=None)')
parser.add_argument('--bn_eps',        default=1e-5,  type=float, metavar='E',
                    help='--norm batch: epsilon in 1/sqrt(var+E).  A larger value damps the '
                         'normalization of low-variance channels, so a near-dead channel is '
                         'not amplified back up')
parser.add_argument('--dff_norm',      default='none', choices=['none', 'softmax', 'std'],
                    help='condition the DFF state ON THE WAY OUT of the register, on the '
                         'feedback path only.  The register itself keeps the raw ReLU output '
                         '(sparse, ~50%% exact zeros -- what a hardware state memory wants); '
                         'only what is fed back into the layer is transformed, and because '
                         'that transform is scale-free the recurrence is bounded however '
                         'large the stored state grows.  "softmax" applies '
                         'Softmax2d over the channel dimension to the value each layer '
                         'commits to its register, so at every one of the SxS positions the '
                         'n_hidden channel values form a probability distribution: unit mass '
                         'per position, every value in (0,1), strictly positive.  The state '
                         'therefore cannot explode, cannot collapse to zero, and cannot have '
                         'dead units, by construction rather than by tuning -- which is what '
                         'the recurrence needs, since the DFF is detached every step and is '
                         'an input the model must be robust to rather than a path the '
                         'optimizer can shape. '
                         'Only the STORED state is transformed; the value travelling up the '
                         'stack and into the decoder is untouched, so the feed-forward path '
                         'is unchanged and only the feedback loop is bounded. '
                         'Stateless and per-sample, so train and eval compute the same '
                         'function.  Adds no parameters, so it can be toggled on an existing '
                         'checkpoint.  Intended with --norm none, which leaves ContextCNN as '
                         'plain conv2d + ReLU. '
                         '"std" standardizes instead: subtract the state\'s own mean and '
                         'divide by its standard deviation, per sample and per layer, over '
                         'all of (channels, S, S).  Unlike softmax it keeps a SIGN and a full '
                         'dynamic range -- the state is zero-mean unit-variance rather than a '
                         'distribution on the simplex -- so roughly half the values are '
                         'negative and no channel is forced positive.  Same guarantees that '
                         'matter: the state cannot explode or collapse, train and eval agree, '
                         'no parameters, no buffers')
parser.add_argument('--norm_groups',   default=32,    type=int, metavar='G',
                    help='--norm group: channel groups. G=1 is LayerNorm over the whole '
                         'channel dimension, G=n_hidden is InstanceNorm. Clamped to '
                         '[1, n_hidden]. No parameters either way (affine=False)')
parser.add_argument('--norm',          default='batch', choices=['batch', 'none', 'group'],
                    help='normalization inside ContextCNN. "batch" (default) is '
                         'Conv->BatchNorm2d(affine=False)->ReLU, the historical model. '
                         '"none" removes it entirely, leaving Conv->ReLU, and switches the '
                         'convs to He initialization (kaiming_normal, fan_in, relu gain) '
                         'because nothing downstream rescales any more -- PyTorch\'s default '
                         'conv init has a gain far below 1 for ReLU and would shrink the '
                         'signal ~3x per layer, which over 51 layers reaches the readout as '
                         'nothing. '
                         'Why it matters beyond simplicity: BatchNorm is the only module here '
                         'whose function differs between train and eval, and the recurrence '
                         'amplifies that difference -- it is the mechanism behind every '
                         'train/held-out blowup seen in this model, and behind free-running '
                         'generation locking up while training metrics stay clean. --norm '
                         'none computes the same function in both modes by construction. '
                         'It also drops the running-statistics buffers, which are real state '
                         'in an FPGA implementation. '
                         'Changes the state_dict (BatchNorm buffers disappear), so unlike '
                         '--clock it cannot be toggled on an existing checkpoint')
parser.add_argument('--tap_norm',      default='none', choices=['none', 'batch', 'group'],
                    help='normalize the output of each --tap 1x1 conv, i.e. the value that '
                         'feeds the DFF register. The feedback path is the one place in the '
                         'model with no normalization: ContextCNN is Conv->BatchNorm->ReLU '
                         'throughout, but tap, deep_proj and decoder.proj are bare 1x1 convs, '
                         'so the recurrence gain is unconstrained and can drift above 1 as '
                         'training proceeds -- which is what makes the state grow '
                         'geometrically at inference and lock generation into a repeating '
                         'token. Bounding the state itself (--clip_dff) does not fix that, '
                         'because the drift is in the weights, not the state. '
                         '"batch" is BatchNorm2d(affine=False), matching ContextCNN\'s idiom, '
                         'but it carries running statistics and so behaves differently in '
                         'train and eval -- and the train/eval gap compounding through the '
                         'recurrence is itself a suspect for the runaway, so this adds to the '
                         'very mechanism it is meant to fix. '
                         '"group" is GroupNorm(32, affine=False): identical in train and eval '
                         'because it normalizes per sample over channel groups with no '
                         'running statistics, which bounds the feedback gain AND removes the '
                         'train/eval mismatch on that path. It adds no parameters and no '
                         'state_dict entries, so unlike "batch" it can be toggled on an '
                         'existing checkpoint. Requires --tap')
parser.add_argument('--dff_penalty',   default=0.0,   type=float, metavar='W',
                    help='add W * relu(mean of the DFF state) to the training loss, so a '
                         'POSITIVE mean state is penalized and a negative one is free '
                         '(0 = off).\n'
                         'What it is for: the state\'s scale inflates monotonically for a '
                         'whole run -- the logged dff_std climbs 0.7 -> 1.65 over 3.6M steps '
                         'and never settles -- and the mean rides with it, because the '
                         'register accumulates the ReLU outputs of the stack, which are '
                         'non-negative before the linear projection. relu() and not abs() '
                         'because only the positive direction is the runaway one: pushing '
                         'the mean below zero is not an improvement worth paying gradient '
                         'for, and abs() would make 0 an attractor the state has no reason '
                         'to sit at.\n'
                         'Applied to the PRE-DETACH layer outputs, i.e. the tensors that are '
                         'about to become the register, so the gradient reaches the '
                         'projector that produced them. Penalizing self.dff instead would be '
                         'a no-op: it is detached (gradient horizon = 1 token) and carries '
                         'no graph. Complements --clip_dff, which bounds the state after the '
                         'fact without any gradient signal to avoid the bound.')
parser.add_argument('--dff_bias',      default=0.0,   type=float, metavar='W',
                    help='add W * (mean of the DFF state) to the training loss -- the '
                         'TWO-SIDED form of --dff_penalty: a positive mean costs and a '
                         'negative one is rewarded, without limit (0 = off).\n'
                         'Where it differs: --dff_penalty relu()s the mean, so it is a '
                         'restoring force that goes silent once the mean is negative and '
                         'therefore contributes nothing in steady state (measured: W=10 parks '
                         'the mean at -0.0022 and the loss stays pure cross-entropy). This one '
                         'never goes silent -- it is a constant downward pull on the mean, and '
                         'the loss it reports is CE + W*mean, which is BELOW the true CE '
                         'whenever the mean is negative. Read the loss column accordingly: '
                         'with --dff_bias the logged loss is the objective, not the '
                         'cross-entropy, and is not comparable with a run trained without it.\n'
                         'The pull is bounded only by whatever the CE term is willing to pay, '
                         'so a large W can drive the state arbitrarily negative; the DFF '
                         'columns (dff_mean, dff_std) are what say whether the state is still '
                         'carrying information or has simply been pushed down.\n'
                         'Applied to the PRE-DETACH layer outputs, like --dff_penalty, so the '
                         'gradient reaches the projector. May be combined with it, though the '
                         'combination is two forces on the same quantity.')
parser.add_argument('--clip_dff',      default=0.0,   type=float, metavar='MAX',
                    help='bound the magnitude of the DFF state after every write (0 = off). '
                         'Rescales rather than clamping element-wise -- if a layer\'s state '
                         'for a row exceeds MAX in absolute value, the whole tensor is scaled '
                         'down so its max is MAX -- so the spatial and channel pattern of the '
                         'state is preserved and only its scale is bounded, the same '
                         'reasoning as gradient-norm clipping. Applied per layer and per '
                         'batch row, since rows are independent. '
                         'What it is for: the recurrence can run with gain > 1 in FREE-RUNNING '
                         'mode, where the model eats its own output -- the state then grows '
                         'geometrically (measured at ~10x per 5 tokens) until it saturates '
                         'the readout and generation locks into a repeating token. Teacher-'
                         'forced loss never sees this, because ground truth is injected every '
                         'step and holds the state bounded, so a checkpoint can score well '
                         'and still be unusable as a generator. A healthy run here sits at '
                         'dff_max ~10-40 during generation, so MAX of a few hundred bounds '
                         'the blow-up without touching normal dynamics. Applies in training, '
                         '--generate, --eval and --vis alike; adds no parameters, so it can '
                         'be toggled on an existing checkpoint')
parser.add_argument('--clock_ends',  default=None,
                                  help='DEPRECATED, ACCEPTED AND IGNORED. The DFF write clock is gone: every\n'
                                       'register is written every step and the timescale is the --ema/\n'
                                       '--ema_ladder blend rate, which spans the same spans continuously.\n'
                                       'Kept parseable so the command lines in ./doit still run.')
parser.add_argument('--clock_max',   default=None,
                                 help='DEPRECATED, ACCEPTED AND IGNORED. The DFF write clock is gone: every\n'
                                      'register is written every step and the timescale is the --ema/\n'
                                      '--ema_ladder blend rate, which spans the same spans continuously.\n'
                                      'Kept parseable so the command lines in ./doit still run.')
parser.add_argument('--clock_base',  default=None,
                                  help='DEPRECATED, ACCEPTED AND IGNORED. The DFF write clock is gone: every\n'
                                       'register is written every step and the timescale is the --ema/\n'
                                       '--ema_ladder blend rate, which spans the same spans continuously.\n'
                                       'Kept parseable so the command lines in ./doit still run.')
parser.add_argument('--accumulate',    default=False,
                    action=argparse.BooleanOptionalAction,
                    help='DEPRECATED, ACCEPTED AND IGNORED. It averaged the outputs a layer '
                         'computed while HOLDING its register, and nothing holds any more: '
                         'the DFF write clock is gone and every register is written every '
                         'step. Kept parseable so the command lines in ./doit still run.')
parser.add_argument('--ema_ladder',    default=None,  type=str, nargs='?', const='13.15',
                    metavar='SPEC',
                    help='put the TIMESCALE LADDER IN THE EMA INSTEAD OF THE CLOCK. Every layer '
                         'writes its register EVERY STEP (all clock periods forced to 1), and '
                         'depth is expressed by the blend rate instead: layer li gets '
                         'ema = 1/BASE**li, so layer 1 replaces outright (ema 1.0) and each '
                         'deeper layer folds in a proportionally smaller share of its new '
                         'output.\n'
                         'The effective memory window is ~1/ema tokens, so BASE reproduces the '
                         'clock ladder\'s spans: --ema_ladder 13.15 gives windows of 1, 13 and '
                         '173 tokens, the same as --clock fixed --clock_base 13.15 -- but the '
                         'deep register now moves a little every step rather than jumping once '
                         'every 173. Same timescales, continuous instead of piecewise.\n'
                         'Overrides --ema, and disables --accumulate, which has nothing to '
                         'average when no layer ever holds.\n'
                         'TWO FORMS. A single number is a BASE and the windows are 1, B, B**2 '
                         '-- which pins layer 1 at a 1-token window for EVERY base, i.e. '
                         'replace-outright, so no base can slow the top layer down. A '
                         'COMMA-SEPARATED LIST is per-layer WINDOWS IN TOKENS and sets each '
                         'layer independently: --ema_ladder 3.2,10,32 gives ema 0.3162, 0.1, '
                         '0.03162. Size these against the data -- the vocab stream averages 11 '
                         'tokens per sentence, so a 173-token window averages ~15 unrelated '
                         'sentences while a 32-token one spans about three.')
parser.add_argument('--ema',           default=None,  type=float, nargs='?', const=0.5,
                    metavar='DECAY',
                    help='hold a moving average in each layer\'s DFF register: a write blends '
                         'into what is already there, register = register + DECAY*(new - '
                         'register), instead of replacing it. Bare --ema uses 0.5; a value '
                         'must be in (0,1), and 1 would be the default replace-outright '
                         'behavior. Costs nothing to store -- the update is in place -- which '
                         'is what makes it the cheap moving average next to --accumulate, and '
                         'the two compose: --accumulate decides what value a write proposes '
                         '(the mean over the hold rather than that step\'s output), --ema '
                         'decides how it is committed. What it gives up is exactness -- an '
                         'exponential window instead of a box mean, and blind to the steps '
                         'where the layer did not write. The effective window is ~1/DECAY '
                         'writes, so ~period/DECAY tokens under a --clock ladder, which makes '
                         'it a second way to stretch the state\'s timescale without freezing '
                         'it. Applies under every --clock mode including sync, where it turns '
                         'each layer into a leaky integrator updated every step. A row\'s '
                         'first write after a document boundary replaces rather than blends, '
                         'so no --init seed is left in the state. No parameters, so it can be '
                         'toggled on an existing checkpoint')
parser.add_argument('--qproj',         default='none', choices=_QPROJ_MODES,
                    help='put a pointwise 1x1 linear conv2d on each layer\'s DFF path, one '
                         'per layer at --n_hidden: width^2 + width parameters per layer, '
                         '65.8K per layer at --n_hidden 256. The value travelling up the '
                         'stack and into the decoder is never projected, so the feed-forward '
                         'path is unchanged. '
                         '"read" projects on the way out of the register, between the state '
                         'and the feedback add: the register keeps the sparse ReLU output '
                         '(~50%% exact zeros) and what the layer adds back is a dense signed '
                         'recombination of it. Trainable, and initialized to the identity, so '
                         'at step 0 the model is exactly --qproj none. '
                         'Why it is not redundant with the convs already there: it is applied '
                         'to the state but not to the token injection it is summed with, so a '
                         'layer can transform what it remembers differently from what it is '
                         'being told. Adds parameters, so unlike --clock it cannot be toggled '
                         'on an existing checkpoint')
parser.add_argument('--linout',        default=False, action='store_true',
                    help='ONE pointwise 1x1 linear conv2d at the end of EACH layer, whose '
                         'output is both what the DFF register stores and what the next layer '
                         'receives. The DFF therefore holds a DENSE SIGNED tensor instead of '
                         'the sparse non-negative ReLU output (~50%% exact zeros), which is '
                         'the point: --accumulate averages the register and the next step adds '
                         'it back, so a non-negative register can only ever accumulate, never '
                         'cancel.\n'
                         'This is NOT --tap. --tap ADDS a 1x1 in front of the 1x1 already on '
                         'the upward path (deep_proj), leaving two in series with no '
                         'nonlinearity between them -- which compose to one, so the second is '
                         'redundant weight. --linout REPLACES deep_proj rather than preceding '
                         'it: n_layers convs total instead of --tap\'s 2*n_layers-1, and the '
                         'projection that makes the register dense is the same one that feeds '
                         'the layer above. Mutually exclusive with --tap.\n'
                         'Identity-initialized, so the register starts holding exactly the '
                         'ReLU output and becomes signed as the weights move -- within a few '
                         'steps in practice. Note step 0 is NOT identical to the baseline, '
                         'unlike --tap: dropping deep_proj changes the upward path even at '
                         'identity.\n'
                         'WITH --c_context THIS 1x1 IS ALSO THE WIDENING. ContextCNN then '
                         'runs at c_context end to end -- final BN and ReLU included -- and '
                         'this conv projects c_context -> n_hidden, replacing a 3x3 that '
                         'would have cost 9x its weights to do the same job. The nonlinearity '
                         'therefore sits at the INTERIOR width and the only thing that widens '
                         'to the register is linear, which is the intended shape. Init is '
                         'semi-orthogonal rather than identity in that case (an identity '
                         'needs a square matrix): norm-preserving, and dense/signed from step '
                         '0 instead of leaving n_hidden-c_context channels at zero.')
parser.add_argument('--dff_every',     default=1,     type=int, metavar='K',
                    help='DEPRECATED, ACCEPTED AND IGNORED. K=2 used to leave every other '
                         'layer straight through -- no register, no feedback add. EVERY '
                         'LAYER NOW HAS A DFF AND A FEEDBACK ADD. The measurement that '
                         'settled it: at identical parameter count, identical conv depth and '
                         'identical data, removing one of two registers cost 0.503 nats '
                         '(6.7188 -> 7.2219) and landed WORSE than two replace-outright '
                         'registers -- the recurrent state is what the model runs on, so a '
                         'layer without one is not worth its convs. Kept parseable so the '
                         'command lines in ./doit still run.')
parser.add_argument('--linout_kernel', default=1,     type=int, metavar='K',
                    help='kernel size of the --linout conv2d (odd; default 1 = pointwise). '
                         'K=3 makes it a 3x3 with zero padding K//2, so the S x S grid comes '
                         'out the size it went in and nothing else in the model changes '
                         'shape. What DOES change is reach: at 1x1 the projection mixes '
                         'channels at a single position and every spatial interaction in the '
                         'layer comes from ContextCNN\'s own convs, so the tensor written to '
                         'the DFF register is a per-position recombination of that layer\'s '
                         'output. At 3x3 the write itself is spatial -- each position of the '
                         'register sees a 3x3 neighbourhood of the layer output -- which adds '
                         'one more hop of receptive field per step to the recurrence, on the '
                         'path the state actually travels. Costs 9x the linout weights '
                         '(n_hidden * c_context * 9), which is small next to the conv stack '
                         'but not next to a 1x1: at n_hidden 4096, c_context 256 it is 9.4M '
                         'against 1.0M. Identity init still holds -- dirac_ puts the identity '
                         'on the CENTRE tap and zeros the rest, so K=3 starts as exactly K=1 '
                         'and grows its neighbourhood as the off-centre taps move.')
parser.add_argument('--tap',           default=False, action='store_true',
                    help='put two pointwise 1x1 linear conv2d projections in series after '
                         'each layer\'s last conv2d-BN-ReLU -- the tensor that normally feeds '
                         'the DFF -- and tap the DFF from between them. This flag adds the '
                         'first of the two; the second is the 1x1 already on the upward path '
                         '(deep_proj into the next layer, decoder.proj on the last layer), so '
                         'the series is  output -> tap -> [register] -> deep_proj -> next '
                         'layer. A separate second module would be exactly redundant: two '
                         '1x1s in series with no nonlinearity between compose to one, so '
                         'folding it into deep_proj costs nothing representable and halves '
                         'the parameters. The register therefore holds a dense signed '
                         'embedding instead of the sparse ReLU output (~50%% exact zeros). '
                         'The tap trains, unlike --qproj write in the same position: the '
                         'register it feeds is detached, but the upward path through it is '
                         'not. Identity-initialized, so step 0 is exactly the model without '
                         '--tap. One conv per layer at --n_hidden: width^2 + width per layer, '
                         '65.8K per layer at --n_hidden 256. Since the register goes dense, '
                         '--init gaussian suits it better than the default relu, and '
                         'dff_zeros will read ~0. Adds parameters, so it cannot be toggled on '
                         'an existing checkpoint')
parser.add_argument('--kernel',        default=3,     type=int,
                    help='conv kernel size (odd integer)')
# training
parser.add_argument('--dataset',       default='tiny',
                    help='tiny | c4 | web | brt | dolma3 | s1k | pile | pile_nc | wdef | '
                         'bdict (local file, --bdict_file). s1k is only '
                         '1000 reasoning examples -- meant for --mix, it loops quickly on '
                         'its own. pile is EleutherAI\'s deduplicated Pile re-release '
                         '(EleutherAI/pile itself was emptied by a DMCA takedown and cannot '
                         'be loaded); pile_nc is the same corpus with the copyrighted '
                         'subsets removed. Both are large -- use --streaming, or --shards N '
                         'to pull only the first N shards')
parser.add_argument('--mix',           default=None,
                    help='joint multi-dataset training, "name:weight,..." e.g. '
                         '"brt:0.5,web:0.5"; overrides --dataset, samples one dataset per clip '
                         '(token-proportional)')
parser.add_argument('--mix_slots',     default=False, action='store_true',
                    help='read the --mix weights as SLOT fractions instead of sampling '
                         'weights: each dataset gets its own round(w * --batch) slots and its '
                         'own clip queue, fed by builder threads pinned to that dataset. '
                         'Every slot contributes one token per step, so this is an EXACT '
                         'token split -- "fwcrawl:0.5,tinytb:0.5 --batch 250" is 125 slots '
                         'each, every step -- where plain --mix only holds on average and '
                         'only after its running mean of clip lengths has settled. Same '
                         'batchwise idea as --vocab_slots, for hub corpora.')
parser.add_argument('--unframed',      default=None,
                    help='comma-separated --dataset/--mix corpora whose documents are NOT '
                         'wrapped in <STX>/<ETX>: on those slots the raw tokens of one '
                         'document are followed directly by the first token of the next, the '
                         'slot never signals a document start, and the recurrent state is '
                         'never reset -- the same contract as an unframed --vocab_files pool, '
                         'applied to a streaming corpus. Because a slot is either resetting '
                         'or not, an unframed corpus needs slots of its own: with --mix this '
                         'requires --mix_slots. Held-out eval (--eval_corpora) still scores '
                         'that corpus FRAMED, one document at a time from a reset state, so '
                         'its EVAL line measures the same thing as a framed run\'s.')
parser.add_argument('--shuffle',       default=None,
                    action=argparse.BooleanOptionalAction,
                    help='shuffle the corpus, or read it in FILE ORDER. Unset (the default) '
                         'is per-dataset: on for every hub corpus, which is what every run '
                         'before this flag did, and OFF for --dataset file, whose whole '
                         'purpose is a fixed sequence. --shuffle forces it on even for a '
                         'file, --no-shuffle forces it off even for a hub corpus.\n'
                         'What "on" means depends on the load: a buffer when streaming, a '
                         'true permutation for a corpus small enough to fit page cache, a '
                         'sharded buffer otherwise (see _make_iter). None of those is '
                         'reproducible across runs -- the builder threads race for the '
                         'iterator -- so --no-shuffle is what makes two runs see the same '
                         'documents in the same order, and the only way to tell a 0.04-nat '
                         'config difference from a different draw.')
parser.add_argument('--subsample',     default=0,     type=int, metavar='N',
                    help='train on a FIXED sample of N examples per corpus instead of the '
                         'whole stream. The sample is drawn once at startup -- the first N '
                         'usable examples the (shuffled) corpus iterator yields, after the '
                         'per-corpus filter and the held-out hash split, so every one of '
                         'them is a document the model will actually see -- and is then '
                         'treated as the corpus: one pass over it is one epoch, and each '
                         'epoch is an independent reshuffle of the same N documents '
                         '(random.Random(--seed + epoch)). Under --mix every corpus gets '
                         'its own N-example sample. The epoch column and the EPOCH lines '
                         'behave as for any finite corpus, so this is the tool for '
                         'measuring how many passes a closed set of documents takes to '
                         'memorize: 10000 fineweb docs is ~1 step per document at batch '
                         '250, so --subsample 10000 cycles the same text every few hundred '
                         'steps. 0 (default) = off, stream the corpus as before.')
parser.add_argument('--refresh',       default=0.0,   type=float, metavar='FRAC',
                    help='--subsample turnover driven by a LEARNING-STALL DETECTOR instead of '
                         'the fixed --epochs schedule: when the model has stopped learning '
                         'from the current pool, replace FRAC of it (the oldest documents) '
                         'with fresh ones, which should restart learning, and repeat. '
                         '0 (default) = off. Mutually exclusive with --epochs.\n'
                         'THE DETECTOR is arXiv:2403.02473 ("When do Convolutional Neural '
                         'Networks Stop Learning?"), which stops training when the data '
                         'variation across ALL layers goes still; here the same signal '
                         'triggers a data refresh rather than a stop. Per conv layer i and '
                         'epoch e: alpha = std of that layer\'s POST-CONVOLUTION activations, '
                         'sampled every --refresh_sample steps; mu_i^e = mean(alpha) over the '
                         'epoch; delta_i^e = round(mu_i^e, --refresh_r) - round(mu_i^(e-1), '
                         '--refresh_r); the epoch is STILL when sum_i delta_i^e == 0, and the '
                         'refresh fires after --refresh_hold consecutive still epochs.\n'
                         'Post-CONVOLUTION and not post-norm on purpose: BatchNorm/GroupNorm '
                         'with affine=False makes the post-norm std 1 by construction and the '
                         'post-ReLU std a constant of it, so the only layer output that '
                         'carries information about data variation is the conv output itself.')
parser.add_argument('--refresh_r',     default=2,     type=int, metavar='R',
                    help='--refresh: decimal places the per-layer mean is rounded to before '
                         'differencing. The paper\'s r=2 is its one critical hyperparameter -- '
                         'r=1 declares the stall too early, r>=3 never declares it.')
parser.add_argument('--refresh_every', default=0,     type=int, metavar='K',
                    help='--refresh on a FIXED SCHEDULE instead of on the stall detector: '
                         'turn the pool over every K epochs regardless of what the detector '
                         'says. 0 (default) = the detector decides.\n'
                         'The refresh itself is identical -- the same --refresh fraction, the '
                         'oldest first -- so this is the controlled comparison for a '
                         'stall-driven run: same action, same pool, only the timing rule '
                         'differs. It is NOT --epochs, which retires N/E documents EVERY '
                         'epoch so the pool drifts continuously; this swaps a block at once, '
                         'the way a triggered refresh does.\n'
                         'The detector is DISABLED in this mode -- no activation hooks are '
                         'registered and nothing is measured -- because a fixed schedule does '
                         'not consult it, and leaving it on would pay one extra reduction per '
                         'conv layer for a number nothing reads.')
parser.add_argument('--refresh_mode',  default='rel', choices=['rel', 'abs'],
                    help='--refresh: how a stalled epoch is declared.\n'
                         '"abs" is the paper verbatim: still when abs(sum delta) <= '
                         '--refresh_eps, with EPS 0 the paper\'s exact ==0.\n'
                         '"rel" (default) asks whether the drift is STILL FALLING rather '
                         'than whether it has reached a floor: an epoch counts as progress '
                         'only if abs(sum delta) sets a new minimum (by more than '
                         '--refresh_tol, relatively), and --refresh_hold epochs with no new '
                         'minimum declare the stall. It is the default because the absolute '
                         'floor is not a property of the data -- it is set by this model\'s '
                         'permanent activation-scale inflation, so "abs" with EPS 0 never '
                         'fires here and an EPS chosen above the floor degenerates into a '
                         'fixed schedule: measured at --subsample 100, EPS 0.5 fired every '
                         '1+--refresh_hold epochs exactly, i.e. --epochs 4 with extra steps. '
                         'A minimum-tracking test needs no scale constant and so transfers '
                         'across depth, width and step count.')
parser.add_argument('--refresh_tol',   default=0.0,   type=float, metavar='T',
                    help='--refresh_mode rel: relative margin a new minimum must beat, '
                         'best*(1-T). 0 (default) counts any new minimum as progress; raise '
                         'it to ignore noise-sized improvements (T 0.05 = "at least 5%% '
                         'better than the best epoch so far").')
parser.add_argument('--refresh_eps',   default=0.0,   type=float, metavar='EPS',
                    help='--refresh: declare the epoch STILL when abs(sum of per-layer '
                         'deltas) <= EPS, instead of the paper\'s exact == 0. Default 0.0 IS '
                         'the paper.\n'
                         'Why it is needed here and not there: the paper\'s networks are '
                         'feed-forward image classifiers whose activation statistics settle, '
                         'so the rounded per-layer means eventually stop moving. This model is '
                         'RECURRENT and its state scale drifts upward for the whole run '
                         '(measured: the DFF std climbs from 0.7 to 1.65 over 3.6M steps), '
                         'which drags the post-convolution activation std with it, so a few '
                         'layers cross a rounding boundary every epoch and the exact criterion '
                         'may never fire. Measured on --subsample 100: sum_delta decays '
                         '2.43 -> 0.40 over 20 epochs and then flattens near 0.40-0.45 while '
                         'the mean activation std is still climbing. With 32 layers and r=2, '
                         'EPS 0.5 means "no more than ~50 rounding units of total drift", i.e. '
                         'most layers unchanged; EPS 0 means every layer identical twice over.')
parser.add_argument('--refresh_hold',  default=3,     type=int, metavar='K',
                    help='--refresh: consecutive still epochs (sum delta == 0) required before '
                         'the pool is refreshed. The paper uses 3.')
parser.add_argument('--refresh_sample', default=10,   type=int, metavar='N',
                    help='--refresh: sample the per-layer activation std every N training '
                         'steps rather than every step. The epoch mean is over the samples, '
                         'so this trades a little precision for the cost of one extra full '
                         'reduction per conv layer: every step is ~8%% of step time at '
                         'depth 32, N=10 is under 1%%.')
parser.add_argument('--epochs',        default=0,     type=int, metavar='E',
                    help='--subsample turnover: how many epochs each sampled document lives '
                         'before it is retired for a fresh one. 0 (default) = never, the '
                         'sample is closed and every epoch is the same N documents. With E '
                         'set the pool still holds N documents at all times, but after every '
                         'epoch the N/E OLDEST are dropped and N/E fresh ones are drawn from '
                         'the stream (the remainder spread so that exactly N turn over per E '
                         'epochs), so the refresh is gradual rather than a wholesale swap: '
                         'each document is seen E times, the pool composition drifts '
                         'continuously, and at any moment it holds documents at every age '
                         'from 1 to E epochs. E=1 replaces the whole pool every epoch. '
                         'Requires --subsample.')
parser.add_argument('--data_file',     default='data/fineweb2k.jsonl',
                    help='file backing --dataset file: a LOCAL JSONL corpus, one JSON object '
                         'per line with a "text" field. Unlike every hub corpus this one is '
                         'READ IN FILE ORDER AND NEVER SHUFFLED -- not at load, not in a '
                         'buffer, not per epoch -- so two runs see the same documents in the '
                         'same sequence and the data stops being a source of run-to-run '
                         'variance. That is the point: the streaming shuffle is not '
                         'seed-controlled, so on a hub corpus even --seed leaves the batch '
                         'composition thread-scheduling dependent, and a 0.04-nat difference '
                         'between two configs cannot be told from a different draw. JSONL '
                         'rather than plain lines because documents contain newlines; '
                         'data/fineweb2k.jsonl (2000 fineweb docs, 6.3M chars) is the one '
                         'this repo ships. Small enough to wrap many times in a run: the '
                         'epoch column counts passes and they are IDENTICAL passes.')
parser.add_argument('--bdict_file',    default='basic_dict_e3.txt',
                    help='file backing --dataset bdict: a LOCAL plain-text corpus, ONE '
                         'DOCUMENT PER LINE. Unlike every other corpus here it is authored '
                         'rather than downloaded, so it is version-controlled with the code '
                         'and the exact bytes trained on are recoverable from git. Used for '
                         'the basic-vocabulary memorization probe, where the corpus is small '
                         'enough (848 lines) that thousands of epochs fit in a normal run. '
                         'The _eN suffix is SENTENCES PER WORD: basic_dict_e3.txt has 3 '
                         'example sentences per vocabulary word, basic_dict_e10.txt has 10 '
                         'and is a strict superset (same 848 words, same first 3 sentences '
                         'verbatim), so a pair of runs isolates "more text per item" from '
                         'every other variable.')
parser.add_argument('--datarep',       default=1,     type=int, metavar='N',
                    help='feed every token N TIMES IN A ROW, giving the recurrent state N '
                         'steps of computation per input token instead of one (default 1 = '
                         'off, byte-identical to before this flag existed). The replication '
                         'is per slot and covers the framing: <STX> and <ETX> repeat like '
                         'any other token, and the (x, y) pair repeats with them, so every '
                         'replica is trained to predict the SAME next token -- the later '
                         'replicas simply get to use a more settled state to do it.\n'
                         'CADENCES ARE NOT SCALED: --monitor, --gen_interval, '
                         '--eval_interval and --checkpoint are all counts of RAW STEPS at '
                         'any N, so each flag means what it says. Note the consequence when '
                         'comparing runs: a step is 1/N of a token, so an EVAL at step 20000 '
                         'is 20000/N tokens in, and two runs at different N line up on '
                         'step/N rather than on step.\n'
                         'DECODE mirrors training: the prompt is fed N times per token and '
                         'the sample is drawn from the logits of the LAST replica, then that '
                         'sample is itself replicated N times, so one output token appears '
                         'every N steps (--generate, --vis and the periodic GEN samples all '
                         'work this way). Held-out eval replicates too, since it frames '
                         'documents with the same clip_text the trainer uses -- so its '
                         'nats/token stay comparable WITHIN a --datarep setting but not '
                         'across two different ones.\n'
                         'Costs N steps per token: at a fixed step budget the model sees 1/N '
                         'of the data, and at a fixed data budget the run takes N times '
                         'longer.')
parser.add_argument('--gen_pool',      default='last', choices=('last', 'mean'),
                    help='--datarep > 1: which of a token\'s N replica steps the next-token '
                         'distribution is drawn from during DECODE (--generate, --vis, the '
                         'periodic GEN samples). "last" (default) samples from the final '
                         'replica\'s logits -- the state has settled longest there, and it '
                         'is what the training stream\'s last replica is optimized to '
                         'predict. "mean" takes the ARITHMETIC MEAN OF THE PROBABILITIES '
                         'across all N replicas -- softmax each, average, sample from that -- '
                         'so the replicas vote as distributions and one confidently wrong '
                         'replica is outvoted rather than dominating. (An arithmetic mean of '
                         'probabilities, not of logits: a logit mean is a GEOMETRIC mean once '
                         'softmaxed, where a single near-zero probability vetoes a token no '
                         'matter what the others say.) --temperature still applies, to the '
                         'pooled distribution. Every replica is trained against the same '
                         'target, so both readings are of the same quantity -- this chooses '
                         'which one the sampler sees. No effect at --datarep 1, where there '
                         'is one replica and the two are identical.')
parser.add_argument('--vocab_files',   default=None,
                    help='comma-separated local files of ONE SENTENCE PER LINE that feed a '
                         'BATCHWISE stream (see --vocab_slots). These are NOT framed: no '
                         '<STX>/<ETX> is added and the slot never signals a document start, '
                         'so the model state is never reset on those slots -- the sentences '
                         'run head to tail as an unbroken stream. Files are weighted EQUALLY '
                         'by slot, so two files split the vocab slots 50/50 and three split '
                         'them in thirds -- pass a multiple of the file count as '
                         '--vocab_slots to get an exact split. The STEP line\'s epoch column '
                         'is the MEAN number of complete passes over these files.')
parser.add_argument('--vocab_framed',   default=None,
                    help='comma-separated subset of --vocab_files (path or bare stem) whose '
                         'examples ARE framed: each one is wrapped in <STX>...<ETX> and the '
                         'slot signals a document start on its first step, so the recurrent '
                         'state resets between examples exactly as it does on a corpus slot. '
                         'This is the right setting for a pool whose examples are long, '
                         'self-contained documents (reasoning_phase1: ~761 tokens of '
                         'question + <think> + <answer>) rather than short sentences meant '
                         'to run head to tail. Framed pools are EXCLUDED from the epoch '
                         'column\'s mean -- they wrap tens of times more slowly than a '
                         'sentence pool and would dominate nothing while being dominated.')
parser.add_argument('--vocab_slots',   default=0,     type=int,
                    help='how many of the --batch slots the --vocab_files stream occupies. '
                         'The REMAINING slots are filled the normal way from --dataset/--mix, '
                         'with <STX>/<ETX> framing. Because every slot contributes exactly '
                         'one token per step, the slot split IS the token split: '
                         '--batch 250 --vocab_slots 225 is exactly 90%% vocab / 10%% corpus '
                         'tokens, with no dependence on document lengths. That is the point '
                         'of doing this batchwise rather than through --mix, whose '
                         'token-proportional sampling only holds on average.')
parser.add_argument('--bdict_split',   default=False, action='store_true',
                    help='--dataset bdict: drop the leading "word: " key and make EVERY '
                         'SENTENCE its own training example. basic_dict_e10.txt goes from '
                         '848 documents of 10 sentences to 8,480 documents of one sentence. '
                         'This is the PRE-PRETRAINING form: without the key the corpus stops '
                         'being a lookup table to memorize and becomes plain simple English, '
                         'so what transfers downstream is ordinary sentence structure rather '
                         'than "after a colon, recite". Documents get ~10x shorter, so <ETX> '
                         'and the context reset arrive ~10x more often.')
parser.add_argument('--gen_score',     default=None,  nargs='?', metavar='MODEL',
                    const='EleutherAI/pythia-70m',
                    help='score each GEN sample for FLUENCY with a frozen reference LM '
                         '(bare flag: EleutherAI/pythia-70m, 70M params). Prints a GENSCORE '
                         'line beside the sample: nats/token under the reference, plus a '
                         '0-100%% position between two anchors computed ONCE from this run\'s '
                         'own corpus -- FLOOR is real training text, CEILING is the same text '
                         'with its words shuffled. The anchors are what make the number mean '
                         'anything: raw nats/token is uninterpretable without knowing what '
                         'the reference scores on real text of the same kind, and they are '
                         'frozen after the first computation so the series is comparable '
                         'across steps.\n'
                         'READ IT WITH THE REPETITION COLUMN, NEVER ALONE. A reference LM is '
                         'DELIGHTED by degenerate output -- "the the the" scores near-zero '
                         'nats -- which is exactly the failure mode a recurrent model falls '
                         'into (see exp/gencheck.py). GENSCORE therefore also reports rep1, '
                         'the larger of the fraction of the sample made of its most common '
                         'WORD and the fraction of its non-whitespace CHARACTERS made of the '
                         'most common one -- a wall of one punctuation character broken by '
                         'spaces defeats the word rate alone (0.08, while the reference LM '
                         'scores it 98%% fluent) and the character rate catches it (0.75); '
                         'a high fluency score next to a high rep1 is a collapsed model, not '
                         'a fluent one.\n'
                         'Runs on the CPU and only every --gen_interval steps, so it costs '
                         'no GPU memory and no measurable training time. Off by default: a '
                         'run without it is byte-identical to one from before the flag.')
parser.add_argument('--blocks',        default=False, action=argparse.BooleanOptionalAction,
                    help='read the corpus as ONE CONTIGUOUS STREAM PER SLOT instead of a bag '
                         'of documents: each file is cut into --batch byte ranges and slot k '
                         'reads range k of every file, head to tail, in file order.\n'
                         'For a line-oriented corpus this is the difference between a slot '
                         'seeing ~13 tokens of continuity and then jumping somewhere else in '
                         'the corpus, and a slot reading hundreds of thousands of contiguous '
                         'tokens. The ordinary path hands documents out from a shared queue, '
                         'so a slot gets roughly every --batch-th line; on an --unframed slot, '
                         'whose state is never reset, that asks the recurrence to carry '
                         'context across boundaries with nothing behind them.\n'
                         'PER FILE, so the batch moves through the files together and an '
                         'unshuffled curriculum survives; cutting the concatenated corpus '
                         'would put slot 0 in the first file and the last slot in the last, '
                         'with every file present in every batch. One pass over every range '
                         'of every file is one epoch, and the epoch length in steps is '
                         'unchanged: corpus_tokens / batch.\n'
                         'Local text corpora only (--dataset babylm), single dataset, and it '
                         'is inherently ordered -- implies --no-shuffle.')
parser.add_argument('--gen_null',      default=False, action=argparse.BooleanOptionalAction,
                    help='sample from the SEEDED STATE ALONE: the prompt is empty, not even '
                         '<STX>. Applies everywhere a sample is drawn -- the periodic GEN '
                         'lines, --generate and --vis.\n'
                         'Default off, where a prompt of "" still means the single token '
                         '<STX> (see _prompt_ids), so generation always opens at a document '
                         'boundary the way every training clip does. That is the right '
                         'default for a FRAMED corpus and the wrong one for an UNDELIMITED '
                         'stream (--unframed), which never sees <STX> in training: feeding '
                         'one at sample time puts the model in a state it was never trained '
                         'on. With --gen_null the DFF is seeded by --init (gaussian noise, '
                         'say) and the first token is read straight off that state through '
                         'the decoder, with no token injection at all -- which is what the '
                         'recurrence does mid-stream, and the only honest way to sample a '
                         'model trained without document markers.')
parser.add_argument('--gen_prompts',   default=None,
                    help='EXTRA prompts for the periodic GEN sample, comma-separated, e.g. '
                         '"aardvark,telescope,zorbulate". The NULL prompt (bare <STX>, i.e. '
                         'free-running text) is always sampled first and is not affected by '
                         'this flag, so adding prompts never costs the unprompted sample: '
                         'free-running text and a keyed probe answer different questions -- '
                         '"what has this model learned to write" versus "does it know THIS '
                         'entry" -- and on a memorization run both are needed. A confident, '
                         'well-formed definition of a word that does not exist is the '
                         'signature of having learned the FORM and not the CONTENT, which is '
                         'why a deliberate non-word belongs in the list. Prompts cannot '
                         'contain a comma.')
parser.add_argument('--wdef_format',   default='term', choices=('term', 'defs'),
                    help='how --dataset wdef renders one dictionary entry. "term" (default) '
                         'emits the headword then its numbered senses, so the document is a '
                         'term->definition MAPPING and free-running generation can be read '
                         'as dictionary entries -- that is what makes "did it memorize the '
                         'dictionary" a question the samples can answer. "defs" emits the '
                         'definitions column alone, which is 466k unlabelled gloss sentences: '
                         'still a memorization target, but with no headword to key on and no '
                         'way to tell recall from fluent paraphrase.')
parser.add_argument('--streaming',     default=False, action='store_true')
parser.add_argument('--shards',        default=None,  type=int,
                    help='non-streaming: load only the first N parquet shards of the dataset '
                         '(skips most of the slow "Loading dataset shards" step for large '
                         'corpora like web/openwebtext); ignored with --streaming or if the '
                         'repo is not parquet')
parser.add_argument('--batch',         default=100,   type=int)
parser.add_argument('--workers',       default=12,    type=int,
                    help='parallel clip-builder threads (decode/download); raise for cc3m image streaming')
parser.add_argument('--preroll',       default=False,
                    action=argparse.BooleanOptionalAction,
                    help='decorrelate the batch before training: discard batches (no forward, '
                         'no step) until the first <ETX> comes out of the data stream, then '
                         'start training. Every slot loads its first clip on step 0, so on a '
                         'corpus whose examples open alike (TinyStories: "Once upon a time...") '
                         'the whole batch runs near-identical text in lockstep for its first '
                         'few hundred steps. Draining to the first <ETX> ends the shortest clip '
                         'in the batch and leaves every slot at a different point in a '
                         'different story.\n'
                         '--no-preroll turns it off, which is what a LONG-FORM corpus needs: '
                         'the cost is one shortest-clip\'s worth of discarded batches, which '
                         'is a few hundred steps on TinyStories but thousands on sebooks '
                         '(whole books, mean 126k tokens) -- and the correlated-opening '
                         'problem it fixes does not arise there, since 250 slots land on 250 '
                         'different books that share no opening text. It is a negation rather '
                         'than dropping the flag because exp/run.sh bakes --preroll into the '
                         'baseline, so an override has to be expressible on the command line.')
parser.add_argument('--run_steps',     default=None,  type=int,
                    help='stop the run after this many gradient steps (None = run indefinitely); '
                         'handy for fixed-length sweeps')
parser.add_argument('--opt',           default='sgd',
                    choices=['sgd', 'rmsprop', 'rprop', 'adagrad', 'adamw'],
                    help='training optimizer')
parser.add_argument('--momentum',      default=0.0,   type=float,
                    help='momentum (--opt sgd/rmsprop; the fallback for adamw beta2 when '
                         '--beta2 is unset, kept for compatibility with runs and '
                         'checkpoints that predate --beta2; ignored by rprop/adagrad)')
parser.add_argument('--beta1',         default=None,  type=float, metavar='DECAY',
                    help='--opt adamw first-moment (gradient EMA) decay. Default 0.9. The '
                         'averaging window is ~1/(1-beta1) steps, so 0.9 averages ~10 '
                         'gradients and 0.99 ~100; lower it to react faster, raise it to '
                         'ride through a noisy stretch. Ignored, with a warning, by any '
                         'other --opt (--momentum is the knob for sgd/rmsprop)')
parser.add_argument('--beta2',         default=None,  type=float, metavar='DECAY',
                    help='--opt adamw second-moment (squared-gradient EMA) decay, the '
                         'per-parameter step-size normalizer. Torch defaults to 0.999 '
                         '(~1000-step window); this script has historically taken it from '
                         '--momentum, so --beta2 overrides that and --momentum remains the '
                         'fallback when --beta2 is unset. A short window (0.9 = ~10 steps) '
                         'lets one gradient spike rescale every parameter\'s step, which is '
                         'worth knowing on a recurrent model whose state can spike at '
                         'startup. Ignored, with a warning, by any other --opt')
parser.add_argument('--nesterov',      default=False, action='store_true',
                    help='Nesterov momentum for --opt sgd: take the gradient at the point '
                         'the momentum is already carrying the weights to, instead of at '
                         'the current weights. Needs --momentum > 0 (torch also requires '
                         'zero dampening, which is what this script uses); ignored, with a '
                         'warning, for any other --opt or at --momentum 0')
parser.add_argument('--weight_decay',  default=0.0,   type=float,
                    help='L2 weight decay (--opt sgd/rmsprop/adagrad; ignored by rprop)')
parser.add_argument('--clip',          default=0.0,   type=float,
                    help='clip the global gradient norm to this value before the optimizer '
                         'step (0 = off). ContextCNN is a plain Conv->BatchNorm->ReLU chain '
                         'with no residual path, which amplifies the backward signal by ~1.15x '
                         'per layer, so the gradient norm at init grows like 1.15**--depth: '
                         'harmless at depth 8, ~1e2 at 32, ~1e4 at 56. AdamW hides this (its '
                         'step is bounded by the lr however large the gradient is) but SGD '
                         'multiplies it straight into the weights and diverges on step 0. '
                         'Clipping makes the deep configurations trainable with any optimizer. '
                         'The logged grad column still reports the norm BEFORE clipping, and a '
                         '"clipped" column reports the fraction of steps that hit the limit')
# learning rate: all --schedule modes are driven by this one set. lr_max is the peak
# (and the optimizer base lr); lr_min is the floor; lr_warmup / lr_period are step counts.
parser.add_argument('--schedule',      default='const',
                    choices=['const', 'warmup', 'step', 'linear', 'coswarm', 'triangle', 'cosine', 'plat'],
                    help='lr schedule: "const" (fixed --lr_max), "warmup" (ramp '
                         '--lr_min->--lr_max over --lr_warmup steps, then hold; the ramp is '
                         'measured from the start of this run, so it restarts on --load), '
                         '"step" (hold --lr_min for the first --lr_warmup GLOBAL steps, then '
                         'jump to --lr_max: a short fixed low-lr settle instead of a ramp), '
                         '"linear" (ramp '
                         '--lr_min->--lr_max over --lr_period, then hold), "coswarm" (ONE '
                         'half-cosine rise --lr_min->--lr_max over --lr_period GLOBAL steps, '
                         'then hold: the first half of a "cosine" cycle without the descent, '
                         'so the approach to --lr_max is gentle at both ends), "triangle" (ramp '
                         '--lr_min->--lr_max over --lr_warmup, then --lr_max->--lr_min over '
                         '--lr_period), "cosine" (cyclic --lr_min<->--lr_max, --lr_period '
                         'steps/cycle) or "plat" (start at --lr_max; every --checkpoint steps '
                         'fit a line to the loss over the last --lr_period steps and multiply '
                         'the lr by --lr_rate if the slope is non-negative, floor at --lr_min; '
                         'a decay clears the window, so the lr drops at most once per '
                         '--lr_period steps)')
parser.add_argument('--lr_min',        default=1e-6,  type=float,
                    help='minimum / floor learning rate (warmup|step|linear|coswarm|triangle|cosine)')
parser.add_argument('--lr_max',        default=0.001, type=float,
                    help='peak learning rate; also the constant lr for --schedule const '
                         'and the optimizer base lr')
parser.add_argument('--lr_mult',       default=1.0,   type=float,
                    help='per-layer lr multiplier: layer k (1-based) gets base_lr * '
                         '--lr_mult**(k-1), so with --lr_mult 10 --n_layers 3 the three '
                         'layers use lr, 10*lr, 100*lr. Default 1.0 (all layers equal)')
parser.add_argument('--lr_warmup',     default=1000,  type=int,
                    help='ramp-up length in steps (warmup|triangle); hold length for step')
parser.add_argument('--lr_period',     default=10000, type=int,
                    help='schedule length in steps: linear ramp / triangle ramp-down / cosine cycle '
                         '/ plat slope window (steps of loss history the line is fit to, and '
                         'the minimum gap between two plat decays)')
parser.add_argument('--lr_rate',       default=0.5,   type=float,
                    help='--schedule plat decay factor: lr *= --lr_rate when the fitted loss '
                         'slope over the --lr_period window is non-negative')
# I/O
parser.add_argument('--load',          default=None)
parser.add_argument('--save',          default='checkpoint.pt')
parser.add_argument('--checkpoint',    default=1000,  type=int)
parser.add_argument('--teacher',       default='openai-community/gpt2',
                    help='--dataset synth: HuggingFace causal-LM whose samples ARE the '
                         'corpus. Any text-generation repo works (gpt2, gpt2-medium, '
                         'EleutherAI/pythia-160m, ...). Bigger teacher = cleaner text and '
                         'slower generation; see --teacher_batch for the throughput budget')
parser.add_argument('--teacher_batch', default=64,    type=int,
                    help='sequences per generate() call. Generation is autoregressive, so '
                         'wall time is set by the LONGEST sequence in the batch and batching '
                         'is nearly free: measured 2084 tok/s at 16 and 4725 tok/s at 64 on '
                         'a 4090 already running a trainer. VLA consumes 765 tok/s at '
                         '--batch 250, so 64 keeps the teacher well ahead of the trainer')
parser.add_argument('--teacher_temp', default=1.0,   type=float)
parser.add_argument('--teacher_topk',  default=50,    type=int)
parser.add_argument('--teacher_topp',  default=0.95,  type=float)
parser.add_argument('--teacher_rep_penalty', default=1.15, type=float,
                    help='repetition_penalty for the teacher. NOT cosmetic: suppressing eos '
                         'to force a 500-1000 token document pushes a small model past where '
                         'it wanted to stop and it degenerates into loops. Measured on '
                         'pythia-160m, fraction of repeated 8-grams: 0.089 at 1.0, 0.000 at '
                         '1.15, at identical wall time. 1.0 disables it. A corpus that loops '
                         'is not the "clean text" this experiment is premised on')
parser.add_argument('--synth_min',     default=500,   type=int,
                    help='--dataset synth: each example is a uniform random length in '
                         '[--synth_min, --synth_max] TEACHER tokens')
parser.add_argument('--synth_max',     default=1000,  type=int)
parser.add_argument('--teacher_device', default=None,
                    help='device for the teacher (default: --device). Set cpu to keep the '
                         'GPU entirely for training, at roughly 20x less generation speed')
parser.add_argument('--synth_eval_docs', default=400, type=int,
                    help='documents in the CACHED synthetic held-out set. Generated once, '
                         'written to ./synth_eval/, and reused: an eval set regenerated per '
                         'call would make the EVAL curve a walk over datasets as much as '
                         'over training')
parser.add_argument('--gen_interval',  default=0,     type=int,
                    help='print a free-running GEN sample every N training steps. 0 (the '
                         'default) means "every --checkpoint steps", which is what the '
                         'generation sample was tied to before this flag existed, so every '
                         'pre-existing invocation is unchanged. Generation is cheap next to '
                         'a checkpoint save, and the text is the measurement that has '
                         'overturned the scalars more than once, so it is worth sampling '
                         'far more often than the weights are written')
parser.add_argument('--eval_interval', default=0,     type=int,
                    help='score the held-out split of --dataset every N training steps and '
                         'print an EVAL line. 0 (the default) disables it. Uses the same '
                         'held-out documents every time and the same framing as one-shot '
                         '--eval, and reports clean/median/runaway% the way exp/score.py '
                         'does -- a plain mean is not usable here, a handful of runaway '
                         'documents move it by orders of magnitude')
parser.add_argument('--eval_corpora',  default=None,
                    help='comma-separated held-out sets to score every --eval_interval '
                         'steps, e.g. "synth,pile". Default: the training corpus alone. '
                         'Scoring a corpus the run was NOT trained on is the TRANSFER '
                         'measurement -- for synthetic pre-pretraining that is the whole '
                         'point, since fit to the teacher is not the claim. Each set gets '
                         'its own EVAL line tagged with its corpus name; they are built '
                         'once each and reused')
parser.add_argument('--reason_eval',   default=None,
                    help='comma-separated zero-shot multiple-choice benchmarks scored every '
                         '--eval_interval steps: arc_easy | arc_chal | obqa | winogrande. '
                         'Held-out LOSS cannot measure reasoning -- on a factual corpus it '
                         'rewards memorisation, which is the opposite of the goal -- so this '
                         'is the metric that tracks whether the model REASONS. winogrande is '
                         'the cleanest: it needs plausibility judgement and no retrievable '
                         'fact. Chance is 1/n_choices and is printed on every line')
parser.add_argument('--reason_docs',   default=0,     type=int,
                    help='cap items per benchmark (0 = the whole validation split)')
parser.add_argument('--eval_json',     default=None,
                    help='--eval --eval_corpora: also write the results table as JSON here')
parser.add_argument('--eval_docs',     default=400,   type=int,
                    help='documents in the --eval_interval held-out set (400 matches '
                         'exp/score.py and PLAN.txt\'s reference table)')
parser.add_argument('--log',           default=None)
parser.add_argument('--monitor',       default=100,   type=int)
parser.add_argument('--generate',      default=False, action='store_true',
                    help='one-shot: load checkpoint, generate from START+prompt, print, exit (no dataset/training)')
parser.add_argument('--n',             default=200,   type=int,
                    help='tokens to generate for --generate. Nothing else reads it: --vis '
                         'streams until the window is closed, and the training-loop GEN '
                         'samples are a fixed length')
parser.add_argument('--prompt',        default='',
                    help='generation prompt; START is always prepended (0x02 with '
                         '--tokenizer char, <|endoftext|> with a pretrained one), so leave '
                         'empty to generate from START alone')
parser.add_argument('--eval',          default=False, action='store_true',
                    help='one-shot: load a checkpoint, compute teacher-forced loss over a '
                         'held-out split of --dataset, report it and exit. No training. '
                         'Each document is an independent batch row framed [START] text '
                         '[END] with a fresh DFF state, and every step is scored -- the '
                         'same clip framing and gradient target the training loop uses, and '
                         'the same measurement gptneo.py --eval makes, so the two numbers '
                         'compare directly. Note --init: a "relu"/"gaussian" context seed is '
                         'random, so the loss moves slightly run to run unless --seed is '
                         'fixed (--init zero is exactly reproducible)')
parser.add_argument('--split',         default=None,
                    help="--eval split; default is the corpus's held-out split (validation "
                         "for tiny/c4), or 'validation' for a bare hub repo id")
parser.add_argument('--column',        default=None,
                    help='--eval text column (default: the corpus default, else "text")')
parser.add_argument('--examples',      default=0,     type=int,
                    help='--eval: stop after this many documents (0 = the whole split)')
parser.add_argument('--init',          default='relu',
                    choices=['zero', 'gaussian', 'relu'],
                    help='how the DFF context is seeded before prompting and at every '
                         'context reset, in all modes (training, --generate, --vis): '
                         'zeros, standard-normal noise, or relu(randn) '
                         '(non-negative, ~50%% zeros, matching the steady-state shape)')
parser.add_argument('--seed',          default=None,  type=int)
parser.add_argument('--device',        default=None)
parser.add_argument('--verbose',       default=False, action='store_true',
                    help='print the torchinfo model summaries in --generate/--vis (training '
                         'always prints them, since they are logged)')
parser.add_argument('--altvis',        default=False, action='store_true',
                    help='live per-layer DFF map: an n_layers x 2 grid of imshow panels. Top '
                         'row is each layer\'s ContextCNN INPUT, bottom row its OUTPUT -- the '
                         'tensor the register stores and the layer above receives. Each panel '
                         'is the STANDARD DEVIATION ACROSS CHANNELS at every spatial position, '
                         'an SxS map, so it shows WHERE in the grid the state carries '
                         'variation rather than how much of it there is overall. Like --vis '
                         'this is read-only: it generates from --prompt and trains nothing.')
parser.add_argument('--vis',           default=False, action='store_true',
                    help='live text-generation viz (DFF std + P(next token)) from the '
                         'prompt token; no training. Read-only. Press x to exit')
parser.add_argument('--delay',         default=0.1,   type=float,
                    help='seconds to pause per vis frame')
parser.add_argument('--cmap',          default='viridis',
                    help='matplotlib colormap for --vis')
parser.add_argument('--temperature',   default=1.0,   type=float,
                    help='sampling temperature for --vis/--generate and the training-loop '
                         'text samples (0 = argmax)')
parser.add_argument('--push',          default=False, action='store_true',
                    help='push the --load checkpoint to the HuggingFace hub as a '
                         'PyTorchModelHubMixin model (repo --hub_repo), then exit. '
                         'No training. Requires a write token (huggingface-cli login)')
parser.add_argument('--pretrained',    default=None, nargs='?', metavar='REPO',
                    const='siliconperception/VLA',
                    help='load weights + architecture from this HuggingFace hub repo '
                         'instead of a local checkpoint, e.g. siliconperception/VLA '
                         '(the value used when the flag is given with no repo). '
                         'Overrides --load')
parser.add_argument('--revision',      default=None,
                    help='--pretrained: hub branch, tag or commit (default: main)')
parser.add_argument('--hub_repo',      default='siliconperception/VLA',
                    help='--push target hub repo id')
parser.add_argument('--private',       default=False, action='store_true',
                    help='--push: create the hub repo private (default: the org/user default '
                         'visibility). Ignored if the repo already exists')
args = parser.parse_args()
if args.epochs and not args.subsample:
    raise SystemExit('--epochs is the --subsample turnover rate and needs --subsample')
if args.refresh and not args.subsample:
    raise SystemExit('--refresh is the --subsample turnover rate and needs --subsample')
if args.blocks:
    if args.dataset != 'babylm' or args.mix:
        raise SystemExit('--blocks needs a local text corpus and a single dataset '
                         '(--dataset babylm, no --mix)')
    if args.subsample:
        raise SystemExit('--blocks and --subsample are two different ways to choose what a '
                         'slot reads; pick one')
    if args.shuffle:
        raise SystemExit('--blocks is a contiguous read and cannot be shuffled')
    args.shuffle = False
    if args.dataset not in {n.strip() for n in (args.unframed or '').split(',')}:
        raise SystemExit(f'--blocks needs --unframed {args.dataset}: a contiguous stream has '
                         'no document boundaries to frame, and a framed slot resets the DFF '
                         'at every refill -- the opposite of what blocks are for')
if args.refresh_every and not args.refresh:
    raise SystemExit('--refresh_every is the --refresh schedule and needs --refresh')
if args.refresh and args.epochs:
    raise SystemExit('--refresh and --epochs are two turnover schedules for the same pool: '
                     '--epochs is a fixed rate, --refresh is stall-driven. Pick one.')
if args.refresh and not (0.0 < args.refresh <= 1.0):
    raise SystemExit(f'--refresh {args.refresh}: a fraction of the pool, in (0, 1]')


def _cli_given(argv=None):
    """The set of option dests actually typed on the command line. argparse fills every
    default in, so a value in `args` cannot otherwise be told apart from one the user passed;
    re-parsing with the defaults suppressed leaves only what was really there. Used to let a
    few options beat the architecture a --load checkpoint carries (see _ARCH_OVERRIDE)."""
    saved = [a.default for a in parser._actions]
    for a in parser._actions:
        a.default = argparse.SUPPRESS
    try:
        return set(vars(parser.parse_args(argv)))
    finally:
        for a, d in zip(parser._actions, saved):
            a.default = d


_CLI_GIVEN = _cli_given()

# ── multi-dataset mix ─────────────────────────────────────────────────────────

def _parse_mix(spec):
    """'brt:0.5,web:0.5' -> ([names], [normalized weights]); None if unset."""
    if not spec:
        return None
    names, weights = [], []
    for part in spec.split(','):
        nm, _, w = part.partition(':')
        names.append(nm.strip())
        weights.append(float(w) if w else 1.0)
    s = sum(weights) or 1.0
    return names, [w / s for w in weights]

_mix = _parse_mix(args.mix)

# --unframed: every name must be a corpus this run trains on, and with several corpora the
# unframed one has to own its slots (see the help text), which is what --mix_slots does.
_UNFRAMED = {n.strip() for n in (args.unframed or '').split(',') if n.strip()}
if _UNFRAMED:
    _train_names = set(_mix[0]) if _mix else {args.dataset}
    if _UNFRAMED - _train_names:
        raise SystemExit(f'--unframed: not in --dataset/--mix: '
                         f'{",".join(sorted(_UNFRAMED - _train_names))}')
    if _mix and not args.mix_slots:
        raise SystemExit('--unframed with --mix needs --mix_slots: a slot either resets on '
                         'every document or never does, so an unframed corpus cannot share '
                         'the one clip queue --mix feeds every slot from')

# How many of the --batch slots the batchwise vocab stream occupies. worker() derives the
# same number for slot construction; it is computed here too because the training loop logs
# the vocab and corpus halves of the loss separately and has to know where the split is.
# Slot order is vocab-first (see worker()), so rows [0:_N_VOCAB] are the vocab channel.
_N_VOCAB = (min(args.vocab_slots, args.batch)
            if (args.vocab_files or '').strip() and args.vocab_slots else 0)

# --datarep, resolved once at module scope: clip_text, the vocab slots, generate() and the
# --vis loop all read it, and they run in different threads.
# --accumulate is deprecated: accepted so old command lines still run, ignored so it cannot
# silently change a run. It only ever did anything for a layer that HELD its register, and
# with --ema_ladder (periods forced to 1) or --clock sync nothing holds.
if int(getattr(args, 'dff_every', 1) or 1) != 1:
    print(f'WARNING: --dff_every {args.dff_every} is DEPRECATED and ignored: every layer has '
          f'a DFF register and a feedback add. Removing one cost 0.503 nats at equal '
          f'parameter count (see PLAN.txt).', flush=True)
    args.dff_every = 1

_dead = [f for f in ('clock', 'clock_base', 'clock_max', 'clock_ends')
         if getattr(args, f, None) is not None]
if _dead:
    print(f'WARNING: {", ".join("--" + f for f in _dead)} DEPRECATED and ignored. The DFF '
          f'write clock is gone -- every register is written every step and the timescale '
          f'is the --ema/--ema_ladder blend rate.', flush=True)

if getattr(args, 'accumulate', False):
    print('WARNING: --accumulate is DEPRECATED and ignored. It applied only to layers that '
          'hold their register between writes; --ema_ladder and --clock sync both write '
          'every layer every step, so it averaged a single output. Drop it from the command '
          'line.', flush=True)
    args.accumulate = False

_DATAREP = int(args.datarep or 1)
if _DATAREP < 1:
    raise SystemExit(f'--datarep {_DATAREP}: must be >= 1 (1 is off)')
# Every human-facing cadence is scaled by N so the run READS the same at any --datarep: a
# STEP line every --monitor tokens, a sample every --gen_interval tokens, an eval every
# --eval_interval tokens, a checkpoint every --checkpoint tokens. Without this, N=8 would
# print 8x the STEP lines and generate 8x the samples for the same data.
# NOT scaled: --run_steps, which is the step budget the user is explicitly spending, and the
# step NUMBER itself, which is the optimizer clock the checkpoint and resume logic run on.
# NOT dedupable: the loss VALUE. Slots stream independent clips, so at any given step the
# batch holds a mix of replica positions -- there is no "last replica" step to report.
if _DATAREP > 1:
    # NOTHING is scaled. Every interval -- --monitor, --gen_interval, --eval_interval,
    # --checkpoint -- is a count of RAW STEPS at any --datarep, so each flag means exactly
    # what it says. The consequence to keep in mind when comparing runs: at N > 1 a given
    # step count is 1/N of the DATA, so an EVAL at step 20000 is 20000/N tokens in, and two
    # runs at different N are only comparable on step/N, not on step.
    print(f'--datarep {_DATAREP}: each token is fed {_DATAREP}x. All intervals are RAW '
          f'STEPS -- monitor {args.monitor}, gen {args.gen_interval}, eval '
          f'{args.eval_interval}, checkpoint {args.checkpoint}. A step is {1.0/_DATAREP:.3g} '
          f'tokens, so compare runs at different --datarep on step/{_DATAREP}', flush=True)

# Validated HERE, in the main thread, not in worker(): worker runs as a thread, and a
# SystemExit raised there kills only that thread -- the training loop then blocks forever
# on an empty clip queue instead of exiting. Anything that can be checked from the flags
# alone therefore has to be checked before the worker starts.
if _N_VOCAB:
    _vf = [f.strip() for f in args.vocab_files.split(',') if f.strip()]
    _fr = {os.path.splitext(os.path.basename(f))[0]
           for f in (args.vocab_framed or '').split(',') if f.strip()}
    if _N_VOCAB < len(_vf) and _fr and len(_fr) < len(_vf):
        raise SystemExit(
            f'--vocab_slots {_N_VOCAB} with {len(_vf)} --vocab_files merges several files '
            f'into one slot, but --vocab_framed names only {sorted(_fr)}. A framed pool '
            f'resets the recurrent state between examples and an unframed one never does; '
            f'one slot cannot do both. Either frame all of them, none of them, or give each '
            f'file its own slot (--vocab_slots >= {len(_vf)}).')

# ── restore architecture args from checkpoint ─────────────────────────────────

_ARCH_ARGS = ('context', 'n_hidden', 'c_context', 'c_text', 'n_layers', 'depth', 'kernel',
              'tokenizer', 'head_norm', 'ema', 'ema_ladder', 'qproj',
              'tap', 'linout', 'linout_kernel', 'dff_every',
              'init', 'clock_base', 'clock_max', 'clock_ends', 'clip_dff', 'tap_norm', 'norm', 'norm_groups', 'dff_norm', 'bn_track', 'bn_affine',
                  'bn_momentum', 'bn_eps')

# Architecture args a command-line value may override on --load/--pretrained, instead of the
# checkpoint's own. These add no parameters and no shapes, so the state_dict loads either way
# and the run is still the model that was trained -- the DFF write schedule is the one thing
# you can legitimately change at load time. Everything else in _ARCH_ARGS defines the weights
# and is taken from the checkpoint whatever the command line says.
# --init seeds the DFF at every context reset, in training, --generate and --vis alike, so
# a checkpoint sampled without it was being seeded differently than it was trained -- it adds
# no parameters, so it restores like the rest and overrides like the other write-schedule
# options.
_ARCH_OVERRIDE = ('ema', 'ema_ladder', 'init', 'clip_dff', 'tap_norm', 'norm', 'norm_groups', 'dff_norm', 'bn_track', 'bn_affine',
                  'bn_momentum', 'bn_eps')


def _restore_arch(saved, source):
    """Copy the architecture a checkpoint was trained with into args, except for the
    _ARCH_OVERRIDE options the user actually typed -- those win, e.g. training a model with
    --clock dither and then sampling it with --clock fixed."""
    for k in _ARCH_ARGS:
        if k in _ARCH_OVERRIDE and k in _CLI_GIVEN:
            was = saved.get(k, '(unset)')
            if was != getattr(args, k):
                print(f'--{k} {getattr(args, k)} overrides the {source} value {was}')
            continue
        # older checkpoints may predate an arch arg → keep the current default for it
        if k in saved:
            setattr(args, k, saved[k])


_loaded_ckpt = None
_start_step  = 0                 # resumed global step count (0 for a fresh run)
_start_exs   = 0                 # resumed cumulative training-example count
_start_lr    = None              # lr the checkpoint was saved at (--schedule plat resume)
_start_plat  = None              # binned loss window carried across a --schedule plat resume
if args.pretrained and args.load is not None:
    # --pretrained overrides --load: the hub repo carries both weights and config.json,
    # so a local checkpoint would only be half-used (its saved_args then foreign weights).
    print(f'--pretrained overrides --load {args.load}: loading {args.pretrained} from the hub')
    args.load = None
if args.load is not None:
    _loaded_ckpt = torch.load(args.load, map_location='cpu', weights_only=True)
    # rebuild the model with the architecture it was trained with
    _restore_arch(_loaded_ckpt['saved_args'], 'checkpoint')
    _start_step = int(_loaded_ckpt.get('step', 0))   # continue the step sequence
    _start_exs  = int(_loaded_ckpt.get('examples', 0))   # continue the example count
    # read here: the ckpt is freed before the scheduler is built
    _start_lr   = _loaded_ckpt.get('lr')
    _start_plat = _loaded_ckpt.get('plat')

if args.c_text is None:          # default token embedding width to n_hidden
    args.c_text = args.n_hidden

# Resolved AFTER _restore_arch, so a checkpoint's own interior width wins over the default
# on --load. Unset means n_hidden, which is what every run before this flag existed built.
if args.c_context is None:       # default ContextCNN interior width to n_hidden
    args.c_context = args.n_hidden
if args.c_context != args.n_hidden and args.depth < 2:
    print(f'WARNING: --c_context {args.c_context} ignored at --depth {args.depth}: a '
          f'single conv has to map the DFF state to itself, so there is no interior to '
          f'widen or narrow. Building n_hidden -> n_hidden.')

# ── log / device / seed ───────────────────────────────────────────────────────

if args.log is None:
    if args.generate or args.vis or args.altvis or args.push or args.eval:  # one-shot: no log
        args.log = os.devnull
    else:
        # training -> log/log.<date>. Never reuse a name: two runs started in the
        # same second would otherwise interleave their lines in one file.
        os.makedirs('log', exist_ok=True)
        date = subprocess.check_output(['/usr/bin/date', '+%Y.%m.%d-%H.%M.%S']).decode().strip()
        stem = f'log/log.{date}'
        args.log, n = stem, 1
        while os.path.exists(args.log):
            args.log, n = f'{stem}.{n}', n + 1
if args.device is None:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
if args.seed is None:
    args.seed = int.from_bytes(os.urandom(4), byteorder='big')
    print('seed', args.seed)

torch.manual_seed(args.seed)
print(args)
# Prepend the resumed checkpoint's log so chart.py sees one uninterrupted sequence.
# Only for real training log files (skip devnull / generate / vis).
if _loaded_ckpt is not None and args.log and args.log != os.devnull:
    _prev_log = _loaded_ckpt.get('log') or ''
    if _prev_log:
        with open(args.log, 'a') as f:
            f.write(_prev_log)
            if not _prev_log.endswith('\n'):
                f.write('\n')
with open(args.log, 'a') as f:
    print('ARGS', args, file=f)

# ── model ─────────────────────────────────────────────────────────────────────

class ContextCNN(nn.Module):
    """DFF state update: a plain chain of conv(-norm)-ReLU blocks.
    Input:  [B, n_hidden, S, S]
    Output: [B, n_hidden, S, S]

    The interior runs at c_context channels (--c_context, default n_hidden): the first
    conv is n_hidden -> c_context and everything after is c_context -> c_context. The INPUT
    width is not free -- it is the DFF state's -- and the output width is c_out, which is
    n_hidden when this module has to widen back to the register itself, or c_context under
    --linout, where the 1x1 does the widening and the whole chain, final ReLU included,
    stays narrow.

    --norm none removes the BatchNorm entirely, leaving conv2d + ReLU. That is a
    bigger change than it looks, because BatchNorm is the source of every
    train/eval discrepancy this model has: it is the ONLY module whose function
    differs between the two modes, and the recurrence amplifies that difference.
    Concretely, with --norm batch:
      - the DFF carried between steps is recomputed in EVAL mode, so the state the
        model trains on is normalized by running statistics that lag the weights
      - a model can score well on teacher-forced training loss and be unusable
        held-out (observed twice: 2.9 and 3.4 nats)
      - free-running generation can lock into a repeating token while every
        training-time metric stays clean
    With --norm none the model computes the same function in both modes, so all
    of that goes away by construction. It also removes running-statistics buffers
    from the state_dict and from an FPGA implementation.

    What it costs: BatchNorm is what keeps a 51-conv chain trainable. Without it
    the initialization has to preserve variance itself, so the convs are
    He-initialized (kaiming_normal, fan_in, relu gain) instead of PyTorch's
    default kaiming_uniform(a=sqrt(5)), which has a gain far below 1 for ReLU and
    would shrink the signal by ~3x per layer -- over 51 layers that is 3**-51,
    i.e. nothing reaches the readout. Even so, a deep plain chain is harder to
    train than a normalized one; that is the experiment.
    """
    def __init__(self, n_hidden, depth, kernel, norm='batch', groups=32,
                 bn_track=True, bn_affine=False, bn_momentum=0.1, bn_eps=1e-5,
                 c_context=None, c_out=None):
        super().__init__()
        pad = kernel // 2
        self.norm_kind = norm
        # --c_context: the interior width. The ENDS are pinned by the DFF state this module
        # updates -- it reads [B, n_hidden, S, S] and its output is written back to a
        # register of that shape -- so the first conv widens into the interior and the last
        # narrows out of it. depth 1 has no interior and stays n_hidden -> n_hidden.
        # The EFFECTIVE width, not the requested one: at depth 1 there is no interior, so
        # what gets built is n_hidden -> n_hidden and that is what this must report --
        # saved_args reads it back, and a --load has to rebuild the stack that was trained.
        self.c_context = int(c_context) if (c_context and depth > 1) else n_hidden
        w = self.c_context
        # c_out: what the LAST conv produces. n_hidden by default -- the chain widens back to
        # the DFF's width itself, because its output goes straight into the register. Under
        # --linout the caller passes c_out=c_context instead and lets the 1x1 do the widening,
        # so the chain never runs a wide conv and the final ReLU sits at the interior width.
        self.c_out = int(c_out) if c_out else n_hidden
        def block(cin, cout):
            conv = nn.Conv2d(cin, cout, kernel, padding=pad)
            if norm == 'group':
                # GroupNorm normalizes each SAMPLE over channel groups and space, so it
                # carries no running statistics and computes the same function in train
                # and eval -- the property that motivated trying to remove BatchNorm,
                # kept while restoring the per-layer per-step re-centring that --norm
                # none turned out to need.  affine=False keeps the parameter count
                # identical to the BatchNorm path.
                return nn.Sequential(conv,
                                     nn.GroupNorm(max(1, min(groups, cout)), cout,
                                                  affine=False),
                                     nn.ReLU())
            if norm == 'none':
                # variance-preserving init: without BatchNorm nothing downstream
                # rescales, so the init has to do it. fan_in + relu gain keeps
                # Var(out) ~ Var(in) through conv->ReLU.
                nn.init.kaiming_normal_(conv.weight, mode='fan_in', nonlinearity='relu')
                nn.init.zeros_(conv.bias)
                return nn.Sequential(conv, nn.ReLU())
            # --bn_track False makes BatchNorm use BATCH statistics in eval as well as
            # train, so there is no train/eval discrepancy and no running-statistics
            # buffers -- while keeping the cross-batch pooling that per-sample normalizers
            # (group, softmax, std) all failed without.  Note that at inference the
            # statistics come from whatever batch is fed: at batch 1 BatchNorm2d degenerates
            # to InstanceNorm over the SxS grid, a well-defined but different function.
            return nn.Sequential(conv,
                                 nn.BatchNorm2d(cout, affine=bn_affine,
                                                track_running_stats=bn_track,
                                                momentum=bn_momentum, eps=bn_eps),
                                 nn.ReLU())
        self.layers = nn.ModuleList(
            block(n_hidden if i == 0 else w, self.c_out if i == depth - 1 else w)
            for i in range(depth))

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class DecoderCNN(nn.Module):
    """1×1 conv n_hidden→n_out, then global average pool.
    Input:  [B, n_hidden, S, S]
    Output: [B, n_out]

    n_out is the readout width: 256 (the byte vocabulary, so this is already the logits)
    for --tokenizer char, or the pretrained embedding width for every other --tokenizer,
    where the conv is the linear adapter feeding a frozen lm_head.

    norm2d (--head_norm batch2d) inserts a BatchNorm2d between the conv and the pool, the
    same Conv->BatchNorm2d shape ContextCNN uses. It normalizes per channel over batch and
    space, before the pool averages, and is a plain affine per channel at inference, so it
    folds into proj's weights."""
    def __init__(self, n_hidden, S, n_out=256, norm2d=False):
        super().__init__()
        self.proj = nn.Conv2d(n_hidden, n_out, 1)
        self.norm = nn.BatchNorm2d(n_out) if norm2d else nn.Identity()
        self.pool = nn.AvgPool2d(S)

    def forward(self, x):
        return self.pool(self.norm(self.proj(x))).squeeze(-1).squeeze(-1)


class DFFEma:
    """How a register commits the value its layer just computed.

    Every register is written every step -- there is no gating and no schedule -- so all
    this holds is the blend: register <- register + e*(new - register), with e from
    --ema/--ema_ladder. e == 1.0 (or ema None) replaces outright.

    It owns one piece of state, a per-row step counter, and that exists for a single rule:
    a row's FIRST write of a document must replace the register outright rather than blend,
    or (1-e) of the --init seed would survive in the state for the rest of the document.

    One writer belongs to one context, like the DFF list beside it: forward() keeps its own,
    generate() and --vis keep theirs, so a sample drawn mid-training cannot disturb the
    training state."""

    def __init__(self, ema, B, device):
        self.ema = ema                       # float, or one per register (--ema_ladder)
        self.t   = torch.zeros(B, dtype=torch.long, device=device)

    def write(self, li, o, prev):
        if self.ema is None:
            return o
        e = self.ema[li] if isinstance(self.ema, (list, tuple)) else self.ema
        if e >= 1.0:
            return o
        # first write of a document replaces; every later one blends
        return torch.where((self.t == 0).view(-1, 1, 1, 1), o, prev + e * (o - prev))

    def advance(self):
        """One step of the token stream has been consumed."""
        self.t = self.t + 1

    def reset(self, flag):
        """Rows starting a new document are back at their first write."""
        self.t = torch.where(flag, torch.zeros_like(self.t), self.t)


# PyTorchModelHubMixin gives VLAModel save_pretrained()/push_to_hub()/from_pretrained()
# (see --push). It records the __init__ kwargs as config.json, so a hub checkpoint rebuilds
# with the architecture it was trained with. huggingface_hub is optional: without it the
# model is a plain nn.Module and only --push is unavailable.
try:
    from huggingface_hub import PyTorchModelHubMixin as _HubMixin
except ImportError:                                  # pragma: no cover
    class _HubMixin:                                 # no-op base
        pass


class VLAModel(nn.Module, _HubMixin):
    """Recurrent CNN language model. Each step the current token is embedded, broadcast
    to an S×S grid, projected to n_hidden and summed into the per-layer DFF state;
    ContextCNN updates the state and the decoder reads it out to next-token logits.
    n_layers stacks (ContextCNN + feedback) units in series, each carrying its own DFF
    state. clock (--clock) decides how often each layer
    commits its new state -- every step, on a per-layer ladder, or on a random schedule --
    and accumulate (--accumulate) makes each of those writes an average rather than a
    sample; see DFFClock.

    `tokenizer` picks the vocabulary and both ends of the token path:
      char           learned nn.Embedding(256, c_text) in, decoder straight to 256
                     logits out, lmhead = Identity. Fully self-contained.
      tiny1m/tiny8m  the pretrained TinyStories GPT-Neo embedding in and its lm_head out.
      pythia*        the same, from the Pile-trained EleutherAI GPT-NeoX models, whose
                     embeddings (unlike TinyStories') have no untrained rows.

    For every pretrained tokenizer the borrowed layers are frozen (see
    set_pretrained_trainable / --unfreeze) and c_text is forced to that model's embedding
    width, so the CNN meets them through two linear 1×1 conv2d adapters: text_proj
    (c_text → n_hidden) and decoder.proj (n_hidden → c_text). By default nothing sits
    between the decoder and the head; head_norm (--head_norm) optionally normalizes the
    readout there, since the borrowed head was trained downstream of a final norm."""
    def __init__(self, n_hidden, depth, kernel, S,
                 c_context=None, c_text=None, n_layers=1, tokenizer='char', head_norm='none',
                 ema=None, qproj='none', tap=False, clip_dff=0.0,
                 tap_norm='none', norm='batch', norm_groups=32, dff_norm='none',
                 bn_track=True, bn_affine=False, bn_momentum=0.1, bn_eps=1e-5):
        super().__init__()
        self.S          = S
        self.n_hidden   = n_hidden
        # ContextCNN's interior width (--c_context). n_hidden still sizes the DFF state and
        # every module that reads or writes it; this sizes only the conv chain in between.
        self.c_context  = int(c_context) if c_context else n_hidden
        self.c_text     = c_text if c_text is not None else n_hidden
        self.n_layers   = max(1, n_layers)    # stacked (ContextCNN + feedback) layers (see --n_layers)
        # --ema/--ema_ladder: how much of its new output each register takes. Every
        # register is written every step (see DFFEma); the convs run every step regardless.
        self.ema = None                                  # derived in set_ema
        self.clip_dff   = float(clip_dff or 0.0)
        # --dff_penalty: read off the module-level args, the same way --linout is, so a
        # checkpoint rebuilt by exp/score.py or exp/reach.py does not need a new kwarg --
        # it changes the LOSS, not the architecture, and no state_dict entry depends on it.
        self.dff_penalty = float(getattr(args, 'dff_penalty', 0.0) or 0.0)
        self.dff_bias    = float(getattr(args, 'dff_bias', 0.0) or 0.0)
        self.tap_norm_kind = tap_norm or 'none'
        self.norm_kind     = norm or 'batch'
        self.norm_groups   = int(norm_groups)
        self.bn_track    = bool(bn_track)
        self.bn_affine   = bool(bn_affine)
        self.bn_momentum = float(bn_momentum)
        self.bn_eps      = float(bn_eps)
        self.dff_norm_kind = dff_norm or 'none'
        self.dff_softmax   = nn.Softmax2d() if self.dff_norm_kind == 'softmax' else None
        # Every layer owns a DFF register and reads a feedback add. (--dff_every, which
        # made every Kth layer straight through, is deprecated: removing a register cost
        # 0.503 nats at identical parameter count and conv depth.) These are kept as the
        # identity map because the ladder reporting and --altvis index through them.
        self.dff_layers = list(range(self.n_layers))
        self.dff_slot   = {li: li for li in range(self.n_layers)}
        self.n_dff      = self.n_layers
        self.set_ema(ema, getattr(args, 'ema_ladder', None))
        self.tokenizer  = tokenizer           # vocabulary / token path (see --tokenizer)
        # --head_norm only has a job when there is a borrowed head to feed; with char the
        # decoder emits logits directly and normalizing them would just rescale the
        # softmax. Forced to 'none' there so head_norm always describes what was built.
        self.head_norm_kind = head_norm if tokenizer != 'char' else 'none'
        _ln_f = _ln_f_path = None             # the borrowed final norm, for head_norm='ln_f'

        if tokenizer == 'char':
            self.tok      = ByteTokenizer()
            self.vocab    = self.tok.vocab_size
            self.tok_embed = nn.Embedding(self.vocab, self.c_text)   # token → c_text channels
            self.lmhead   = nn.Identity()     # the decoder already emits the 256 byte logits
        else:
            # Pull the vocabulary-facing layers out of the pretrained causal LM and drop the
            # transformer blocks. get_input_embeddings/get_output_embeddings are the
            # family-agnostic accessors, so gpt_neo (transformer.wte / lm_head) and gpt_neox
            # (gpt_neox.embed_in / embed_out) are both handled without naming either. GPT-Neo
            # ties its two (lm_head.weight IS wte.weight, one weight matrix); GPT-NeoX does
            # not, so pythia* contributes two independently trained matrices.
            from transformers import AutoModelForCausalLM
            repo = _TOKENIZERS[tokenizer]
            lm   = AutoModelForCausalLM.from_pretrained(repo)
            self.vocab     = lm.config.vocab_size
            self.c_text    = lm.config.hidden_size   # the embedding width is not ours to choose
            self.tok       = HFTokenizer(repo, self.vocab)
            self.tok_embed = lm.get_input_embeddings()    # vocab → c_text
            self.lmhead    = lm.get_output_embeddings()   # c_text → vocab
            # --head_norm ln_f additionally borrows the final norm the source model applies
            # right before this head, so the head sees the input distribution it was fit to.
            if self.head_norm_kind == 'ln_f':
                _ln_f_path, _ln_f = _final_norm(lm)
                if _ln_f is None:
                    print(f'WARNING: --head_norm ln_f: no final norm found on {repo} '
                          f'(model_type {lm.config.model_type}); falling back to none. Add '
                          f'its path to _FINAL_NORM_PATHS.')
                    self.head_norm_kind = 'none'

        self.start_id  = self.tok.start_id
        self.end_id    = self.tok.end_id
        self.null_id   = self.tok.null_id

        # --linout puts a 1x1 at the end of every layer, and that 1x1 is the natural place
        # for the widening: with it on, the conv chain STAYS at c_context (final BN+ReLU
        # included) and linout projects c_context -> n_hidden. Without it there is nothing
        # downstream to widen, so the chain's last conv has to reach n_hidden itself.
        # Decided here because it sets ContextCNN's output width. When c_context == n_hidden
        # (the default) both paths build exactly the same convs as before either flag existed.
        self.ctx_out   = self.c_context if getattr(args, 'linout', False) else n_hidden
        self.context   = ContextCNN(n_hidden, depth, kernel, norm=self.norm_kind,
                                    groups=self.norm_groups, bn_track=self.bn_track,
                                    bn_affine=self.bn_affine,
                                    bn_momentum=(self.bn_momentum or None),
                                    bn_eps=self.bn_eps, c_context=self.c_context,
                                    c_out=self.ctx_out)
        self.decoder   = DecoderCNN(n_hidden, S, self.c_text if tokenizer != 'char' else 256,
                                    norm2d=self.head_norm_kind == 'batch2d')
        # token grid (c_text) → n_hidden, summed into the DFF state
        self.text_proj = nn.Conv2d(self.c_text, n_hidden, 1)

        # --head_norm, on the [B, c_text] readout between the decoder and the head.
        # batch2d already lives inside the decoder (before the pool), so it is Identity here.
        # ln_f is borrowed and frozen with the other pretrained weights; layer/rms/batch are
        # fresh and train with the CNN.
        self.norm_path = _ln_f_path              # provenance of an ln_f head_norm, for the summaries
        self.head_norm = {
            'none':    lambda: nn.Identity(),
            'batch2d': lambda: nn.Identity(),
            'ln_f':    lambda: _ln_f,
            'layer':   lambda: nn.LayerNorm(self.c_text),
            'rms':     lambda: nn.RMSNorm(self.c_text),
            'batch':   lambda: nn.BatchNorm1d(self.c_text),
        }[self.head_norm_kind]()

        if tokenizer != 'char':
            self.set_pretrained_trainable(False)  # frozen unless --unfreeze

        # Deep layers 2..N: each is its own (ContextCNN + feedback) unit. Layer 1 takes
        # the token injection; deep layers take the previous layer's output combined with
        # their own DFF state. Only built when n_layers>1, so the n_layers=1 state_dict is
        # byte-identical to the single-layer model.
        if self.n_layers > 1:
            # Every layer is built the same: n_hidden in, c_context through the chain,
            # linout back out to n_hidden.
            self.deep_context = nn.ModuleList(
                ContextCNN(n_hidden, depth, kernel, norm=self.norm_kind,
                                    groups=self.norm_groups, bn_track=self.bn_track,
                                    bn_affine=self.bn_affine,
                                    bn_momentum=(self.bn_momentum or None),
                                    bn_eps=self.bn_eps, c_context=self.c_context,
                                    c_out=self.ctx_out)
                for _ in range(self.n_layers - 1))
            self.deep_proj = nn.ModuleList(
                nn.Conv2d(n_hidden, n_hidden, 1) for _ in range(self.n_layers - 1))
        else:
            self.deep_context = self.deep_proj = None

        # --linout: one 1x1 per layer, replacing deep_proj on the upward path. Identity-
        # initialized so the register starts out holding the ReLU output exactly; the weights
        # move off identity within a few steps and the register goes signed from then on.
        # args.linout is restored from the checkpoint by _restore_arch on --load (it is in
        # _ARCH_ARGS and deliberately NOT in _ARCH_OVERRIDE: it adds convolutions, so the
        # checkpoint's value defines the weights and a command-line value must not win).
        # getattr keeps checkpoints that predate the flag loadable -- they simply have no
        # 'linout' key and fall back to False.
        self.linout = None
        if getattr(args, 'linout', False):
            if getattr(args, 'tap', False):
                raise SystemExit('--linout and --tap are mutually exclusive: both put a 1x1 '
                                 'on the register path, and --tap also keeps deep_proj')
            # in_channels is the CHAIN's output width: n_hidden when --c_context is unset,
            # c_context when it is -- in which case this 1x1 IS the widening, and the last
            # 3x3 (c_context x n_hidden x 9 weights) disappears in favour of it
            # (c_context x n_hidden x 1).
            _lk = int(getattr(args, 'linout_kernel', 1) or 1)
            if _lk < 1 or _lk % 2 == 0:
                raise SystemExit(f'--linout_kernel {_lk}: must be a positive ODD integer '
                                 f'(even kernels cannot keep the grid the same size with '
                                 f'symmetric padding)')
            # padding K//2 with the default zeros padding_mode: S x S in, S x S out, so the
            # register, the feedback add and the decoder all keep the shapes they had.
            # one per LAYER, recurrent or not: every chain ends at c_context and every
            # layer widens back to n_hidden with its own 1x1/3x3 (see --dff_every).
            self.linout = nn.ModuleList(nn.Conv2d(self.ctx_out, n_hidden, _lk, padding=_lk // 2)
                                        for _ in range(self.n_layers))
            for _c in self.linout:
                if self.ctx_out == n_hidden:
                    # square: dirac_ is the identity on the CENTRE tap (and zeros elsewhere
                    # when K>1), so K=3 starts out computing exactly what K=1 does
                    nn.init.dirac_(_c.weight)
                else:
                    # Rectangular, so there is no identity. Semi-orthogonal instead: it
                    # preserves the norm of the channel vector at every position (no rescaling
                    # inside a recurrence that is prone to blowing up) and makes the register
                    # dense and SIGNED from step 0 -- which is the entire point of --linout.
                    # dirac_ would also "work" here, but it would copy the ReLU output into
                    # the first c_context channels and leave the other n_hidden-c_context at
                    # zero, i.e. a sparse non-negative register: the thing the flag exists to
                    # avoid, and 75% of the state dead at init when c_context is n_hidden/4.
                    _w = torch.empty(n_hidden, self.ctx_out)
                    nn.init.orthogonal_(_w)
                    with torch.no_grad():
                        _c.weight.zero_()
                        # centre tap carries the whole projection; the off-centre taps start
                        # at zero, so K>1 is again exactly K=1 at step 0 and grows from there
                        _c.weight[:, :, _lk // 2, _lk // 2] = _w
                nn.init.zeros_(_c.bias)
            self.deep_proj = None          # its job is done by linout now

        # --qproj: a 1x1 linear conv per layer on the DFF path, at that layer's own width
        # since it has to land on a tensor of the register's shape. Two placements,
        # applied between the register and the feedback add -- see _fb.
        #
        #   read   between the register and the feedback add. Trainable, so it is initialized
        #          to the identity (dirac kernel, zero bias): at step 0 the model is exactly
        #          --qproj none and training moves it off from there, which keeps an A/B
        #          honest and keeps a random mixer out of a loop prone to blowing up.
        #   write  between the layer output and the register, so the register holds a dense
        #          signed embedding. Its output only ever reaches the loss through the DFF,
        #          which forward() detaches, so it can never get gradient: it is frozen, and
        #          random rather than identity (an identity that cannot learn would be a
        #          no-op). Orthogonal, not gaussian -- a rotation preserves the norm of the
        #          channel vector at every position, so a fixed mixer inside the recurrence
        #          cannot rescale or collapse the state, and it stays invertible, so nothing
        #          in the state is destroyed. Frozen parameters are still state_dict entries,
        #          so a reload gets the same random projection back.
        if qproj == 'write':
            raise SystemExit("--qproj write was removed: its only path to the loss is through "
                             "the DFF, which is detached every step, so it could never train. "
                             "Use --qproj read (trainable) or --qproj none.")
        self.qproj_mode = qproj if qproj in _QPROJ_MODES else ('read' if qproj else 'none')
        # per RECURRENT layer (--dff_every): both sit on the register path, and a
        # straight-through layer has no register to read from or write to.
        self.qproj = (nn.ModuleList(nn.Conv2d(n_hidden, n_hidden, 1)
                                    for _ in range(self.n_dff))
                      if self.qproj_mode != 'none' else None)
        if self.qproj is not None:
            for _c in self.qproj:
                nn.init.dirac_(_c.weight)
                nn.init.zeros_(_c.bias)

        # --tap: a 1x1 linear conv after each layer's last conv-BN-ReLU, with the DFF
        # register fed from its output (see _tap). It is the first of the two convs in
        # series -- the second is the 1x1 already sitting on the upward path, deep_proj into
        # the next layer or decoder.proj on the last one, so no second module is needed.
        # Identity-initialized, like --qproj read, so step 0 is exactly the model without
        # --tap.
        self.tap = None
        self.tap_norm = None
        if tap:
            self.tap = nn.ModuleList(nn.Conv2d(n_hidden, n_hidden, 1)
                                     for _ in range(self.n_dff))
            # --tap_norm: normalize what leaves the tap, so the feedback gain is bounded by
            # construction rather than left to whatever the weights drift to. affine=False in
            # both cases, so no parameters are added; group additionally has no running
            # statistics, so train and eval compute the same function.
            if self.tap_norm_kind == 'batch':
                self.tap_norm = nn.ModuleList(nn.BatchNorm2d(n_hidden, affine=False)
                                              for _ in range(self.n_dff))
            elif self.tap_norm_kind == 'group':
                self.tap_norm = nn.ModuleList(
                    nn.GroupNorm(min(32, n_hidden), n_hidden, affine=False)
                    for _ in range(self.n_dff))
            for _c in self.tap:
                nn.init.dirac_(_c.weight)
                nn.init.zeros_(_c.bias)

        self.dff = None   # list of n_layers tensors [B, n_hidden, S, S], detached; None until first step
        self.clk = None   # DFFClock for self.dff (None under --clock sync); built with it

        # How a fresh context is seeded, set from --init after construction. Runtime
        # behaviour, not architecture: deliberately not part of the hub config, so it never
        # affects checkpoint or from_pretrained compatibility.
        self.init_mode = 'relu'

    def pretrained_params(self):
        """The borrowed embedding + lm_head, plus the final norm under --head_norm ln_f
        (empty with --tokenizer char). Deduped by identity: GPT-Neo ties lm_head.weight to
        tok_embed.weight, so there it is one tensor; GPT-NeoX (pythia*) keeps them separate.
        The fresh --head_norm kinds are not borrowed, so they are not listed here and stay
        trainable regardless of --unfreeze."""
        if self.tokenizer == 'char':
            return []
        mods = (self.tok_embed, self.lmhead)
        if self.head_norm_kind == 'ln_f':
            mods += (self.head_norm,)
        seen, out = set(), []
        for m in mods:
            for p in m.parameters():
                if id(p) not in seen:
                    seen.add(id(p))
                    out.append(p)
        return out

    def readout(self, dec):
        """Decoder output [B, c_text] → logits [B, vocab]: --head_norm, then the borrowed
        unembedding. Both are Identity with --tokenizer char, where the decoder already
        emits the 256 byte logits, and head_norm is Identity for 'none' and for 'batch2d'
        (which normalizes earlier, inside the decoder)."""
        return self.lmhead(self.head_norm(dec))

    def set_pretrained_trainable(self, flag):
        """Freeze/unfreeze the borrowed embedding + lm_head (see --unfreeze). Called from
        __init__ with False, so a model is frozen by default however it was built."""
        for p in self.pretrained_params():
            p.requires_grad_(bool(flag))

    def _new_dff(self, B, device):
        """A fresh DFF context state (--init). Used everywhere a context is started or
        reset, so train/generate/vis all begin from the same distribution.

          zero      zeros
          gaussian  standard-normal noise
          relu      relu(randn): non-negative and ~50% exact zeros, the shape the state
                    actually has in steady state, since it is a ReLU output

        Unit variance needs no scale knob: every step puts the state through `depth`
        stacked Conv->BatchNorm(affine=False)->ReLU, which drives it onto a fixed attractor
        (measured: mean 0.43, std 0.71, 52% exact zeros) regardless of how it started. The
        init is forgotten fast -- relative divergence between a zero and a gaussian start
        falls to 3% by 20 bytes and to float32 noise by 50 -- so --init only changes what
        the model sees for the first few dozen bytes of a context."""
        shapes = [(B, self.n_hidden, self.S, self.S)] * self.n_dff
        if self.init_mode == 'gaussian':
            return [torch.randn(s, device=device) for s in shapes]
        if self.init_mode == 'relu':
            return [torch.randn(s, device=device).relu() for s in shapes]
        return [torch.zeros(s, device=device) for s in shapes]

    def set_ema(self, ema=None, ema_ladder=None):
        """Set (or change) the DFF blend rate; None leaves it alone. It adds no parameter
        and changes no shape, so this is safe on a model whose weights are already loaded --
        it is what lets --ema/--ema_ladder on the command line override what a checkpoint was
        trained with (see _ARCH_OVERRIDE). Any live writer is dropped and rebuilt with the
        next context.

        Rates are indexed over the layers that HAVE REGISTERS (--dff_every): a blend rate
        describes a register, and a straight-through layer has none. At --dff_every 1 that
        is every layer."""
        if ema is not None:
            if isinstance(ema, (list, tuple)):
                self.ema = list(ema)          # a per-register ladder, already built
            else:
                self.ema = float(ema) if 0.0 < float(ema) < 1.0 else None
        if ema_ladder is not None:
            _spec = str(ema_ladder).strip()
            self.ema_ladder = _spec if _spec else None
        _nreg = getattr(self, 'n_dff', self.n_layers)
        if getattr(self, 'ema_ladder', None):
            _spec = str(self.ema_ladder)
            if ',' in _spec:
                # per-register WINDOWS in tokens. Short lists repeat their last entry, long
                # ones are truncated, so the spec need not be re-typed when --n_layers or
                # --dff_every changes.
                _w = [float(x) for x in _spec.split(',') if x.strip()]
                if not _w:
                    raise SystemExit(f'--ema_ladder {_spec!r}: no windows parsed')
                _w = (_w + [_w[-1]] * _nreg)[:_nreg]
                if any(x <= 0 for x in _w):
                    raise SystemExit(f'--ema_ladder {_spec!r}: windows must be > 0')
                self.ema = [min(1.0, 1.0 / x) for x in _w]
            else:
                _b = float(_spec)
                if _b <= 1.0:
                    raise SystemExit(f'--ema_ladder {_spec!r}: a bare BASE must be > 1 '
                                     f'(use a comma-separated window list for anything else)')
                self.ema = [min(1.0, 1.0 / (_b ** i)) for i in range(_nreg)]
        self.clk = None

    def _new_writer(self, B, device):
        """The blend state for one context. None when there is nothing to blend -- no --ema
        and no --ema_ladder -- where a write is a plain replace and needs no state."""
        return DFFEma(self.ema, B, device) if self.ema is not None else None

    def _init_dff(self, B, device):
        dev = torch.device(device)
        if (self.dff is None or len(self.dff) != self.n_layers
                or self.dff[0].shape[0] != B or self.dff[0].device != dev):
            self.dff = self._new_dff(B, device)
            self.clk = self._new_writer(B, dev)   # blend state too: rebuilt with the DFF

    def _fb(self, li, d):
        """Layer li's DFF state as the feedback add sees it (--qproj read). Off, this is the
        state itself: the ReLU output the layer last wrote, ~50% exact zeros. On, it is that
        state through a trainable 1x1 linear conv -- every output channel a signed
        combination of all the input channels at that spatial position -- so what the layer
        adds in is dense and signed even though the register holding it is sparse.

        This placement is the trainable one. Projecting on the way into the register instead
        (--qproj write) puts the conv outside the gradient horizon: its output reaches the
        loss only through self.dff, which forward() detaches every step, so those weights get
        grad None (measured: None, against 1.21 for text_proj on the same batch) and the
        mode only makes sense frozen.

        Note the two placements feed the *same* tensor into the add, since this conv is
        linear and --accumulate's running mean is linear too: mean(Q(o)) == Q(mean(o)) to
        float precision. What differs is what sits in the register -- sparse and
        non-negative here, dense and signed under write -- and therefore what the next
        step's ReLU sees.

        Why it is not redundant with the convs already on that path: Q is applied to the
        state but not to the token injection it is summed with, so the layer can transform
        what it remembers differently from what it is being told. Applied to the whole output
        instead, it would just be a reparameterization of the following 1x1 (deep_proj,
        decoder.proj) or 3x3 (ContextCNN) conv."""
        # --dff_norm conditions the state ON THE WAY OUT, so the REGISTER keeps the raw
        # ReLU output -- sparse, ~50% exact zeros, which is what a hardware state memory
        # wants -- while what is fed back into the layer is bounded.  Normalizing on the
        # write side instead would store a dense tensor and throw that sparsity away.
        # Because the read is scale-free, the stored state's magnitude no longer matters to
        # the recurrence: the feedback loop is bounded however large the register grows.
        if self.dff_norm_kind == 'std':
            # zero mean, unit variance per sample over the whole (C, S, S) volume.  Keeps
            # the sign and dynamic range that softmax removes.
            m = d.mean(dim=(1, 2, 3), keepdim=True)
            v = d.var(dim=(1, 2, 3), keepdim=True, unbiased=False)
            d = (d - m) * torch.rsqrt(v + 1e-5)
        elif self.dff_norm_kind == 'softmax':
            d = self.dff_softmax(d)
        return d if self.qproj_mode != 'read' else self.qproj[li](d)

    def _tap(self, li, o):
        """Layer li's ContextCNN output, through the --tap projection (identity when off).
        The result is both what the register stores and what leaves the layer:

            o -> tap -> a ,   a -> register
                        a -> deep_proj -> next layer   (decoder.proj on the last layer)

        which is the two-1x1-in-series arrangement with the register tapped between them --
        the second 1x1 being the one already on the upward path rather than a module of its
        own. A separate second conv there would be exactly redundant: two 1x1s in series with
        no nonlinearity between compose to a single 1x1, so folding it into deep_proj costs
        nothing representable and halves the added parameters.

        Both consumers of `a` matter. The register is detached, so on its own it would leave
        these weights with no gradient (that is what --qproj write runs into); the upward path
        is not, so the tap trains through it.

        The register therefore holds a dense signed embedding of the layer's output rather
        than the sparse ReLU output -- which is the part that changes what the model can
        remember, since --accumulate averages it and the next step adds it back in."""
        if self.tap is None:
            return o
        a = self.tap[li](o)
        return a if self.tap_norm is None else self.tap_norm[li](a)

    def _clip_state(self, outs):
        """--clip_dff: bound the DFF state's magnitude, per layer and per batch row.

        Rescales instead of clamping element-wise, so what the state *encodes* -- the pattern
        across channels and the SxS grid -- is untouched and only its overall scale is capped.
        Element-wise clamping would flatten the peaks against the ceiling and distort the
        representation; this is the same argument that makes gradient-norm clipping preferable
        to clamping individual gradients.

        Rows are clipped independently because the CNN never mixes the batch dimension, so one
        row running away must not rescale its neighbours.

        Only the stored state is clipped. The value travelling up the stack and into the
        decoder is the layer output itself, which is left alone -- this bounds the feedback
        loop without altering the feed-forward path."""
        c = self.clip_dff
        if not c:
            return outs
        out = []
        for d in outs:
            m = d.detach().abs().amax(dim=(1, 2, 3), keepdim=True)
            out.append(d * torch.clamp(c / m.clamp_min(1e-12), max=1.0))
        return out

    def _tok_grid(self, byte_idx):
        B   = byte_idx.shape[0]
        tok = self.tok_embed(byte_idx)                             # [B, c_text]
        return tok.view(B, self.c_text, 1, 1).expand(-1, -1, self.S, self.S)

    def _layers(self, dff, tok_grid, clk=None, record=None):
        """Run the stack of n_layers (ContextCNN + feedback) units once.
        dff: list of n_layers tensors [B, n_hidden, S, S]. Layer 0 takes the token injection;
        each deeper layer takes the previous layer's output summed with its own DFF state,
        so a deep layer sees the current token only through the layers below it.
        clk: the DFFClock for this context (None under --clock sync). It is consumed here —
        one step of it per call — so pass the clock that belongs to the state in `dff`.
        --qproj puts a 1x1 conv either on the way out of each register (read, see _fb) or
        --tap puts one between the layer output and the
        register (see _tap), on the path the stack above takes as well.
        Returns (new_dff_list, last_layer_output [B, n_hidden, S, S]). No detach here — the
        caller detaches the returned list to bound the time horizon.

        record: if a list is passed, one {'in':…, 'out':…} dict per layer is appended, holding
        that layer's ContextCNN INPUT (the feedback sum, i.e. what the register contributes
        plus what arrives from below) and its OUTPUT (what the register will store and the
        layer above receives). --altvis draws these; nothing else uses them, and passing None
        leaves the forward pass byte-identical."""
        tok  = self.text_proj(tok_grid)        # [B, n_hidden, S, S], computed once
        if self.linout is not None:
            # ONE 1x1 per layer. `o` leaves the projection already dense and signed, and is
            # both stored in the register and handed straight to the layer above -- there is
            # no second projection on the way up, which is the whole difference from --tap.
            # Layer 0 always owns a register (--dff_every counts from it).
            x0   = self._fb(0, dff[0]) + tok
            o    = self.linout[0](self.context(x0))
            outs = [o]
            if record is not None:
                record.append({'in': x0, 'out': o})
            for li in range(self.n_layers - 1):
                x = self._fb(li + 1, dff[li + 1]) + o
                o = self.linout[li + 1](self.deep_context[li](x))
                outs.append(o)
                if record is not None:
                    record.append({'in': x, 'out': o})
        else:
            x0   = self._fb(0, dff[0]) + tok
            o    = self._tap(0, self.context(x0))
            outs = [o]
            if record is not None:
                record.append({'in': x0, 'out': o})
            for li in range(self.n_layers - 1):
                x = self._fb(li + 1, dff[li + 1]) + self.deep_proj[li](o)
                o = self._tap(li + 1, self.deep_context[li](x))
                outs.append(o)
                if record is not None:
                    record.append({'in': x, 'out': o})
        # --clock: a layer that does not write this step keeps the state it had, while still
        # passing the output it just computed up the stack -- so the decoder, which reads the
        # top layer's output, moves every step whatever the clock does.
        if clk is not None:
            outs = [clk.write(li, oi, d) for li, (oi, d) in enumerate(zip(outs, dff))]
            clk.advance()
        return self._clip_state(outs), o

    def forward(self, byte_idx, targets=None, flag=None):
        """
        byte_idx  [B] long — current token (teacher-forced: ground truth at t)
        targets   [B] long — next token (CE target), or None
        flag      [B] bool — reset DFF for these batch elements
        """
        B, dev = byte_idx.shape[0], byte_idx.device
        self._init_dff(B, dev)

        if flag is not None and flag.any():
            self.dff = [d.clone() for d in self.dff]   # clone before in-place
            # reseed just the restarting rows, via _new_dff so --init has one definition
            fresh = self._new_dff(int(flag.sum()), self.dff[0].device)
            for d, f in zip(self.dff, fresh):
                d[flag] = f
            if self.clk is not None:
                self.clk.reset(flag)     # a restarting row is back at step 0 (--clock phase)

        stack, new_ctx = self._layers(self.dff, self._tok_grid(byte_idx), self.clk)
        self.dff = [d.detach().clone() for d in stack]   # store for next step (gradient horizon = 1)

        logits = self.readout(self.decoder(new_ctx))
        loss   = F.cross_entropy(logits, targets.long()) if targets is not None else None
        if loss is not None and (self.dff_penalty or self.dff_bias):
            # Mean state, element-weighted across layers so a wide layer counts for what it
            # is rather than one layer one vote. On `stack`, which still carries the graph --
            # self.dff above is detached and would contribute nothing.
            _n = sum(d.numel() for d in stack)
            _m = sum(d.sum() for d in stack) / _n
            if self.dff_penalty:
                loss = loss + self.dff_penalty * F.relu(_m)   # one-sided: restoring force
            if self.dff_bias:
                loss = loss + self.dff_bias * _m              # two-sided: constant pull
        return logits, loss

    @torch.no_grad()
    def generate(self, prompt_ids, n_tokens, temperature=1.0):
        """Autoregressive generation seeded by prompt_ids (temperature 0 = argmax).

        Returns n_tokens tokens. An END ends a SEQUENCE, not the sample: it is kept in the
        output so callers render <ETX>, and if the budget is not yet filled the state is
        reset, the prompt fed again, and a fresh sequence appended -- exactly what the
        model does at a document boundary in training. Without this a model that has
        learned to end documents returns a few dozen tokens of a 200-token budget and the
        sample stops showing what it does mid-document. Both --generate and the in-training
        GEN line go through here, so they see the same behaviour. Capped at 20 sequences so
        a model that emits END immediately cannot spin. Returns short only on NaN/Inf."""
        self.eval()
        dev = next(self.parameters()).device
        dff = clk = None

        def _step(b):
            nonlocal dff
            bi   = torch.tensor([b], dtype=torch.long, device=dev)
            tok  = self.tok_embed(bi).view(1, self.c_text, 1, 1).expand(-1, -1, self.S, self.S)
            stack, new_ctx = self._layers(dff, tok, clk)
            dff     = [d.detach().clone() for d in stack]
            if not all(d.isfinite().all() for d in dff):
                print('generate: dff NaN/Inf')
                return None
            logits = self.readout(self.decoder(new_ctx))
            if not logits.isfinite().all():
                print('generate: logits NaN/Inf')
                return None
            return logits

        _pool = getattr(args, 'gen_pool', 'last')

        def _feed(b):
            """--datarep: one token, N steps. The logits returned are the LAST replica's by
            default -- the one that has seen the token settle longest -- or the MEAN over
            all N replicas under --gen_pool mean. At N=1 both are exactly _step().
            Everything above it therefore reads the same at any --datarep: one sample per
            token, one token per output position."""
            lg = acc = None
            for _ in range(_DATAREP):
                lg = _step(b)
                if lg is None:
                    return None
                if _pool == 'mean':
                    p = F.softmax(lg, dim=-1)          # pool PROBABILITIES, not logits
                    acc = p if acc is None else acc + p
            if _pool != 'mean':
                return lg
            # Returned as log(mean p) so every caller downstream is unchanged: they do
            # softmax(x / T), and softmax(log p / T) is p^(1/T)/Z -- the temperature applied
            # to the POOLED distribution, and exactly p at T=1. clamp keeps log(0) finite.
            return torch.log((acc / _DATAREP).clamp_min(1e-20))

        out = []
        for _ in range(20):
            # fresh state per sequence: its own dff and blend state, so generate runs locally
            dff = self._new_dff(1, dev)
            clk = self._new_writer(1, dev)
            # feed each prompt token exactly once; logits after the last one seed generation
            logits = None
            for b in prompt_ids:
                logits = _feed(b)
                if logits is None:
                    return out
            if logits is None:
                # EMPTY PROMPT (--gen_null): there is no token to inject, so the first
                # distribution is read straight off the freshly seeded state -- decode the
                # top register exactly as _step does with the layer output. Everything after
                # this is the ordinary loop: the sampled token is fed back normally.
                if not prompt_ids:
                    with torch.no_grad():
                        logits = self.readout(self.decoder(dff[-1]))
                    if not logits.isfinite().all():
                        print('generate: logits NaN/Inf from seed')
                        return out
                else:
                    return out
            while len(out) < n_tokens:
                prob = F.softmax(logits[0] / max(temperature, 1e-6), dim=-1)
                bval = torch.multinomial(prob, 1).item()
                if bval == self.end_id:
                    out.append(bval)   # keep the terminator so callers render <ETX>
                    break
                if bval != self.null_id:   # null_id is None outside byte mode: nothing filtered
                    out.append(bval)
                logits = _feed(bval)           # the sample is replicated too, like a real token
                if logits is None:
                    return out
            if len(out) >= n_tokens:
                break
        return out


# ── DFF state stats ─────────────────────────────────────────────────────────────
# The DFF state is a list of one tensor per recurrent layer. These flatten across all
# layers to report a single aggregate (element-weighted over the whole state).

def _dff_absmax(dff):
    """Max |value| across the whole per-layer DFF list (0.0 if empty/None)."""
    return max((d.abs().max().item() for d in dff), default=0.0) if dff else 0.0


def _dff_stats(dff):
    """(mean, std, absmax, zero_frac) flattened across the whole per-layer DFF list."""
    if not dff:
        return 0.0, 0.0, 0.0, 0.0
    flat = torch.cat([d.reshape(-1) for d in dff])
    return (flat.mean().item(), flat.std().item(),
            flat.abs().max().item(), (flat == 0).float().mean().item())


# ── clip builders ──────────────────────────────────────────────────────────────

# Thread-safe tally of text examples. Builder threads
# count examples/tokens and stash the most recent raw sample; the main loop drains
# both each checkpoint to report throughput and show a training-text sample.
_text_lock  = threading.Lock()
# 'sample' is the last FRAMED corpus document, 'vsample' a dict of the last undelimited
# sentence PER VOCAB POOL. They are kept apart because the two streams pull at wildly
# different rates -- 75 vocab slots take a sentence every ~12 steps while 175 corpus slots
# take a document every ~1000, so a single shared field would be vocab text essentially
# always and the corpus half of the mix would never be seen.
# vsample is per-pool rather than one field for the same reason one field is wrong across
# the two streams: with three curriculum files a single slot shows whichever pool happened
# to draw last, so math_phase1 would appear in only a third of the reports. Keyed by pool
# name, every report shows one line from EACH file.
_text_stats = {'examples': 0, 'tokens': 0, 'sample': '', 'vsample': {},
               # first few CORPUS documents, kept verbatim for the --gen_score
               # anchors. Capped: this is a fixed reference sample, not a log.
               'anchor': []}

# Passes over each corpus, published by the builder threads and read by the TEXT line.
# Same worker->main-loop channel as _text_stats, and for the same reason: the epoch counter
# lives inside worker()'s closure, but the only place it is worth reading is the throughput
# line in the training loop. 1-based and means "currently consuming pass N", matching the
# EPOCH line _next_example writes on each wrap. On an effectively infinite corpus this stays
# at 1 forever and is just noise; on a CLOSED corpus (wdef) it is the experiment's clock.
_epoch_lock  = threading.Lock()
_epoch_stats = {}
# Fractional passes over each --vocab_files pool, e.g. 812.437 = 812 complete passes and
# 44% of the next.  Separate from _epoch_stats, which stays the 1-based "consuming pass N"
# integer the EPOCH line and _epoch_report() have always printed.
_epoch_frac  = {}
# Pools kept OUT of the epoch column's mean (--vocab_framed). Written once at worker
# start-up, before any thread reads it.
_epoch_mean_exclude = set()
# --vocab_slots: pool name -> example count, published once at worker start-up. The STEP
# line's epoch_vocab column needs the DENOMINATOR of the vocab channel's own consumption,
# which otherwise lives only in worker()'s closure.
_vocab_total = {}

# ── learning-stall detector (--refresh, arXiv:2403.02473) ─────────────────────
# "When do Convolutional Neural Networks Stop Learning?" measures DATA VARIATION across
# every layer: per layer, the std of its post-convolution activations, averaged over the
# epoch's iterations, rounded to r decimals; when the SUM of the per-layer epoch-over-epoch
# differences is exactly 0 for three consecutive epochs, the network has reached its
# near-optimal capacity on that data. The paper stops training there. Here the same signal
# says "this pool is exhausted", and the response is to replace part of the pool.
#
# The trainer accumulates; the WORKER reads, because the worker is what owns the pool and
# knows where an epoch ends. Everything here is a no-op unless --refresh is set: no hooks are
# registered, so a run without it is byte-identical to one from before the flag.
_stab_lock = threading.Lock()
_stab_sum  = collections.defaultdict(float)   # layer -> sum of sampled activation stds
_stab_cnt  = collections.defaultdict(int)     # layer -> number of samples
_stab_prev = {}                               # layer -> previous epoch's ROUNDED mean
_stab_hold = [0]                              # consecutive still epochs
_stab_step = [0]                              # step counter for --refresh_sample
_stab_last = [None]                           # last closed epoch's (delta, abs delta, layers)
_stab_best = [None]                           # --refresh_mode rel: smallest abs(sum delta) yet


def _stab_register(model):
    """Forward hooks on every Conv2d in the recurrent stack. Post-convolution, pre-norm:
    with affine=False the post-norm std is 1 by construction, so the conv output is the only
    place the layer's data variation is still visible."""
    n = 0
    for name, m in model.named_modules():
        if isinstance(m, nn.Conv2d) and ('context' in name or 'deep_context' in name):
            def _hook(mod, inp, out, _k=name):
                # sampled, and detached: this must not touch the graph or the step time.
                # TRAIN MODE ONLY -- the loop runs a second forward after optimizer.step()
                # to recompute the DFF, and generation/eval run more; counting those would
                # mix distributions into one epoch mean.
                if not mod.training or _stab_step[0] % max(1, args.refresh_sample):
                    return
                v = float(out.detach().float().std())
                if math.isfinite(v):
                    with _stab_lock:
                        _stab_sum[_k] += v
                        _stab_cnt[_k] += 1
            m.register_forward_hook(_hook)
            n += 1
    print(f'--refresh: stall detector on {n} conv layers, sampled every '
          f'{args.refresh_sample} steps, r={args.refresh_r}, hold={args.refresh_hold}',
          flush=True)
    return n


def _stab_peek():
    """Detector state for the periodic TRIGGER line: the epoch-SO-FAR mean activation std,
    how many samples it rests on, and the last closed epoch's verdict. Does NOT drain the
    accumulator -- only _stab_epoch() may, or an epoch mean would be taken over a partial
    window and the deltas would compare unequal amounts of evidence."""
    with _stab_lock:
        mus = [_stab_sum[k] / _stab_cnt[k] for k in _stab_sum if _stab_cnt[k]]
        nsamp = min([_stab_cnt[k] for k in _stab_cnt], default=0)
    mu = sum(mus) / len(mus) if mus else float('nan')
    return mu, nsamp, len(mus), _stab_last[0], _stab_hold[0]


def _stab_epoch(r):
    """Close the epoch: -> (sum of per-layer deltas, n layers, mean mu, n samples per layer).
    Drains the accumulator, so each epoch's mean is over that epoch's samples only."""
    with _stab_lock:
        mus = {k: _stab_sum[k] / _stab_cnt[k] for k in _stab_sum if _stab_cnt[k]}
        nsamp = min([_stab_cnt[k] for k in _stab_cnt], default=0)
        _stab_sum.clear(); _stab_cnt.clear()
    if not mus:
        return None
    cur = {k: round(v, r) for k, v in mus.items()}
    if not _stab_prev:                      # first epoch: nothing to difference against
        _stab_prev.update(cur)
        return None
    d = sum(cur[k] - _stab_prev.get(k, cur[k]) for k in cur)
    dabs = sum(abs(cur[k] - _stab_prev.get(k, cur[k])) for k in cur)
    _stab_prev.update(cur)
    _stab_last[0] = (d, dabs, len(cur))
    return d, dabs, len(cur), sum(mus.values()) / len(mus), nsamp


def _epoch_set(name, n):
    with _epoch_lock:
        _epoch_stats[name] = n

def _epoch_frac_set(name, v):
    with _epoch_lock:
        _epoch_frac[name] = v

def _epoch_num():
    """The STEP line's `epoch` column.

    With --vocab_files active it is the MEAN number of complete passes over the curriculum
    pools, fractional, and a mean rather than the min so it does not quantise to a step
    change when one pool wraps a few thousand steps before another.  The corpus is
    effectively infinite and is deliberately excluded (see _track_corpus_epochs).

    --vocab_framed pools are EXCLUDED from the mean.  Pools are equal in SLOTS, not in
    tokens, so equal slot counts do NOT make equal epoch rates: at 10 slots each the
    ~12-token sentence files wrap every ~12k steps while the ~761-token reasoning_phase1
    wraps every ~776k, a 60x spread.  Averaging across that spread produces a number that
    describes neither group, so the mean covers the short curriculum pools only and the
    long one is reported on its own.  _epoch_report() still prints EVERY pool separately
    and fractionally, which is the honest reading when example lengths differ.

    Without vocab files it is the old reading: passes over the corpus that has wrapped LEAST,
    which for a single dataset is simply its epoch. 0 before the worker starts."""
    with _epoch_lock:
        frac = {k: v for k, v in _epoch_frac.items() if k not in _epoch_mean_exclude}
        if frac:
            return sum(frac.values()) / len(frac)
        return float(min(_epoch_stats.values())) if _epoch_stats else 0.0


def _epoch_vocab():
    """The STEP line's `epoch_vocab` column: fractional passes over the vocab stream as a
    WHOLE, i.e. every example the vocab slots have drawn divided by the size of the pool
    they draw from. With several files merged into one channel that is the number that
    describes the channel -- the per-file breakdown is still in the EPOCH line.

    Distinct from the `epoch` column, which is the MEAN of the per-file fractions: the two
    agree only when the files are the same length (vocab_phase1/2 are both 10k lines, so
    they do here). 0 before the worker starts."""
    with _epoch_lock:
        tot = sum(_vocab_total.values())
        if not tot:
            return 0.0
        return sum(_vocab_consumed.get(k, 0) for k in _vocab_total) / tot


def _epoch_report():
    """'name=pass' per dataset, e.g. 'wdef=3' or 'math_phase1=12.48,web=1'; '' before load.

    Vocab pools report the FRACTIONAL pass, corpora the integer one. A pool whose examples
    are long enough to wrap only a handful of times in a whole run (reasoning_phase1: ~5
    passes in 4M steps) sits at the integer 1 for hundreds of thousands of steps, which is
    indistinguishable from a stalled stream; the fraction shows it moving."""
    with _epoch_lock:
        return ','.join(f'{k}={_epoch_frac[k]:.2f}' if k in _epoch_frac else f'{k}={v}'
                        for k, v in sorted(_epoch_stats.items()))

def _text_tally(n_tokens, sample='', vocab=False):
    """`vocab` is the POOL NAME for a --vocab_files sentence, False for a corpus document."""
    with _text_lock:
        _text_stats['examples'] += 1
        _text_stats['tokens']   += n_tokens
        if sample:
            if vocab:
                _text_stats['vsample'][vocab if isinstance(vocab, str) else 'vocab'] = sample
            else:
                _text_stats['sample'] = sample
                if len(_text_stats['anchor']) < 24:
                    _text_stats['anchor'].append(sample)

def _text_drain():
    """Return (examples, tokens, sample) since the last drain; reset the counters.
    The sample is kept (not cleared) so a recent one is always available."""
    with _text_lock:
        e, t, s = _text_stats['examples'], _text_stats['tokens'], _text_stats['sample']
        _text_stats['examples'] = _text_stats['tokens'] = 0
    return e, t, s


def _text_peek():
    """The most recent raw training-text sample, WITHOUT touching the counters.

    Exists so the GEN block can print a TXT-SAMPLE on its own (fast) interval while the
    TEXT throughput line stays on the checkpoint interval.  _text_drain() RESETS
    examples/tokens, so calling it every --gen_interval steps would silently rescale every
    TEXT line to a tenth of the window it claims to cover.  The sample itself is safe to
    read repeatedly: builder threads overwrite it in place and the drain never clears it."""
    with _text_lock:
        return _text_stats['sample'], dict(_text_stats['vsample'])


def _sample_window(text, n=240):
    """A RANDOM window of a training document, not its opening n characters.

    A head slice is fine when documents are short, and actively misleading when they are
    not. On sebooks (whole books, mean 126k tokens) every TXT-SAMPLE showed a book's
    chapter-one opening -- never the text the model was really training on, a hundred
    thousand steps deep -- and the SAME opening repeated in report after report, because
    the stored sample only changes when a slot loads a new document and a slot holds one
    book for ~126k steps. A random offset shows where the run actually is, and makes a
    repeated document read as a repeat rather than as a stalled data pipeline.
    """
    if len(text) <= n:
        return text
    i = random.randrange(0, len(text) - n)
    return ('...' + text[i:i + n]) if i else text[:n]


def _text_anchors():
    with _text_lock:
        return list(_text_stats['anchor'])
# Each builder returns (steps, caption). A step is a 4-tuple
#   (x_byte, y_byte, img_or_None, aud_or_None)
# one entry per 100 Hz frame.

def clip_text(text):
    """One step per token: input/target are consecutive ids of [START]+text+[END].
    Tokens are raw bytes or BPE ids depending on --tokenizer; nothing downstream cares.

    --datarep N repeats each (x, y) pair N times, so the stream is the same tokens with the
    same targets, N steps each. Done HERE because this is the one place both the training
    clips and the held-out eval documents are framed -- putting it in the slot instead would
    replicate training and leave eval scoring a different stream. _ClipSlot needs no change:
    its is_start() is pos == 0, which is still the first replica of the first pair, so the
    state resets once per document rather than once per replica."""
    full = [_tokenizer.start_id] + _tokenizer.encode(text) + [_tokenizer.end_id]
    steps = [(full[i], full[i + 1]) for i in range(len(full) - 1)]
    if _DATAREP > 1:
        steps = [pair for pair in steps for _ in range(_DATAREP)]
    return steps, text


# ── dataset loading ────────────────────────────────────────────────────────────

# The Pile: EleutherAI/pile itself is an empty shell -- the 2023 DMCA takedown left it with
# a README and a loading script pointing at dead the-eye.eu mirrors, and datasets>=3 dropped
# script support, so it cannot be loaded at all. 'pile' therefore points at EleutherAI's own
# deduplicated re-release (1650 parquet shards, text column, no meta), and 'pile_nc' at the
# community copy with the copyrighted subsets (Books3 etc.) removed. Both are the corpus the
# pythia* tokenizers were trained on, so they pair with --tokenizer pythia14m..pythia160m.
_TEXT_DATASETS = {
    'tiny':    ('roneneldan/TinyStories', None, 'train', 'text'),
    'c4':      ('allenai/c4',            'en', 'train', 'text'),
    'web':     ('Skylion007/openwebtext', None, 'train', 'text'),
    'brt':     ('allenai/big-reasoning-traces', 'DeepSeek', 'train', 'text'),
    'dolma3':  ('allenai/dolma3_mix-150B-1025', None, 'train', 'text'),
    's1k':     ('simplescaling/s1K',      None, 'train', None),
    'pile':    ('EleutherAI/the_pile_deduplicated', None, 'train', 'text'),
    # LittleCurriculum: 2546 parquet shards of (id, text), ~74k rows each -- far too large to
    # fetch whole, and it needs no subset file list because it STREAMS: 250 slots at one token
    # per step is ~24 KB/s, so the network is never the bottleneck. Ordinary framed corpus,
    # so <STX>/<ETX> and the usual prompting apply.
    'littlec': ('littlelearner/LittleCurriculum', None, 'train', 'text'),
    'pile_nc': ('monology/pile-uncopyrighted', None, 'train', 'text'),
    # synth has no repo: examples are generated on the fly by --teacher. The tuple exists so
    # _build_clip finds the 'text' column and _split_for_name resolves, exactly as for a
    # real corpus -- everything downstream of the worker is unchanged.
    'synth':   (None, None, 'train', 'text'),
    # ── fifth-grade / reasoning corpora ──────────────────────────────────────────
    # Chosen because they are simple AND explanatory. Filtering openwebtext by reading
    # level does NOT get you here: measured over 3000 documents its median Flesch-Kincaid
    # grade is 10.3, only 3.9% fall at grade <=6, and what survives that filter is blog
    # chatter (a Disney donut review, a DIY lamp build) -- simple language, no reasoning.
    # Readability and reasoning are anti-correlated on raw web text.
    'swiki':   ('wikimedia/wikipedia', '20231101.simple', 'train', 'text'),
    'fwedu':   ('HuggingFaceFW/fineweb-edu', 'sample-10BT', 'train', 'text'),
    # The SAME 10BT sample of the SAME crawl as fwedu, but WITHOUT the edu classifier:
    # HuggingFaceFW/fineweb sample-10BT is 15 parquet files of 2.15 GB (~10B tokens, ~667M
    # per file), the unfiltered FineWeb pipeline output. Registered so 'raw web' and
    # 'edu-filtered web' can be compared with the filter as the only variable -- fwedu is
    # this corpus after the classifier, and smolfwedu is fwedu after exact dedup. Too large
    # to materialize casually (32 GB), so pair it with --streaming.
    'fineweb': ('HuggingFaceFW/fineweb', 'sample-10BT', 'train', 'text'),
    # ONE CRAWL of fineweb rather than the cross-crawl 10BT sample. FineWeb's MinHash
    # dedup runs WITHIN a crawl and not across them, so a single dump is already clean of
    # near-duplicates while a sample drawn over 110 crawls is not -- the same page recrawled
    # in 2023 and 2025 survives as two documents there. CC-MAIN-2025-26 is the newest dump
    # (250 shards, 450 GB); 18 shards is ~10B tokens, matching sample-10BT's budget with the
    # duplicate structure removed. In _HUB_SUBSET, so only the fetched shards are read.
    'fwcrawl': ('HuggingFaceFW/fineweb', 'CC-MAIN-2025-26', 'train', 'text'),
    # cosmo is cosmopedia/stories UNFILTERED as of 2026-08-29. It previously kept only
    # audience == 'young_children' (26.3% of rows, the same rows format == 'story_children'
    # selects) via _fmt_cosmo, which has been REMOVED. BACKWARD COMPATIBILITY IS BROKEN ON
    # PURPOSE: every 'cosmo' number recorded before that date -- f1_grade5_1b, c1_sense_1b,
    # and their EVAL lines -- was measured on the young_children subset and is NOT
    # comparable to anything measured after. Unfiltered, the config is 73.7% 'general'
    # (median Flesch-Kincaid grade 11.5 vs 9.4) and spans five formats: story_children
    # 26.3, story_life_lessons 25.7, story_reddit 25.3, story_morality 11.5,
    # story_forums 11.2 -- so it now carries a conversational/forum register too.
    'cosmo':   ('HuggingFaceTB/cosmopedia', 'stories', 'train', 'text'),
    # The BROAD cosmopedia config: 10.3M examples / 58.7GB, seeded from open web samples
    # rather than one source type, which is what makes it general-domain where every other
    # config is a genre. Internally general 73% / college_students 27%, and blogpost 62% /
    # textbook_academic 27% / textbook_narrative 5% / wikihow 5%. web_samples_v1 is the same
    # idea and slightly larger (12.4M / 69.1GB); v2 is the refined seeding, so it is the one
    # registered. Far too large to materialize -- always pair with --streaming.
    'cosmoweb': ('HuggingFaceTB/cosmopedia', 'web_samples_v2', 'train', 'text'),
    # smollm-corpus: the two text subsets SmolLM was trained on. 'smolcosmo' is
    # cosmopedia-v2, the regenerated synthetic textbook/story corpus (28B tokens, better
    # prompts and a wider audience mix than cosmopedia v1, which is what 'cosmo'/'cosmoweb'
    # above still point at); 'smolfwedu' is fineweb-edu-dedup, fineweb-edu with exact
    # dedup applied. Both carry a plain 'text' column.
    # Registered in _HUB_SUBSET, NOT resolved on demand: the two configs are 672 GB (550 +
    # 122), and load_dataset would try to resolve the whole repo. Fetch a spread subset of
    # shards into the HF cache first; the longest run here reads ~1 GB of text.
    # nampdn-ai/tiny-strange-textbooks: 4.4 GB of synthetic textbook-style prose in one
    # 'text' column, ~1B tokens. Small enough to download whole (no _HUB_SUBSET needed) and
    # small enough that a 4M-step run at batch 250 -- 1e9 tokens -- is roughly ONE pass, so
    # unlike fwedu the epoch column on the STEP line is a real clock here rather than
    # pinned at 1. NOT named 'tiny*': that prefix is TinyStories in this table.
    'strangetb': ('nampdn-ai/tiny-strange-textbooks', None, 'train', 'text'),
    # nampdn-ai/tiny-textbooks: 399k train / 21k test rows. Trains on the 'textbook' column,
    # NOT 'text' -- same call as finephrase above: 'text' is the SOURCE snippet the row was
    # generated from (refinedweb/minipile, mean 219 tokens, visibly scraped web text) while
    # 'textbook' is the generated textbook prose the dataset exists to provide (mean 622
    # tokens, median 605). Short-form, so preroll and held-out eval both apply normally.
    'tinytb':    ('nampdn-ai/tiny-textbooks', None, 'train', 'textbook'),
    # Same repo as tinytb; the column is None because _fmt_tinytb_pair builds the text from
    # two columns, the way s1k and wdef do.
    'tinytbpair': ('nampdn-ai/tiny-textbooks', None, 'train', None),
    # Nelathan/standardebooks: 1233 public-domain books, whole book per row. 0.43 GB,
    # ~175M tokens. UNLIKE EVERY OTHER CORPUS HERE THE DOCUMENTS ARE ENORMOUS -- mean
    # 126k tokens, median 107k, max 659k -- so a slot holds one book for ~126k steps and
    # sees only ~32 of them in a 4M-step run. The <ETX> document reset therefore fires
    # ~100x more rarely than on fwedu (mean 1080 tokens), which is a real change to the
    # training signal, not just to the text. --preroll still terminates promptly: it waits
    # for the SHORTEST clip of the batch, and the shortest of 250 draws from this corpus is
    # a few thousand tokens, not 126k.
    'sebooks':   ('Nelathan/standardebooks', None, 'train', 'text'),
    'smolcosmo': ('HuggingFaceTB/smollm-corpus', 'cosmopedia-v2',     'train', 'text'),
    'smolfwedu': ('HuggingFaceTB/smollm-corpus', 'fineweb-edu-dedup', 'train', 'text'),
    # HuggingFaceTB/dclm-edu: DCLM-baseline re-filtered with the FineWeb-Edu classifier
    # (edu_int_score >= 2 kept), 1769 parquet shards of ~2.9 GB each -- ~5 TB, so it is in
    # _HUB_SUBSET like the smollm configs and a spread subset is fetched by hand. Plain
    # 'text' column; the other columns (edu_score, url, language) are metadata we ignore.
    # This is REAL WEB TEXT that an education classifier liked, which is what it contributes
    # to a mix whose other two members are synthetic prose (smolcosmo) and a differently
    # filtered slice of the SAME web (smolfwedu, fineweb-edu-dedup): the three are not
    # independent samples, they are three filters over overlapping crawls.
    'dclmedu':   ('HuggingFaceTB/dclm-edu', None, 'train', 'text'),
    # finephrase: reasoning-shaped generations over fineweb-edu documents. The corpus we
    # train on is rollout_results, NOT the `text` column -- `text` is the source document
    # verbatim, i.e. fineweb-edu, which --dataset fwedu already provides. See _fmt_finephrase.
    'fpfaq':   ('HuggingFaceFW/finephrase', 'faq',  'train', 'text'),
    'fpmath':  ('HuggingFaceFW/finephrase', 'math', 'train', 'text'),
    # finephrase 'tutorial': explanatory how-to / popular-science rewrites of fineweb-edu
    # documents. Registered for the k1 curriculum stage, which needs AI-generated LANGUAGE
    # AND GENERAL KNOWLEDGE with no math and no code -- fpmath and brt are both disqualified
    # on that rule, which otherwise leaves only two AI sources. Only ONE shard (67,000 rows,
    # ~27M tokens) is on disk, enough for roughly one pass at this mix weight.
    'fptut':   ('HuggingFaceFW/finephrase', 'tutorial', 'train', 'text'),
    # ── closed, finite corpus: a memorization probe, not a sample of a distribution ──
    # 466,670 headwords, 1.72 senses each, ~43 tokens per rendered entry -> ONE EPOCH IS
    # ~20M tokens (80k steps at batch 250). Every other corpus here is effectively infinite
    # at our budget and is seen once; this one is meant to be repeated until it is learned,
    # which is the point (see --wdef_format, and _make_iter's exact-shuffle branch).
    # The payload is 'definitions', a LIST of strings -- there is no 'text' column, so the
    # entry is rendered by _fmt_wdef and the column name here is documentation only.
    'wdef':    ('MongoDB/english-words-definitions', None, 'train', 'definitions'),
    # Authored locally, not downloaded: --bdict_file, one document per line. The tuple's
    # repo is None for the same reason 'synth' is -- _init_one_dataset intercepts the name
    # before the repo is read -- but the 'text' column and 'train' split still have to be
    # here so _corpus_text and _split_for_name resolve exactly as for a hub corpus.
    'bdict':   (None, None, 'train', 'text'),
    # Local JSONL, --data_file. repo None for the same reason bdict's is: _init_one_dataset
    # intercepts the name before the repo is read. Split and column still have to be here so
    # _corpus_text and _split_for_name resolve exactly as for a hub corpus.
    'file':    (None, None, 'train', 'text'),
    # BabyLM 2026 Strict: six plain-text files (bnc_spoken, childes, gutenberg,
    # open_subtitles, simple_wiki, switchboard), ~543 MB, fetched from the hub as TEXT rather
    # than parquet. repo None for the same reason 'file' and 'bdict' are: _init_one_dataset
    # builds it locally and nothing downstream needs to know the difference.
    'babylm':  (None, None, 'train', 'text'),
}

# Repos where only a SUBSET of the files is on disk, loaded from the hub cache directly.
# finephrase is 4.69 TB across 27,104 parquet files: it does not fit, and load_dataset()
# cannot even enumerate it -- streaming yielded no row in 10 minutes because HF resolves
# the entire file list first. Pointing 'parquet' at the downloaded snapshot files skips
# resolution entirely and uses exactly what was fetched. ~33M tokens of rollout per file,
# so a few dozen files exceed a 1B-token run.
_HUB_SUBSET = {
    'smolcosmo': ('HuggingFaceTB/smollm-corpus', 'cosmopedia-v2'),
    'smolfwedu': ('HuggingFaceTB/smollm-corpus', 'fineweb-edu-dedup'),
    # dclm-edu's shards live under data/ rather than a config directory, so 'data' is the
    # subdirectory _hub_subset_files globs -- not a config name (the repo has none).
    'dclmedu': ('HuggingFaceTB/dclm-edu', 'data'),
    # fineweb's 10BT sample lives under sample/10BT/, so that path is what gets globbed --
    # a subdirectory, not a config name, even though 'sample-10BT' IS a real config of the
    # repo. Going through _HUB_SUBSET rather than load_dataset(repo, 'sample-10BT') keeps
    # the read on the 15 files already in the cache: no repo resolution, no network, and
    # with --streaming no arrow build either (the parquet loader streams local files).
    'fineweb': ('HuggingFaceFW/fineweb', 'sample/10BT'),
    'fwcrawl': ('HuggingFaceFW/fineweb', 'data/CC-MAIN-2025-26'),
    'fpfaq':  ('HuggingFaceFW/finephrase', 'faq'),
    'fpmath': ('HuggingFaceFW/finephrase', 'math'),
    'fptut':  ('HuggingFaceFW/finephrase', 'tutorial'),
}


def _babylm_files():
    """The BabyLM-2026-Strict .txt files in the hub cache, SORTED -- the order is the
    curriculum under --no-shuffle, and the block partition under --blocks."""
    home = os.environ.get('HF_HOME') or os.path.expanduser('~/.cache/huggingface')
    root = os.path.join(home, 'hub',
                        'datasets--BabyLM-community--BabyLM-2026-Strict', 'snapshots')
    files = sorted(glob.glob(os.path.join(root, '*', '*.txt')))
    if not files:
        raise SystemExit('babylm: no .txt files under HF_HOME for '
                         'BabyLM-community/BabyLM-2026-Strict -- fetch it first with '
                         "snapshot_download('BabyLM-community/BabyLM-2026-Strict', "
                         "repo_type='dataset')")
    return files


def _hub_subset_files(name):
    repo, cfg = _HUB_SUBSET[name]
    home = os.environ.get('HF_HOME') or os.path.expanduser('~/.cache/huggingface')
    root = os.path.join(home, 'hub', 'datasets--' + repo.replace('/', '--'), 'snapshots')
    return sorted(glob.glob(os.path.join(root, '*', cfg, '*.parquet')))


_FP_REFUSALS = ('no answer', 'no table', 'no question', 'none', 'n/a', 'no faq')


def _fmt_finephrase(ex):
    """The GENERATED rollout, not the source document.

    ~99% of rows carry a usable generation (median ~1.9k chars for faq, ~1.0k for math);
    the rest are refusals the generator emitted when the source had nothing to work with
    ('No answer', 'No table'). Returning '' skips the row, the contract _fmt_s1k uses."""
    rr = ex.get('rollout_results')
    if not isinstance(rr, (list, tuple)) or not rr:
        return ''
    first = rr[0]
    txt = (first.get('text') if isinstance(first, dict) else None) or ''
    txt = txt.strip()
    if len(txt) < 40 or txt.lower().startswith(_FP_REFUSALS):
        return ''
    return txt

# Corpora that ship a TRAIN SPLIT ONLY. There is no held-out set to point --eval_corpora at,
# and slicing (train[-3000:]) cannot be streamed. So the split is made by HASHING the
# document: a fixed 1/_HOLDOUT_MOD of documents is reserved for eval and skipped by the
# training worker. Deterministic, streaming-compatible, and disjoint regardless of shuffle
# order or --seed -- none of which is true of "take the first N documents".
# Corpora with a real held-out split (tiny/c4/pile/web) are NOT hashed: they keep the exact
# sets every earlier number in PLAN.txt was measured on.
_HASH_HOLDOUT = {'swiki', 'fwedu', 'fineweb', 'fwcrawl', 'cosmo', 'cosmoweb', 'fpfaq', 'fpmath', 'fptut',
                 'smolcosmo', 'smolfwedu', 'strangetb', 'sebooks', 'dclmedu', 'babylm',
                 'littlec'}
_HOLDOUT_MOD = 32                       # ~3.1% held out. Sized by the SCAN COST of building
                                        # the eval set, not by statistics: the filters
                                        # compound. cosmo keeps 26.5% (audience) x 1/MOD
                                        # x ~13% (>= _EVAL_MINLEN tokens), so at MOD=256
                                        # assembling 400 documents meant scanning ~3M rows.
                                        # At 32 it is ~375k. Losing 3.1% of training data
                                        # is immaterial next to a corpus of millions.


def _is_heldout(text):
    # crc32 of a prefix: cheap, stable across processes and Python versions (unlike hash(),
    # which is randomised per process by PYTHONHASHSEED and would silently reshuffle the
    # split on every restart).
    return zlib.crc32(text[:512].encode('utf-8', 'ignore')) % _HOLDOUT_MOD == 0

# --eval: the held-out split to score, for the corpora that have one. A plain string is a
# split of the training repo itself; a (repo, config, split) triple is a held-out set that
# lives in a different repo, which is how the Pile ships its validation split -- neither
# pile re-release carries one, so both score the Pile's own official validation set.
# Anything missing here falls back to the training split in _TEXT_DATASETS, with a warning
# -- that number is a training loss, not a validation loss.
_EVAL_SPLITS = {
    # ships a genuine test split (21k rows), so there is nothing to hash out of training
    'tinytb':  'test',
    'tinytbpair': 'test',
    'tiny':    'validation',
    'c4':      'validation',
    # openwebtext ships no validation split. train[-3000:] is the tail exp/score.py,
    # exp/ngram.py and exp/pythia_ref.py all hold out, and every web number in PLAN.txt's
    # reference table is measured on it. Without this line --eval_corpora web would score
    # the TRAINING split and silently report a training loss as a held-out one.
    'web':     'train[-3000:]',
    'pile':    ('mit-han-lab/pile-val-backup', None, 'validation'),
    'pile_nc': ('mit-han-lab/pile-val-backup', None, 'validation'),
}

# Datasets with no single text column: the example is rendered to one string here.
# s1K (https://huggingface.co/datasets/simplescaling/s1K) is 1000 curated reasoning
# examples with columns question / thinking_trajectories (list of traces, one per
# teacher sample) / attempt (the final written answer) / solution (reference answer).
# Rendered in the same <think>/<answer> shape brt's text column uses, so a
# --mix "brt:...,s1k:..." teaches one consistent reasoning format.

def _fmt_s1k(ex):
    traj = ex.get('thinking_trajectories') or []
    think = (traj[0] if traj else '') or ''
    # 'attempt' is the teacher's written-out answer; fall back to the reference solution
    answer = (ex.get('attempt') or ex.get('solution') or '').strip()
    q = (ex.get('question') or '').strip()
    if not q or not (think.strip() or answer):
        return ''
    return f'{q}<think>\n{think.strip()}\n</think>\n<answer>\n{answer}\n</answer>'


_BD_ABBREV = ('Mr.', 'Mrs.', 'Ms.', 'Dr.', 'St.')

def _split_sentences(text):
    """Split one bdict line body into sentences, for --bdict_split.

    Two things defeat a plain split on [.!?]: the abbreviation HEADWORDS this corpus
    defines ('Mr.', 'Mrs.', 'Ms.') -- "Mr. Johnson teaches math." is ONE sentence -- and
    quoted dialogue, where `"Great job!" he shouted.` would break at the exclamation mark
    and leave `he shouted.` as its own "sentence". Abbreviations are masked before the
    split; a fragment that begins lower-case is a dialogue tag and is merged back.

    A boundary is TERMINAL PUNCTUATION OPTIONALLY FOLLOWED BY A CLOSING QUOTE, then space.
    Both halves of that matter. Without the quote a sentence ending in a quotation runs into
    the next one (`with "Dear friend." His grandmother...`, exactly one line of e3: 'dear').
    But splitting after ANY quote is wrong the other way: `"No candy before dinner," Mom
    reminded him` has a COMMA before the quote and is one sentence, and 'Mom' is capitalised
    so the lower-case merge cannot rescue it. Matching [.!?] before the optional quote keeps
    both cases right."""
    t = text
    for i, a in enumerate(_BD_ABBREV):
        t = t.replace(a, f'\x00{i}\x00')
    # mark boundaries, then split on the marker, so the closing quote stays on its sentence
    t = re.sub(r'([.!?]["\']?)\s+', '\\1\x01', t)
    out = []
    for part in t.split('\x01'):
        for i, a in enumerate(_BD_ABBREV):
            part = part.replace(f'\x00{i}\x00', a)
        part = part.strip()
        if not part:
            continue
        if out and part[:1].islower():
            out[-1] = out[-1] + ' ' + part
        else:
            out.append(part)
    return out


def _fmt_wdef(ex):
    """One dictionary entry. 'definitions' is a list of senses, not a string.

    --wdef_format term (default) renders the headword and its numbered senses; a single-sense
    entry is left unnumbered so the common case reads like a dictionary line rather than a
    one-item list. --wdef_format defs drops the headword and emits the senses alone.
    ~0.05% of rows carry an empty definition list; '' skips them, the contract _fmt_s1k uses."""
    defs = [d.strip() for d in (ex.get('definitions') or []) if d and d.strip()]
    if not defs:
        return ''
    if args.wdef_format == 'defs':
        return '\n'.join(defs)
    term = (ex.get('term') or '').strip()
    if not term:
        return ''
    if len(defs) == 1:
        return f'{term}\n{defs[0]}'
    return term + '\n' + '\n'.join(f'{i}. {d}' for i, d in enumerate(defs, 1))


# cosmo has NO entry here any more: _fmt_cosmo (the audience == 'young_children' filter)
# was removed 2026-08-29, so cosmo now reads its 'text' column like any other corpus.
def _fmt_tinytb_pair(ex):
    """tiny-textbooks SOURCE then LESSON in one example: text + '\n\n' + textbook.

    The corpus is a rewrite pair -- `text` is the raw web snippet an entry was built from
    (~600 chars, scraped and fragmentary) and `textbook` is the synthetic lesson generated
    FROM it (~3000 chars, titled and sectioned). vla.py's 'tinytb' reads the lesson alone, so
    the model never sees what the lesson was written about. Concatenated, one framed example
    is <STX> raw source, then the lesson derived from it <ETX>, and the transition from messy
    source to structured exposition falls inside a single document -- which, for a model whose
    state carries across the whole example, is the part worth having.

    A blank line between them, not a marker: the boundary is a paragraph break in ordinary
    text, which is what the tokenizer and the model already know how to read. Entries missing
    either half are dropped -- half a pair is just 'tinytb' or raw web text under a name that
    claims otherwise."""
    raw  = (ex.get('text') or '').strip()
    book = (ex.get('textbook') or '').strip()
    return f'{raw}\n\n{book}' if raw and book else ''


_TEXT_FORMAT = {'s1k': _fmt_s1k, 'wdef': _fmt_wdef, 'tinytbpair': _fmt_tinytb_pair,
                'fpfaq': _fmt_finephrase, 'fpmath': _fmt_finephrase,
                'fptut': _fmt_finephrase}

# A dataset prepared on local disk takes precedence over the hub repo. dolma3 must be
# prepared this way (see dolma3_prep.py): the hub shards are topic-partitioned and
# per-source schemas differ, so streaming them trains on one topic at a time and loading
# them non-streaming fails to cast. dolma3_prep.py rewrites the corpus into text-only
# parquet parts that are each a uniform random sample of the whole corpus.
_LOCAL_DIRS = {'dolma3': './dolma3_text'}


def _local_files(name):
    d = _LOCAL_DIRS.get(name)
    return sorted(glob.glob(os.path.join(d, '*.parquet'))) if d else []


def _split_for_name(name):
    return _TEXT_DATASETS[name][2] if name in _TEXT_DATASETS else 'train'


_SHARD_EXTS = ('.parquet', '.jsonl.zst', '.json.zst', '.jsonl.gz', '.jsonl')


def _shard_files(hf, cfg, n):
    """First n train shard paths in dataset repo `hf` (config subdir `cfg` if the repo is
    multi-config). Parquet plus the compressed-jsonl layouts, since pile_nc ships
    train/NN.jsonl.zst and --shards is what keeps a 200GB+ corpus off the disk. Empty list
    if nothing matches, in which case the caller loads the whole repo."""
    from huggingface_hub import HfApi
    sib = [s.rfilename for s in HfApi().repo_info(hf, repo_type='dataset').siblings]
    par = sorted(f for f in sib if f.endswith(_SHARD_EXTS) and 'train' in f)
    if cfg:                                       # multi-config repo: keep only this config
        par = [f for f in par if f'/{cfg}/' in f or f.startswith(f'{cfg}/')]
    return par[:n]


# ── synthetic corpus (--dataset synth) ────────────────────────────────────────
# Pre-pretraining on CLEAN text before real data: a pretrained LLM writes the corpus, so
# phase 1 sees fluent, well-formed English with none of the boilerplate, markup, encoding
# damage or truncated fragments a web/Pile crawl carries.  Phase 2 then continues on real
# text (--load the phase-1 checkpoint, --dataset pile).
#
# THREE THINGS THIS GOT WRONG FIRST, all measured, all now handled:
#  1. An EMPTY-STRING prompt does not batch.  transformers' text-generation pipeline
#     collapses ['']*16 to ONE result -- 16 requests in, 1 sequence out, silently.  The null
#     prompt here is the tokenizer's eos/bos marker ('<|endoftext|>' for gpt2), which is a
#     real token, batches correctly, and is what GPT-2 saw at document starts in training.
#  2. GPT-2 emits eos early.  Asked for 750 tokens it stopped at ~157, so lengths would have
#     been whatever the teacher felt like, not the requested 500-1000.  eos is suppressed and
#     min_new_tokens is set, which forces the length.
#  3. Decoder-only models need LEFT padding.  Right padding corrupts generation; the
#     tokenizer is constructed with padding_side='left' rather than patched afterwards,
#     because the pipeline keeps its own reference.
#
# Diversity comes from temperature/top-k/top-p alone (the prompt is constant), so those are
# the knobs that matter.  Measured 64/64 unique openings at the defaults.


class SyntheticCorpus:
    """Infinite stream of teacher-generated documents, shaped like an HF dataset row.

    Thread-safe: the worker runs --workers builder threads and they share one teacher, so
    generation is serialised under a lock and handed out from a buffer.  One generate() call
    costs the same wall time whether it fills 1 request or --teacher_batch of them, so
    batching is what keeps the teacher ahead of the trainer."""

    def __init__(self, teacher, batch, temp, topk, topp, lo, hi, device, seed=0,
                 rep_penalty=1.15):
        self.teacher, self.batch = teacher, max(1, batch)
        self.temp, self.topk, self.topp, self.rep = temp, topk, topp, rep_penalty
        self.lo, self.hi = lo, hi
        self.device = device
        self.rng = random.Random(seed)
        self._pipe = None
        self._buf = []
        self._lock = threading.Lock()

    def _ensure(self):
        if self._pipe is not None:
            return
        import torch as _t
        from transformers import pipeline, AutoTokenizer
        dev = self.device
        tok = AutoTokenizer.from_pretrained(self.teacher, padding_side='left')
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        kw = {}
        if str(dev).startswith('cuda'):
            kw = dict(device=0, dtype=_t.float16)
        else:
            kw = dict(device=-1)
        self._pipe = pipeline('text-generation', model=self.teacher, tokenizer=tok, **kw)
        self._eos = tok.eos_token_id
        self._null = tok.eos_token or tok.bos_token or '\n'
        print(f'synth: teacher {self.teacher} on {dev}, null prompt {self._null!r}, '
              f'lengths {self.lo}-{self.hi}, batch {self.batch}', flush=True)

    def _fill(self):
        self._ensure()
        # one target length per example; generate to the longest and truncate each to its
        # own, so lengths are genuinely uniform rather than constant within a batch
        tgts = [self.rng.randint(self.lo, self.hi) for _ in range(self.batch)]
        want = max(tgts)
        out = self._pipe([self._null] * self.batch, max_new_tokens=want,
                         min_new_tokens=want, do_sample=True, temperature=self.temp,
                         top_k=self.topk, top_p=self.topp, repetition_penalty=self.rep,
                         pad_token_id=self._eos, suppress_tokens=[self._eos],
                         return_full_text=False, batch_size=self.batch)
        tk = self._pipe.tokenizer
        for o, n in zip(out, tgts):
            txt = o[0]['generated_text'] if isinstance(o, list) else o['generated_text']
            ids = tk.encode(txt)[:n]
            if ids:
                self._buf.append(tk.decode(ids))

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            if not self._buf:
                self._fill()
            # pop(0), not pop(): documents must come out in generation order, or the cached
            # eval set's first N are a reversed tail of each batch and "first 400 of 500"
            # stops equalling a 400-document set.
            return {'text': self._buf.pop(0)}


# The synthetic HELD-OUT set is generated ONCE and cached to disk, never regenerated.
# vla.py's --eval_interval, exp/score.py and exp/reach.py all read the same file, so an EVAL
# curve reflects the weights alone and a checkpoint scored today is comparable to one scored
# next week.  Regenerating per call would make every number a fresh sample of the teacher.
# The filename carries everything that changes the distribution, so altering the teacher or
# the length range produces a DIFFERENT file rather than silently reusing the old one.
SYNTH_EVAL_DIR = './synth_eval'
SYNTH_EVAL_SEED = 987654321          # fixed and distinct from any training seed


def synth_eval_file(teacher, n, lo, hi):
    slug = teacher.replace('/', '_')
    return os.path.join(SYNTH_EVAL_DIR, f'{slug}.{n}.{lo}-{hi}.jsonl')


SYNTH_EVAL_BATCH = 16                # PINNED, see below. Small on purpose: generating the
                                     # eval set spins up a SECOND teacher pipeline while the
                                     # training one is still resident, and its KV cache is
                                     # ~110MB per batch row at 750 tokens. At 64 that is
                                     # ~1.8GB landing on a GPU already at 22.1/24.5GB, i.e.
                                     # an OOM at the first eval -- two hours into a run, and
                                     # one the supervisor would faithfully restart into
                                     # again at every subsequent eval.


def ensure_synth_eval(teacher, n, lo, hi, batch, temp, topk, topp, device, rep=1.15):
    """Path to the cached synthetic held-out set, generating it on first use.

    REPRODUCIBILITY.  The filename keys only (teacher, n, lo, hi), so everything else that
    changes the content has to be pinned here or two runs produce different held-out sets
    under the same name:
      * torch's global RNG drives do_sample, and SyntheticCorpus seeds only its own length
        picker -- so without the manual_seed below the set was NOT reproducible across
        processes at all, merely stable once written.
      * generation batch size changes how the RNG stream is consumed, so --teacher_batch
        would leak into the content.  Eval generation therefore ignores it and uses
        SYNTH_EVAL_BATCH.
    Content now depends only on (teacher, n, lo, hi, temp, topk, topp, SYNTH_EVAL_SEED),
    which also makes the first 400 documents of a 500-document set identical to a
    400-document set -- so --eval_docs can be varied without changing which documents are
    scored."""
    path = synth_eval_file(teacher, n, lo, hi)
    if os.path.exists(path):
        return path
    os.makedirs(SYNTH_EVAL_DIR, exist_ok=True)
    print(f'synth eval: generating {n} held-out documents -> {path}', flush=True)
    torch.manual_seed(SYNTH_EVAL_SEED)
    corpus = SyntheticCorpus(teacher, SYNTH_EVAL_BATCH, temp, topk, topp, lo, hi, device,
                             seed=SYNTH_EVAL_SEED, rep_penalty=rep)
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        for i in range(n):
            f.write(json.dumps({'text': next(corpus)['text']}) + '\n')
            if (i + 1) % 100 == 0:
                print(f'  synth eval: {i+1}/{n}', flush=True)
    os.replace(tmp, path)              # atomic: a killed run must not leave a partial set
    # Release the eval teacher immediately. In a TRAINING process the corpus teacher is still
    # loaded and about to be used again, so leaving a second copy of the model plus its KV
    # cache in the allocator costs headroom for the whole run, not just this call.
    del corpus
    try:
        torch.cuda.empty_cache()
    except Exception:
        pass
    return path


def _corpus_text(name, example):
    """The training text of one raw example, after any per-corpus filter/render.

    ONE definition, used by both the training worker and the held-out eval builder. They
    used to derive it separately, which meant cosmo's eval set was drawn from the whole
    corpus while training saw only the audience-filtered subset -- scoring a distribution
    the model was never trained on."""
    fmt = _TEXT_FORMAT.get(name)
    if fmt is not None:
        return fmt(example) or ''
    col = _TEXT_DATASETS[name][3] if name in _TEXT_DATASETS else 'text'
    return example.get(col, example.get('text', '')) or ''


def _init_one_dataset(name, streaming, shards=None):
    from datasets import load_dataset
    if name in _HUB_SUBSET:
        files = _hub_subset_files(name)
        if not files:
            raise SystemExit(f'{name}: no downloaded parquet files found under HF_HOME for '
                             f'{_HUB_SUBSET[name][0]} [{_HUB_SUBSET[name][1]}]. Fetch a '
                             f'subset first -- this repo is too large to resolve on demand.')
        if shards:
            files = files[:shards]
        print(f'{name}: {len(files)} local parquet file(s) from the hub cache', flush=True)
        return load_dataset('parquet', data_files={'train': files}, streaming=streaming)
    if name == 'synth':
        return SyntheticCorpus(args.teacher, args.teacher_batch, args.teacher_temp,
                               args.teacher_topk, args.teacher_topp, args.synth_min,
                               args.synth_max, args.teacher_device or args.device,
                               seed=args.seed, rep_penalty=args.teacher_rep_penalty)
    if name == 'file':
        path = args.data_file
        if not os.path.exists(path):
            raise SystemExit(f'--dataset file: no such file: {path} (set --data_file)')
        n = sum(1 for _ in open(path))
        _how = 'SHUFFLED (--shuffle)' if args.shuffle else 'file order, NOT shuffled'
        print(f'file: {path} ({n} documents, {_how})', flush=True)
        return load_dataset('json', data_files={'train': path}, streaming=streaming)
    if name == 'babylm':
        # One document per LINE, like bdict: the transcripts and subtitles are line-oriented
        # and a whole 152 MB file is not a "document" in any sense the slot machinery means.
        # Files are concatenated in SORTED ORDER and, with --no-shuffle, read in that order,
        # so the run sees bnc_spoken, then childes, then gutenberg ... -- a curriculum by
        # corpus rather than an interleaving. That is only meaningful unshuffled; with the
        # default per-corpus shuffle it is an ordinary mixed stream.
        files = _babylm_files()
        _how = 'file order, NOT shuffled' if args.shuffle is False else 'shuffled'
        print(f'babylm: {len(files)} text file(s), {_how}: '
              f'{", ".join(os.path.basename(f) for f in files)}', flush=True)
        return load_dataset('text', data_files={'train': files}, streaming=streaming)
    if name == 'bdict':
        # one document per LINE. datasets' 'text' builder with the default sample_by='line'
        # is exactly that, so the rest of the pipeline (shuffle, epoch wrap, _corpus_text)
        # is identical to a hub corpus and nothing downstream needs to know the difference.
        path = args.bdict_file
        if not os.path.exists(path):
            raise SystemExit(f'bdict: no such file: {path} (set --bdict_file)')
        if args.bdict_split:
            # built in memory rather than by load_dataset('text'): the split is one row to
            # MANY documents, which the line-oriented builder cannot express. The corpus is
            # ~300 KB, so materializing it costs nothing and the epoch counter then reports
            # passes over SENTENCES, which is what the run is actually measured in.
            from datasets import Dataset, DatasetDict
            sents = []
            for line in open(path):
                line = line.strip()
                if not line:
                    continue
                body = line.split(':', 1)[1] if ':' in line else line
                sents.extend(_split_sentences(body.strip()))
            print(f'bdict: {path} -> {len(sents)} sentence examples '
                  f'(--bdict_split, key stripped)', flush=True)
            return DatasetDict({'train': Dataset.from_dict({'text': sents})})
        print(f'bdict: {path} ({sum(1 for _ in open(path))} lines)', flush=True)
        return load_dataset('text', data_files={'train': path}, streaming=streaming)
    if name not in _TEXT_DATASETS:
        raise ValueError(f'unknown dataset: {name}')
    hf, cfg, _, _ = _TEXT_DATASETS[name]

    # prepared local copy (dolma3_prep.py) wins over the hub repo: no download, and its
    # parts are pre-shuffled across the whole corpus.
    local = _local_files(name)
    if local:
        if shards:
            local = local[:shards]
        print(f'{name}: loading {len(local)} local parquet part(s) from {_LOCAL_DIRS[name]}')
        return load_dataset('parquet', data_files={'train': local}, streaming=streaming)
    if name in _LOCAL_DIRS:
        print(f'{name}: no prepared copy at {_LOCAL_DIRS[name]} -- falling back to the hub '
              f'repo. Hub shards are topic-partitioned: streaming trains on one topic at a '
              f'time and non-streaming fails to cast. See dolma3_prep.py')

    # --shards: restrict a non-streaming load to the first N parquet shards via data_files,
    # so datasets only resolves/reads those files instead of the whole repo.
    data_files = None
    if not streaming and shards:
        files = _shard_files(hf, cfg, shards)
        if files:
            print(f'{name}: --shards {shards} -> loading {len(files)} shard(s)')
            data_files = {'train': files}
        else:
            print(f'{name}: --shards set but no shard files found; loading full dataset')

    if data_files is not None:
        # no_checks: skip the split-size verification, which would fail since we load only
        # a subset of the repo's shards (recorded rows != the repo's recorded full split).
        loader = lambda dlc: load_dataset(hf, data_files=data_files, download_config=dlc,
                                          verification_mode='no_checks')
    else:
        loader = lambda dlc: load_dataset(hf, cfg, streaming=streaming, download_config=dlc)

    # Non-streaming eagerly resolves every shard (large corpora have thousands), which
    # can blow past HF's 5000-requests/5-min limit -> 429. Throttle the download workers
    # and retry across rate-limit windows; cached shards persist between tries so each
    # attempt makes forward progress until the cache is complete.
    if streaming:
        return loader(None)
    from datasets import DownloadConfig
    dlc = DownloadConfig(num_proc=4, max_retries=8)
    for attempt in range(1, 1000):
        try:
            return loader(dlc)
        except Exception as e:
            if '429' not in str(e) and 'Too Many Requests' not in str(e):
                raise
            print(f'HF 429 rate-limit on {name} (attempt {attempt}); cached shards kept, '
                  f'cooling down 300s then resuming...')
            time.sleep(300)


# Below this on-disk size a corpus is shuffled by TRUE PERMUTATION rather than by a
# sliding buffer: it fits in page cache, so the read-amplification argument in _make_iter
# does not apply. 1 GiB covers wdef (~70MB) with room to spare and excludes every web-scale
# corpus here by three orders of magnitude.
_EXACT_SHUFFLE_BYTES = 1 << 30


def _make_iter(ds, split, streaming, seed, buffer_size=10000, shuffle=True):
    # a SyntheticCorpus is already an infinite iid stream: there is no split to select and
    # nothing a shuffle buffer could reorder that is not already random.
    if isinstance(ds, SyntheticCorpus):
        return iter(ds)
    split_ds = ds[split] if split in ds else ds['train']
    # --dataset file: iterate in FILE ORDER. Every other branch below shuffles somehow --
    # a buffer when streaming, a permutation when small, a sharded buffer otherwise -- and
    # none of that is reproducible across runs, so a fixed corpus is the only way to take
    # the data out of the comparison. Returned before any of them.
    if not shuffle:
        return iter(split_ds)
    if streaming:
        return iter(split_ds.shuffle(buffer_size=buffer_size, seed=seed))
    # SMALL corpus: a true permutation. The amplification disaster described below is a
    # property of random access into a 45.7GB arrow file, not of Dataset.shuffle() itself --
    # a corpus that fits in page cache pays nothing for it. This matters specifically for a
    # CLOSED corpus that is REPEATED (wdef): under a 10k-row buffer an entry's neighbours are
    # largely the same on every pass, so each epoch would re-present the same local orderings
    # and any "memorization" could be an artifact of that correlation. A full permutation
    # makes each epoch an independent ordering, which is what --seed + epoch is for.
    _bytes = getattr(split_ds, 'dataset_size', None)
    if _bytes is not None and _bytes <= _EXACT_SHUFFLE_BYTES:
        return iter(split_ds.shuffle(seed=seed))
    # NON-STREAMING: never Dataset.shuffle() here. It builds a permutation and iteration
    # then becomes RANDOM ACCESS across the whole arrow file. Measured on fineweb-edu
    # (45.7GB local): 164MB of logical reads pulled 73GB off disk -- 445x amplification --
    # at 10MB/s, and the trainer produced ZERO steps in nine minutes while looking healthy
    # (process running, GPU allocated, no error).
    # to_iterable_dataset() reads the shards SEQUENTIALLY and shuffles inside a buffer, the
    # same approximate shuffle the streaming path uses, at disk-friendly access patterns.
    it = split_ds.to_iterable_dataset(num_shards=64)
    return iter(it.shuffle(buffer_size=buffer_size, seed=seed))


class _BlockReader:
    """--blocks: the corpus as ONE CONTIGUOUS STREAM per slot, not a bag of documents.

    Why it exists. A line-oriented corpus (babylm) loaded the ordinary way becomes one
    "document" per line -- ~13 tokens for transcripts and subtitles -- and every slot draws
    from a shared queue, so a slot gets roughly every Bth line: thirteen tokens of real
    continuity, then a jump to a distant part of the corpus. For an --unframed slot, whose
    state is never reset, that asks the recurrence to carry context across boundaries with no
    continuity behind them. Contiguity is the whole point of a long-reach model, so it has to
    come from the reader.

    PER FILE, not per corpus. Each file is cut into B byte ranges at newline boundaries and
    slot k reads range k of file 0, then range k of file 1, and so on. Cutting the CONCATENATED
    corpus instead would be simpler and would destroy the curriculum: slot 0 would sit in
    bnc_spoken while slot 200 sits in simple_wiki, so every batch would hold all six corpora
    at once. This way the whole batch moves through the files together -- childes while the
    model is learning child-directed speech -- and each slot still reads its own range of that
    file head to tail.

    One pass over every range of every file is one EPOCH, and the token count is the corpus
    token count, so the epoch length in steps is unchanged: corpus_tokens / batch.
    """
    CHUNK = 1 << 16          # bytes per refill; ~16k tokens, so a slot refills rarely

    def __init__(self, files, nslots, name):
        self.files, self.n, self.name = files, nslots, name
        # byte ranges per file, aligned FORWARD to the next newline so no line is split
        # across two slots and none is dropped.
        self.ranges = []
        for f in files:
            size = os.path.getsize(f)
            cuts = [0]
            with open(f, 'rb') as fh:
                for i in range(1, nslots):
                    fh.seek(size * i // nslots)
                    fh.readline()                  # advance past the partial line
                    cuts.append(min(fh.tell(), size))
            cuts.append(size)
            self.ranges.append([(cuts[i], cuts[i + 1]) for i in range(nslots)])
        self.fi   = [0] * nslots                   # current file index, per slot
        self.pos  = [self.ranges[0][k][0] for k in range(nslots)]
        self.epoch = [1] * nslots
        tot = sum(os.path.getsize(f) for f in files)
        print(f'blocks: {name} {len(files)} file(s) cut into {nslots} contiguous ranges each, '
              f'{tot / nslots / 1e6:.1f} MB per slot per pass', flush=True)

    def next_text(self, k):
        """The next chunk of slot k's stream, as text. Advances to the next file at the end
        of a range and wraps to file 0 (a new epoch) at the end of the last."""
        for _ in range(len(self.files) + 1):
            f          = self.files[self.fi[k]]
            start, end = self.ranges[self.fi[k]][k]
            if self.pos[k] >= end:
                self.fi[k] += 1
                if self.fi[k] >= len(self.files):
                    self.fi[k] = 0
                    self.epoch[k] += 1
                    _epoch_set(self.name, min(self.epoch))
                self.pos[k] = self.ranges[self.fi[k]][k][0]
                continue
            at_start = self.pos[k] == start        # first read of this range?
            with open(f, 'rb') as fh:
                fh.seek(self.pos[k])
                buf = fh.read(min(self.CHUNK, end - self.pos[k]))
                if self.pos[k] + len(buf) < end:
                    buf += fh.readline()           # never split a line
                self.pos[k] += len(buf)
            # NEWLINES OUT. The line breaks are the corpus FILE's format, not the text: a
            # BabyLM transcript puts one utterance per line, so a raw read stitches the block
            # together with a '\n' every ~13 tokens and the model spends its capacity
            # learning to emit them. --blocks exists to present the corpus as one continuous
            # document, so the separator becomes a space -- a space and not nothing, or the
            # last word of one line would fuse with the first of the next -- and runs of
            # whitespace collapse, since a blank line would otherwise leave a double space.
            # A chunk that CONTINUES a range keeps its leading space, because each chunk is
            # tokenized on its own: without it the first word would encode as a
            # start-of-text token instead of the ' word' form it has mid-document, once per
            # refill. One boundary in ~16k tokens either way, but it costs one space.
            txt = ' '.join(buf.decode('utf-8', errors='replace').split())
            return txt if at_start else ' ' + txt
        return ''


# ── worker ─────────────────────────────────────────────────────────────────────

class _ClipSlot:
    """One batch slot: independent clip stream. `name` is the dataset whose clip queue
    refills it under --mix_slots; None means the shared queue every slot draws from."""
    __slots__ = ['steps', 'pos', 'caption', 'name']

    def __init__(self, name=None):
        self.steps   = []
        self.pos     = 0
        self.caption = ''
        self.name    = name

    def load(self, steps, caption=''):
        self.steps   = steps
        self.pos     = 0
        self.caption = caption

    def done(self):       return self.pos >= len(self.steps)
    def is_start(self):   return self.pos == 0

    def advance(self):
        item     = self.steps[self.pos]
        self.pos += 1
        return item   # (x_byte, y_byte)


class _StreamSlot(_ClipSlot):
    """A corpus slot for an --unframed dataset. The builder hands it raw token ids rather
    than <STX>...<ETX> pairs, load() APPENDS them to a running buffer instead of replacing
    the clip, and the (x, y) pair that straddles a document boundary is the last token of
    one document -> the first of the next. is_start() is always False, so the recurrent
    state is never reset on this slot. Identical to the unframed _VocabSlot contract, for a
    streaming corpus instead of a local file; the buffer trim and --datarep handling are
    the same code."""
    __slots__ = ['ids', 'rep']

    def __init__(self, name=None):
        super().__init__(name)
        self.ids = []
        self.rep = 0

    def load(self, ids, caption=''):
        self.ids.extend(ids)
        self.caption = caption

    def done(self):       return self.pos + 1 >= len(self.ids)
    def is_start(self):   return False

    def advance(self):
        x, y = self.ids[self.pos], self.ids[self.pos + 1]
        self.rep += 1
        if self.rep < _DATAREP:
            return (x, y)
        self.rep = 0
        self.pos += 1
        if self.pos > 8192:                 # drop the consumed prefix; keeps memory flat
            self.ids = self.ids[self.pos:]
            self.pos = 0
        return (x, y)


# Sentences drawn per vocab file, so the epoch column can report passes over the FILE
# rather than per-slot cycles. Touched only by the worker thread (the stepping loop), which
# is single-threaded, so it needs no lock.
_vocab_consumed = {}


class _VocabSlot:
    """One batch slot fed by an endless stream of examples drawn from one local file.

    UNFRAMED (the default) differs from _ClipSlot in the two ways that matter:
      * NO FRAMING. clip_text wraps every document in <STX>...<ETX>; here the raw sentence
        tokens are concatenated head to tail, so the (x, y) pair that straddles a sentence
        boundary is a real transition from one sentence's last token to the next sentence's
        first. There is no delimiter for the model to key on.
      * is_start() IS ALWAYS FALSE, so this slot never signals a document start and the
        recurrent state is never reset on it. A corpus slot resets every <ETX>; this one
        runs forever.

    FRAMED (--vocab_framed) gives up both of those and behaves exactly like a corpus slot:
    one example at a time, wrapped <STX>...<ETX>, is_start() true on its first step so the
    DFF and the clock reset between examples. It is deliberately NOT the unframed stream
    with delimiters added -- examples do not run head to tail, so no (x, y) pair ever
    straddles a boundary and the model is never asked to predict across one. That is the
    same contract _ClipSlot has, which is the point: a pool of long self-contained documents
    should look to the model like documents, not like an unbroken sentence stream.

    Each slot keeps its own shuffled permutation and reshuffles on wrap, so N slots are
    N independent orderings of the same file rather than N copies of one ordering."""
    __slots__ = ['pool', 'texts', 'name', 'rng', 'order', 'oi', 'ids', 'pos',
                 'framed', 'steps', 'names', 'rep']

    def __init__(self, pool, name, seed, texts=None, framed=False, names=None):
        self.pool, self.name, self.texts = pool, name, texts
        # names: the SOURCE FILE of each example, when this slot merges several pools (see
        # the slot assignment in worker()). Epoch and text-sample accounting stay per FILE
        # even though the stream is one channel; None means every example came from `name`.
        self.names  = names
        self.framed = framed
        self.rng   = random.Random(seed)
        self.order = list(range(len(pool)))
        self.rng.shuffle(self.order)
        self.oi, self.ids, self.pos = 0, [], 0
        self.rep   = 0        # --datarep: replicas of the current pair already emitted
        self.steps = []

    def _next_index(self):
        """Index of the next example in this slot's permutation; reshuffles on wrap."""
        if self.oi >= len(self.order):
            self.oi = 0
            self.rng.shuffle(self.order)
        j = self.order[self.oi]
        self.oi += 1
        return j

    def _load_example(self):
        """FRAMED mode: make the next example the slot's current clip, <STX>...<ETX>."""
        j   = self._next_index()
        ids = [_tokenizer.start_id] + list(self.pool[j]) + [_tokenizer.end_id]
        self.steps = [(ids[i], ids[i + 1]) for i in range(len(ids) - 1)]
        if _DATAREP > 1:                       # same replication clip_text applies
            self.steps = [pair for pair in self.steps for _ in range(_DATAREP)]
        self.pos   = 0
        k = self.names[j] if self.names else self.name
        _vocab_consumed[k] = _vocab_consumed.get(k, 0) + 1
        _text_tally(len(ids), sample=(self.texts[j] if self.texts else ''),
                    vocab=k)

    def _append_next(self):
        j = self._next_index()
        ids = self.pool[j]
        self.ids.extend(ids)
        k = self.names[j] if self.names else self.name
        _vocab_consumed[k] = _vocab_consumed.get(k, 0) + 1
        _text_tally(len(ids), sample=(self.texts[j] if self.texts else ''), vocab=k)

    def done(self):      return False       # never refilled from clip_q

    def is_start(self):
        # unframed: never resets the state. framed: true on the <STX> step, like _ClipSlot.
        if not self.framed:
            return False
        if self.pos >= len(self.steps):     # called before advance(), so fill here too
            self._load_example()
        return self.pos == 0

    def advance(self):
        if self.framed:
            if self.pos >= len(self.steps):
                self._load_example()
            item = self.steps[self.pos]
            self.pos += 1
            return item
        while self.pos + 1 >= len(self.ids):
            self._append_next()
        x, y = self.ids[self.pos], self.ids[self.pos + 1]
        # --datarep: hold this pair for N steps before moving down the stream. The unframed
        # slot has no steps list to pre-expand, so the counter lives here instead.
        self.rep += 1
        if self.rep < _DATAREP:
            return (x, y)
        self.rep = 0
        self.pos += 1
        if self.pos > 8192:                 # drop the consumed prefix; keeps memory flat
            self.ids = self.ids[self.pos:]
            self.pos = 0
        return (x, y)


def _load_vocab_pools(paths, framed=None):
    """path -> (token-id lists one per line, path, n_lines, raw lines, framed).

    An UNFRAMED pool carries no <STX>/<ETX> and a trailing space is tokenized with each
    sentence, so concatenation reads as 'One sentence. Another sentence.' rather than
    running the words together.  A pool named in `framed` is wrapped per example by the
    slot instead, and gets NO trailing space: the example ends at <ETX>, so a space before
    it would train a token that the corpus path never emits there."""
    framed_stems = {os.path.splitext(os.path.basename(f.strip()))[0]
                    for f in (framed or '').split(',') if f.strip()}
    unknown = framed_stems - {os.path.splitext(os.path.basename(p))[0] for p in paths}
    if unknown:
        raise SystemExit(f'--vocab_framed: not in --vocab_files: {",".join(sorted(unknown))}')
    pools = {}
    for i, path in enumerate(paths):
        if not os.path.exists(path):
            raise SystemExit(f'--vocab_files: no such file: {path}')
        lines = [l.strip() for l in open(path) if l.strip()]
        # Keyed by FILE STEM, not by position: with three curriculum files the epoch
        # report has to say which one wrapped, and 'vocab3=812' does not identify
        # math_phase1.txt.  Positional keys are kept only to break a stem collision.
        key = os.path.splitext(os.path.basename(path))[0]
        if key in pools:
            key = f'{key}#{i+1}'
        is_framed = key in framed_stems
        pools[key] = ([_tokenizer.encode(l if is_framed else l + ' ') for l in lines],
                      path, len(lines), lines, is_framed)
    return pools


def worker(stop, q, datasets, args, mix=None):
    # datasets: {name: hf_dataset}. mix: (names, weights) or None (single dataset).
    if mix is None:
        names, weights = [args.dataset], [1.0]
    else:
        names, weights = mix
    _iters  = {}
    _locks  = {}
    _epochs = {}
    _shufs  = {}          # per-corpus shuffle decision, reused by every iterator re-make
    # When the batchwise vocab stream is active the epoch column must report passes over the
    # VOCAB FILES only: the corpus is effectively infinite and would pin the reported epoch
    # at 1 forever, since _epoch_num() takes the minimum across datasets.
    _track_corpus_epochs = not (args.vocab_files and args.vocab_slots)
    for n in set(names):
        # --shuffle unset: file order for --dataset file, shuffled for everything else.
        # Set either way, it applies to every corpus in the mix.
        # Remembered per corpus, because EVERY later _make_iter must reproduce it: an epoch
        # wrap and a --subsample stream re-make both rebuild the iterator, and _make_iter
        # defaults to shuffle=True. Without this, --no-shuffle held only for epoch 1 and the
        # corpus was silently shuffled from epoch 2 on -- which for an unshuffled curriculum
        # run is the whole experiment.
        _shuf      = (n != 'file') if args.shuffle is None else bool(args.shuffle)
        _shufs[n]  = _shuf
        _iters[n]  = _make_iter(datasets[n], _split_for_name(n), args.streaming, args.seed,
                                shuffle=_shuf)
        _locks[n]  = threading.Lock()   # HF streaming iterator is not thread-safe
        _epochs[n] = [1]
        if _track_corpus_epochs:
            _epoch_set(n, 1)

    # --subsample: replace each corpus iterator with a fixed list of N raw examples, drawn
    # once here from the shuffled stream. Drawn AFTER the same filters _build_clip applies
    # (_corpus_text and the held-out hash split), so the N examples are N usable documents
    # rather than N raw rows of which some would be dropped every epoch. The list itself is
    # the corpus from here on: exhaustion is an epoch, and the next epoch is a fresh
    # permutation of the same list under --seed + epoch, the convention _make_iter already
    # uses for its reshuffle seed.
    # HOW MANY DOCUMENTS CAN BE IN FLIGHT AT ONCE: one per batch slot, plus the built-clip
    # queue (maxsize 2*workers), plus one in each builder's hand. Conservative under
    # --mix_slots, where the batch is split across corpora and each has its own queue.
    _INFLIGHT = args.batch + 3 * max(1, args.workers)
    _recent = collections.defaultdict(lambda: collections.deque(maxlen=_INFLIGHT))

    def _subsample_epoch(pool, seed, hold=()):
        """Permute the pool for one epoch, with the documents still IN FLIGHT deferred to
        the end of it.

        Without this a reshuffle is independent of what the slots are holding, so a document
        drawn near the end of one epoch can be handed to a second slot at the start of the
        next while the first is still running it -- the same text twice in one batch, at two
        offsets, correlating the gradient and the BatchNorm statistics. Deferring the
        in-flight set turns an unbounded collision rate into a bounded one: a document cannot
        be redrawn until the other N - |hold| have been, which buys it
        (N - |hold|) * mean_len / batch steps to finish. Only documents LONGER than that can
        still double, so the bound is printed at startup rather than left implicit."""
        held, rest = [], []
        for d in pool:
            (held if id(d) in hold else rest).append(d)
        rng = random.Random(seed)
        rng.shuffle(rest)
        rng.shuffle(held)
        return rest + held

    _samples = {}
    _stream  = {}     # the underlying corpus iterator, kept for --epochs refreshes
    _spass   = {}     # how many times the stream has been re-made (its reshuffle seed)

    _fresh_docs = collections.Counter()   # --subsample: distinct documents drawn so far
    _fresh_toks = collections.Counter()   # ...and their token count, per corpus

    def _sub_log(msg):
        """subsample lines go to stdout AND log/exp.$M: the fresh-token tally is the x-axis
        of a --epochs experiment and has to survive a resume, which rewrites .out."""
        print(msg, flush=True)
        with open(args.log, 'a') as f:
            print(msg, file=f)

    def _draw(n, k):
        """k usable examples off the corpus stream (re-made, reseeded, on exhaustion)."""
        drawn, seen, remade = [], 0, False
        while len(drawn) < k:
            try:
                ex = next(_stream[n])
            except StopIteration:
                if remade:
                    break                        # corpus smaller than k: take what there is
                remade = True                    # one fresh pass per draw, then stop
                _spass[n] += 1
                _stream[n] = _make_iter(datasets[n], _split_for_name(n), args.streaming,
                                        args.seed + 7919 * _spass[n], shuffle=_shufs[n])
                continue
            seen += 1
            text = _corpus_text(n, ex)
            if not text or (n in _HASH_HOLDOUT and _is_heldout(text)):
                continue
            drawn.append(ex)
            _fresh_toks[n] += len(_tokenizer.encode(text))
        _fresh_docs[n] += len(drawn)
        return drawn, seen

    def _fresh(n):
        return f'fresh total {_fresh_docs[n]} docs / {_fresh_toks[n]:,} tokens'

    def _refresh_count(epoch):
        """Documents to turn over at the start of this epoch: N/E, remainder spread so that
        exactly N have turned over after every E epochs."""
        N, E = args.subsample, args.epochs
        return (N * epoch) // E - (N * (epoch - 1)) // E

    if args.subsample:
        for n in set(names):
            _stream[n] = _iters[n]
            _spass[n]  = 0
            drawn, seen = _draw(n, args.subsample)
            _samples[n] = drawn
            _sub_log(f'SUBSAMPLE {n} {len(drawn)} examples drawn from {seen} '
                     f'(requested {args.subsample}, seed {args.seed}'
                     f'{f", {_refresh_count(2)}/epoch turnover over {args.epochs} epochs" if args.epochs else ", closed"}) '
                     f'{_fresh(n)}')
            _iters[n] = iter(_subsample_epoch(drawn, args.seed + 1, set(_recent[n])))
            # The bound the holdback buys, in the corpus's own units. A document longer than
            # this can still be redrawn while a slot is running it; shorter ones cannot.
            _mlen = _fresh_toks[n] / max(_fresh_docs[n], 1)
            _gap  = max(len(drawn) - _INFLIGHT, 0) * _mlen / max(args.batch, 1)
            if len(drawn) <= _INFLIGHT:
                print(f'WARNING: --subsample {args.subsample} is not larger than the '
                      f'{_INFLIGHT} documents that can be in flight ({args.batch} slots + '
                      f'{3 * max(1, args.workers)} queued/building), so every batch holds '
                      f'duplicates and no holdback can prevent it', flush=True)
            else:
                print(f'subsample holdback: {n} defers up to {_INFLIGHT} in-flight docs to '
                      f'the end of each reshuffle; a redrawn document has had >= {_gap:,.0f} '
                      f'steps to finish, so only documents longer than {_gap:,.0f} tokens '
                      f'(mean is {_mlen:,.0f}) can appear twice in one batch', flush=True)

    def _next_example(name):
        """Thread-safe pull of the next raw example for one dataset (loops on exhaustion)."""
        with _locks[name]:
            try:
                _ex = next(_iters[name])
                if args.subsample:
                    _recent[name].append(id(_ex))   # identity, for the reshuffle holdback
                return _ex
            except StopIteration:
                _epochs[name][0] += 1
                # For a finite corpus that is deliberately repeated (wdef) the epoch boundary
                # is a real landmark: it is where documents start being seen for the Nth time,
                # and memorization should appear as a loss step at exactly these positions.
                # Written to args.log, not just stdout, so it interleaves with the STEP lines
                # in log/exp.$M instead of landing only in the buffered .out.
                if _track_corpus_epochs:
                    _epoch_set(name, _epochs[name][0])
                # stdout only. The epoch is a COLUMN on every STEP line now, so a
                # standalone line in the main log would duplicate it and break the
                # one-row-per-step shape chart.py reads. This still lands in log/exp.$M.out,
                # which is where the reshuffle seed stays recoverable.
                print(f'EPOCH {name} -> {_epochs[name][0]} '
                      f'(reshuffle seed {args.seed + _epochs[name][0]})', flush=True)
                if name in _samples:
                    if args.refresh:
                        if args.refresh_every:
                            # FIXED SCHEDULE. The stall detector is not consulted and is not
                            # even running -- no hooks are registered (see _stab_register),
                            # nothing is measured, nothing is logged -- because a schedule
                            # does not read it, and the measurement costs one extra full
                            # reduction per conv layer. The epoch counter alone decides.
                            _fire = _epochs[name][0] % args.refresh_every == 0
                        else:
                            # STALL-DRIVEN. _stab_epoch is drained here, at the epoch
                            # boundary, so 'epoch' means the same thing to the detector as
                            # it does to the pool.
                            _fire = False
                            _st = _stab_epoch(args.refresh_r)
                            if _st is None:
                                _sub_log(f'TRIGGER {name} epoch {_epochs[name][0]} detector '
                                         f'warming up (no baseline yet)')
                            else:
                                _d, _da, _nl, _mu, _ns = _st
                                # STILL? Either the drift is under an absolute floor (the
                                # paper), or it has stopped setting new minima (relative).
                                _ad = abs(_d)
                                if args.refresh_mode == 'abs':
                                    _still = _ad <= args.refresh_eps
                                    _extra = f'eps {args.refresh_eps:g}'
                                else:
                                    _b = _stab_best[0]
                                    _improved = _b is None or _ad < _b * (1.0 - args.refresh_tol)
                                    if _improved:
                                        _stab_best[0] = _ad
                                    _still = not _improved
                                    _extra = f'best {_stab_best[0]:.{args.refresh_r}f}'
                                _stab_hold[0] = _stab_hold[0] + 1 if _still else 0
                                _sub_log(f'TRIGGER {name} epoch {_epochs[name][0]} '
                                         f'sum_delta {_d:+.{args.refresh_r}f} '
                                         f'sum_abs_delta {_da:.{args.refresh_r}f} '
                                         f'mean_std {_mu:.4f} layers {_nl} samples {_ns} '
                                         f'{args.refresh_mode} {_extra} '
                                         f'still {_stab_hold[0]}/{args.refresh_hold}')
                                _fire = _stab_hold[0] >= args.refresh_hold
                        if _fire:
                            k = max(1, int(round(args.refresh * args.subsample)))
                            fresh, seen = _draw(name, k)
                            pool = _samples[name]
                            del pool[:len(fresh)]
                            pool.extend(fresh)
                            # The detector's baseline goes too -- a no-op on the scheduled
                            # path, where it was never built: the next epoch runs on partly
                            # new data, so differencing it against the stalled epoch would
                            # compare two different datasets and fire spuriously.
                            _stab_hold[0] = 0
                            _stab_prev.clear()
                            _stab_best[0] = None
                            _sub_log(f'TRIGGER {name} '
                                     f'{"SCHEDULED" if args.refresh_every else "STALLED"} '
                                     f'at epoch {_epochs[name][0]} -- retired {len(fresh)} '
                                     f'oldest, drew {len(fresh)} fresh from {seen} '
                                     f'(pool {len(pool)}) {_fresh(name)}')
                    if args.epochs:
                        # --epochs: retire the oldest k, draw k fresh. The pool is kept in
                        # insertion order so "oldest" is the head; a document therefore
                        # lives exactly E epochs from the epoch it entered.
                        k = _refresh_count(_epochs[name][0])
                        fresh, seen = _draw(name, k)
                        pool = _samples[name]
                        del pool[:len(fresh)]
                        pool.extend(fresh)
                        _sub_log(f'SUBSAMPLE {name} epoch {_epochs[name][0]} retired '
                                 f'{len(fresh)} oldest, drew {len(fresh)} fresh from {seen} '
                                 f'(pool {len(pool)}) {_fresh(name)}')
                    _iters[name] = iter(_subsample_epoch(_samples[name],
                                                         args.seed + _epochs[name][0],
                                                         set(_recent[name])))
                else:
                    _iters[name] = _make_iter(datasets[name], _split_for_name(name),
                                              args.streaming, args.seed + _epochs[name][0],
                                              shuffle=_shufs[name])
                return next(_iters[name])

    def _build_clip(name, example):
        text = _corpus_text(name, example)
        # '' means the example was filtered or unusable -> empty steps, builder skips it.
        # The hash check must come AFTER the _TEXT_FORMAT branch and apply to BOTH: a
        # corpus with a formatter (cosmo) is still hash-split, and returning early here
        # would train on exactly the documents the eval holds out.
        if not text:
            return ([], '')
        if name in _HASH_HOLDOUT and _is_heldout(text):
            return ([], '')
        if name in _UNFRAMED:             # raw ids; the _StreamSlot runs them head to tail
            return (_tokenizer.encode(text), text)
        return clip_text(text)

    # BATCHWISE MIX. The first --vocab_slots slots stream undelimited sentences from
    # --vocab_files (split evenly between the files); the rest are ordinary _ClipSlots fed
    # from --dataset/--mix with <STX>/<ETX>. Slots map 1:1 to tokens per step, so this is an
    # exact token split rather than the on-average one --mix gives.
    _vocab_paths = [p.strip() for p in (args.vocab_files or '').split(',') if p.strip()]
    n_vocab = min(args.vocab_slots, args.batch) if _vocab_paths else 0
    if args.vocab_slots and not _vocab_paths:
        raise SystemExit('--vocab_slots set but --vocab_files is empty')
    slots = []
    if n_vocab:
        pools = _load_vocab_pools(_vocab_paths, args.vocab_framed)
        keys  = sorted(pools)
        for k in keys:
            _vocab_consumed[k] = 0
            _vocab_total[k] = pools[k][2]
            _epoch_set(k, 1)
            if pools[k][4]:
                _epoch_mean_exclude.add(k)   # framed pools sit outside the epoch mean
            _framing = '<STX>/<ETX> framed' if pools[k][4] else 'undelimited'
            print(f'{k}: {pools[k][1]} ({pools[k][2]} examples, {_framing})', flush=True)
        if _epoch_mean_exclude:
            print(f'epoch mean over {[k for k in keys if k not in _epoch_mean_exclude]}, '
                  f'excluding framed {sorted(_epoch_mean_exclude)}', flush=True)
        def _merge(ks):
            """Several files as ONE stream: pools concatenated, each example remembering
            which file it came from. Drawn uniformly over the union, so files contribute in
            proportion to their LINE COUNTS (two 10k-line files are 50/50)."""
            fr = {pools[k][4] for k in ks}
            if len(fr) > 1:
                raise SystemExit(
                    f'--vocab_slots {n_vocab} would merge {",".join(ks)} into one slot, but '
                    f'they disagree on framing (--vocab_framed). A framed pool resets the '
                    f'state between examples and an unframed one never does; one slot cannot '
                    f'do both. Give them separate slots (--vocab_slots >= {len(keys)}).')
            pool, texts, nm = [], [], []
            for k in ks:
                pool.extend(pools[k][0])
                texts.extend(pools[k][3])
                nm.extend([k] * pools[k][2])
            return pool, texts, nm, fr.pop()

        for i in range(n_vocab):
            # More slots than files: round robin, one file per slot (the historical split).
            # FEWER slots than files: each slot merges a stripe of the files into a single
            # undelimited stream, so --vocab_slots 1 with two files is ONE channel carrying
            # both -- not the first file only, which is what a bare round robin would give.
            my = [keys[i % len(keys)]] if n_vocab >= len(keys) else keys[i::n_vocab]
            if len(my) == 1:
                k = my[0]
                slots.append(_VocabSlot(pools[k][0], k, args.seed + 9973 * i, pools[k][3],
                                        framed=pools[k][4]))
            else:
                _pl, _tx, _nm, _fr = _merge(my)
                print(f'vocab slot {i}: {" + ".join(my)} merged, {len(_pl)} examples, '
                      f'{"<STX>/<ETX> framed" if _fr else "undelimited"}', flush=True)
                slots.append(_VocabSlot(_pl, '+'.join(my), args.seed + 9973 * i, _tx,
                                        framed=_fr, names=_nm))
        print(f'batchwise mix: {n_vocab}/{args.batch} vocab slots '
              f'({100.0*n_vocab/args.batch:.1f}% of tokens), '
              f'{args.batch-n_vocab} corpus slots', flush=True)
    n_corpus = args.batch - n_vocab
    _slot_of = lambda n: _StreamSlot(n) if n in _UNFRAMED else _ClipSlot(n)
    if args.mix_slots and mix is not None:
        # --mix_slots: round(w * slots) each, the remainder to the largest fractional parts
        # so the counts sum exactly to n_corpus. A weight that rounds to zero slots is a
        # corpus that would silently never be trained on, so it is an error.
        _exact = [w * n_corpus for w in weights]
        _cnt   = [int(e) for e in _exact]
        for i in sorted(range(len(names)), key=lambda i: _exact[i] - _cnt[i], reverse=True):
            if sum(_cnt) >= n_corpus:
                break
            _cnt[i] += 1
        _zero = [n for n, c in zip(names, _cnt) if c == 0]
        if _zero:
            raise SystemExit(f'--mix_slots: {",".join(_zero)} rounds to 0 of {n_corpus} slots')
        for n, c in zip(names, _cnt):
            slots += [_slot_of(n) for _ in range(c)]
        print('batchwise mix: ' + ', '.join(
            f'{n} {c} slots ({"undelimited" if n in _UNFRAMED else "<STX>/<ETX> framed"})'
            for n, c in zip(names, _cnt)), flush=True)
    else:
        # one shared queue (slot name None); a single --dataset may be --unframed, in which
        # case every corpus slot is a _StreamSlot
        _un = mix is None and names[0] in _UNFRAMED
        slots += [(_StreamSlot() if _un else _ClipSlot()) for _ in range(n_corpus)]

    # Pool of builder threads runs the dataset pull/encode in parallel and parks
    # finished clips in clip_q, so the stepping loop below never blocks on one clip.
    # Under --mix_slots each dataset has its own queue and its own builders (pinned round
    # robin, so every dataset gets at least one): a shared queue would let one corpus's
    # clips block the other's slots, and a random per-clip dataset choice would let a full
    # queue on one side stall a builder the other side needs.
    n_builders = max(1, args.workers)
    clip_q     = queue.Queue(maxsize=2 * n_builders)
    if args.mix_slots and mix is not None:
        _ds_list = sorted(set(names))
        _pinned  = [_ds_list[i % len(_ds_list)] for i in range(max(n_builders, len(_ds_list)))]
        clip_qs  = {n: queue.Queue(maxsize=2 * _pinned.count(n)) for n in _ds_list}
    else:
        _pinned  = [None] * n_builders
        clip_qs  = {None: clip_q}

    # token-proportional dataset sampling: `weights` is the desired *token* mix, but
    # datasets have very different tokens-per-example, so choosing examples directly by
    # `weights` skews the token mix. Track a running mean clip length per dataset and
    # sample examples with weight w/mean_len, so expected tokens per dataset ∝ w.
    _len_lock = threading.Lock()
    _len_sum  = {n: 0.0 for n in set(names)}
    _len_cnt  = {n: 0   for n in set(names)}

    def _mix_weights():
        with _len_lock:
            # bootstrap unseen datasets with mean_len=1 so they still get sampled
            return [w / max(_len_sum[n] / _len_cnt[n] if _len_cnt[n] else 1.0, 1e-9)
                    for n, w in zip(names, weights)]

    def builder(fixed=None):
        rng = random.Random()   # per-clip dataset choice (thread-local instance)
        cq  = clip_qs[fixed]    # --mix_slots: this thread's dataset and its queue
        while not stop.is_set():
            name = fixed if fixed is not None else rng.choices(names, weights=_mix_weights(), k=1)[0]
            try:
                steps, caption = _build_clip(name, _next_example(name))
            except Exception as e:
                print(f'builder: {e}')
                continue
            if not steps:
                continue
            with _len_lock:                      # update token-length stats for the mix
                _len_sum[name] += len(steps)
                _len_cnt[name] += 1
            _text_tally(len(steps), sample=caption)
            while not stop.is_set():
                try:
                    cq.put((steps, caption), timeout=0.5)
                    break
                except queue.Full:
                    pass

    # --blocks: each slot reads its own contiguous byte range, so the shared clip queue and
    # its builder threads are bypassed for corpus slots entirely. Refills happen inline in
    # the loop below: a 64 KB chunk is ~16k tokens and a slot consumes one token per step, so
    # a slot refills about every 16k steps and the tokenizer cost is a fraction of a percent.
    _blocks = _BlockReader(_babylm_files(), n_corpus, names[0]) if args.blocks else None

    builders = [] if _blocks else [threading.Thread(target=builder, args=(f,), daemon=True)
                                   for f in _pinned]
    for b in builders:
        b.start()

    while not stop.is_set():
        for _si, slot in enumerate(slots):
            while slot.done():
                if _blocks is not None and _si >= n_vocab:
                    # RAW IDS, not (x, y) pairs: a _StreamSlot appends to a running buffer
                    # and forms the pair itself, so the pair straddling a refill is the last
                    # token of one chunk -> the first of the next and the stream is unbroken
                    # across the 64 KB boundary. Passing pairs here made load() extend the
                    # buffer with tuples and the slot never became ready.
                    text = _blocks.next_text(_si - n_vocab)
                    ids  = _tokenizer.encode(text) if text else []
                    if _DATAREP > 1:
                        ids = [x for x in ids for _ in range(_DATAREP)]
                    if not ids:
                        break          # nothing left to read this sweep; retry on the next
                    # The WHOLE chunk as the sample, not its opening 400 characters.
                    # _sample_window draws a random window from the stored sample precisely
                    # so a long-lived load does not show its first lines forever (see the
                    # sebooks note there) -- and a 400-char store defeats that: every window
                    # overlaps, so report after report reads as the same text. A slot holds
                    # this chunk for ~16k steps, so the chunk IS what the run is training on
                    # for that whole stretch, and a window of it is the honest sample.
                    _text_tally(len(ids), sample=text)
                    slot.load(ids, text[:400])
                    continue
                try:
                    steps, caption = clip_qs[slot.name].get(timeout=0.5)
                except queue.Empty:
                    if stop.is_set():
                        return
                    continue
                slot.load(steps, caption)

        if n_vocab:
            # passes over the FILE = total sentences drawn / file size, which is the honest
            # reading when 225 slots each hold their own permutation of the same file.
            for k in keys:
                _epoch_set(k, 1 + _vocab_consumed[k] // pools[k][2])
                _epoch_frac_set(k, _vocab_consumed[k] / pools[k][2])

        x_list, y_list, flag_list = [], [], []
        for slot in slots:
            flag_list.append(slot.is_start())
            x, y = slot.advance()
            x_list.append(x)
            y_list.append(y)

        q.put((x_list, y_list, flag_list))


# ── dataset loading (before CUDA init) ───────────────────────────────────────

if args.vis or args.altvis or args.generate or args.push or args.eval:
    hf_dataset = None                 # one-shot modes: --vis/--generate run from the prompt
                                      # token, --push only uploads weights, and --eval loads
                                      # its own held-out split — none of them needs the
                                      # training dataset
else:
    print('loading dataset...')
    if _mix is not None:
        _ds_names  = sorted(set(_mix[0]))
        hf_dataset = {n: _init_one_dataset(n, args.streaming, args.shards) for n in _ds_names}
        print('mix:', ', '.join(f'{n}:{w:.3f}' for n, w in zip(_mix[0], _mix[1])))
    else:
        hf_dataset = {args.dataset: _init_one_dataset(args.dataset, args.streaming, args.shards)}
    print('dataset ready')

# ── model instantiation ───────────────────────────────────────────────────────

if args.pretrained:
    # Hub checkpoint: config.json (written by save_pretrained) supplies the architecture,
    # so the model is built from it rather than from the --context/--n_hidden/... args.
    # Those args are then synced to what was actually built, since the rest of the script
    # reads them (DFF shapes, summaries, logged ARGS line).
    if not hasattr(VLAModel, 'from_pretrained'):
        print('ERROR: --pretrained requires huggingface_hub (pip install huggingface_hub)')
        raise SystemExit(1)
    print(f'loading {args.pretrained} from the hub...')
    model = VLAModel.from_pretrained(args.pretrained, revision=args.revision)
    _cfg  = getattr(model, '_hub_mixin_config', None) or {}
    _restore_arch({_k: _cfg[_a] for _k, _a in
                   (('context', 'S'), ('n_hidden', 'n_hidden'), ('c_context', 'c_context'),
                    ('c_text', 'c_text'),
                    ('n_layers', 'n_layers'), ('depth', 'depth'), ('kernel', 'kernel'),
                    ('tokenizer', 'tokenizer'),
                    ('head_norm', 'head_norm'),
                    ('clock', 'clock'), ('clock_base', 'clock_base'),
                    ('accumulate', 'accumulate'), ('ema', 'ema'),
                    ('qproj', 'qproj'), ('tap', 'tap')) if _a in _cfg},
                  'pretrained config')
    # from_pretrained built the model straight from that config, so an overridden blend
    # rate has to be pushed onto the model too -- unlike --load there is no later
    # construction step.
    if _CLI_GIVEN & {'ema', 'ema_ladder'}:
        model.set_ema(args.ema, ema_ladder=args.ema_ladder)
    print('pretrained config', _cfg)
    # The ARGS line was logged before the hub config was known, so it still shows the CLI
    # arch defaults. Re-log the corrected args, or the log would misattribute the run.
    print('ARGS (pretrained)', args)
    with open(args.log, 'a') as f:
        print('ARGS', args, file=f)
else:
    model = VLAModel(
        n_hidden  = args.n_hidden,
        depth     = args.depth,
        kernel    = args.kernel,
        S         = args.context,
        c_context = args.c_context,
        c_text    = args.c_text,
        n_layers  = args.n_layers,
        clip_dff   = args.clip_dff,
        tap_norm   = args.tap_norm,
        norm       = args.norm,
        norm_groups= args.norm_groups,
        dff_norm   = args.dff_norm,
        bn_track   = args.bn_track,
        bn_affine  = args.bn_affine,
        bn_momentum= args.bn_momentum,
        bn_eps     = args.bn_eps,
        ema        = args.ema,
        qproj      = args.qproj,
        tap        = args.tap,
        tokenizer = args.tokenizer,
        head_norm = args.head_norm,
    )

    if _loaded_ckpt is not None:
        model.load_state_dict(_loaded_ckpt['state_dict'])
        del _loaded_ckpt

# Bind the module-level tokenizer used by clip_text() and every display path. The worker
# threads that call clip_text() are only started further down, so this is set in time.
_tokenizer = model.tok
if args.refresh and not args.refresh_every:
    _stab_register(model)
# --tokenizer tiny* takes c_text from the pretrained embedding width, so sync it back:
# saved_args must describe the model that was actually built or a --load would rebuild
# a different one.
args.c_text = model.c_text
# likewise --c_context: --depth 1 forces it to n_hidden, so saved_args must record the width
# that was built or a --load would rebuild a different stack.
args.c_context = model.context.c_context
# likewise --head_norm: char forces it to 'none', and so does an ln_f that the source model
# turned out not to expose, so read back what was actually built.
args.head_norm = model.head_norm_kind
args.clip_dff   = model.clip_dff
args.tap_norm   = model.tap_norm_kind
args.norm       = model.norm_kind
args.norm_groups = model.norm_groups
args.dff_norm   = model.dff_norm_kind
args.bn_track   = model.bn_track
args.bn_affine  = model.bn_affine
# Only a SCALAR ema syncs back. Under --ema_ladder model.ema is a per-layer list, and
# writing that into args would put a list in saved_args['ema'] -- which _restore_arch then
# hands to set_clock on the next --load, where float(list) raises. ema_ladder is the source
# of truth for the ladder and is saved separately.
args.ema        = model.ema if isinstance(model.ema, float) else args.ema
args.qproj      = model.qproj_mode
args.tap        = model.tap is not None

# --unfreeze trains the borrowed embedding/lm_head too. requires_grad is not part of the
# state_dict, so this is re-applied on every run (including --load/--pretrained) from the
# flag rather than inherited from the checkpoint.
if args.unfreeze:
    model.set_pretrained_trainable(True)


def _prompt_ids(text=None):
    """A prompt as token ids, with START prepended: the same [START] text framing every
    training clip opens with, so a sample always starts at a document boundary.

    text=None means --prompt (the original behaviour, unchanged for every existing caller);
    the periodic GEN block passes each entry of _gen_prompt_list() explicitly."""
    t = args.prompt if text is None else text
    if args.gen_null and not t:
        return []                      # --gen_null: no <STX>, no tokens; see generate()
    return [_tokenizer.start_id] + (_tokenizer.encode(t) if t else [])


class _GenScorer:
    """Fluency of a GEN sample under a frozen reference LM, anchored to this run's corpus.

    nats/token alone says nothing -- a reference model's absolute surprise depends on the
    domain. So the score is placed between two anchors drawn from the training text itself:
        FLOOR    real corpus text            -> 100%, as fluent as this corpus gets
        CEILING  the same text, words shuffled -> 0%, same words with the syntax destroyed
    Anchors are computed ONCE, from the first corpus documents the data worker produced, and
    then frozen -- a drifting anchor would make the series incomparable across steps.

    The reference is a different model from the one under test, so this cannot be gamed by
    the run. It lives on the CPU: it runs once per --gen_interval, so it costs nothing worth
    contending for GPU memory over, and it can never perturb the training allocation.

    rep1 is reported alongside, and exists because THIS METRIC IS BACKWARDS ON DEGENERATE
    TEXT: a model emitting one token forever is maximally predictable and scores as maximally
    fluent. rep1 is the larger of two rates -- the fraction of the sample made of its most
    common WORD and the fraction of its non-whitespace CHARACTERS made of the most common one
    -- because a word-only rate has a hole: a wall of one punctuation character broken by
    spaces splits into many distinct "words" and reads 0.08, while the reference LM scores
    that sample 98% fluent (v196 step 10000); the character rate calls it 0.75. Read together, a
    high score with a high rep1 is collapse, not fluency.
    """
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
        except Exception as e:                      # never take the training run down
            print(f'--gen_score: DISABLED, could not load {self.repo}: {e}', flush=True)
            self.failed = True

    @torch.no_grad()
    def _nll(self, text):
        ids = self.tok(text, return_tensors='pt', truncation=True,
                       max_length=512).input_ids
        if ids.shape[1] < 2:
            return None
        v = float(self.ref(ids, labels=ids).loss)
        return v if math.isfinite(v) else None

    def _anchor(self):
        """FLOOR/CEILING from real corpus text; computed once, then frozen."""
        if self.floor is not None:
            return True
        docs = [d for d in _text_anchors() if len(d.split()) >= 24][:12]
        if len(docs) < 4:
            return False                            # not enough corpus text yet
        rng = random.Random(1234)                   # fixed: the same shuffle every run
        lo, hi = [], []
        for d in docs:
            w = d.split()[:256]
            a = self._nll(' '.join(w))
            sw = w[:]; rng.shuffle(sw)
            b = self._nll(' '.join(sw))
            if a is not None and b is not None:
                lo.append(a); hi.append(b)
        if len(lo) < 4 or np.mean(hi) - np.mean(lo) < 1e-6:
            return False
        self.floor, self.ceil = float(np.mean(lo)), float(np.mean(hi))
        print(f'--gen_score: anchors from {len(lo)} corpus documents -- '
              f'FLOOR {self.floor:.3f} (real text) CEILING {self.ceil:.3f} (words shuffled)',
              flush=True)
        return True

    def score(self, text):
        """-> 'nats 4.812 fluency 63% rep1 0.07', or '' if unavailable."""
        self._load()
        if self.failed:
            return ''
        # Gate on CHARACTERS, not words. A collapsed sample is often one unbroken run
        # ('okinetics*******...'), i.e. a single "word" -- and that is exactly the case this
        # metric exists to flag, so it must not be the case that gets skipped.
        text = text.strip()
        if len(text) < 16:
            return ''
        words = text.split()
        # rep1 is the MAX of the word-level and character-level rates, not a fallback from
        # one to the other. A word-only rep1 has a hole this metric cannot afford: a wall of
        # one punctuation character broken by spaces ('||| H|| |||||||| ...') splits into
        # many DISTINCT 'words' of different run lengths, so no single word dominates and
        # rep1 reads a healthy 0.12 -- while the reference LM, delighted by the most
        # predictable text imaginable, scored that sample 3.53 nats and 98% fluency
        # (v196 step 10000). Measured at the character level the same sample is ~0.7.
        # Whitespace is excluded from the character count so ordinary spacing cannot itself
        # become the dominant 'character' in a short sample.
        _chars = [c for c in text if not c.isspace()]
        rep1w  = max(collections.Counter(words).values()) / len(words) if words else 0.0
        rep1c  = max(collections.Counter(_chars).values()) / len(_chars) if _chars else 0.0
        rep1   = max(rep1w, rep1c)
        n = self._nll(' '.join(words[:256]) if words else text[:1024])
        if n is None:
            return ''
        if not self._anchor():
            return f'nats {n:.3f} fluency n/a (no anchors yet) rep1 {rep1:.2f}'
        pct = 100.0 * (self.ceil - n) / (self.ceil - self.floor)
        return f'nats {n:.3f} fluency {max(-999.0, min(999.0, pct)):.0f}% rep1 {rep1:.2f}'


_gen_scorer = _GenScorer(args.gen_score) if args.gen_score else None


def _gen_prompt_list():
    """Prompts for the periodic GEN sample: the NULL prompt first, then --prompt, then
    --gen_prompts, de-duplicated in that order.

    The null prompt is unconditional and first because it is exactly what every run before
    2026-08-28 sampled (--prompt defaults to '', so _prompt_ids() was already [START] alone).
    An invocation that adds reference prompts therefore gets them as EXTRA lines and its
    free-running sample is unchanged -- no run loses the measurement that has overturned the
    scalar reading more than once."""
    out = ['']
    if args.prompt:
        out.append(args.prompt)
    for p in (args.gen_prompts or '').split(','):
        p = p.strip()
        if p and p not in out:
            out.append(p)
    return out


_dff_shape = (1, args.n_hidden, args.context, args.context)
def _summ(title, mod, **kw):
    # --generate/--vis have no log file, so their summaries would only be terminal noise in
    # front of the sample / the plot window. --verbose asks for them anyway.
    if (args.generate or args.vis or args.altvis or args.push or args.eval) and not args.verbose:
        return
    s = str(torchinfo.summary(mod, col_names=['input_size', 'output_size', 'num_params'],
                              verbose=0, **kw))
    block = f'── {title} ──\n{s}'
    print(block)
    with open(args.log, 'a') as f:                  # mirror to log, each line prefixed INFO
        for line in block.splitlines():
            print(f'INFO {line}', file=f)

# Summaries follow the data flow: tok_embed → text_proj (token grid → n_hidden,
# summed into the DFF) → context (recurrent state update) → decoder → head_norm → lmhead
# → logits.
_borrowed = ('' if args.tokenizer == 'char' else
             f', frozen{"" if not args.unfreeze else " -> TRAINABLE (--unfreeze)"}')
_summ('tok_embed' + ('' if args.tokenizer == 'char' else
                     f' ({_TOKENIZERS[args.tokenizer]} input embedding{_borrowed})'),
      model.tok_embed, input_data=torch.zeros(1, dtype=torch.long))
_summ('text_proj', model.text_proj, input_size=(1, model.c_text, args.context, args.context))
if model.tap is not None:
    _summ(f'tap x{model.n_layers} (layer output -> DFF register and on to deep_proj, '
          f'trainable, identity-initialized)', model.tap[0], input_size=_dff_shape)
if model.qproj is not None:
    _summ(f'qproj x{model.n_layers} ('
          + ('DFF state -> feedback add, trainable, identity-initialized'
             if model.qproj_mode == 'read' else
             'layer output -> DFF register, FROZEN random orthogonal')
          + ')', model.qproj[0], input_size=_dff_shape)
_ctx_label = 'context (layer 1)' if model.n_layers > 1 else 'context'
if model.context.c_context != model.n_hidden:
    _ctx_label += (f' -- interior {model.context.c_context} channels (--c_context), '
                   f'ends pinned to n_hidden {model.n_hidden} by the DFF')
_summ(_ctx_label, model.context, input_size=_dff_shape)
# The blend rate is invisible in the layer summaries (it adds no parameters and no shapes),
# so state it explicitly: it is the only thing deciding how long the state remembers.
if model.ema is not None and (not (args.generate or args.vis or args.altvis or args.push
                                   or args.eval) or args.verbose):
    _lbl = getattr(model, 'dff_layers', list(range(model.n_layers)))
    if isinstance(model.ema, (list, tuple)):
        _txt = ('DFF blend rate per register '
                + ', '.join(f'L{_lbl[i] + 1}={e:.4g} (~{1.0 / e:.0f} tok window)'
                            for i, e in enumerate(model.ema)))
        print(f'--ema_ladder {model.ema_ladder}: {_txt}')          # spec as typed
        _line = f'--ema_ladder {model.ema_ladder}: {_txt}'
    else:
        _line = (f'--ema {model.ema:.4g}: every register blends '
                 f'register + {model.ema:.4g}*(new - register) every step '
                 f'(~{1.0 / model.ema:.0f} token window)')
        print(_line)
    with open(args.log, 'a') as f:
        print(f'INFO {_line}', file=f)
elif model.ema is None and not (args.generate or args.vis or args.altvis or args.push
                                or args.eval):
    print('no --ema/--ema_ladder: every register REPLACES its contents every step')

if model.deep_context is not None:
    _summ(f'deep_context x{model.n_layers - 1} (layers 2..{model.n_layers})',
          model.deep_context[0], input_size=_dff_shape)
if model.tap is not None and (not (args.generate or args.vis or args.altvis or args.push or args.eval)
                              or args.verbose):
    _tap_txt = (
        '── tap ──\n'
        '--tap: per layer, ContextCNN -> tap (1x1) -> DFF register, and the same tensor on\n'
        '       to ' + ('deep_proj (1x1) -> next layer; the last layer to decoder.proj (1x1)'
                        if model.n_layers > 1 else 'decoder.proj (1x1)') + '\n'
        '       so the two 1x1s in series are tap then '
        + ('deep_proj/decoder.proj' if model.n_layers > 1 else 'decoder.proj')
        + ', tapped between.\n'
        f'       register holds a dense signed embedding (was the sparse ReLU output); '
        f'--init {args.init}'
        + ('' if args.init == 'gaussian' else ' (gaussian matches a dense register better)'))
    print(_tap_txt)
    with open(args.log, 'a') as f:
        for line in _tap_txt.splitlines():
            print(f'INFO {line}', file=f)
_summ('decoder', model.decoder, input_size=_dff_shape)
if model.head_norm_kind not in ('none', 'batch2d'):
    _src = (f'{_TOKENIZERS[args.tokenizer]} {model.norm_path}{_borrowed}'
            if model.head_norm_kind == 'ln_f' else 'fresh, trained with the CNN')
    # batch 2, not 1: BatchNorm1d refuses a single sample per channel in train mode
    _summ(f'head_norm ({model.head_norm_kind}: {_src})',
          model.head_norm, input_size=(2, model.c_text))
if args.tokenizer != 'char':
    # GPT-Neo ties the head to the embedding, GPT-NeoX does not: say which, since it
    # decides whether --unfreeze trains one matrix or two.
    _tied = (next(model.lmhead.parameters()).data_ptr()
             == next(model.tok_embed.parameters()).data_ptr())
    _summ(f'lmhead ({_TOKENIZERS[args.tokenizer]} output embedding, '
          f'{"tied to tok_embed" if _tied else "untied"}{_borrowed})',
          model.lmhead, input_size=(1, model.c_text))

model = model.to(args.device)
model.init_mode = args.init   # applies to both construction paths (--pretrained and local)
print(f'tokenizer {args.tokenizer}: vocab {model.vocab}, embedding width {model.c_text}')
_trainable_n = sum(p.numel() for p in model.parameters() if p.requires_grad)
_frozen_n    = sum(p.numel() for p in model.parameters() if not p.requires_grad)
print(_trainable_n / 1e6, 'M trainable params'
      + (f' ({_frozen_n / 1e6:.6f} M frozen pretrained)' if _frozen_n else ''))


def _param_summary(model):
    """Per-module parameter counts and the total, printed once before training starts.

    The torchinfo tables above are per-submodule and verbose; this is the one place that
    says how big the model is in total and where the weights actually sit. It matters here
    because the answer is not obvious from the flags: --linout REPLACES deep_proj, a frozen
    pretrained embedding can outweigh everything trained, and the conv stack scales as
    n_layers * ((depth-2)*c_context**2 + 2*n_hidden*c_context) -- n_layers * depth *
    n_hidden**2 when --c_context is unset -- so a width change moves the total
    quadratically. The
    weight ROM is the thing being sized for hardware, so print it, not just infer it.

    Modules are walked by NAME off the model, then anything not claimed by a named module is
    swept into 'other' -- so the parts always sum to the total, whatever the flags did."""
    named = [('tok_embed',    model.tok_embed),
             ('text_proj',    model.text_proj),
             ('context',      model.context),
             ('deep_context', model.deep_context),
             ('deep_proj',    model.deep_proj),
             ('linout',       model.linout),
             ('tap',          model.tap),
             ('decoder',      model.decoder),
             ('head_norm',    getattr(model, 'head_norm', None)),
             ('lmhead',       model.lmhead)]
    seen, rows = set(), []
    for name, mod in named:
        if mod is None:
            continue
        tr = fr = 0
        for prm in mod.parameters():
            if id(prm) in seen:        # lmhead is TIED to tok_embed on GPT-Neo: count once
                continue
            seen.add(id(prm))
            if prm.requires_grad: tr += prm.numel()
            else:                 fr += prm.numel()
        if tr or fr:
            rows.append((name, tr, fr))
    o_tr = o_fr = 0
    for prm in model.parameters():
        if id(prm) in seen:
            continue
        seen.add(id(prm))
        if prm.requires_grad: o_tr += prm.numel()
        else:                 o_fr += prm.numel()
    if o_tr or o_fr:
        rows.append(('other', o_tr, o_fr))
    w = max(len(r[0]) for r in rows)
    out = ['PARAMS  ' + f'{"module":<{w}}  {"trainable":>13}  {"frozen":>13}  {"total":>13}']
    for name, tr, fr in rows:
        out.append(f'PARAMS  {name:<{w}}  {tr:>13,}  {fr:>13,}  {tr + fr:>13,}')
    t_tr = sum(r[1] for r in rows); t_fr = sum(r[2] for r in rows)
    out.append('PARAMS  ' + '-' * (w + 46))
    out.append(f'PARAMS  {"TOTAL":<{w}}  {t_tr:>13,}  {t_fr:>13,}  {t_tr + t_fr:>13,}')
    out.append(f'PARAMS  total {(t_tr + t_fr) / 1e6:.3f} M '
               f'({t_tr / 1e6:.3f} M trainable, {t_fr / 1e6:.3f} M frozen), '
               f'weights {(t_tr + t_fr) * 4 / 2**20:.1f} MiB at fp32')
    return '\n'.join(out)


_psum = _param_summary(model)
print(_psum)
if args.log:
    with open(args.log, 'a') as _f:
        print(_psum, file=_f)

if args.push:
    # one-shot: save the loaded checkpoint in HuggingFace format (model.safetensors +
    # config.json, from PyTorchModelHubMixin) and upload it to --hub_repo, then exit.
    # Needs a write token in the environment (huggingface-cli login, or HF_TOKEN).
    if args.load is None and args.pretrained is None:
        print('ERROR: --push requires --load (nothing to push but random weights)')
        raise SystemExit(1)
    if not hasattr(model, 'push_to_hub'):
        print('ERROR: --push requires huggingface_hub (pip install huggingface_hub)')
        raise SystemExit(1)
    local = os.path.basename(args.hub_repo)
    print(f'saving {args.load or args.pretrained} to ./{local} ...')
    model.to('cpu').save_pretrained(local)
    print(f'pushing to https://huggingface.co/{args.hub_repo} ...')
    # private=None (not False) when the flag is unset: that lets the hub apply the org's
    # default visibility for a new repo. Ignored if the repo already exists.
    model.push_to_hub(args.hub_repo, private=args.private or None)
    print('done')
    raise SystemExit(0)

# ── eval ──────────────────────────────────────────────────────────────────────

def _eval_source(name=None):
    """(repo, config, split, column) for --eval, with --split/--column overriding.

    `name` defaults to --dataset. It is passed explicitly by --eval_corpora, which scores a
    run against held-out sets it was NOT trained on -- the transfer measurement."""
    name = name or args.dataset
    if name in _TEXT_DATASETS:
        hf, cfg, split, col = _TEXT_DATASETS[name]
        held = _EVAL_SPLITS.get(name, split)
        # a triple redirects to a held-out set in another repo (see _EVAL_SPLITS)
        if isinstance(held, tuple):
            hf, cfg, split = held
        else:
            split = held
    else:                                    # not a short name: take it as a hub repo id
        hf, cfg, split, col = name, None, 'validation', 'text'
    return hf, cfg, (args.split or split), (args.column or col or 'text')


def _batched(it, n):
    it = iter(it)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


if args.eval and not args.eval_corpora:
    # One-shot validation loss over a WHOLE split, token-weighted. --eval_corpora instead
    # runs the exp/score.py protocol (fixed 400-doc sample, clean/median/runaway) further
    # down, which is the number that compares to a training run's EVAL lines.
    # One-shot validation loss. Every document is an independent batch row: its own fresh
    # DFF state, framed by clip_text() exactly as the training loop frames a clip, and every
    # step scored. Rows in a batch have different lengths, so short ones are padded out and
    # their padding is dropped from the loss -- padding cannot leak between rows, since the
    # CNN never mixes the batch dimension.
    if args.load is None and args.pretrained is None:
        print('WARNING: --eval without --load/--pretrained is measuring an untrained model')

    from datasets import load_dataset

    hf, cfg, split, col = _eval_source()
    if args.dataset not in _EVAL_SPLITS and not args.split:
        print(f'WARNING: no held-out split configured for "{args.dataset}"; scoring "{split}", '
              f'which the model was trained on -- that is a training loss, not a validation '
              f'loss. Pass --split to choose one explicitly')
    print(f'loading {hf}' + (f' [{cfg}]' if cfg else '') + f' split {split} ...')
    rows = load_dataset(hf, cfg, split=split, streaming=args.streaming)
    print('dataset ready')
    if args.examples:
        rows = itertools.islice(rows, args.examples)

    _fmt = _TEXT_FORMAT.get(args.dataset)    # corpora with no single text column (s1k)
    _dev = next(model.parameters()).device
    model.eval()

    nll = 0.0            # summed cross-entropy over every scored step, in nats
    ntok = nbyte = 0     # scored steps, and utf-8 bytes of the text they cover
    nex  = 0
    t0   = time.time()

    def _report(tag):
        # token-weighted mean over everything scored so far, not a mean of per-batch means:
        # documents differ in length, so those are not the same number.
        per_tok = nll / max(ntok, 1)
        print(f'{tag} examples {nex:8d} tokens {ntok:10d} bytes {nbyte:11d} '
              f'loss {per_tok:11.6f} ppl {math.exp(min(per_tok, 700)):12.4f} '
              f'bpb {nll / max(nbyte, 1) / math.log(2):9.6f} '
              f'wall {time.time() - t0:8.1f}s', flush=True)

    # Length bucketing: the recurrent loop runs once per step of the *longest* row, so a
    # batch of mixed lengths spends most of its steps on padding. Sorting a buffer of
    # BUCKET batches by length before splitting it up cuts that waste without changing the
    # result -- rows are independent and the loss is a sum over valid steps only.
    BUCKET = 8

    # --monitor counts scored batches, not buffers: one batch is B*T recurrent forwards and
    # can run for minutes on cpu, so it is the smallest unit that can honestly be reported.
    nb, last_report = 0, -1

    for buf in _batched(rows, args.batch * BUCKET):
        clips = []
        for ex in buf:
            text = (_fmt(ex) if _fmt is not None else ex.get(col, ex.get('text', ''))) or ''
            if not text.strip():
                continue
            steps, _ = clip_text(text)        # [(x, y), ...], the training framing
            if steps:
                clips.append((steps, len(text.encode('utf-8'))))
        clips.sort(key=lambda c: len(c[0]))

        for chunk in _batched(clips, args.batch):
            B = len(chunk)
            T = max(len(s) for s, _ in chunk)
            if args.monitor and (nb % args.monitor) == 0:
                # announced before the work, not after: on a deep model this is the line that
                # shows the run is alive and how much it has bitten off
                print(f'EVAL batch {nb:8d} rows {B:4d} steps {T:6d} scoring ...', flush=True)
            X = torch.zeros((B, T), dtype=torch.long)
            Y = torch.zeros((B, T), dtype=torch.long)
            M = torch.zeros((B, T), dtype=torch.bool)
            for r, (steps, _) in enumerate(chunk):
                X[r, :len(steps)] = torch.tensor([s[0] for s in steps], dtype=torch.long)
                Y[r, :len(steps)] = torch.tensor([s[1] for s in steps], dtype=torch.long)
                M[r, :len(steps)] = True
            X, Y, M = X.to(_dev), Y.to(_dev), M.to(_dev)

            model.dff = None                  # fresh context per document (see _new_dff/--init)
            b_nll = torch.zeros((), device=_dev)
            with torch.no_grad():
                for t in range(T):
                    logits, _ = model(X[:, t])            # targets=None: keep per-row losses
                    ce = F.cross_entropy(logits, Y[:, t], reduction='none')
                    b_nll += (ce * M[:, t]).sum()         # accumulate on device, one sync/batch

            nll   += float(b_nll)
            ntok  += int(M.sum())
            nbyte += sum(b for _, b in chunk)
            nex   += B
            nb    += 1

            if args.monitor and ((nb - 1) % args.monitor) == 0:
                _report('EVAL')
                last_report = nb

    if ntok:
        if last_report != nb:                 # skip a line that would just repeat the last
            _report('EVAL')
        print(f'\n{args.load or args.pretrained or "(untrained)"} '
              f'[--tokenizer {args.tokenizer}] on {hf} [{split}]:')
        print(f'  loss {nll / ntok:.6f} nats/token   ppl {math.exp(min(nll / ntok, 700)):.4f}')
        # bits per byte normalizes out the tokenizer, so it is the number that compares a
        # byte-vocabulary run against a BPE run (or against gptneo.py's transformer).
        print(f'  bpb  {nll / nbyte / math.log(2):.6f} bits/byte '
              f'over {nex} documents, {ntok} tokens, {nbyte} bytes')
    else:
        print('EVAL: no usable documents')

    if not (args.generate or args.vis or args.altvis):
        raise SystemExit(0)

if args.generate:
    # one-shot text generation: prompt = START + args.prompt, print the decoded
    # continuation, then exit. No dataset, worker, optimizer or training loop.
    # Same seeding as --vis and the training-loop sampler, and the same [START]+text
    # framing the model is trained on, so the output always opens with <STX>.
    if args.load is None and args.pretrained is None:
        print('WARNING: --generate without --load/--pretrained is running an untrained model')
    prompt = _prompt_ids()
    out    = model.generate(prompt, args.n, temperature=args.temperature)
    print(_render(prompt + out))
    raise SystemExit(0)

# ── vis setup ─────────────────────────────────────────────────────────────────

_vis_exit        = False
_vis_stats_line  = 'initializing...'
_VIS_WIN         = 180   # ticker-tape display width, in characters (display only)
_AV_WIN          = 220   # --altvis draws a longer tape (its figure is taller, not wider)
_VIS_HDR_PT      = 7     # header/ticker point size, both displays


def _ticker_width_in(nchars, pt=_VIS_HDR_PT, left=0.01, slack=1.04):
    """Figure width, in inches, that fits `nchars` monospace characters on one line.

    The ticker is the widest thing either display draws and it does not wrap, so a figure
    sized for the PANELS alone clips it -- which is what --altvis did at --n_layers 1,
    where its width is 4*n_layers = 4 inches against a 220-character tape. DejaVu Sans
    Mono advances 0.602 em; the margin and a little slack are added on top."""
    return (nchars * pt * 0.602 / 72.0) / (1.0 - left) * slack


def _vc(t):
    """Single-token renderer for the vis ticker. Same markers as _printable(), but with
    '$'/'\\' masked out: the ticker is drawn as matplotlib text, where those trigger
    mathtext parsing. Byte mode renders the byte directly (no UTF-8 decode, since the
    ticker is fed one byte at a time); BPE mode decodes the one token."""
    if _tokenizer.is_char:
        if t == START: return STX_TEXT
        if t == END:   return ETX_TEXT
        if t == NULL:  return NULL_TEXT
        c = chr(t) if 32 <= t < 127 else DOT_TEXT
        return DOT_TEXT if c in '$\\' else c
    return ''.join(DOT_TEXT if c in '$\\' else c for c in _render([t]))


if args.altvis:
    # ── per-layer DFF map ──────────────────────────────────────────────────────
    # An n_layers x 2 grid: top row each layer's ContextCNN INPUT, bottom row its OUTPUT.
    # Every panel is the standard deviation ACROSS CHANNELS at each spatial position, so a
    # panel answers "where in the SxS grid does this tensor carry variation", not "how much".
    # A per-panel colour scale is deliberate: input and output live on different scales (the
    # output has been through a projection), and layers differ by more than the map's shape,
    # so a shared scale would flatten five of the six panels into noise.
    plt.style.use('dark_background')
    plt.ion()
    _NL = model.n_layers
    # 4in per layer for the panels, but never narrower than the ticker needs: at
    # --n_layers 1 the panel rule alone gives 4 inches and the tape is cut off at ~15% of
    # its length.
    _av_w = max(4 * _NL, _ticker_width_in(_AV_WIN + 8))
    _av_fig, _av_axes = plt.subplots(3, _NL, figsize=(_av_w, 10), squeeze=False)
    _av_fig.subplots_adjust(top=0.85, bottom=0.05, left=0.05, right=0.98,
                            hspace=0.25, wspace=0.12)
    # Row 3 is the REGISTER. Every register is written every step (there is no clock any
    # more), so what this row shows is how fast the state MOVES -- which is the --ema blend
    # rate, not a write schedule. Under --dff_every a layer may own no register at all, and
    # its panel says so rather than showing another layer's state.
    _sl_of = getattr(model, 'dff_slot', {c: c for c in range(_NL)})
    _emas  = model.ema if isinstance(model.ema, (list, tuple)) else None
    for _r, _lbl in enumerate(('input', 'output', 'state')):
        for _c in range(_NL):
            _ax = _av_axes[_r][_c]
            if _lbl == 'state':
                if _c in _sl_of:
                    _e = (_emas[_sl_of[_c]] if _emas else
                          (model.ema if model.ema is not None else 1.0))
                    _t = (f'layer {_c + 1} DFF state std  (ema {_e:.4g}, '
                          f'~{1.0 / _e:.0f} tok window)')
                else:
                    _t = f'layer {_c + 1}: no register (--dff_every)'
            else:
                _t = f'layer {_c + 1} DFF {_lbl} std / {model.n_hidden} ch'
            _ax.set_title(_t, fontsize=8, pad=3)
            _ax.set_xlabel(str(model.S), fontsize=7)
            _ax.set_ylabel(str(model.S), fontsize=7)
            _ax.set_xticks([]); _ax.set_yticks([])
    _av_imgs   = [[None] * _NL for _ in range(3)]
    _av_vmax   = [[None] * _NL for _ in range(3)]   # slow-tracking scale, as --vis does
    _av_header = _av_fig.text(0.01, 0.99, '', family='monospace', fontsize=7,
                              va='top', ha='left')

    def _av_on_key(event):
        global _vis_exit
        if event.key in ('x', 'X'):
            _vis_exit = True
    _av_fig.canvas.mpl_connect('key_press_event', _av_on_key)

    def _std_map(t):
        """[1, C, S, S] -> [S, S] std across the channel axis."""
        return t[0].std(dim=0).detach().float().cpu().numpy()

    model.eval()
    _dev    = next(model.parameters()).device
    _prompt = _prompt_ids()
    _ptext  = _render(_prompt)
    _queue  = list(_prompt)
    _b      = _queue.pop(0)
    _ticker = _ptext
    _nstep  = 0
    dff     = model._new_dff(1, _dev)
    clk     = model._new_writer(1, _dev)

    while not _vis_exit:
        rec = []
        with torch.no_grad():
            bi   = torch.tensor([_b], dtype=torch.long, device=_dev)
            tok  = model.tok_embed(bi).view(1, model.c_text, 1, 1).expand(-1, -1, model.S, model.S)
            stack, new_ctx = model._layers(dff, tok, clk, record=rec)
            dff    = [d.detach().clone() for d in stack]
            logits = model.readout(model.decoder(new_ctx))
        _nstep += 1
        prob = F.softmax(logits[0] / max(args.temperature, 1e-6), dim=-1)

        for _r in range(3):
            for _c in range(_NL):
                if _r == 2:
                    # the register itself, after this step's blend. A straight-through layer
                    # has none, so its panel stays blank rather than borrowing a neighbour's.
                    m = (_std_map(dff[_sl_of[_c]]) if _c in _sl_of
                         else np.zeros_like(_std_map(rec[_c]['out'])))
                else:
                    m = _std_map(rec[_c]['in' if _r == 0 else 'out'])
                # ease the colour ceiling upward and let it decay, so a single spike does not
                # permanently wash the panel out and a quiet stretch still fills the range
                hi = float(m.max())
                _av_vmax[_r][_c] = hi if _av_vmax[_r][_c] is None else \
                    max(hi, 0.97 * _av_vmax[_r][_c])
                if _av_imgs[_r][_c] is None:
                    _av_imgs[_r][_c] = _av_axes[_r][_c].imshow(
                        m, cmap=args.cmap, interpolation='nearest',
                        vmin=0.0, vmax=max(_av_vmax[_r][_c], 1e-9))
                else:
                    _av_imgs[_r][_c].set_data(m)
                    _av_imgs[_r][_c].set_clim(0.0, max(_av_vmax[_r][_c], 1e-9))

        _av_header.set_text(
            f'step {_nstep}   ' + '   '.join(
                f'L{c+1} in {rec[c]["in"].std().item():6.3f} out {rec[c]["out"].std().item():6.3f} '
                + (f'state {dff[_sl_of[c]].std().item():6.3f}' if c in _sl_of else 'no reg')
                for c in range(_NL))
            + '\n' + _ticker[-_AV_WIN:])

        if _queue:
            _b = _queue.pop(0)
        else:
            nxt = int(torch.multinomial(prob, 1).item())
            if nxt == model.end_id:
                _ticker += ETX_TEXT
                dff    = model._new_dff(1, _dev)
                clk    = model._new_writer(1, _dev)
                _queue = list(_prompt)
                _b     = _queue.pop(0)
                _ticker += _ptext
            else:
                if nxt != model.null_id:
                    _ticker += _vc(nxt)
                _b = nxt
            _ticker = _ticker[-_VIS_WIN:]

        plt.pause(max(args.delay, 1e-3))
        if not plt.fignum_exists(_av_fig.number):
            break
    raise SystemExit(0)


if args.vis:
    # P(next token) is drawn as a near-square grid of the whole vocabulary: exactly 16×16
    # for the 256 bytes, and for a BPE vocabulary the smallest grid that covers it (50257
    # → 225×224), with the leftover cells zero-padded.
    _PROB_R = int(math.ceil(math.sqrt(model.vocab)))
    _PROB_C = int(math.ceil(model.vocab / _PROB_R))

    def _prob_grid(prob):
        a = np.zeros(_PROB_R * _PROB_C, dtype=np.float32)
        p = prob.detach().cpu().numpy()
        a[:p.shape[0]] = p
        return a.reshape(_PROB_R, _PROB_C)

    plt.style.use('dark_background')
    plt.ion()
    # 12in fits the three panels comfortably; the max() guarantees the tape fits too, so
    # raising _VIS_WIN later cannot silently start clipping it.
    _vis_fig, _vis_axes_grid = plt.subplots(
        1, 3, figsize=(max(12, _ticker_width_in(_VIS_WIN + 5)), 4))
    _vis_fig.subplots_adjust(top=0.78, bottom=0.10, left=0.04, right=0.98,
                              hspace=0.1, wspace=0.08)
    _vis_ax_dff, _vis_ax_zero, _vis_ax_prob = _vis_axes_grid
    _vis_ax_dff.set_title('DFF std / {:d} ch'.format(model.n_hidden), fontsize=8, pad=2)
    _vis_ax_zero.set_title('DFF zeros / {:d} ch'.format(model.n_hidden), fontsize=8, pad=2)
    _vis_ax_prob.set_title('P(next token)', fontsize=8, pad=2)
    # row/column dimension labels (e.g. "7"): DFF state is S×S, prob is the vocabulary grid.
    _vis_ax_dff.set_xlabel(str(model.S),  fontsize=7); _vis_ax_dff.set_ylabel(str(model.S),  fontsize=7)
    _vis_ax_zero.set_xlabel(str(model.S), fontsize=7); _vis_ax_zero.set_ylabel(str(model.S), fontsize=7)
    _vis_ax_prob.set_xlabel(str(_PROB_C), fontsize=7); _vis_ax_prob.set_ylabel(str(_PROB_R), fontsize=7)
    _vis_img_dff  = None
    _vis_img_zero = None
    _vis_img_prob = None
    _vis_dff_vmax = None   # slow-tracking color scale for the DFF-std panel (see set_clim below)
    _vis_header   = _vis_fig.text(0.01, 0.99, _vis_stats_line,
                                   family='monospace', fontsize=7,
                                   va='top', ha='left')

    # header font is in points (fixed); scale it with window width so the monospace
    # ticker keeps filling the same fraction of the figure when the window resizes.
    _vis_hdr_base_pt = 7
    _vis_w0          = _vis_fig.get_size_inches()[0] * _vis_fig.dpi
    def _scale_header(event=None):
        w = event.width if event is not None else _vis_w0
        _vis_header.set_fontsize(max(_vis_hdr_base_pt * w / _vis_w0, 4.0))
    _vis_fig.canvas.mpl_connect('resize_event', _scale_header)
    _scale_header()

    def _on_key(event):
        global _vis_exit
        if event.key in ('x', 'X'):
            _vis_exit = True
    _vis_fig.canvas.mpl_connect('key_press_event', _on_key)

    # ── live text-generation visualization (no training) ───────────────────────
    # Feed the prompt (START, plus --prompt if given) then autoregressively sample,
    # rendering the DFF-std and P(next token) panels for every generated byte. The header
    # shows a stats line and the generated text. Read-only: no dataset, optimizer or worker.
    model.eval()
    _dev    = next(model.parameters()).device
    _prompt = _prompt_ids()
    _ptext  = _render(_prompt)  # rendered prompt, echoed at each episode start
    _queue  = list(_prompt)   # remaining prompt tokens to inject
    _b      = _queue.pop(0)   # current token being injected
    _ticker = _ptext          # ticker-tape display buffer (trailing _VIS_WIN chars)
    _nstep  = 0
    _rep    = 0               # --datarep: replicas of the current token drawn so far
    _acc    = None            # --gen_pool mean: probabilities pooled across them
    dff     = model._new_dff(1, _dev)
    clk     = model._new_writer(1, _dev)   # this episode's blend state

    while not _vis_exit:
        with torch.no_grad():
            bi   = torch.tensor([_b], dtype=torch.long, device=_dev)
            tok  = model.tok_embed(bi).view(1, model.c_text, 1, 1).expand(-1, -1, model.S, model.S)
            # ONE model step per FRAME, at every --datarep: the replicas are exactly what
            # this display exists to show -- the state settling within a token -- so they
            # are drawn, not collapsed. The token only ADVANCES on the last replica, so the
            # ticker still gains one character per token while the panels update N times.
            stack, new_ctx = model._layers(dff, tok, clk)          # last-layer output
            dff    = [d.detach().clone() for d in stack]
            logits = model.readout(model.decoder(new_ctx))
            if args.gen_pool == 'mean':                            # see --gen_pool
                _p   = F.softmax(logits, dim=-1)
                _acc = _p if _acc is None else _acc + _p
        _nstep += 1
        _rep  += 1
        _last  = _rep >= _DATAREP

        # The grid shows THIS replica's distribution as it forms; on the last replica it
        # shows the one actually sampled from (pooled under --gen_pool mean).
        _lg = (torch.log((_acc / _DATAREP).clamp_min(1e-20))
               if (_last and args.gen_pool == 'mean') else logits)
        prob = F.softmax(_lg[0] / max(args.temperature, 1e-6), dim=-1)

        if not _last:
            pass                           # thinking step: draw it, emit nothing
        elif _queue:
            _b = _queue.pop(0)             # still draining the prompt
        else:
            nxt = int(torch.multinomial(prob, 1).item())
            # --n does not apply here: --vis streams forever, so an episode runs until the
            # model emits END on its own and the next one starts from the prompt again.
            if nxt == model.end_id:
                _ticker += ETX_TEXT        # mark the episode break in the ticker
                dff    = model._new_dff(1, _dev)
                clk    = model._new_writer(1, _dev)
                _queue = list(_prompt)     # episode over: reset state, restart prompt
                _b     = _queue.pop(0)
                _ticker += _ptext          # new episode opens with <STX> again
            else:
                if nxt != model.null_id:   # null_id is None outside byte mode
                    _ticker += _vc(nxt)
                _b = nxt
            _ticker = _ticker[-_VIS_WIN:]  # slide + bound the visible window (ticker tape)

        if _last:                          # token consumed: start the next one's replicas
            _rep, _acc = 0, None

        # ── render ──────────────────────────────────────────────────────────
        # DFF-std panel shows the last layer's state (the one feeding the decoder).
        dff_std_map = new_ctx[0].cpu().std(dim=0).numpy()           # [S, S]
        # per-location sparsity: how many of the n_hidden channels are exactly 0 here
        zero_map    = (new_ctx[0] == 0).sum(dim=0).cpu().numpy()     # [S, S], 0..n_hidden
        prob_img    = _prob_grid(prob)                               # vocabulary → R×C grid
        _dff_mean, _dff_std, _dff_max, _ = _dff_stats(dff)
        _vis_header.set_text(
            ('step {:8d}  layers {:d}  dff_std {:6.4f}  dff_max {:7.3f}  p_max {:5.3f}  T {:.2f}').format(
                _nstep, model.n_layers, _dff_std, _dff_max,
                float(prob.max()), args.temperature)
            + '\n' + 'gen: ' + _ticker
        )

        if _vis_img_dff is None:
            _vis_img_dff = _vis_ax_dff.matshow(dff_std_map, cmap=args.cmap)
            _vis_ax_dff.set_xticks([]); _vis_ax_dff.set_yticks([])
        else:
            _vis_img_dff.set_data(dff_std_map)
        _fmax = float(dff_std_map.max())
        _vis_dff_vmax = _fmax if _vis_dff_vmax is None else max(_fmax, 0.98 * _vis_dff_vmax)
        _vis_img_dff.set_clim(0.0, _vis_dff_vmax or 1e-9)

        # fixed 0..n_hidden scale: absolute zero-count is more readable than an autoscale.
        if _vis_img_zero is None:
            _vis_img_zero = _vis_ax_zero.matshow(zero_map, cmap=args.cmap,
                                                 vmin=0, vmax=model.n_hidden)
            _vis_ax_zero.set_xticks([]); _vis_ax_zero.set_yticks([])
        else:
            _vis_img_zero.set_data(zero_map)

        if _vis_img_prob is None:
            _vis_img_prob = _vis_ax_prob.matshow(prob_img, cmap=args.cmap, vmin=0, vmax=1)
            _vis_ax_prob.set_xticks([]); _vis_ax_prob.set_yticks([])
            # overlay printable-ASCII (32..126) glyphs in white at each byte's 16×16 cell;
            # byte b is row b//16, col b%16 (matches the prob_img reshape order). Byte mode
            # only: a 225×224 BPE grid has cells too small for a glyph, and most tokens are
            # multi-character anyway.
            if _tokenizer.is_char:
                _vis_prob_txts = [
                    _vis_ax_prob.text(b % _PROB_C, b // _PROB_C, chr(b), color='white',
                                      ha='center', va='center', family='monospace')
                    for b in range(32, 127)
                ]
                # font size is in points (fixed), so rescale to the cell's pixel size on resize.
                def _scale_prob_text(event=None):
                    bb = _vis_ax_prob.get_window_extent()
                    cell_px = min(bb.width, bb.height) / 16.0   # one of 16×16 cells
                    pts = max(cell_px * 72.0 / _vis_fig.dpi * 0.55, 1.0)
                    for _t in _vis_prob_txts:
                        _t.set_fontsize(pts)
                _vis_fig.canvas.mpl_connect('resize_event', _scale_prob_text)
                _scale_prob_text()
        else:
            _vis_img_prob.set_data(prob_img)
        _vis_img_prob.set_clim(0, float(prob_img.max()) or 1e-9)

        _vis_fig.canvas.draw()        # synchronous: render every step (draw_idle coalesces
        _vis_fig.canvas.flush_events()  # frames when sleep blocks the GUI loop → skips steps)
        time.sleep(args.delay)

    raise SystemExit(0)

# ── optimizer ─────────────────────────────────────────────────────────────────

_trainable = [p for p in model.parameters() if p.requires_grad]

# --lr_mult scales the base lr per layer: layer 1 keeps base lr, each deeper layer is
# multiplied by an extra factor of --lr_mult. Layer 1 = {tok_embed, text_proj, context};
# deep layers 2..N = their (deep_context + deep_proj) unit; the decoder reads the last
# layer's output, so it rides the deepest lr. Groups carry a per-group 'lr' (its initial_lr)
# which LambdaLR then scales by the shared schedule factor. With --lr_mult 1.0 we pass the
# flat param list so the optimizer/checkpoint layout is byte-identical to before.
def _lr_scaled_groups(model, base_lr, mult):
    N      = model.n_layers
    layers = [[] for _ in range(N)]
    layers[0] += list(model.tok_embed.parameters())
    layers[0] += list(model.text_proj.parameters())
    layers[0] += list(model.context.parameters())
    if model.qproj is not None:             # --qproj read; write is frozen and filtered below
        for li in range(N):
            layers[li] += list(model.qproj[li].parameters())
    if model.tap is not None:               # --tap: each conv belongs to its own layer
        for li in range(N):
            layers[li] += list(model.tap[li].parameters())
    if model.deep_context is not None:
        for li in range(N - 1):
            layers[li + 1] += list(model.deep_context[li].parameters())
            layers[li + 1] += list(model.deep_proj[li].parameters())
    layers[-1] += list(model.decoder.parameters())
    layers[-1] += list(model.head_norm.parameters())   # empty for --head_norm none/batch2d
    layers[-1] += list(model.lmhead.parameters())      # empty for --tokenizer char (Identity)
    # Dedupe by identity: with --tokenizer tiny* --unfreeze, lm_head.weight IS tok_embed.weight
    # (GPT-Neo ties them), so it would otherwise land in both the first and the last group and
    # the optimizer would reject the duplicate.
    seen = set()
    groups = []
    for i, g in enumerate(layers):
        ps = [p for p in g if p.requires_grad and id(p) not in seen]
        seen.update(id(p) for p in ps)
        groups.append({'params': ps, 'lr': base_lr * (mult ** i)})
    return groups

# Only build per-layer optimizer groups when lr_mult scaling is active; otherwise pass the
# flat param list so the optimizer/checkpoint layout is byte-identical to before.
_params = _lr_scaled_groups(model, args.lr_max, args.lr_mult) if args.lr_mult != 1.0 else _trainable

# Per-layer summary: trainable params and lr, shown when --lr_mult scales the layers. Param
# counts come from the same grouping as the lr scaling (layer 1 includes tok_embed/text_proj;
# the last includes the decoder), so the columns add up to the trainable total.
if args.lr_mult != 1.0:
    _groups = _lr_scaled_groups(model, args.lr_max, args.lr_mult)
    _pc  = [sum(p.numel() for p in g['params']) for g in _groups]
    _lrs = [g['lr'] for g in _groups]
    _yw  = max(len('layer'), 1 + len(str(len(_groups))))   # 'L' + index, vs header label
    _pw  = max(len('params'), *(len(f'{p:,}')   for p in _pc))
    _lw  = max(len('lr'),     *(len(f'{lr:.9f}') for lr in _lrs))
    print(f'per-layer (lr_mult {args.lr_mult}):')
    print(f'  {"layer":<{_yw}}  {"params":>{_pw}}  {"lr":>{_lw}}')
    for _i in range(len(_groups)):
        print(f'  {"L" + str(_i + 1):<{_yw}}  {_pc[_i]:>{_pw},}  {_lrs[_i]:>{_lw}.9f}')

# Route lr/weight_decay/momentum to each optimizer's supported knobs: Rprop takes
# neither weight_decay nor momentum; Adagrad takes weight_decay but no momentum.
# --nesterov is SGD-only and needs a positive momentum -- torch raises on nesterov with
# momentum 0, so an inapplicable flag is reported and dropped rather than left to blow up.
# --beta1/--beta2 are adamw-only; report and drop them elsewhere rather than silently
# ignoring a flag the caller believes is taking effect.
_beta1 = 0.9 if args.beta1 is None else args.beta1
_beta2 = args.momentum if args.beta2 is None else args.beta2
if args.opt != 'adamw' and (args.beta1 is not None or args.beta2 is not None):
    print(f'WARNING: --beta1/--beta2 apply to --opt adamw, and this run is --opt {args.opt}; '
          f'ignored (use --momentum for sgd/rmsprop)')
_nesterov = args.nesterov and args.opt == 'sgd' and args.momentum > 0
if args.nesterov and not _nesterov:
    print(f'WARNING: --nesterov ignored: it applies to --opt sgd with --momentum > 0, '
          f'and this run is --opt {args.opt} --momentum {args.momentum}')
if args.opt == 'sgd':
    optimizer = torch.optim.SGD(_params, lr=args.lr_max, momentum=args.momentum,
                                weight_decay=args.weight_decay, nesterov=_nesterov)
elif args.opt == 'rmsprop':
    optimizer = torch.optim.RMSprop(_params, lr=args.lr_max,
                                    momentum=args.momentum, weight_decay=args.weight_decay, centered=True)
elif args.opt == 'rprop':
    optimizer = torch.optim.Rprop(_params, lr=args.lr_max)
elif args.opt == 'adagrad':
    optimizer = torch.optim.Adagrad(_params, lr=args.lr_max,
                                    weight_decay=args.weight_decay)
elif args.opt == 'adamw':
    # --beta1/--beta2 set the moment decays directly. --momentum stays the beta2 fallback
    # so every existing invocation and checkpoint keeps the behavior it was trained with.
    optimizer = torch.optim.AdamW(_params, lr=args.lr_max,
                                  betas=(_beta1, _beta2),
                                  weight_decay=args.weight_decay)
    print(f'adamw betas ({_beta1}, {_beta2})'
          + ('' if args.beta2 is not None else '  [beta2 from --momentum]'))

# ── scheduler ─────────────────────────────────────────────────────────────────
# Every --schedule oscillates between --lr_min and --lr_max. LambdaLR multiplies the
# optimizer base lr (--lr_max), so we express the absolute lr as a factor relative to it.
_lo, _hi = args.lr_min, args.lr_max
_warm    = max(1, args.lr_warmup)
_period  = max(1, args.lr_period)

def _lr_factor(step):
    if args.schedule == 'const':                       # fixed lr_max
        lr = _hi
    elif args.schedule == 'warmup':                    # ramp lr_min -> lr_max over lr_warmup, then hold
        # measured from the start of *this* run, not the global step: resuming a
        # checkpoint with --schedule warmup means "ease this run back in", so the
        # ramp restarts on every --load instead of being fast-forwarded past.
        lr = _lo + (_hi - _lo) * min((step - _start_step) / _warm, 1.0)
    elif args.schedule == 'step':                      # lr_min for lr_warmup steps, then lr_max
        lr = _lo if step < _warm else _hi
    elif args.schedule == 'linear':                    # ramp lr_min -> lr_max over lr_period, then hold
        lr = _lo + (_hi - _lo) * min(step / _period, 1.0)
    elif args.schedule == 'coswarm':                   # half-cosine lr_min -> lr_max over lr_period, then hold
        lr = _lo + (_hi - _lo) * (1.0 - math.cos(math.pi * min(step / _period, 1.0))) / 2.0
    elif args.schedule == 'triangle':                  # up over lr_warmup, down over lr_period, then hold lr_min
        if step < _warm:
            lr = _lo + (_hi - _lo) * (step / _warm)
        elif step < _warm + _period:
            lr = _hi + (_lo - _hi) * ((step - _warm) / _period)
        else:
            lr = _lo
    else:                                              # cosine: cyclic lr_min <-> lr_max, lr_period per cycle
        phase = (1.0 - math.cos(2.0 * math.pi * (step % _period) / _period)) / 2.0   # 0->1->0
        lr = _lo + (_hi - _lo) * phase
    return lr / _hi

# "plat" is not a closed-form schedule: the lr responds to the loss curve, so it is
# driven by _plat_update() in the training loop instead of a torch scheduler.
_plateau = args.schedule == 'plat'

# per-group floor, scaled so --lr_mult keeps its ratio as the lr decays
_min_lrs = [args.lr_min * (_g['lr'] / _hi) for _g in optimizer.param_groups]

# Loss history for the slope fit, binned one point per --checkpoint interval rather
# than one per step. --lr_period is meant to be long (1e6 steps), and binning is
# statistically free: the OLS slope's standard error is sigma*sqrt(12)/(T*sqrt(n)), so
# averaging C steps into one point cuts n by C and sigma by sqrt(C) — same SE, same
# test. It also keeps the window at ~1000 floats instead of 1e6, small enough to ride
# along in the checkpoint so a resumed run doesn't start its window over.
_plat_bins = max(2, _period // max(1, args.checkpoint))   # window length, in intervals
_plat_loss = collections.deque(_start_plat or [], maxlen=_plat_bins)

if _plateau and args.lr_period < 2 * args.checkpoint:
    # the window can never be finer than one point per --checkpoint interval
    print(f'WARNING: --lr_period {args.lr_period} < 2*--checkpoint {args.checkpoint}; '
          f'plat fits {_plat_bins} bins = {_plat_bins * args.checkpoint} steps')

def _plat_update():
    """Fit a line to the binned loss window; decay the lr if it is not going down.

    Called once per --checkpoint interval. The fit needs a full window (--lr_period
    steps of history), and a decay clears it — that is the cooldown: a single plateau
    cannot stack decays from overlapping windows, so the lr falls at most one
    --lr_rate factor per --lr_period steps. A non-negative slope means the loss has
    stalled (or is rising) across the whole window, so every group's lr is multiplied
    by --lr_rate, floored at its --lr_min. Returns (fitted change over the window, lr,
    decayed) for logging, or None while the window is still filling.
    """
    if len(_plat_loss) < _plat_bins:
        return None
    y     = np.asarray(_plat_loss, dtype=np.float64)
    slope = np.polyfit(np.arange(len(y), dtype=np.float64), y, 1)[0]
    decay = slope >= 0.0
    if decay:
        for _g, _min in zip(optimizer.param_groups, _min_lrs):
            _g['lr'] = max(_min, _g['lr'] * args.lr_rate)
        _plat_loss.clear()                    # cooldown: refill before deciding again
    # report the fitted total change across the window (nats), not the per-bin slope:
    # at these window sizes the slope itself is ~1e-9 and unreadable
    return slope * (len(y) - 1), optimizer.param_groups[0]['lr'], decay

scheduler = (None if _plateau else
             torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=_lr_factor))

# On resume, fast-forward the schedule to the checkpoint's step so the lr at the first
# continued step matches where the previous run left off (LambdaLR is stateless in step).
# Update the live optimizer lr and the scheduler's cached last_lr (what the STEP line
# reports). "plat" has no closed form in step, so it instead picks up the lr the
# checkpoint was saved at (its loss window still refills from scratch).
if _plateau:
    if _start_step and _start_lr:
        for _g, _min in zip(optimizer.param_groups, _min_lrs):
            _g['lr'] = max(_min, _start_lr * (_g['lr'] / _hi))
elif _start_step:
    scheduler.last_epoch = _start_step
    _lrs = [_base * _lr_factor(_start_step) for _base in scheduler.base_lrs]
    for _g, _lr in zip(optimizer.param_groups, _lrs):
        _g['lr'] = _lr
    scheduler._last_lr = _lrs

# ── data thread ───────────────────────────────────────────────────────────────

stop  = threading.Event()
q     = queue.Queue(maxsize=args.batch)
# One-shot modes set hf_dataset = None, and the worker immediately subscripts it. Before
# --eval_corpora existed the legacy --eval block exited above this line so it never ran;
# now it does, and the worker died in its thread with a TypeError traceback while the eval
# printed correct results around it. Harmless but indistinguishable from a real failure in
# a log, which is exactly the kind of thing that gets chased for an hour later.
if hf_dataset is None:
    w = None
else:
    w = threading.Thread(target=worker,
                         args=[stop, q, hf_dataset, args, _mix],
                         daemon=False)
    w.start()

# ── helpers ───────────────────────────────────────────────────────────────────

# ── gradient / explosion instrumentation ──────────────────────────────────────

def _gnorm(params):
    return sum(p.grad.detach().norm(2).item() ** 2
               for p in params if p.grad is not None) ** 0.5


def _wnorm(params):
    return sum(p.detach().norm(2).item() ** 2 for p in params) ** 0.5


def _gnorm_all(model):
    return sum(p.grad.detach().norm(2).item() ** 2
               for p in model.parameters()
               if p.grad is not None and p.requires_grad) ** 0.5


def _param_groups_named(model):
    """Trainable params split by submodule, for per-module norm reporting."""
    g = {'emb':  list(model.tok_embed.parameters()),
         'tprj': list(model.text_proj.parameters()),
         'ctx':  list(model.context.parameters()),
         'dec':  list(model.decoder.parameters())}
    if model.deep_context is not None:   # stacked layers 2..N (--n_layers)
        # deep_proj is None under --linout, which REPLACES it (see VLAModel.__init__). This
        # is reached from the non-finite-loss HALT path, so crashing here loses the gradient
        # diagnostic on exactly the runs that need it -- every --linout run that diverges.
        g['deep'] = list(model.deep_context.parameters())
        if model.deep_proj is not None:
            g['deep'] += list(model.deep_proj.parameters())
    if model.linout is not None:         # --linout: the 1x1 on the way up out of each layer
        g['linout'] = list(model.linout.parameters())
    if model.tap is not None:            # --tap: the 1x1 after each layer
        g['tap'] = list(model.tap.parameters())
    if not isinstance(model.lmhead, nn.Identity):   # pretrained tokenizer: borrowed lm_head
        g['head'] = list(model.head_norm.parameters()) + list(model.lmhead.parameters())
    return g


def _diag(model):
    return ' '.join(f'{n}:g{_gnorm(ps):.1e}/w{_wnorm(ps):.1e}'
                    for n, ps in _param_groups_named(model).items())

# ── in-training held-out eval (--eval_interval) ────────────────────────────────
# Why this exists as well as the one-shot --eval and exp/score.py: the one-shot modes score
# a checkpoint AFTER the fact, so a run only learns its held-out number once someone goes
# and measures it, and the train/eval GAP -- the signal that killed both Phase 1 promotions
# -- is invisible while the run is in flight. This puts it in the log next to the training
# loss, on the same axis, every --eval_interval steps.
#
# The document set is built ONCE and reused, so successive EVAL lines differ only by the
# weights. Rebuilding it per eval (or streaming a fresh slice each time) would make the
# series a walk over documents as much as over training, which is exactly the confound
# that makes an eval curve unreadable.

_eval_docs_cache = {}        # corpus -> [[(x, y), ...], ...], built once per corpus
_eval_results    = {}        # corpus -> last scored result, for the --eval_corpora table
_eval_failed     = {}        # corpus -> True once it has raised; per corpus, not global
_reason_cache    = {}        # benchmark -> items, built once
_reason_failed   = {}        # benchmark -> True once it has raised


def _eval_corpus_names():
    """Held-out sets to score, in order. --eval_corpora overrides; default is the training
    corpus alone, which is what every run before --eval_corpora existed did."""
    if args.eval_corpora:
        return [c.strip() for c in args.eval_corpora.split(',') if c.strip()]
    return [args.dataset]


def _build_eval_docs(corpus=None):
    """First --eval_docs held-out documents of `corpus`, framed as training clips."""
    from datasets import load_dataset
    corpus = corpus or args.dataset
    if corpus == 'synth':
        path = ensure_synth_eval(args.teacher, args.synth_eval_docs, args.synth_min,
                                 args.synth_max, args.teacher_batch, args.teacher_temp,
                                 args.teacher_topk, args.teacher_topp,
                                 args.teacher_device or args.device,
                                 args.teacher_rep_penalty)
        print(f'eval set: loading cached synthetic held-out {path}', flush=True)
        rows = load_dataset('json', data_files={'train': path}, split='train')
        docs = []
        for ex in rows:
            steps, _ = clip_text(ex.get('text') or '')
            if len(steps) >= _EVAL_MINLEN:
                docs.append(steps[:_EVAL_MAXLEN])
            if len(docs) >= args.eval_docs:
                break
        docs.sort(key=len)
        print(f'eval set: {len(docs)} documents, {sum(len(d) for d in docs)} tokens',
              flush=True)
        return docs
    hf, cfg, split, col = _eval_source(corpus)
    if corpus in _HASH_HOLDOUT:
        # scan the TRAIN stream and keep only the hashed-out documents -- the complement of
        # what _build_clip feeds the model. Streaming is fine here: the sample is small.
        print(f'eval set: {corpus} hashed hold-out (1/{_HOLDOUT_MOD} of {hf}'
              + (f' [{cfg}]' if cfg else '') + ') ...', flush=True)
        if corpus in _HUB_SUBSET:
            # must NOT go through load_dataset(repo, cfg): finephrase has 27k files and
            # resolving them takes longer than the eval itself. Use the same local subset
            # the trainer reads, so the hold-out is the complement of what training sees.
            _f = _hub_subset_files(corpus)
            rows = load_dataset('parquet', data_files={'train': _f}, split='train',
                                streaming=args.streaming)
        else:
            rows = load_dataset(hf, cfg, split=split, streaming=args.streaming)
        docs, seen = [], 0
        for ex in rows:
            seen += 1
            t = _corpus_text(corpus, ex)          # same filter training applies
            if not t.strip() or not _is_heldout(t):
                continue
            steps, _ = clip_text(t)
            if len(steps) >= _EVAL_MINLEN:
                docs.append(steps[:_EVAL_MAXLEN])
            if len(docs) >= args.eval_docs:
                break
        docs.sort(key=len)
        print(f'eval set: {len(docs)} documents, {sum(len(d) for d in docs)} tokens '
              f'(scanned {seen})', flush=True)
        return docs
    if corpus not in _EVAL_SPLITS and not args.split:
        print(f'WARNING: --eval_interval: no held-out split configured for "{corpus}"; '
              f'scoring "{split}"'
              + (' , which the model is TRAINING on -- that is a training loss, not a '
                 'validation loss' if corpus == args.dataset else ''))
    # A SLICED split ("train[-3000:]") cannot be streamed -- datasets rejects it with
    # "Bad split". web has no validation split and its held-out IS that slice, so streaming
    # is forced off for it regardless of --streaming. It is a download, but it is the same
    # tail exp/score.py uses and therefore the only web number comparable to PLAN.txt.
    _stream = args.streaming and '[' not in split
    print(f'eval set: loading {hf}' + (f' [{cfg}]' if cfg else '') + f' split {split}'
          + ('' if _stream else ' (non-streaming)') + ' ...', flush=True)
    rows = load_dataset(hf, cfg, split=split, streaming=_stream)
    # keyed on CORPUS, not args.dataset: this builder serves --eval_corpora, which scores
    # corpora the run is NOT training on. Keying it on the training set applied that set's
    # renderer to another corpus's rows -- _fmt_finephrase looking for 'rollout_results' in
    # a pile row -- so every row rendered '' and the corpus was dropped with "0 documents".
    # Cost the pile column of an entire 1B-token run. The hashed path above never had this
    # bug; it has always gone through _corpus_text(corpus, ex).
    _fmt = _TEXT_FORMAT.get(corpus)
    docs = []
    for ex in rows:
        text = (_fmt(ex) if _fmt is not None else ex.get(col, ex.get('text', ''))) or ''
        if not text.strip():
            continue
        steps, _ = clip_text(text)
        if len(steps) >= _EVAL_MINLEN:
            docs.append(steps[:_EVAL_MAXLEN])
        if len(docs) >= args.eval_docs:
            break
    # longest-first inside the chunking below wastes the least padding; rows are independent
    # and eval-mode BatchNorm uses running stats, so grouping does not change any per-document
    # result (batch invariance measured at 1e-4).
    docs.sort(key=len)
    print(f'eval set: {len(docs)} documents, {sum(len(d) for d in docs)} tokens', flush=True)
    return docs


def _heldout_eval(step):
    """Score every --eval_corpora held-out set, one tagged EVAL line each. Never raises:
    an eval failure must not take down a training run that is otherwise healthy."""
    for corpus in _eval_corpus_names():
        _heldout_eval_one(step, corpus)


def _heldout_eval_one(step, corpus):
    # Failure is tracked PER CORPUS. A global disable made one bad corpus silently cancel
    # every later one in the same call: web raised on a sliced split and c4 -- which is
    # fine -- was never scored at all, reported as "failed" in the table.
    if _eval_failed.get(corpus):
        return
    try:
        if corpus not in _eval_docs_cache:
            _eval_docs_cache[corpus] = _build_eval_docs(corpus)
        docs = _eval_docs_cache[corpus]
        if not docs:
            print(f'WARNING: --eval_interval: no usable held-out documents for "{corpus}"; '
                  f'skipping it')
            _eval_docs_cache[corpus] = []
            return

        _dev = next(model.parameters()).device
        _was_training = model.training
        # The training context must survive the eval untouched, and the context is BOTH
        # tensors: _init_dff() rebuilds self.dff and self.clk together whenever the batch
        # width changes (see vla.py's "a clock belongs to a context, not to the model").
        # Scoring at _EVAL_BATCH rows rebuilds both at that width; restoring only dff then
        # leaves _init_dff with a matching dff, so it skips the rebuild and the next
        # training step runs a 250-row batch against a 400-row clock. That is not a silent
        # error -- it raised at the first step after the first eval and killed the run.
        # try/finally, not a plain restore after the loop: the outer `except` below exists
        # so an eval failure cannot take down a healthy training run, but a failure raised
        # part-way through scoring would skip the restore and leave the model holding the
        # eval-width context -- turning the guard into the very crash it is meant to absorb.
        _saved_dff, _saved_clk = model.dff, model.clk
        model.eval()
        t0 = time.time()
        per_doc = []                    # mean nats/token for each document, kept separate
        bad_doc = []                    # per document: did ANY token exceed _EVAL_THRESH
        try:
          with torch.no_grad():
            for c in range(0, len(docs), _EVAL_BATCH):
                chunk = docs[c:c + _EVAL_BATCH]
                B = len(chunk); T = max(len(d) for d in chunk)
                X = torch.zeros((B, T), dtype=torch.long)
                Y = torch.zeros((B, T), dtype=torch.long)
                M = torch.zeros((B, T), dtype=torch.bool)
                for r, st in enumerate(chunk):
                    X[r, :len(st)] = torch.tensor([x for x, _ in st], dtype=torch.long)
                    Y[r, :len(st)] = torch.tensor([y for _, y in st], dtype=torch.long)
                    M[r, :len(st)] = True
                X, Y, M = X.to(_dev), Y.to(_dev), M.to(_dev)
                model.dff = None        # fresh context per document (see _new_dff/--init)
                rs = torch.zeros(B, device=_dev)
                bad = torch.zeros(B, dtype=torch.bool, device=_dev)
                for t in range(T):
                    logits, _ = model(X[:, t])
                    ce = F.cross_entropy(logits, Y[:, t], reduction='none')
                    # a diverged row produces inf/nan; map it to a large finite value so it
                    # is counted as runaway instead of poisoning every other row's sum
                    ce = torch.where(torch.isfinite(ce), ce, torch.full_like(ce, 1e30))
                    rs += ce * M[:, t]
                    # Runaway is ANY TOKEN over threshold, which is exactly what
                    # exp/score.py counts -- NOT "the document mean went over".  The mean
                    # criterion is far laxer and silently disagrees: at p1_pile step 5000 it
                    # reported 0.00% where score.py found 0.2%, and a web-trained checkpoint
                    # that score.py rates 26.0% runaway on pile would have read near zero.
                    # PLAN.txt treats runaway% as the primary countable metric, so an EVAL
                    # line must report the same statistic score.py does or the two cannot be
                    # compared -- and on a long run the EVAL line is the only one watching.
                    bad |= M[:, t] & (ce > _EVAL_THRESH)
                n = M.sum(dim=1).clamp(min=1)
                per_doc.append((rs / n).cpu().numpy())
                bad_doc.append(bad.cpu().numpy())
        finally:
            model.dff, model.clk = _saved_dff, _saved_clk
            if _was_training:
                model.train()

        per = np.concatenate(per_doc)
        bad = np.concatenate(bad_doc)
        clean = float(per[~bad].mean()) if (~bad).any() else float('nan')
        _eval_results[corpus] = dict(
            corpus=corpus, step=int(step), clean=clean, median=float(np.median(per)),
            ppl=float(math.exp(min(clean, 700))) if clean == clean else None,
            runaway_pct=100.0 * float(bad.mean()), nrun=int(bad.sum()), docs=int(len(per)),
            tokens=int(sum(len(d) for d in docs)))
        # clean/median/runaway, not a mean: three runaway documents out of 400 move a plain
        # mean by nine orders of magnitude and report a healthy model as destroyed.
        # the corpus tag is not decoration: with --eval_corpora these lines interleave, and
        # a fit number and a transfer number are not comparable to each other.
        d = ('EVAL step {:10} corpus {:8} clean {:11.6f} ppl {:12.4f} median {:11.6f} '
             'runaway {:6.2f}% nrun {:4d} docs {:5d} wall {:7.1f}s'
             ).format(step, corpus, clean,
                      math.exp(min(clean, 700)) if clean == clean else float('nan'),
                      float(np.median(per)), 100.0 * float(bad.mean()), int(bad.sum()),
                      len(per), time.time() - t0)
        print(d, flush=True)
        with open(args.log, 'a') as f:
            print(d, file=f)
    except Exception as e:
        print(f'WARNING: --eval_interval failed at step {step} on "{corpus}": {e!r}; '
              f'disabling THAT CORPUS, others continue', flush=True)
        _eval_failed[corpus] = True


# ── zero-shot multiple-choice reasoning eval (--reason_eval) ──────────────────
# Held-out LOSS cannot measure the thing this project now wants. If the goal is a model
# that REASONS and looks obscure facts up, then loss on a factual corpus actively rewards
# the opposite: a model that memorised Wikipedia scores better than one that reasons. So
# reasoning needs its own metric, scored the standard zero-shot way.
#
# Each item is a context plus N candidate continuations. Every candidate is scored by the
# summed log-probability of its tokens given the context, and the argmax is the answer.
#   acc       argmax of the TOTAL log-probability
#   acc_norm  argmax of the PER-TOKEN mean -- the headline, because it does not penalise
#             long candidates. Chance is 1/N: 25% for the 4-way sets, 50% for winogrande.
#
# winogrande is the purest test of the hypothesis: resolving "Sarah was a better surgeon
# than Maria so _ got the easier cases" needs plausibility judgement and no retrievable
# fact. arc_easy/obqa are grade-school SCIENCE and do lean on knowledge, so a low score
# there is ambiguous -- it may mean the model cannot reason, or simply does not know.
_REASON_BENCH = {
    'arc_easy':   ('allenai/ai2_arc', 'ARC-Easy', 'validation'),
    'arc_chal':   ('allenai/ai2_arc', 'ARC-Challenge', 'validation'),
    'obqa':       ('allenai/openbookqa', 'main', 'validation'),
    'winogrande': ('allenai/winogrande', 'winogrande_xs', 'validation'),
}


def _mc_items(bench, limit=0):
    """-> [(context, [candidate, ...], gold_index)]. One shape for every benchmark."""
    from datasets import load_dataset
    repo, cfg, split = _REASON_BENCH[bench]
    rows = load_dataset(repo, cfg, split=split)
    out = []
    for ex in rows:
        if bench == 'winogrande':
            # Standard partial evaluation: substitute the option into the blank and score
            # the text AFTER it. Scoring the whole sentence would compare candidates that
            # differ only in a shared prefix, which measures the option's unigram frequency
            # more than the resolution.
            sent = ex['sentence']
            if '_' not in sent:
                continue
            pre, post = sent.split('_', 1)
            cands = [pre + ex['option1'], pre + ex['option2']]
            # context differs per candidate here, so carry the pair and score `post`
            out.append((cands, [post, post], int(ex['answer']) - 1))
        else:
            q = ex.get('question') or ex.get('question_stem') or ''
            ch = ex['choices']
            texts, labels = ch['text'], ch['label']
            key = ex['answerKey']
            if key not in labels:
                continue
            out.append((q, [' ' + t for t in texts], labels.index(key)))
        if limit and len(out) >= limit:
            break
    return out


def _reason_eval(step):
    """Score every --reason_eval benchmark and log one MC line each. Never raises."""
    for bench in [b.strip() for b in (args.reason_eval or '').split(',') if b.strip()]:
        if _reason_failed.get(bench):
            continue
        try:
            if bench not in _reason_cache:
                _reason_cache[bench] = _mc_items(bench, args.reason_docs)
            items = _reason_cache[bench]
            _dev = next(model.parameters()).device
            was = model.training
            _saved_dff, _saved_clk = model.dff, model.clk
            model.eval()
            t0 = time.time()
            try:
                rows, owner = [], []
                for qi, (ctx, cands, gold) in enumerate(items):
                    for ci, cand in enumerate(cands):
                        c = ctx[ci] if isinstance(ctx, list) else ctx
                        cid = [_tokenizer.start_id] + _tokenizer.encode(c)
                        aid = _tokenizer.encode(cand)
                        if not aid:
                            aid = [_tokenizer.end_id]
                        rows.append((cid, aid))
                        owner.append((qi, ci))
                tot = np.zeros(len(rows)); cnt = np.zeros(len(rows))
                with torch.no_grad():
                    for s0 in range(0, len(rows), _EVAL_BATCH):
                        chunk = rows[s0:s0 + _EVAL_BATCH]
                        B = len(chunk)
                        T = max(len(c) + len(a) for c, a in chunk)
                        X = torch.zeros((B, T), dtype=torch.long)
                        Y = torch.zeros((B, T), dtype=torch.long)
                        M = torch.zeros((B, T), dtype=torch.bool)
                        for r, (c, a) in enumerate(chunk):
                            seq = c + a
                            X[r, :len(seq) - 1] = torch.tensor(seq[:-1])
                            Y[r, :len(seq) - 1] = torch.tensor(seq[1:])
                            # score ONLY the candidate's own tokens
                            M[r, len(c) - 1:len(seq) - 1] = True
                        X, Y, M = X.to(_dev), Y.to(_dev), M.to(_dev)
                        model.dff = None
                        acc = torch.zeros(B, device=_dev)
                        for t in range(T):
                            # --datarep: N steps per token, scored on the last replica --
                            # the same contract training and generate() use
                            for _ in range(_DATAREP):
                                lg, _ = model(X[:, t])
                            lp = -F.cross_entropy(lg, Y[:, t], reduction='none')
                            lp = torch.where(torch.isfinite(lp), lp, torch.full_like(lp, -1e30))
                            acc += lp * M[:, t]
                        tot[s0:s0 + B] = acc.cpu().numpy()
                        cnt[s0:s0 + B] = M.sum(dim=1).clamp(min=1).cpu().numpy()
            finally:
                model.dff, model.clk = _saved_dff, _saved_clk
                if was:
                    model.train()
            nq = len(items)
            best_t = [None] * nq; best_n = [None] * nq
            for i, (qi, ci) in enumerate(owner):
                if best_t[qi] is None or tot[i] > best_t[qi][1]:
                    best_t[qi] = (ci, tot[i])
                nrm = tot[i] / cnt[i]
                if best_n[qi] is None or nrm > best_n[qi][1]:
                    best_n[qi] = (ci, nrm)
            golds = [g for _, _, g in items]
            a1 = float(np.mean([best_t[i][0] == golds[i] for i in range(nq)]))
            a2 = float(np.mean([best_n[i][0] == golds[i] for i in range(nq)]))
            nch = len(items[0][1])
            d = ('MC   step {:10} bench {:11} acc {:6.4f} acc_norm {:6.4f} '
                 'chance {:6.4f} n {:5d} wall {:6.1f}s'
                 ).format(step, bench, a1, a2, 1.0 / max(nch, 1), nq, time.time() - t0)
            print(d, flush=True)
            with open(args.log, 'a') as f:
                print(d, file=f)
        except Exception as e:
            print(f'WARNING: --reason_eval "{bench}" failed at step {step}: {e!r}; '
                  f'disabling that benchmark', flush=True)
            _reason_failed[bench] = True


# ── one-shot protocol eval (--eval --eval_corpora) ────────────────────────────
# Offline scoring of a checkpoint against any number of held-out sets, using EXACTLY the
# measurement the training loop writes as EVAL lines: the same 400-document sample, the same
# clean/median/runaway definition, the same per-token runaway criterion exp/score.py uses.
# That is the point -- a number produced here is directly comparable to a run's own EVAL
# curve and to every other checkpoint scored this way, which the whole-split --eval is not
# (it is token-weighted over a different, much larger set).
#
#   python vla.py --eval --load checkpoint/foo.pt --eval_corpora c4,pile,web --streaming
#
# Note on c4 for a gpt2-teacher run: GPT-2 was trained on WebText, NOT on C4 (C4 is T5's
# corpus). The open replication of WebText is Skylion007/openwebtext == --dataset web, so
# `web` is the closer probe of what a gpt2 teacher's text resembles; c4 is a second,
# independent crawl-derived corpus and is useful precisely because it is NOT that.
if args.eval and args.eval_corpora:
    if args.load is None and args.pretrained is None:
        print('WARNING: --eval without --load/--pretrained is measuring an untrained model')
    print(f'protocol eval: {args.eval_docs} docs, minlen {_EVAL_MINLEN}, maxlen '
          f'{_EVAL_MAXLEN}, runaway >{_EVAL_THRESH} nats on ANY token', flush=True)
    _heldout_eval(_start_step)
    if args.reason_eval:
        _reason_eval(_start_step)

    _ck = args.load or args.pretrained or '(untrained)'
    print(f'\n{"="*86}\nPROTOCOL EVAL  {_ck}  step {_start_step}\n{"="*86}')
    print(f'{"corpus":10} {"clean":>10} {"ppl":>11} {"median":>10} {"runaway%":>9} '
          f'{"nrun":>5} {"docs":>6} {"tokens":>9}')
    print('-' * 86)
    for _c in _eval_corpus_names():
        r = _eval_results.get(_c)
        if r is None:
            print(f'{_c:10} {"(failed or empty -- see WARNING above)":>50}')
            continue
        print(f'{r["corpus"]:10} {r["clean"]:10.4f} {r["ppl"]:11.2f} {r["median"]:10.4f} '
              f'{r["runaway_pct"]:9.2f} {r["nrun"]:5d} {r["docs"]:6d} {r["tokens"]:9d}')
    print('-' * 86)
    # Corpora are NOT comparable to each other: each has its own information floor (pile
    # unigram 7.9470 vs web 7.5732), so a lower number on one corpus does not mean the model
    # is better there. Compare a corpus against ITSELF across checkpoints.
    print('note: compare a corpus across checkpoints, never across corpora -- each has its'
          '\n      own floor (pile unigram 7.9470, web 7.5732; pile bigram 6.3511, web 5.8279)')
    if args.eval_json:
        with open(args.eval_json, 'w') as _f:
            json.dump({'checkpoint': _ck, 'step': int(_start_step),
                       'eval_docs': args.eval_docs, 'minlen': _EVAL_MINLEN,
                       'maxlen': _EVAL_MAXLEN, 'thresh': _EVAL_THRESH,
                       'results': _eval_results}, _f, indent=1)
        print(f'wrote {args.eval_json}')
    raise SystemExit(0)


# ── training loop ─────────────────────────────────────────────────────────────

larr, garr = [], []
carr = []             # --clip: 1.0 on steps whose grad norm hit the limit
varr = []             # --vocab_slots: per-step loss over the vocab slots alone
i = _start_step        # continue the step count from the resumed checkpoint (0 if fresh)
# cumulative count of training examples (one <STX>..<ETX> clip) begun, over all slots;
# a slot's flag is True on the step it emits its <STX>, so summing flags counts examples.
n_examples = _start_exs
_plat_sum, _plat_n = 0.0, 0    # running mean of this interval's losses, for the plat bin
# --gen_interval 0 keeps the pre-flag behaviour: one GEN sample per --checkpoint interval.
_gen_interval = args.gen_interval or args.checkpoint

# --preroll: throw away batches until the stream produces its first <ETX>. Cheap —
# it only drains the queue, no forward/backward — and it costs one clip's worth of
# tokens. Slots all begin their first clip together on step 0, so until the first
# clip ends the batch is `--batch` copies of the same opening; training through that
# is a correlated batch at the point the run is most sensitive to it. The first <ETX>
# is the shortest clip in the batch ending: from there each slot sits at a different
# offset in a different story and slots reload at staggered steps.
if args.preroll:
    _pre = 0
    while True:
        _, _y_list, _ = q.get()
        _pre += 1
        if model.end_id in _y_list:   # a slot just emitted the <ETX> target ending its clip
            break
    print(f'preroll: discarded {_pre} steps ({_pre * args.batch:,} tokens) '
          f'to reach the first <ETX>')

try:
    while True:
        # ── checkpoint / generation sample ───────────────────────────────────
        if (i % args.checkpoint) == 0:
            # --schedule plat: bin this interval's losses, then take one lr decision from
            # the slope over the whole window (see _plat_update). Ahead of the save below,
            # so the checkpoint carries the post-decision lr and window.
            if _plateau:
                if _plat_n:
                    _plat_loss.append(_plat_sum / _plat_n)
                _plat_sum, _plat_n = 0.0, 0
                _pu = _plat_update()
                if _pu is not None:
                    d = ('PLAT step {:10} fit {:+12.6f} lr {:10.9f} bins {}/{} {}'
                         ).format(i, _pu[0], _pu[1], len(_plat_loss), _plat_bins,
                                  'DECAY' if _pu[2] else 'hold')
                    print(d)
                    with open(args.log, 'a') as f:
                        print(d, file=f)

            _finite = all(torch.isfinite(p).all() for p in model.state_dict().values()
                          if p.is_floating_point())
            if _finite:
                # Embed the cumulative log so a later --load can prepend it and chart.py
                # sees one uninterrupted sequence across resumes. args.log already begins
                # with any log carried in from the checkpoint we resumed from.
                _log_text = ''
                if args.log and args.log != os.devnull and os.path.exists(args.log):
                    with open(args.log) as _lf:
                        _log_text = _lf.read()
                # 'lr'/'plat' carry --schedule plat across a resume: it has no closed form
                # to fast-forward, so it picks up the lr it was saved at and keeps filling
                # the same binned loss window instead of starting it over.
                torch.save({'saved_args': vars(args), 'state_dict': model.state_dict(),
                            'log': _log_text, 'step': i, 'examples': n_examples,
                            'lr': optimizer.param_groups[0]['lr'],
                            'plat': list(_plat_loss) if _plateau else None}, args.save)
            else:
                print(f'WARNING: non-finite params at step {i}; skipping checkpoint save')

            # text throughput for this checkpoint interval (examples/tokens consumed).
            # Stays in THIS block, not the generation block below: _text_drain() resets the
            # counters it reports, so draining it on the (faster) generation interval would
            # silently rescale every TEXT line. exp/watch.sh also triggers off 'TEXT step',
            # i.e. off checkpoints, which is what it is meant to track.
            # --refresh: the stall detector's state, on the checkpoint cadence. The verdict
            # itself only exists at an epoch boundary, which can be tens of thousands of
            # steps apart at --subsample 10000, so this reports the epoch-so-far mean and the
            # last verdict in between -- enough to see the detector converging toward still
            # rather than only learning about it when it fires.
            if args.refresh and not args.refresh_every:
                _mu, _ns, _nl, _lastv, _hold = _stab_peek()
                _lv = ('none yet' if _lastv is None else
                       f'{_lastv[0]:+.{args.refresh_r}f} (abs {_lastv[1]:.{args.refresh_r}f})')
                _ref = (f'eps {args.refresh_eps:g}' if args.refresh_mode == 'abs' else
                        'best ' + ('none' if _stab_best[0] is None
                                   else f'{_stab_best[0]:.{args.refresh_r}f}'))
                _tl = (f'TRIGGER step {i:10} mean_std {_mu:.4f} samples {_ns} layers {_nl} '
                       f'last_sum_delta {_lv} {args.refresh_mode} {_ref} '
                       f'still {_hold}/{args.refresh_hold}')
                print(_tl)
                with open(args.log, 'a') as f:
                    print(_tl, file=f)

            _te, _tt, _ = _text_drain()      # sample is read separately, see _text_peek
            if _te:
                d = f'TEXT step {i:10} examples {_te} tokens {_tt}'
                _ep = _epoch_report()          # passes over the corpus; the clock of a
                if _ep:                        # closed-corpus run, 'wdef=1' until it wraps
                    d += f' epoch {_ep}'
                print(d)
                with open(args.log, 'a') as f:
                    print(d, file=f)

        # ── held-out eval ─────────────────────────────────────────────────────
        # after the save, so the EVAL line in the log describes the weights that were just
        # written to disk and can be re-derived from that checkpoint with exp/score.py.
        # Skipped at step 0 (like exp/watch.sh's report): it would score the UNTRAINED model,
        # which is ln(vocab) by construction and already known -- measured 10.8221 against a
        # ln(50304) = 10.8258 ceiling. It is not free: 400 documents is ~137s on a 4090, and
        # it lands before the first training step, so the run looks hung for over two minutes
        # at every start with nothing in the log moving.
        if args.eval_interval and i > 0 and (i % args.eval_interval) == 0:
            _heldout_eval(i)
            if args.reason_eval:
                _reason_eval(i)

        # ── generation sample ─────────────────────────────────────────────────
        # own interval: text has repeatedly overturned what the scalars said (a model called
        # "bigram-level with zero semantics" was writing grammatical clauses), and sampling
        # 200 tokens is cheap next to writing 30M parameters to disk.
        if (i % _gen_interval) == 0:
            model.eval()
            # generate() runs on a LOCAL dff/clock (see Model.generate), so sampling several
            # prompts here cannot perturb the training state -- only cost time, and a batch-1
            # 200-token sample is trivial next to --gen_interval training steps.
            lines = []
            for _p in _gen_prompt_list():
                prompt = _prompt_ids(_p)
                out    = model.generate(prompt, _GEN_SAMPLE, temperature=args.temperature)
                lines.append(f'GEN step {i:10} [{_p or ("<NULL>" if args.gen_null else "<STX>")}]: {_render(prompt + out)}')
                if _gen_scorer is not None:
                    # score the DECODED generation, not the rendered line: _render escapes
                    # whitespace and inserts <STX>/<ETX>, none of which is text the model
                    # produced, and all of which the reference would be scoring instead.
                    _txt = _decode_plain(out)
                    _sc  = _gen_scorer.score(_txt)
                    if _sc:
                        lines.append(f'GENSCORE step {i:10} [{_p or ("<NULL>" if args.gen_null else "<STX>")}]: {_sc}')
            _tsample, _vsample = _text_peek()  # recent corpus / per-pool vocab training text
            _vw = max([len(k) for k in _vsample] + [6])
            for _k in sorted(_vsample):            # every curriculum file, every report
                lines.append(f'TXT-{_k:<{_vw}}: {_printable(_sample_window(_vsample[_k]))}')
            if _tsample:
                lines.append(f'TXT-{"SAMPLE":<{_vw}}: {_printable(_sample_window(_tsample))}')
            print('\n' + '\n'.join(lines) + '\n')
            with open(args.log, 'a') as f:
                print('\n' + '\n'.join(lines) + '\n', file=f)

        # ── fetch batch ───────────────────────────────────────────────────────
        x_list, y_list, flag_list = q.get()
        n_examples += sum(flag_list)
        x    = torch.tensor(x_list,    dtype=torch.long).to(args.device)
        y    = torch.tensor(y_list,    dtype=torch.long).to(args.device)
        flag = torch.tensor(flag_list, dtype=torch.bool).to(args.device)

        # ── train step ────────────────────────────────────────────────────────
        dff_prev = model.dff                                    # save pre-step DFF
        model.train()
        if args.refresh and not args.refresh_every:
            _stab_step[0] += 1     # --refresh: sample cadence, counted in TRAINING steps
        logits, loss = model(x, targets=y, flag=flag)

        # ── instrumentation: the vocab channel's loss, separately from the corpus ──────
        # The batch loss is dominated by the 249 corpus slots, so a single vocab slot is
        # invisible in it -- 0.4% of the mean. This is what says whether the channel is
        # being learned at all, and it is free: reduction='none' over the logits the
        # training forward already produced, no second forward and no gradient. There is no
        # loss_corpus column because the loss column already IS it to within that 0.4%.
        if _N_VOCAB:
            with torch.no_grad():
                _per = F.cross_entropy(logits, y.long(), reduction='none')
                varr.append(float(_per[:_N_VOCAB].mean()))

        # halt immediately on non-finite loss — do NOT backward/step/save, so the
        # last good checkpoint on disk is preserved.
        if not torch.isfinite(loss):
            print(f'\n*** HALT: non-finite loss at step {i} ***')
            print(f'  loss     = {loss.item()}')
            print(f'  dff_max  = {_dff_absmax(model.dff)}')
            print(f'  logit_max= {logits.detach().abs().max().item()}')
            print(f'  grads(prev step): {_diag(model)}')
            break

        loss.backward()

        # --clip rescales every gradient so the global norm is at most args.clip.
        # clip_grad_norm_ returns the norm measured BEFORE clipping, which is exactly what
        # _gnorm_all would have reported, so the logged grad column means the same thing
        # whether clipping is on or off -- and the non-finite halt below still sees the real
        # pre-clip norm rather than the zeros clipping would leave behind.
        if args.clip > 0:
            total_norm = float(torch.nn.utils.clip_grad_norm_(_trainable, args.clip))
            carr.append(1.0 if total_norm > args.clip else 0.0)
        else:
            total_norm = _gnorm_all(model)                     # grad norm BEFORE the step
        garr.append(total_norm)

        # halt before the optimizer corrupts weights if grads went non-finite
        if not math.isfinite(total_norm):
            print(f'\n*** HALT: non-finite grad at step {i} ***')
            print(f'  dff_max  = {_dff_absmax(model.dff)}')
            print(f'  logit_max= {logits.detach().abs().max().item()}')
            print(f'  per-module g(rad)/w(eight): {_diag(model)}')
            break

        optimizer.step()
        model.dff = dff_prev                                    # restore so eval recomputes same step
        model.eval()
        with torch.no_grad():
            _, _ = model(x, targets=y, flag=flag)              # recompute DFF using updated model

        # ── monitor ───────────────────────────────────────────────────────────
        larr.append(loss.item())
        if _plateau:
            _plat_sum, _plat_n = _plat_sum + larr[-1], _plat_n + 1   # binned at --checkpoint

        if (i % args.monitor) == 0:
            _dmean, _dstd, _dmax, _dzero = _dff_stats(model.dff)
            # batch is logged per step, not just in the ARGS line: a run resumed from a
            # checkpoint at a different --batch appends to a new log, so chart.py needs the
            # batch size that produced each point (loss/grad both scale with it).
            # The epoch column reports the VOCAB channel's own passes when that channel
            # exists: it is the finite, repeating stream, and the corpus alongside it is
            # effectively infinite (fineweb pins at 1 forever), so its passes are the only
            # epoch number that means anything in such a run. Without a vocab channel the
            # column is the corpus epoch, exactly as before.
            _ep_name, _ep_val = (('epoch_vocab', _epoch_vocab()) if _N_VOCAB
                                 else ('epoch', _epoch_num()))
            s = ('STEP {:10} wall {} loss {:12.9f} grad {:12.6f} '
                 'lr {:10.9f} dff_mean {:12.5f} dff_std {:12.5f} dff_max {:11.3f} '
                 'dff_zeros {:8.5f} batch {:6d} examples {:12d} {} {:10.3f}').format(
                i, datetime.datetime.now(),
                np.mean(larr[-args.monitor:]),
                np.mean(garr[-args.monitor:]),
                optimizer.param_groups[0]['lr'],
                _dmean, _dstd, _dmax, _dzero, args.batch, n_examples, _ep_name, _ep_val,
            )
            # appended only when clipping is on, so logs from non-clip runs stay byte-identical
            # (chart.py looks fields up by name and defaults a missing one to 0.0)
            if args.clip > 0:
                s += ' clipped {:8.5f}'.format(float(np.mean(carr[-args.monitor:])) if carr else 0.0)
            # loss_vocab / loss_corpus: the same monitor-window mean the loss column uses,
            # split by slot group. Present only under --vocab_slots, so logs from every
            # other run stay byte-identical (chart.py looks fields up by name).
            if _N_VOCAB and varr:
                s += ' loss_vocab {:12.9f}'.format(float(np.mean(varr[-args.monitor:])))
            print(s)
            with open(args.log, 'a') as f:
                print(s, file=f)

            # bound monitor history so host RAM stays flat over long runs (these are
            # only ever read as [-monitor:]; without this they grow once per step forever)
            for _a in (larr, garr, carr, varr):
                if len(_a) > args.monitor:
                    del _a[:-args.monitor]

        if not _plateau:            # plat drives the lr from the checkpoint block instead
            scheduler.step()
        optimizer.zero_grad()
        i += 1

        if args.run_steps is not None and (i - _start_step) >= args.run_steps:
            break   # --run_steps caps steps for this invocation, not the global count

except KeyboardInterrupt:
    pass

# ── shutdown ──────────────────────────────────────────────────────────────────

print('\nSTOPPING THREADS')
stop.set()
while not q.empty():
    q.get()
if w is not None:            # one-shot modes never started a worker (see above)
    w.join()
print('EXIT MAIN')

# Hard-exit after our work is flushed. Streaming datasets keep native aiohttp
# threads alive whose teardown races Python finalization (PyGILState_Release
# crash); os._exit skips finalization entirely. Everything is already saved.
import sys
sys.stdout.flush(); sys.stderr.flush()
os._exit(0)
