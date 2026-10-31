# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## Project

`vla.py` is the whole model: a recurrent CNN (`--layers` in series) whose state is K 2-D register grids per
layer (plus, with `--attn`, a fixed-size recall ring), trained one token per row per step with truncated backpropagation through time. It trains, evaluates (`--eval`), generates (`--generate`),
exports to the Hugging Face hub (`--push`) and loads from it (`--pretrained`). The model is specified in
`docs/spec/README.md`; when the spec and the code disagree, fix the spec (its template, see Releases).

## Layout

- `vla.py`: everything above; its `--help` is the reference for flags.
- `tools/`: `run.sh` (the launcher: records the resolved command line in `./doit`, keeps `log/exp.<name>` and
  `checkpoint/<name>.pt` in step), `snapwatch.sh`, `logwatch.py`, the `*_prep.py` data builders, `pairs_ref.py`.
- `docs/`: the github.io page (`index.html`), figures, functional spec, model card.
- `paper/`, `tests/` (`tests/smoke.sh`: CPU, network), `archive/` (retired projects, not maintained).
- Local only (gitignored): `checkpoint/`, `log/`, `lab/` (the research record), `doit`.

## Releases

Hugging Face holds one model, `siliconperception/vla`, overwritten by each release (no tags, history squashed).
`docs/model_card.md`, `docs/index.html` and `docs/spec/README.md` are generated: edit the templates in
`tools/release/*.in` and the numbers in `tools/release/release.json`, then run `python tools/release_docs.py`,
so the card and the web page always agree. Push with `vla.py --load <frozen copy> --push --card
docs/model_card.md`, then `HfApi().super_squash_history('siliconperception/vla')`, and check that
`vla.py --pretrained --eval` matches the local score exactly.

## Conventions

- Local corpora live under `$VLA_DATA` (default `/data`).
- Never write a test checkpoint over a live run's `checkpoint/<name>.pt`.
- The model and weights are MIT; the silicon implementation is proprietary and does not belong in this repo
  (see `PATENTS`).
