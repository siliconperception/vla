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
# that is concatenated with the token grid. An image-caption example is the caption alone,
# the image being the prompt; the image is present at every token, seen through a fresh
# random 224x224 crop each token:
# a close-up at native resolution (only an image with a side under 224 is scaled up, uniformly,
# to fill the crop) or, for --full_crops of them, a full view of the whole image scaled so its
# shorter side is 224; text-only rows get a zero image map.
#
# Built to be extended: the input side is a LIST of grids concatenated in front of ctx_cat, and
# the text readout is a self-contained decoder module that other decoders (e.g. actions) can
# sit beside.

import argparse
import bisect
import collections
import contextlib
import copy
import datetime
import glob
import io
import itertools
import shutil
import textwrap
import json
import math
import os
import queue
import random
import re
import subprocess
import signal
import sys
import threading
import time
_T0 = time.time()           # STARTUP: wall clock from here to the first training step
import zlib

import numpy as np
import torch ; print('torch', torch.__version__)
import torch.nn as nn
from torch.nn import functional as F

_DATA = os.environ.get('VLA_DATA', '/data')   # root of the local corpora and features (prep scripts write here)

NUL_TEXT = '<NUL>'          # how _NULL renders where it is named (GEN prompts, sample panel)
DOT_TEXT = '\xb7'           # how any other unprintable character renders
_ESCAPES = {'\n': '\\n', '\t': '\\t', '\r': '\\r'}

_GEN_SAMPLE = 300           # tokens in each periodic GEN sample (--n is for --generate)
_GENI_LEN = 100             # token cap on each GENI caption
_SAMPLE_CELLS = 10          # crop thumbnails in the TRAIN sample window (<NUL> + 9 tokens)
# Every example -- a text document or an image caption -- is <NUL> then its tokens: the first
# step reads _NULL, a "blink": a zero token grid AND a zero image grid for every row, text or
# image, and predicts the first token (so a caption's first token is predicted before its image
# is seen). The state resets there unless --continuous covers the example's kind. There are no START/END tokens, so the
# model never predicts the end of an example and generation is one continuous stream.
_NULL = -1
_PAD = -2                    # --clock_hz: a tick where nothing was said -- no token (a zero token
                             # grid) but, unlike the _NULL blink, the picture and sound stay on
_NUL_ID = None               # --clock_hz: the output id of <NUL> (the tokenizer's first unused
                             # embedding row), bound when the model is built; None = no <NUL> head
_SIL = None                  # --clock_hz: the target of a tick where nothing was said -- _NUL_ID
                             # with a <NUL> head, else -100 (--inner_voice: no loss on that tick)

# Held-out eval protocol constants (tools/score.py and PLAN.txt's reference table use the same
# selection). Pinned, not exposed: changing one makes EVAL lines incomparable with history.
_EVAL_MINLEN = 512          # documents shorter than this (in tokens) are skipped ...
_EVAL_MINLEN_SHORT = {'simplestories': 128}   # ... except on short-document corpora
_EVAL_MAXLEN = 1024         # and each is clipped to this many
_EVAL_BATCH = 400           # rows per eval forward chunk
_EVAL_THRESH = 20.0         # a document with ANY token above this many nats is "runaway"


def _eval_minlen(corpus):
    if corpus in _IMAGE_DATASETS or corpus in _VIDEO_DATASETS:
        return 1                    # captions are short; every held-out caption counts
    return _EVAL_MINLEN_SHORT.get(corpus, _EVAL_MINLEN)


# Image-caption corpora: a local directory of parquet files (see tools/img_prep.py,
# tools/caption_prep.py) with an encoded 'image', an 'id', a 'class' and the caption column(s).
_IMAGE_DATASETS = {
    'imagenet21k': dict(dir=_DATA + '/imagenet21k_recap', caption='recaption',    # synthetic
                        eval_group0=True),   # its eval set reads only row group 0 per file
    'redcaps':     dict(dir=_DATA + '/redcaps5m', caption='caption'),     # Reddit post titles
    'redcaps25':   dict(dir=_DATA + '/redcaps5m_25', caption='caption'),  # its first 25 shards
    'coco':        dict(dir=_DATA + '/coco_captions', caption='caption'), # 5 human captions/image
    # Wikipedia images: one example = the human caption, a newline, the Gemini description
    'wit':         dict(dir=_DATA + '/wit_1m_recap', caption=('caption', 'gemini_caption')),
    # wit filtered (tools/wit_score.py, tools/wit_filter.py): fineweb-edu classifier >= 2.5 on
    # the example text AND CLIP ViT-L/14 image-vs-human-caption >= 0.25
    'witq':        dict(dir=_DATA + '/witq', caption=('caption', 'gemini_caption')),
}


def _caption_cols(cfg):
    """An image corpus's caption column(s), as a list."""
    c = cfg['caption']
    return [c] if isinstance(c, str) else list(c)


def _caption_of(row, cfg):
    """The example text of a row: its caption columns' non-empty values, one per line."""
    return '\n'.join(t for t in ((row[c] or '').strip() for c in _caption_cols(cfg)) if t)

# --imagine: text-to-image models that invent the pictures of text rows, as
# key -> (hub repo, denoising steps, guidance scale); any other diffusers repo runs 1 step, no CFG
_IMAGINE_MODELS = {
    'sd-turbo':    ('stabilityai/sd-turbo', 1, 0.0),
    'sdxl-turbo':  ('stabilityai/sdxl-turbo', 1, 0.0),
    'sana-sprint': ('Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers', 2, 4.5),
}

# Captioned-video corpora (tools/video_prep.py): local parquet, one row per video, with JPEG
# frames at 'fps' (short side 224), Kyutai Mimi audio codes (12.5 Hz) and the caption timeline
# 'events' = [[start_s, end_s, kind, text]] ('act' scene activity, 'say' speech segment, 'cap'
# clip caption). Phase A (token-clocked): one step per caption token as for text; each token
# is placed in media time inside its event and the step that predicts it sees the frame and
# the last _AUD_WIN Mimi frames of sound at that time. train/eval: file globs; eval None =
# the id-hash held-out 1/_HOLDOUT_MOD of the training files.
_VIDEO_DATASETS = {
    'finevideo': dict(dir=_DATA + '/finevideo_feat', train='train-*.parquet', eval=None),
    'valor':     dict(dir=_DATA + '/valor_feat', train='train-*.parquet', eval='test-*.parquet'),
}                           # valor: deprecated 2026-10-17 (25k short clips, over-repeated)
_VID_EVAL_CLIPS = 64        # held-out videos per video eval corpus (decoded frames stay in RAM) ...
_VID_EVAL_MAXLEN = 512      # ... each its opening window of at most this many tokens
_VID_EVAL_SPAN = 60.0       # ... (--clock_hz: of at most this many seconds; 120 until v448)
_VID_EVAL_MINTOK = 20       # ... with at least this many caption tokens
_VID_MAXTOK = 2048          # a longer video example is a random window of whole events ...
_VID_MAXSPAN = 600.0        # ... that also spans at most this many seconds of media
_AUD_RATE = 12.5            # audio grid cells per second (a Mimi frame, 80 ms)
_AUD_DIM = 512              # Mimi latent width
_AUDIO_ENCODERS = {'mimi': 'kyutai/mimi',      # frozen; codes -> [512, T] latents
                   'quartznet': 'nvidia/stt_en_quartznet15x5',   # frozen; 16 kHz sound -> [1024, T]
                   'logmel': None}               # fixed DSP, no weights; 16 kHz sound -> [256, S, S]
_LM_MELS, _LM_FR = 64, 4    # logmel: 64 mels x 4 frames of 10 ms per grid cell (40 ms; 1.96 s at S=7)
_LM_NFFT, _LM_WIN, _LM_HOP = 512, 400, 160
_AUD_DIMS = {'mimi': _AUD_DIM, 'quartznet': 1024, 'logmel': _LM_MELS * _LM_FR}
_WAV_ENCODERS = ('quartznet', 'logmel')   # read the clean 16 kHz soundtrack (the sound buffers)
# logmel: per-mel mean / std of log power over 4.1M non-silent frames of 200 FineVideo soundtracks
_LM_MU = [
    -5.557, -4.207, -4.062, -3.739, -4.051, -4.060, -4.423, -4.360, -4.623, -4.697, -5.034,
    -5.224, -5.591, -5.875, -6.169, -6.390, -6.590, -6.815, -6.938, -7.172, -7.236, -7.373,
    -7.503, -7.507, -7.650, -7.706, -7.752, -7.803, -7.881, -7.845, -7.936, -7.975, -8.078,
    -8.181, -8.373, -8.464, -8.519, -8.612, -8.580, -8.592, -8.649, -8.758, -8.955, -9.102,
    -9.232, -9.337, -9.437, -9.543, -9.703, -9.925, -10.126, -10.346, -10.533, -10.756, -10.946,
    -11.077, -11.208, -11.324, -11.416, -11.497, -11.598, -11.764, -12.153, -12.838]
_LM_SD = [
    3.774, 3.627, 3.621, 3.570, 3.593, 3.608, 3.646, 3.685, 3.740, 3.777, 3.801, 3.801, 3.811,
    3.825, 3.807, 3.757, 3.726, 3.683, 3.655, 3.640, 3.627, 3.612, 3.613, 3.600, 3.600, 3.608,
    3.622, 3.611, 3.616, 3.593, 3.587, 3.585, 3.579, 3.567, 3.572, 3.557, 3.555, 3.582, 3.599,
    3.624, 3.652, 3.631, 3.600, 3.563, 3.557, 3.587, 3.628, 3.642, 3.652, 3.626, 3.612, 3.617,
    3.633, 3.636, 3.662, 3.667, 3.694, 3.688, 3.690, 3.649, 3.660, 3.673, 3.692, 3.669]
# --audio_encoder quartznet: NVIDIA's QuartzNet 15x5 CTC speech recognizer (NGC, CC-BY-4.0), all
# 1-D separable convs; its 1024-wide C3 features (50 Hz) of the clean soundtrack, which the
# sidecar corpus holds (tools/audio_prep.py) as 16 kHz FLAC joined to the video rows by id
_QN_URL = ('https://api.ngc.nvidia.com/v2/models/nvidia/nemo/stt_en_quartznet15x5/versions/'
           '1.0.0rc1/files/stt_en_quartznet15x5.nemo')
_QN_DIR = _DATA + '/huggingface/quartznet'
_QN_SR = 16000
_QN_HOP = int(_QN_SR / _AUD_RATE)      # samples per audio grid cell (1280)
_QN_WIN = 8 * _QN_SR        # each grid is computed from the last 8 s heard (it looks both ways)
_QN_FRAMES = 4              # quartznet: sound heard is counted in its 20 ms frames, 4 per grid cell
_AUD_SIDECAR = {'finevideo': _DATA + '/finevideo_audio'}
_VCAP_SIDECAR = {'finevideo': _DATA + '/finevideo_vcap'}   # --fifo3: visual captions (tools/vcap_prep.py)
_ALIGN_SIDECAR = {'finevideo': _DATA + '/finevideo_align'}  # --speech_align: word times (tools/align_prep.py)
_VCAP_SAME = 0.6             # --fifo3: a caption whose word overlap (Jaccard) with one of the last 3
                             # kept exceeds this repeats it and is dropped

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
    """A pretrained BPE tokenizer (its vocabulary, embedding and lm_head are borrowed)."""

    def __init__(self, repo, vocab_size):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(repo)
        self.tok.model_max_length = int(1e12)   # recurrent: no context window, never truncate
        self.vocab_size = vocab_size            # the embedding's rows, not len(tokenizer)

    def encode(self, text): return self.tok.encode(text, add_special_tokens=False)
    def decode(self, ids):  return self.tok.decode(ids)


_tokenizer = None           # bound to model.tok once the model is built


def _printable(s):
    """Escape whitespace and mask unprintable characters for one-line display."""
    return ''.join(_ESCAPES.get(c, c if c.isprintable() else DOT_TEXT) for c in s)


def _decode_plain(ids):
    """Token ids -> plain text, _NULL / _PAD / <NUL> dropped (what a judge LM reads)."""
    body = [t for t in ids if t >= 0 and t != _NUL_ID]
    return _tokenizer.decode(body) if body else ''


def _truncate(prob):
    """--top_k: zero every word outside the K most likely; --min_p: zero every word below
    min_p x the most likely word's probability. Sampling is from the rest (torch.multinomial
    renormalizes); with both, a word must pass both."""
    if args.top_k and args.top_k < prob.shape[-1]:
        prob = prob * (prob >= prob.topk(args.top_k, dim=-1).values[..., -1:])
    if args.min_p:
        prob = prob * (prob >= args.min_p * prob.max(dim=-1, keepdim=True).values)
    return prob


def _render(ids):
    """Token ids -> one-line display text, _NULL dropped."""
    return _printable(_decode_plain(ids))


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
parser.add_argument('--bn_frozen', action='store_true',
                    help='train with BatchNorm in eval mode: its running statistics normalize and '
                         'are not updated (no batch statistics), as a batch-1 continual learner '
                         'would run')
parser.add_argument('--bn_momentum', default=0.1, type=float,
                    help='ContextCNN BatchNorm running-statistics momentum (0 = cumulative)')
parser.add_argument('--init',       default='zero', choices=['zero', 'gaussian', 'relu'],
                    help='DFF register value at every example start (see --continuous)')
parser.add_argument('--reset_scale', default=0.0, type=float, metavar='F',
                    help='at an example start (<NUL>) multiply a row\'s DFF registers by F instead of '
                         'resetting them to --init (0 = reset): the next example starts with a faint '
                         'trace of the last. Training only: eval rows and generation start from --init')
parser.add_argument('--continuous', default='', metavar='KINDS',
                    help='example kinds whose rows run CONTINUOUSLY: the DFF registers flow on into '
                         'the next example instead of resetting to --init at its first (<NUL>) '
                         'step -- the regime of continuous inference and training in an embodied '
                         'agent, which never gets a reset. "text", "image" (captioned images), '
                         '"video" (captioned videos) or a comma list; default none, every example starts fresh. Training only: '
                         'eval rows hold one example each and generation is a single stream')
parser.add_argument('--image_encoder', default=None, choices=['none'] + sorted(_IMAGE_ENCODERS),
                    help='frozen image encoder whose feature map joins the input concat; '
                         'default: resnet50 if --mix or --eval_corpora names an image or video '
                         'corpus, else none')
parser.add_argument('--audio_encoder', default=None, choices=['none'] + sorted(_AUDIO_ENCODERS),
                    help='frozen audio encoder whose latents join the input concat: the last '
                         'S*S Mimi frames (80 ms each; 3.9 s at S=7) laid out row-major over the '
                         'SxS grid; quartznet: the same layout of QuartzNet 15x5 speech features '
                         '(1024 wide, 4 frames averaged per cell) computed over the last 8 s of '
                         'the clean 16 kHz soundtrack (tools/audio_prep.py sidecar); given with '
                         '--load, it replaces the checkpoint\'s encoder (its ctx_cat columns '
                         'start at zero); default: mimi if --mix or --eval_corpora names a video '
                         'corpus, else none')
parser.add_argument('--fifo3', default=None, action=argparse.BooleanOptionalAction,
                    help='--streams 3 with a FIFO per stream and every target from the dataset: '
                         'voice = the speech transcript, image = the visual captions of '
                         'tools/vcap_prep.py (Florence-2, picture only), text = the activity lines '
                         '(on video rows the text stream says <NUL> between them). Each stream '
                         'reads its own last target, never a sample. Video shards without a '
                         'visual-caption sidecar are skipped. Architecture (the text stream gets '
                         'a <NUL> logit); saved and restored like --clock_hz')
parser.add_argument('--streams', default=1, type=int, choices=[1, 3],
                    help='3: three token streams, each with its own input embedding grid and its '
                         'own decoder tree -- text (fineweb words; on video rows the inner voice: '
                         'the model\'s own sampled word, no loss), voice (speech words) and image '
                         '(activity lines). Voice and image target <NUL> where they have nothing '
                         '(every text-row tick, silent video ticks) and are fed back on their own '
                         'at inference. Needs --clock_hz; architecture, saved with the checkpoint. '
                         'A one-stream checkpoint is widened: both new decoders start as copies of '
                         'its decoder and the new token inputs as copies of its token input')
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
parser.add_argument('--imagine',    default=None, metavar='MODEL',
                    help='text rows see pictures invented live by a text-to-image model ('
                         f'{", ".join(_IMAGINE_MODELS)} or a diffusers hub repo), running in a '
                         'thread beside training on --device. Each picture is made from the last '
                         '--imagine_window tokens the row has READ (causal: never from tokens it '
                         'is about to predict) and replaces the row\'s picture when it arrives; a '
                         'row has no picture (zero image grid) from its example\'s start until '
                         'its first one. The generator serves the rows that have read the most '
                         'tokens since their last request, so the picture rate is whatever it '
                         'sustains; the STEP line reports it (img/s, img_tok, live)')
parser.add_argument('--imagine_window', default=32, type=int, metavar='T',
                    help='--imagine: prompt = the last T tokens read')
parser.add_argument('--imagine_min', default=10, type=int, metavar='T',
                    help='--imagine: a row asks for a new picture only after reading T tokens '
                         'since its last request (caps the rate when the generator outpaces it)')
parser.add_argument('--imagine_size', default=256, type=int, metavar='PX',
                    help='--imagine: picture side in pixels (crops are 224)')
parser.add_argument('--imagine_batch', default=16, type=int, help='--imagine: pictures per call')
parser.add_argument('--image',      default=None, metavar='PATH',
                    help='--generate/--vis: condition on this image (caption it)')
parser.add_argument('--shards',     default=None, type=int, help='load only the first N parquet shards')
parser.add_argument('--shard_offset', default=0, type=int, metavar='K',
                    help='a local hub-subset corpus (e.g. fineweb) trains on shards K..K+N-1 '
                         'instead of the first N (fresh text); its eval set stays on the first N, '
                         'so EVAL lines remain comparable')
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
parser.add_argument('--schedule',   default='coswarm', choices=['const', 'coswarm', 'decay'],
                    help='const: --lr_max throughout. coswarm: half-cosine rise from --lr_min '
                         'to --lr_max over --lr_period global steps, then hold. decay: coswarm, '
                         'then a half-cosine fall to --lr_final over --decay_steps steps from '
                         '--decay_start, then hold')
parser.add_argument('--lr_final',   default=1e-3, type=float, help='decay: final lr')
parser.add_argument('--decay_steps', default=200000, type=int, help='decay: fall length in steps')
parser.add_argument('--decay_start', default=None, type=int, metavar='STEP',
                    help='decay: global step the fall begins (default: this run\'s first step)')
parser.add_argument('--eval_at_start', action='store_true',
                    help='also run the held-out eval at a resumed run\'s first step')
parser.add_argument('--profile', default=0, type=int, metavar='N',
                    help='time each part of the training step (GPU synchronized) over N steps '
                         'after 50 of warm-up, print the table and exit')
parser.add_argument('--bptt', default=1, type=int, metavar='K',
                    help='truncated backpropagation through time: K steps run forward keeping the graph '
                         'through the register writes, then one backward of their mean loss and one '
                         'optimizer step (the gradient horizon grows from 1 token to up to K); 1 = off')
parser.add_argument('--lr_restart', action='store_true',
                    help='coswarm: rise over --lr_period steps from this run\'s first step '
                         '(a resumed run warms up again) instead of from global step 0')
parser.add_argument('--momentum',   default=0.0,  type=float, help='SGD momentum')
parser.add_argument('--weight_decay', default=0.0, type=float, help='SGD weight decay')
parser.add_argument('--run_steps',  default=None, type=int, help='stop after N steps of this run')
parser.add_argument('--seed',       default=None, type=int)
parser.add_argument('--device',     default=None)
# checkpoint / log
parser.add_argument('--load',       default=None, help='resume from a checkpoint')
parser.add_argument('--save',       default='checkpoint.pt')
parser.add_argument('--checkpoint', default=None, type=int,
                    help='save every N steps (default: --eval_interval, so every EVAL describes '
                         'weights on disk; 4000 without eval)')
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
                         'panel, a new random set at every GEN; the log gets one GENI/REF pair '
                         'per GEN (the first of the set); 0 = off')
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
parser.add_argument('--eval_cloze', default=0,    type=int, metavar='N',
                    help='EVALC on N Story Cloze stories (xstory_cloze en): share where the '
                         'right ending costs fewer nats than the wrong one after the 4-sentence story')
parser.add_argument('--eval_pairs', default=0,    type=int, metavar='N',
                    help='EVALM (every eval): minimal pairs, each sentence read '
                         'from a zero state; share '
                         'where the acceptable one costs fewer nats. Up to N pairs from each of '
                         'BLiMP (grammar, spread over its 67 paradigms) and ComVE (which '
                         'statement makes sense). Winogrande was tried and dropped: it sits at '
                         'chance up to pythia-160m (Qwen2.5-1.5B 63.7%)')
parser.add_argument('--eval_hold',  default=0,    type=int, metavar='N',
                    help='EVALH on N samples from <NUL>: does the second half follow the first '
                         '(self), beyond generic priming (cross), and when re-read (own)')
parser.add_argument('--doc_log',    default=0,    type=int, metavar='N',
                    help='from every N-th step on, the next document a text row starts is '
                         'recorded as fed (its first --doc_log_len tokens, with the steps it '
                         'started and ended), for EVALR; every 10th is kept for good in '
                         '--doc_log_file, the rest in memory while under 10K steps old')
parser.add_argument('--doc_log_len', default=384, type=int, metavar='T')
parser.add_argument('--doc_keep',   default=10,   type=int, metavar='K',
                    help='--doc_log: one record in K is kept for good in --doc_log_file (1 = all)')
parser.add_argument('--doc_log_file', default=None, metavar='PATH',
                    help='--doc_log / --eval_recent: the recorded training documents '
                         '(default <--log>.docs)')
parser.add_argument('--eval_recent', default=0, type=int, metavar='K',
                    help='EVALR: up to K recorded training documents per age band (steps since '
                         'the model last read them), and K held-out ones: loss on them, on their '
                         'continuation after --eval_gen_prompt tokens, and EVALG delta from that '
                         'prefix -- does the model know what it read recently better than old?')
parser.add_argument('--weight_ema', default='', metavar='T1,T2,...',
                    help='keep a running average of the weights (and BatchNorm statistics) with '
                         'each time constant T (steps), updated every step, saved in the '
                         'checkpoint; at every eval, EVAL lines for each average (corpus '
                         '<name>~emaTK). Training is unchanged: these are slow copies to measure')
parser.add_argument('--use_ema', default=0, type=int, metavar='T',
                    help='after --load, replace the weights by the checkpoint\'s --weight_ema '
                         'average with time constant T (for --eval, --doc_score, --generate...)')
parser.add_argument('--doc_score',  default=None, metavar='OUT',
                    help='load, score every record in --doc_log_file and the first --eval_docs '
                         'held-out documents (cut to --doc_log_len) with this checkpoint, one '
                         'JSON line each to OUT (kind, start / end step, nats per token), exit. '
                         'Two checkpoints\' files, paired by record, give a forgetting curve')
parser.add_argument('--doc_ablate', default='', metavar='K1,K2,...',
                    help='--doc_score: registers K (1 = the slowest) read as their mean state over '
                         'the held-out documents, as in EVALI\'s ablations: is what the weights '
                         'remember about a document keyed on the slow context?')
parser.add_argument('--step_tokens', default=0, type=int, metavar='N',
                    help='at every STEP line, a TOK line: row 0\'s last N text-stream input tokens '
                         'and the token sampled at each from its prediction, as GEN samples (--temperature, '
                         '--min_p); observation only, with its own random generator, so training\'s draws '
                         'are unchanged')
parser.add_argument('--doc_tokens', action='store_true',
                    help='--doc_score: also write each document\'s per-token nats (ce), for loss by '
                         'position in the document')
parser.add_argument('--eval_wp',    default=0,    type=int, metavar='N',
                    help='GENW: N fixed WritingPrompts prompts continued at every eval, for reading')
parser.add_argument('--eval_wp_len', default=256, type=int, metavar='C', help='GENW tokens')
parser.add_argument('--eval_qa',    default=0,    type=int, metavar='N',
                    help='EVALQ (every eval): N held-out qaipt pages; nats per ANSWER token, from a zero '
                         'state, open book (the page, then its Q/A pairs) and closed book (the pairs '
                         'alone); gain = closed - open, what reading the page is worth')
parser.add_argument('--eval_rare',  default=10,   type=int, metavar='N',
                    help='run the slow or low-value evals only at every Nth eval: EVALX, EVALI, '
                         'the video "-off" variant and EVALB of video corpora (0 = every eval)')
parser.add_argument('--eval_reach', default=0,    type=int, metavar='N',
                    help='EVALX on N spliced rows: excess loss from losing history older than c')
parser.add_argument('--eval_reach_period', default=256, type=int, metavar='P')
# one-shot modes (no training)
parser.add_argument('--generate',   default=False, action='store_true',
                    help='load, generate --n tokens from <NUL>+--prompt, print, exit')
parser.add_argument('--n',          default=200,  type=int, help='--generate length')
parser.add_argument('--free_run',   default=0,    type=int, metavar='N',
                    help='load, free-run --free_rows streams of N tokens each from one zero '
                         'state (<NUL>, never reset, every sample fed back), report each '
                         '--free_window tokens (FREE lines: judge fluency, coherence, rep1, '
                         '<NUL> share, register RMS), exit')
parser.add_argument('--eval_free',  default=0,    type=int, metavar='N',
                    help='EVALL: --free_run in short at every --eval_rare-th eval: --free_rows '
                         'streams of N tokens, never reset; fluency per --free_window, drift')
parser.add_argument('--free_rows',  default=8,    type=int, metavar='R')
parser.add_argument('--free_window', default=2000, type=int, metavar='W')
parser.add_argument('--free_chunk', default=128,  type=int, metavar='C',
                    help='--free_run: the judge reads C-token chunks, each after the one before')
parser.add_argument('--free_save',  default=None, metavar='PATH',
                    help='--free_run: write each stream\'s text to PATH (one section per row)')
parser.add_argument('--prompt_tune', default=0,   type=int, metavar='I',
                    help='load, then for the EVALG prompts compare ways of starting a '
                         'continuation (TUNE lines): cold (zero state, read the prompt), warm '
                         '(free-run --prompt_warm tokens first), and tuned (the initial '
                         'registers optimized for I Adam steps, by BPTT through the prompt, so '
                         'the model predicts it; weights frozen); each scored by its own nats '
                         'on the real continuation and by the judge (EVALG fluency / delta), exit. '
                         'With --generate: tune the start state on --prompt (one per '
                         '--prompt_tune_cap), print each continuation and the cold one, same seed')
parser.add_argument('--prompt_tune_lr', default=0.01, type=float, metavar='LR')
parser.add_argument('--prompt_tune_cap', default='1', metavar='C1,C2,...',
                    help='--prompt_tune: one tuned variant per value: each register\'s RMS is '
                         'held to at most C x its natural level (its mean RMS after reading the '
                         'prompts cold); 0 = no cap')
parser.add_argument('--prompt_tune_batch', default=10, type=int, metavar='B',
                    help='--prompt_tune: prompts tuned together (BPTT memory is about B x the '
                         'prompt length)')
parser.add_argument('--prompt_warm', default=256, type=int, metavar='K')
parser.add_argument('--prompt_tune_save', default=None, metavar='PATH',
                    help='--prompt_tune: write every prompt and each method\'s continuation')
parser.add_argument('--clock_hz',   default=None, type=float, metavar='R',
                    help='video corpora run on a fixed clock: one step per 1/R s tick, the '
                         'target a caption token or <NUL> (0 / unset: one step per caption '
                         'token). Saved with the checkpoint and restored unless given')
parser.add_argument('--ctx_tau',    default=None, metavar='SECONDS',
                    help='--clock_hz: register windows in seconds for all but the last '
                         '(plain-copy) register, e.g. 64,16,4,1 -> --ctx_ema of tau*R...,1; '
                         'saved and restored like --clock_hz')
parser.add_argument('--vision_hz',  default=None, type=float, metavar='V',
                    help='--clock_hz: the picture refreshes at V Hz and is held in between '
                         '(default: every stored frame; FineVideo frames are stored at 2 fps, so '
                         'training cannot refresh faster than that). Saved and restored')
parser.add_argument('--max_lag',    default=2.0, type=float, metavar='S',
                    help='--clock_hz: caption tokens wait in a FIFO for free ticks; an activity '
                         'line that would start more than S seconds late is dropped (speech is '
                         'never dropped)')
parser.add_argument('--nul_weight', default=None, type=float,
                    help='--clock_hz: loss weight of <NUL> targets (caption tokens weigh 1); below '
                         '1 the model learns P(<NUL>) too low (its odds scaled by the weight). '
                         'Default 0.2. Saved and restored unless given')
parser.add_argument('--clip', default=0.0, type=float, metavar='G',
                    help='scale the gradient down to norm G when it is larger (0 = off); the STEP '
                         'grad column is the norm before clipping')
parser.add_argument('--loss_norm', default=None, choices=('weight', 'words'),
                    help='--clock_hz: divide the summed loss by the summed target weight (weight, '
                         'the default) or by the number of word (non-<NUL>) targets (words: with '
                         '--nul_weight 1 the loss is the true likelihood and P(<NUL>) calibrated, '
                         'while a word gets the same step however many <NUL>s share the batch; '
                         'learned <NUL>s fade by themselves). Saved and restored unless given')
parser.add_argument('--inner_voice', default=None, action=argparse.BooleanOptionalAction,
                    help='--clock_hz without <NUL>: a tick with no caption token has no target '
                         '(no loss) and the model\'s own sampled token from it is the next '
                         'input, so the text free-runs between captions as at inference. Saved '
                         'and restored like --clock_hz; --no-inner_voice switches a loaded '
                         'inner-voice model back to a zero-initialized <NUL> target on silent ticks')
parser.add_argument('--min_p',      default=None, type=float, metavar='P',
                    help='sample only words with at least P x the top word\'s probability: in '
                         'generation and for --inner_voice\'s own tokens in training and eval '
                         '(0 = the full distribution). Saved and restored like --clock_hz')
parser.add_argument('--caption_feed', default=None, type=float, metavar='P',
                    help='--inner_voice: on a random P of video caption ticks the next input is the '
                         'word the model sampled there instead of the true caption word (scheduled '
                         'sampling; the loss stays on the true word). Saved and restored like '
                         '--clock_hz')
parser.add_argument('--text_feed', default=None, type=float, metavar='P',
                    help='--inner_voice: on a random P of text-corpus ticks the input is the word '
                         'the model sampled at the previous tick instead of the true word '
                         '(scheduled sampling; the loss stays on the true word). Saved and '
                         'restored like --clock_hz')
parser.add_argument('--top_k',      default=None, type=int, metavar='K',
                    help='sample only from the K most likely words, wherever --min_p applies '
                         '(with --min_p too, a word must pass both; 0 = all words). Saved and '
                         'restored like --clock_hz')
parser.add_argument('--audio_hz',   default=None, type=float, metavar='A',
                    help='--clock_hz: the audio grid refreshes at A Hz (at multiples of 1/A s, as '
                         '--vision_hz does the picture) and is held in between (0 / unset: every '
                         'tick). Saved and restored like --clock_hz')
parser.add_argument('--speech_delay', default=None, type=float, metavar='S',
                    help='--clock_hz: each speech token is due S seconds after its estimated '
                         'end (words are spread evenly over a transcript segment, so the delay '
                         'absorbs timing error and its sound is heard by then). Saved and '
                         'restored like --clock_hz; changes the eval set\'s targets')
parser.add_argument('--speech_align', default=None, action=argparse.BooleanOptionalAction,
                    help='--fifo3: each speech token is due at the aligned end of its word '
                         '(tools/align_prep.py\'s CTC forced alignment, /data/finevideo_align) plus '
                         '--speech_delay, not spread evenly over its transcript segment. A '
                         'video without alignments is skipped, an example holding a segment '
                         'whose alignment failed or scored under --align_min is dropped. Saved '
                         'and restored like --clock_hz; changes the eval set\'s targets')
parser.add_argument('--align_min', default=None, type=float, metavar='P',
                    help='--speech_align: the lowest segment score (mean frame probability of '
                         'its aligned characters; low = not English, or not what was said) an '
                         'example may hold (default 0.5). Saved and restored like --clock_hz')
parser.add_argument('--write_surprise', default=None, metavar='rat,H[,MEAN] | LO,HI[,MEAN]',
                    help='each step, the slow registers (all but the plain copy) write at their '
                         'rate times a gain g from the surprise s = -log p of the text token just '
                         'read (from the state before it), so unexpected tokens are kept longer. '
                         'rat,H: g = H pm / ((H-1) p + pm), pm = exp(-running mean of s): smooth '
                         'and bounded, 1 at the mean surprise, toward H as p -> 0, then divided by '
                         'its running mean so the average write rate is unchanged. LO,HI: g = '
                         's / its running mean, clamped to [LO, HI]. off / 0: plain EMAs. '
                         'MEAN: the running mean to start from when the checkpoint has none '
                         '(default: measured in training; until then gain 1). '
                         'Saved and restored like --clock_hz')
parser.add_argument('--voice_drop', default=None, type=float, metavar='P',
                    help='--inner_voice: on a random P of silent ticks the model\'s own word is '
                         'not fed back (the input stays _PAD, no word) -- in training, eval, '
                         'video generation and the live player, where a dropped word is still '
                         'shown. 1 = silent ticks never see the model\'s own words. Saved and '
                         'restored like --clock_hz')
parser.add_argument('--fluency_target', default=0.0, type=float, metavar='PCT',
                    help='with --gen_score and --min_p: after each GEN sample from <NUL>, move '
                         '--min_p so its GENSCORE fluency averages PCT (above it: the text is '
                         'too predictable, lower --min_p; below: raise it). 0 = fixed --min_p')
parser.add_argument('--fluency_gain', default=0.5, type=float, metavar='G',
                    help='--fluency_target: log(min_p) moves by G x (target - fluency)/100 per '
                         'GEN sample')
parser.add_argument('--video',      default=None, metavar='FILE|eval',
                    help='--generate: play FILE live in a window with its sound while the model '
                         'captions it from <NUL>+--prompt, looping with a <NUL> between plays; '
                         '"eval" plays a random held-out FineVideo video and scrolls its '
                         'reference text beside the caption')
parser.add_argument('--video_rate', default=4.0, type=float, metavar='TOK_PER_S',
                    help='--video FILE: caption tokens per second of media (FineVideo mean 4.1; '
                         'eval uses the reference text\'s own rate)')
