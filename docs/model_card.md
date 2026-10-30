---
license: mit
language:
- en
library_name: pytorch
pipeline_tag: text-generation
tags:
- recurrent
- cnn
- vla
datasets:
- HuggingFaceFW/fineweb
---

# VLA (recurrent CNN), v502

A language model with a fixed-size state and no positional encoding. Its memory is two 2-D registers of
512 × 7 × 7 and a ring holding a small entry for each of the last 1,024 ticks. Every tick, one convolutional
network reads the current token, the registers and one attention read of the ring, writes the registers back
and appends a new entry to the ring, dropping the oldest.

It is the text-trained core of a vision-language-action design. The intended applications do not need
superintelligence; they need conversational common sense, grounded in and modulated by what the device perceives
(sound, video, touch), at frame rates up to 500 Hz, with low and deterministic latency for embedded control, on a
power budget a battery can supply. So the target is a single chip with no external DRAM: a CNN is
parameter-efficient enough that every weight fits in on-chip SRAM, where the weights stay programmable, and the
fixed-size state makes every tick the same work.

Code, functional spec and figures: [github.com/siliconperception/vla](https://github.com/siliconperception/vla)

![One clock tick](https://raw.githubusercontent.com/siliconperception/vla/main/docs/figures/vla_v502.svg)

## Use

```bash
git clone https://github.com/siliconperception/vla && cd vla && pip install -r requirements.txt
for p in "The colors of the rainbow are" \
         "The best way to learn a new language is" \
         "My grandmother's recipe for apple pie starts with" \
         "When you plant a vegetable garden, the first thing to do is" \
         "The history of the bicycle began in"; do
  python vla.py --pretrained --generate --n 120 --prompt "$p" --device cuda
done

# prompt tuning: fit the starting registers (weights frozen) until the model predicts the prompt,
# then continue from them; prints the cold and the tuned continuation
python vla.py --pretrained --generate --prompt_tune 200 --n 120 --prompt "The colors of the rainbow are" --device cuda
```

`--pretrained` downloads `model.safetensors` and `vla_args.json` (the settings the weights were trained with)
and restores both. The weights are not a `transformers` model; load them through `vla.py`. Training is
continuing and new weights are pushed here from time to time, each tagged with its step (`stepNNNNNN`);
`--revision stepNNNNNN` loads a particular one.

## Model

| | |
|---|---|
| Parameters | 46.4 M: 20.7 M trained, 25.8 M frozen (token embedding and output layer from pythia-31m) |
| State | 2 registers × 512 × 7 × 7 and a ring of 1,024 entries × 2 × 7 × 7: 150,528 values, fixed in size |
| Register windows | 512 / 1 ticks (20 s and one tick at 25 Hz), fixed |
| Recall | one attention read per tick over the ring (the last 1,024 ticks, 41 s at 25 Hz): 8 heads of 64 sharing one key and value, no positional encoding |
| State update | 1×1 mix (2,304 → 384), 8 × (3×3 conv, BatchNorm, ReLU) at 384, 3×3 project (384 → 512), cascade write, ring write |
| Readout | 3 decoders (text, voice, image), each a tree of three 3×3 convs and the frozen pythia-31m output layer |
| Tokenizer | pythia-31m BPE (50,304) plus a `<NUL>` token ("say nothing this tick") |

## Training

- From scratch: 120,000 steps × 250 rows, one token per row per step (30 M tokens), plain SGD.
- Learning rate: a half-cosine rise from 4e-4 to 0.02 over the first 20,000 steps, then held. Truncated
  backpropagation through time over 16 steps; the loss is normalized per word rather than per token.
- Data: FineWeb sample-10BT, text only. Every document starts from a zero state (registers and ring).

## Evaluation (at the published step, 120,000)

| | Score |
|---|---|
| FineWeb held-out (100 documents, nats/token) | 5.402 |
| BabyLM 2026 dev (100 pieces, nats/token) | 5.192 |
| BLiMP (1,005 pairs from all 67 paradigms) | 64.1 % |
| ComVE (999 pairs, common-sense) | 60.8 % |

The BLiMP and ComVE pairs are scored the same way as for these reference models (each sentence read without
context; the lower total loss wins):

| Model | Size | BLiMP | ComVE |
|---|---|---|---|
| pythia-14m | 14 M | 69.7 | 64.7 |
| pythia-31m | 31 M | 71.1 | 66.9 |
| babyllama-10m-2024 | trained on 10 M words | 70.0 | 63.7 |
| SmolLM2-135M | 135 M | 80.9 | 79.3 |
| **this model** | 20.7 M trained, 30 M tokens seen | 64.1 | 60.8 |

The reference models have seen far more text (pythia: 300 B tokens). A comparison with pythia-70m at matched
training tokens is in preparation.

## Limits

A small model early in training: it writes locally fluent text that is often not factual or consistent. Not
instruction-tuned, not safety filtered beyond its training corpora. The voice and image decoders are present but
this model has been trained on text only. Training is continuing; this card describes the step above.

## License

MIT, Copyright (c) 2024-2026 Silicon Perception Inc. The license covers the software and these weights and grants
no patent rights; see [PATENTS](https://github.com/siliconperception/vla/blob/main/PATENTS). Frozen third-party
weights inside: EleutherAI [pythia-31m](https://huggingface.co/EleutherAI/pythia-31m) embedding and output
layer (Apache-2.0).
