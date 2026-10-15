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

fs = None


def one(job):
    i, fname, out, groups = job
    global fs
    if fs is None:
        fs = HfFileSystem()
    dst = os.path.join(out, f'train-{i:05d}.parquet')
    if os.path.exists(dst):
        return i, 0
    for attempt in range(8):
        try:
            with fs.open(f'datasets/{REPO}/{fname}', block_size=8 << 20) as fh:
                pf = pq.ParquetFile(fh)
                G = pf.metadata.num_row_groups
                picks = sorted({min(G - 1, round((j + 0.5) * G / groups - 0.5))
                                for j in range(groups)})
                t = pa.concat_tables([pf.read_row_group(g, columns=COLS) for g in picks])
            pq.write_table(t, dst + '.tmp', row_group_size=100)
            os.replace(dst + '.tmp', dst)
            return i, t.num_rows
        except Exception as e:
            print(f'shard {i} attempt {attempt}: {e!r}', flush=True)
            time.sleep(min(300, 15 * 2 ** attempt))
    return i, -1


if __name__ == '__main__':
    import multiprocessing
    ap = argparse.ArgumentParser()
    ap.add_argument('--groups', type=int, default=2, help='row groups sampled per shard')
    ap.add_argument('--out', default='/data/imagenet21k_recap')
    ap.add_argument('--workers', type=int, default=32)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    files = sorted(s.rfilename for s in HfApi().dataset_info(REPO).siblings
                   if s.rfilename.endswith('.parquet'))
    # Worker PROCESSES, in waves of a fresh pool per 8 shards per worker: a long-lived thread
    # pool grew to 58 GB of host RAM (HfFileSystem/pyarrow buffers) and was OOM-killed, and
    # max_tasks_per_child deadlocks in Python 3.12's ProcessPoolExecutor.
    todo = [(i, f, args.out, args.groups) for i, f in enumerate(files)
            if not os.path.exists(os.path.join(args.out, f'train-{i:05d}.parquet'))]
    print(f'{len(files) - len(todo)} shards already done, {len(todo)} to go', flush=True)
    t0, rows, done, failed = time.time(), 0, 0, []
    wave = 8 * args.workers
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
