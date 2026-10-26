#!/usr/bin/env python3
"""Word timings of the captioned-video speech: a sidecar to tools/video_prep.py's
/data/finevideo_feat, one parquet per shard with the same file name, one row per video:

  id     source video id (as in finevideo_feat)
  s      list<float32>        start (s) of each 'say' event, in events order (the key vla.py
                              checks the alignment against)
  ws     list<list<float32>>  per say event, the media time each whitespace word of its text
  we     list<list<float32>>  starts / ends (s), from CTC forced alignment
  score  list<float32>        per say event, the mean frame probability of its aligned
                              characters (NaN where the alignment failed: the text did not fit
                              the frames; vla.py then spreads the words evenly as before)

FineVideo times speech per transcript segment (median 3.4 s); the words inside one are not
timed. Here each run of back-to-back segments (at most CHUNK s) is cut from the clean
soundtrack (tools/audio_prep.py's /data/finevideo_audio) with PAD s either side, QuartzNet 15x5
(the frozen CTC recognizer vla.py's --audio_encoder quartznet uses) gives 50 Hz character
log-probs, and torchaudio's forced_align puts the segment texts, lower-cased to its 28
characters (space, a-z, '), on its frames. A word with nothing alignable (a number, a symbol)
starts where the word before it ends and ends where the word after it starts.

CPU workers read and decode, the main process runs QuartzNet and the alignment on the GPU.
Resumable like audio_prep.py: finished shards are skipped, each is written to .tmp and renamed.

    nice -n 10 python tools/align_prep.py --out /data/finevideo_align
"""
import argparse
import collections
import glob
import io
import json
import math
import multiprocessing as mp
import os
import re
import sys
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

SR = 16000
PAD = 0.5                    # s of sound either side of a chunk of segments
CHUNK = 30.0                 # s: longest run of back-to-back segments aligned in one go
GAP = 0.3                    # s: a segment starting within this of the last one's end joins it
LABELS = " abcdefghijklmnopqrstuvwxyz'"
BLANK = len(LABELS)
FRAME = 0.02                 # s per QuartzNet output frame
QN_DIR = '/data/huggingface/quartznet'
SCHEMA = pa.schema([('id', pa.string()), ('s', pa.list_(pa.float32())),
                    ('ws', pa.list_(pa.list_(pa.float32()))),
                    ('we', pa.list_(pa.list_(pa.float32()))), ('score', pa.list_(pa.float32()))])


def norm_word(w):
    """A transcript word -> its characters in LABELS (may be '')."""
    return re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))


def chunks(say):
    """[(start, end, text)] of a video's say events -> [[event index, ...]] runs of
    back-to-back segments, each at most CHUNK s."""
    out, cur = [], []
    for i, (s, e, _) in enumerate(say):
        if cur and (s - say[cur[-1]][1] > GAP or e - say[cur[0]][0] > CHUNK):
            out.append(cur)
            cur = []
        cur.append(i)
    return out + ([cur] if cur else [])


def shard_chunks(job):
    """(feat shard, audio shard) -> (name, [(id, say [(s, e, text)], [chunk])]) where a chunk is
    (event indices, t0 (s), int16 sound from t0)."""
    feat, aud = job
    import soundfile as sf
    ev = {r['id']: [(float(s), float(e), t) for s, e, k, t in json.loads(r['events'])
                    if k == 'say' and t.strip()]
          for r in pq.read_table(feat, columns=['id', 'events']).to_pylist()}
    vids = []
    pf = pq.ParquetFile(aud)
    for g in range(pf.num_row_groups):
        for r in pf.read_row_group(g, columns=['id', 'flac']).to_pylist():
            say = ev.get(r['id'])
            if not say:
                continue
            wav = sf.read(io.BytesIO(r['flac']), dtype='int16')[0] if r['flac'] else \
                np.zeros(0, np.int16)
            cs = []
            for c in chunks(say):
                t0 = max(0.0, say[c[0]][0] - PAD)
                a, b = int(t0 * SR), int((say[c[-1]][1] + PAD) * SR)
                if b - a >= SR // 10 and a < len(wav):
                    cs.append((c, t0, np.ascontiguousarray(wav[a:b])))
            vids.append((r['id'], say, cs))
    return os.path.basename(feat), vids


