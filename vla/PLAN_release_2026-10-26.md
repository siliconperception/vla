# Release plan: siliconperception/vla (GitHub code, Hugging Face model, github.io page)

Revision 2, 2026-10-26, after your answers. Nothing below has been executed. Every push, rename, deletion and
publication waits for your go.

## The boundary: open model, proprietary silicon

Silicon Perception Inc is a chip company. It sells chips that are hardened versions of `vla.py`. It owns the
pending patent US-20260010766-A1, on implementing a CNN optimally in silicon.
- **Open (MIT, Copyright Silicon Perception Inc):** the model: `vla.py`, its tools, the trained weights on HF,
  the figures, the model's functional spec (what it computes each tick), the paper, the page.
- **Proprietary (the private `perceptron` repo, never touched, or off GitHub):** the silicon instantiation: RTL,
  netlists, the fixed-point and quantization mapping, the chip microarchitecture, area, power and timing figures,
  process and vendor details, cost and margin plans.
- **Patent and license:** plain MIT says nothing about patents; whether it implies a license to the patent for
  people who build hardware from `vla.py` is exactly the kind of question counsel should answer before release.
  Options for counsel: (a) MIT plus a `PATENTS` notice naming US-20260010766-A1 and stating that no patent rights
  are granted; (b) the BSD-3-Clause-Clear license, which says that in its text (not OSI-approved); (c) Apache-2.0,
  which grants patent rights and is likely the wrong choice here. Not legal advice; I'll draft whichever counsel picks.

## Decisions taken (2026-10-26)

| # | Decision |
|---|---|
| 1 | Publish the latest model to HF (which checkpoint: see open question A) |
| 2 | Delete the old HF models: `IE120R`, `CNN_LM`, `VLA` |
| 4 | Keep the git history |
| 5 | Page under the repo: `siliconperception.github.io/vla` |
| 6 | The latest SVG (`vla_v451.svg`) on the page |
| 7 | Copyright (c) 2024-2026 Silicon Perception Inc |
| - | v476 may pause during the refactor |
| - | No redundant names: the repo root IS the project, `siliconperception/vla/vla.py` |

## Open questions

- **A. Which checkpoint is "the latest model".** v476 is a 2-hour-old BabyLM experiment: FineWeb held-out is worse
  than v472 (4.80 vs 4.56) and its bet hasn't been scored. v472 is the latest finished model. Recommend v472 now,
  then v476 as a new HF revision if it wins bet 2.
- **B. The research record.** See the advice in the reply; recommend keeping the raw diary out of the published
  tree and publishing curated results instead.
- **C. PyPI.** See the advice in the reply; recommend yanking the legacy releases and keeping the name.
- **D. License wording** (counsel; the boundary section above).

## Layout

```
siliconperception/vla                 repo root = the project (renamed from devices)
├── README.md                         pitch, figure, quickstart, links (model, page, paper)
├── LICENSE                           MIT, Copyright (c) 2024-2026 Silicon Perception Inc
├── PATENTS                           only if counsel picks option (a)
├── vla.py                            the model, training, eval, generation
├── requirements.txt
├── tools/                            the live tools from exp/: run.sh, snapwatch, logwatch, babylm_prep,
│                                     pairs_ref, select, ... (old sweep scripts go to archive/)
├── docs/                             the github.io site AND the docs, served as-is by Pages (main, /docs);
│   ├── index.html                    landing page, the latest SVG inline
│   ├── figures/                      vla_vNNN.svg
│   └── spec/                         functional spec of the model (not the chip)
├── paper/                            LaTeX (arXiv style), Makefile, built PDF
├── tests/                            CPU smoke test
└── archive/                          everything retired, unchanged inside
    ├── README.md                     what each folder was, why archived
    ├── IE120R/  DX120P/  dev/  src/  pyproject.toml  Makefile
    └── vla-legacy/                   retired vla scripts and old exp/ sweeps
```

- **`docs/` instead of `doc/`:** GitHub Pages serves a branch's `/docs` folder with no workflow. One directory
  then holds the landing page, the figures and the spec, and the spec is readable on the site too.