parser.add_argument('--video_sound', default='mimi', choices=['mimi', 'original'],
                    help='--video: play what the model hears (the Mimi codes it reads, decoded '
                         'back to sound) or the original soundtrack')
parser.add_argument('--video_seconds', default=0.0, type=float,
                    help='--video: stop after this many seconds (0: until x or the window closes)')
parser.add_argument('--video_save', default=None, metavar='PNG',
                    help='--video: write the window to PNG on exit')
parser.add_argument('--teach',      default=0, type=int, metavar='N',
                    help='active learning: load, run N teaching episodes at batch 1 on held-out qaipt pages, '
                         'report, exit (weights are never saved). Each episode reads a page from a zero '
                         'state, asks a question (--teach_ask), force-feeds the answer and takes SGD steps '
                         'on the answer tokens only (BatchNorm in inference mode, the gradient through '
                         'the register writes over the answer span), then quizzes it closed book')
parser.add_argument('--teach_ask',  default='data', choices=['data', 'model'],
                    help="--teach: 'data' = the page's own first Q/A pair; 'model' = the model writes the "
                         'question after "Q:" and --teach_teacher answers it from the page')
parser.add_argument('--teach_teacher', default='Qwen/Qwen2.5-1.5B-Instruct', metavar='MODEL',
                    help='--teach_ask model: the instruction-tuned LM that answers the questions')
parser.add_argument('--teach_lr',   default=1e-3, type=float, help='--teach: SGD learning rate')
parser.add_argument('--teach_steps', default=1, type=int, help='--teach: SGD steps per answer')
parser.add_argument('--teach_control', default=100, type=int, metavar='N',
                    help='--teach: untaught held-out Q/A pairs scored before and after the session')
parser.add_argument('--teach_skip', default=1000, type=int, metavar='N',
                    help='--teach: skip the first N held-out pages (the EVALQ set)')
parser.add_argument('--teach_json', default=None, help='--teach: write every episode as JSON')
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
parser.add_argument('--hub_repo',   default='siliconperception/vla',
                    help="--push target; '-' writes --push_dir only")
parser.add_argument('--private',    default=False, action='store_true', help='--push: private repo')
parser.add_argument('--push_dir',   default=None, help='--push: local folder written first (default ./<repo name>)')
parser.add_argument('--card',       default=None, help='--push: model card (markdown) uploaded as README.md')
parser.add_argument('--hub_tag',    default=None, help='--push: tag the pushed commit (e.g. the run name)')
parser.add_argument('--pretrained', default=None, nargs='?', const='siliconperception/vla',
                    metavar='REPO', help='load weights + architecture from a hub repo')
parser.add_argument('--revision',   default=None, help='--pretrained: branch, tag or commit')
parser.add_argument('--verbose',    default=False, action='store_true',
                    help='print the model graph and parameter table in one-shot modes too')
args = parser.parse_args()
if args.checkpoint is None:
    args.checkpoint = args.eval_interval or 4000
_continuous = {k.strip() for k in args.continuous.split(',') if k.strip()}   # example kinds
if _continuous - {'text', 'image', 'video'}:
    raise SystemExit(f'--continuous {args.continuous}: kinds are text, image and video')

_ONESHOT = (args.generate or args.eval or args.vis or args.push or args.free_run or
            args.prompt_tune or args.doc_score or args.teach)

# ── checkpoint ────────────────────────────────────────────────────────────────

_ARCH_ARGS = ('context', 'n_hidden', 'c_context', 'depth', 'kernel', 'tokenizer', 'ctx_ema',
              'ctx_read_norm', 'dec_tree_kernels', 'dec_width', 'bn_momentum', 'init',
              'image_encoder', 'audio_encoder', 'streams')


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
_ROW_CORPUS = [n for n, k in _MIX for _ in range(k)]
_IMAGE_ROWS = [r for r, n in enumerate(_ROW_CORPUS) if n in _IMAGE_DATASETS]
_VIDEO_ROWS = [r for r, n in enumerate(_ROW_CORPUS) if n in _VIDEO_DATASETS]
_MEDIA_DATASETS = set(_IMAGE_DATASETS) | set(_VIDEO_DATASETS)
# --imagine: the text rows, whose pictures are invented from their own text
_SYNTH_ROWS = [r for r, n in enumerate(_ROW_CORPUS) if n not in _MEDIA_DATASETS] if args.imagine else []
_names = [n.strip() for n in [n for n, _ in _MIX] + (args.eval_corpora or '').split(',')]
if args.image_encoder is None:     # on --load the checkpoint's value replaces this
    args.image_encoder = ('resnet50' if args.imagine or any(n in _MEDIA_DATASETS
                                                            for n in _names) else 'none')
if args.audio_encoder is None:
    args.audio_encoder = 'mimi' if any(n in _VIDEO_DATASETS for n in _names) else 'none'

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
_aud_switch = None           # --load with another --audio_encoder: (old, new)
_start_step = 0
_start_exs = 0
_start_exs_by = {}            # corpus -> examples trained, for the STEP ex_/ep_ columns
_HUB_ARGS = 'vla_args.json'  # --push: the checkpoint's saved_args, step and examples beside model.safetensors


def _hub_checkpoint(repo, revision=None):
    """--pretrained: a pushed repo (hub id or local folder) as the dict --load reads from a .pt."""
    from safetensors.torch import load_file
    if os.path.isdir(repo):
        get = lambda f: os.path.join(repo, f)
    else:
        from huggingface_hub import hf_hub_download
        get = lambda f: hf_hub_download(repo, f, revision=revision)
    meta = json.load(open(get(_HUB_ARGS)))
    return dict(meta, state_dict=load_file(get('model.safetensors')))


if args.pretrained and args.load:
    print(f'--pretrained overrides --load {args.load}')
    args.load = None
if args.pretrained:
    print(f'loading {args.pretrained} from the hub...')
    _loaded_ckpt = _hub_checkpoint(args.pretrained, args.revision)
elif args.load:
    _loaded_ckpt = torch.load(args.load, map_location='cpu', weights_only=True)
if _loaded_ckpt is not None:
    _saved = _loaded_ckpt['saved_args']
    _bad = {k: _saved[k] for k, v in _FIXED_ARCH.items() if k in _saved and _saved[k] != v}
    if _bad:
        raise SystemExit(f'{args.load or args.pretrained} is not a v395-type checkpoint: {_bad}')
    _aud_given = (args.audio_encoder if any(a == '--audio_encoder' or a.startswith('--audio_encoder=')
                                            for a in sys.argv) else None)
    for k in _ARCH_ARGS:
        if k in _saved:
            setattr(args, k, _saved[k])
    if _aud_given and _aud_given != (_saved.get('audio_encoder') or 'none'):
        _aud_switch = (_saved.get('audio_encoder') or 'none', _aud_given)   # a new audio encoder
        args.audio_encoder = _aud_given
    if 'full_crops' not in _saved and not any(a.startswith('--full_crops') for a in sys.argv):
        args.full_crops = 0.0         # trained before full views existed: keep its crops
    _start_step = int(_loaded_ckpt.get('step', 0))
    _start_exs = int(_loaded_ckpt.get('examples', 0))
    _start_exs_by = dict(_loaded_ckpt.get('examples_by', {}))
    for k in ('clock_hz', 'ctx_tau', 'vision_hz', 'audio_hz', 'inner_voice', 'min_p', 'top_k', 'voice_drop', 'caption_feed', 'text_feed', 'speech_delay', 'fifo3', 'nul_weight', 'loss_norm', 'speech_align', 'align_min', 'write_surprise'):     # restored unless given
        if getattr(args, k) is None:
            setattr(args, k, _saved.get(k))
args.clock_hz = float(args.clock_hz or 0)
args.inner_voice = bool(args.inner_voice)
args.min_p = float(args.min_p or 0)
args.top_k = int(args.top_k or 0)
args.voice_drop = float(args.voice_drop or 0)
args.caption_feed = float(args.caption_feed or 0)
args.text_feed = float(args.text_feed or 0)
args.speech_delay = float(args.speech_delay or 0)
args.audio_hz = float(args.audio_hz or 0)
args.streams = int(args.streams or 1)
args.fifo3 = bool(args.fifo3)
args.speech_align = bool(args.speech_align)
if args.eval_recent and args.doc_log_len < 1 + args.eval_gen_prompt + args.eval_gen_len:
    raise SystemExit(f'--eval_recent: --doc_log_len {args.doc_log_len} is shorter than a prompt '
                     f'and its continuation ({1 + args.eval_gen_prompt + args.eval_gen_len})')
if args.write_surprise in (None, '', '0', 'off'):
    args.write_surprise = None
_surprise, _surp_init = None, None      # ('rat', H) or ('clamp', LO, HI); the starting mean
if args.write_surprise:
    _v = str(args.write_surprise).split(',')
    try:
        if _v[0] == 'rat' and len(_v) in (2, 3) and float(_v[1]) > 1:
            _surprise, _surp_init = ('rat', float(_v[1])), (float(_v[2]) if len(_v) == 3 else None)
        elif len(_v) in (2, 3) and 0 < float(_v[0]) <= 1 <= float(_v[1]):
            _surprise = ('clamp', float(_v[0]), float(_v[1]))
            _surp_init = float(_v[2]) if len(_v) == 3 else None
    except ValueError:
        pass
    if _surprise is None:
        raise SystemExit(f'--write_surprise {args.write_surprise}: want rat,H[,MEAN] with H > 1, '
                         f'or LO,HI[,MEAN] with 0 < LO <= 1 <= HI')
args.align_min = 0.5 if args.align_min is None else float(args.align_min)
if args.speech_align and not (args.fifo3 and args.clock_hz):
    raise SystemExit('--speech_align needs --fifo3 and --clock_hz')
args.nul_weight = 0.2 if args.nul_weight is None else float(args.nul_weight)
args.loss_norm = args.loss_norm or 'weight'
if args.fifo3 and args.streams != 3:
    raise SystemExit('--fifo3 needs --streams 3')
if args.streams == 3:
    if not args.clock_hz:
        raise SystemExit('--streams 3 needs --clock_hz')
    if args.inner_voice or args.voice_drop or args.caption_feed or args.text_feed:
        raise SystemExit('--streams 3: the text stream is the inner voice; give --no-inner_voice '
                         'and no --voice_drop / --caption_feed / --text_feed')
if args.inner_voice and not args.clock_hz:
    raise SystemExit('--inner_voice needs --clock_hz')
if args.ctx_tau:
    if not args.clock_hz:
        raise SystemExit('--ctx_tau needs --clock_hz')
    args.ctx_ema = ','.join(f'{float(t) * args.clock_hz:g}' for t in str(args.ctx_tau).split(',')
                            if t.strip()) + ',1'


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


def _switch_audio_state_dict(sd, model, old, new):
    """--load with another --audio_encoder: ctx_cat's audio-grid columns are replaced by zeros
    of the new encoder's width, so the model starts deaf and learns to read the new grid."""
    sd = dict(sd)
    w = sd['ctx_cat.weight']
    o = model.c_text + model.img_width
    wo = _AUD_DIMS[old] if old != 'none' else 0
    sd['ctx_cat.weight'] = torch.cat([w[:, :o], w.new_zeros(w.shape[0], model.aud_width, 1, 1),
                                      w[:, o + wo:]], dim=1)
    print(f'--audio_encoder {new} (checkpoint: {old}): ctx_cat audio columns {wo} -> '
          f'{model.aud_width}, zero-initialized; ctx_cat {tuple(w.shape)} -> '
          f'{tuple(sd["ctx_cat.weight"].shape)}', flush=True)
    return sd


