# Release plan: siliconperception/vla (GitHub code, Hugging Face model, github.io page)

Draft for review, 2026-10-26. Nothing below has been executed. Every push, rename, deletion and
publication waits for your go, step by step.

## The boundary: open model, proprietary silicon

Silicon Perception Inc is a chip company. It sells chips that are hardened versions of `vla.py`.
- **Open (MIT, Copyright Silicon Perception Inc):** the model, meaning `vla.py`, its tools, the trained weights on
  HF, the figures, the model's functional spec (what it computes each tick), the paper, the page.
- **Proprietary (stays in the private `perceptron` repo or off GitHub):** the silicon instantiation: RTL, netlists,
  the fixed-point and quantization mapping, the chip microarchitecture (dataflow, memories, clocking), area, power
  and timing figures, process and vendor details, and the cost and margin plans.
- **What that means in this plan:**
  - `vla/doc/spec/` describes the model, not the chip.
  - Before it goes public, every file bound for `lab/`, `doc/` or `paper/` gets a read for chip-side content. The
    PLAN files talk about ASIC/FPGA parameter budgets, the ≥100 Hz target and register fixed-point; I'll list
    each such passage for you to keep, cut or soften.
  - The archived `IE120R/` and `DX120P/` already publish Verilog and FPGA builds under MIT. Moving them to
    `archive/` doesn't change that. Pulling them out of the public repo (and history) is a separate decision.
- **Patents:** MIT grants use "without restriction", and lawyers disagree about how far that reaches patents. It
  has no explicit patent clause either way. Apache-2.0 would add an explicit patent grant, which a chip company may
  not want. If the company holds or plans patents on the hardware, this choice is one for counsel before the
  release. (Not legal advice.)

## What exists today

| Asset | State |
|---|---|
| GitHub `siliconperception/devices` | public, default branch `main`, 417 commits, 2,627 tracked files, `.git` 354 MB (large `.memh` and old checkpoint blobs in history). Top level: `IE120R/` (1,295 files), `DX120P/` (951), `vla/` (361), `dev/` (CNN_LM, 12), `src/siliconperception/` (PyPI package: IE120R.py, DX120P.py), `pyproject.toml`, `Makefile`, `LICENSE` (MIT, "Copyright (c) 2024 siliconperception"), `README.md`, `CLAUDE.md` |
| GitHub `siliconperception/perceptron` | private, **not touched** |
| `vla/` | `vla.py` (6.3K lines, self-contained, stdlib + torch/transformers/datasets/pyarrow), `exp/` (249 files: run.sh, snapwatch, logwatch, prep and eval scripts), `log/` (61 tracked: notes, sweeps), 7 PLAN files, `doit`, 17 `vla_vNNN.svg` figures (latest `vla_v451.svg`, 2026-10-22), `vla.pdf`, a stale README (still describes `--evaluate` HellaSwag and old datasets), old scripts (gptneo.py, pythia.py, chart.py, sweep_*.py, *_prep.py), untracked clutter (vla.py.1-9, train.py.N, foo, echo, vla.odp) |
| Hugging Face `siliconperception` | models `IE120R` (4 downloads), `CNN_LM` (284), `VLA` (3; an August model: S 28, n_hidden 128, pythia14m, 66 MB). No datasets |
| github.io | `siliconperception.github.io` returns 404; Pages is off on `devices` |
| Tooling here | `git` over SSH works (push rights). No `gh` CLI. HF token exists (`../dev/HF_TOKEN`) but is off limits unless you say otherwise |
| Live run | v476 trains in `/proj/devices/vla` (checkpoint/, log/, exp/run.sh, exp/snapwatch.sh). Nothing below may move those paths while it runs |

## Decisions for you (each changes what I do)

1. **Which model to publish.** Recommend: v472 now (text, FineWeb 40M-step lineage, best documented), as
   `siliconperception/vla` revision `v472`; replace it with v476 when bet 2 finishes if v476 wins (BLiMP/ComVE +2,
   no loss of free-running quality). Alternative: wait about a day for v476 and publish once.
2. **Old HF repos.** Deleting is permanent and breaks anyone loading them. `IE120R` is loaded by the PyPI package
   `siliconperception` 0.0.13. Recommend: rename `VLA` to `VLA-legacy-2026-08` (frees the name, keeps old links via
   the HF redirect), and give `IE120R` and `CNN_LM` a deprecation banner in their model cards plus a pointer to
   `siliconperception/vla`. Delete only what you name explicitly.
