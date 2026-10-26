# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Concept

The unifying theme is **CNN as a very high-dimensional function approximator with efficient hardware implementation**. A CNN with `n_hidden` channels and a `context × context` spatial grid maintains a state of `n_hidden × context × context` values (e.g., 96×96×96 ≈ 885K dimensions), yet the projector that transforms this state has only O(kernel² × channels²) parameters — the same small kernel is reused at every spatial position. This weight sharing is what makes CNNs both parameter-efficient and hardware-efficient: a small weight ROM drives a dataflow architecture that computes over a very large state.

The **CNN_LM** (`dev/`) applies this to language modeling. The **IE120R** image encoder (`src/siliconperception/IE120R.py`, FPGA chip) uses the same principle for vision, and is a natural multimodal front-end: its output feature maps are already 2D spatial tensors that can be injected directly into the CNN_LM context.

## CNN_LM Architecture (`dev/models.py`)

The model is a **stateful recurrent CNN**. The context `ctx` is a 2D feature map of shape `[1, n_hidden, context, context]` that accumulates information across tokens. Each forward step:

```
token → embed → [n_embd, 1, 1] → encoder → [n_hidden, context, context]
ctx ← projector(ctx + encoded_token)          # state update (detached)
logits ← lmhead(decoder(ctx))                 # next-token prediction
```

The state transition (`projector`) is a CNN operating on the full `context × context` grid. The decoder collapses the 2D grid back to a token embedding. No attention, no positional encoding.

### Submodules (all parameterized by the `--alt` string)

**`CNN_ENCODER`** (`repl` variant) — replicates the token embedding `[n_embd, 1, 1]` to `[n_hidden, context, context]` via a 1×1 conv followed by nearest-neighbor upsample. This broadcasts a single token's information uniformly across the spatial context.

**`CNN_PROJECTOR`** — the core memory update; variant chosen by `--alt` keyword:
- `res` / `deep` / `xtra` — residual stacks: `x ← 0.5*x + layer(x)`, depth scales with context size
- `wide` — 7×7 kernel conv stack (larger receptive field per layer)
- `fixed` — 3×3 kernel conv stack with linear output projection

**`CNN_DECODER`** — collapses `[n_hidden, context, context]` → `[n_embd]`; variant:
- `pool` — 1×1 conv then `AvgPool2d(context)`: simple global average
- `tree` — strided 3×3 convs downsampling by 2× per stage until 1×1

**Embedding backends** (chosen by `n_embd` and `--alt`):
- `n_embd=256, char` in alt — `ByteLevelTokenizer` + `CharacterOneHotEmbedding` (vocab=256, no learned embedding, `lmhead=Identity`). Fully self-contained, no external model dependency.
- `n_embd=256` — TinyStories-8M token embeddings (vocab≈10K); `embed` and `lmhead` frozen
- `n_embd=768` — TinyStories-33M token embeddings (vocab≈50K); `embed` and `lmhead` frozen

Only `projector` and `decoder` parameters are trained (see optimizer parameter groups in `pretrain.py`).

### Training protocol

Sequences are fed **one token at a time**. The `\x02` (STX) byte is the start-of-example token; `pretrain.py` resets `ctx` to zero when it sees one (`flag` from the data worker). The data worker streams tokens continuously across document boundaries, resetting context only at document starts — so the model learns to carry context within a document and restart cleanly between them.

The context is detached from the computation graph each step (`proj.clone().detach()`), making the gradient horizon exactly one token. This is deliberate: it keeps memory bounded and avoids BPTT instability, at the cost of not backpropagating through the state.

## Running CNN_LM

All commands run from `dev/`:

```bash
# Train (byte-level char model, small config)
python pretrain.py \
    --context 96 --n_hidden 96 --dataset tiny \
    --learning_rate 0.000001 --opt adamw --weight_decay 0.01 --beta2 0.95 \
    --batch 50 --monitor 20 --generate 500 \
    --alt repl-pool-wide-char

# Generate text from a checkpoint
python generate.py --load checkpoint.pt --n 200 --alt repl-pool-wide-char \
    --context 96 --n_hidden 96 --prompt $'\x03\x03'

# Visualize context dynamics while generating (shows std of ctx across channels)
python generate.py --load checkpoint.pt --vis --delay 0.1

# Plot training loss from a log file
python chart.py --log log/log.2026.01.02-18.41.00 --head 10
```

Key `pretrain.py` arguments:
- `--context` — spatial size of the context grid (context × context)
- `--n_hidden` — channel depth of the context feature map
- `--alt` — architecture variant string (e.g., `repl-pool-wide-char`)
- `--dataset` — `tiny`, `c4`, `dolma`, `web`, `codelion`, `mix`; add `--streaming` to avoid downloading
- `--schedule` — `linear`, `cyclic`, `decay`, `piecewise`; controls LR over `--period` steps
- `--load` / `--save` / `--checkpoint` — checkpoint I/O
- `--steps` — stop after N gradient steps (omit to run indefinitely)
- `--prompt` — string fed to the model during periodic generation samples (use `\x02` as START, `\x03` as END)

The `doit` file is the experiment history — commented-out invocations showing which hyperparameters were tried and in what order. Read it to understand the trajectory of experiments.

## IE120R as a Multimodal Encoder

IE120R (`src/siliconperception/IE120R.py`) takes a 896×896 RGB image and outputs five multi-scale feature maps, the last of which (`f4`) is `[512, 7, 7]`. These are 2D spatial tensors — the same shape convention as `ctx` in CNN_LM.

The natural multimodal extension: project IE120R's `f4` (or a combination of scales) into `[n_hidden, context, context]` and inject it as the initial context or as an additive signal at each step, analogous to how the encoder injects the token embedding. IE120R's bfloat18 weight quantization (`IE120R_HW`) is designed for the same FPGA fabric that would run CNN_LM in hardware, so the two can share a dataflow pipeline.

## Package Build and Publish

```bash
# Bump version in src/siliconperception/__init__.py AND pyproject.toml first
make build    # python3 -m build --wheel
make upload   # twine upload dist/*
```

Models are also published to HuggingFace: `siliconperception/IE120R`, `siliconperception/CNN_LM`.

## IE120R Training Scripts (`IE120R/scripts/`)

```bash
bash dataset.bash          # download ImageNet 2010 into ./dataset/

python pretrain.py \       # knowledge distillation from frozen ResNet-18 teacher
    --dataset ./dataset --save checkpoint.pt --device cuda --batch 20 --workers 12

python classify.py \       # top-1 accuracy with frozen IE120R encoder + linear probe
    --backbone ie120r --dataset ./dataset/ --device cuda
```
