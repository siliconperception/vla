# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## Project

`vla.py` is the whole model: a recurrent CNN whose state is K 2-D register grids (plus, with `--attn`, a
fixed-size recall ring), trained one token per row per step with truncated backpropagation through time. It trains, evaluates (`--eval`), generates (`--generate`),
exports to the Hugging Face hub (`--push`) and loads from it (`--pretrained`). The model is specified in
`docs/spec/README.md`; when the spec and the code disagree, fix the spec.

## Layout

- `vla.py`: everything above; its `--help` is the reference for flags.
- `tools/`: `run.sh` (the launcher: records the resolved command line in `./doit`, keeps `log/exp.<name>` and
  `checkpoint/<name>.pt` in step), `snapwatch.sh`, `logwatch.py`, the `*_prep.py` data builders, `pairs_ref.py`.
- `docs/`: the github.io page (`index.html`), figures, functional spec, model card.
- `paper/`, `tests/` (`tests/smoke.sh`: CPU, network), `archive/` (retired projects, not maintained).
- Local only (gitignored): `checkpoint/`, `log/`, `lab/` (the research record), `doit`.

## Conventions

- Local corpora live under `$VLA_DATA` (default `/data`).
- Never write a test checkpoint over a live run's `checkpoint/<name>.pt`.
- The model and weights are MIT; the silicon implementation is proprietary and does not belong in this repo
  (see `PATENTS`).
