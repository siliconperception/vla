"""BabyLM 2026 Strict (100M words, already preprocessed upstream by babylm_data_preprocessing + detox) ->
one shuffled parquet of documents for vla.py's 'babylm' corpus.

usage: python exp/babylm_prep.py [--src DIR] [--dst /data/babylm2026_nat] [--chunk 0] [--stream_words 500000] [--seq 0]
                                [--files '*.train.txt']

Documents are the source's own: the hub copy's '= = = name = = =' lines mark transcripts, books, articles
and films (in every file; bnc_spoken's one marks a CHILDES transcript appended at its end), and a file
with no marks is one document. No boundaries are added (user, 2026-10-26). Formatting per file:
  childes        (and any 'childes/...' document) '*MOT:<tab>' speaker codes -> 'Mother: ' (common codes named,
                 the rest dropped); %add/%int/%flo tiers and '[...]' comment lines dropped; xxx/yyy/www
                 (unintelligible) removed
  switchboard    'A:<tab>' -> 'A: ' (no marks: the whole file is one document). A run of over _SWB_RUN
                 'A:<tab>'/'B:<tab>' lines inside another file is Switchboard too, cut out as its own document:
                 simple_wiki.train.txt lines 512259-642735 (130,477 lines, ~1.08M words) are Switchboard
                 conversations appended to the Saramago article with no mark
  bnc_spoken     as is (no marks before the appended transcript: one 7.6M-word document)
  open_subtitles all-caps lines -> sentence case
  gutenberg      title line 'PGnnnn' dropped
  simple_wiki    the article title as its first line
Unmarked stretches (a 'document' over --stream_words words: BNC, nearly all of OpenSubtitles, one Simple
Wiki stretch; the largest book is 266K words) are written as plain text to DST/streams/<name>.txt (v474's
lanes, since reverted); the rest go to DST/docs/train.parquet (corpus 'babylm'). Lines join with newlines.
--chunk N > 0 (off by default) instead cuts documents over N words into pieces at line boundaries, all to
DST/train.parquet (v473's 'babylm1k' data: --chunk 1000 --stream_words 0). --seq S > 0 with --chunk keeps
a document's pieces in order: up to S consecutive pieces make one row, the pieces joined by '\x1e'
(vla.py reads them back to back, each an example of its own; corpus 'babylmseq': --dst /data/babylm2026_seq
--chunk 1000 --stream_words 0 --seq 16). The official dev split, for vla.py's eval-only corpus 'babylmdev':
--src <BabyLM-dev snapshot> --files '*.dev' --dst /data/babylm2026_dev --chunk 1000 --stream_words 0."""
import argparse, glob, os, random, re
import pyarrow as pa, pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument('--src', default=None)
ap.add_argument('--dst', default='/data/babylm2026_nat')
ap.add_argument('--stream_words', type=int, default=500000, help='a longer unmarked document is a stream (0 = none)')
ap.add_argument('--chunk', type=int, default=0, help='cut documents into pieces of about N words (0 = never)')
ap.add_argument('--seq', type=int, default=0, help='with --chunk: up to S consecutive pieces per row, in order')
ap.add_argument('--files', default='*.train.txt', help='source file pattern (the dev split: *.dev)')
ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
src = a.src or glob.glob('/data/huggingface/hub/datasets--BabyLM-community--BabyLM-2026-Strict/snapshots/*/')[0]

SEP = re.compile(r'^= = = (.*) = = =$')
SPEAKER = {'MOT': 'Mother', 'CHI': 'Child', 'FAT': 'Father', 'INV': 'Investigator', 'EXP': 'Experimenter',
           'TEA': 'Teacher', 'PAR': 'Parent', 'PAR1': 'Parent', 'SIS': 'Sister', 'BRO': 'Brother',
           'GMA': 'Grandma', 'GPA': 'Grandpa', 'DAD': 'Dad', 'MOM': 'Mom', 'NAN': 'Nanny', 'GRA': 'Grandma',
           'AUN': 'Aunt', 'UNC': 'Uncle', 'BAB': 'Baby'}
CHAT = re.compile(r'^\*([A-Z0-9]+):\t?(.*)$')
SWB = re.compile(r'^[AB]:\t')
_SWB_RUN = 50                     # consecutive Switchboard turns that make a run (not a quoted exchange)
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


def split_switchboard(title, ls):
    """[(title, src or None, lines)]: runs of over _SWB_RUN Switchboard turns cut out as ('switchboard', run)."""
    out, start, k = [], 0, 0
    while k < len(ls):
        if SWB.match(ls[k]):
            j = k
            while j < len(ls) and SWB.match(ls[j]):
                j += 1
            if j - k > _SWB_RUN:
                if k > start:
                    out.append((title, None, ls[start:k]))
                out.append((None, 'switchboard', ls[k:j]))
                start = j
            k = j
        else:
            k += 1
    if start < len(ls):
        out.append((title, None, ls[start:]))
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


rows, streams = [], []
for path in sorted(glob.glob(os.path.join(src, a.files))):
    name = os.path.basename(path).split('.')[0]
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    docs = docs_of(lines, True)
    n_doc = n_word = 0
    parts = [p for t, ls in docs for p in (split_switchboard(t, ls) if name != 'switchboard' else [(t, None, ls)])]
    for title, src_name, ls in parts:
        src_name = src_name or ('childes' if (title or '').startswith('childes/') else name)
        if src_name == 'childes':
            ls = [x for x in map(childes, ls) if x]
        elif src_name == 'switchboard':
            ls = [re.sub(r'^([AB]):\t', r'\1: ', x) for x in ls]
        elif src_name == 'open_subtitles':
            ls = [sentence_case(x) for x in ls]
        elif src_name == 'simple_wiki' and title:
            ls = [title] + ls
        if a.stream_words and sum(len(x.split()) for x in ls) > a.stream_words:
            streams.append((f'{src_name}_{len(streams)}', ls))
            n_word += sum(len(x.split()) for x in ls)
            continue
        pieces = [t for t in ('\n'.join(p).strip() for p in (chunks(ls, a.chunk) if a.chunk > 0 else [ls])) if t]
        for k in range(0, len(pieces), a.seq or 1):
            text = '\x1e'.join(pieces[k:k + (a.seq or 1)])
            rows.append((text, src_name))
            n_doc += 1
            n_word += len(text.split())
    n_swb = sum(len(ls) for _, s, ls in parts if s == 'switchboard' and name != 'switchboard')
    print(f'{name:15s} {len(docs):7d} source documents -> {n_doc:7d} documents, {n_word / 1e6:6.2f}M words'
          + (f' ({n_swb} Switchboard lines cut out)' if n_swb else ''), flush=True)

random.Random(a.seed).shuffle(rows)
if streams:
    os.makedirs(os.path.join(a.dst, 'streams'), exist_ok=True)
    for name, ls in streams:
        with open(os.path.join(a.dst, 'streams', name + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(ls) + '\n')
        print(f'stream {name}: {len(ls)} lines, {sum(len(x.split()) for x in ls) / 1e6:.2f}M words')
    a.dst = os.path.join(a.dst, 'docs')
os.makedirs(a.dst, exist_ok=True)
out = os.path.join(a.dst, 'train.parquet')
pq.write_table(pa.table({'text': [r[0] for r in rows], 'source': [r[1] for r in rows]}), out, row_group_size=4096)
print(f'{len(rows)} documents, {sum(len(r[0].split()) for r in rows) / 1e6:.2f}M words -> {out}')