def _widen_state_dict(sd, model):
    """A one-stream state_dict -> streams 3: the voice and image decoders start as copies of
    the text decoder (its <NUL> logit included), the text decoder loses its <NUL> logit, and
    ctx_cat gets the voice and image token-grid columns as copies of the text token columns, so
    a caption word in either new stream reads as it did in the one stream."""
    sd = dict(sd)
    for k in [k for k in sd if k.startswith('text_dec.')]:
        for d in ('voc_dec', 'img_dec'):
            sd[d + k[len('text_dec'):]] = sd[k].clone()
        if k.startswith('text_dec.nul.'):
            del sd[k]
    w = sd['ctx_cat.weight']
    n_in = sum(model.in_widths[:len(model.in_widths) - 2])        # text, image, audio grids
    c = model.c_text
    sd['ctx_cat.weight'] = torch.cat([w[:, :n_in], w[:, :c], w[:, :c], w[:, n_in:]], dim=1)
    print(f'--streams 3: widened a one-stream checkpoint (voice/image decoders copied from the '
          f'text decoder; ctx_cat {tuple(w.shape)} -> {tuple(sd["ctx_cat.weight"].shape)})',
          flush=True)
    return sd


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
    slot = {'gen': 0, 'sample': 1, 'imagine': 1, 'genv': 0, 'video': 1}
    title = {'gen': 'GEN captions', 'sample': 'TRAIN sample', 'imagine': 'TRAIN imagine',
             'genv': 'GEN video captions', 'video': 'TRAIN video'}
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
                if w >= 640 and h >= 360:             # a bogus screen (display asleep at
                    win.setGeometry(g.x() + slot[kind] * w, g.y(), w, h)   # launch): keep figsize
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
        saw at that step, labelled with the token it was reading (the first _SAMPLE_CELLS)."""
        n = len(toks)
        crops = crops[:_SAMPLE_CELLS]
        m = len(crops)
        cols = max(1, min(m, math.ceil(math.sqrt(m * 2.2))))
        rows = math.ceil(m / cols)
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

    def draw_imagine(fig, step, text, n, spans):
        """--imagine: one recorded text example and the pictures invented for it, each
        labelled with the token span it was shown for and the prompt it was made from."""
        spans = [s for s in spans if s[1] < s[2]]
        m = max(1, len(spans))
        cols = max(1, min(m, math.ceil(math.sqrt(m * 2.2))))
        rows = math.ceil(m / cols)
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 3.2], left=0.01, right=0.99, top=0.93,
                              bottom=0.08, hspace=0.06)        # room for 3-line labels
        tx = fig.add_subplot(gs[0])
        tx.set_axis_off()
        tx.text(0, 1, textwrap.fill(cut(text, 900), 170), va='top', fontsize=8,
                color='limegreen', transform=tx.transAxes, clip_on=True)
        sub = gs[1].subgridspec(rows, cols, wspace=0.06, hspace=0.75)
        for k, (im, a, b, span, prompt) in enumerate(spans):
            ax = fig.add_subplot(sub[k // cols, k % cols])
            ax.imshow(im)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f'[{a}:{b}] ' + cut(span.replace(chr(10), ' '), 18), fontsize=8,
                         family='monospace', pad=2)
            ax.set_xlabel(textwrap.fill(prompt[-56:].replace(chr(10), ' '), 28), fontsize=8,
                          labelpad=1, color='0.7')
        fig.suptitle(f'TRAIN imagine step {step}   {n} tokens   {len(spans)} pictures   '
                     f'{args.imagine}   {args.log}', family='monospace', fontsize=8)

    def spec_ax(ax, spec, ext, marks=()):
        """A spectrogram (0-8 kHz) over media time ext = (t0, t1) seconds."""
        if spec is None or spec.size < 2:
            ax.text(0.5, 0.5, 'no sound', ha='center', va='center', fontsize=8, color='0.6',
                    transform=ax.transAxes)
            ax.set_axis_off()
            return
        lo, hi = np.percentile(spec, 5), spec.max()
        ax.imshow(spec, origin='lower', aspect='auto', cmap='magma', vmin=lo, vmax=hi,
                  extent=(ext[0], ext[1], 0, 8))
        for t in marks:
            ax.axvline(t, color='cyan', lw=0.6, alpha=0.7)
        ax.set_yticks([0, 4, 8])
        ax.set_yticklabels(['0', '4k', '8k'], fontsize=7)
        ax.tick_params(axis='x', labelsize=7, pad=1)

    def draw_genv(fig, step, items):
        """Held-out clips: 4 frames (titled with their media time) and the spectrogram of the
        sound over the stretch captioned, then the caption generated with picture and sound
        (A+V, or see / hear / think) and the reference (REF), marked every _GENV_MARK s."""
        n = len(items)
        gs = fig.add_gridspec(n, 2, width_ratios=[1, 1.25], left=0.03, right=0.99, top=0.94,
                              bottom=0.03, wspace=0.03, hspace=0.3)
        colors = {'A+V': 'white', 'see': 'white', 'hear': 'white', 'think': 'skyblue'}
        for k, (strip, spec, name, caps, ftimes, ext) in enumerate(items):
            sub = gs[k, 0].subgridspec(2, 1, height_ratios=[1, 0.7], hspace=0.25)
            ax = fig.add_subplot(sub[0])
            ax.imshow(strip)
            w = strip.shape[1] / max(1, len(ftimes))  # each frame titled with its media time
            ax.set_xticks([(j + 0.5) * w for j in range(len(ftimes))])
            ax.set_xticklabels([f't={t:.1f}s' for t in ftimes], fontsize=7, color='0.7')
            ax.tick_params(length=0, pad=1)
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_title(name, fontsize=8, pad=2)
            sa = fig.add_subplot(sub[1])
            spec_ax(sa, spec, ext, ftimes)            # cyan: when those frames were shown
            tx = fig.add_subplot(gs[k, 1])
            tx.set_axis_off()
            dy = 0                                    # points below the top of the cell
            for lab, cap in caps.items():
                t = textwrap.fill(f'{lab}: ' + cut(cap.replace(chr(10), ' / '), 500), 100)
                tx.annotate(t, xy=(0, 1), xycoords='axes fraction', xytext=(0, -dy),
                            textcoords='offset points', va='top', fontsize=7.5,
                            color=colors.get(lab, 'limegreen'), annotation_clip=False)
                dy += 9.0 * (t.count(chr(10)) + 1) + 3
        fig.suptitle(f'GEN video step {step}   {args.log}', family='monospace', fontsize=8)

    def draw_video(fig, step, name, text, cells, spec, ext, n):
        """One training video example: its opening tokens, the frames shown while they were
        read (each titled with its token span and media time) and the sound's spectrogram with
        the frames' times marked."""
        m = max(1, len(cells))
        cols = min(m, 6)
        rows = math.ceil(m / cols)
        tracks = isinstance(text, list)   # --fifo3: [(stream, text marked [Ns])]
        gs = fig.add_gridspec(3, 1, height_ratios=[1.8 if tracks else 1.0, 1.55 * rows, 0.9],
                              left=0.04, right=0.99, top=0.93, bottom=0.05, hspace=0.18)
        tx = fig.add_subplot(gs[0])
        tx.set_axis_off()
        if tracks:                        # one block per stream, each in its own colour
            dy = 0
            for lab, t in text:
                t = textwrap.fill(f'{lab}: ' + cut(t, 560), 170)
                tx.annotate(t, xy=(0, 1), xycoords='axes fraction', xytext=(0, -dy),
                            textcoords='offset points', va='top', fontsize=8,
                            color={'see': 'white', 'hear': 'gold'}.get(lab, 'skyblue'),
                            annotation_clip=False)
                dy += 10.0 * (t.count(chr(10)) + 1) + 3
        else:
            tx.text(0, 1, textwrap.fill(cut(text.replace(chr(10), ' / '), 900), 170), va='top',
                    fontsize=8, color='limegreen', transform=tx.transAxes, clip_on=True)
        sub = gs[1].subgridspec(rows, cols, wspace=0.05, hspace=0.45)
        for k, (im, t, a, b, span) in enumerate(cells):
            ax = fig.add_subplot(sub[k // cols, k % cols])
            ax.imshow(im)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f'[{a}:{b}] ' + cut(span.replace(chr(10), ' '), 22), fontsize=8,
                         family='monospace', pad=2)
            ax.set_xlabel(f't={t:.1f}s', fontsize=8, labelpad=1, color='0.7')
        spec_ax(fig.add_subplot(gs[2]), spec, ext, [c[1] for c in cells])
        fig.suptitle(f'TRAIN video step {step}   {name}   {n}   {args.log}',
                     family='monospace', fontsize=8)

    draw = {'gen': draw_gen, 'sample': draw_sample, 'imagine': draw_imagine,
            'genv': draw_genv, 'video': draw_video}

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
            draw[kind](fig, *msg[1:])
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

    def __init__(self, c_in, S, kernels, width, lmhead, nul_id=None):
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
        # --clock_hz: <NUL> is the first embedding row the tokenizer never uses. Those rows of
        # the frozen lm_head were never trained, so its logit gets its own trainable head and
        # the other unused rows are masked off.
        self.nul_id = nul_id
        if nul_id is not None:
            self.nul = nn.Linear(lmhead.in_features, 1)
            nn.init.zeros_(self.nul.weight)
            nn.init.zeros_(self.nul.bias)

    def forward(self, x):
        for conv in self.tree:
            x = conv(x)
        h = self.pool(self.proj(x)).squeeze(-1).squeeze(-1)
        logits = self.lmhead(h)
        if self.nul_id is not None:
            k = self.nul_id
            logits = torch.cat([logits[:, :k], self.nul(h).to(logits.dtype),
                                logits.new_full((logits.shape[0], logits.shape[1] - k - 1), -1e4)],
                               dim=1)
        return logits


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


class AudioEncoder(nn.Module):
    """Frozen Kyutai Mimi (transformers MimiModel) kept out of the module registry, so it adds
    no state_dict keys: codes [32, T] (12.5 Hz) -> dequantized latents [512, T], and, for the
    viewers only, codes -> 24 kHz audio."""

    def __init__(self, name):
        super().__init__()
        from transformers import MimiModel
        m = MimiModel.from_pretrained(_AUDIO_ENCODERS[name], dtype=torch.float32).eval()
        for p in m.parameters():
            p.requires_grad_(False)
        self.__dict__['_mimi'] = m
        self.width = _AUD_DIM

    def _on(self, dev):
        m = self.__dict__['_mimi']
        if next(m.parameters()).device != dev:
            m.to(dev)
        return m

    @torch.no_grad()
    def latents(self, codes, dev):
        """int16/long codes [32, T] -> float latents [512, T] on dev ([512, 0] if T == 0)."""
        codes = torch.as_tensor(codes)
        if codes.shape[-1] == 0:
            return torch.zeros(_AUD_DIM, 0, device=dev)
        m = self._on(dev)
        return m.quantizer.decode(codes.to(dev).long()[None])[0].float()

    @torch.no_grad()
    def codes(self, wav, dev):
        """float mono 24 kHz waveform (numpy) -> int16 codes [32, T] at 12.5 Hz, encoded in 30 s
        pieces (as tools/video_prep.py does)."""
        hop = int(24000 / _AUD_RATE)
        wav = wav[:len(wav) // hop * hop]
        m, out = self._on(dev), []
        for s in range(0, len(wav), 375 * hop):
            x = torch.from_numpy(np.ascontiguousarray(wav[s:s + 375 * hop])).to(dev)[None, None]
            out.append(m.encode(x, num_quantizers=32).audio_codes[0].short().cpu())
        return torch.cat(out, 1) if out else torch.zeros(32, 0, dtype=torch.short)

    @torch.no_grad()
    def audio(self, codes, dev):
        """codes [32, T] -> float numpy waveform at 24 kHz (viewers)."""
        codes = torch.as_tensor(codes)
        if codes.shape[-1] == 0:
            return np.zeros(0, np.float32)
        m, out = self._on(dev), []
        for s in range(0, codes.shape[-1], 375):            # 30 s pieces: a whole video fits
            c = codes[:, s:s + 375].to(dev).long()[None]
            out.append(m.decode(c).audio_values[0, 0].float().cpu().numpy())
        return np.concatenate(out)


class QuartzNetEncoder(nn.Module):
    """Frozen QuartzNet 15x5 (pure PyTorch, weights from the .nemo file, BatchNorm folded into
    the pointwise convs), kept out of the module registry like Mimi: 16 kHz sound -> NeMo's
    log-mel front end (pre-emphasis, 20/10 ms STFT, 64 mels, per-mel normalization) -> C1 +
    15 residual blocks of 5 separable conv sub-blocks + C2 + C3 -> [1024, T] at 50 Hz."""
    BLOCKS = ([(256, 33, 1, 2, 1)] + [(256, 33, 5, 1, 1)] * 3 + [(256, 39, 5, 1, 1)] * 3 +
              [(512, 51, 5, 1, 1)] * 3 + [(512, 63, 5, 1, 1)] * 3 + [(512, 75, 5, 1, 1)] * 3 +
              [(512, 87, 1, 1, 2)])          # (filters, kernel, sub-blocks, stride, dilation)

    def __init__(self):
        super().__init__()
        ck = os.path.join(_QN_DIR, 'model_weights.ckpt')
        if not os.path.exists(ck):
            import tarfile, urllib.request
            os.makedirs(_QN_DIR, exist_ok=True)
            nemo = os.path.join(_QN_DIR, 'stt_en_quartznet15x5.nemo')
            print(f'downloading {_QN_URL}', flush=True)
            urllib.request.urlretrieve(_QN_URL, nemo)
            with tarfile.open(nemo) as tf:
                tf.extract(tf.getmember(next(n for n in tf.getnames()
                                             if n.endswith('model_weights.ckpt'))), _QN_DIR,
                           filter='data')
            ck = next(os.path.join(r, f) for r, _, fs in os.walk(_QN_DIR) for f in fs
                      if f == 'model_weights.ckpt')
        sd = torch.load(ck, map_location='cpu', weights_only=True)

        def fold(pw, p):                     # pointwise conv + BatchNorm (eps 1e-3) -> (w, b)
            s = sd[p + '.weight'] / torch.sqrt(sd[p + '.running_var'] + 1e-3)
            return pw * s[:, None, None], sd[p + '.bias'] - sd[p + '.running_mean'] * s

        t = {'win': sd['preprocessor.featurizer.window'], 'fb': sd['preprocessor.featurizer.fb'][0]}
        blocks = []
        for b, (c, k, rep, st, dil) in enumerate(self.BLOCKS):
            p = f'encoder.encoder.{b}.'
            subs = [(sd[p + f'mconv.{5 * r}.conv.weight'],) +
                    fold(sd[p + f'mconv.{5 * r + 1}.conv.weight'], p + f'mconv.{5 * r + 2}')
                    for r in range(rep)]
            res = fold(sd[p + 'res.0.0.conv.weight'], p + 'res.0.1') if rep > 1 else None
            blocks.append((subs, res, k, st, dil))
        t['c3'] = fold(sd['encoder.encoder.17.mconv.0.conv.weight'], 'encoder.encoder.17.mconv.1')
        t['ctc'] = (sd['decoder.decoder_layers.0.weight'], sd['decoder.decoder_layers.0.bias'])
        self.__dict__['_t'], self.__dict__['_blocks'] = t, blocks
        self.__dict__['_dev'] = torch.device('cpu')
        self.width = _AUD_DIMS['quartznet']
        self.n_params = sum(v.numel() for k, v in sd.items() if k.startswith(('encoder.', 'decoder.')))

    def _on(self, dev):
        dev = torch.device(dev)
        if self._dev != dev:
            mv = lambda x: x.to(dev) if torch.is_tensor(x) else x
            self.__dict__['_t'] = {k: tuple(map(mv, v)) if isinstance(v, tuple) else mv(v)
                                   for k, v in self._t.items()}
            self.__dict__['_blocks'] = [([tuple(map(mv, sb)) for sb in subs],
                                         tuple(map(mv, res)) if res else None, k, st, dil)
                                        for subs, res, k, st, dil in self._blocks]
            self.__dict__['_dev'] = dev

    @torch.no_grad()
    def features(self, wav):
        """float sound [N, L] at 16 kHz -> (C3 features [N, 1024, T], valid [N, T]) at 50 Hz;
        a frame of digital silence (before the sound starts) is left out of the normalization
        and marked invalid."""
        self._on(wav.device)
        t = self._t
        x = torch.cat([wav[:, :1], wav[:, 1:] - 0.97 * wav[:, :-1]], 1)
        s = torch.stft(x, 512, 160, 320, t['win'], center=True, pad_mode='constant',
                       return_complex=True)
        p = t['fb'] @ s.abs().pow(2)                                        # [N, 64, T]
        ok = (p.sum(1, keepdim=True) > 1e-10).float()
        x = torch.log(p + 2 ** -24)
        n = ok.sum(2, keepdim=True).clamp(min=2)
        mu = (x * ok).sum(2, keepdim=True) / n
        sd = (((x - mu) * ok).pow(2).sum(2, keepdim=True) / (n - 1)).sqrt()
        x = (x - mu) / (sd + 1e-5) * ok
        with torch.autocast(x.device.type, dtype=torch.bfloat16, enabled=x.is_cuda):
            for subs, res, k, st, dil in self._blocks:
                y = x
                for j, (dw, pw, b) in enumerate(subs):
                    y = F.conv1d(y, dw.to(y.dtype), stride=st, padding=dil * (k // 2),
                                 dilation=dil, groups=y.shape[1])
                    y = F.conv1d(y, pw.to(y.dtype), b.to(y.dtype))
                    if j < len(subs) - 1:
                        y = F.relu(y)
                if res is not None:
                    y = y + F.conv1d(x, res[0].to(y.dtype), res[1].to(y.dtype))
                x = F.relu(y)
            w, b = t['c3']
            x = F.relu(F.conv1d(x, w.to(x.dtype), b.to(x.dtype)))
        return x.float(), ok[:, 0, ::2][:, :x.shape[2]] > 0

    @torch.no_grad()
    def grids(self, wav, ends, S):
        """int16 sound buffers [N, L] (sample 0 of a buffer = _QN_WIN samples before its grid
        cell 0) and cells heard [N] (in quarters: 20 ms frames) -> audio grids [N, 1024, S, S]:
        the C3 features of the _QN_WIN samples before each end, the last S*S cells of 4 frames
        (80 ms) each laid out row-major; a cell before the sound starts is zeros."""
        i0 = (ends.double() * _QN_HOP).round().long()[:, None] + \
            torch.arange(_QN_WIN, device=wav.device)[None]
        x = wav.gather(1, i0.clamp(max=wav.shape[1] - 1)).float() / 32768.0
        f, ok = self.features(x)
        W = S * S * 4
        f, ok = f[:, :, -W:], ok[:, -W:].float()
        f = (f * ok[:, None]).view(f.shape[0], f.shape[1], S * S, 4).sum(3)
        f = f / ok.view(ok.shape[0], 1, S * S, 4).sum(3).clamp(min=1)
        return f.view(f.shape[0], f.shape[1], S, S)

    @torch.no_grad()
    def transcribe(self, wav):
        """float sound [L] at 16 kHz -> greedy CTC text (a check that the weights loaded)."""
        f, _ = self.features(wav[None])
        lg = F.conv1d(f, *self._t['ctc'])[0].argmax(0).tolist()
        labels = " abcdefghijklmnopqrstuvwxyz'"
        return ''.join(labels[c] for c, p in zip(lg, [-1] + lg[:-1]) if c != p and c < len(labels))


class LogMelEncoder(nn.Module):
    """--audio_encoder logmel: a fixed log-mel front end, no weights (an FFT and a filter
    bank): 16 kHz sound -> 64 slaney mels of 25 ms frames every 10 ms (power, log), each mel
    standardized by fixed corpus constants (_LM_MU/_LM_SD). The grid is the spectrogram of the
    last S*S*4 frames heard, 4 frames (40 ms) per cell laid out row-major, channel = frame x 64
    + mel -- causal, so each 25 Hz tick only adds a cell (a shift register in hardware)."""

    def __init__(self):
        super().__init__()
        import torchaudio
        fb = torchaudio.functional.melscale_fbanks(_LM_NFFT // 2 + 1, 0.0, _QN_SR / 2, _LM_MELS,
                                                   _QN_SR, norm='slaney', mel_scale='slaney')
        self.__dict__['_t'] = {'fb': fb.T.contiguous(), 'win': torch.hann_window(_LM_WIN),
                               'mu': torch.tensor(_LM_MU)[:, None], 'sd': torch.tensor(_LM_SD)[:, None]}
        self.width = _AUD_DIMS['logmel']
        self.n_params = 0

    def _on(self, dev):
        if self._t['fb'].device != torch.device(dev):
            self.__dict__['_t'] = {k: v.to(dev) for k, v in self._t.items()}

    @torch.no_grad()
    def features(self, x, norm=True):
        """float sound [N, L] at 16 kHz -> (log-mel [N, 64, T], valid [N, T]), frame j over
        samples j*160 .. j*160+512 (no padding); a frame of digital silence (before the sound
        starts) is 0 and invalid."""
        self._on(x.device)
        t = self._t
        sp = torch.stft(x.float(), _LM_NFFT, _LM_HOP, _LM_WIN, t['win'], center=False,
                        return_complex=True)
        p = t['fb'] @ sp.abs().pow(2)
        ok = p.sum(1) > 1e-10
        f = torch.log(p + 1e-10)
        if norm:
            f = (f - t['mu']) / t['sd']
        return f * ok[:, None], ok

    def grids(self, wav, ends, S):
        """int16 sound buffers [N, L] (as QuartzNetEncoder.grids: sample 0 = _QN_WIN samples
        before grid cell 0 of 80 ms) and 80 ms cells heard [N] (in 20 ms quarters) -> grids
        [N, 256, S, S] of the S*S*4 frames ending at the sound heard."""
        nf = S * S * _LM_FR
        L = (nf - 1) * _LM_HOP + _LM_NFFT
        e = (ends.double() * _QN_HOP).round().long()[:, None] + _QN_WIN
        i0 = e - L + torch.arange(L, device=wav.device)[None]
        x = wav.gather(1, i0.clamp(0, wav.shape[1] - 1)).float() / 32768.0
        f, _ = self.features(x)
        N = f.shape[0]
        return f.view(N, _LM_MELS, S * S, _LM_FR).permute(0, 3, 1, 2).reshape(
            N, _LM_FR * _LM_MELS, S, S)


def _cells_heard(t):
    """Grid cells of sound heard by media time t (s): whole 80 ms cells for Mimi; for quartznet
    in quarter cells (one 20 ms QuartzNet frame each), so an --audio_hz above 12.5 still moves
    the grid every refresh."""
    if args.audio_encoder in _WAV_ENCODERS:
        return math.floor(t * _AUD_RATE * _QN_FRAMES + 1e-9) / _QN_FRAMES
    return int(t * _AUD_RATE)


def _qn_buffer(wav, a0, a1):
    """A row's whole-video int16 sound at 16 kHz -> the buffer QuartzNetEncoder.grids reads for
    an example whose grid cells a0..a1 (12.5 Hz) are heard: samples from _QN_WIN before cell
    a0 to cell a1, zeros before the start of the sound."""
    s0, s1 = a0 * _QN_HOP - _QN_WIN, round(max(a1, a0) * _QN_HOP)
    out = np.zeros(s1 - s0, np.int16)
    a, b = max(s0, 0), min(s1, len(wav))
    if b > a:
        out[a - s0:b - s0] = wav[a:b]
    return out


def _aud_windows(lat, ends, S):
    """lat [N, 512, T] latents, ends [N] long = Mimi frames heard so far per row -> the last
    S*S frames before each end laid out row-major over an SxS grid, [N, 512, S, S]; frames
    before the start of the sound are zeros."""
    N, C, T = lat.shape
    W = S * S
    idx = ends[:, None] - W + torch.arange(W, device=lat.device)[None]          # [N, W]
    ok = (idx >= 0) & (idx < T)
    g = lat.gather(2, idx.clamp(0, max(T - 1, 0))[:, None, :].expand(N, C, W))
    return (g * ok[:, None, :]).view(N, C, S, S)


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


def _norm_u8(x):
    """uint8 [N, 3, 224, 224] -> the encoder's normalized float input."""
    mean = torch.tensor(_IMG_MEAN, device=x.device).view(1, 3, 1, 1)
    std = torch.tensor(_IMG_STD, device=x.device).view(1, 3, 1, 1)
    return (x.float() / 255.0 - mean) / std


def _crop224(im, off=0.5):
    """A video frame uint8 [3, h, w] -> [3, 224, 224]: scaled (if needed) so its shorter side
    is 224, then cropped along the longer side at fraction `off` (0 = left/top, 0.5 = centre)."""
    h, w = im.shape[1:]
    if min(h, w) != _IMG_IN:
        s = _IMG_IN / min(h, w)
        im = F.interpolate(im[None].float(), size=(max(_IMG_IN, round(h * s)), max(_IMG_IN, round(w * s))),
                           mode='bilinear', antialias=True, align_corners=False)[0].round().clamp(0, 255).byte()
        h, w = im.shape[1:]
    y, x = round(off * (h - _IMG_IN)), round(off * (w - _IMG_IN))
    return im[:, y:y + _IMG_IN, x:x + _IMG_IN]


def _decode_jpegs(jpegs, device='cpu'):
    """JPEG bytes -> list of uint8 RGB [3, h, w] (CPU: ~0.2 ms per 224p frame)."""
    from torchvision.io import decode_jpeg, ImageReadMode
    return [decode_jpeg(torch.frombuffer(bytearray(b), dtype=torch.uint8), mode=ImageReadMode.RGB)
            for b in jpegs]


class _VideoClip:
    """A held-out video example for EVAL and GEN: frames uint8 [F, 3, 224, 224] (centre crops,
    CPU), Mimi latents [512, T] (device), the codes (for the viewer's spectrogram), and per
    scored step (fi, ai); GEN plays it at `rate` tokens per second of media from t0. see /
    hear False blank the picture / the sound (blind / deaf)."""

    def __init__(self, frames, lat, codes, fi, ai, fps, t0, rate, meta, see=True, hear=True):
        self.frames, self.lat, self.codes, self.fi, self.ai = frames, lat, codes, fi, ai
        # grid cells of sound: a 1-D lat is a quartznet sound buffer (see _qn_buffer)
        self.n_aud = lat.shape[-1] if lat.dim() == 2 else max(0, lat.shape[0] - _QN_WIN) // _QN_HOP
        self._ag = (None, None)          # quartznet: (cells heard, audio grid) of the last step
        self._agrid, self._aidx = None, {}   # quartznet: grids precomputed per cells heard
        self.fps, self.t0, self.rate, self.meta = fps, t0, rate, meta
        self.see, self.hear = see, hear
        self.phase = 0.0 if args.clock_hz else 0.5     # tick k at t0 + k/R; token k mid-slot

    def precompute_audio(self, model, dev, chunk=64):
        """quartznet: the audio grid of every distinct cells-heard value of the clip's ticks,
        computed once (the encoder is frozen) and kept fp16 on dev -- only when the sound is
        held over several ticks (a grid per tick would not fit: _score computes them then)."""
        u = sorted(set(self.ai))
        if len(u) * 4 > len(self.ai):
            return
        lat = self.lat[None].to(dev)
        self._agrid = torch.cat([model.audio_grid(lat.expand(len(u[i:i + chunk]), -1),
                                                  torch.tensor(u[i:i + chunk], device=dev)).half()
                                 for i in range(0, len(u), chunk)])
        self._aidx = {a: k for k, a in enumerate(u)}

    def aud_at(self, model, ai, dev):
        """quartznet: the audio grid [1, 1024, S, S] after ai cells heard."""
        k = self._aidx.get(ai)
        if k is not None:
            return self._agrid[k:k + 1].float()
        return model.audio_grid(self.lat[None].to(dev), torch.tensor([ai], device=dev))

    def variant(self, see, hear):
        v = copy.copy(self)
        v.see, v.hear = see, hear
        return v

    def at(self, k):
        """(fi, ai) for generation step k: the media time of the k-th token at self.rate. A
        clocked eval clip has them per tick already (exactly as training builds them)."""
        if args.clock_hz and len(self.ai) > 1 and k < len(self.ai):
            return self.fi[k], self.ai[k]
        t = self.t0 + (k + self.phase) / max(self.rate, 1e-6)
        fi = min(self.frames.shape[0] - 1, max(0, int((t - self.t0) * self.fps)))
        if args.audio_hz:          # --audio_hz: the sound refreshes at multiples of 1/A s
            t = max(self.t0, math.floor(t * args.audio_hz + 1e-9) / args.audio_hz)
        return fi, min(self.n_aud, _cells_heard(t - self.t0) + self.ai[0])

    def grids(self, model, sels, dev):
        """(img, aud) grids [1, ...] for one step of this clip."""
        (fi, ai), = sels
        img = aud = None
        if model.img_width and self.see:
            img = model.image_grid(_norm_u8(self.frames[fi][None].to(dev)))
        if model.aud_width and self.hear:
            if self.lat.dim() == 2:
                aud = model.audio_grid(self.lat[None].to(dev), torch.tensor([ai], device=dev))
            else:                        # quartznet runs only when the sound refreshes
                if self._ag[0] != ai:
                    self._ag = (ai, self.aud_at(model, ai, dev))
                aud = self._ag[1]
        return img, aud


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


def _views(bank, hw, fit, gen=None):
    """One random 224x224 crop per image, normalized for the encoder: a native-resolution
    close-up copied pixel for pixel (images are at least 224 on each side, see _prep_image)
    or, with probability --full_crops, a full view -- the whole image scaled so its shorter
    side is 224, at a random offset along the longer side (see _fit). gen: a torch.Generator
    on the bank's device, for reproducible crops (eval)."""
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
        full = fit[rows, :, ar[None, :, None], (of[:, None] + ar)[:, None, :]]
        full = torch.where((H > W)[:, None, None, None], full.transpose(1, 2), full)
        pick = torch.rand(N, device=dev, generator=gen) < args.full_crops
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
    streams 3: three token grids (text, voice, image; the voice and image grids after the audio
    grid) and three decoders, logits [B, 3, vocab]; a one-stream idx [B] is read as the text
    stream with voice and image silent (as on a text row) and gets the text logits [B, vocab].
    """

    def __init__(self, S=8, n_hidden=512, c_context=384, depth=8, kernel=3,
                 tokenizer='pythia31m', windows=(256, 64, 16, 4, 1), read_norm=1.0,
                 dec_kernels=(3, 3, 3), dec_width=256, bn_momentum=0.1, init='zero',
                 image_encoder='none', audio_encoder='none', nul_head=False, streams=1,
                 text_nul=False, surprise=None):
        super().__init__()
        from transformers import AutoModelForCausalLM
        repo = _TOKENIZERS[tokenizer]
        lm = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float32)
        self.S, self.n_hidden, self.c_context = S, n_hidden, c_context
        self.windows = [float(w) for w in windows]
        if not self.windows or min(self.windows) < 1:
            raise SystemExit(f'--ctx_ema {windows}: windows must be >= 1 token')
        self.K = len(self.windows)
        self.read_norm = float(read_norm)
        self.init_mode = init
        self.vocab, self.c_text = lm.config.vocab_size, lm.config.hidden_size
        self.tok = HFTokenizer(repo, self.vocab)

        self.tok_embed = lm.get_input_embeddings()                      # frozen
        self.context = ContextCNN(c_context, depth, kernel, bn_momentum)
        self.streams = int(streams)
        self.nul_id = len(self.tok.tok) if (nul_head or self.streams == 3) and \
            len(self.tok.tok) < self.vocab else None
        lmhead = lm.get_output_embeddings()                             # frozen, shared
        # streams 3: the text stream never says <NUL> (but --fifo3: text_nul); voice and image do
        self.text_dec = TextDecoder(n_hidden, S, list(dec_kernels), dec_width, lmhead,
                                    nul_id=None if self.streams == 3 and not text_nul
                                    else self.nul_id)
        if self.streams == 3:
            self.voc_dec = TextDecoder(n_hidden, S, list(dec_kernels), dec_width, lmhead,
                                       nul_id=self.nul_id)
            self.img_dec = TextDecoder(n_hidden, S, list(dec_kernels), dec_width, lmhead,
                                       nul_id=self.nul_id)
        for p in self.pretrained_params():
            p.requires_grad_(False)

        # ctx_cat reads [input grids..., registers...]. It starts as [I, I, ..., I] onto the
        # first outputs each block fits, i.e. the plain sum of the sources -- except the image
        # and audio blocks, which start at zero, so a media model starts out as the text-only
        # function and learns to read its senses.
        self.image_encoder = image_encoder or 'none'
        self.audio_encoder = audio_encoder or 'none'
        self.img_width = 2048 if self.image_encoder != 'none' else 0
        self.aud_width = _AUD_DIMS[self.audio_encoder] if self.audio_encoder != 'none' else 0
        self.in_widths = ([self.c_text] + ([self.img_width] if self.img_width else [])
                          + ([self.aud_width] if self.aud_width else [])
                          + [self.c_text] * (self.streams - 1))     # voice, image token grids
        widths = self.in_widths + [n_hidden] * self.K
        n_tok_extra = self.streams - 1
        self.ctx_cat = nn.Conv2d(sum(widths), c_context, 1)
        with torch.no_grad():
            self.ctx_cat.weight.zero_()
            o = 0
            for i, w in enumerate(widths):
                if i == 0 or i >= len(self.in_widths) - n_tok_extra:
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
        self.aud_enc = (None if not self.aud_width else QuartzNetEncoder()       # frozen
                        if self.audio_encoder == 'quartznet' else LogMelEncoder()  # no weights
                        if self.audio_encoder == 'logmel' else AudioEncoder(self.audio_encoder))

        self.register_buffer('ctx_read_rms', torch.zeros(self.K))       # 0 = not measured yet
        self.register_buffer('rate', torch.tensor([min(1.0, 1.0 / w) for w in self.windows]),
                             persistent=False)
        # --write_surprise ('rat', H) / ('clamp', LO, HI): the slow registers' write gain
        self.surprise = tuple(surprise) if surprise else None
        if self.surprise and self.windows[-1] != 1:
            raise SystemExit('--write_surprise needs a plain-copy last register (window 1)')
        self.register_buffer('surp_mean', torch.zeros(()))     # running mean surprise; 0 = unset
        self.register_buffer('gain_mean', torch.zeros(()))     # 'rat': running mean gain; 0 = unset
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

    def audio_grid(self, lat, ends):
        """Latents [N, 512, T] and frames heard [N] -> audio grid [N, 512, S, S] (see
        _aud_windows), each position RMS-normalized over channels; silence-before-start stays 0.
        quartznet: lat is the int16 sound buffers [N, L] (see _qn_buffer), the grid [N, 1024,
        S, S] (see QuartzNetEncoder.grids)."""
        if self.audio_encoder in _WAV_ENCODERS:
            a = self.aud_enc.grids(lat, ends, self.S)
        else:
            a = _aud_windows(lat, ends, self.S).float()
        return a * torch.rsqrt(a.pow(2).mean(dim=1, keepdim=True) + 1e-6)

    def expand(self, idx):
        """streams 3: a one-stream idx [B] -> [B, 3], the text stream with voice and image
        silent (_PAD; _NULL at a blink), as on a text row."""
        if self.streams == 1 or idx.dim() == 2:
            return idx
        quiet = torch.where(idx == _NULL, _NULL, _PAD)
        return torch.stack([idx, quiet, quiet], dim=1)

    def _tok_grid(self, idx):
        B = idx.shape[0]
        tok = self.tok_embed(idx.clamp(min=0))
        tok = tok * torch.rsqrt(tok.pow(2).mean(dim=1, keepdim=True) + 1e-12)
        tok = tok.masked_fill((idx < 0)[:, None], 0.0)      # _NULL / _PAD: a zero token grid
        return tok.view(B, self.c_text, 1, 1).expand(-1, -1, self.S, self.S)

    def _inputs(self, idx, img, aud=None):
        """The input grids, in self.in_widths order: the RMS-normalized token embedding
        broadcast over the grid, then (image model) the image grid and (audio model) the audio
        grid, zeros where None, then (streams 3) the voice and image token grids."""
        idx = self.expand(idx)
        cols = [idx] if idx.dim() == 1 else list(idx.unbind(1))
        blink = cols[0] == _NULL
        B = idx.shape[0]
        grids = [self._tok_grid(cols[0])]
        if self.img_width:
            if img is None:
                img = grids[0].new_zeros(B, self.img_width, self.S, self.S)
            else:      # <NUL> is a blink: no token AND no image, the registers carry on
                img = img.masked_fill(blink[:, None, None, None], 0.0)
            grids.append(img)
        if self.aud_width:
            if aud is None:
                aud = grids[0].new_zeros(B, self.aud_width, self.S, self.S)
            else:      # ... and no sound (a _PAD tick keeps both)
                aud = aud.masked_fill(blink[:, None, None, None], 0.0)
            grids.append(aud)
        grids += [self._tok_grid(c) for c in cols[1:]]
        return grids

    def heads(self, o):
        """Layer output -> logits: [B, vocab], or (streams 3) [B, 3, vocab] for text, voice,
        image."""
        if self.streams == 1:
            return self.text_dec(o)
        return torch.stack([self.text_dec(o), self.voc_dec(o), self.img_dec(o)], dim=1)

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

    def _write(self, o, dff, gain=None):
        """Laplacian-pyramid cascade: register k blends toward o minus registers 1..k-1 as
        just written. gain [B] (--write_surprise) scales the rate of every register but the
        plain copy, capped at 1."""
        new = []
        for k, p in enumerate(dff.chunk(self.K, dim=1)):
            inp = o - sum(new) if k else o
            r = self.rate[k]
            if gain is not None and self.windows[k] > 1:
                r = (r * gain).clamp(max=1.0).view(-1, 1, 1, 1)
            new.append(p + r * (inp - p))
        return torch.cat(new, dim=1)

    @torch.no_grad()
    def _gain(self, idx, dff):
        """--write_surprise: [B] write gain from the surprise s of the text token being read
        (-log p under the text logits of the state before it; the registers of a cascade
        whose last is a plain copy sum to the previous layer output) and its running mean m.
        'rat': H / (1 + (H-1) exp(m - s)) = H pm / ((H-1) p + pm), over its own running mean;
        'clamp': s / m clamped to (LO, HI). 1 for no token (<NUL> blink, pad). Training
        updates the means; until they are set, the row's own surprise stands in (gain 1)."""
        t = self.expand(idx)
        t = t[:, 0] if t.dim() == 2 else t
        lp = F.log_softmax(self.text_dec(sum(dff.chunk(self.K, dim=1))).float(), dim=-1)
        s = -lp.gather(1, t.clamp(min=0)[:, None])[:, 0]
        ok = t >= 0
        run = self.surp_mean
        if self.training and bool(ok.any()):
            b = s[ok].mean()
            run.copy_(torch.where(run == 0, b, 0.999 * run + 0.001 * b))
        m = torch.where(run > 0, run, s)
        if self.surprise[0] == 'rat':
            H = self.surprise[1]
            g = H / (1 + (H - 1) * torch.exp(m - s))
            gm = self.gain_mean
            if self.training and bool(ok.any()):
                b = g[ok].mean()
                gm.copy_(torch.where(gm == 0, b, 0.999 * gm + 0.001 * b))
            g = g / torch.where(gm > 0, gm, torch.ones_like(gm))
        else:
            g = (s / m.clamp(min=1e-6)).clamp(*self.surprise[1:])
        return torch.where(ok, g, torch.ones_like(g))

    def step(self, idx, dff, img=None, aud=None):
        """One token for every row: -> (new registers, layer output). No detach."""
        gain = self._gain(idx, dff) if self.surprise else None
        x = self.ctx_cat(torch.cat(self._inputs(idx, img, aud) + self._read(dff), dim=1))
        o = self.linout(self.context(x))
        return self._write(o, dff, gain), o

    def forward(self, idx, targets=None, flag=None, img=None, aud=None, keep=0.0, graph=False):
        """idx [B] current tokens; targets [B] next tokens or None; flag [B] rows starting a
        document (their registers reset, or are scaled by keep if nonzero: --reset_scale);
        img [B, 2048, S, S] image grid and aud [B, 512, S, S] audio grid, or None (zeros).
        Advances self.dff by one step; graph (--bptt): self.dff keeps its autograd graph."""
        B, dev = idx.shape[0], idx.device
        if self.dff is None or self.dff.shape[0] != B or self.dff.device != dev:
            self.dff = self.new_state(B, dev)
        if flag is not None and flag.any():
            self.dff = self.dff.clone()
            if keep:
                self.dff[flag] = self.dff[flag] * keep
            else:
                self.dff[flag] = self.new_state(int(flag.sum()), dev)
        new, o = self.step(idx, self.dff, img, aud)
        self.dff = new if graph else new.detach().clone()
        if self.streams == 3 and idx.dim() == 1:     # a one-stream caller: the text stream
            logits = self.text_dec(o)
        else:
            logits = self.heads(o)
        loss = F.cross_entropy(logits, targets.long()) if targets is not None else None
        return logits, loss

    @torch.no_grad()
    def generate(self, prompt_ids, n_tokens, temperature=1.0, image=None, video=None,
                 stop_chars=None, h0=None):
        """Sample n_tokens after prompt_ids (opened with _NULL, see _prompt_ids) on a private
        state; short only on NaN/Inf. image: uint8 [3, h, w], seen through a fresh random
        224x224 crop every token (as in training); None = text-only. video: a _VideoClip,
        played at its own token rate (see _VideoClip.at); its frames and/or sound may be
        None (blind / deaf). stop_chars: stop early once the text (<NUL> dropped) is that
        many characters long. h0: the starting registers [1, ...] (None = zero)."""
        self.eval()
        dev = next(self.parameters()).device
        bank = _bank([image], dev) if image is not None else None
        pos = [0]

        def feed(b, dff):
            img = self.image_grid(_views(*bank)) if bank is not None else None
            aud = None
            if video is not None:
                img, aud = video.grids(self, [video.at(pos[0])], dev)
            pos[0] += 1
            new, o = self.step(torch.tensor([b], device=dev), dff, img, aud)
            logits = self.text_dec(o)
            if not (new.isfinite().all() and logits.isfinite().all()):
                print('generate: NaN/Inf')
                return None, None
            return logits, new

        out, dff, logits = [], self.new_state(1, dev) if h0 is None else h0, None
        for b in prompt_ids:
            logits, dff = feed(b, dff)
            if logits is None:
                return out
        drop = args.voice_drop if args.inner_voice and video is not None else 0.0
        for _ in range(n_tokens):                 # one tick each
            prob = F.softmax(logits[0] / max(temperature, 1e-6), dim=-1)
            b = torch.multinomial(_truncate(prob), 1).item()
            out.append(b)
            if stop_chars and b != _NUL_ID and len(_decode_plain(out)) >= stop_chars:
                return out
            # --voice_drop: a dropped word is said (shown) but not fed back
            fed = _PAD if b == _NUL_ID or (drop and random.random() < drop) else b
            logits, dff = feed(fed, dff)
            if logits is None:
                return out
        return out

    @torch.no_grad()
    def generate3(self, n_ticks, video, temperature=1.0):
        """streams 3: n_ticks of a _VideoClip from a _NULL blink on a private state, every
        stream's sample fed back (no word after a <NUL>) -> (text, voice, image) id lists with
        <NUL> dropped, and each token's tick; short only on NaN/Inf."""
        self.eval()
        dev = next(self.parameters()).device
        dff = self.new_state(1, dev)
        x = torch.full((1, 3), _NULL, dtype=torch.long, device=dev)
        outs, ticks = ([], [], []), ([], [], [])
        for k in range(n_ticks):
            img, aud = video.grids(self, [video.at(k)], dev)
            dff, o = self.step(x, dff, img, aud)
            logits = self.heads(o)[0]
            if not (dff.isfinite().all() and logits.isfinite().all()):
                print('generate3: NaN/Inf')
                break
            prob = F.softmax(logits.float() / max(temperature, 1e-6), dim=-1)
            b = torch.multinomial(_truncate(prob), 1)[:, 0]
            for st in range(3):
                if int(b[st]) != _NUL_ID:
                    outs[st].append(int(b[st]))
                    ticks[st].append(k)
            x = torch.where(b == _NUL_ID, _PAD, b)[None]
        return outs, ticks


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

# Local document parquets (a 'text' column) written by a prep script: name -> directory.
_LOCAL_PARQUET = {
    'babylm':   _DATA + '/babylm2026_nat/docs',  # tools/babylm_prep.py: BabyLM 2026 Strict, marked documents
    'babylm1k': _DATA + '/babylm2026_docs',      # v473: the same cut into ~1000-word pieces (--chunk 1000)
    'babylmseq': _DATA + '/babylm2026_seq2',     # the same pieces, up to 16 of a document in order per row (--seq 16;
                                              # Switchboard hidden in simple_wiki cut out, v476 on)
    'babylmseq0': _DATA + '/babylm2026_seq',     # v475's build (that Switchboard labelled simple_wiki, tabs kept)
    'babylmdev': _DATA + '/babylm2026_dev',      # BabyLM's official dev split as ~1000-word pieces: eval only
    'qaipt':     _DATA + '/qa_ipt',              # tools/qa_prep.py: RefinedWeb pages + synthesized Q/A pairs (ODC-BY)
}
_EVAL_ONLY = {'babylmdev'}                  # a held-out split as a whole: --eval_corpora only, never --mix

# Train-only corpora: a fixed 1/_HOLDOUT_MOD of documents, chosen by a hash of the text, is
# held out for eval and skipped in training (deterministic, streaming-compatible).
_HASH_HOLDOUT = {'swiki', 'fwedu', 'fineweb', 'fwcrawl', 'cosmo', 'cosmoweb', 'smolcosmo',
                 'smolfwedu', 'strangetb', 'sebooks', 'dclmedu', 'littlec', 'simplestories', 'babylm', 'babylm1k',
                 'babylmseq', 'babylmseq0', 'qaipt'}
_HOLDOUT_MOD = 32

# Corpora with a real held-out split; a triple is a held-out set in another repo.
_EVAL_SPLITS = {
    'tinytb':  'test',
    'tiny':    'validation',
    'c4':      'validation',
    'web':     'train[-3000:]',       # the tail tools/score.py holds out
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


def _local_files(name):
    files = sorted(glob.glob(os.path.join(_LOCAL_PARQUET[name], '*.parquet')))
    if not files:
        raise SystemExit(f'{name}: no parquet under {_LOCAL_PARQUET[name]}; run its prep script first')
    return files


def _load_corpus(name, streaming, shards=None):
    from datasets import load_dataset, DownloadConfig
    if name in _EVAL_ONLY:
        raise SystemExit(f'{name} is a held-out split: --eval_corpora only, not --mix/--dataset')
    if name in _LOCAL_PARQUET:
        files = _local_files(name)
        print(f'{name}: {len(files)} local parquet file(s) from {_LOCAL_PARQUET[name]}', flush=True)
        return load_dataset('parquet', data_files={'train': files}, streaming=streaming)
    if name in _HUB_SUBSET:
        files = _hub_subset_files(name)
        if not files:
            raise SystemExit(f'{name}: no downloaded parquet files under HF_HOME for '
                             f'{_HUB_SUBSET[name]}; fetch a subset first')
        k = args.shard_offset
        files = files[k:k + shards] if shards else files[k:]
        print(f'{name}: {len(files)} local parquet file(s) from the hub cache'
              + (f', from shard {k}: {[os.path.basename(f) for f in files][:4]}' if k else ''),
              flush=True)
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


_PIECE_SEP = '\x1e'          # a row of consecutive pieces of one document (tools/babylm_prep.py --seq)


def clip_text(text):
    """A document or caption as (input, target) pairs over [_NULL] tokens; a row of pieces
    joined by _PIECE_SEP as each piece's pairs back to back (a <NUL> opens every piece)."""
    if _PIECE_SEP in text:
        return [st for piece in text.split(_PIECE_SEP) for st in clip_text(piece)]
    full = [_NULL] + _tokenizer.encode(text)
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
            raise SystemExit(f'{name}: no parquet files in {cfg["dir"]} (see tools/img_prep.py)')
        self.cfg, self.rng = cfg, random.Random(seed)
        self.pool, self.lock = [], threading.Lock()
        print(f'{name}: {len(self.files)} local parquet files in {cfg["dir"]}', flush=True)

    def _fill(self):
        with self.lock:
            f = self.rng.choice(self.files)
        pf = self.pq.ParquetFile(f)
        with self.lock:
            g = self.rng.randrange(pf.metadata.num_row_groups)
        rows = pf.read_row_group(g, columns=['image', 'id', 'class',
                                             *_caption_cols(self.cfg)]).to_pylist()
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
                    return _caption_of(row, self.cfg), row
            self._fill()


def _video_files(name, split='train'):
    cfg = _VIDEO_DATASETS[name]
    pat = cfg[split] if split == 'train' or cfg.get(split) else cfg['train']
    return sorted(glob.glob(os.path.join(cfg['dir'], pat)))


_VID_COLS = ['id', 'category', 'duration', 'fps', 'frames', 'codes', 'n_codes', 'events']


_sidecar_idx = {}            # sidecar parquet -> (row-group bounds, {id: row})
_sidecar_lock = threading.Lock()


def _sidecar_path(corpus, feat_file):
    d = _AUD_SIDECAR.get(corpus)
    return os.path.join(d, os.path.basename(feat_file)) if d else None


_vcap_cache = collections.OrderedDict()   # --fifo3: sidecar parquet -> {id: (t, cap)}


def _vcap_path(corpus, feat_file):
    d = _VCAP_SIDECAR.get(corpus)
    return os.path.join(d, os.path.basename(feat_file)) if d else None


def _row_vcap(corpus, feat_file, vid):
    """--fifo3: a video's visual captions ([times], [captions]) from the sidecar corpus
    (tools/vcap_prep.py); None if its shard is not there (yet) or lacks the id. Whole shards are
    cached (small: text only), the 64 most recent."""
    import pyarrow.parquet as pq
    path = _vcap_path(corpus, feat_file)
    if not path or not os.path.exists(path):
        return None
    with _sidecar_lock:
        d = _vcap_cache.get(path)
        if d is not None:
            _vcap_cache.move_to_end(path)
    if d is None:
        d = {r['id']: (r['t'], r['cap']) for r in pq.read_table(path).to_pylist()}
        with _sidecar_lock:
            _vcap_cache[path] = d
            while len(_vcap_cache) > 64:
                _vcap_cache.popitem(last=False)
    return d.get(vid)


_align_cache = collections.OrderedDict()  # --speech_align: sidecar parquet -> {id: (s, we, score)}


def _align_path(corpus, feat_file):
    d = _ALIGN_SIDECAR.get(corpus)
    return os.path.join(d, os.path.basename(feat_file)) if d else None


def _row_align(corpus, feat_file, vid):
    """--speech_align: a video's word timings (say-event starts, per event its word ends,
    per event its score) from the sidecar corpus (tools/align_prep.py); None if its shard is not
    there (yet) or lacks the id. Whole shards are cached, the 64 most recent."""
    import pyarrow.parquet as pq
    path = _align_path(corpus, feat_file)
    if not path or not os.path.exists(path):
        return None
    with _sidecar_lock:
        d = _align_cache.get(path)
        if d is not None:
            _align_cache.move_to_end(path)
    if d is None:
        d = {r['id']: (r['s'], r['we'], r['score'])
             for r in pq.read_table(path, columns=['id', 's', 'we', 'score']).to_pylist()}
        with _sidecar_lock:
            _align_cache[path] = d
            while len(_align_cache) > 64:
                _align_cache.popitem(last=False)
    return d.get(vid)


def _row_wav(corpus, feat_file, vid):
    """--audio_encoder quartznet: a video's clean soundtrack, int16 [n] at 16 kHz, from the
    sidecar corpus (tools/audio_prep.py); None if its shard is not there (yet) or lacks the id."""
    import pyarrow.parquet as pq
    import soundfile as sf
    path = _sidecar_path(corpus, feat_file)
    if not path or not os.path.exists(path):
        return None
    with _sidecar_lock:
        idx = _sidecar_idx.get(path)
    pf = pq.ParquetFile(path)
    if idx is None:
        ids = pf.read(columns=['id']).column('id').to_pylist()
        idx = (np.cumsum([0] + [pf.metadata.row_group(g).num_rows
                                for g in range(pf.metadata.num_row_groups)]),
               {v: k for k, v in enumerate(ids)})
        with _sidecar_lock:
            _sidecar_idx[path] = idx
    bounds, at = idx
    k = at.get(vid)
    if k is None:
        return None
    g = int(np.searchsorted(bounds, k, side='right')) - 1
    flac = pf.read_row_group(g, columns=['flac']).column('flac')[int(k - bounds[g])].as_py()
    if not flac:
        return np.zeros(0, np.int16)
    return sf.read(io.BytesIO(flac), dtype='int16')[0]


def _video_events(row):
    """A video row's events [[start, end, kind, text]] that have text, in time order."""
    return [e for e in json.loads(row['events']) if e[3].strip()]


def _event_tokens(ev):
    """One token list per event: its line of text (speech in double quotes) and a newline."""
    return [_tokenizer.encode((f'"{t}"' if k == 'say' else t) + '\n') for _, _, k, t in ev]


def _timed_tokens(ev, toks, k0=0, maxtok=1 << 30, maxspan=math.inf):
    """(ids, media times) of events ev[k0:] as whole events, at most maxtok tokens and
    maxspan seconds (see _video_example for where each token is placed)."""
    ids, times, last = [], [], 0.0
    for (s, e, kind, _), tk in zip(ev[k0:], toks[k0:]):
        if ids and (len(ids) + len(tk) > maxtok or max(e, s) - ev[k0][0] > maxspan):
            break
        for m in range(len(tk)):
            last = max(last, s + (e - s) * (m + 1) / len(tk) if kind == 'say' else s)
            ids.append(tk[m])
            times.append(last)
    return ids[:maxtok], times[:maxtok]


def _clocked_example(row, rng=None, maxspan=_VID_MAXSPAN):
    """--clock_hz R: a video row -> (text, media) with one step per tick of 1/R s over a window
    of at most maxspan seconds (the whole video, or from a random event's start with rng).
    Caption tokens are scheduled as in _video_example (speech where just heard, an activity
    line at its start) and wait in a FIFO for the first free tick at or after that time; an
    activity line that would start more than --max_lag s late is dropped. Every other tick's
    target is <NUL>. Step k's input is the previous target (_PAD after a <NUL>, the _NULL
    blink at k = 0) and it sees the frame on screen and the Mimi frames heard at t0 + k/R."""
    R, frames = args.clock_hz, row['frames']
    if not frames:
        return None
    fps = float(row['fps'])
    codes = np.frombuffer(row['codes'], dtype='<i2').reshape(32, -1)
    ev = _video_events(row)
    dur = float(row.get('duration') or 0) or len(frames) / fps
    ta = 0.0
    if rng is not None and dur > maxspan and ev:
        ta = max(0.0, min(ev[rng.randrange(len(ev))][0], dur - maxspan))
    tb = min(dur, ta + maxspan)
    n = int((tb - ta) * R)
    if n < 2:
        return None
    tgt, nxt, dropped = [_SIL] * n, 0, 0
    kind = [0] * n                           # per tick: 0 silent, 1 speech, 2 activity line
    for (s, e, kd, _), tk in zip(ev, _event_tokens(ev)):
        if not ta <= s < tb:
            continue
        if kd != 'say' and ta + nxt / R - s > args.max_lag:
            dropped += len(tk)
            continue
        for m in range(len(tk)):
            t = s + (e - s) * (m + 1) / len(tk) + args.speech_delay if kd == 'say' else s
            k = max(math.ceil((t - ta) * R - 1e-9), nxt)
            if k >= n:
                break
            tgt[k], nxt = tk[m], k + 1
            kind[k] = 1 if kd == 'say' else 2
    ids = [y for y in tgt if y != _SIL]
    if not ids:
        return None
    V = min(args.vision_hz or fps, fps)      # picture refresh: held between refreshes
    fabs = [min(len(frames) - 1, int(math.floor((ta + k / R) * V + 1e-9) / V * fps + 1e-9))
            for k in range(n)]
    A = args.audio_hz                        # --audio_hz: sound refresh, held in between
    aabs = [min(codes.shape[1], _cells_heard(math.floor((ta + k / R) * A + 1e-9) / A if A
                                             else ta + k / R)) for k in range(n)]
    f0, a0 = fabs[0], max(0, int(aabs[0]) - 64)
    xs = [_NULL] + [_PAD if y == _SIL else y for y in tgt[:-1]]
    text = _tokenizer.decode(ids)
    media = dict(jpegs=frames[f0:max(fabs) + 1], codes=np.ascontiguousarray(codes[:, a0:int(max(aabs))]),
                 wav=_qn_buffer(row['wav'], a0, max(aabs)) if row.get('wav') is not None else None,
                 off=rng.random() if rng is not None else 0.5,     # crop offset, per example
                 fi=[f - f0 for f in fabs], ai=[a - a0 for a in aabs], fps=fps,
                 t0=ta, t1=tb, text=text, n=n, f0=f0, a0=a0, clock=R, dropped=dropped, kind=kind,
                 name=f'{row["id"]}  {row.get("category") or ""}'.strip(),
                 steps=list(zip(xs, tgt)))
    return text, media


def _vcap_lines(vcap):
    """--fifo3: a video's visual captions (times, captions) -> [(t, caption)] without the
    near-repeats (word Jaccard over _VCAP_SAME with one of the last 3 kept)."""
    out, last = [], []
    for t, c in zip(*(vcap or ([], []))):
        w = set(c.lower().split())
        if not w or any(len(w & q) / len(w | q) > _VCAP_SAME for q in last):
            continue
        out.append((float(t), c.strip()))
        last = (last + [w])[-3:]
    return out


def _word_timed_tokens(text, ends):
    """--speech_align: a speech line's tokens ('"text"' and a newline) and the media time each
    is heard by: the aligned end of the word holding its last character (the opening quote:
    the first word's; the closing quote and newline: the last word's). (None, None) if the
    words do not match the alignment."""
    wb = [m.end() for m in re.finditer(r'\S+', text)]    # end offset of each word in text
    if len(wb) != len(ends) or not wb:
        return None, None
    enc = _tokenizer.tok(f'"{text}"\n', return_offsets_mapping=True, add_special_tokens=False)
    times = [ends[min(bisect.bisect_right(wb, min(max(b - 2, 0), len(text) - 1)), len(wb) - 1)]
             for _, b in enc['offset_mapping']]
    return enc['input_ids'], times


def _clocked3_example(row, rng=None, maxspan=_VID_MAXSPAN):
    """--fifo3: a video row -> (text, media) with one step per tick of 1/R s, as
    _clocked_example, but every tick has a target for each of the three streams, each from its
    own FIFO: voice the speech transcript (each token due where just heard, plus
    --speech_delay), image the visual captions (row['vcap'], each line due at its frame), text
    the activity lines (each due at its start); a line that would start more than --max_lag s
    late is dropped. A stream with nothing due targets <NUL>. Step k's input per stream is that
    stream's previous target (_PAD after a <NUL>; the _NULL blink at k = 0) -- always the
    dataset's, never the model's. steps: [((x_text, x_voice, x_image), (y_text, y_voice,
    y_image))] per tick."""
    R, frames = args.clock_hz, row['frames']
    if not frames:
        return None
    fps = float(row['fps'])
    codes = np.frombuffer(row['codes'], dtype='<i2').reshape(32, -1)
    ev = _video_events(row)
    caps = _vcap_lines(row.get('vcap'))
    dur = float(row.get('duration') or 0) or len(frames) / fps
    starts = [e[0] for e in ev] + [t for t, _ in caps]
    ta = 0.0
    if rng is not None and dur > maxspan and starts:
        ta = max(0.0, min(rng.choice(starts), dur - maxspan))
    tb = min(dur, ta + maxspan)
    n = int((tb - ta) * R)
    if n < 2:
        return None
    wend = [None] * len(ev)                  # --speech_align: per say event (word ends, score)
    if args.speech_align:
        a_s, a_we, a_sc = row['align']
        si = [i for i, x in enumerate(ev) if x[2] == 'say']
        if len(si) != len(a_s) or any(abs(ev[i][0] - x) > 1e-3 for i, x in zip(si, a_s)):
            return None                      # aligned to other events: not this row's
        for i, we, sc in zip(si, a_we, a_sc):
            wend[i] = (we, sc)
    # (stream, start, end, is speech, text, event) lines; stream 0 text, 1 voice, 2 image
    lines = [(1 if kd == 'say' else 0, s, e, kd == 'say', f'"{t}"' if kd == 'say' else t, i)
             for i, (s, e, kd, t) in enumerate(ev)] + [(2, t, t, False, c, None) for t, c in caps]
    lines.sort(key=lambda x: (x[1], x[0]))
    tgt = [[_SIL] * n for _ in range(3)]
    nxt, dropped = [0, 0, 0], 0
    for st, s, e, say, txt, i in lines:
        if not ta <= s < tb:
            continue
        tt = None
        if say and args.speech_align:
            we, sc = wend[i]
            if not sc >= args.align_min:     # a failed (NaN) or doubtful alignment
                return None
            tk, tt = _word_timed_tokens(txt[1:-1], we)
            if tk is None:
                return None
        else:
            tk = _tokenizer.encode(txt + '\n')
        if not say and ta + nxt[st] / R - s > args.max_lag:
            dropped += len(tk)
            continue
        for m in range(len(tk)):
            t = (tt[m] if tt else s + (e - s) * (m + 1) / len(tk)) + args.speech_delay if say \
                else s
            k = max(math.ceil((t - ta) * R - 1e-9), nxt[st])
            if k >= n:
                break
            tgt[st][k], nxt[st] = tk[m], k + 1
    ids = [[y for y in tg if y != _SIL] for tg in tgt]
    if not any(ids):
        return None
    V = min(args.vision_hz or fps, fps)
    fabs = [min(len(frames) - 1, int(math.floor((ta + k / R) * V + 1e-9) / V * fps + 1e-9))
            for k in range(n)]
    A = args.audio_hz
    aabs = [min(codes.shape[1], _cells_heard(math.floor((ta + k / R) * A + 1e-9) / A if A
                                             else ta + k / R)) for k in range(n)]
    f0, a0 = fabs[0], max(0, int(aabs[0]) - 64)
    xs = [tuple(_NULL for _ in range(3))] + \
        [tuple(_PAD if tgt[st][k] == _SIL else tgt[st][k] for st in range(3)) for k in range(n - 1)]
    ys = [tuple(tgt[st][k] for st in range(3)) for k in range(n)]
    text = '\n'.join(f'{lab}: ' + _tokenizer.decode(i).replace('\n', ' / ')
                      for lab, i in zip(('think', 'hear', 'see'), ids))
    media = dict(jpegs=frames[f0:max(fabs) + 1], codes=np.ascontiguousarray(codes[:, a0:int(max(aabs))]),
                 wav=_qn_buffer(row['wav'], a0, max(aabs)) if row.get('wav') is not None else None,
                 off=rng.random() if rng is not None else 0.5,
                 fi=[f - f0 for f in fabs], ai=[a - a0 for a in aabs], fps=fps,
                 t0=ta, t1=tb, text=text, n=n, f0=f0, a0=a0, clock=R, dropped=dropped,
                 name=f'{row["id"]}  {row.get("category") or ""}'.strip(),
                 steps=list(zip(xs, ys)))
    return text, media


def _ntok(steps):
    """Caption / text targets in an example's steps (every stream's, --fifo3)."""
    return sum(sum(v != _SIL for v in y) if isinstance(y, tuple) else y != _SIL
               for _, y in steps)


def _loss_den(wt, y):
    """The clocked loss's denominator: the summed target weight, or (--loss_norm words) the
    number of word targets."""
    if args.loss_norm == 'words':
        return ((y != _NUL_ID) & (y != -100)).sum().clamp(min=1)
    return wt.sum()


def _as3(x, y):
    """--fifo3: a one-stream text / image row's (x, y) -> the three streams' (as _stream_xy):
    the word is the text stream's, voice and image read _PAD and target <NUL>."""
    if isinstance(y, tuple):
        return x, y
    return ((x, x, x) if x == _NULL else (x, _PAD, _PAD)), (y, _NUL_ID, _NUL_ID)


def _video_example(row, rng=None, maxtok=_VID_MAXTOK, maxspan=_VID_MAXSPAN):
    """A video row -> (text, steps, media) for one token-clocked example. Events become lines
    of text in time order (speech segments in double quotes); a video longer than maxtok
    tokens or maxspan seconds is cut to a window of whole events starting at a random event
    (rng) or at the first (rng None). Each caption token is placed in media time, never moving
    backwards: an activity line is a headline, all of it at the event's start (activities span
    the speech heard during them -- spreading one over its span pushed that speech tens of
    seconds late); a speech token at the point in its segment where it has just been heard
    (evenly by token). Step i -- the one that PREDICTS token i --
    sees the frame on screen and the Mimi frames heard by that time. media: the window's JPEG
    frames and codes plus, per step, fi (frame index into them) and ai (Mimi frames heard,
    relative to the codes kept)."""
    if args.clock_hz:
        return (_clocked3_example if args.fifo3 else _clocked_example)(row, rng, maxspan)
    ev = _video_events(row)
    if not ev:
        return None
    toks = _event_tokens(ev)
    k0 = rng.randrange(len(ev)) if rng is not None and (
        sum(map(len, toks)) > maxtok or ev[-1][1] - ev[0][0] > maxspan) else 0
    ids, times = _timed_tokens(ev, toks, k0, maxtok, maxspan)
    fps, frames = float(row['fps']), row['frames']
    codes = np.frombuffer(row['codes'], dtype='<i2').reshape(32, -1)
    if not frames:
        return None
    fabs = [min(len(frames) - 1, int(t * fps)) for t in times]
    aabs = [min(codes.shape[1], int(t * _AUD_RATE)) for t in times]
    f0, a0 = fabs[0], max(0, aabs[0] - 64)
    a1 = max(aabs) if aabs else 0
    text = _tokenizer.decode(ids)
    full = [_NULL] + ids
    media = dict(jpegs=frames[f0:max(fabs) + 1], codes=np.ascontiguousarray(codes[:, a0:a1]),
                 wav=_qn_buffer(row['wav'], a0, a1) if row.get('wav') is not None else None,
                 off=rng.random() if rng is not None else 0.5,     # crop offset, per example
                 fi=[f - f0 for f in fabs], ai=[a - a0 for a in aabs], fps=fps,
                 t0=times[0], t1=times[-1], text=text, n=len(ids), f0=f0, a0=a0,
                 name=f'{row["id"]}  {row.get("category") or ""}'.strip(),
                 steps=[(full[i], full[i + 1]) for i in range(len(ids))])
    return text, media


class _VideoSource(_ImageSource):
    """Random training videos of a local video corpus, drawn from a small pool of whole row
    groups of random files (rows hold every frame of a video, so the pool is kept small). The
    file list is re-read every RESCAN seconds, so shards still being written by
    tools/video_prep.py join the draw as they land."""
    POOL = 48
    RESCAN = 600

    def __init__(self, name, seed):
        import pyarrow.parquet as pq
        self.pq, self.name, self.cfg = pq, name, _VIDEO_DATASETS[name]
        self.files = _video_files(name)
        if not self.files:
            raise SystemExit(f'{name}: no parquet files in {self.cfg["dir"]} (see tools/video_prep.py)')
        self.rng, self.pool, self.lock = random.Random(seed), [], threading.Lock()
        self.held = self.cfg.get('eval') is None          # id-hash held-out split
        self.scanned = time.time()
        print(f'{name}: {len(self.files)} local parquet files in {self.cfg["dir"]}', flush=True)

    def _fill(self):
        with self.lock:
            if time.time() - self.scanned > self.RESCAN:
                self.scanned, n = time.time(), len(self.files)
                self.files = _video_files(self.name) or self.files
                if len(self.files) != n:
                    print(f'{self.name}: {len(self.files)} local parquet files', flush=True)
            files = self.files
            if args.fifo3:                             # only shards with visual captions
                files = [f for f in files if os.path.exists(_vcap_path(self.name, f) or '')]
                if not files:
                    raise SystemExit(f'{self.name}: no visual captions in '
                                     f'{_VCAP_SIDECAR.get(self.name)} (see tools/vcap_prep.py)')
            if args.speech_align:                      # only shards with word timings
                files = [f for f in files if os.path.exists(_align_path(self.name, f) or '')]
                if not files:
                    raise SystemExit(f'{self.name}: no word timings in '
                                     f'{_ALIGN_SIDECAR.get(self.name)} (see tools/align_prep.py)')
            if args.audio_encoder in _WAV_ENCODERS:      # only shards whose sound is there
                files = [f for f in files if os.path.exists(_sidecar_path(self.name, f) or '')]
                if not files:
                    raise SystemExit(f'{self.name}: no sidecar sound in '
                                     f'{_AUD_SIDECAR.get(self.name)} (see tools/audio_prep.py)')
            f = self.rng.choice(files)
        pf = self.pq.ParquetFile(f)
        if not pf.metadata.num_row_groups:
            return
        with self.lock:
            g = self.rng.randrange(pf.metadata.num_row_groups)
        rows = pf.read_row_group(g, columns=_VID_COLS).to_pylist()
        rows = [dict(r, _file=f) for r in rows if not (self.held and _id_heldout(r['id']))]
        with self.lock:
            self.pool.extend(rows)

    def next(self):
        """-> a video row (--audio_encoder quartznet: with its clean sound, 'wav')."""
        while True:
            row = None
            with self.lock:
                if len(self.pool) >= self.POOL:
                    i = self.rng.randrange(len(self.pool))
                    row, self.pool[i] = self.pool[i], self.pool[-1]
                    self.pool.pop()
            if row is None:
                self._fill()
                continue
            if args.fifo3:                              # read only now: the pool stays small
                row['vcap'] = _row_vcap(self.name, row['_file'], row['id'])
                if row['vcap'] is None:
                    continue
            if args.speech_align:
                row['align'] = _row_align(self.name, row['_file'], row['id'])
                if row['align'] is None:
                    continue
            if args.audio_encoder in _WAV_ENCODERS:
                row['wav'] = _row_wav(self.name, row['_file'], row['id'])
                if row['wav'] is None:
                    continue
            return row


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
        if name not in _MEDIA_DATASETS and len(_anchors) < 24:
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
    """One batch row: the document it is currently reading (and a video's media)."""
    __slots__ = ['steps', 'pos', 'media', 'shown']

    def __init__(self):
        self.steps, self.pos, self.media, self.shown = [], 0, None, -1

    def load(self, steps, media=None):
        self.steps, self.pos, self.media, self.shown = steps, 0, media, -1


def worker(stop, q, datasets):
    """Per corpus, builder threads turn documents (and images) into clips on that corpus's
    queue; this loop advances every slot one token per step and puts (x_list, y_list,
    start_flags, new_images, media) on q. Slots are assigned to corpora in _MIX order;
    new_images lists (row, (uint8 image, name)) for image rows and (row, media dict) for video
    rows that started a new example this step; media = (per video row in _VIDEO_ROWS order the
    (frame, heard) indices of _video_example, [(video row index, uint8 [3, 224, 224] crop)]
    for the video rows whose frame on screen changed -- decoded here, off the GPU)."""
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

    def video_builder(name, cq):
        src = _VideoSource(name, args.seed)
        rng = random.Random(args.seed + 7)

        def build():
            return _video_example(src.next(), rng)
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
            vid = isinstance(got[1], dict)
            steps = got[1]['steps'] if vid else clip_text(got[0])
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
                 else video_builder(name, cq) if name in _VIDEO_DATASETS
                 else text_builder(name, datasets[name], cq))
        for _ in range(max(1, args.workers)):
            threading.Thread(target=run, args=(name, build, cq), daemon=True).start()

    global _ROW_SLOTS
    names = [n for n, k in _MIX for _ in range(k)]
    slots = _ROW_SLOTS = [_Slot() for _ in names]
    stagger = random.Random(args.seed)
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
                first = not slot.steps
                slot.load(steps, img if isinstance(img, dict) else None)
                if first and len(steps) > 1:
                    # Stagger: rows that all start together (step 0, a resume) all read <NUL> on
                    # a zero state -- identical inputs (<NUL> blanks the image too), so
                    # BatchNorm divides by a zero variance and the first update explodes (v402: grad 4e9, never recovered).
                    slot.pos = stagger.randrange(len(steps))
                if img is not None:
                    new_imgs.append((r, img))
        # an example starts at a clip's first step, or at a later piece's <NUL> (--seq rows)
        flags = [slot.pos == 0 or (slot.media is None and slot.steps[slot.pos][0] == _NULL) for slot in slots]
        xy = [slot.steps[slot.pos] for slot in slots]
        idx, shown = [], []
        for j, r in enumerate(_VIDEO_ROWS):
            sl = slots[r]
            f = sl.media['fi'][sl.pos]
            kd = sl.media.get('kind')        # --streams 3: the tick kinds of this step's target and input
            idx.append((f, sl.media['ai'][sl.pos], kd[sl.pos] if kd else 0,
                        kd[sl.pos - 1] if kd and sl.pos else 0))
            if f != sl.shown:
                sl.shown = f
                shown.append((j, _crop224(_decode_jpegs([sl.media['jpegs'][f]])[0], sl.media['off'])))
        for slot in slots:
            slot.pos += 1
        if args.fifo3:                       # every row as the three streams' (x, y)
            xy = [_as3(x, y) for x, y in xy]
        q.put(([x for x, _ in xy], [y for _, y in xy], flags, new_imgs, (idx, shown)))


hf_datasets, _ROW_SLOTS = {}, []
if not _ONESHOT:
    print('loading datasets...')
    _t_data = time.time()
    for name in dict.fromkeys(n for n, _ in _MIX):
        if name not in _MEDIA_DATASETS:
            hf_datasets[name] = _load_corpus(name, args.streaming, args.shards)
    _t_data = time.time() - _t_data
    print('datasets ready')


def _corpus_size(name):
    """Training examples in one pass over a corpus, for the STEP ep_ columns; None if unknown
    (streaming). An image corpus is counted as its file count times the rows of its first file
    (tools/img_prep.py writes the same number per file -- reading every footer takes minutes),
    less the held-out 1/_HOLDOUT_MOD."""
    if name in _VIDEO_DATASETS:
        import pyarrow.parquet as pq
        files = _video_files(name)
        return (sum(pq.ParquetFile(f).metadata.num_rows for f in files) or None) if files else None
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

model = VLAModel(S=args.context, n_hidden=args.n_hidden, c_context=args.c_context,
                 depth=args.depth, kernel=args.kernel, tokenizer=args.tokenizer,
                 windows=[float(w) for w in str(args.ctx_ema).split(',') if w.strip()],
                 read_norm=args.ctx_read_norm,
                 dec_kernels=[int(k) for k in str(args.dec_tree_kernels).split(',') if k.strip()],
                 dec_width=args.dec_width, bn_momentum=args.bn_momentum, init=args.init,
                 image_encoder=args.image_encoder, audio_encoder=args.audio_encoder,
                 nul_head=not args.inner_voice and (
                     bool(args.clock_hz) or (_loaded_ckpt is not None and
                                             'text_dec.nul.weight' in _loaded_ckpt['state_dict'])),
                 streams=args.streams, text_nul=args.fifo3,
                 surprise=_surprise)
if _loaded_ckpt is not None:
    _sd = _upgrade_state_dict(_loaded_ckpt['state_dict'])
    if _aud_switch:
        _sd = _switch_audio_state_dict(_sd, model, *_aud_switch)
    if model.streams == 3 and 'voc_dec.proj.weight' not in _sd:
        _sd = _widen_state_dict(_sd, model)
    missing, unexpected = model.load_state_dict(_sd, strict=False)
    bad = [k for k in missing if not re.match(r'(text|voc|img)_dec\.nul\.|surp_mean$|gain_mean$', k)] + \
          [k for k in unexpected if not ((args.inner_voice or model.streams == 3)
                                         and k.startswith('text_dec.nul.'))]
    if bad:
        raise SystemExit(f'{args.load} does not fit this model: {bad[:6]}')
    if [k for k in missing if k not in ('surp_mean', 'gain_mean')]:
        print('text_dec.nul (the <NUL> logit) is new: zero-initialized', flush=True)
    if unexpected:
        print('--inner_voice: the checkpoint\'s <NUL> logit (text_dec.nul) is dropped', flush=True)
if _surp_init is not None and float(model.surp_mean) == 0:
    model.surp_mean.fill_(_surp_init)
if args.use_ema:
    _e = (_loaded_ckpt or {}).get('weight_ema', {}).get(args.use_ema)
    if _e is None:
        raise SystemExit(f'--use_ema {args.use_ema}: {args.load} has no such average '
                         f'(it has {sorted((_loaded_ckpt or {}).get("weight_ema", {}))})')
    model.load_state_dict(_e, strict=False)
    print(f'--use_ema: weights replaced by the T={args.use_ema} running average', flush=True)
model = model.to(args.device)
_tokenizer = model.tok
_NUL_ID = model.nul_id
_SIL = _NUL_ID if _NUL_ID is not None else -100


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
            new, o = model.step(model.expand(torch.zeros(1, dtype=torch.long, device=dev)),
                                model.new_state(1, dev))
            model.heads(o)
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
            if model.audio_encoder == 'logmel':
                out.append(dict(name='aud_enc -> (audio grid)',
                                op=f'log-mel (fixed: STFT {_LM_NFFT}/{_LM_WIN}/{_LM_HOP}, {_LM_MELS} '
                                   f'mels, corpus mu/sd), last {S * S} cells of {_LM_FR} frames '
                                   f'(40 ms), RMSnorm',
                                inp=f'{(S * S * _LM_FR - 1) * _LM_HOP + _LM_NFFT} samples',
                                out=f'{model.aud_width}x{S}x{S}', tr=0, fr=0))
                srcs.insert(2 if model.img_enc is not None else 1, '(audio grid)')
            elif model.audio_encoder == 'quartznet':
                out.append(dict(name='aud_enc -> (audio grid)',
                                op=f'QuartzNet 15x5 C3 (frozen) over the last {_QN_WIN / _QN_SR:g} s, '
                                   f'last {S * S} cells of 80 ms, RMSnorm',
                                inp=f'{_QN_WIN} samples', out=f'{model.aud_width}x{S}x{S}', tr=0,
                                fr=model.aud_enc.n_params))
                srcs.insert(2 if model.img_enc is not None else 1, '(audio grid)')
            elif model.aud_enc is not None:
                mimi = model.aud_enc.__dict__['_mimi']
                out.append(dict(name='aud_enc -> (audio grid)',
                                op=f'Mimi codes -> latents (frozen), last {S * S} frames, RMSnorm',
                                inp=f'32x{S * S}', out=f'{model.aud_width}x{S}x{S}', tr=0,
                                fr=sum(p.numel() for p in mimi.quantizer.parameters())))
                srcs.insert(2 if model.img_enc is not None else 1, '(audio grid)')
            if model.streams == 3:         # the voice and image streams' token grids
                srcs[len(srcs) - model.K:len(srcs) - model.K] = ['(voice token grid)', '(image token grid)']
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
    # a long module name or op wraps onto continuation lines, so no line passes _GRAPH_WIDTH
    ws = max(max(len(r['inp']), len(r['out'])) for r in out)
    room = _GRAPH_WIDTH - (3 + 2 + 2 + 2 + ws + 4 + ws + 2 + 12)
    w = min(max(len(r['name']) for r in out), room * 2 // 5)
    wo = min(max(len(r['op']) for r in out), room - w)
    lines = [f'{"#":>3}  {"module":<{w}}  {"op":<{wo}}  {"in":>{ws}}    {"out":<{ws}}  {"params":>12}']
    for n, r in enumerate(out, 1):
        p = r['tr'] + r['fr']
        ps = '' if not p else f'{p:,}' + (' frozen' if r['fr'] and not r['tr'] else '')
        nm = textwrap.wrap(r['name'], w, break_on_hyphens=False) or ['']
        op = textwrap.wrap(r['op'], wo, break_on_hyphens=False) or ['']
        lines.append(f'{n:>3}  {nm[0]:<{w}}  {op[0]:<{wo}}  {r["inp"]:>{ws}} -> '
                     f'{r["out"]:<{ws}}  {ps:>12}'.rstrip())
        for a, b in itertools.zip_longest(nm[1:], op[1:], fillvalue=''):
            lines.append(f'{"":>3}  {a:<{w}}  {b}'.rstrip())
    return lines


_GRAPH_WIDTH = 270                # INFO model-graph lines fit the terminal


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
    """A prompt as ids, opened with _NULL like every training example."""
    return [_NULL] + (_tokenizer.encode(text) if text else [])


def _reg_rms(h):
    """Each register's RMS per row: [b, n_hidden * K, S, S] -> [b, K]."""
    return torch.stack([r.pow(2).mean(dim=(1, 2, 3)).sqrt() for r in h.chunk(model.K, dim=1)], 1)


def _tune_state(P, iters, cap, nat):
    """--prompt_tune: the initial registers h0 [b, ...] optimized by Adam (--prompt_tune_lr),
    BPTT through the prompt ids P [b, T] with the weights frozen, so the model predicts P
    from h0. cap > 0 holds each register's RMS to at most cap x nat [K] (its natural level)
    after every step. -> (h0, 'iter:nats ...' at log points)."""
    dev = P.device
    h0 = torch.zeros_like(model.new_state(P.shape[0], dev), requires_grad=True)
    opt = torch.optim.Adam([h0], lr=args.prompt_tune_lr)
    log = []
    for it in range(iters + 1):
        h, loss = h0, 0.0
        for t in range(P.shape[1] - 1):
            h, o = model.step(P[:, t], h)
            loss = loss + F.cross_entropy(model.text_dec(o).float(), P[:, t + 1])
        loss = loss / (P.shape[1] - 1)
        if it in (0, 10, 25, 50, 100, 200, 400) or it == iters:
            log.append(f'{it}:{float(loss.detach()):.3f}')
        if it == iters:
            break
        opt.zero_grad()
        loss.backward()
        opt.step()
        if cap:
            with torch.no_grad():
                f = (cap * nat / _reg_rms(h0).clamp(min=1e-8)).clamp(max=1.0)
                h0.mul_(f.repeat_interleave(model.n_hidden, 1)[:, :, None, None])
    h0 = h0.detach()
    if dev.type == 'cuda':
        torch.cuda.empty_cache()             # BPTT's peak, returned to a GPU shared with a trainer
    return h0, ' '.join(log)


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
        self.pct = None             # the last score()'s fluency (%), None if it had none

    def _load(self):
        if self.ref is not None or self.failed:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tok = AutoTokenizer.from_pretrained(self.repo)
            self.ref = AutoModelForCausalLM.from_pretrained(self.repo, dtype=torch.float32).to('cpu').eval()
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
        # the first 40 held-out documents (>= 100 words) of the first text eval corpus, a fixed
        # set, so fluency means the same in every run on that corpus; until its eval set is
        # built (the first eval) there are no anchors
        text = [c for c in _eval_corpus_names() if c not in _MEDIA_DATASETS]
        if not text or text[0] not in _eval_docs_cache:
            return False
        docs = [t for t in (_decode_plain(_doc_tokens(d)) for d in _eval_docs_cache[text[0]])
                if len(t.split()) >= 100][:40]
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
        self.pct = None
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
        self.pct = pct
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
    from safetensors.torch import save_file
    local = args.push_dir or os.path.basename(args.hub_repo)
    os.makedirs(local, exist_ok=True)
    print(f'saving {args.load or args.pretrained} to {local}/ ...')
    save_file({k: v.detach().cpu().clone().contiguous() for k, v in model.state_dict().items()},
              os.path.join(local, 'model.safetensors'))     # clone: the decoders share one lm_head
    with open(os.path.join(local, _HUB_ARGS), 'w') as f:
        json.dump({k: _loaded_ckpt.get(k) for k in ('saved_args', 'step', 'examples', 'examples_by')},
                  f, indent=1, default=str)
    if args.card:
        shutil.copy(args.card, os.path.join(local, 'README.md'))
    if args.hub_repo != '-':
        from huggingface_hub import HfApi
        api = HfApi()
        print(f'pushing to https://huggingface.co/{args.hub_repo} ...')
        api.create_repo(args.hub_repo, private=args.private, exist_ok=True)
        api.upload_folder(repo_id=args.hub_repo, folder_path=local,
                          commit_message=f'{os.path.basename(args.load or args.pretrained)} step {_start_step}')
        if args.hub_tag:
            api.create_tag(args.hub_repo, tag=args.hub_tag)
    print('done')
    raise SystemExit(0)

_LIVE_H = 480                 # --video: display height in px
_LIVE_TICK = 150              # --video: characters per ticker line


def _ff_json(path):
    """ffprobe: (fps, width, height, duration s) of the first video stream; fps 0 if none."""
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'stream=codec_type,avg_frame_rate,width,height:format=duration',
                        '-of', 'json', path], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    j = json.loads(r.stdout or '{}')
    v = next((st for st in j.get('streams', []) if st.get('codec_type') == 'video'), None)
    dur = float((j.get('format') or {}).get('duration') or 0)
    if v is None:
        return 0.0, 0, 0, dur
    n, d = (v.get('avg_frame_rate') or '0/1').split('/')
    return (float(n) / float(d) if float(d) else 0.0), int(v['width']), int(v['height']), dur


def _ff_audio(path, rate, ch):
    """The soundtrack as float32 [n, ch] at `rate` Hz ([0, ch] if none)."""
    a = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vn', '-ac', str(ch),
                        '-ar', str(rate), '-f', 'f32le', '-'], capture_output=True,
                       stdin=subprocess.DEVNULL).stdout
    return np.frombuffer(a, np.float32).reshape(-1, ch)


def _ff_frames2(path, fps=2.0):
    """The model's view of a video file: frames at `fps` (2, as tools/video_prep.py stores
    them, unless --vision_hz), short side 224, centre crops, uint8 [F, 3, 224, 224]."""
    vf = f"fps={fps:g},scale='if(gt(iw,ih),-2,224)':'if(gt(iw,ih),224,-2)'"
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-an', '-vf', vf,
                        '-q:v', '3', '-f', 'image2pipe', '-c:v', 'mjpeg', '-'],
                       capture_output=True, stdin=subprocess.DEVNULL).stdout
    starts, k = [], r.find(b'\xff\xd8\xff')
    while k >= 0:
        starts.append(k)
        k = r.find(b'\xff\xd8\xff', k + 3)
    jpegs = [r[a:b] for a, b in zip(starts, starts[1:] + [len(r)])]
    return torch.stack([_crop224(im) for im in _decode_jpegs(jpegs, 'cpu')])


