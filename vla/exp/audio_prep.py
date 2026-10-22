#!/usr/bin/env python3
"""Clean soundtracks for the captioned-video corpus: a sidecar to exp/video_prep.py's
/data/finevideo_feat, one parquet per source shard with the same file name, columns

  id         source video id (as in finevideo_feat: original_video_filename without extension)
  sr         sample rate (SR)
  n_samples  samples of mono audio (0 when the video has no audio)
  flac       FLAC bytes, mono 16-bit at SR, from t=0 of the mp4 (aligned with frames/codes)

vla.py joins it to finevideo_feat by id (--audio_encoder quartznet). CPU only (ffmpeg); the
download is the bottleneck. Resumable like video_prep.py: finished shards are skipped, each is
written to .tmp and renamed, the downloaded shard is deleted once processed.

    python exp/audio_prep.py --out /data/finevideo_audio --workers 6 --stage ~/fa_stage
"""
import argparse
import io
import json
import multiprocessing as mp
import os
import subprocess
import sys
import tempfile
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import soundfile as sf

SR = 16000
GROUP = 1                    # one video per row group: the trainer reads single videos
SCHEMA = pa.schema([('id', pa.string()), ('sr', pa.int32()), ('n_samples', pa.int64()),
                    ('flac', pa.binary())])
FV_REPO = 'HuggingFaceFV/finevideo'


def flac_of(mp4_bytes):
    """(n_samples, FLAC bytes) of the mono SR soundtrack of one mp4 given as bytes."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', dir='/dev/shm') as f:
        f.write(mp4_bytes)
        f.flush()
        a = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', f.name, '-vn',
                            '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                           capture_output=True).stdout
    a = np.frombuffer(a, '<i2')
    if len(a) == 0:
        return 0, b''
    buf = io.BytesIO()
    sf.write(buf, a, SR, format='FLAC', subtype='PCM_16')
    return len(a), buf.getvalue()


def fv_shard(args):
    """Download one finevideo shard, extract its soundtracks, delete the download."""
    fname, out_dir, stage = args
    from huggingface_hub import hf_hub_download
    out = os.path.join(out_dir, os.path.basename(fname))
    if os.path.exists(out):
        return fname, 0, 0.0
    t0 = time.time()
    tmp_dir = stage or os.path.join(out_dir, '.download')
    p = hf_hub_download(FV_REPO, fname, repo_type='dataset', local_dir=tmp_dir)
    rows, pf = [], pq.ParquetFile(p)
    for g in range(pf.num_row_groups):
        for r in pf.read_row_group(g, columns=['mp4', 'json']).to_pylist():
            j = r['json'] or {}
            if isinstance(j, str):
                j = json.loads(j)
            vid = os.path.splitext(j.get('original_video_filename') or '')[0]
            try:
                n, flac = flac_of(r['mp4'])
            except Exception as e:                 # a broken video: skip it, keep the shard
                print(f'{fname}: {vid}: {e!r}'[:500], flush=True)
                continue
            rows.append(dict(id=vid, sr=SR, n_samples=n, flac=flac))
    tmp = out + '.tmp'
    with pq.ParquetWriter(tmp, SCHEMA) as w:
        for i in range(0, len(rows), GROUP):
            w.write_table(pa.Table.from_pylist(rows[i:i + GROUP], schema=SCHEMA))
    os.replace(tmp, out)
    os.remove(p)
    return fname, len(rows), time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--limit', type=int, default=0, help='first N source shards only')
    ap.add_argument('--stage', default=None,
                    help='download shards here instead of <out>/.download; each is deleted '
                         'once processed')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    from huggingface_hub import HfApi
    files = sorted(f for f in HfApi().list_repo_files(FV_REPO, repo_type='dataset')
                   if f.startswith('data/') and f.endswith('.parquet'))
    files = files[:args.limit] if args.limit else files
    t0, n = time.time(), 0
    with mp.get_context('spawn').Pool(args.workers, maxtasksperchild=1) as pool:
        jobs = [(f, args.out, args.stage) for f in files]
        for k, (name, rows, dt) in enumerate(pool.imap_unordered(fv_shard, jobs)):
            n += rows
            print(f'[{k + 1}/{len(jobs)}] {name}: {rows} videos in {dt:.0f}s '
                  f'(total {n} videos, {(time.time() - t0) / 3600:.2f} h)', flush=True)


if __name__ == '__main__':
    sys.exit(main())