def load_quartznet():
    """QuartzNet 15x5 from the .nemo weights vla.py downloads: (features fn, ctc (w, b))."""
    import torch
    import torch.nn.functional as F
    ck = next(os.path.join(r, f) for r, _, fs in os.walk(QN_DIR) for f in fs
              if f == 'model_weights.ckpt')
    sd = torch.load(ck, map_location='cpu', weights_only=True)
    dev = 'cuda'

    def fold(pw, p):
        s = sd[p + '.weight'] / torch.sqrt(sd[p + '.running_var'] + 1e-3)
        return (pw * s[:, None, None]).to(dev), (sd[p + '.bias'] - sd[p + '.running_mean'] * s).to(dev)

    BLOCKS = ([(256, 33, 1, 2, 1)] + [(256, 33, 5, 1, 1)] * 3 + [(256, 39, 5, 1, 1)] * 3 +
              [(512, 51, 5, 1, 1)] * 3 + [(512, 63, 5, 1, 1)] * 3 + [(512, 75, 5, 1, 1)] * 3 +
              [(512, 87, 1, 1, 2)])
    blocks = []
    for b, (c, k, rep, st, dil) in enumerate(BLOCKS):
        p = f'encoder.encoder.{b}.'
        subs = [(sd[p + f'mconv.{5 * r}.conv.weight'].to(dev),) +
                fold(sd[p + f'mconv.{5 * r + 1}.conv.weight'], p + f'mconv.{5 * r + 2}')
                for r in range(rep)]
        res = fold(sd[p + 'res.0.0.conv.weight'], p + 'res.0.1') if rep > 1 else None
        blocks.append((subs, res, k, st, dil))
    c3 = fold(sd['encoder.encoder.17.mconv.0.conv.weight'], 'encoder.encoder.17.mconv.1')
    ctc = (sd['decoder.decoder_layers.0.weight'].to(dev), sd['decoder.decoder_layers.0.bias'].to(dev))
    win, fb = sd['preprocessor.featurizer.window'].to(dev), sd['preprocessor.featurizer.fb'][0].to(dev)

    @torch.no_grad()
    def logprobs(wav):
        """float sound [N, L] -> CTC log-probs [N, T, 29] at 50 Hz (as vla.py's
        QuartzNetEncoder.features: zero padding is left out of the per-mel normalization)."""
        x = torch.cat([wav[:, :1], wav[:, 1:] - 0.97 * wav[:, :-1]], 1)
        s = torch.stft(x, 512, 160, 320, win, center=True, pad_mode='constant', return_complex=True)
        p = fb @ s.abs().pow(2)
        ok = (p.sum(1, keepdim=True) > 1e-10).float()
        x = torch.log(p + 2 ** -24)
        n = ok.sum(2, keepdim=True).clamp(min=2)
        mu = (x * ok).sum(2, keepdim=True) / n
        sdv = (((x - mu) * ok).pow(2).sum(2, keepdim=True) / (n - 1)).sqrt()
        x = (x - mu) / (sdv + 1e-5) * ok
        with torch.autocast('cuda', dtype=torch.float16):
            for subs, res, k, st, dil in blocks:
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
            x = F.relu(F.conv1d(x, c3[0].to(x.dtype), c3[1].to(x.dtype)))
        return F.conv1d(x.float(), *ctc).log_softmax(1).transpose(1, 2)
    return logprobs