def _write_wav(path, a, rate):
    """float32 [n, ch] -> 16-bit PCM wav."""
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(a.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes())


def _eval_video():
    """A random held-out FineVideo video: (local row, original mp4 path or None). The row (2 fps
    frames, Mimi codes, events) is what the model sees, as in training; the original mp4 is read
    from the same hub shard for the window and the sound (None if that fails)."""
    import pyarrow.parquet as pq
    rng = random.Random()
    files = _video_files('finevideo')
    if not files:
        raise SystemExit('--video eval: no FineVideo shards under '
                         f'{_VIDEO_DATASETS["finevideo"]["dir"]}')
    while True:
        f = rng.choice(files)
        pf = pq.ParquetFile(f)
        ids = pf.read(columns=['id']).column('id').to_pylist()
        held = [k for k, v in enumerate(ids) if _id_heldout(v)]
        if not held:
            continue
        k = rng.choice(held)
        bounds = np.cumsum([0] + [pf.metadata.row_group(g).num_rows
                                  for g in range(pf.metadata.num_row_groups)])
        g = int(np.searchsorted(bounds, k, side='right')) - 1
        row = pf.read_row_group(g, columns=_VID_COLS).to_pylist()[k - bounds[g]]
        row['_file'] = f
        if args.fifo3 and args.clock_hz:     # its sidecars, and a reference training would use
            row['vcap'] = _row_vcap('finevideo', f, row['id'])
            row['align'] = _row_align('finevideo', f, row['id']) if args.speech_align else None
            if row['vcap'] is None or (args.speech_align and row['align'] is None) or \
                    _clocked3_example(row, None, math.inf) is None:
                continue
        break
    print(f'--video eval: {row["id"]} ({row.get("category")}, {row["duration"]:.0f} s) '
          f'from {os.path.basename(f)}', flush=True)
    try:
        from huggingface_hub import HfFileSystem
        print('fetching the original mp4 from the hub shard ...', flush=True)
        hub = HfFileSystem()
        with hub.open(f'datasets/HuggingFaceFV/finevideo/data/{os.path.basename(f)}', 'rb') as h:
            up = pq.ParquetFile(h)
            for ug in range(up.metadata.num_row_groups):
                js = up.read_row_group(ug, columns=['json']).column('json').to_pylist()
                hit = [i for i, j in enumerate(js)
                       if os.path.splitext((j or {}).get('original_video_filename') or '')[0]
                       == row['id']]
                if hit:
                    mp4 = up.read_row_group(ug, columns=['mp4']).column('mp4')[hit[0]].as_py()
                    path = f'/dev/shm/vla_live_{os.getpid()}.mp4'
                    with open(path, 'wb') as out:
                        out.write(mp4)
                    return row, path
        print('--video eval: not found in the hub shard; showing the 2 fps frames', flush=True)
    except Exception as e:
        print(f'--video eval: hub fetch failed ({e!r}); showing the 2 fps frames', flush=True)
    return row, None