- **Local, not in git:** `checkpoint/`, `log/` (run logs), `data` links (gitignored).

## Steps

### Phase 0: prepare (local, nothing published; v476 keeps running)
1. Pre-publication read: list every passage with chip-side content (ASIC/FPGA budgets, the ≥100 Hz target,
   register fixed-point) in files that will be public at HEAD; you rule on each. Grep for tokens, keys, emails.
2. Draft README, `archive/README.md`, LICENSE, `requirements.txt`, the CPU smoke test.
3. Make data locations configurable: `vla.py` hard-codes `/data/...`; read a `VLA_DATA` root from the environment,
   defaulting to today's paths. Several old `exp/` scripts hard-code `cd /proj/devices/vla`; they go to the archive.

### Phase 1: refactor (v476 paused)
4. SIGTERM v476 (it saves) and stop its watchers.
5. `git mv` the current root content (IE120R, DX120P, dev, src, pyproject.toml, Makefile, old README, CLAUDE.md)
   into `archive/`; `git mv vla/*` up to the root; figures to `docs/figures/`; live tools to `tools/`; retired
   scripts to `archive/vla-legacy/`; the research record per question B. Untracked clutter (vla.py.1-9, train.py.N,
   foo, echo, ...) listed for you before deletion.
6. Local directory `/proj/devices` → `/proj/vla`, so the working tree matches the repo. Then fix what depends on
   the path: `exp/run.sh` paths, CLAUDE.md, and **Claude's memory folder** (`~/.claude/projects/-proj-devices*` is keyed
   by the path; copy it to `-proj-vla` or the memories won't load).
7. Smoke test (CPU) and a 200-step GPU resume of v476 from its stop checkpoint in the new tree, saved to the
   scratchpad. Then resume v476 itself under the same name (identical config, so no new vNNN).
8. **Push** `main` (your go). **Rename** `devices` → `vla` on GitHub (Settings; or an admin token), then
   `git remote set-url origin git@github.com:siliconperception/vla.git`. The old URL redirects.

### Phase 2: Hugging Face
9. Extend `--push` to write a model card: what it is, figure, data and steps, held-out and EVALM results next to
   the yardstick (pythia-14m, babyllama-10m), limits, license, how to load
   (`python vla.py --pretrained siliconperception/vla --generate ...`).
10. Round trip on CPU from a clean clone: push to a private test repo, `--pretrained` back, check the evals match
    exactly; delete the test repo.
11. **Delete** `siliconperception/IE120R`, `CNN_LM`, `VLA` (you run `huggingface-cli login`, or tell me to use
    `../dev/HF_TOKEN`).
12. **Publish** `siliconperception/vla` with the checkpoint from question A, tagged with the run name;
    vla.py's `--hub_repo` and `--pretrained` defaults point to it.

### Phase 3: PyPI (per question C)
13. Yank 0.0.1-0.0.13 of `siliconperception` (they stay installable by exact pin, hidden otherwise) and update the
    project description to point to `siliconperception/vla`. Needs your PyPI login.

### Phase 4: github.io
14. `docs/index.html`: the latest SVG inline as the hero, a short pitch, a results table, real generations, links to
    code, model and paper. Light and dark, readable on a phone, no external scripts.
15. Enable Pages (Settings → Pages → `main`, `/docs`). **Push**, then check
    `https://siliconperception.github.io/vla/` loads on desktop and phone.

### Phase 5: paper (after bets 2 and 3 report)
16. `paper/`: arXiv LaTeX skeleton and outline now; the text after the results. Page and model card link to the PDF.

## Risks
- **Keeping history keeps everything ever committed public**, including the PLAN files' chip budgets and the
  IE120R/DX120P Verilog. Removing a file at HEAD hides it from browsing, not from `git log`. Only a history rewrite
  removes it (that conflicts with decision 4).
- **Deleting HF `IE120R` breaks `siliconperception` 0.0.13** (`IE120R.from_pretrained`); yanking (step 13) is the
  matching move.
- **Links into `devices`** keep working through GitHub's rename redirect unless a new `devices` repo is created.
- **v476 pause:** about an hour if the moves and the resume test go cleanly.
