"""The canonical bdict sentence splitter.

This is a VERBATIM copy of vla.py's _split_sentences. It lives here so the dataset build
scripts split exactly the way training does -- a corpus whose line count disagrees with
what --bdict_split produces is a corpus whose "10,000 examples" is a fiction.

NOT imported by vla.py: vla.py is mid-run (pp1) and adding an import to it would put a new
failure mode on the longrun restart path for no benefit today. Refactor vla.py to import
this once the GPU is free. verify() below is what keeps the two honest -- it asserts the
known-good counts for the two committed corpora.
"""
import re

_BD_ABBREV = ('Mr.', 'Mrs.', 'Ms.', 'Dr.', 'St.')


def split_sentences(text):
    t = text
    for i, a in enumerate(_BD_ABBREV):
        t = t.replace(a, f'\x00{i}\x00')
    t = re.sub(r'([.!?]["\']?)\s+', '\\1\x01', t)
    out = []
    for part in t.split('\x01'):
        for i, a in enumerate(_BD_ABBREV):
            part = part.replace(f'\x00{i}\x00', a)
        part = part.strip()
        if not part:
            continue
        if out and part[:1].islower():
            out[-1] = out[-1] + ' ' + part
        else:
            out.append(part)
    return out


def split_keyed_file(path):
    """A 'word: s1 s2 ...' file -> flat list of sentences, key stripped (what --bdict_split
    feeds the trainer)."""
    out = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        body = line.split(':', 1)[1] if ':' in line else line
        out.extend(split_sentences(body.strip()))
    return out


def verify():
    for path, want in (('basic_dict_e3.txt', 2544), ('basic_dict_e10.txt', 8480)):
        got = len(split_keyed_file(path))
        assert got == want, f'{path}: split gave {got}, vla.py gives {want}'
    return True


if __name__ == '__main__':
    verify(); print('sentsplit agrees with vla.py on both committed corpora')