3. **The research record.** Keep it public? Recommend yes, in `vla/lab/`: PLAN files, `doit`, `log/notes`,
   `log/sweeps`. It is the evidence behind the paper's numbers, and most of it is already public today. It goes in
   only after the chip-side read (see the boundary above).
4. **Git history.** Recommend keeping it (a GitHub rename keeps stars, issues and redirects
   `siliconperception/devices` to `siliconperception/vla`). The alternative, a fresh history without the 354 MB of
   IE120R/DX120P blobs, loses that and makes `devices` a separate frozen repo.
5. **Page address.** Recommend a project page at `siliconperception.github.io/vla`, published from the `vla` repo
   by a GitHub Actions workflow. An organization page at `siliconperception.github.io` needs a separate repo of
   that exact name; it can come later as a one-line redirect.
6. **The figure.** The latest SVG (`vla_v451.svg`) draws the multimodal design (log-mel hearing, vision, three
   streams); the model on HF will be text-only. Recommend: v451 as the hero image, captioned as the design, plus a
   new figure of the published model (the 4-register cascade, tau 128/32/8/2), drawn for the doc and the model card.
7. **License holder.** Today: "Copyright (c) 2024 siliconperception". Change it to "Copyright (c) 2024-2026
   Silicon Perception Inc", the same text in the root, in `vla/` and in the model card.

## Proposed layout

```
siliconperception/vla              (repo root, renamed from devices)
├── README.md                      landing: one-paragraph pitch, figure, links (code, model, page, paper)
├── LICENSE                        MIT (the one GitHub detects)
├── .github/workflows/pages.yml    publishes vla/site to github.io
├── archive/                       everything non-VLA, unchanged inside
│   ├── README.md                  what each folder was, last PyPI version, why archived
│   ├── IE120R/  DX120P/  dev/     (dev = the CNN_LM predecessor)
│   ├── src/  pyproject.toml  Makefile   (the PyPI package siliconperception 0.0.13)
│   └── vla-legacy/                retired vla scripts: gptneo.py, pythia.py, chart.py, sweep_*.py,
│                                  dolma3/reasoning/worddefs prep, push_to_hub.py, vla.pdf, old README
└── vla/                           the MIT open-source project
    ├── README.md                  install, train, generate, evaluate, load from HF, reproduce v472
    ├── requirements.txt           torch, transformers, datasets, pyarrow, numpy (versions we run)
    ├── vla.py
    ├── tools/                     today's exp/: launch (run.sh), watchers (snapwatch, logwatch),
    │                              data prep (babylm_prep ...), eval (pairs_ref, select ...)
    ├── doc/
    │   ├── figures/               vla_vNNN.svg (+ the new model figure)
    │   └── spec/                  functional spec: tick, registers, I/O, numerics, chip budget
    ├── paper/                     LaTeX (arXiv style), Makefile, built PDF; figures from doc/figures
    ├── site/                      the github.io page (static HTML, no build step)
    ├── lab/                       research record: PLAN*.md, doit, notes, sweeps (decision 3)
    └── tests/                     CPU smoke test: build, 50 steps, save, reload, generate
```

Directories I'm adding beyond your list, and why:
- **`site/`**: keeps the page next to the code it describes; the workflow publishes it, no gh-pages branch to drift.
- **`lab/`**: separates the research diary from the code people install, without hiding it.
- **`tests/`**: one smoke test, so a refactor or a dependency bump can't silently break `vla.py` for outside users.
- **`tools/`** instead of `exp/`: says what it is. Optional; the rename waits for a run boundary (below).

## Steps

### Phase 0: prepare (local, nothing published)
1. Write the new root README, `archive/README.md`, `vla/README.md`, `requirements.txt`, the MIT LICENSE.
2. Sweep for things that shouldn't go public: chip-side content (the boundary above; you rule on each passage),
   tokens and keys (grep the tree and the staged diff), personal paths,
   emails. Add `HF_TOKEN`, `checkpoint/`, `*.pt`, `__pycache__/` to `.gitignore`.
