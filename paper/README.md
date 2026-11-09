# Paper (in preparation)

An arXiv-style white paper on the recurrent CNN VLA. It covers:

- **The architecture:** ConvDelta blocks of 3 × 3 convolutions on a 9 × 9 grid, each followed by a gated
  delta-rule memory at every grid position, with a fixed-size state and the same work every tick.
- **Memory time scales:** fixed base decay windows, log-spaced over all heads, that the input can move within a
  band, compared with learned windows.
- **Training:** windows trained at once by an exact chunked parallel scan, with the state carried between windows.
- **Results:** against pythia-70m at matched training tokens and fully trained, on held-out FineWeb-Edu, FineWeb
  and BabyLM text, and on BLiMP and ComVE minimal pairs, with the use of context by position in the document.
- **The path to a single chip and its limits.**

The LaTeX source and the built PDF will live here. Figures come from `../docs/figures/`; the published model is
described in `../docs/spec/README.md`.