def _video_live():
    """--generate --video: the live player (see --video)."""
    import atexit
    import matplotlib.pyplot as plt
    dev = next(model.parameters()).device
    if model.img_enc is None or model.aud_enc is None:
        raise SystemExit('--video needs a model with image and audio encoders')
    model.eval()
    tmp = []
    atexit.register(lambda: [os.path.exists(p) and os.remove(p) for p in tmp])
    ref_ids = ref_times = ref3 = None
    if args.video == 'eval':
        row, path = _eval_video()
        if path:
            tmp.append(path)
        jp = row['frames']
        frames = torch.stack([_crop224(im) for im in _decode_jpegs(jp, 'cpu')])
        codes = torch.from_numpy(np.frombuffer(row['codes'], '<i2').reshape(32, -1).copy())
        dur = float(row['duration'])
        if args.clock_hz and args.fifo3:     # each stream's reference as training places it
            ys = [y for _, y in _clocked3_example(row, None, math.inf)[1]['steps']]
            ref3 = {st: ([ys[k][st] for k in range(len(ys)) if ys[k][st] != _SIL],
                         [k / args.clock_hz for k in range(len(ys)) if ys[k][st] != _SIL])
                    for st in range(3)}
            rate = args.clock_hz
        elif args.clock_hz:      # the reference as training places it: tokens on free ticks
            ys = [y for _, y in _clocked_example(row, None, math.inf)[1]['steps']]
            at = [k for k, y in enumerate(ys) if y != _SIL]
            ref_ids, ref_times = [ys[k] for k in at], [k / args.clock_hz for k in at]
            rate = args.clock_hz
        else:
            ref_ids, ref_times = _timed_tokens(_video_events(row), _event_tokens(_video_events(row)))
            rate = len(ref_ids) / max(dur, 1e-3)
        name = f'{row["id"]}  {row.get("category") or ""}  (held-out FineVideo)'
    else:
        path = args.video
        if not os.path.exists(path):
            raise SystemExit(f'--video: no such file {path}')
        print(f'--video: preparing {path} (2 fps frames, Mimi codes) ...', flush=True)
        vfps = args.vision_hz or 2.0
        frames = _ff_frames2(path, vfps)
        codes = (torch.zeros(32, 0, dtype=torch.short) if model.audio_encoder in _WAV_ENCODERS
                 else model.aud_enc.codes(_ff_audio(path, 24000, 1)[:, 0], dev))
        dur, rate, name = _ff_json(path)[3], args.clock_hz or args.video_rate, os.path.basename(path)
    if len(frames) == 0:
        raise SystemExit('--video: no frames')
    w16 = None                   # quartznet: the clean 16 kHz sound it hears
    if model.audio_encoder in _WAV_ENCODERS:
        w16 = _row_wav('finevideo', row['_file'], row['id']) if args.video == 'eval' else None
        if w16 is None:
            w16 = (np.clip(_ff_audio(path, _QN_SR, 1)[:, 0], -1, 1) * 32767).astype(np.int16) \
                if path else np.zeros(0, np.int16)
        lat = torch.from_numpy(_qn_buffer(w16, 0, len(w16) // _QN_HOP)).to(dev)
    else:
        lat = model.aud_enc.latents(codes, dev)
    clip = _VideoClip(frames, lat, codes, [0], [0], 2.0 if args.video == 'eval' else vfps, 0.0,
                      rate, (name, '', ''))
    # what the window shows and plays: the original file, else the 2 fps frames and the sound
    # Mimi decodes from the codes
    wav = f'/dev/shm/vla_live_{os.getpid()}.wav'
    tmp.append(wav)
    if path and args.video_sound == 'original':
        _write_wav(wav, _ff_audio(path, 48000, 2), 48000)
    elif w16 is not None:       # what the model hears: the clean 16 kHz sound
        _write_wav(wav, (w16.astype(np.float32) / 32768.0)[:, None], _QN_SR)
    else:       # what the model hears: its Mimi codes decoded back to 24 kHz sound
        _write_wav(wav, model.aud_enc.audio(codes, dev)[:, None], 24000)
    if path:
        fps, w, h, d2 = _ff_json(path)
        dur = dur or d2
        W = max(2, round(w * _LIVE_H / max(h, 1) / 2) * 2)
    else:
        fps, W = 2.0, round(frames.shape[3] * _LIVE_H / frames.shape[2])
        raw = [im.permute(1, 2, 0).numpy() for im in _decode_jpegs(row['frames'], 'cpu')]
    has_sound = os.path.getsize(wav) > 1000 and (codes.shape[-1] > 0 or
                                                 (w16 is not None and len(w16) > 0))
    dur = dur or len(frames) / 2.0
    print(f'--video: {name}: {dur:.1f} s at {fps:.2f} fps, '
          f'{"one step per tick at %g Hz" % rate if args.clock_hz else "captioned at %.2f tokens/s" % rate}'
          f'{"" if has_sound else " (no sound)"}; x closes', flush=True)

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12.8, 9.0), dpi=100)
    fig.canvas.manager.set_window_title(f'vla --video  {name}')
    ax = fig.add_axes([0.01, 0.20, 0.98, 0.74])
    ax.set_axis_off()
    im = ax.imshow(np.zeros((_LIVE_H, W, 3), np.uint8), interpolation='bilinear')
    hud = ax.text(0.995, 0.99, '', transform=ax.transAxes, ha='right', va='top', fontsize=12,
                  family='monospace', color='white',
                  bbox=dict(facecolor='black', alpha=0.6, pad=3, edgecolor='none'))
    snd = ('original' if path and args.video_sound == 'original' else
           'clean 16 kHz (what the model hears)' if w16 is not None else 'Mimi (what the model hears)')
    fig.text(0.01, 0.975, f'{name}   {args.load or args.pretrained}   T={args.temperature:g}   '
             f'sound: {snd}',
             fontsize=9, family='monospace', color='0.7', va='top')
    kw = dict(fontsize=10, family='monospace', va='center', ha='left')
    S3 = model.streams == 3          # one line per stream: hears (voice), sees (image), thinks (text)
    tick_ref3 = {}
    if S3 and ref3 is not None:      # --fifo3: each stream's reference above it
        tick3 = {}
        for y_, (lab, st, col) in zip((0.163, 0.103, 0.043), (('HEAR', 1, 'white'), ('SEE', 2, 'white'),
                                                          ('THINK', 0, 'skyblue'))):
            fig.text(0.01, y_ + 0.025, 'REF', color='limegreen', **kw)
            tick_ref3[st] = fig.text(0.07, y_ + 0.025, '', color='limegreen', **kw)
            fig.text(0.01, y_, lab, color=col, **kw)
            tick3[st] = fig.text(0.07, y_, '', color=col, **kw)
        tick_gen = tick3[1]
    elif S3:
        tick3 = {}
        if ref_ids is not None:
            fig.text(0.01, 0.17, 'REF', color='limegreen', **kw)
            tick_ref = fig.text(0.07, 0.17, '', color='limegreen', **kw)
        for y_, (lab, st, col) in zip((0.125, 0.08, 0.035), (('HEAR', 1, 'white'), ('SEE', 2, 'white'),
                                                            ('THINK', 0, 'skyblue'))):
            fig.text(0.01, y_, lab, color=col, **kw)
            tick3[st] = fig.text(0.07, y_, '', color=col, **kw)
        tick_gen = tick3[1]
    elif ref_ids is not None:
        fig.text(0.01, 0.155, 'REF', color='limegreen', **kw)
        tick_ref = fig.text(0.05, 0.155, '', color='limegreen', **kw)
        fig.text(0.01, 0.09, 'VLA', color='white', **kw)
        tick_gen = fig.text(0.05, 0.09, '', color='white', **kw)
    else:
        fig.text(0.01, 0.12, 'VLA', color='white', **kw)
        tick_gen = fig.text(0.05, 0.12, '', color='white', **kw)
    _exit = [False]
    fig.canvas.mpl_connect('key_press_event',
                           lambda e: _exit.__setitem__(0, _exit[0] or e.key in ('x', 'X')))
    fig.canvas.mpl_connect('close_event', lambda e: _exit.__setitem__(0, True))
    plt.show(block=False)

    def clean(t):
        return t.replace('\n', ' / ')

    gen_done, ref_done = '', ''      # earlier plays' text; this play's is decoded whole, so a
    gen_ids, ref_now = [], []        # character split over several tokens renders correctly
    done3, gen3, n3 = {0: '', 1: '', 2: ''}, {0: [], 1: [], 2: []}, {0: -1, 1: -1, 2: -1}
    rdone3, rnow3 = {0: '', 1: '', 2: ''}, {0: [], 1: [], 2: []}    # --fifo3 references
    prompt = _prompt_ids(args.prompt)
    t_all, player, pipe, plays = time.monotonic(), None, None, 0
    try:
        while not _exit[0]:
            # one play of the video: <NUL> + prompt on fresh registers, then live captions
            if plays:
                gen_done += clean(_decode_plain(gen_ids)) + ' <NUL> '
                ref_done += clean(_decode_plain(ref_now)) + ' <NUL> '
                for st in done3:
                    done3[st] += clean(_decode_plain(gen3[st])) + ' <NUL> '
                    rdone3[st] += clean(_decode_plain(rnow3[st])) + ' <NUL> '
            gen3, rnow3, rn3 = {0: [], 1: [], 2: []}, {0: [], 1: [], 2: []}, {0: -1, 1: -1, 2: -1}
            gen_ids, ref_now = list(prompt[1:]), []
            n3 = {0: -1, 1: -1, 2: -1}
            plays += 1
            if path:
                # -nostdin and no stdin: an ffmpeg on the terminal puts the tty in raw mode
                # and, when killed at the end of a play, never restores it
                pipe = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-an',
                                         '-vf', f'scale={W}:{_LIVE_H}', '-f', 'rawvideo',
                                         '-pix_fmt', 'rgb24', '-'], stdin=subprocess.DEVNULL,
                                        stdout=subprocess.PIPE, bufsize=10 ** 7)
            player = subprocess.Popen(['pw-play', wav], stdin=subprocess.DEVNULL,
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL) if has_sound else None
            t0 = time.monotonic()
            dff, logits, pos, shown, nref = model.new_state(1, dev), None, 0, -1, 0
            pending = list(prompt)
            n_gen = n_ref = -1
            while not _exit[0]:
                t = time.monotonic() - t0
                if t >= dur or (args.video_seconds and time.monotonic() - t_all
                                >= args.video_seconds):
                    break
                # the model: every token due by now, each at its own media time
                with torch.no_grad():
                    while (pos + clip.phase) / rate <= t:
                        if S3:
                            if pending:
                                xin = model.expand(torch.tensor([pending.pop(0)], device=dev))
                            else:
                                prob = F.softmax(logits[0] / max(args.temperature, 1e-6), dim=-1)
                                b3 = torch.multinomial(_truncate(prob), 1)[:, 0]
                                for st in range(3):
                                    if int(b3[st]) != _NUL_ID:
                                        gen3[st].append(int(b3[st]))
                                xin = torch.where(b3 == _NUL_ID, _PAD, b3)[None]
                            img, aud = clip.grids(model, [clip.at(pos)], dev)
                            dff, o = model.step(xin, dff, img, aud)
                            logits = model.heads(o)
                            pos += 1
                            continue
                        if pending:
                            b = pending.pop(0)
                        else:
                            prob = F.softmax(logits[0] / max(args.temperature, 1e-6), dim=-1)
                            b = torch.multinomial(_truncate(prob), 1).item()
                            if b == _NUL_ID:
                                b = _PAD                # nothing said this tick
                            else:
                                gen_ids.append(b)
                                if (args.inner_voice and args.voice_drop and
                                        random.random() < args.voice_drop):
                                    b = _PAD            # said (shown) but not fed back
                        img, aud = clip.grids(model, [clip.at(pos)], dev)
                        dff, o = model.step(torch.tensor([b], device=dev), dff, img, aud)
                        logits = model.text_dec(o)
                        pos += 1
                if ref_ids is not None:
                    while nref < len(ref_ids) and ref_times[nref] <= t:
                        ref_now.append(ref_ids[nref])
                        nref += 1
                for st, (rids, rts) in (ref3 or {}).items():
                    while len(rnow3[st]) < len(rids) and rts[len(rnow3[st])] <= t:
                        rnow3[st].append(rids[len(rnow3[st])])
                # the picture: the frame due now (frames behind the clock are skipped)
                want = int(t * fps)
                if path:
                    while shown < want:
                        buf = pipe.stdout.read(W * _LIVE_H * 3)
                        if len(buf) < W * _LIVE_H * 3:
                            break
                        shown += 1
                    if shown == want:
                        im.set_data(np.frombuffer(buf, np.uint8).reshape(_LIVE_H, W, 3))
                elif want != shown and want < len(raw):
                    shown = want
                    im.set_data(raw[want])
                hud.set_text(f'{fps:.2f} fps  frame {max(shown, 0):d}\n'
                             f'{t:6.1f} / {dur:.1f} s  play {plays}')
                if S3:
                    for st in range(3):
                        if len(gen3[st]) != n3[st]:
                            n3[st] = len(gen3[st])
                            tick3[st].set_text((done3[st] + clean(_decode_plain(gen3[st])))[-_LIVE_TICK:])
                        if st in tick_ref3 and len(rnow3[st]) != rn3[st]:
                            rn3[st] = len(rnow3[st])
                            tick_ref3[st].set_text((rdone3[st] + clean(_decode_plain(rnow3[st])))[-_LIVE_TICK:])
                elif len(gen_ids) != n_gen:
                    n_gen = len(gen_ids)
                    tick_gen.set_text((gen_done + clean(_decode_plain(gen_ids)))[-_LIVE_TICK:])
                if ref_ids is not None and len(ref_now) != n_ref:
                    n_ref = len(ref_now)
                    tick_ref.set_text((ref_done + clean(_decode_plain(ref_now)))[-_LIVE_TICK:])
                fig.canvas.draw_idle()
                fig.canvas.start_event_loop(0.001)
            for p in (player, pipe):
                if p is not None and p.poll() is None:
                    p.kill()
            if args.video_seconds and time.monotonic() - t_all >= args.video_seconds:
                break
    finally:
        for p in (player, pipe):
            if p is not None and p.poll() is None:
                p.kill()
        if args.video_save:
            fig.savefig(args.video_save, dpi=100)
            print(f'saved {args.video_save}')
    print(f'--video: {plays} play(s)')
    if S3:
        for lab, st in (('HEAR', 1), ('SEE', 2), ('THINK', 0)):
            print(f'{lab}:', (done3[st] + clean(_decode_plain(gen3[st])))[-2000:])
    else:
        print('VLA:', (gen_done + clean(_decode_plain(gen_ids)))[-2000:])
    raise SystemExit(0)


if args.generate and args.video:
    _video_live()