3. Make data locations configurable: `vla.py` hard-codes `/data/...` and `/data/huggingface` paths
   (`_LOCAL_PARQUET` etc.). Read a `VLA_DATA` root from the environment, defaulting to today's paths.
4. Add `tests/` and run it on CPU (scratchpad output, never the live checkpoint).

### Phase 1: GitHub restructure (one commit per step, on `main`)
5. `git mv` IE120R, DX120P, dev, src, pyproject.toml, Makefile into `archive/`. Safe while v476 runs: it only uses
   `vla/`.
6. Inside `vla/`: move figures to `doc/figures/`, the research files to `lab/`, the retired scripts to
   `archive/vla-legacy/`, delete untracked clutter (vla.py.1-9, train.py.N, foo, echo; I'll list each before deleting).
   **Deferred to a run boundary:** `exp/` → `tools/`, `log/` and `doit` → `lab/`, because the live run writes
   `log/` and its driver calls `exp/run.sh` and `exp/snapwatch.sh`.
7. Update `CLAUDE.md` and memory paths.
8. **Push** `main` (your go).
9. **Rename** `devices` → `vla` in GitHub Settings. You click it, or give me a token with admin scope. GitHub
   redirects the old URL. Then I run `git remote set-url origin git@github.com:siliconperception/vla.git`.
10. Local directory: `/proj/devices` → `/proj/vla` only at a run boundary (checkpoint paths, memory notes and
    `exp/run.sh` all use it). Until then the local name doesn't matter.

### Phase 2: Hugging Face model
11. Extend `--push` so the repo is self-describing: `config.json` (the architecture args `--pretrained` needs),
    `model.safetensors`, and a model card (`README.md`): what the model is, figure, training data and steps,
    held-out and EVALM results next to the yardstick (pythia-14m, babyllama-10m), limitations, license, and how to
    load it (`python vla.py --pretrained siliconperception/vla --generate ...`).
12. Round trip on CPU from a clean clone in the scratchpad: `--push` to a private test repo, `--pretrained` back,
    and check the eval numbers match the local checkpoint exactly. Then delete the private test repo.
13. **Old repos** per decision 2 (rename `VLA`; deprecation cards on `IE120R` and `CNN_LM`). You run
    `huggingface-cli login`, or tell me to use `../dev/HF_TOKEN`.
14. **Publish** `siliconperception/vla` (public), tagged with the run name. Default `--hub_repo` and
    `--pretrained` in vla.py point to it.

### Phase 3: github.io page
15. `vla/site/index.html`: a single static page. Hero = the SVG inline (it scales and stays sharp). A short pitch
    (a recurrent CNN whose state is a 2-D register grid; one small weight ROM; aimed at a single-chip VLA at
    ≥100 Hz). Results table, a few real generations, the three links (code, model, paper). Light and dark,
    readable on a phone, no external scripts.
16. `.github/workflows/pages.yml` (deploys `vla/site` on push to `main`). Enable Pages → "GitHub Actions" in repo
    settings (your click or the admin token).
17. **Push**, then check `https://siliconperception.github.io/vla/` returns 200 and renders on desktop and phone.

### Phase 4: paper (after bets 2 and 3 report)
18. `vla/paper/`: arXiv LaTeX skeleton and outline (architecture; the register cascade and clock rates; training
    without BPTT; results vs the yardstick; the chip budget; limits). Draft text comes once bet 2 (and 3) are in.
    The page and the model card link to the PDF when it exists.

## Order and timing
Phase 0 and step 5 can start now; nothing touches the live run. Steps 6-10 split around the next run boundary.
Phase 2 needs decision 1 (v472 now, or v476 in about a day). Phase 3 needs Phase 1's rename (the page lives under
the repo name). Phase 4 follows the results.

## Risks
- **The PyPI package** `siliconperception` builds from `src/` and `pyproject.toml` at the root. After the move, its
  build lives in `archive/`; the published 0.0.13 keeps working, and `IE120R.from_pretrained` keeps working only if
  the HF `IE120R` repo stays.
- **Links into `devices`** (papers, the PyPI page, HF cards) keep working through GitHub's rename redirect, unless a
  new repo named `devices` is ever created.
- **History size**: clones stay 354 MB with the archived blobs (decision 4).
- **Hard-coded paths**: `vla.py` won't run elsewhere until step 3 is done; the README must say what data to fetch.
