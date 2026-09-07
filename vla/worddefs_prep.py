#!/usr/bin/env python3
"""Build worddefs.txt from MongoDB/english-words-definitions (466,670 terms).

    python worddefs_prep.py

One line per term = that term's `definitions` list concatenated, in the same undelimited
one-example-per-line shape as vocab_phase1/2 and math_phase1, so the file is a --vocab_files
pool: those slots get no <STX>/<ETX> and never reset the recurrent state.

The `definitions` field is a LIST of strings (most terms have one, some several). They are
joined with a single space and the list brackets/quotes are not part of the text -- the
quotes in a repr() of the row are Python's, not content.

Each line is the bare `term` followed by its definitions. The term is worth the stutter it
sometimes causes (many definitions already open by naming their term): a definition does
not always contain its headword, and the point of this pool is to teach the association
FROM the bare word form, which only holds if the word is actually present to key on.

Whitespace is flattened to single spaces because _load_vocab_pools splits the file on
newlines and a multi-line example would be torn into independently shuffled fragments.
"""
import re
from datasets import load_dataset

OUT = 'worddefs.txt'

def flat(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def main():
    ds = load_dataset('MongoDB/english-words-definitions', split='train')
    lines, skipped = [], 0
    for ex in ds:
        defs = ex.get('definitions') or []
        if isinstance(defs, str):            # tolerate a scalar, should not occur
            defs = [defs]
        term = flat(ex.get('term'))
        body = flat(' '.join(d for d in defs if d))
        if not term or len(body) < 8:
            skipped += 1
            continue
        lines.append(f'{term} {body}')
    assert not any('\n' in l for l in lines)
    with open(OUT, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{OUT}: {len(lines):,} examples, {skipped:,} skipped')

if __name__ == '__main__':
    main()
