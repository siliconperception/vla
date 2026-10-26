"""BabyLM 2026 Strict (100M words, already preprocessed upstream by babylm_data_preprocessing + detox) ->
one shuffled parquet of documents for vla.py's 'babylm' corpus.

usage: python exp/babylm_prep.py [--src DIR] [--dst /data/babylm2026_docs] [--chunk 1000]

Per file (the hub copy's own '= = = name = = =' lines mark transcripts, books, articles and films):
  childes        one document per transcript; '*MOT:<tab>' speaker codes -> 'Mother: ' (common codes named,
                 the rest dropped); %add/%int/%flo tiers and '[...]' comment lines dropped; xxx/yyy/www
                 (unintelligible) removed
  switchboard    no boundaries: 'A:<tab>' -> 'A: ', cut into chunks
  bnc_spoken     no boundaries (one stray header): cut into chunks
  open_subtitles one document per film; all-caps lines -> sentence case
  gutenberg      one document per book (title line 'PGnnnn' dropped)
  simple_wiki    one document per article, the title as its first line
Any document over --chunk words is cut at line boundaries into pieces of about --chunk words, so documents
are about the size of FineWeb's and the state resets about as often. Lines join with newlines."""
import argparse, glob, os, random, re
import pyarrow as pa, pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument('--src', default=None)
ap.add_argument('--dst', default='/data/babylm2026_docs')
ap.add_argument('--chunk', type=int, default=1000, help='words per piece of a long document')
ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
src = a.src or glob.glob('/data/huggingface/hub/datasets--BabyLM-community--BabyLM-2026-Strict/snapshots/*/')[0]

SEP = re.compile(r'^= = = (.*) = = =$')
SPEAKER = {'MOT': 'Mother', 'CHI': 'Child', 'FAT': 'Father', 'INV': 'Investigator', 'EXP': 'Experimenter',
           'TEA': 'Teacher', 'PAR': 'Parent', 'PAR1': 'Parent', 'SIS': 'Sister', 'BRO': 'Brother',
           'GMA': 'Grandma', 'GPA': 'Grandpa', 'DAD': 'Dad', 'MOM': 'Mom', 'NAN': 'Nanny', 'GRA': 'Grandma',
           'AUN': 'Aunt', 'UNC': 'Uncle', 'BAB': 'Baby'}
CHAT = re.compile(r'^\*([A-Z0-9]+):\t?(.*)$')
UNINT = re.compile(r'\b(?:xxx|yyy|www)\b\s?')


def docs_of(lines, split_on_sep):
    """[(title, [lines])]; with split_on_sep False the whole file is one document."""
    out, title, cur = [], None, []
    for l in lines:
        m = SEP.match(l) if split_on_sep else None
        if m:
            if cur:
                out.append((title, cur))
            title, cur = m.group(1), []
        elif l.strip():
            cur.append(l.rstrip())
    if cur:
        out.append((title, cur))
    return out


def sentence_case(l):
    if not re.search('[A-Z]', l) or l.upper() != l:
        return l
    s = l.lower()
    s = re.sub(r"\bi\b", 'I', s)
    s = re.sub(r"\bi'", "I'", s)
    return re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), s)


def childes(l):
    if l.startswith('%') or l.startswith('['):
        return None
    m = CHAT.match(l)
    if not m:
        return l
    who, text = m.groups()
    text = UNINT.sub('', text).strip()
    if not text or text in '.?!':
        return None
    return f'{SPEAKER[who]}: {text}' if who in SPEAKER else text


def chunks(lines, n):
    """Pieces of about n words at line boundaries; a tail under n/4 words joins the piece before it."""
    out, piece, words = [], [], 0
    for l in lines:
        piece.append(l)
        words += len(l.split())
        if words >= n:
            out.append(piece)
            piece, words = [], 0
    if piece:
        if out and words < n // 4:
            out[-1] += piece
        else:
            out.append(piece)
    return out


rows = []
for path in sorted(glob.glob(os.path.join(src, '*.train.txt'))):
    name = os.path.basename(path).split('.')[0]
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    docs = docs_of(lines, name in ('childes', 'open_subtitles', 'gutenberg', 'simple_wiki'))
    n_doc = n_word = 0
    for title, ls in docs:
        if name == 'childes':
            ls = [x for x in map(childes, ls) if x]
        elif name == 'switchboard':
            ls = [re.sub(r'^([AB]):\t', r'\1: ', x) for x in ls]
        elif name == 'open_subtitles':
            ls = [sentence_case(x) for x in ls]
        elif name == 'simple_wiki' and title:
            ls = [title] + ls
        for piece in chunks(ls, a.chunk):
            text = '\n'.join(piece).strip()
            if text:
                rows.append((text, name))
                n_doc += 1
                n_word += len(text.split())
    print(f'{name:15s} {len(docs):7d} source documents -> {n_doc:7d} documents, {n_word / 1e6:6.2f}M words', flush=True)

random.Random(a.seed).shuffle(rows)
os.makedirs(a.dst, exist_ok=True)
out = os.path.join(a.dst, 'train.parquet')
pq.write_table(pa.table({'text': [r[0] for r in rows], 'source': [r[1] for r in rows]}), out, row_group_size=4096)
print(f'{len(rows)} documents, {sum(len(r[0].split()) for r in rows) / 1e6:.2f}M words -> {out}')
