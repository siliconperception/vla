#!/usr/bin/env python3
"""Visual captions for the captioned-video corpus: a sidecar to exp/video_prep.py's
/data/finevideo_feat, one parquet per shard with the same file name, one row per video:

  id     source video id (as in finevideo_feat)
  t      list<float32> media time (s) of each captioned frame
  cap    list<string>  Florence-2-base <CAPTION> of that frame (picture only: no sound, no
                       metadata -- unlike FineVideo's activity lines)

Frames are the 2 fps JPEGs already in finevideo_feat. A frame is captioned on a shot change
(mean abs difference of 16x16 grey thumbnails over CUT) or once a static shot has gone REFRESH
seconds without one. Every gated caption is kept (near-repeats included); vla.py dedupes.
CPU workers decode and gate, the main process captions on the GPU. Resumable like
audio_prep.py: finished shards are skipped, each is written to .tmp and renamed.

    nice -n 10 python exp/vcap_prep.py --out /data/finevideo_vcap
"""
import argparse
import glob
import io
import multiprocessing as mp
import os
import sys
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

REFRESH = 4.0
CUT = 0.125
MODEL = 'florence-community/Florence-2-base'
SCHEMA = pa.schema([('id', pa.string()), ('t', pa.list_(pa.float32())),
                    ('cap', pa.list_(pa.string()))])


def gate(frames, fps):
    """Indices of the frames to caption."""
    from PIL import Image
    keep, last_t, last = [], -1e9, None
    for i, jp in enumerate(frames):
        th = np.asarray(Image.open(io.BytesIO(jp)).convert('L').resize((16, 16)),
                        np.float32) / 255.0
        t = i / fps
        if last is None or np.abs(th - last).mean() > CUT or t - last_t >= REFRESH:
            keep.append(i)
            last_t, last = t, th
    return keep


def shard_frames(f):
    """One feat shard -> (file, [(id, [times], [jpeg bytes]), ...]) of its gated frames."""
    pf = pq.ParquetFile(f)
    vids = []
    for g in range(pf.num_row_groups):
        for r in pf.read_row_group(g, columns=['id', 'fps', 'frames']).to_pylist():
            fps = float(r['fps'] or 2.0)
            k = gate(r['frames'] or [], fps)
            vids.append((r['id'], [i / fps for i in k], [r['frames'][i] for i in k]))
    return f, vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='/data/finevideo_feat')
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--limit', type=int, default=0, help='first N shards only')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.src, '*.parquet')))
    files = files[:args.limit] if args.limit else files
    todo = [f for f in files if not os.path.exists(os.path.join(args.out, os.path.basename(f)))]
    print(f'{len(files)} shards, {len(todo)} to caption', flush=True)

    import torch
    from PIL import Image
    from transformers import AutoProcessor, Florence2ForConditionalGeneration
    dev = 'cuda'
    proc = AutoProcessor.from_pretrained(MODEL)
    model = Florence2ForConditionalGeneration.from_pretrained(
        MODEL, dtype=torch.float16).to(dev).eval()

    @torch.no_grad()
    def caption(jpegs):
        out = []
        for b in range(0, len(jpegs), args.batch):
            ims = [Image.open(io.BytesIO(j)).convert('RGB') for j in jpegs[b:b + args.batch]]
            x = proc(text=['<CAPTION>'] * len(ims), images=ims,
                     return_tensors='pt').to(dev, torch.float16)
            y = model.generate(**x, max_new_tokens=40, num_beams=1, do_sample=False)
            out += [s.strip() for s in proc.batch_decode(y, skip_special_tokens=True)]
        return out

    t0, n_cap = time.time(), 0
    with mp.get_context('spawn').Pool(args.workers, maxtasksperchild=4) as pool:
        for k, (f, vids) in enumerate(pool.imap(shard_frames, todo)):
            ts = time.time()
            caps = caption([j for _, _, js in vids for j in js])
            rows, i = [], 0
            for vid, times, js in vids:
                rows.append(dict(id=vid, t=times, cap=caps[i:i + len(js)]))
                i += len(js)
            out = os.path.join(args.out, os.path.basename(f))
            pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), out + '.tmp')
            os.replace(out + '.tmp', out)
            n_cap += len(caps)
            print(f'[{k + 1}/{len(todo)}] {os.path.basename(f)}: {len(vids)} videos, '
                  f'{len(caps)} captions in {time.time() - ts:.0f}s ({len(caps) / max(1e-3, time.time() - ts):.0f}/s; '
                  f'total {n_cap}, {(time.time() - t0) / 3600:.2f} h)', flush=True)


if __name__ == '__main__':
    sys.exit(main())