if args.generate:
    if args.load is None and args.pretrained is None:
        print('WARNING: --generate without --load/--pretrained is running an untrained model')
    prompt = _prompt_ids(args.prompt)
    if not args.prompt_tune:
        print(_render(prompt + model.generate(prompt, args.n, temperature=args.temperature,
                                              image=_image)))
        raise SystemExit(0)
    # --prompt_tune: the start state tuned on --prompt (as in --prompt_tune's TUNE), then the
    # prompt read from it; the cold continuation (zero state) with the same seed, to compare
    if len(prompt) < 3:
        raise SystemExit('--generate --prompt_tune needs a --prompt of at least two tokens')
    dev = next(model.parameters()).device
    model.eval()
    for q in model.parameters():
        q.requires_grad_(False)
    P = torch.tensor([prompt], device=dev)
    with torch.no_grad():
        h = model.new_state(1, dev)
        for t in prompt:
            h, _ = model.step(torch.tensor([t], device=dev), h)
    nat = _reg_rms(h)[0]
    seed = random.randrange(2 ** 31)
    for cap in [None] + [float(c) for c in args.prompt_tune_cap.split(',')]:
        if cap is None:
            h0, tag = None, 'cold'
        else:
            h0, log = _tune_state(P, args.prompt_tune, cap, nat)
            tag = f'tuned cap {cap:g}, prompt nats by iter {log}'
        torch.manual_seed(seed)
        out = model.generate(prompt, args.n, temperature=args.temperature, image=_image, h0=h0)
        print(f'===== {tag} =====\n{_render(prompt)} ‖ {_render(out)}\n', flush=True)
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
    if _image is not None:                           # the prompt image above P(next token)
        ki = max(1, rows // 3)
        ax_i = fig.add_subplot(gs[:ki, 1])
        ax_i.imshow(_image.permute(1, 2, 0).numpy())
        ax_i.set_axis_off()
        ax_i.set_title(f'image  {os.path.basename(args.image)}  '
                       f'({_image.shape[2]}x{_image.shape[1]})', fontsize=9, pad=3)
        ax_p = fig.add_subplot(gs[ki:, 1])
    else:
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
    cur = list(prompt)                               # ids so far (the ticker's tail)
    dff = model.new_state(1, dev)
    bank = _bank([_image], dev) if _image is not None else None
    imgs, vmax, img_p, nstep = [None] * rows, [None] * rows, None, 0
    while not _exit[0] and plt.fignum_exists(fig.number):
        with torch.no_grad():
            img = model.image_grid(_views(*bank)) if bank is not None else None
            dff, o = model.step(torch.tensor([b], device=dev), dff, img)
            prob = F.softmax(model.text_dec(o)[0] / max(args.temperature, 1e-6), dim=-1)
        nstep += 1
        if pending:
            b = pending.pop(0)
        else:
            b = int(torch.multinomial(_truncate(prob), 1).item())
            cur = (cur + [b])[-2 * _VIS_WIN:]
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
        ticker = ''.join(DOT_TEXT if c in '$\\' else c for c in _render(cur))[-_VIS_WIN:]
        header.set_text(f'step {nstep:8d}  dff_std {float(dff.std()):6.4f}  dff_max '
                        f'{float(dff.abs().max()):7.3f}  p_max {float(prob.max()):5.3f}  '
                        f'T {args.temperature:.2f}\ngen: {ticker}')
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(args.delay)
    raise SystemExit(0)

def _stream_xy(x, y, kin, kout, video):
    """--streams 3: one-stream inputs / targets x, y [B], the kinds of their ticks kin (x's)
    and kout (y's; 0 silent, 1 speech, 2 activity), and video [B] bool -> X, Y [B, 3] for the
    text, voice and image streams. A text row's word is the text stream's: voice and image read
    _PAD and target <NUL>. A video row's caption word is voice's (speech) or image's (activity):
    the other stream reads _PAD and targets <NUL>, and text reads _PAD with no target (-100; the
    caller feeds it the inner voice, the model's own last text word). _NULL blinks all three."""
    st_in = torch.where(video, torch.where(kin > 0, kin, -1), 0)
    st_out = torch.where(video, torch.where(kout > 0, kout, -1), 0)
    X = torch.stack([torch.where(st_in == k, x, _PAD) for k in range(3)], dim=1)
    X = torch.where((x == _NULL)[:, None], _NULL, X)
    Y = torch.stack([torch.where(st_out == 0, y, -100)] +
                    [torch.where(st_out == k, y, _NUL_ID) for k in (1, 2)], dim=1)
    return X, Y


# ── held-out eval ─────────────────────────────────────────────────────────────
# Each held-out set is built once and reused, so successive EVAL lines differ only by the
# weights. Every eval runs on a fresh state and restores the training state afterwards.

_eval_docs_cache = {}        # corpus -> [[(x, y), ...], ...]
_eval_imgs = {}              # image corpus -> [uint8 image] aligned with its eval docs
_eval_meta = {}              # image corpus -> [(id, class, caption)] aligned likewise
_eval_vids = {}              # video corpus -> [_VideoClip] aligned with its eval docs
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
    """--eval_docs held-out captions of an image corpus with their images, sorted by length:
    the first held-out row of each of --eval_docs files spread over the (sorted) shards, or,
    when there are fewer files, the first ceil(--eval_docs / files) of every file.
    eval_group0 corpora look only in row group 0 (their eval set as first defined)."""
    import pyarrow.parquet as pq
    cfg = _IMAGE_DATASETS[corpus]
    files = sorted(glob.glob(os.path.join(cfg['dir'], '*.parquet')))
    items = []
    per = max(1, math.ceil(args.eval_docs / max(1, len(files))))
    for f in files[::max(1, len(files) // max(1, args.eval_docs))]:
        pf, got = pq.ParquetFile(f), 0
        for g in range(1 if cfg.get('eval_group0') else pf.metadata.num_row_groups):
            for r in pf.read_row_group(g, columns=['image', 'id', 'class',
                                                   *_caption_cols(cfg)]).to_pylist():
                cap = _caption_of(r, cfg)
                if cap and _id_heldout(r['id']) and got < per:
                    items.append((clip_text(cap)[:_EVAL_MAXLEN], _decode_image(r),
                                  (r['id'], r['class'], cap)))
                    got += 1
            if got >= per or len(items) >= args.eval_docs:
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


def _clip_of(r, m, dev):
    """A video row and its example's media (see _video_example) -> a _VideoClip: centre-crop
    frames on the CPU, the sound on dev."""
    frames = torch.stack([_crop224(im) for im in _decode_jpegs(m['jpegs'], 'cpu')])
    if model.audio_encoder in _WAV_ENCODERS:
        lat = torch.from_numpy(m['wav']).to(dev)
    elif model.aud_enc is not None:
        lat = model.aud_enc.latents(m['codes'], dev)
    else:
        lat = torch.zeros(_AUD_DIM, m['codes'].shape[1], device=dev)
    span = max(m['t1'] - m['t0'], 1e-3)
    ref = ' '.join(t for _, _, _, t in json.loads(r['events']))
    clip = _VideoClip(frames, lat, m['codes'], m['fi'], m['ai'], m['fps'], m['t0'],
                      args.clock_hz or m['n'] / span, (r['id'], r.get('category') or '', ref))
    clip.kind = m.get('kind')       # --clock_hz: speech / activity per tick (EVALS)
    clip.f0, clip.a0 = m['f0'], m['a0']       # first frame / grid cell kept (the GEN window)
    return clip


def _gen_clip(corpus, rng):
    """A random held-out video of a local video corpus for the GEN window -- a fresh one each
    refresh, not the eval set -- as (steps, clip), its window starting at a random event (a
    fresh state, as training starts one); None if none was found."""
    import pyarrow.parquet as pq
    held = _VIDEO_DATASETS[corpus].get('eval') is None
    files = _video_files(corpus, 'eval')
    if model.audio_encoder in _WAV_ENCODERS:
        files = [f for f in files if os.path.exists(_sidecar_path(corpus, f) or '')]
    if args.fifo3:
        files = [f for f in files if os.path.exists(_vcap_path(corpus, f) or '')]
    if args.speech_align:
        files = [f for f in files if os.path.exists(_align_path(corpus, f) or '')]
    for _ in range(8):
        if not files:
            return None
        f = rng.choice(files)
        pf = pq.ParquetFile(f)
        ids = pf.read(columns=['id']).column('id').to_pylist()
        pick = [k for k, v in enumerate(ids) if not held or _id_heldout(v)]
        if not pick:
            continue
        k = rng.choice(pick)
        bounds = np.cumsum([0] + [pf.metadata.row_group(g).num_rows
                                  for g in range(pf.metadata.num_row_groups)])
        g = int(np.searchsorted(bounds, k, side='right')) - 1
        r = pf.read_row_group(g, columns=_VID_COLS).to_pylist()[k - bounds[g]]
        if model.audio_encoder in _WAV_ENCODERS:
            r['wav'] = _row_wav(corpus, f, r['id'])
            if r['wav'] is None:
                continue
        if args.fifo3:
            r['vcap'] = _row_vcap(corpus, f, r['id'])
            if r['vcap'] is None:
                continue
        if args.speech_align:
            r['align'] = _row_align(corpus, f, r['id'])
            if r['align'] is None:
                continue
        ex = _video_example(r, rng, maxspan=_GENV_SPAN)
        if ex is None or _ntok(ex[1]['steps']) < _VID_EVAL_MINTOK:
            continue
        return ex[1]['steps'], _clip_of(r, ex[1], next(model.parameters()).device)
    return None


def _timed_text(ids, ticks, t0, rate, limit, every=None):
    """Token ids, each at tick k = media time t0 + k / rate -> their text with a [Ns] mark
    before the first token of each `every` seconds, cut once about `limit` characters of text
    (marks not counted) are out."""
    every = every or _GENV_MARK
    segs, n = [], 0
    for y, k in zip(ids, ticks):
        if n >= limit:
            break
        m = int((t0 + k / rate) // every)
        if not segs or segs[-1][0] != m:
            segs.append((m, []))
        segs[-1][1].append(y)
        n += len(_decode_plain([y]))
    return ' '.join(f'[{m * every:.0f}s] ' + _decode_plain(ys).replace(chr(10), ' / ').strip()
                    for m, ys in segs)


def _build_video_eval(corpus):
    """Up to _VID_EVAL_CLIPS held-out videos of a video corpus (its eval files spread evenly,
    else the id-hash held-out rows of the train files in name order, so the set is stable as
    prep adds files), each the opening window of at most _VID_EVAL_MAXLEN tokens (see
    _video_example), with its frames (centre crops) and Mimi latents, sorted by length. Only
    the row groups holding a chosen row are read."""
    import pyarrow.parquet as pq
    cfg = _VIDEO_DATASETS[corpus]
    files = _video_files(corpus, 'eval')
    held = cfg.get('eval') is None
    want = min(args.eval_docs, _VID_EVAL_CLIPS)
    if not held:
        files = files[::max(1, len(files) // want)]
    per = 1 << 30 if held else max(1, math.ceil(want / max(1, len(files))))
    dev = next(model.parameters()).device
    items, no_wav = [], 0
    for f in files:
        if len(items) >= want:
            break
        pf = pq.ParquetFile(f)
        ids = pf.read(columns=['id']).column('id').to_pylist()
        pick = [k for k, v in enumerate(ids) if not held or _id_heldout(v)][:per]
        bounds = np.cumsum([0] + [pf.metadata.row_group(g).num_rows
                                  for g in range(pf.metadata.num_row_groups)])
        for g in sorted({int(np.searchsorted(bounds, k, side='right')) - 1 for k in pick}):
            rows = pf.read_row_group(g, columns=_VID_COLS).to_pylist()
            for k in pick:
                if not bounds[g] <= k < bounds[g + 1] or len(items) >= want:
                    continue
                r = rows[k - bounds[g]]
                if model.audio_encoder in _WAV_ENCODERS:
                    r['wav'] = _row_wav(corpus, f, r['id'])
                    if r['wav'] is None:
                        no_wav += 1
                        continue
                if args.fifo3:
                    r['vcap'] = _row_vcap(corpus, f, r['id'])
                    if r['vcap'] is None:
                        no_wav += 1
                        continue
                if args.speech_align:
                    r['align'] = _row_align(corpus, f, r['id'])
                    if r['align'] is None:
                        no_wav += 1
                        continue
                ex = _video_example(r, None, maxtok=min(_EVAL_MAXLEN, _VID_EVAL_MAXLEN),
                                    maxspan=_VID_EVAL_SPAN if args.clock_hz else _VID_MAXSPAN)
                if ex is None or _ntok(ex[1]['steps']) < _VID_EVAL_MINTOK:
                    continue
                text, m = ex
                clip = _clip_of(r, m, dev)
                if model.audio_encoder in _WAV_ENCODERS:
                    clip.precompute_audio(model, dev)
                items.append((m['steps'], clip))
    items.sort(key=lambda it: len(it[0]))
    _eval_vids[corpus] = [it[1] for it in items]
    docs = [it[0] for it in items]
    print(f'eval set: {corpus} {len(docs)} held-out videos from {len(files)} files, '
          f'{sum(len(d) for d in docs)} tokens', flush=True)
    if no_wav:
        print(f'WARNING: eval set {corpus}: {no_wav} held-out videos skipped, their sidecar '
              f'sound / visual captions are not there yet (the set differs from a full corpus\'s)', flush=True)
    return docs


def _build_eval_docs(corpus):
    """The first --eval_docs held-out documents of `corpus`, framed like training clips,
    clipped to _EVAL_MAXLEN, sorted by length."""
    from datasets import load_dataset
    if corpus in _IMAGE_DATASETS:
        return _build_image_eval(corpus)
    if corpus in _VIDEO_DATASETS:
        return _build_video_eval(corpus)
    hf, cfg, split, col = _eval_source(corpus)
    hashed = corpus in _HASH_HOLDOUT
    if corpus in _LOCAL_PARQUET:
        hf = _LOCAL_PARQUET[corpus]
        rows = load_dataset('parquet', data_files={'train': _local_files(corpus)}, split='train', streaming=True)
    elif hashed and corpus in _HUB_SUBSET:
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
        steps = clip_text(text.split(_PIECE_SEP)[0])      # a row of pieces: its first
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
    """An eval document as its token list, _NULL first."""
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
        shp = (B, T, 3) if isinstance(chunk[0][1][0], tuple) else (B, T)   # --fifo3 clips
        X = torch.zeros(shp, dtype=torch.long)
        Y = torch.zeros(shp, dtype=torch.long)
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
                cnt.update(v for _, y in d for v in (y if isinstance(y, tuple) else (y,)))
        V = max(model.vocab, max(cnt) + 1 if cnt else 1)
        edges = [int(e) for e in args.eval_bands.split(',') if e.strip()]
        band = torch.full((V,), len(edges), dtype=torch.long)
        for r, (tid, _) in enumerate(cnt.most_common()):
            band[tid] = sum(r >= e for e in edges)
        _band_cache['b'] = band
        print(f'--eval_bands: ranks from {sum(cnt.values())} held-out tokens, {len(cnt)} '
              f'distinct; edges {edges}', flush=True)
    return _band_cache['b'].to(dev)


def _score3f_tick(X3, Y3, video, free, own3, img, aud, Mt3, Mnt3, nul3, kce, kn, gen, bands):
    """--fifo3, one eval tick: X3, Y3 [B, 3] the streams' inputs and targets (the dataset's),
    Mt3 / Mnt3 [B, 3] bool their word / <NUL> targets; own3 [B, 3] each stream's sample at the
    last tick. free (EVALF): every stream reads its own last sample instead (no word after its
    own <NUL>), as in the live demo. -> (summed word loss [B], words [B], largest word loss
    [B], this tick's samples [B, 3] or None). Per-stream word loss (kce / kn: 1 voice, 2 image,
    3 text), <NUL> statistics (nul3 by stream) and bands = (band_of, bsum, bcnt) accumulate."""
    B = X3.shape[0]
    if free and own3 is not None and video:
        X3 = torch.where(X3 == _NULL, X3, torch.where(own3 == _NUL_ID, _PAD, own3))
    logits, _ = model(X3, img=img, aud=aud)                       # [B, 3, V]
    V = logits.shape[-1]
    samp = None
    if free and video:
        samp = torch.multinomial(_truncate(F.softmax(logits.float().view(-1, V), dim=-1)), 1,
                                 generator=gen).view(B, 3)
    ce3 = F.cross_entropy(logits.view(-1, V), Y3.clamp(min=0).view(-1), reduction='none').view(B, 3)
    ce3 = torch.where(torch.isfinite(ce3), ce3, torch.full_like(ce3, 1e30))
    w = Mt3.float()
    if video:
        pn = F.softmax(logits.float(), dim=-1)[:, :, _NUL_ID]     # [B, 3]
        for kk, st in ((1, 1), (2, 2), (3, 0)):
            kce[kk] += float((ce3[:, st].clamp(max=30) * Mt3[:, st]).sum())
            kn[kk] += int(Mt3[:, st].sum())
            d = nul3[st]
            d['ce'] += float((ce3[:, st].clamp(max=30) * Mnt3[:, st]).sum())
            d['n'] += int(Mnt3[:, st].sum())
            d['p_nul'] += float((pn[:, st] * Mnt3[:, st]).sum())
            d['p_tok'] += float((pn[:, st] * Mt3[:, st]).sum())
            d['n_tok'] += int(Mt3[:, st].sum())
    if bands is not None:
        band_of, bsum, bcnt = bands
        oh = F.one_hot(band_of[Y3.clamp(0, band_of.numel() - 1)], bsum.shape[1]).float() * w[..., None]
        bsum += (oh * ce3[..., None]).sum(1)
        bcnt += oh.sum(1)
    return (ce3 * w).sum(1), w.sum(1), (ce3 * w).max(1).values, samp


def _score3_tick(x, y, Kd, t, video, free, own3, img, aud, Mt, Mnt, nul3, gen):
    """--streams 3, one eval tick: x, y [B] one-stream input / target, Kd [B, T] tick kinds
    (None: text docs), video: the rows are clips, own3 [B, 3] each stream's sample at the last
    tick (None at the first). Training's streams (see _stream_xy); a clip's text stream reads its
    own word, and free (EVALF) every stream reads its own (no word after a <NUL>). -> (loss [B]
    of the word y in the stream that owns it, this tick's samples [B, 3]); the voice / image
    <NUL> statistics of clips accumulate in nul3."""
    B = x.shape[0]
    z = torch.zeros_like(x)
    kout = Kd[:, t] if Kd is not None else z
    kin = Kd[:, t - 1] if Kd is not None and t else z
    vid = torch.full((B,), bool(video), dtype=torch.bool, device=x.device)
    X3, Y3 = _stream_xy(x, y, kin, kout, vid)
    if own3 is not None and video:
        fed = torch.where(own3 == _NUL_ID, _PAD, own3)
        if free:                       # EVALF: every stream its own
            X3 = torch.where(X3 == _NULL, X3, fed)
        else:                          # the inner voice
            X3[:, 0] = torch.where(X3[:, 0] == _PAD, fed[:, 0], X3[:, 0])
    logits, _ = model(X3, img=img, aud=aud)                       # [B, 3, V]
    V = logits.shape[-1]
    samp = None
    if video:
        samp = torch.multinomial(_truncate(F.softmax(logits.float().view(-1, V), dim=-1)), 1,
                                 generator=gen).view(B, 3)
    ce3 = F.cross_entropy(logits.view(-1, V), Y3.view(-1), reduction='none').view(B, 3)
    st = torch.where(vid, kout.clamp(min=0), 0)                   # the stream y belongs to
    ce = ce3.gather(1, st[:, None])[:, 0]
    if video:
        pn = F.softmax(logits.float(), dim=-1)[:, :, _NUL_ID]     # [B, 3]
        for k in (1, 2):
            isn = (Y3[:, k] == _NUL_ID) & (Mt | Mnt)
            tok = Mt & (kout == k)
            d = nul3[k]
            d['ce'] += float((ce3[:, k].clamp(max=30) * isn).sum())
            d['n'] += int(isn.sum())
            d['p_nul'] += float((pn[:, k] * isn).sum())
            d['p_tok'] += float((pn[:, k] * tok).sum())
            d['n_tok'] += int(tok.sum())
    return ce, samp


def _score(step, corpus, docs, imgs=None, tag=None, clips=None, bands=True, free=False):
    """EVAL (clean / median / runaway%) and EVALB (loss by frequency band) lines, tagged
    `tag` (default corpus). imgs: one image per doc, seen through a fresh random crop every
    token from a fixed-seed generator, so successive evals see the same crops. clips: one
    _VideoClip per doc, its frame and sound at each step (blanked where it is blind / deaf).
    Every row starts from zeroed registers, whatever --continuous says. free (video): every
    input after the first tick is the model's own last word (no word after its own <NUL>), as in
    the live demo;
    only the EVALF line (speech / activity loss) is written."""
    tag = tag or corpus
    t0 = time.time()
    dev = next(model.parameters()).device
    band_of = _token_bands(dev) if args.eval_bands else None
    nb = int(band_of.max()) + 1 if band_of is not None else 0
    per_doc, bad_doc, band_sum, band_cnt = [], [], [], []
    nul = dict(ce=0.0, n=0, p_tok=0.0, n_tok=0, p_nul=0.0)    # --clock_hz: the <NUL> targets
    nul3 = {k: dict(ce=0.0, n=0, p_tok=0.0, n_tok=0, p_nul=0.0) for k in (0, 1, 2)}  # by stream
    # EVALS: loss / count by tick kind (1 speech, 2 activity; --fifo3 by stream: 1 voice,
    # 2 image, 3 text)
    kce, kn = [0.0, 0.0, 0.0, 0.0], [0, 0, 0, 0]
    f3 = False                               # --fifo3 clips: three targets per tick
    with _EvalState(), torch.no_grad():
        c = 0
        gen = torch.Generator(device=dev).manual_seed(1234)
        for chunk, X, Y, M in _batches(_doc_rows(docs)):
            B, T = X.shape[:2]
            f3 = X.dim() == 3
            if f3:                           # per stream: word targets, <NUL> targets
                M3, Mn3 = M[..., None] & (Y != _NUL_ID), M[..., None] & (Y == _NUL_ID)
                n3 = torch.zeros(B, device=X.device)
                Mn = None
            # every loss below is over caption tokens only; <NUL> targets are summed apart
            Mn = M & (Y == _NUL_ID) if _NUL_ID is not None and not f3 else None
            if Mn is not None:
                M = M & ~Mn
            if not f3:
                M = M & (Y >= 0)             # --inner_voice: a silent tick (-100) has no target
            own = None                       # --inner_voice: the token sampled at the last tick
            own3 = None                      # --streams 3: each stream's sample at the last tick
            bank = _bank(imgs[c:c + B], dev) if imgs is not None else None
            cb = clips[c:c + B] if clips is not None else None
            c += B
            if cb is not None:
                see, hear = cb[0].see and model.img_width, cb[0].hear and model.aud_width
                if hear and model.audio_encoder not in _WAV_ENCODERS:
                    Tm = max(1, max(v.lat.shape[1] for v in cb))
                    lat = torch.zeros(B, _AUD_DIM, Tm, device=dev)
                    for r, v in enumerate(cb):
                        lat[r, :, :v.lat.shape[1]] = v.lat
                heard, agrid = [-1] * B, None    # quartznet: each clip's precomputed grids
                wbuf = None                      # ... or, not precomputed, the sound buffers
                if hear and model.audio_encoder in _WAV_ENCODERS and \
                        any(v._agrid is None for v in cb):
                    wbuf = torch.zeros(B, max(v.lat.shape[0] for v in cb), dtype=torch.int16,
                                       device=dev)
                    for r, v in enumerate(cb):
                        wbuf[r, :v.lat.shape[0]] = v.lat
                last = [len(v.fi) - 1 for v in cb]
                shown, grid = [-1] * B, None     # the encoder runs only when a frame changes
            Kd = None
            if cb is not None and all(getattr(v, 'kind', None) for v in cb):
                Kd = torch.zeros((B, T), dtype=torch.long, device=dev)
                for r, v in enumerate(cb):
                    Kd[r, :len(v.kind)] = torch.tensor(v.kind[:T], device=dev)
            model.dff = None
            rs = torch.zeros(B, device=dev)
            bad = torch.zeros(B, dtype=torch.bool, device=dev)
            if nb:
                bsum = torch.zeros(B, nb, device=dev)
                bcnt = torch.zeros(B, nb, device=dev)
            for t in range(T):
                img = model.image_grid(_views(*bank, gen)) if bank is not None else None
                aud = None
                if cb is not None:
                    if see:
                        fis = [v.fi[min(t, last[r])] for r, v in enumerate(cb)]
                        ch = [r for r in range(B) if fis[r] != shown[r]]
                        if ch:
                            g = model.image_grid(_norm_u8(torch.stack(
                                [cb[r].frames[fis[r]] for r in ch]).to(dev)))
                            if grid is None:
                                grid = g.new_zeros((B,) + tuple(g.shape[1:]))
                            grid[ch] = g
                            for r in ch:
                                shown[r] = fis[r]
                        img = grid
                    if hear:
                        ais = [v.ai[min(t, last[r])] for r, v in enumerate(cb)]
                        if model.audio_encoder not in _WAV_ENCODERS:
                            aud = model.audio_grid(lat, torch.tensor(ais, device=dev))
                        else:
                            ch = [r for r in range(B) if ais[r] != heard[r]]
                            if ch:
                                if wbuf is None:
                                    g = torch.cat([cb[r].aud_at(model, ais[r], dev) for r in ch])
                                else:            # a grid per tick: every changed row at once
                                    g = model.audio_grid(wbuf[ch], torch.tensor(
                                        [float(ais[r]) for r in ch], device=dev))
                                if agrid is None:
                                    agrid = g.new_zeros((B,) + tuple(g.shape[1:]))
                                agrid[ch] = g
                                for r in ch:
                                    heard[r] = ais[r]
                            aud = agrid
                xt = X[:, t]
                if f3:
                    ce, nw, cmax, own3 = _score3f_tick(
                        X[:, t], Y[:, t], cb is not None, free, own3, img, aud, M3[:, t],
                        Mn3[:, t], nul3, kce, kn, gen, (band_of, bsum, bcnt) if nb else None)
                    rs += ce
                    n3 += nw
                    bad |= cmax > _EVAL_THRESH
                    continue
                if model.streams == 3:
                    ce = _score3_tick(X[:, t], Y[:, t], Kd, t, cb is not None, free, own3,
                                      img, aud, M[:, t], Mn[:, t], nul3, gen)
                    own3 = ce[1]
                    ce = ce[0]
                elif free and own is not None:     # EVALF: every word is the model's own
                    xt = torch.where((xt >= 0) | (xt == _PAD), own, xt)
                    if _NUL_ID is not None:      # ... and after its own <NUL>, no word
                        xt = torch.where(xt == _NUL_ID, _PAD, xt)
                elif args.inner_voice and own is not None:   # after a silent tick: its own token
                    fb = xt == _PAD
                    if args.voice_drop:
                        fb &= torch.rand(xt.shape, device=dev, generator=gen) >= args.voice_drop
                    xt = torch.where(fb, own, xt)
                if model.streams == 1:
                    logits, _ = model(xt, img=img, aud=aud)
                    if args.inner_voice or free:
                        own = torch.multinomial(_truncate(F.softmax(logits.float(), dim=-1)), 1,
                                                generator=gen)[:, 0]
                    ce = F.cross_entropy(logits, Y[:, t], reduction='none')
                # a diverged row is counted as runaway rather than poisoning the sums
                ce = torch.where(torch.isfinite(ce), ce, torch.full_like(ce, 1e30))
                if Mn is not None and model.streams == 1:
                    pn = F.softmax(logits.float(), dim=-1)[:, _NUL_ID]
                    nul['ce'] += float((ce.clamp(max=30) * Mn[:, t]).sum())
                    nul['n'] += int(Mn[:, t].sum())
                    nul['p_nul'] += float((pn * Mn[:, t]).sum())
                    nul['p_tok'] += float((pn * M[:, t]).sum())
                    nul['n_tok'] += int(M[:, t].sum())
                if nb:
                    oh = F.one_hot(band_of[Y[:, t].clamp(0, band_of.numel() - 1)],
                                   nb).float() * M[:, t, None]
                    bsum += oh * ce[:, None]
                    bcnt += oh
                rs += ce * M[:, t]
                if Kd is not None:
                    for kk in (1, 2):
                        mk = M[:, t] & (Kd[:, t] == kk)
                        kce[kk] += float((ce.clamp(max=30) * mk).sum())
                        kn[kk] += int(mk.sum())
                bad |= M[:, t] & (ce > _EVAL_THRESH)     # ANY token over: tools/score.py's rule
            per_doc.append((rs / (n3 if f3 else M.sum(dim=1)).clamp(min=1)).cpu().numpy())
            bad_doc.append(bad.cpu().numpy())
            if nb:
                band_sum.append(bsum.cpu().numpy())
                band_cnt.append(bcnt.cpu().numpy())
    per, bad = np.concatenate(per_doc), np.concatenate(bad_doc)
    # word loss by kind: speech / activity lines, or (--fifo3) by stream: hear / see / think
    kinds = ((1, 'speech'), (2, 'see'), (3, 'think')) if f3 else ((1, 'speech'), (2, 'activity'))
    if free:
        f = lambda kk: f'{kce[kk] / kn[kk]:.4f}' if kn[kk] else 'n/a'
        _eval_results[f'{tag}~free'] = dict(**{lab: kce[kk] / max(1, kn[kk]) for kk, lab in kinds},
                                            median=float(np.median(per)))
        _emit(f'EVALF step {step:10} corpus {tag:8} '
              + ' '.join(f'{lab} {f(kk)}' for kk, lab in kinds)
              + f' median {float(np.median(per)):.4f} wall {time.time() - t0:5.1f}s')
        return
    clean = float(per[~bad].mean()) if (~bad).any() else float('nan')
    # nats per character over the clean documents: comparable across tokenizers
    nt = np.array([_ntok(d) for d in docs], dtype=np.float64)
    nc = np.array([max(1, sum(len(_decode_plain([y[st] for _, y in d if y[st] != _SIL]))
                              for st in range(3)) if f3 else len(_decode_plain(_doc_tokens(d))))
                   for d in docs], dtype=np.float64)
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
    if sum(kn):
        # EVALS: token-mean loss (each clamped to 30 nats) on speech words and on activity lines
        # (--fifo3: on each stream's words)
        f = lambda kk: f'{kce[kk] / kn[kk]:.4f} ({100 * kn[kk] / sum(kn):.0f}%)' if kn[kk] else 'n/a'
        _eval_results[f'{tag}~kinds'] = {lab: kce[kk] / max(1, kn[kk]) for kk, lab in kinds}
        _emit(f'EVALS step {step:10} corpus {tag:8} ' + ' '.join(f'{lab} {f(kk)}' for kk, lab in kinds))
    if f3 and nul3[1]['n']:
        # EVALN (--fifo3): as below, for all three streams (text says <NUL> between activities)
        g = lambda d, a, b: d[a] / max(1, d[b])
        sts = ((1, 'voice'), (2, 'image'), (0, 'text'))
        nn_ = sum(nul3[k]['n'] for k, _ in sts)
        _eval_results[f'{tag}~nul'] = {
            'ce': sum(nul3[k]['ce'] for k, _ in sts) / max(1, nn_),
            **{f'{lab}_{q}': g(nul3[k], 'p_' + q, 'n' if q == 'nul' else 'n_tok')
               for k, lab in sts for q in ('nul', 'tok')}}
        _emit(f'EVALN step {step:10} corpus {tag:8} nul_ce {_eval_results[f"{tag}~nul"]["ce"]:9.6f} '
              + ' '.join(f'{lab} P(nul|nul) {g(nul3[k], "p_nul", "n"):.4f} P(nul|tok) '
                         f'{g(nul3[k], "p_tok", "n_tok"):.4f}' for k, lab in sts))
    elif nul3[1]['n']:
        # EVALN (--streams 3): per stream, the mean P(<NUL>) on its <NUL> targets (want ~1) and
        # on its caption words (want ~0); nul_ce over both streams' <NUL> targets
        g = lambda d, a, b: d[a] / max(1, d[b])
        nn_ = nul3[1]['n'] + nul3[2]['n']
        _eval_results[f'{tag}~nul'] = {
            'ce': (nul3[1]['ce'] + nul3[2]['ce']) / max(1, nn_),
            **{f'{lab}_{q}': g(nul3[k], 'p_' + q, 'n' if q == 'nul' else 'n_tok')
               for k, lab in ((1, 'voice'), (2, 'image')) for q in ('nul', 'tok')}}
        _emit(f'EVALN step {step:10} corpus {tag:8} nul_ce {_eval_results[f"{tag}~nul"]["ce"]:9.6f} '
              + ' '.join(f'{lab} P(nul|nul) {g(nul3[k], "p_nul", "n"):.4f} P(nul|tok) '
                         f'{g(nul3[k], "p_tok", "n_tok"):.4f}'
                         for k, lab in ((1, 'voice'), (2, 'image'))))
    if nul['n']:
        # EVALN: the <NUL> targets' loss, and the mean P(<NUL>) the model gives on ticks whose
        # target is <NUL> (want ~1) and on ticks whose target is a caption token (want ~0)
        _eval_results[f'{tag}~nul'] = dict(ce=nul['ce'] / nul['n'], p_nul=nul['p_nul'] / nul['n'],
                                           p_tok=nul['p_tok'] / max(1, nul['n_tok']),
                                           nul_frac=nul['n'] / (nul['n'] + nul['n_tok']))
        _emit(f'EVALN step {step:10} corpus {tag:8} nul_ce {nul["ce"] / nul["n"]:9.6f} '
              f'P(nul|nul) {nul["p_nul"] / nul["n"]:.4f} P(nul|tok) '
              f'{nul["p_tok"] / max(1, nul["n_tok"]):.4f} nul {100 * nul["n"] / (nul["n"] + nul["n_tok"]):.1f}%')
    if nb and bands and (~bad).any():
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
_gen_anchor = {}             # corpus -> _gen_prompts' list
_NO_PROMPT = '\n'            # the judge's "no prompt": a bare document start


def _gen_prompts(corpus, docs):
    """EVALG's fixed prompts for a corpus, built once: (prompt ids, prompt text, the judge's
    nats on the real continuation, on it shuffled, on it without the prompt, its ids)."""
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
            u = _judge.cond_nll(_NO_PROMPT, real.lstrip())
            if a is not None and b is not None and u is not None:
                items.append((q[:1 + P], ptxt, a, b, u, q[1 + P:1 + P + C]))
            if len(items) >= args.eval_gen:
                break
        _gen_anchor[corpus] = items
    return _gen_anchor[corpus]


def _gen_eval(step, corpus, docs):
    """EVALG: continue held-out prompts; the judge scores the continuation given the prompt,
    against the document's real continuation (floor) and its words shuffled (ceiling).
    delta: the judge's nats on the continuation without the prompt minus with it -- how much
    the prompt explains the continuation, i.e. how on-topic it stayed (real_delta: the same for
    the document's own continuation)."""
    global _judge
    t0 = time.time()
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    C = args.eval_gen_len
    g_n, r_n, s_n, gd, rd, reps, d2s = [], [], [], [], [], [], []
    dev = next(model.parameters()).device
    with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
        for prompt, ptxt, a, b, u, _ in _gen_prompts(corpus, docs):
            out = model.generate(prompt, C, temperature=args.temperature)
            ctxt = _decode_plain(out)
            n = _judge.cond_nll(ptxt, ctxt) if ctxt.strip() else None
            n0 = _judge.cond_nll(_NO_PROMPT, ctxt.lstrip()) if n is not None else None
            if n0 is None:
                continue
            w = ctxt.split()
            bg = list(zip(w, w[1:]))
            g_n.append(n); r_n.append(a); s_n.append(b); gd.append(n0 - n); rd.append(u - a)
            reps.append(_rep1(ctxt)); d2s.append(len(set(bg)) / len(bg) if bg else 0.0)
    if not g_n:
        return
    g, r, s = float(np.mean(g_n)), float(np.mean(r_n)), float(np.mean(s_n))
    flu = 100.0 * (s - g) / (s - r) if s > r else float('nan')
    d, dr = float(np.mean(gd)), float(np.mean(rd))
    _eval_results[f'{corpus}~gen'] = dict(nats=g, real=r, shuf=s, fluency=flu, delta=d,
                                          real_delta=dr, rep1=float(np.mean(reps)),
                                          distinct2=float(np.mean(d2s)))
    _emit(f'EVALG step {step:10} corpus {corpus:8} prompts {len(g_n)} nats {g:.4f} '
          f'real {r:.4f} shuf {s:.4f} fluency {flu:.1f}% delta {d:+.4f} real_delta {dr:+.4f} '
          f'rep1 {np.mean(reps):.3f} distinct2 {np.mean(d2s):.3f} wall {time.time() - t0:.1f}s')


def _hold_eval(step):
    """EVALH: does the model hold a topic it chose itself? N samples of 2C tokens from <NUL>
    (seed k for sample k, so evals are paired), split into halves A, B. The judge's nats on B:
      self   = nats(B | no prompt) - nats(B | A)       its own topic, carried in its state
      cross  = nats(B | no prompt) - nats(B | A of the next sample)   generic priming only
      own    = the same as self for B', a fresh state's continuation of A fed back as a prompt
               (its own text re-read; compare EVALG delta, a human prompt re-read)
    self - cross is the topic-specific part; rep1 of B guards against a loop scoring high."""
    global _judge
    t0 = time.time()
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    C, N = args.eval_gen_len, args.eval_hold
    dev = next(model.parameters()).device
    halves = []
    with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
        for k in range(N):
            torch.manual_seed(k)
            out = model.generate(_prompt_ids(), 2 * C, temperature=args.temperature)
            if len(out) < 2 * C:
                continue
            a = out[:C]
            torch.manual_seed(k)
            b2 = model.generate(_prompt_ids() + a, C, temperature=args.temperature)
            halves.append((_decode_plain(a), _decode_plain(out[C:]), _decode_plain(b2)))
    sd, xd, od, reps = [], [], [], []
    for k, (a, b, b2) in enumerate(halves):
        ax = halves[(k + 1) % len(halves)][0]
        if not (a.strip() and b.strip() and b2.strip() and ax.strip()):
            continue
        n0, n1, nx = (_judge.cond_nll(_NO_PROMPT, b.lstrip()), _judge.cond_nll(a, b),
                      _judge.cond_nll(ax, b))
        m0, m1 = _judge.cond_nll(_NO_PROMPT, b2.lstrip()), _judge.cond_nll(a, b2)
        if None in (n0, n1, nx, m0, m1):
            continue
        sd.append(n0 - n1); xd.append(n0 - nx); od.append(m0 - m1); reps.append(_rep1(b))
    if not sd:
        return
    s, x, o = float(np.mean(sd)), float(np.mean(xd)), float(np.mean(od))
    _eval_results['hold'] = dict(self=s, cross=x, own=o, topic=s - x, rep1=float(np.mean(reps)),
                                 samples=len(sd))
    _emit(f'EVALH step {step:10} samples {len(sd)} self {s:+.4f} cross {x:+.4f} topic {s - x:+.4f} '
          f'own {o:+.4f} rep1 {np.mean(reps):.3f} wall {time.time() - t0:.1f}s')


_RECENT_BANDS = (0, 2000, 10000, 50000, 200000, 1000000)   # EVALR age bands, lower edges
_DOC_BRIEF = 10000           # the others stay in memory while younger than this (steps)
_doc_records = None          # [(start step, end step, ids, kept)]; --doc_log_file, read once


def _doc_file():
    return args.doc_log_file or args.log + '.docs'


def _load_doc_records():
    global _doc_records
    if _doc_records is None:
        _doc_records = []
        if os.path.exists(_doc_file()):
            with open(_doc_file()) as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    _doc_records.append((r['step'], r['end'], np.array(r['ids'], dtype=np.int32),
                                         True))
    return _doc_records


def _recent_eval(step, corpus, docs):
    """EVALR: training documents by how long ago they were read (age = step - the step the
    record ended), against held-out ones cut the same way. Per band: ce, the model's nats per
    token over the record; cont, over the tokens after the --eval_gen_prompt prefix; gain,
    held-out minus band (how much better it knows what it read); delta, EVALG's delta when
    continuing that prefix; ovl, the share of the continuation's word bigrams in the real one."""
    global _judge
    t0 = time.time()
    _load_doc_records()
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    P, C, K, T = args.eval_gen_prompt, args.eval_gen_len, args.eval_recent, args.doc_log_len
    need = 1 + P + C
    rng = random.Random(step)
    groups = []
    for b, lo in enumerate(_RECENT_BANDS):
        hi = _RECENT_BANDS[b + 1] if b + 1 < len(_RECENT_BANDS) else float('inf')
        pool = [q for s0, e, q, _ in _doc_records
                if lo <= step - e < hi and e <= step and len(q) >= need]
        if pool:
            groups.append((f'{lo // 1000}K+' if lo else '0+',
                           [q.tolist() for q in rng.sample(pool, min(K, len(pool)))]))
    held = [q[:T] for q in (_doc_tokens(d) for d in docs) if len(q) >= need][:K]
    groups.append(('heldout', held))
    rows = [(q[:-1], q[1:]) for _, g in groups for q in g]
    if not rows or not groups[:-1]:
        return
    ce = iter(_ce_pairs(rows))
    res = []
    dev = next(model.parameters()).device
    for name, g in groups:
        cs, cc, dl, ov = [], [], [], []
        for q in g:
            c = next(ce)
            cs.append(float(c.mean())); cc.append(float(c[P:].mean()))
        with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
            torch.manual_seed(step)
            for q in g:
                ptxt, real = _decode_plain(q[:1 + P]), _decode_plain(q[1 + P:1 + P + C])
                gen = _decode_plain(model.generate(q[:1 + P], C, temperature=args.temperature))
                n = _judge.cond_nll(ptxt, gen) if gen.strip() else None
                n0 = _judge.cond_nll(_NO_PROMPT, gen.lstrip()) if n is not None else None
                if n0 is None:
                    continue
                dl.append(n0 - n)
                w, rw = gen.split(), real.split()
                bg, rb = list(zip(w, w[1:])), set(zip(rw, rw[1:]))
                ov.append(sum(x in rb for x in bg) / len(bg) if bg else 0.0)
        res.append((name, len(g), np.mean(cs), np.mean(cc), np.mean(dl) if dl else float('nan'),
                    np.mean(ov) if ov else float('nan')))
    h = res[-1]
    _eval_results['recent'] = {r[0]: dict(n=r[1], ce=r[2], cont=r[3], delta=r[4], ovl=r[5])
                               for r in res}
    _emit(f'EVALR step {step:10} corpus {corpus:8} records {len(_doc_records)} | ' +
          ' | '.join(f'{r[0]} n{r[1]} ce {r[2]:.3f} cont {r[3]:.3f} gain {h[3] - r[3]:+.3f} '
                     f'delta {r[4]:+.3f} ovl {r[5]:.3f}' for r in res) +
          f' | wall {time.time() - t0:.1f}s')


_CLOZE_SRC = ('juletxara/xstory_cloze', 'en', 'eval')
_cloze_set = []              # [(story token ids, right ending ids, wrong ending ids)]


def _cloze_eval(step):
    """EVALC: Story Cloze. Each story's four sentences, then each of its two endings, from a
    fresh state; acc: the right ending has the lower summed nats (lm-eval's acc), acc_tok: the
    lower nats per token (length-normalized). margin: wrong minus right, nats per token."""
    t0 = time.time()
    if not _cloze_set:
        from datasets import load_dataset
        rows = load_dataset(*_CLOZE_SRC[:2], split=_CLOZE_SRC[2])
        for ex in rows.select(range(min(args.eval_cloze, len(rows)))):
            story = ' '.join(ex[f'input_sentence_{k}'] for k in range(1, 5))
            ends = [ex['sentence_quiz1'], ex['sentence_quiz2']]
            r = int(ex['answer_right_ending']) - 1
            _cloze_set.append((_prompt_ids(story), _tokenizer.encode(' ' + ends[r]),
                               _tokenizer.encode(' ' + ends[1 - r])))
        print(f'--eval_cloze: {len(_cloze_set)} stories from {"/".join(_CLOZE_SRC)}', flush=True)
    rows = [(s + e[:-1], s[1:] + e) for s, R, W in _cloze_set for e in (R, W)]
    ce = _ce_pairs(rows)
    right, tok, marg = [], [], []
    for k, (s, R, W) in enumerate(_cloze_set):
        a, b = ce[2 * k][len(s) - 1:], ce[2 * k + 1][len(s) - 1:]
        right.append(a.sum() < b.sum())
        tok.append(a.mean() < b.mean())
        marg.append(b.mean() - a.mean())
    acc, acc_t, m = 100.0 * np.mean(right), 100.0 * np.mean(tok), float(np.mean(marg))
    _eval_results['cloze'] = dict(acc=acc, acc_tok=acc_t, margin=m, stories=len(_cloze_set))
    _emit(f'EVALC step {step:10} stories {len(_cloze_set)} acc {acc:.1f}% acc_tok {acc_t:.1f}% '
          f'margin {m:+.4f} wall {time.time() - t0:.1f}s')


_pair_sets = {}              # name -> [(ids a, ids b, group)], a the acceptable one


def _sentence(t):
    """A ComVE statement in one form: stripped, capitalized, closed by one period (its pairs
    differ in final punctuation about a third of the time, which would score as sense)."""
    t = t.strip().rstrip('.').strip()
    return t[:1].upper() + t[1:] + '.'


def _load_pairs():
    from datasets import get_dataset_config_names, load_dataset
    N = args.eval_pairs
    bl = []
    cfgs = get_dataset_config_names('nyu-mll/blimp')
    for c in cfgs:
        for ex in load_dataset('nyu-mll/blimp', c, split='train').select(range(-(-N // len(cfgs)))):
            bl.append((_prompt_ids(ex['sentence_good']), _prompt_ids(ex['sentence_bad']), ex['field']))
    cv = []
    for ex in load_dataset('tasksource/ComVE', split='test').select(range(min(N, 999))):
        ch = [_sentence(t) for t in ex['choices_list']]
        cv.append((_prompt_ids(ch[ex['labels']]), _prompt_ids(ch[1 - ex['labels']]), 'comve'))
    _pair_sets.update(blimp=bl, comve=cv)
    print(f'--eval_pairs: BLiMP {len(bl)}, ComVE {len(cv)} pairs', flush=True)


_qa_rows = []                # EVALQ: (open inputs, targets, answer mask), then the closed-book row
_QA_MAXLEN = 1024            # EVALQ: tokens per row; a pair that would not fit is left out


def _qa_tokens(page, pairs):
    """[_NULL] + page + its pairs as one row of (inputs, targets, mask over answer targets);
    page None: the pairs alone (closed book)."""
    ids, mask = [_NULL], [0]
    if page is not None:
        ids += _tokenizer.encode(page)
        mask += [0] * (len(ids) - 1)
    for k, (q, a) in enumerate(pairs):
        head = _tokenizer.encode(('' if page is None and k == 0 else '\n\n') + f'Q: {q}\nA:')
        ans = _tokenizer.encode(' ' + a)
        if len(ids) + len(head) + len(ans) > _QA_MAXLEN:
            break
        ids += head + ans
        mask += [0] * len(head) + [1] * len(ans)
    return ids[:-1], ids[1:], mask[1:]


def _load_qa():
    """The first --eval_qa held-out qaipt pages (with at least one pair that fits)."""
    import pyarrow.parquet as pq
    for f in _local_files('qaipt'):
        for text in pq.read_table(f, columns=['text']).column(0).to_pylist():
            if not _is_heldout(text):
                continue
            page, sep, rest = text.partition('\n\nQ: ')
            pairs = [tuple(x.split('\nA: ', 1)) for x in rest.split('\n\nQ: ')] if sep else []
            pairs = [qa for qa in pairs if len(qa) == 2]
            o, c = _qa_tokens(page, pairs), _qa_tokens(None, pairs)
            if sum(o[2]) and sum(c[2]) and sum(o[2]) == sum(c[2]):
                _qa_rows.append((o, c))
            if len(_qa_rows) >= args.eval_qa:
                break
        if len(_qa_rows) >= args.eval_qa:
            break
    print(f'--eval_qa: {len(_qa_rows)} held-out qaipt pages, '
          f'{sum(sum(o[2]) for o, _ in _qa_rows)} answer tokens', flush=True)


def _qa_eval(step):
    """EVALQ: answer tokens of held-out Q/A pages, open book and closed book (see --eval_qa)."""
    t0 = time.time()
    if not _qa_rows:
        _load_qa()
    ce = _ce_pairs([(x, y) for o, c in _qa_rows for x, y, _ in (o, c)])
    res = {}
    for j, name in enumerate(('open', 'closed')):
        v = np.concatenate([ce[2 * k + j][np.array(r[j][2], dtype=bool)] for k, r in enumerate(_qa_rows)])
        res[name] = float(v.mean())
    res['gain'] = res['closed'] - res['open']
    _eval_results['qa'] = res
    _emit(f'EVALQ step {step:10} pages {len(_qa_rows)} | answer nats open {res["open"]:.4f} '
          f'closed {res["closed"]:.4f} gain {res["gain"]:+.4f} | wall {time.time() - t0:.1f}s')


def _pairs_eval(step):
    """EVALM: minimal pairs from a zero state, the model's own regime: the only context is the
    sentence itself. acc: the acceptable one has the lower summed nats; acc_tok: per token;
    margin: unacceptable minus acceptable, nats per token. BLiMP is also split by field."""
    t0 = time.time()
    if not _pair_sets:
        _load_pairs()
    out, res = [], {}
    for name, pairs in _pair_sets.items():
        rows = [(q[:-1], q[1:]) for a, b, _ in pairs for q in (a, b)]
        ce = _ce_pairs(rows)
        right, tok, marg, grp = [], [], [], collections.defaultdict(list)
        for k, (a, b, g) in enumerate(pairs):
            ca, cb = ce[2 * k], ce[2 * k + 1]
            right.append(ca.sum() < cb.sum())
            tok.append(ca.mean() < cb.mean())
            marg.append(cb.mean() - ca.mean())
            grp[g].append(right[-1])
        res[name] = dict(n=len(pairs), acc=100.0 * np.mean(right), acc_tok=100.0 * np.mean(tok),
                         margin=float(np.mean(marg)))
        out.append(f'{name} n{len(pairs)} acc {res[name]["acc"]:.1f}% acc_tok '
                   f'{res[name]["acc_tok"]:.1f}% margin {res[name]["margin"]:+.4f}')
        if name == 'blimp':
            out[-1] += ' (' + ' '.join(f'{g} {100.0 * np.mean(v):.1f}'
                                       for g, v in sorted(grp.items())) + ')'
    _eval_results['pairs'] = res
    _emit(f'EVALM step {step:10} ' + ' | '.join(out) + f' | wall {time.time() - t0:.1f}s')


_WP_SRC = ('euclaise/writingprompts', 'test')
_wp_prompts = []             # fixed prompt texts, the same at every eval


def _wp_clean(t):
    """A WritingPrompts prompt, its tag and the dataset's tokenized spacing undone."""
    t = re.sub(r'^\s*\[\s*\w+\s*\]\s*', '', t).replace('``', '"').replace("''", '"')
    t = re.sub(r' ([.,!?;:%)\]])', r'\1', t)
    t = re.sub(r" (n't|'s|'re|'ve|'ll|'d|'m)\b", r'\1', t)
    return re.sub(r'([(\[]) ', r'\1', t).strip()


def _wp_samples(step):
    """GENW: the --eval_wp fixed WritingPrompts prompts, each continued for --eval_wp_len
    tokens, one log line each, for reading across evals."""
    if not _wp_prompts:
        from datasets import load_dataset
        for ex in load_dataset(*_WP_SRC[:1], split=_WP_SRC[1], streaming=True):
            p = _wp_clean(ex['prompt'])
            if 40 <= len(p) <= 300:
                _wp_prompts.append(p)
            if len(_wp_prompts) >= args.eval_wp:
                break
    dev = next(model.parameters()).device
    with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
        torch.manual_seed(step)
        for k, p in enumerate(_wp_prompts):
            prompt = _prompt_ids(p + '\n')
            out = model.generate(prompt, args.eval_wp_len, temperature=args.temperature)
            # the prompt in bold (ANSI, for a terminal) and closed by ‖, so the continuation's
            # start shows in any viewer
            _emit(f'GENW step {step:10} [{k}]: \033[1m{_render(prompt)}\033[0m ‖ {_render(out)}')


_VIDEO_VARIANTS = ((True, True, ''), (False, True, '-blind'), (True, False, '-deaf'),
                   (False, False, '-off'))


def _heldout_eval(step):
    """Every eval corpus: EVAL/EVALB, then for text corpora EVALX, EVALG and EVALI (first
    text corpus only). An image corpus is scored with its images and again blind (image grid
    zeroed); the gap is what the model takes from the image. Failures are reported and
    never take the training run down."""
    text = [c for c in _eval_corpus_names() if c not in _MEDIA_DATASETS]
    # --eval_rare: the slow / low-value evals only at every Nth eval (all of them under --eval)
    rare = args.eval or not args.eval_rare or not args.eval_interval or \
        (step // args.eval_interval) % args.eval_rare == 0
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
            if corpus in _VIDEO_DATASETS:
                # with picture and sound, then each sense removed, then both: the gaps are what
                # the model takes from each
                # --streams 3: no blind passes (without a picture the input looks like a text
                # row and both caption streams say <NUL> -- they measured nothing)
                variants = [v for v in _VIDEO_VARIANTS if v[0] or v[1] is False or
                            model.streams != 3]
                for see, hear, sfx in variants:
                    if (see or hear) or rare:
                        _score(step, corpus, docs, tag=corpus + sfx, bands=rare,
                               clips=[v.variant(see, hear) for v in _eval_vids[corpus]])
                if args.inner_voice or _NUL_ID is not None:   # EVALF: every word its own
                    for see, hear, sfx in variants:
                        if see or hear:
                            _score(step, corpus, docs, tag=corpus + sfx, free=True,
                                   clips=[v.variant(see, hear) for v in _eval_vids[corpus]])
                continue
            _score(step, corpus, docs)
        except Exception as e:
            print(f'WARNING: eval failed at step {step} on "{corpus}": {e!r}; disabling it',
                  flush=True)
            _eval_failed[corpus] = True
            continue
        for fn, on in ((_reach_eval, args.eval_reach and rare), (_gen_eval, args.eval_gen),
                       (_recent_eval, args.eval_recent and corpus == text[0]),
                       (_info_eval, args.eval_info and rare and corpus == text[0])):
            if on:
                try:
                    fn(step, corpus, docs)
                except Exception as e:
                    print(f'WARNING: {fn.__name__} failed at step {step} on "{corpus}": {e!r}',
                          flush=True)
    for fn, on in ((_cloze_eval, args.eval_cloze), (_pairs_eval, args.eval_pairs), (_qa_eval, args.eval_qa),  # corpus-free
                   (_hold_eval, args.eval_hold), (_free_eval, args.eval_free and rare),
                   (_wp_samples, args.eval_wp)):
        if on and not _eval_failed.get(fn.__name__):
            try:
                fn(step)
            except Exception as e:
                print(f'WARNING: {fn.__name__} failed at step {step}: {e!r}; disabling it',
                      flush=True)
                _eval_failed[fn.__name__] = True


_free_anchor = []            # [real nats, shuffled nats, pairs] on held-out chunk pairs, built once


def _free_anchors(C):
    """--free_run / EVALL fluency anchors: the judge's nats on a held-out chunk of C tokens
    after the chunk before it (real, 100%), and on it with its words shuffled (0%)."""
    global _judge
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    if not _free_anchor:
        rng, real, shuf = random.Random(1234), [], []
        for d in _eval_docs(_eval_corpus_names()[0]):
            q = _doc_tokens(d)
            if len(q) < 1 + 2 * C:
                continue
            p, c = _decode_plain(q[1:1 + C]), _decode_plain(q[1 + C:1 + 2 * C])
            sw = c.split()
            rng.shuffle(sw)
            a, b = _judge.cond_nll(p, c), _judge.cond_nll(p, ' ' + ' '.join(sw))
            if a is not None and b is not None:
                real.append(a); shuf.append(b)
        _free_anchor[:] = [float(np.mean(real)), float(np.mean(shuf)), len(real)]
    return _free_anchor


def _free_streams(R, N, W, C):
    """R streams from one zero state, never reset, for N tokens. Every chunk of C words
    (<NUL> dropped) is judged after the chunk before it: nats, fluency between _free_anchors'
    real (100%) and shuffled (0%), and coh = nats without the previous chunk minus with it
    (does it still follow itself?). -> (one dict per W-token window: those, rep1 / distinct2
    of the window's text, the <NUL> share, each register's RMS (does the state settle, grow
    or die?); each stream's tokens, <NUL> included)."""
    fr, fs, _ = _free_anchors(C)
    dev = next(model.parameters()).device
    model.eval()
    dff = model.new_state(R, dev)
    x = torch.full((R,), _NULL, dtype=torch.long, device=dev)
    toks = [[] for _ in range(R)]           # every sample, <NUL> included
    words = [[] for _ in range(R)]          # <NUL> dropped
    done = [0] * R                          # words already judged (whole chunks)
    prev = [None] * R                       # the last judged chunk's text
    win, out = dict(n=[], n0=[], rms=[]), []
    with torch.no_grad():
        for t in range(N):
            dff, o = model.step(x, dff)
            logits = model.text_dec(o)
            if not (dff.isfinite().all() and logits.isfinite().all()):
                print(f'FREE step {t}: NaN/Inf in the state or logits -- stopping', flush=True)
                break
            prob = F.softmax(logits.float() / max(args.temperature, 1e-6), dim=-1)
            b = torch.multinomial(_truncate(prob), 1)[:, 0]
            x = torch.where(b == _NUL_ID, torch.full_like(b, _PAD), b) if _NUL_ID is not None else b
            win['rms'].append(_reg_rms(dff).mean(0).cpu())
            for r, v in enumerate(b.tolist()):
                toks[r].append(v)
                if v != _NUL_ID:
                    words[r].append(v)
            for r in range(R):              # judge each finished chunk after the one before
                while len(words[r]) - done[r] >= C:
                    txt = _decode_plain(words[r][done[r]:done[r] + C])
                    done[r] += C
                    if prev[r] is not None and txt.strip():
                        n1 = _judge.cond_nll(prev[r], txt)
                        n0 = _judge.cond_nll(_NO_PROMPT, txt.lstrip())
                        if n1 is not None and n0 is not None:
                            win['n'].append(n1); win['n0'].append(n0)
                    prev[r] = txt
            if (t + 1) % W == 0 or t + 1 == N:
                lo = t + 1 - len(win['rms'])
                reps, d2s, nul = [], [], []
                for r in range(R):
                    seg = toks[r][lo:t + 1]
                    nul.append(sum(v == _NUL_ID for v in seg) / len(seg))
                    txt = _decode_plain(seg)
                    if txt.split():
                        w = txt.split()
                        bg = list(zip(w, w[1:]))
                        reps.append(_rep1(txt)); d2s.append(len(set(bg)) / len(bg) if bg else 0.0)
                g = float(np.mean(win['n'])) if win['n'] else float('nan')
                out.append(dict(lo=lo, hi=t + 1, chunks=len(win['n']), nats=g,
                                fluency=100.0 * (fs - g) / (fs - fr) if fs > fr else float('nan'),
                                coh=float(np.mean(np.array(win['n0']) - np.array(win['n'])))
                                if win['n'] else float('nan'),
                                rep1=float(np.mean(reps)) if reps else float('nan'),
                                distinct2=float(np.mean(d2s)) if d2s else float('nan'),
                                nul=100.0 * float(np.mean(nul)),
                                rms=torch.stack(win['rms']).mean(0).tolist()))
                win = dict(n=[], n0=[], rms=[])
                yield out[-1], toks


def _free_run():
    """--free_run: _free_streams over --free_rows streams of N tokens, a FREE line per window."""
    R, N, W, C = args.free_rows, args.free_run, args.free_window, args.free_chunk
    fr, fs, na = _free_anchors(C)
    print(f'FREE anchors: {na} held-out chunk pairs, real {fr:.4f} shuffled {fs:.4f} '
          f'nats/token; {R} streams x {N} tokens, window {W}, chunk {C}', flush=True)
    t0, toks = time.time(), None
    for w, toks in _free_streams(R, N, W, C):
        js = (f'chunks {w["chunks"]:4d} nats {w["nats"]:.4f} fluency {w["fluency"]:5.1f}% '
              f'coh {w["coh"]:+.4f}') if w['chunks'] else 'chunks    0' + ' ' * 37
        print(f'FREE tokens {w["lo"]:8d}-{w["hi"]:<8d} {js} rep1 {w["rep1"]:.3f} distinct2 '
              f'{w["distinct2"]:.3f} nul {w["nul"]:4.1f}% rms '
              f'{"/".join(f"{v:.4f}" for v in w["rms"])} wall {time.time() - t0:.0f}s', flush=True)
    if args.free_save and toks:
        with open(args.free_save, 'w') as f:
            for r in range(R):
                print(f'===== stream {r} ({len(toks[r])} tokens) =====\n{_decode_plain(toks[r])}\n',
                      file=f)
        print(f'FREE: text saved to {args.free_save}')


def _free_eval(step):
    """EVALL: --free_run in short, during training: --free_rows streams of --eval_free tokens
    from one zero state, never reset (the same seed every eval, so evals are paired). Per
    --free_window window, fluency (each chunk judged after the one before; real held-out
    text 100%, shuffled 0%); drift = last window minus first; and over the run coh, rep1,
    the <NUL> share and the slowest register's RMS in the last window."""
    t0 = time.time()
    dev = next(model.parameters()).device
    with _EvalState(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
        torch.manual_seed(1234)
        ws = [w for w, _ in _free_streams(args.free_rows, args.eval_free, args.free_window,
                                          args.free_chunk)]
    ws = [w for w in ws if w['chunks']]
    if not ws:
        return
    fl = [w['fluency'] for w in ws]
    _eval_results['free'] = dict(fluency=fl, drift=fl[-1] - fl[0],
                                 coh=float(np.mean([w['coh'] for w in ws])),
                                 rep1=float(np.mean([w['rep1'] for w in ws])))
    _emit(f'EVALL step {step:10} streams {args.free_rows} tokens {args.eval_free} | fluency '
          f'{"/".join(f"{v:.1f}" for v in fl)} drift {fl[-1] - fl[0]:+.1f} | coh '
          f'{_eval_results["free"]["coh"]:+.4f} rep1 {_eval_results["free"]["rep1"]:.3f} nul '
          f'{np.mean([w["nul"] for w in ws]):.1f}% rms1 {ws[-1]["rms"][0]:.4f} '
          f'wall {time.time() - t0:.0f}s')


def _prompt_tune():
    """--prompt_tune: the EVALG prompts, continued from four kinds of start, all scored alike.
      none   zero state, no prompt (what the continuation costs the model unprompted)
      cold   zero state, read the prompt (EVALG)
      warm   free-run --prompt_warm tokens from zero, then read the prompt
      tune   the initial registers h0 optimized by Adam, BPTT through the prompt, so the model
             predicts the prompt from h0 (weights frozen); then read the prompt from h0. One
             variant per --prompt_tune_cap: each register's RMS held to at most cap x its level
             after reading the prompts cold (0 = no cap)
    Per method: pnll, the model's nats/token on the prompt; cont, on the real continuation
    after it (teacher-forced); then a sampled continuation judged as in EVALG (fluency, delta =
    the judge's nats without the prompt minus with it) and its rep1. rms: the start state's
    per-register RMS."""
    global _judge
    dev = next(model.parameters()).device
    if _judge is None:
        _judge = _Judge(args.eval_gen_judge)
    corpus = _eval_corpus_names()[0]
    items = _gen_prompts(corpus, _eval_docs(corpus))
    C, B = args.eval_gen_len, args.prompt_tune_batch
    caps = [float(c) for c in args.prompt_tune_cap.split(',')]
    model.eval()
    for q in model.parameters():
        q.requires_grad_(False)

    def run(h, ids):
        """Teacher-force ids [b, T] from state h: (nats [b, T-1], end state, last logits)."""
        ce = []
        for t in range(ids.shape[1]):
            h, o = model.step(ids[:, t], h)
            logits = model.text_dec(o).float()
            if t + 1 < ids.shape[1]:
                ce.append(F.cross_entropy(logits, ids[:, t + 1], reduction='none'))
        return (torch.stack(ce, 1) if ce else None), h, logits

    def sample(h, logits, n):
        out = []
        for _ in range(n):
            prob = F.softmax(logits / max(args.temperature, 1e-6), dim=-1)
            b = torch.multinomial(_truncate(prob), 1)[:, 0]
            out.append(b)
            x = torch.where(b == _NUL_ID, torch.full_like(b, _PAD), b) if _NUL_ID is not None else b
            h, o = model.step(x, h)
            logits = model.text_dec(o).float()
        return torch.stack(out, 1).tolist(), h

    methods = ['none', 'cold', f'warm{args.prompt_warm}'] + \
        [f'tune{args.prompt_tune}_cap{c:g}' for c in caps]
    res = {m: dict(pnll=[], cont=[], gen=[], rms=[]) for m in methods}
    nat = None
    t0 = time.time()
    for c0 in range(0, len(items), B):
        chunk = items[c0:c0 + B]
        b = len(chunk)
        P = torch.tensor([it[0] for it in chunk], device=dev)                 # [b, 1+P]
        R = torch.tensor([it[5] for it in chunk], device=dev)                 # [b, C]
        zero = model.new_state(b, dev)

        def score(m, h0, read_prompt=True):
            with torch.no_grad():
                if read_prompt:
                    ce, h, lg = run(h0, torch.cat([P, R], 1))
                    res[m]['pnll'] += ce[:, :P.shape[1] - 1].mean(1).tolist()
                    res[m]['cont'] += ce[:, P.shape[1] - 1:].mean(1).tolist()
                    _, h, lg = run(h0, P)
                else:
                    ce, _, _ = run(h0, torch.cat([P[:, :1], R], 1))
                    res[m]['cont'] += ce.mean(1).tolist()
                    _, h, lg = run(h0, P[:, :1])
                res[m]['rms'].append(_reg_rms(h0).cpu())
                with torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
                    torch.manual_seed(1234 + c0)
                    res[m]['gen'] += sample(h, lg, C)[0]
            return h

        score('none', zero, read_prompt=False)
        h_cold = score('cold', zero)
        nat_c = _reg_rms(h_cold).mean(0)
        nat = nat_c if nat is None else nat + nat_c
        with torch.no_grad(), torch.random.fork_rng(devices=[dev] if dev.type == 'cuda' else []):
            torch.manual_seed(4321 + c0)
            h = zero
            x = torch.full((b,), _NULL, dtype=torch.long, device=dev)
            lg = None
            for _ in range(args.prompt_warm):
                h, o = model.step(x, h)
                lg = model.text_dec(o).float()
                s_ = torch.multinomial(_truncate(F.softmax(lg / max(args.temperature, 1e-6), -1)), 1)[:, 0]
                x = torch.where(s_ == _NUL_ID, torch.full_like(s_, _PAD), s_) if _NUL_ID is not None else s_
        score(methods[2], h)
        for cap, m in zip(caps, methods[3:]):
            h0, log = _tune_state(P, args.prompt_tune, cap, nat_c)
            print(f'TUNE prompts {c0}-{c0 + b - 1} {m} prompt nats by iter {log} '
                  f'wall {time.time() - t0:.0f}s', flush=True)
            score(m, h0)
    nat = (nat / -(-len(items) // B)).tolist()
    texts = {}
    for m in methods:
        g_n, gd, reps = [], [], []
        texts[m] = []
        for (prompt, ptxt, a, b_, u, _), out in zip(items, res[m]['gen']):
            ctxt = _decode_plain(out)
            texts[m].append(ctxt)
            n = _judge.cond_nll(ptxt, ctxt) if ctxt.strip() else None
            n0 = _judge.cond_nll(_NO_PROMPT, ctxt.lstrip()) if n is not None else None
            if n0 is None:
                continue
            g_n.append(n); gd.append(n0 - n); reps.append(_rep1(ctxt))
        r_, s_ = np.mean([it[2] for it in items]), np.mean([it[3] for it in items])
        g = float(np.mean(g_n))
        rr = torch.cat(res[m]['rms']).mean(0).tolist()
        pn = f'{np.mean(res[m]["pnll"]):.4f}' if res[m]['pnll'] else '     -'
        print(f'TUNE {m:16} prompts {len(g_n)} pnll {pn} cont {np.mean(res[m]["cont"]):.4f} | '
              f'judge {g:.4f} fluency {100.0 * (s_ - g) / (s_ - r_):5.1f}% delta {np.mean(gd):+.4f} '
              f'rep1 {np.mean(reps):.3f} | rms {"/".join(f"{v:.4f}" for v in rr)}', flush=True)
    print(f'TUNE natural register RMS after a cold prompt: {"/".join(f"{v:.4f}" for v in nat)}; '
          f'real-continuation delta {np.mean([it[4] - it[2] for it in items]):+.4f}; '
          f'wall {time.time() - t0:.0f}s', flush=True)
    if args.prompt_tune_save:
        with open(args.prompt_tune_save, 'w') as f:
            for k, it in enumerate(items):
                print(f'===== prompt {k} =====\n{it[1]}\n----- real -----\n{_decode_plain(it[5])}', file=f)
                for m in methods:
                    print(f'----- {m} -----\n{texts[m][k]}', file=f)
                print(file=f)
        print(f'TUNE: texts saved to {args.prompt_tune_save}')


if args.free_run:
    _free_run()
    raise SystemExit(0)

if args.doc_score:
    _recs = _load_doc_records()
    _held = [q[:args.doc_log_len] for q in (_doc_tokens(d) for d in _eval_docs(_eval_corpus_names()[0]))
             if len(q) >= 2]
    _rows = [(list(q[:-1]), list(q[1:])) for _, _, q, _ in _recs] + [(q[:-1], q[1:]) for q in _held]
    if args.doc_ablate:
        # the mean register state over the held-out documents, every position and token
        _dev = next(model.parameters()).device
        _sum, _n = 0.0, 0
        with _EvalState(), torch.no_grad():
            for _c, _X, _Y, _M in _batches([(q[:-1], q[1:]) for q in _held]):
                model.dff = None
                for _t in range(_X.shape[1]):
                    model(_X[:, _t])
                    _m = _M[:, _t].bool()
                    if _m.any():
                        _sum = _sum + model.dff[_m].double().sum(0, keepdim=True)
                        _n += int(_m.sum())
        model._read_mean = (_sum / _n).float().to(_dev)
        model._ablate = {int(k) - 1 for k in args.doc_ablate.split(',')}
        print(f'--doc_ablate: registers {args.doc_ablate} read as their mean state', flush=True)
    _ce = _ce_pairs(_rows)
    with open(args.doc_score, 'w') as f:
        for k, c in enumerate(_ce):
            r = dict(kind='train', start=int(_recs[k][0]), end=int(_recs[k][1])) if k < len(_recs) \
                else dict(kind='heldout', idx=k - len(_recs))
            r.update(n=len(c), nats=float(c.mean()), step=_start_step, ablate=args.doc_ablate)
            if args.doc_tokens:
                r['ce'] = [round(float(x), 4) for x in c]
            print(json.dumps(r), file=f)
    print(f'--doc_score: {len(_recs)} training records, {len(_held)} held-out documents at step '
          f'{_start_step} -> {args.doc_score}')
    raise SystemExit(0)

if args.prompt_tune:
    _prompt_tune()
    raise SystemExit(0)

def _teach_pages(n):
    """The held-out qaipt pages after the first --teach_skip, as (page, [(q, a)])."""
    import pyarrow.parquet as pq
    out, seen = [], 0
    for f in _local_files('qaipt'):
        for text in pq.read_table(f, columns=['text']).column(0).to_pylist():
            if not _is_heldout(text):
                continue
            seen += 1
            if seen <= args.teach_skip:
                continue
            page, sep, rest = text.partition('\n\nQ: ')
            pairs = [tuple(x.split('\nA: ', 1)) for x in rest.split('\n\nQ: ')] if sep else []
            pairs = [qa for qa in pairs if len(qa) == 2 and qa[0].strip() and qa[1].strip()]
            if pairs and len(_tokenizer.encode(page)) < _QA_MAXLEN - 64:
                out.append((page, pairs))
            if len(out) >= n:
                return out
    return out


class _Teacher:
    """--teach_ask model: an instruction-tuned LM answers a question from the page, in a few words."""

    def __init__(self, name):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(name)
        self.lm = AutoModelForCausalLM.from_pretrained(name, dtype=torch.bfloat16).to(args.device).eval()

    @torch.no_grad()
    def answer(self, page, q):
        msgs = [{'role': 'system', 'content': 'Answer the question from the text. Reply with only the answer, '
                                              'a few words, not a sentence.'},
                {'role': 'user', 'content': f'Text:\n{page[:4000]}\n\nQuestion: {q}'}]
        prompt = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        enc = self.tok(prompt, return_tensors='pt').to(args.device)
        out = self.lm.generate(**enc, max_new_tokens=24, do_sample=False)
        return self.tok.decode(out[0, enc['input_ids'].shape[1]:], skip_special_tokens=True).strip().split('\n')[0]


def _closed_ce(qas):
    """Mean nats per answer token of each (q, a), closed book from a zero state."""
    rows = [_qa_tokens(None, [qa]) for qa in qas]
    ce = _ce_pairs([(x, y) for x, y, _ in rows])
    return [float(c[np.array(m, dtype=bool)].mean()) for c, (_, _, m) in zip(ce, rows)]


def _teach():
    """--teach: see its help. Episodes run in order on one set of weights, so later quizzes of earlier
    answers measure forgetting."""
    dev = args.device
    model.eval()                                   # BatchNorm and the read scale: inference statistics
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.SGD(params, lr=args.teach_lr)
    pages = _teach_pages(args.teach + args.teach_control)
    eps, ctrl = pages[:args.teach], [prs[0] for _, prs in pages[args.teach:]]
    teacher = _Teacher(args.teach_teacher) if args.teach_ask == 'model' else None
    ctrl_before = _closed_ce(ctrl) if ctrl else []

    def feed(ids, dff, grad=False):
        """Step through ids from dff -> (list of logits, final dff)."""
        out = []
        with torch.set_grad_enabled(grad):
            for b in ids:
                dff, o = model.step(torch.tensor([b], device=dev), dff)
                out.append(model.text_dec(o))
                if not grad:
                    dff = dff.detach()
        return out, dff

    rec = []
    for k, (page, pairs) in enumerate(eps):
        t0 = time.time()
        _, page_dff = feed([_NULL] + _tokenizer.encode(page), model.new_state(1, dev))
        if args.teach_ask == 'data':
            q, a = pairs[0]
            q_ids = _tokenizer.encode('\n\nQ: ' + q)
        else:                                      # the model asks: sample after "Q:" until a newline
            q_ids = _tokenizer.encode('\n\nQ:')
            lg, dff = feed(q_ids, page_dff)
            for _ in range(40):
                b = torch.multinomial(_truncate(F.softmax(lg[-1][0].float(), dim=-1)), 1).item()
                if '\n' in _tokenizer.decode([b]):
                    break
                q_ids.append(b)
                lg, dff = feed([b], dff)
            q = _tokenizer.decode(q_ids).replace('Q:', '', 1).strip()
            if len(q) < 3:
                _emit(f'TEACH ep {k:4d} | (no question: {_printable(q)!r}) skipped')
                continue
            a = teacher.answer(page, q)
            if not a:
                _emit(f'TEACH ep {k:4d} | Q: {_printable(q)} | (no answer) skipped')
                continue
        _, dff = feed(q_ids[:-1], page_dff)        # the state before the question's last token
        head, ans = _tokenizer.encode('\nA:'), _tokenizer.encode(' ' + a)
        xs, ys = [q_ids[-1]] + head + ans[:-1], head + ans
        mask = torch.tensor([0.0] * len(head) + [1.0] * len(ans), device=dev)
        y = torch.tensor(ys, device=dev)
        closed_before = _closed_ce([(q, a)])[0]
        start = dff.detach()
        open_before = None
        for _ in range(args.teach_steps):
            lg, _ = feed(xs, start, grad=True)
            ce = F.cross_entropy(torch.cat(lg).float(), y, reduction='none')
            loss = (ce * mask).sum() / mask.sum()
            if open_before is None:
                open_before = float(loss)
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            lg, _ = feed(xs, start)
            open_after = float((F.cross_entropy(torch.cat(lg).float(), y, reduction='none') * mask).sum() / mask.sum())
        closed_after = _closed_ce([(q, a)])[0]
        rec.append(dict(ep=k, q=q, a=a, open_before=open_before, open_after=open_after,
                        closed_before=closed_before, closed_after=closed_after))
        _emit(f'TEACH ep {k:4d} | Q: {_printable(q)[:80]} | A: {_printable(a)[:40]} | open {open_before:.2f} -> '
              f'{open_after:.2f} | closed {closed_before:.2f} -> {closed_after:.2f} | {time.time() - t0:.1f}s')
    if not rec:
        raise SystemExit('--teach: no episode ran')
    finals = _closed_ce([(r['q'], r['a']) for r in rec])
    for r, f in zip(rec, finals):
        r['closed_final'] = f
    ctrl_after = _closed_ce(ctrl) if ctrl else []
    m = lambda key: float(np.mean([r[key] for r in rec]))
    _emit(f'TEACHSUM episodes {len(rec)} ask {args.teach_ask} lr {args.teach_lr:g} steps {args.teach_steps} | '
          f'closed before {m("closed_before"):.3f} after {m("closed_after"):.3f} end {m("closed_final"):.3f} | '
          f'open before {m("open_before"):.3f} after {m("open_after"):.3f} | control '
          f'{np.mean(ctrl_before) if ctrl else float("nan"):.3f} -> {np.mean(ctrl_after) if ctrl else float("nan"):.3f}')
    if args.teach_json:
        with open(args.teach_json, 'w') as f:
            json.dump(dict(args={k: v for k, v in vars(args).items() if k.startswith('teach')}, episodes=rec,
                           control_before=ctrl_before, control_after=ctrl_after), f, indent=1)


if args.teach:
    _teach()
    raise SystemExit(0)

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
              for k in ((n, f'{n}-blind') if n in _IMAGE_DATASETS else
                        tuple(n + sfx for see, hear, sfx in _VIDEO_VARIANTS
                              if see or not hear or model.streams != 3) if n in _VIDEO_DATASETS
                        else (n,))]:
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
_bn_layers = [m for m in model.modules() if isinstance(m, nn.BatchNorm2d)]
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

# --weight_ema: slow copies of the trainable weights and the float buffers (BatchNorm stats)
_live = {n: p for n, p in model.named_parameters() if p.requires_grad}
_live.update({n: b for n, b in model.named_buffers() if b.is_floating_point()})
_wema = {}
for _T in [int(float(t)) for t in args.weight_ema.split(',') if t]:
    _c = ((_loaded_ckpt or {}).get('weight_ema') or {}).get(_T)
    if _c is not None and set(_c) == set(_live):
        _wema[_T] = {n: _c[n].to(_live[n].device).clone() for n in _live}
        print(f'--weight_ema: T={_T} average restored from the checkpoint', flush=True)
    else:
        _wema[_T] = {n: t.detach().clone() for n, t in _live.items()}
        print(f'--weight_ema: T={_T} average starts from the loaded weights', flush=True)
_wema_lists = {T: ([e[n] for n in _live], [_live[n] for n in _live]) for T, e in _wema.items()}
if _wema:
    print(f'--weight_ema: {sum(t.numel() for t in _live.values()) / 1e6:.1f}M values per average',
          flush=True)
_loaded_ckpt = None


def _wema_step():
    with torch.no_grad():
        for T, (e, live) in _wema_lists.items():
            torch._foreach_lerp_(e, [t.detach() for t in live], 1.0 / T)


def _wema_swap(T):
    """Exchange the live weights with the T average (twice restores them)."""
    with torch.no_grad():
        for e, live in zip(*_wema_lists[T]):
            tmp = live.detach().clone()
            live.copy_(e)
            e.copy_(tmp)


def _wema_eval(step):
    """EVAL (held-out loss) for each --weight_ema average, as corpus <name>~emaTK."""
    for T in _wema:
        _wema_swap(T)
        try:
            for corpus in [c for c in _eval_corpus_names() if c not in _MEDIA_DATASETS][:1]:
                _score(step, corpus, _eval_docs(corpus), tag=f'{corpus}~ema{T // 1000}K',
                       bands=False)
        except Exception as e:
            print(f'WARNING: --weight_ema eval failed at step {step}: {e!r}', flush=True)
        finally:
            _wema_swap(T)


def _lr_factor(step):
    """lr / lr_max at a global step."""
    if args.schedule == 'const':
        return 1.0
    if args.schedule == 'decay':
        d0 = _start_step if args.decay_start is None else args.decay_start
        if step >= d0:
            f = (1.0 + math.cos(math.pi * min((step - d0) / max(1, args.decay_steps), 1.0))) / 2.0
            return (args.lr_final + (args.lr_max - args.lr_final) * f) / args.lr_max
    if args.lr_restart:          # warm up again from this run's first step
        step -= _start_step
    f = (1.0 - math.cos(math.pi * min(max(0, step) / max(1, args.lr_period), 1.0))) / 2.0
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
# --imagine rows hold their latest invented picture the same way; until a row's first picture
# of an example arrives it is not live and gets a zero grid, like a plain text row.
_BANK_ROWS = _IMAGE_ROWS + _SYNTH_ROWS
_img_rows = torch.tensor(_BANK_ROWS, dtype=torch.long, device=args.device)
_bank_of = {r: j for j, r in enumerate(_BANK_ROWS)}
img_bank = torch.zeros(len(_BANK_ROWS), 3, _IMG_BANK, _IMG_BANK, dtype=torch.uint8,
                       device=args.device)
img_fit = torch.zeros(len(_BANK_ROWS), 3, _IMG_IN, _IMG_BANK, dtype=torch.uint8,
                      device=args.device)
img_hw = torch.full((len(_BANK_ROWS), 3), float(_IMG_BANK), device=args.device)
img_live = torch.tensor([r in _IMAGE_ROWS for r in _BANK_ROWS], dtype=torch.bool,
                        device=args.device)
if model.streams == 3 and _BANK_ROWS:
    raise SystemExit('--streams 3: image corpora and --imagine are not supported yet')
if _BANK_ROWS and model.img_enc is None:
    raise SystemExit('--mix has an image corpus (or --imagine is on) but the model has no '
                     'image encoder')
# rows of each corpus, for the per-corpus loss columns of a mixed run
_rows_of, _r = {}, 0
for _n, _k in _MIX:
    _rows_of.setdefault(_n, []).extend(range(_r, _r + _k))
    _r += _k
_text_names = [n for n in _rows_of if n not in _MEDIA_DATASETS]
# --continuous: rows whose example kind keeps its registers across example boundaries
_continuous_row = torch.tensor([('image' if n in _IMAGE_DATASETS else 'video' if n in _VIDEO_DATASETS
                                 else 'text') in _continuous
                           for n, k in _MIX for _ in range(k)], device=args.device)
_video_row = torch.tensor([n in _VIDEO_DATASETS for n, k in _MIX for _ in range(k)], device=args.device)
_text_row = torch.tensor([n not in _MEDIA_DATASETS for n, k in _MIX for _ in range(k)], device=args.device)

# Video rows: each holds its example's JPEG frames (decoded on the GPU when the frame on screen
# changes, cropped 224x224 at a random offset per example along the longer side) and the Mimi
# latents of its sound in a fixed-size GPU buffer; every step the current frame goes through
# the image encoder and the last S*S Mimi frames heard make the audio grid.
_vid_rows = torch.tensor(_VIDEO_ROWS, dtype=torch.long, device=args.device)
_vid_of = {r: j for j, r in enumerate(_VIDEO_ROWS)}
_VID_CAP = int(_VID_MAXSPAN * _AUD_RATE) + 256         # Mimi frames a row's buffer holds
vid_cur = torch.zeros(len(_VIDEO_ROWS), 3, _IMG_IN, _IMG_IN, dtype=torch.uint8, device=args.device)
_own = None                  # --inner_voice: each row's token sampled at the last step (its next input
                             # after a silent tick)
vid_grid = None              # the frozen encoder's grid of vid_cur, recomputed only for rows whose
                             # frame changed (frames are held between 2 fps updates)
vid_lat = (torch.zeros(len(_VIDEO_ROWS), _AUD_DIM, _VID_CAP, dtype=torch.float16, device=args.device)
           if _VIDEO_ROWS and model.aud_width and model.audio_encoder not in _WAV_ENCODERS else None)
# quartznet: each video row's int16 sound buffer (see _qn_buffer), its audio grid and the cells
# heard when that was computed (it runs only for rows whose sound refreshed)
vid_wav = (torch.zeros(len(_VIDEO_ROWS), _QN_WIN + _VID_CAP * _QN_HOP, dtype=torch.int16,
                       device=args.device)
           if _VIDEO_ROWS and model.audio_encoder in _WAV_ENCODERS else None)
vid_agrid = None
vid_heard = torch.full((len(_VIDEO_ROWS),), -1.0, device=args.device)
if _VIDEO_ROWS and model.img_enc is None:
    raise SystemExit('--mix has a video corpus but the model has no image encoder')
_vid_rec = False             # --sample_vis: record the next example to start in any video row


def _grad_norm():
    """The global gradient norm, one host sync (not one per parameter tensor: behind a GPU
    shared with another process each sync waits its turn)."""
    g = [p.grad.detach() for p in model.parameters() if p.grad is not None and p.requires_grad]
    return float(torch.linalg.vector_norm(torch.stack(torch._foreach_norm(g)))) if g else 0.0


def _save(i, n_examples):
    if not all(torch.isfinite(t).all() for t in model.state_dict().values()
               if t.is_floating_point()):
        print(f'WARNING: non-finite params at step {i}; skipping checkpoint save')
        return
    log = open(args.log).read() if os.path.exists(args.log) else ''
    torch.save({'saved_args': vars(args), 'state_dict': model.state_dict(), 'log': log,
                'step': i, 'examples': n_examples, 'examples_by': dict(_n_by),
                'lr': optimizer.param_groups[0]['lr'],
                'optimizer': optimizer.state_dict(),
                'weight_ema': {T: dict(e) for T, e in _wema.items()}}, args.save)


def _gen_lines(i):
    """GEN samples (text-only, from <NUL> and --prompt), captions of --gen_images held-out
    images per image eval corpus for the --gen_vis panel (one GENI/REF pair of them in the
    log), and a recent training text per corpus."""
    lines = []
    for p in dict.fromkeys(['', args.prompt]):
        prompt = _prompt_ids(p)
        out = model.generate(prompt, _GEN_SAMPLE, temperature=args.temperature)
        lines.append(f'GEN step {i:10} [{p or NUL_TEXT}]: {_render(prompt + out)}')
        sc = _gen_scorer.score(_decode_plain(out)) if _gen_scorer else ''
        if sc:
            if args.fluency_target and not p and _gen_scorer.pct is not None:
                # --fluency_target: integral control of log(min_p) on this sample's fluency
                err = (args.fluency_target - max(-100.0, min(300.0, _gen_scorer.pct))) / 100.0
                args.min_p = min(0.9, max(1e-4, (args.min_p or 0.1) * math.exp(args.fluency_gain * err)))
            if args.min_p:
                sc += f' min_p {args.min_p:.4f}'
            lines.append(f'GENSCORE step {i:10} [{p or NUL_TEXT}]: {sc}')
    panel = []
    for c in _eval_corpus_names():
        if c not in _IMAGE_DATASETS or model.img_enc is None or not args.gen_images:
            continue
        n = len(_eval_docs(c))
        if not n:
            continue
        # a new random set of held-out images at every GEN, keyed by the step alone so a
        # resume redraws the same set and runs see the same images at the same step; the log
        # gets one pair per GEN, the first of the set
        ks = random.Random(f'{c}:{i}').sample(range(n), min(n, args.gen_images))
        logk = ks[0]
        for k in ks if args.gen_vis and _gen_inbox is not None else [logk]:
            prompt = _prompt_ids()
            out = model.generate(prompt, _GENI_LEN, temperature=args.temperature,
                                 image=_eval_imgs[c][k])
            iid, cls, cap = _eval_meta[c][k]
            if k == logk:
                lines.append(f'GENI step {i:10} [{iid}{" " if cls else ""}{cls.split(",")[0]}]: '
                             f'{_render(prompt + out)}')
                lines.append(f'REF  step {i:10} [{iid}]: {_printable(cap[:400])}')
            panel.append((_eval_imgs[c][k].permute(1, 2, 0).numpy(),
                          (f'{cls.split(",")[0]}  ({iid})' if cls else iid), _decode_plain(out), cap))
    if panel and _gen_inbox is not None and args.gen_vis:
        try:
            _gen_inbox.put_nowait(('gen', i, panel))
        except queue.Full:
            pass                                  # viewer busy: skip this panel
    vpanel = []
    for c in _eval_corpus_names():
        if c not in _VIDEO_DATASETS or model.img_enc is None or not args.gen_images:
            continue
        # fresh held-out videos every refresh (the eval set's 64 kept coming back), each
        # from a random event
        rng = random.Random(f'{c}:{i}')
        want = min(_GENV_CLIPS, args.gen_images) if args.gen_vis and _gen_inbox is not None else 1
        try:
            clips = [g for g in (_gen_clip(c, rng) for _ in range(want)) if g is not None]
        except Exception as e:
            print(f'WARNING: GEN video clips: {e!r}', flush=True)
            clips = []
        for n_clip, (steps, v) in enumerate(clips):
            # the caption generated with picture and sound over the media time of the clip's
            # first _GENV_LEN reference tokens; each stream shown up to REF's length, with a
            # mark every _GENV_MARK s of media time
            ys = [y for _, y in steps]
            vid, cat, _ = v.meta
            tick0 = v.t0 + v.phase / v.rate
            if isinstance(ys[0], tuple):     # --fifo3: each stream beside its own reference
                L = min(len(ys), int(_GENV_SECS * v.rate))
                gen3 = model.generate3(L, v, temperature=args.temperature)
                caps = {}
                for lab, st in (('see', 2), ('hear', 1), ('think', 0)):
                    at = [k for k in range(L) if ys[k][st] != _SIL]
                    caps[lab] = _timed_text(gen3[0][st], gen3[1][st], tick0, v.rate, 1 << 30)
                    caps[f'{lab} REF'] = _timed_text([ys[k][st] for k in at], at, tick0, v.rate,
                                                     1 << 30)
                    if n_clip == 0:
                        lines.append(f'GENV step {i:10} [{vid}{" " if cat and lab == "see" else ""}'
                                     f'{cat if lab == "see" else ""}] {lab}: '
                                     f'{_printable(_decode_plain(gen3[0][st]))}')
                        lines.append(f'REF  step {i:10} [{vid}] {lab}: '
                                     f'{_printable(_decode_plain([ys[k][st] for k in at]))}')
                ref_t = None
            else:
                at = [j for j, y in enumerate(ys) if y != _SIL][:_GENV_LEN]
                ref = _decode_plain([ys[j] for j in at])
                n_ref = max(1, len(ref))
                L = at[-1] + 1 if at else len(ys)
                ref_t = _timed_text([ys[j] for j in at], at, tick0, v.rate, n_ref)
            if ref_t is None:
                pass
            elif model.streams == 3:
                (tx, vo, im_), (ttx, tvo, tim) = model.generate3(L, v, temperature=args.temperature)
                caps = {lab: _timed_text(ids, tk, tick0, v.rate, n_ref)
                        for lab, ids, tk in (('see', im_, tim), ('hear', vo, tvo),
                                             ('think', tx, ttx))}
                if n_clip == 0:
                    tag = f'[{vid}{" " if cat else ""}{cat}]'
                    for lab, ids in (('see', im_), ('hear', vo), ('think', tx)):
                        lines.append(f'GENV step {i:10} {tag} {lab}: '
                                     f'{_printable(_decode_plain(ids)[:n_ref])}')
                        tag = f'[{vid}]'
                    lines.append(f'REF  step {i:10} [{vid}]: {_printable(ref)}')
            else:
                cap = model.generate(_prompt_ids(), len(ys), temperature=args.temperature, video=v,
                                     stop_chars=n_ref)
                L = max(1, min(len(ys), len(cap)))
                caps = {'A+V': _decode_plain(cap)[:n_ref]}
                if n_clip == 0:
                    lines.append(f'GENV step {i:10} [{vid}{" " if cat else ""}{cat}]: '
                                 f'{_printable(_decode_plain(cap)[:n_ref])}')
                    lines.append(f'REF  step {i:10} [{vid}]: {_printable(ref)}')
            # the sound from the window's start (a quartznet buffer / the codes begin a0 cells
            # in, up to 64 cells before it) to the last cell heard
            c0 = max(0.0, v.t0 * _AUD_RATE - v.a0)
            c1 = max(c0 + 1, v.ai[L - 1])
            spec = None
            if model.aud_enc is not None:
                spec = (_spectro(None, args.device, v.lat[_QN_WIN + round(c0 * _QN_HOP):
                                                          _QN_WIN + int(c1 * _QN_HOP)])
                        if v.lat.dim() == 1 else
                        _spectro(v.codes[:, int(c0):int(c1)], args.device))
            f1 = v.fi[L - 1]
            sel = np.linspace(v.fi[0], f1, 4).round().astype(int)
            strip = np.concatenate([v.frames[f].permute(1, 2, 0).numpy() for f in sel], axis=1)
            ftimes = [(v.f0 + f) / v.fps for f in sel]
            t1 = v.t0 + (L - 1 + v.phase) / v.rate
            ext = (v.t0, v.t0 + (spec.shape[1] / 100 if spec is not None else t1 - v.t0))
            vpanel.append((strip, spec, f'{vid}  {cat}  {v.t0:.0f}-{t1:.0f}s'.strip(),
                           dict(caps, REF=ref_t) if ref_t is not None else caps, ftimes, ext))
    if vpanel and _gen_inbox is not None and args.gen_vis:
        try:
            _gen_inbox.put_nowait(('genv', i, vpanel))
        except queue.Full:
            pass
    with _text_lock:
        samples = {n: st['sample'] for n, st in _text_stats.items() if st['sample'] and n in _MEDIA_DATASETS}
    for n, smp in samples.items():
        lines.append(f'TXT-{n}: {_printable(_sample_window(smp))}')
    # TXT-SAMPLE: what a random text row has just read (so the draw follows the batch's shares),
    # labelled with its corpus and row
    rows = [r for r, n in enumerate(_ROW_CORPUS) if n not in _MEDIA_DATASETS]
    if rows and len(_ROW_SLOTS) == len(_ROW_CORPUS):
        r = random.Random(i).choice(rows)
        sl = _ROW_SLOTS[r]
        steps, pos = sl.steps, sl.pos
        txt = _decode_plain([y for _, y in steps[max(0, pos - 96):pos]]) if steps else ''
        lines.append(f'TXT-SAMPLE: [{_ROW_CORPUS[r]} row {r}] {_printable(txt[-240:])}')
    return lines


def _spectro(codes, dev, w16=None):
    """Mimi codes -> log-magnitude spectrogram [freq, time] numpy (0-8 kHz, 100 columns/s),
    from the sound the frozen Mimi decoder renders; or of w16, int16 sound at 16 kHz."""
    if w16 is not None:
        wav = torch.as_tensor(w16).to(dev).float() / 32768.0
        n_fft, hop = 683, 160                    # 342 bins over 0-8 kHz, as below
    else:
        wav = torch.from_numpy(model.aud_enc.audio(codes, dev)).to(dev)
        n_fft, hop = 1024, 240
    if wav.numel() < n_fft:
        return np.zeros((171, 1), np.float32)
    S_ = torch.stft(wav, n_fft=n_fft, hop_length=hop, window=torch.hann_window(n_fft, device=dev),
                    return_complex=True).abs()
    return torch.log10(S_[:342] + 1e-4).cpu().numpy()


def _video_panel(i, m, off):
    """--sample_vis: one training video example as the TRAIN video window shows it: its first
    _VID_PANEL_TOK tokens, up to _VID_PANEL_CELLS frames spread over them (each labelled with
    the tokens read while it was on screen), and the spectrogram of the sound over that span."""
    ys = [y for _, y in m['steps']]
    head = None
    if ys and isinstance(ys[0], tuple):
        # --fifo3: the first _GENV_SECS s, each stream's targets marked every _GENV_MARK s of
        # media time; frames labelled with the speech heard while they were on screen
        W = min(m['n'], int(_GENV_SECS * m['clock']))
        head = []
        for lab, st in (('see', 2), ('hear', 1), ('think', 0)):
            at = [k for k in range(W) if ys[k][st] != _SIL]
            head.append((lab, _timed_text([ys[k][st] for k in at], at, m['t0'], m['clock'],
                                          1 << 30)))
        ys = [y[1] for y in ys]
    elif m.get('clock'):            # ticks: as many as the first _VID_PANEL_TOK tokens span
        at = [k for k, y in enumerate(ys) if y != _SIL]
        W = at[min(_VID_PANEL_TOK, len(at)) - 1] + 1 if at else m['n']
    else:
        W = min(m['n'], _VID_PANEL_TOK)
    fi, ids = m['fi'][:W], ys[:W]
    frames = sorted(set(fi))
    pick = frames[::max(1, math.ceil(len(frames) / _VID_PANEL_CELLS))][:_VID_PANEL_CELLS]
    ims = _decode_jpegs([m['jpegs'][f] for f in pick], 'cpu')
    cells = []
    for f, im in zip(pick, ims):
        ks = [k for k, g in enumerate(fi) if g == f]
        a, b = ks[0], ks[-1] + 1
        cells.append((_thumb(_crop224(im, off), 160), (m['f0'] + f) / m['fps'], a, b,
                      _decode_plain(ids[a:b])))
    a_end = m['ai'][W - 1] if W else 0
    if m.get('wav') is not None:
        spec = _spectro(None, args.device, m['wav'][_QN_WIN:_QN_WIN + int(max(1, a_end) * _QN_HOP)])
    elif model.aud_enc is not None:
        spec = _spectro(m['codes'][:, :int(max(1, a_end))], args.device)
    else:
        spec = np.zeros((1, 1), np.float32)
    ext = (m['a0'] / _AUD_RATE, (m['a0'] + a_end) / _AUD_RATE)
    n = f'{m["n"]} ticks at {m["clock"]:g} Hz' if m.get('clock') else f'{m["n"]} tokens'
    head = head or _decode_plain(ids)
    return ('video', i, m['name'], head, cells, spec, ext, n)


_VID_PANEL_TOK = 400         # TRAIN video window: tokens shown ...
_VID_PANEL_CELLS = 12        # ... and frames
_GENV_CLIPS = 1              # GEN video window: clips per refresh ...
_GENV_SPAN = 60.0            # ... each a window of at most this many seconds from a random event
_GENV_MARK = 5.0             # ... its captions marked every this many seconds of media time
_GENV_SECS = 20.0            # ... --fifo3: each clip's first this many seconds
_GENV_LEN = 80               # ... REF = each clip's first this many reference tokens, and the
                             # generated caption runs until it is as long as REF (characters)


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
                          'name': f"{_img_name.get(j, '')}   {h}x{w} px",     # cropped from
                          'crops': [], 'toks': []}
    rec = _sample['rec']
    if rec is not None and len(rec['crops']) < 160:
        crop = ((views[j] * _IMG_STD_T + _IMG_MEAN_T) * 255.0).clamp(0, 255)
        if x_list[r] < 0:                 # <NUL> blinks: the model saw no image, show black
            crop = torch.zeros_like(crop)
        rec['crops'].append(_thumb(crop, 96))
        rec['toks'].append(NUL_TEXT if x_list[r] < 0 else _tokenizer.decode([x_list[r]]))


class _Imaginer:
    """--imagine: a text-to-image pipeline in a thread beside training, inventing the pictures
    of the --imagine rows from their own text. The main loop calls step() once per training
    step BEFORE the step's tokens are recorded, so a picture is always made from tokens the row
    has already read. The thread repeatedly takes the --imagine_batch rows that have read the
    most tokens since their last request (at least --imagine_min) and generates their pictures
    on its own CUDA stream; a picture that arrives after its row started a new example is
    dropped."""

    _CELLS = 12                   # pictures per TRAIN imagine panel

    def __init__(self, rows):
        self.rows = list(rows)
        self.hist = {r: [] for r in self.rows}    # tokens read in the current example
        self.doc = {r: 0 for r in self.rows}      # example counter per row
        self.fresh = {r: 0 for r in self.rows}    # tokens read since the last request
        self.busy = set()                         # rows with a request in flight
        self.lock = threading.Lock()
        self.done = queue.Queue()
        self.made, self.gap, self.t0 = 0, 0, time.time()
        self.rec = None                           # TRAIN imagine panel being recorded
        repo, self.steps, self.guidance = _IMAGINE_MODELS.get(args.imagine, (args.imagine, 1, 0.0))
        cuda = str(args.device).startswith('cuda')
        dtype = (torch.bfloat16 if 'Sana' in repo else torch.float16) if cuda else torch.float32
        from diffusers import AutoPipelineForText2Image
        if 'Sana_Sprint' in repo:
            from diffusers import SanaSprintPipeline
            pipe = SanaSprintPipeline.from_pretrained(repo, torch_dtype=dtype)
        else:
            kw = dict(variant='fp16') if 'stabilityai' in repo else {}
            pipe = AutoPipelineForText2Image.from_pretrained(repo, torch_dtype=dtype, **kw)
        pipe.set_progress_bar_config(disable=True)
        if getattr(pipe, 'safety_checker', None) is not None:
            pipe.safety_checker = None            # a blacked-out picture is no picture
        self.pipe = pipe.to(args.device)
        self.stream = torch.cuda.Stream(args.device) if cuda else None
        self.gen = torch.Generator(args.device).manual_seed(args.seed)
        print(f'--imagine: {repo} on {args.device} for {len(self.rows)} rows, '
              f'{self.steps} step(s), {args.imagine_size}px, window {args.imagine_window}',
              flush=True)
        threading.Thread(target=self._run, daemon=True).start()

    def _pick(self):
        """-> [(row, example counter, prompt)] for the next call, marking those rows busy."""
        with self.lock:
            cand = [r for r in self.rows if r not in self.busy
                    and self.fresh[r] >= args.imagine_min and self.hist[r]]
            cand.sort(key=lambda r: -self.fresh[r])
            out = []
            for r in cand[:args.imagine_batch]:
                self.gap += self.fresh[r]
                self.fresh[r] = 0
                self.busy.add(r)
                out.append((r, self.doc[r], self.hist[r][-args.imagine_window:]))
        return [(r, d, _tokenizer.decode(ids).strip()) for r, d, ids in out]

    def _run(self):
        while not stop.is_set():
            req = self._pick()
            if not req:
                time.sleep(0.005)
                continue
            try:
                # guidance always explicit: the pipeline default (CFG 7.5) burns out a turbo model
                kw = dict(prompt=[p for _, _, p in req], num_inference_steps=self.steps,
                          height=args.imagine_size, width=args.imagine_size,
                          guidance_scale=self.guidance, generator=self.gen, output_type='pt')
                with torch.cuda.stream(self.stream) if self.stream else contextlib.nullcontext():
                    ims = self.pipe(**kw).images
                    ims = (ims.float().clamp(0, 1) * 255).round().to(torch.uint8)
                if self.stream:
                    self.stream.synchronize()   # the main loop reads them on its own stream
            except Exception as e:
                print(f'--imagine: generation failed: {e!r}', flush=True)
                with self.lock:
                    self.busy.difference_update(r for r, _, _ in req)
                time.sleep(1.0)
                continue
            for (r, d, p), im in zip(req, ims):
                self.done.put((r, d, p, im))

    def step(self, i, x_list, flag_list):
        """Install the pictures that arrived (into the bank, marking their rows live), then
        record this step's tokens: a row starting an example forgets its text and picture."""
        while True:
            try:
                r, d, p, im = self.done.get_nowait()
            except queue.Empty:
                break
            with self.lock:
                self.busy.discard(r)
                stale = d != self.doc[r]
            if stale:
                continue
            if im.is_cuda:     # made on the generator's stream: keep its memory from being
                im.record_stream(torch.cuda.current_stream())    # reused before our copies run
            j = _bank_of[r]
            _bank_put(img_bank, img_hw, img_fit, j, im)
            img_live[j] = True
            self.made += 1
            if self.rec is not None and r == self.rec['row'] and self.rec['toks']:
                self.rec['cells'].append([_thumb(im, 128), len(self.rec['toks']), None, p])
        if self.rec is not None:
            self._record(i, x_list, flag_list)
        with self.lock:
            for r in self.rows:
                if flag_list[r]:
                    self.hist[r], self.fresh[r] = [], 0
                    self.doc[r] += 1
                    img_live[_bank_of[r]] = False
                if x_list[r] >= 0:
                    self.hist[r].append(x_list[r])
                    self.fresh[r] += 1

    def record(self, i):
        """--sample_vis: record the next example of the first --imagine row (unless one is
        still being recorded)."""
        if self.rec is None:
            self.rec = {'row': self.rows[0], 'step': i, 'toks': None, 'cells': []}

    def _record(self, i, x_list, flag_list):
        rec, r = self.rec, self.rec['row']
        if rec['toks'] is None:                   # waiting for the next example to start
            if flag_list[r]:
                rec['toks'], rec['step'] = [], i
            else:
                return
        elif flag_list[r] or len(rec['cells']) > self._CELLS or len(rec['toks']) >= 4000:
            n = len(rec['toks'])
            cells = rec['cells'][:self._CELLS]
            for k, c in enumerate(cells):         # each picture is shown until the next one
                c[2] = cells[k + 1][1] if k + 1 < len(cells) else n
            text = _tokenizer.decode([t for t in rec['toks'] if t >= 0])
            if cells and _gen_inbox is not None:
                spans = [(th, a, b, _tokenizer.decode([t for t in rec['toks'][a:b] if t >= 0]), p)
                         for th, a, b, p in cells]
                try:
                    _gen_inbox.put_nowait(('imagine', rec['step'], text, n, spans))
                except queue.Full:
                    pass
            self.rec = None
            return
        rec['toks'].append(x_list[r])

    def stats(self):
        """' img/s .. img_tok .. live ..' since the last call: pictures installed per second,
        tokens a row read between requests, and the share of rows with a picture."""
        now = time.time()
        rate = self.made / max(1e-9, now - self.t0)
        gap = self.gap / max(1, self.made)
        live = float(img_live[[_bank_of[r] for r in self.rows]].float().mean())
        self.made, self.gap, self.t0 = 0, 0, now
        return f' img/s {rate:5.1f} img_tok {gap:5.1f} live {live:4.2f}'


_imaginer = _Imaginer(_SYNTH_ROWS) if _SYNTH_ROWS else None

larr, garr = [], []
_blk, _blk_start = [], None      # --bptt: the current block's (loss, inputs) and its starting state
_rows_t = {}                 # each corpus's training rows as a device index tensor


def _mmean(v, m):
    """Mean of v where m, nan where m is empty -- a GPU tensor, no host sync."""
    m = m.to(v.dtype)
    return (v * m).sum() / m.sum()


carr = {n: [] for n in _rows_of} if len(_rows_of) > 1 else {}
_nul_col = {n: 'nul' if sum(m in _VIDEO_DATASETS for m in _rows_of) == 1 else f'nul_{n}'
            for n in _rows_of if n in _VIDEO_DATASETS}      # STEP column: loss_nul when one
if carr and _NUL_ID is not None:
    carr.update({c: [] for c in _nul_col.values()})
i, n_examples = _start_step, _start_exs
_n_by = {n: int(_start_exs_by.get(n, 0)) for n in _rows_of}     # examples trained per corpus
# STEP columns ex_t/ep_t (text corpora pooled) and ex_i/ep_i (image corpora pooled): examples
# trained and passes over the data (examples / corpus size; a streaming text corpus, whose
# size is unknown, reports its reshuffle count instead)
_kinds = [(k, ns, [_corpus_size(n) for n in ns]) for k, ns in
          (('t', _text_names), ('i', [n for n in _rows_of if n in _IMAGE_DATASETS]),
           ('v', [n for n in _rows_of if n in _VIDEO_DATASETS])) if ns]


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


_prof, _prof_t = collections.defaultdict(float), [0.0]


def _pt(name):
    """--profile: charge the time since the last mark to name."""
    if args.profile:
        if args.device != 'cpu':
            torch.cuda.synchronize()
        t = time.perf_counter()
        _prof[name] += t - _prof_t[0]
        _prof_t[0] = t


_stop_req = False
_doc_rec = {}                # --doc_log: row -> [start step, ids] being recorded
_doc_next = 0                # the step from which the next document start is recorded


def _doc_log_step(i, x_one, flag_list):
    """--doc_log: extend the records in progress by this step's text input; a row's record
    ends at its next document (or --doc_log_len tokens) and is appended to --doc_log_file.
    From every --doc_log-th step on, the next text row starting a document opens one."""
    global _doc_next
    for r in list(_doc_rec):
        s0, ids = _doc_rec[r]
        if flag_list[r] or len(ids) >= args.doc_log_len:
            del _doc_rec[r]
            keep = (s0 // args.doc_log) % args.doc_keep == 0
            recs = _load_doc_records()
            recs.append((s0, i, np.array(ids, dtype=np.int32), keep))
            if not keep:          # drop the brief records that have aged out
                recs[:] = [d for d in recs if d[3] or i - d[1] < _DOC_BRIEF]
            if keep:
                with open(_doc_file(), 'a') as f:
                    print(json.dumps(dict(step=s0, end=i, ids=ids)), file=f)
        else:
            ids.append(int(x_one[r]))
    if i >= _doc_next:
        for n in _text_names:
            r = next((r for r in _rows_of[n] if flag_list[r] and r not in _doc_rec), None)
            if r is not None:
                _doc_rec[r] = [i, [int(x_one[r])]]
                _doc_next = (i // args.doc_log + 1) * args.doc_log
                break


def _on_sigterm(signum, frame):
    """The first SIGTERM asks the loop to save a checkpoint at the next step boundary and
    exit (a restart then loses no steps); a second one exits at once."""
    global _stop_req
    if _stop_req:
        os._exit(143)
    _stop_req = True
    print(f'\nSIGTERM: saving a checkpoint at the next step, then exiting', flush=True)


signal.signal(signal.SIGTERM, _on_sigterm)
_tok_buf = collections.deque(maxlen=args.step_tokens or 1)   # --step_tokens
_tok_gen = torch.Generator(device=args.device).manual_seed(0) if args.step_tokens else None

try:
    while True:
        if args.profile and i - _start_step == 50:
            _prof.clear()
            _pt('-')
            _prof.clear()
        if args.profile and i - _start_step == 50 + args.profile:
            tot = sum(_prof.values())
            print(f'\nPROFILE {args.profile} steps: {args.profile / tot:.2f} steps/s, '
                  f'{1000 * tot / args.profile:.1f} ms/step')
            for k, v in sorted(_prof.items(), key=lambda kv: -kv[1]):
                print(f'PROFILE {k:<12} {1000 * v / args.profile:8.2f} ms  {100 * v / tot:5.1f}%')
            if args.device != 'cpu':
                print(f'PROFILE peak GPU memory {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB '
                      f'(--bptt {args.bptt}, batch {args.batch})')
            break
        if _stop_req:                # SIGTERM: save this step's weights and exit cleanly
            _save(i, n_examples)
            _emit(f'STOP step {i:10} SIGTERM: checkpoint saved at this step, exiting')
            break
        # before the save at the same step (same weights), so the checkpoint's copy of the log
        # holds its EVAL lines and a run resumed from it keeps them; not at step 0, where it
        # would only measure ln(vocab), nor at a resumed run's first step (the checkpoint it
        # loaded; --eval_at_start to measure it anyway)
        if args.eval_interval and i > 0 and ((i % args.eval_interval == 0 and i > _start_step) or
                                             (i == _start_step and args.eval_at_start)):
            _heldout_eval(i)
            _wema_eval(i)

        if i % args.checkpoint == 0:
            _save(i, n_examples)
            counts = _text_drain()
            te, tt = sum(e for e, _ in counts.values()), sum(t for _, t in counts.values())
            if te:
                ep = ' '.join(f'{n}={_epoch[n]}' for n in _text_names)
                per = (' | ' + ' '.join(f'{n} {e}/{t}' for n, (e, t) in counts.items())
                       if len(counts) > 1 else '')
                _emit(f'TEXT step {i:10} examples {te} tokens {tt} epoch {ep}{per}')

        if args.gen_interval and i % args.gen_interval == 0:
            _emit('\n' + '\n'.join(_gen_lines(i)) + '\n')
            if _gen_inbox is not None and args.sample_vis and _VIDEO_ROWS:
                _vid_rec = True                                     # record the next example
            elif _gen_inbox is not None and args.sample_vis and _IMAGE_ROWS:
                _sample = {'row': _IMAGE_ROWS[0], 'rec': None}     # record the next example
            elif _gen_inbox is not None and args.sample_vis and _imaginer is not None:
                _imaginer.record(i)

        _pt('other')
        x_list, y_list, flag_list, new_imgs, media = q.get()
        _pt('data_wait')
        # the text stream's input per row, for the image-bank tools (--fifo3 rows are triples)
        x_one = [x[0] if isinstance(x, tuple) else x for x in x_list]
        if args.doc_log:
            _doc_log_step(i, x_one, flag_list)
        n_examples += sum(flag_list)
        for n, rows in _rows_of.items():
            _n_by[n] += sum(flag_list[r] for r in rows)
        x = torch.tensor(x_list, dtype=torch.long).to(args.device)
        y = torch.tensor(y_list, dtype=torch.long).to(args.device)
        flag = torch.tensor(flag_list, dtype=torch.bool).to(args.device)
        img = aud = None
        if _BANK_ROWS or _VIDEO_ROWS:
            img = torch.zeros(len(x_list), model.img_width, model.S, model.S, device=args.device)
        if _VIDEO_ROWS:
            for r, m in new_imgs:
                if r not in _vid_of:
                    continue
                j = _vid_of[r]
                if vid_lat is not None:
                    lat = model.aud_enc.latents(m['codes'][:, :_VID_CAP], args.device)
                    vid_lat[j].zero_()
                    vid_lat[j, :, :lat.shape[1]] = lat.half()
                if vid_wav is not None:
                    snd = torch.from_numpy(m['wav'][:vid_wav.shape[1]])
                    vid_wav[j].zero_()
                    vid_wav[j, :len(snd)] = snd.to(args.device, non_blocking=True)
                    vid_heard[j] = -1
                if _vid_rec:          # any row: one row's examples can run for minutes
                    _vid_rec = False
                    try:
                        _gen_inbox.put_nowait(_video_panel(i, m, m['off']))
                    except queue.Full:
                        pass
            idx, shown = media
            if model.streams == 3:
                kout_v = torch.tensor([t[2] for t in idx], dtype=torch.long, device=args.device)
                kin_v = torch.tensor([t[3] for t in idx], dtype=torch.long, device=args.device)
            for j, im in shown:
                vid_cur[j] = im.to(args.device, non_blocking=True)
            if vid_grid is None:
                vid_grid = model.image_grid(_norm_u8(vid_cur))
            elif shown:
                js = torch.tensor([j for j, _ in shown], device=args.device)
                vid_grid[js] = model.image_grid(_norm_u8(vid_cur[js])).to(vid_grid.dtype)
            img[_vid_rows] = vid_grid
            _pt('image_enc')
            if vid_lat is not None or vid_wav is not None:
                aud = torch.zeros(len(x_list), model.aud_width, model.S, model.S, device=args.device)
                ends = torch.tensor([min(t[1], _VID_CAP) for t in idx], device=args.device)
            if vid_lat is not None:
                aud[_vid_rows] = model.audio_grid(vid_lat, ends).float()
            elif vid_wav is not None:
                ch = (ends != vid_heard).nonzero()[:, 0]
                if vid_agrid is None:
                    vid_agrid = torch.zeros(len(_VIDEO_ROWS), model.aud_width, model.S, model.S,
                                            device=args.device)
                if len(ch):
                    vid_agrid[ch] = model.audio_grid(vid_wav[ch], ends[ch])
                    vid_heard[ch] = ends[ch]
                aud[_vid_rows] = vid_agrid
            _pt('audio_enc')
        if _BANK_ROWS:
            for r, (im, name) in new_imgs:
                if r in _vid_of:
                    continue
                j = _bank_of[r]
                _bank_put(img_bank, img_hw, img_fit, j, im.to(args.device, non_blocking=True))
                _img_name[j] = name
            if _imaginer is not None:
                _imaginer.step(i, x_one, flag_list)
            views = _views(img_bank, img_hw, img_fit)
            grid = model.image_grid(views)
            if _SYNTH_ROWS:              # a row without a picture yet sees a zero grid
                grid = grid * img_live[:, None, None, None]
            img[_img_rows] = grid
            if _sample is not None:
                _record_sample(i, x_one, flag_list, views)

        _pt('inputs')
        dff_prev = model.dff
        model.train()
        if args.bn_frozen:
            for m in _bn_layers:
                m.eval()
        if model.streams == 3 and not args.fifo3:   # one-stream (x, y) -> the three streams
            kin, kout = torch.zeros_like(x), torch.zeros_like(x)
            if _VIDEO_ROWS:
                kin[_vid_rows], kout[_vid_rows] = kin_v, kout_v
            x, y = _stream_xy(x, y, kin, kout, _video_row)
            if _own is not None:     # the inner voice: a video row's text stream reads its own word
                x[:, 0] = torch.where(_video_row & (x[:, 0] == _PAD), _own, x[:, 0])
        if args.inner_voice:         # after a silent tick the input is the model's own token
            if _own is not None:     # (none at a resumed run's first step: _PAD stays)
                fb = x == _PAD
                if args.voice_drop:  # --voice_drop: some silent ticks keep _PAD (no word)
                    fb &= torch.rand(x.shape, device=x.device) >= args.voice_drop
                if args.caption_feed:   # --caption_feed: some caption words -> the model's own
                    fb |= (x >= 0) & _video_row & \
                        (torch.rand(x.shape, device=x.device) < args.caption_feed)
                if args.text_feed:      # --text_feed: some text words -> the model's own
                    fb |= (x >= 0) & _text_row & \
                        (torch.rand(x.shape, device=x.device) < args.text_feed)
                x = torch.where(fb, _own, x)
        if args.bptt > 1 and not _blk:            # --bptt: a block starts from a detached state
            _blk_start = model.dff
        logits, _ = model(x, flag=flag & ~_continuous_row, img=img, aud=aud, keep=args.reset_scale,
                          graph=args.bptt > 1)
        if args.step_tokens:         # row 0's text-stream input and argmax prediction, kept on the GPU
            with torch.no_grad():
                lg = (logits[0, 0] if logits.dim() > 2 else logits[0]).detach().float()[None]
                pr = _truncate(F.softmax(lg / max(args.temperature, 1e-6), dim=-1))
                _tok_buf.append(torch.stack([x[0, 0] if x.dim() > 1 else x[0],
                                             torch.multinomial(pr, 1, generator=_tok_gen)[0, 0]]))
        if model.streams == 3:
            ce_all = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1),
                                     reduction='none').view(y.shape)
        else:
            ce_all = F.cross_entropy(logits, y, reduction='none')
        if model.streams == 3:       # <NUL> targets weigh --nul_weight; text on video rows: none
            with torch.no_grad():    # (--fifo3: no sample is ever fed back; _own stays None)
                if not args.fifo3:
                    _own = torch.multinomial(_truncate(F.softmax(logits[:, 0].detach().float(), dim=-1)), 1)[:, 0]
            wt = torch.where(y == _NUL_ID, args.nul_weight, 1.0) * (y != -100)
            loss = (ce_all * wt).sum() / _loss_den(wt, y)
        elif args.inner_voice:
            with torch.no_grad():
                _own = torch.multinomial(_truncate(F.softmax(logits.detach().float(), dim=-1)), 1)[:, 0]
            loss = ce_all.sum() / (y != _SIL).sum().clamp(min=1)
        elif _NUL_ID is not None:    # --clock_hz: <NUL> targets weigh --nul_weight
            wt = torch.where(y == _NUL_ID, args.nul_weight, 1.0)
            loss = (ce_all * wt).sum() / _loss_den(wt, y)
        else:
            loss = ce_all.mean()
        _pt('forward')
        if not torch.isfinite(loss):         # keep the last good checkpoint on disk
            print(f'\n*** HALT: non-finite loss at step {i}: {loss.item()} dff_max '
                  f'{float(model.dff.abs().max())} logit_max {float(logits.detach().abs().max())}')
            break
        if args.bptt > 1:            # --bptt: hold the step until its block is complete
            _blk.append((loss, x, flag & ~_continuous_row, img, aud))
        if args.bptt == 1 or len(_blk) == args.bptt:
            if args.bptt > 1:
                loss_b = sum(t[0] for t in _blk) / len(_blk)
                loss_b.backward()
            else:
                loss.backward()
            _pt('backward')
            gnorm = _grad_norm()
            garr.append(gnorm)
            if not math.isfinite(gnorm):
                print(f'\n*** HALT: non-finite grad at step {i}')
                break
            if args.clip and gnorm > args.clip:
                for p in model.parameters():
                    if p.grad is not None:
                        p.grad.mul_(args.clip / gnorm)
            _pt('grad_norm')
            optimizer.step()
            _wema_step()
            _pt('optimizer')
            # recompute this step's (--bptt: the block's) states with the updated weights
            # (eval-mode BatchNorm), so the state carried forward is the one the model would
            # compute at inference
            model.dff = _blk_start if args.bptt > 1 else dff_prev
            model.eval()
            with torch.no_grad():
                for _, xb, fb, ib, ab in (_blk or [(None, x, flag & ~_continuous_row, img, aud)]):
                    model(xb, flag=fb, img=ib, aud=ab, keep=args.reset_scale)
            _blk = []
            _pt('recompute')

        larr.append(loss.detach())   # 0-d GPU tensors, read once per --monitor (no sync per step)
        if carr:
            with torch.no_grad():
                ce = ce_all.detach()
                for n, rows in _rows_of.items():
                    rt = _rows_t.get(n)
                    if rt is None:
                        rt = _rows_t[n] = torch.tensor(rows, device=ce.device)
                    if model.streams == 3:
                        yr, cr = y[rt], ce[rt]
                        if n in _VIDEO_DATASETS:     # caption words (voice, image; --fifo3 text
                            c0 = 0 if args.fifo3 else 1   # too); <NUL> apart
                            isn = yr[:, c0:] == _NUL_ID
                            carr[n].append(_mmean(cr[:, c0:], ~isn))
                            carr[_nul_col[n]].append(_mmean(cr[:, c0:], isn))
                        else:                        # the text stream
                            carr[n].append(cr[:, 0].mean())
                    elif _NUL_ID is not None and n in _VIDEO_DATASETS:
                        # caption tokens only, as EVAL; the <NUL> targets get their own column
                        isn = y[rt] == _NUL_ID
                        carr[n].append(_mmean(ce[rt], ~isn))
                        carr[_nul_col[n]].append(_mmean(ce[rt], isn))
                    elif args.inner_voice and n in _VIDEO_DATASETS:   # caption ticks only
                        carr[n].append(_mmean(ce[rt], y[rt] != _SIL))
                    else:
                        carr[n].append(ce[rt].mean())
        if _T0 is not None:          # once, at the first step
            _emit(f'STARTUP step {i:10} wall to first step {time.time() - _T0:6.1f}s (of which datasets '
                  f'{_t_data:6.1f}s)')
            _T0 = None
        if i % args.monitor == 0:
            flat = model.dff.reshape(-1)
            line = ('STEP {:10} wall {} loss {:12.9f} grad {:12.6f} lr {:10.9f} dff_mean {:12.5f} '
                    'dff_std {:12.5f} dff_max {:11.3f}'
                    ).format(i, datetime.datetime.now(), torch.stack(larr[-args.monitor:]).mean().item(),
                             np.mean(garr[-args.monitor:]), optimizer.param_groups[0]['lr'],
                             flat.mean().item(), flat.std().item(), flat.abs().max().item())
            line += _ex_ep()
            if _imaginer is not None:
                line += _imaginer.stats()
            for n, a in carr.items():
                v = torch.stack(a[-args.monitor:]).float().cpu().numpy()
                line += f' loss_{n} {np.nanmean(v) if np.isfinite(v).any() else float("nan"):6.3f}'
            _emit(line)
            if _tok_buf:
                t = torch.stack(list(_tok_buf)).tolist()
                _emit(f'TOK step {i:10} in: {_printable(_decode_plain([a for a, _ in t]))} || sampled: '
                      f'{_printable(_decode_plain([b for _, b in t]))}')
            del larr[:-args.monitor], garr[:-args.monitor]   # keep host RAM flat
            for a in carr.values():
                del a[:-args.monitor]

        _pt('stats')
        scheduler.step()
        optimizer.zero_grad()
        i += 1
        if args.run_steps is not None and i - _start_step >= args.run_steps:
            if i % args.checkpoint:      # the last step's weights, unless just saved
                _save(i, n_examples)
            break
except KeyboardInterrupt:
    pass
except BaseException:
    stop.set()      # else the non-daemon worker keeps a crashed run alive and longrun waits forever
    raise

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
