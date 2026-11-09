#!/usr/bin/env python
"""Render the release pages from one source, so the model card and the web page always agree.

tools/release/release.json holds the release (version, step, scores, min_p, samples); the templates in
tools/release/*.in hold the text. This writes docs/model_card.md (the Hugging Face card, pushed with
--card), docs/index.html (the github.io page) and docs/spec/README.md, and fails if a placeholder is
left unfilled.

  python tools/release_docs.py
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'release')
OUT = {'model_card.md.in': 'docs/model_card.md', 'index.html.in': 'docs/index.html',
       'spec.md.in': 'docs/spec/README.md'}

r = json.load(open(os.path.join(SRC, 'release.json')))
_tok = r.get('tokens') or r['step'] * r['rows']    # (tokens: when the rows per step changed during training)
v = {'VERSION': r['version'], 'STEP': f'{r["step"]:,}', 'TOKENS': f'{_tok / 1e6:,.{1 if _tok < 1e9 else 0}f} M',
     'UPDATES': f'{r.get("updates", 0):,}',
     'FW': f'{r["fineweb"]:.3f}', 'FWEDU': f'{r.get("fwedu", 0):.3f}', 'BABY': f'{r["babylm"]:.3f}', 'BLIMP': f'{r["blimp"]:.1f}',
     'COMVE': f'{r["comve"]:.1f}', 'MINP': f'{r["min_p"]:.4f}', 'RUNAWAY': f'{r["runaway"]:g} %',
     **{f'P{k.upper()}_{f.upper()}': (f'{r["pythia70m"][k][f]:.3f}' if f in ('fw', 'fwedu', 'baby') else
                                       f'{r["pythia70m"][k][f]:.1f}')
        for k in r['pythia70m'] for f in r['pythia70m'][k]},
     'SAMPLES_MD': '\n\n'.join(f'> **{s["prompt"]}** {s["text"]}' for s in r['samples']),
     'SAMPLES_HTML': '\n  '.join(f'<blockquote><b>{html.escape(s["prompt"])}</b> {html.escape(s["text"])}'
                                 '</blockquote>' for s in r['samples'])}
for src, dst in OUT.items():
    s = open(os.path.join(SRC, src)).read()
    s = re.sub(r'\{\{(\w+)\}\}', lambda m: v[m.group(1)], s)
    if '{{' in s:
        sys.exit(f'{src}: unfilled placeholder')
    open(os.path.join(ROOT, dst), 'w').write(s)
    print(f'wrote {dst}')
