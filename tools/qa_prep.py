"""instruction-pretrain/general-instruction-augmented-corpora (RefinedWeb pages, each with question/answer
pairs synthesized from it; ODC-BY) -> shuffled parquet of examples for vla.py's 'qaipt' corpus.

usage: python tools/qa_prep.py [--src SNAPSHOT_DIR] [--dst $VLA_DATA/qa_ipt] [--files 20]

Each source line is a JSON list of {"context", "QA_list": [{"Q", "A"}], ...}; every context is one example:

    <page text>

    Q: <question>
    A: <answer>

    Q: ...

Pairs with an empty question or answer are dropped, and so are repeated questions (case-insensitive); a page
left with no pair is dropped. Text mangled by a UTF-8 -> cp1252 round trip ("Youâ€™ll") is repaired where it
decodes cleanly. The rows are shuffled together and written as --files parquet files of a 'text' and an
'n_qa' column."""
import argparse, glob, json, os, random
import pyarrow as pa, pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument('--src', default=None)
ap.add_argument('--dst', default=os.path.join(os.environ.get('VLA_DATA', '/data'), 'qa_ipt'))
ap.add_argument('--files', type=int, default=20)
ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
home = os.environ.get('HF_HOME') or os.path.expanduser('~/.cache/huggingface')
src = a.src or glob.glob(os.path.join(home, 'hub', 'datasets--instruction-pretrain--general-instruction-'
                                               'augmented-corpora', 'snapshots', '*'))[0]


def fix(s):
    """Undo a UTF-8 -> cp1252 mis-decoding when the whole string round-trips cleanly."""
    if 'â€' not in s and 'Ã' not in s:
        return s
    try:
        return s.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


rows, n_pages, n_drop, n_fix = [], 0, 0, 0
shards = sorted(glob.glob(os.path.join(src, 'part-*', 'shard', '*.txt')))
for k, path in enumerate(shards):
    for line in open(path, encoding='utf-8', errors='replace'):
        if not line.strip():
            continue
        for ex in json.loads(line):
            n_pages += 1
            ctx = ex.get('context', '').strip()
            ctx2 = fix(ctx)
            n_fix += ctx2 != ctx
            seen, pairs = set(), []
            for qa in ex.get('QA_list') or []:
                q, ans = fix((qa.get('Q') or '').strip()), fix((qa.get('A') or '').strip())
                if q and ans and q.lower() not in seen:
                    seen.add(q.lower())
                    pairs.append(f'Q: {q}\nA: {ans}')
            if not ctx2 or not pairs:
                n_drop += 1
                continue
            rows.append((ctx2 + '\n\n' + '\n\n'.join(pairs), len(pairs)))
    if (k + 1) % 20 == 0:
        print(f'{k + 1}/{len(shards)} shards, {len(rows)} examples', flush=True)

random.Random(a.seed).shuffle(rows)
os.makedirs(a.dst, exist_ok=True)
per = -(-len(rows) // a.files)
for f in range(a.files):
    part = rows[f * per:(f + 1) * per]
    pq.write_table(pa.table({'text': [r[0] for r in part], 'n_qa': [r[1] for r in part]}),
                   os.path.join(a.dst, f'train-{f:03d}.parquet'), row_group_size=4096)
words = sum(len(r[0].split()) for r in rows)
print(f'{len(shards)} shards: {n_pages} pages, {n_drop} dropped (no text or no pair), {n_fix} re-decoded; '
      f'{len(rows)} examples, {sum(r[1] for r in rows)} Q/A pairs, {words / 1e6:.1f}M words -> {a.dst}')
