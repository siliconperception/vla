#!/usr/bin/env python3
"""Download an image-caption corpus from the hub into the local parquet layout vla.py reads
(see exp/img_prep.py): one parquet per source shard, row groups of 100, columns
image (encoded bytes), id, class, caption.

  redcaps  wusize/redcaps5m_resized: 584 webdataset tars (~1.9 GB, ~9K images each) of
           Reddit images. caption = the poster's own title (json 'original_caption'); the
           repo's 'caption' field is a synthetic recaption and is NOT used. class = ''.
  coco     jxie/coco_captions: COCO 2014 (Karpathy train/val/test), one row per human caption,
           5 per image. id = coco<cocoid>, so vla.py's id-hash held-out split keeps all five
           captions of an image on the same side. class = ''.

Resumable: finished outputs are skipped; a shard is written to .tmp and renamed when done.

    python exp/caption_prep.py redcaps --out /data/redcaps5m --workers 8
    python exp/caption_prep.py coco --out /data/coco_captions --workers 8
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import tarfile
import time

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfApi, HfFileSystem

REPOS = {'redcaps': 'wusize/redcaps5m_resized', 'coco': 'jxie/coco_captions'}
SCHEMA = pa.schema([('image', pa.binary()), ('id', pa.string()), ('class', pa.string()),
                    ('caption', pa.string())])
GROUP = 100

fs = None


def redcaps_rows(fh, i):
    """(image bytes, id, class, caption) per sample of one webdataset tar, streamed."""
    tf = tarfile.open(fileobj=fh, mode='r|')
    cur, key = {}, None
    for m in tf:
        if not m.isfile():
            continue
        k, ext = os.path.splitext(m.name)
        if k != key:
            cur, key = {}, k
        cur[ext] = tf.extractfile(m).read()
        if '.jpg' in cur and '.json' in cur:
            cap = (json.loads(cur['.json']).get('original_caption') or '').strip()
            if cap:
                yield cur['.jpg'], f'rc{i:03d}_{os.path.basename(k)}', '', cap
            cur = {}


def coco_rows(fh, i):
    pf = pq.ParquetFile(fh)
    for g in range(pf.metadata.num_row_groups):
        for r in pf.read_row_group(g, columns=['image', 'cocoid', 'caption']).to_pylist():
            cap = (r['caption'] or '').strip()
            im = r['image']
            if cap and im:
                yield (im['bytes'] if isinstance(im, dict) else im), f"coco{r['cocoid']}", '', cap


def one(job):
    src, repo, i, fname, out = job
    global fs
    if fs is None:
        fs = HfFileSystem()
    dst = os.path.join(out, f'train-{i:05d}.parquet')
    if os.path.exists(dst):
        return i, 0
    gen = redcaps_rows if src == 'redcaps' else coco_rows
    for attempt in range(8):
        try:
            n, buf = 0, []
            with fs.open(f'datasets/{repo}/{fname}', block_size=8 << 20) as fh, \
                    pq.ParquetWriter(dst + '.tmp', SCHEMA) as w:
                for row in gen(fh, i):
                    buf.append(row)
                    if len(buf) == GROUP:
                        w.write_table(pa.Table.from_pylist(
                            [dict(zip(SCHEMA.names, r)) for r in buf], SCHEMA), GROUP)
                        n, buf = n + len(buf), []
                if buf:
                    w.write_table(pa.Table.from_pylist(
                        [dict(zip(SCHEMA.names, r)) for r in buf], SCHEMA), GROUP)
                    n += len(buf)
            os.replace(dst + '.tmp', dst)
            return i, n
        except Exception as e:
            print(f'shard {i} attempt {attempt}: {e!r}', flush=True)
            time.sleep(min(300, 15 * 2 ** attempt))
    return i, -1


if __name__ == '__main__':
    import multiprocessing
    ap = argparse.ArgumentParser()
    ap.add_argument('source', choices=sorted(REPOS))
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=8)
    args = ap.parse_args()
    repo = REPOS[args.source]
    os.makedirs(args.out, exist_ok=True)
    ext = '.tar' if args.source == 'redcaps' else '.parquet'
    files = sorted(s.rfilename for s in HfApi().dataset_info(repo).siblings
                   if s.rfilename.endswith(ext))
    todo = [(args.source, repo, i, f, args.out) for i, f in enumerate(files)
            if not os.path.exists(os.path.join(args.out, f'train-{i:05d}.parquet'))]
    print(f'{repo}: {len(files)} shards, {len(files) - len(todo)} done, {len(todo)} to go',
          flush=True)
    # fresh worker processes per wave, as in exp/img_prep.py (long-lived pools leak host RAM)
    t0, rows, done, failed = time.time(), 0, 0, []
    wave = 4 * args.workers
    for w0 in range(0, len(todo), wave):
        with cf.ProcessPoolExecutor(args.workers,
                                    mp_context=multiprocessing.get_context('spawn')) as ex:
            for i, n in ex.map(one, todo[w0:w0 + wave]):
                done += 1
                if n < 0:
                    failed.append(i)
                rows += max(n, 0)
        print(f'{done}/{len(todo)} shards, {rows} new rows, {time.time() - t0:.0f}s', flush=True)
    print(f'DONE {done} shards, {rows} new rows, failed {failed}, {time.time() - t0:.0f}s')
    sys.exit(1 if failed else 0)
