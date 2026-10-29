# Archive

Earlier Silicon Perception projects, kept as they were when this repository was renamed from `devices` to `vla`
(2026-10-26). Nothing here is maintained; the history is in `git log`.

| Folder | What it was |
|---|---|
| `IE120R/` | IE120R, a single-chip image encoder: a CNN distilled from ResNet-18 on ImageNet, with FPGA (Agilex) Verilog and simulation |
| `DX120P/` | DX120P, a pose decoder paired with IE120R |
| `src/`, `pyproject.toml`, `Makefile` | the `siliconperception` Python package (IE120R and DX120P loaders), last released as 0.0.13 on PyPI; the releases are yanked |
| `dev/` | CNN_LM, the stateful recurrent CNN language model that `vla.py` grew out of |
| `CLAUDE.md` | the old repository guide (CNN_LM era) |
| `README.md.devices` | the old repository README |

The IE120R and CNN_LM weights were removed from Hugging Face on 2026-10-26; the current model is
[siliconperception/vla_v502](https://huggingface.co/siliconperception/vla_v502).
