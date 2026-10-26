#!/usr/bin/env python3
"""Score every row of the local WIT corpus (tools/caption_prep.py wit) with two quality filters,
one output parquet per input shard (id, clip, edu), resumable:

  clip  cosine similarity of the image and its HUMAN caption under openai/clip-vit-large-patch14
        (centre 224 crop of the short-side-224 image; caption truncated to CLIP's 77 tokens);
        NaN when the row has no human caption. Low = the caption says little about what is seen.
  edu   HuggingFaceFW/fineweb-edu-classifier score (regression, ~0-5; FineWeb-Edu kept >= 3) of
        the training text -- human caption + newline + Gemini description, as vla.py joins
        them -- truncated to 512 tokens. High = educational, fineweb-edu-like subject matter.

    python tools/wit_score.py --src /data/wit_1m_recap --out /data/wit_1m_scores
"""
import argparse
import io
import multiprocessing
import os
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import torch
from PIL import Image
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, CLIPModel,
                          CLIPTokenizerFast)

CLIP = 'openai/clip-vit-large-patch14'
EDU = 'HuggingFaceFW/fineweb-edu-classifier'
MEAN = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1)
STD = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1)


def decode(b):
    """JPEG bytes -> uint8 [224, 224, 3]: short side 224 (bicubic), centre crop."""
    try:
        im = Image.open(io.BytesIO(b)).convert('RGB')
    except Exception:
        return None
    w, h = im.size
    s = 224 / min(w, h)
    im = im.resize((max(224, round(w * s)), max(224, round(h * s))), Image.BICUBIC)
    w, h = im.size
    l, t = (w - 224) // 2, (h - 224) // 2
    return np.asarray(im.crop((l, t, l + 224, t + 224)))


@torch.no_grad()
def clip_scores(rows, pool, model, tok, dev, bs=256):
    out = np.full(len(rows), np.nan, dtype=np.float32)
    caps = [(r['caption'] or '').strip() for r in rows]
    ims = pool.imap(decode, (r['image'] for r in rows), chunksize=32)
    for s in range(0, len(rows), bs):
        idx = list(range(s, min(s + bs, len(rows))))
        px = [next(ims) for _ in idx]
        keep = [k for k, i in enumerate(idx) if px[k] is not None and caps[i]]
        if not keep:
            continue
        x = torch.from_numpy(np.stack([px[k] for k in keep])).to(dev).permute(0, 3, 1, 2)
        x = ((x.float() / 255.0 - MEAN.to(dev)) / STD.to(dev)).half()
        t = tok([caps[idx[k]] for k in keep], padding=True, truncation=True, max_length=77,
                return_tensors='pt').to(dev)
        fi = model.get_image_features(pixel_values=x)
        ft = model.get_text_features(**t)
        sim = torch.nn.functional.cosine_similarity(fi.float(), ft.float(), dim=-1)
        out[[idx[k] for k in keep]] = sim.cpu().numpy()
    return out


@torch.no_grad()
def edu_scores(rows, model, tok, dev, bs=128):
    texts = ['\n'.join(t for t in ((r['caption'] or '').strip(),
                                   (r['gemini_caption'] or '').strip()) if t) for r in rows]
    enc = tok(texts, truncation=True, max_length=512)['input_ids']
    order = np.argsort([len(e) for e in enc])
    out = np.zeros(len(rows), dtype=np.float32)
    for s in range(0, len(order), bs):
        b = order[s:s + bs]
        t = tok.pad({'input_ids': [enc[i] for i in b]}, return_tensors='pt').to(dev)
        out[b] = model(**t).logits.squeeze(-1).float().cpu().numpy()
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='/data/wit_1m_recap')
    ap.add_argument('--out', default='/data/wit_1m_scores')
    ap.add_argument('--workers', type=int, default=20)
    ap.add_argument('--limit', type=int, default=0, help='rows per shard (0 = all; for tests)')
    ap.add_argument('--files', type=int, default=0, help='first N shards only (0 = all)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    dev = 'cuda'
    clip = CLIPModel.from_pretrained(CLIP, dtype=torch.float16).to(dev).eval()
    ctok = CLIPTokenizerFast.from_pretrained(CLIP)
    edu = AutoModelForSequenceClassification.from_pretrained(
        EDU, dtype=torch.float16).to(dev).eval()
    etok = AutoTokenizer.from_pretrained(EDU)
    files = sorted(f for f in os.listdir(args.src) if f.endswith('.parquet'))
    if args.files:
        files = files[:args.files]
    t0, n = time.time(), 0
    with multiprocessing.get_context('spawn').Pool(args.workers) as pool:
        for f in files:
            dst = os.path.join(args.out, f)
            if os.path.exists(dst):
                continue
            tr = time.time()
            rows = pq.read_table(os.path.join(args.src, f),
                                 columns=['image', 'id', 'caption', 'gemini_caption']).to_pylist()
            if args.limit:
                rows = rows[:args.limit]
            t1 = time.time()
            c = clip_scores(rows, pool, clip, ctok, dev)
            t2 = time.time()
            e = edu_scores(rows, edu, etok, dev)
            t3 = time.time()
            pq.write_table(pa.table({'id': [r['id'] for r in rows], 'clip': c, 'edu': e}),
                           dst + '.tmp')
            os.replace(dst + '.tmp', dst)
            n += len(rows)
            print(f'{f}: {len(rows)} rows, clip {np.nanmean(c):.3f}, edu {e.mean():.3f}; '
                  f'read/clip/edu {t1 - tr:.0f}/{t2 - t1:.0f}/{t3 - t2:.0f}s; '
                  f'{n} rows {time.time() - t0:.0f}s ({n / (time.time() - t0):.0f}/s)', flush=True)
    print('DONE', n)
