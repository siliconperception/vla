#!/usr/bin/env python3
"""Build reasoning_phase1.txt from Raymond-dev-546730/Open-CoT-Reasoning-Mini (10,200 rows).

    python reasoning_prep.py

One line per example = the `input` field followed by the `output` field, in the same
undelimited one-example-per-line shape as vocab_phase1/2 and math_phase1, so the file is a
fourth --vocab_files pool rather than a --dataset: those slots get no <STX>/<ETX> and never
reset the recurrent state, which is the point of feeding reasoning this way.

FLATTENING. _load_vocab_pools() splits the file on newlines, so an example that spans lines
would be torn into fragments that are then shuffled independently. Every whitespace run --
including the newlines inside the <think> block -- collapses to a single space. Word order
and the <think>/<answer> tags survive; only the line breaks are lost.

NOT IN GIT. 36 MB against a 796 KB largest tracked file, and exactly regenerable from the
Hub by this script, so it follows the same rule as dolma3/ and checkpoint/ (see .gitignore).
The short curriculum files ARE tracked -- they are ~400 KB each and hand-built, not
redownloadable.

SIZE, and why it matters for the epoch column: examples average ~761 tokens against ~12 for
the sentence files, so at equal slot counts this pool wraps ~60x more slowly. Equal slots
are equal TOKENS, not equal epochs. See _epoch_num()/_epoch_report() in vla.py.
"""
import re
from datasets import load_dataset

OUT = 'reasoning_phase1.txt'

def flat(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def main():
    ds = load_dataset('Raymond-dev-546730/Open-CoT-Reasoning-Mini', split='train')
    lines, skipped = [], 0
    for ex in ds:
        inp, out = flat(ex['input']), flat(ex['output'])
        if not inp or not out:       # neither field is ever empty today; guard anyway
            skipped += 1
            continue
        lines.append(f'{inp} {out}')
    assert not any('\n' in l for l in lines)
    with open(OUT, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{OUT}: {len(lines)} examples, {skipped} skipped')

if __name__ == '__main__':
    main()
