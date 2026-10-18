#!/usr/bin/env python3
"""Precompute captioned-video corpora into the local parquet layout vla.py reads for video:
one parquet per source shard, row groups of GROUP videos, columns

  id        source video id
  category  content category ('' if none)
  duration  seconds
  fps       frame rate of `frames` (FPS)
  frames    list of JPEG bytes, one per 1/FPS s from t=0 (ffmpeg fps filter), short side 224
  codes     Kyutai Mimi codes, int16 [32, n_codes] row-major bytes, 12.5 Hz (80 ms frames)
            of the mono 24 kHz soundtrack; all-zero length when the video has no audio
  n_codes   frames of codes
  events    JSON [[start_s, end_s, kind, text], ...] in time order: the caption timeline
            ('act' scene activity, 'say' speech transcript segment, 'cap' clip caption)
  json      the source metadata (finevideo) or '' -- kept for later uses (clocked text)

Corpora:
  finevideo  HuggingFaceFV/finevideo (gated, CC-BY): 43,751 YouTube videos, 1,357 shards.
             events = scene activities + timecoded transcript segments.
  valor      UnFaZeD07/VALOR-32K: 32K 10 s AudioSet clips with one human audio-visual
             caption each (MIT). Splits train/val/test from its annotation files; written
             as <split>-NNNNN.parquet.

The frozen image encoder still runs live in vla.py (2048x7x7 grids at 2 fps would be ~5 TB);
what is precomputed here is the expensive part of the data path: video decode, resampling,
resizing and Mimi encoding. Resumable: finished outputs are skipped; each output is written
to .tmp and renamed when done.

    python exp/video_prep.py finevideo --out /data/finevideo_feat --workers 6 --stage ~/fv_stage
    python exp/video_prep.py valor --out /data/valor_feat --workers 6
"""
import argparse
import json
import multiprocessing as mp
import os
import subprocess
import sys
import tarfile
import tempfile
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

FPS = 2.0
SIDE = 224
SR = 24000
MIMI_HOP = 1920              # samples per Mimi frame (24 kHz / 12.5 Hz)
CHUNK = 375 * MIMI_HOP       # Mimi encodes 30 s at a time (bounded GPU memory)
GROUP = 8
SCHEMA = pa.schema([('id', pa.string()), ('category', pa.string()), ('duration', pa.float32()),
                    ('fps', pa.float32()), ('frames', pa.list_(pa.binary())),
                    ('codes', pa.binary()), ('n_codes', pa.int32()), ('events', pa.string()),
                    ('json', pa.string())])
FV_REPO = 'HuggingFaceFV/finevideo'
VALOR_REPO = 'UnFaZeD07/VALOR-32K'

_mimi = None


def mimi():
    global _mimi
    if _mimi is None:
        import torch
        from transformers import MimiModel
        _mimi = MimiModel.from_pretrained('kyutai/mimi', dtype=torch.float32).cuda().eval()
    return _mimi


def frames_of(path):
    """JPEG bytes per 1/FPS s, short side SIDE (aspect kept)."""
    vf = f"fps={FPS:g},scale='if(gt(iw,ih),-2,{SIDE})':'if(gt(iw,ih),{SIDE},-2)'"
    r = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '4', '-i', path, '-an', '-vf', vf,
                        '-q:v', '3', '-f', 'image2pipe', '-c:v', 'mjpeg', '-'],
                       capture_output=True).stdout
    starts = []
    k = r.find(b'\xff\xd8\xff')
    while k >= 0:
        starts.append(k)
        k = r.find(b'\xff\xd8\xff', k + 3)
    return [r[a:b] for a, b in zip(starts, starts[1:] + [len(r)])]