def align(lp, say, idx, t0):
    """CTC log-probs [T, 29] of one chunk -> {event index: (word starts, word ends, score)}."""
    import torch
    import torchaudio.functional as AF
    words = [(i, w, norm_word(w)) for i in idx for w in say[i][2].split()]
    tgt, span = [], []                       # span: (first, last) target index of each word
    for _, _, n in words:
        if n:
            if tgt:
                tgt.append(0)                # the space between words (QuartzNet emits it)
            span.append((len(tgt), len(tgt) + len(n) - 1))
            tgt += [LABELS.index(ch) for ch in n]
        else:
            span.append(None)
    T = lp.shape[0]
    reps = sum(a == b for a, b in zip(tgt, tgt[1:]))
    out = {}
    ok = bool(tgt) and len(tgt) + reps <= T
    if ok:
        try:
            al, sc = AF.forced_align(lp.contiguous()[None], torch.tensor([tgt], dtype=torch.int32,
                                                             device=lp.device), blank=BLANK)
        except RuntimeError:
            ok = False
    if not ok:
        for i in idx:
            out[i] = ([math.nan] * len(say[i][2].split()), [math.nan] * len(say[i][2].split()),
                      math.nan)
        return out
    al, sc = al[0].tolist(), sc[0].exp().tolist()
    # frames of each target position: the alignment visits targets in order, a new one
    # wherever the label changes or a blank separates a repeat
    first, last, prob = [None] * len(tgt), [None] * len(tgt), [0.0] * len(tgt)
    j, prev = -1, BLANK
    for f, (a, p) in enumerate(zip(al, sc)):
        if a != BLANK:
            if a != prev:
                j += 1
                first[j] = f
            last[j] = f
            prob[j] = max(prob[j], p)
        prev = a
    st = [t0 + first[a] * FRAME if sp else None for sp in span for a in [sp[0] if sp else 0]]
    en = [t0 + (last[b] + 1) * FRAME if sp else None for sp in span for b in [sp[1] if sp else 0]]
    for k in range(len(words)):              # unalignable words: fill from their neighbours
        if st[k] is None:
            p = next((en[q] for q in range(k - 1, -1, -1) if en[q] is not None), None)
            n = next((st[q] for q in range(k + 1, len(words)) if st[q] is not None), None)
            p = p if p is not None else n if n is not None else t0
            n = n if n is not None else p
            st[k], en[k] = p, n
    k = 0
    chars = [prob[a] for a, c in enumerate(tgt) if c != 0]
    for i in idx:
        nw = len(say[i][2].split())
        ii = [q for q in range(k, k + nw) if span[q]]
        ps = [prob[a] for q in ii for a in range(span[q][0], span[q][1] + 1)]
        out[i] = (st[k:k + nw], en[k:k + nw], float(np.mean(ps)) if ps else math.nan)
        k += nw
    del chars
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat', default='/data/finevideo_feat')
    ap.add_argument('--audio', default='/data/finevideo_audio')
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--batch_s', type=float, default=480.0, help='s of sound per GPU batch')
    ap.add_argument('--limit', type=int, default=0, help='first N shards only')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.feat, '*.parquet')))
    files = files[:args.limit] if args.limit else files
    todo = [(f, os.path.join(args.audio, os.path.basename(f))) for f in files
            if os.path.exists(os.path.join(args.audio, os.path.basename(f))) and
            not os.path.exists(os.path.join(args.out, os.path.basename(f)))]
    print(f'{len(files)} shards, {len(todo)} to align', flush=True)

    import torch
    logprobs = load_quartznet()

    def gated(pool):                         # a few shards decoded ahead of the GPU
        pending = collections.deque()
        for j in todo:
            pending.append(pool.apply_async(shard_chunks, (j,)))
            if len(pending) >= args.workers + 2:
                yield pending.popleft().get()
        while pending:
            yield pending.popleft().get()

    t0, n_ev, n_fail, n_words, n_sound = time.time(), 0, 0, 0, 0.0
    with mp.get_context('spawn').Pool(args.workers, maxtasksperchild=4) as pool:
        for k, (name, vids) in enumerate(gated(pool)):
            ts = time.time()
            work = [(v, c) for v in range(len(vids)) for c in range(len(vids[v][2]))]
            work.sort(key=lambda vc: len(vids[vc[0]][2][vc[1]][2]))
            res = [dict() for _ in vids]
            b = 0
            while b < len(work):
                L = len(vids[work[b][0]][2][work[b][1]][2])
                e = b + 1
                while e < len(work) and (e - b + 1) * len(vids[work[e][0]][2][work[e][1]][2]) <= \
                        args.batch_s * SR:
                    e += 1
                L = len(vids[work[e - 1][0]][2][work[e - 1][1]][2])
                x = torch.zeros(e - b, L)
                for q in range(b, e):
                    w = vids[work[q][0]][2][work[q][1]][2]
                    x[q - b, :len(w)] = torch.from_numpy(w.astype(np.float32) / 32768.0)
                lp = logprobs(x.cuda())
                for q in range(b, e):
                    v, c = work[q]
                    idx, c0, w = vids[v][2][c]
                    res[v].update(align(lp[q - b, :len(w) // 320 + 1], vids[v][1], idx, c0))
                    n_sound += len(w) / SR
                b = e
            rows = []
            for (vid, say, _), r in zip(vids, res):
                ws, we, sc = [], [], []
                for i, (s, e, t) in enumerate(say):
                    a = r.get(i)
                    if a is None:                # no sound under it
                        a = ([math.nan] * len(t.split()), [math.nan] * len(t.split()), math.nan)
                    ws.append(a[0])
                    we.append(a[1])
                    sc.append(a[2])
                    n_fail += math.isnan(a[2])
                    n_words += len(t.split())
                n_ev += len(say)
                rows.append(dict(id=vid, s=[s for s, _, _ in say], ws=ws, we=we, score=sc))
            out = os.path.join(args.out, name)
            pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), out + '.tmp')
            os.replace(out + '.tmp', out)
            el = time.time() - t0
            print(f'[{k + 1}/{len(todo)}] {name}: {len(vids)} videos {sum(map(len, res))} segments '
                  f'in {time.time() - ts:.0f}s (total {n_ev} segments {n_words} words, '
                  f'{n_fail / max(1, n_ev):.2%} unaligned, {n_sound / 3600:.1f} h of speech, '
                  f'{n_sound / max(1e-3, el):.0f}x real time, {el / 3600:.2f} h)', flush=True)


if __name__ == '__main__':
    sys.exit(main())
