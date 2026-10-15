#!/usr/bin/env python3
"""Sample gmongaras/Imagenet21K_Recaption into a local directory, a few row groups from EVERY shard.

The repo is 7,770 parquet shards (~0.5 GB, ~1,691 rows, 17 row groups of 100) sorted by
WordNet synset id, so each shard holds only 2-8 classes and skipping a shard drops those
classes entirely. Reading --groups evenly spaced row groups per shard by HTTP range request
gives a stratified sample of every class at a fraction of the 3.9 TB.

Output: <out>/train-NNNNN.parquet, one per source shard (image bytes, id, class, recaption).
Resumable: existing outputs are skipped, so rerunning with a larger --groups adds nothing
to finished shards -- use a new --out for a larger sample.

    python exp/img_prep.py --groups 2 --out /data/imagenet21k_recap --workers 32
"""
import argparse
import concurrent.futures as cf
import os
import sys
import time

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfApi, HfFileSystem

REPO = 'gmongaras/Imagenet21K_Recaption'
COLS = ['image', 'id', 'class', 'recaption']

ap = argparse.ArgumentParser()
ap.add_argument('--groups', type=int, default=2, help='row groups sampled per shard')
ap.add_argument('--out', default='/data/imagenet21k_recap')
ap.add_argument('--workers', type=int, default=32)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

files = sorted(s.rfilename for s in HfApi().dataset_info(REPO).siblings
               if s.rfilename.endswith('.parquet'))
fs = HfFileSystem()


def one(i):
    dst = os.path.join(args.out, f'train-{i:05d}.parquet')
    if os.path.exists(dst):
        return i, 0
    for attempt in range(8):
        try:
            pf = pq.ParquetFile(fs.open(f'datasets/{REPO}/{files[i]}', block_size=8 << 20))
            G = pf.metadata.num_row_groups
            picks = sorted({min(G - 1, round((j + 0.5) * G / args.groups - 0.5))
                            for j in range(args.groups)})
            t = pa.concat_tables([pf.read_row_group(g, columns=COLS) for g in picks])
            pq.write_table(t, dst + '.tmp', row_group_size=100)
            os.replace(dst + '.tmp', dst)
            return i, t.num_rows
        except Exception as e:
            print(f'shard {i} attempt {attempt}: {e!r}', flush=True)
            time.sleep(min(300, 15 * 2 ** attempt))
    return i, -1


t0, rows, done, failed = time.time(), 0, 0, []
with cf.ThreadPoolExecutor(args.workers) as ex:
    for i, n in ex.map(one, range(len(files))):
        done += 1
        if n < 0:
            failed.append(i)
        rows += max(n, 0)
        if done % 100 == 0:
            print(f'{done}/{len(files)} shards, {rows} new rows, {time.time() - t0:.0f}s',
                  flush=True)
print(f'DONE {done} shards, {rows} new rows, failed {failed}, {time.time() - t0:.0f}s')
sys.exit(1 if failed else 0)
