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
v = {'VERSION': r['version'], 'STEP': f'{r["step"]:,}', 'TOKENS': f'{r["step"] * r["rows"] / 1e6:,.0f} M',
     'FW': f'{r["fineweb"]:.3f}', 'BABY': f'{r["babylm"]:.3f}', 'BLIMP': f'{r["blimp"]:.1f}',
     'COMVE': f'{r["comve"]:.1f}', 'MINP': f'{r["min_p"]:.4f}', 'RUNAWAY': f'{r["runaway"]:g} %',
     **{f'P{k.upper()}_{f.upper()}': (f'{r["pythia70m"][k][f]:.3f}' if f in ('fw', 'baby') else
                                       f'{r["pythia70m"][k][f]:.1f}')
        for k in ('128', '256', 'main') for f in ('fw', 'baby', 'blimp', 'comve')},
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