def codes_of(path):
    """Mimi codes int16 [32, T] of the mono 24 kHz soundtrack ([32, 0] if none)."""
    import torch
    a = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(SR),
                        '-f', 'f32le', '-'], capture_output=True).stdout
    a = np.frombuffer(a, np.float32)
    if len(a) < MIMI_HOP:
        return np.zeros((32, 0), np.int16)
    a = a[:len(a) // MIMI_HOP * MIMI_HOP]
    out = []
    with torch.no_grad():
        for s in range(0, len(a), CHUNK):
            x = torch.from_numpy(a[s:s + CHUNK].copy()).cuda()[None, None]
            out.append(mimi().encode(x, num_quantizers=32).audio_codes[0].short().cpu().numpy())
    torch.cuda.empty_cache()                       # leave the GPU to the trainer
    return np.concatenate(out, 1)


def media(mp4_bytes):
    """(frames, codes) of one video given as bytes (written to /dev/shm for seeking)."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', dir='/dev/shm') as f:
        f.write(mp4_bytes)
        f.flush()
        return frames_of(f.name), codes_of(f.name)


def _secs(ts):
    """'HH:MM:SS.mmm' (or MM:SS, or a number) -> seconds; None if unparseable."""
    try:
        if isinstance(ts, (int, float)):
            return float(ts)
        s = 0.0
        for p in str(ts).strip().split(':'):
            s = s * 60 + float(p)
        return s
    except ValueError:
        return None


def fv_events(j, dur):
    """[[start, end, kind, text]] from a finevideo record: scene activities + transcript."""
    ev = []
    for sc in (j.get('content_metadata') or {}).get('scenes') or []:
        for a in sc.get('activities') or []:
            ts = a.get('timestamp') or {}
            s, e = _secs(ts.get('start_timestamp')), _secs(ts.get('end_timestamp'))
            txt = (a.get('description') or '').strip()
            if txt and s is not None:
                ev.append([s, e if e is not None and e > s else s, 'act', txt])
    for seg in j.get('timecoded_text_to_speech') or []:
        s, e = _secs(seg.get('start')), _secs(seg.get('end'))
        txt = (seg.get('text') or '').strip()
        if txt and s is not None:
            ev.append([s, e if e is not None and e > s else s, 'say', txt])
    ev = [[min(max(s, 0.0), dur), min(max(e, 0.0), dur), k, t] for s, e, k, t in ev]
    ev.sort(key=lambda x: (x[0], x[2] != 'act'))     # an activity before speech at a tie
    return ev


def _write(rows, out):
    tmp = out + '.tmp'
    with pq.ParquetWriter(tmp, SCHEMA) as w:
        for i in range(0, len(rows), GROUP):
            w.write_table(pa.Table.from_pylist(rows[i:i + GROUP], schema=SCHEMA))
    os.replace(tmp, out)


def _row(vid, cat, dur, frames, codes, events, js):
    return dict(id=vid, category=cat, duration=float(dur), fps=FPS, frames=frames,
                codes=codes.astype('<i2').tobytes(), n_codes=codes.shape[1],
                events=json.dumps(events), json=js)


def fv_shard(args):
    """Download one finevideo shard, precompute it, delete the download."""
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
        for r in pf.read_row_group(g).to_pylist():
            j = r['json'] or {}
            try:
                frames, codes = media(r['mp4'])
            except Exception as e:                 # a broken video: skip it, keep the shard
                print(f'{fname}: {j.get("original_video_filename")}: {e!r}'[:500], flush=True)
                if 'CUDA' in repr(e):              # a sticky CUDA error poisons the process:
                    return fname + ' FAILED (CUDA error; rerun to retry)', 0, time.time() - t0
                continue
            dur = float(j.get('duration_seconds') or len(frames) / FPS)
            vid = os.path.splitext(j.get('original_video_filename') or '')[0]
            rows.append(_row(vid, j.get('content_parent_category') or '', dur, frames, codes,
                             fv_events(j, dur), json.dumps(j)))
    _write(rows, out)
    os.remove(p)
    return fname, len(rows), time.time() - t0


def valor_part(args):
    """Precompute one list of (video path, id, caption) VALOR clips into `out`."""
    items, out = args
    if os.path.exists(out):
        return out, 0, 0.0
    t0 = time.time()
    rows = []
    for path, vid, cap in items:
        try:
            with open(path, 'rb') as f:
                frames, codes = media(f.read())
        except Exception as e:
            print(f'{vid}: {e}', flush=True)
            continue
        dur = len(frames) / FPS
        rows.append(_row(vid, '', dur, frames, codes, [[0.0, dur, 'cap', cap.strip()]], ''))
    _write(rows, out)
    return out, len(rows), time.time() - t0


def run_pool(fn, jobs, workers):
    t0, n = time.time(), 0
    ctx = mp.get_context('spawn')                  # CUDA in each worker
    # a fresh process per job, so a CUDA fault (e.g. another process crashing the GPU) costs
    # one job, which is then not written and is redone by the next run
    with ctx.Pool(workers, maxtasksperchild=1) as pool:
        for k, (name, rows, dt) in enumerate(pool.imap_unordered(fn, jobs)):
            n += rows
            print(f'[{k + 1}/{len(jobs)}] {name}: {rows} videos in {dt:.0f}s '
                  f'(total {n} videos, {(time.time() - t0) / 3600:.2f} h)', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus', choices=['finevideo', 'valor'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--limit', type=int, default=0, help='first N source shards / parts only')
    ap.add_argument('--stage', default=None,
                    help='finevideo: download shards here (e.g. a fast local disk) instead of '
                         '<out>/.download; each is deleted once processed')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.corpus == 'finevideo':
        from huggingface_hub import HfApi
        files = sorted(f for f in HfApi().list_repo_files(FV_REPO, repo_type='dataset')
                       if f.startswith('data/') and f.endswith('.parquet'))
        files = files[:args.limit] if args.limit else files
        run_pool(fv_shard, [(f, args.out, args.stage) for f in files], args.workers)
    else:
        from huggingface_hub import hf_hub_download
        import zipfile
        dl = os.path.join(args.out, '.download')
        ann = hf_hub_download(VALOR_REPO, 'VALOR-32K-annotations.zip', repo_type='dataset',
                              local_dir=dl)
        vids = os.path.join(dl, 'videos')
        if not os.path.isdir(vids):
            tar = hf_hub_download(VALOR_REPO, 'VALOR-32K-videos.tar', repo_type='dataset',
                                  local_dir=dl)
            os.makedirs(vids + '.tmp', exist_ok=True)
            with tarfile.open(tar) as tf:
                for m in tf:
                    if m.isfile() and m.name.endswith('.mp4'):
                        m.name = os.path.basename(m.name)
                        tf.extract(m, vids + '.tmp')
            os.replace(vids + '.tmp', vids)
            os.remove(tar)
        have = {os.path.splitext(f)[0]: os.path.join(vids, f) for f in os.listdir(vids)}
        jobs = []
        with zipfile.ZipFile(ann) as z:
            for split in ('test', 'val', 'train'):
                name = next(n for n in z.namelist() if n.endswith(f'desc_{split}.json'))
                items = [(have[d['video_id']], d['video_id'], d['desc'])
                         for d in json.loads(z.read(name)) if d['video_id'] in have]
                print(f'{split}: {len(items)} clips with video', flush=True)
                for k, i in enumerate(range(0, len(items), 500)):
                    jobs.append((items[i:i + 500],
                                 os.path.join(args.out, f'{split}-{k:05d}.parquet')))
        jobs = jobs[:args.limit] if args.limit else jobs
        run_pool(valor_part, jobs, args.workers)


if __name__ == '__main__':
    sys.exit(main())
