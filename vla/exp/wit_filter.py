#!/usr/bin/env python3
"""Copy the rows of the local WIT corpus that pass both quality filters (scores from
exp/wit_score.py) into a new corpus with the same layout (one parquet per source shard, row
groups of 100, all columns, ids unchanged so vla.py's id-hash held-out split is unchanged):

    edu  >= --min_edu   (fineweb-edu classifier on caption + Gemini description)
    clip >= --min_clip  (CLIP ViT-L/14 image vs human caption; rows without one are dropped)

    python exp/wit_filter.py --min_edu 2.5 --min_clip 0.25 --out /data/witq
"""
import argparse
import os

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='/data/wit_1m_recap')
    ap.add_argument('--scores', default='/data/wit_1m_scores')
    ap.add_argument('--out', required=True)
    ap.add_argument('--min_edu', type=float, required=True)
    ap.add_argument('--min_clip', type=float, required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    files = sorted(f for f in os.listdir(args.src) if f.endswith('.parquet'))
    tot = kept = 0
    for f in files:
        s = pq.read_table(os.path.join(args.scores, f))
        ok = (np.nan_to_num(s['edu'].to_numpy(), nan=-1e9) >= args.min_edu) & \
             (np.nan_to_num(s['clip'].to_numpy(), nan=-1e9) >= args.min_clip)
        keep = set(np.asarray(s['id'])[ok].tolist())
        t = pq.read_table(os.path.join(args.src, f))
        t = t.filter(pc.is_in(t['id'], value_set=pa.array(sorted(keep), type=t['id'].type)))
        dst = os.path.join(args.out, f)
        pq.write_table(t, dst + '.tmp', row_group_size=100)
        os.replace(dst + '.tmp', dst)
        tot, kept = tot + len(s), kept + t.num_rows
        print(f'{f}: {t.num_rows}/{len(s)}', flush=True)
    print(f'DONE kept {kept}/{tot} ({kept / max(tot, 1):.1%})')
