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

# VLA (recurrent CNN)

**Release v511, step 1,680,000** (420 M training tokens).

A language model with a fixed-size state and no positional encoding. It is two recurrent convolutional layers
in series, each with two 2-D registers of 512 × 7 × 7: a slow one (a 16-tick average in layer 1, a 64-tick
average in layer 2) and a copy of the rest. Every tick, layer 1 reads the current token and its registers,
layer 2 reads layer 1's output and its own registers, each writes its registers back, and the sum of the two
outputs is decoded into the next token.

It is the text-trained core of a vision-language-action design. Most commercial applications for autonomous,
agile robots do not require superintelligence; they need conversational common sense, grounded in and modulated by
what the device perceives (sound, video, touch). To achieve superhuman hand-eye coordination, they need it at frame
rates up to 500 Hz, with low and deterministic latency for embedded control, on a power budget a battery can
supply. So the target is a single chip with no external DRAM: a CNN is parameter-efficient enough that every weight
fits in on-chip SRAM, where the weights stay programmable, and the fixed-size state makes every tick the same work.
Leaving out external memory also saves power: no DRAM chips to keep refreshed, no high-speed interface driving
signals between chips, and a weight read from on-chip SRAM takes on the order of a hundred times less energy than
one fetched from off-chip DRAM.

Code, functional spec and figures: [github.com/siliconperception/vla](https://github.com/siliconperception/vla)

![One clock tick](https://raw.githubusercontent.com/siliconperception/vla/main/docs/figures/vla_v511.svg)

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
and restores both. The weights are not a `transformers` model; load them through `vla.py`. This repository
holds only the current release: each new one replaces the weights and this card, and earlier releases are not
kept.

## Model

| | |
|---|---|
| Parameters | 59.0 M: 33.2 M trained, 25.8 M frozen (token embedding and output layer from pythia-31m) |
| State | 2 layers × 2 registers × 512 × 7 × 7: 100,352 values, fixed in size |
| Register windows | layer 1: 16 / 1 ticks; layer 2: 64 / 1 ticks (0.64 s and 2.56 s at 25 Hz), fixed |
| Layer 1 | 1×1 mix (2,048 → 384) of the token, sound and its two registers (RMS-normalized reads), 8 × (3×3 conv, BatchNorm, ReLU) at 384, 3×3 project (384 → 512), cascade write |
| Layer 2 | the same, reading only layer 1's output and its own registers (1,536 → 384); its output is added to layer 1's |
| Readout | 3 decoders (text, voice, image), each a tree of three 3×3 convs and the frozen pythia-31m output layer |
| Tokenizer | pythia-31m BPE (50,304) plus a `<NUL>` token ("say nothing this tick") |

## Training

- 1,680,000 steps × 250 rows, one token per row per step (420 M tokens), plain SGD. Truncated backpropagation
  through time over 16 steps; the loss is normalized per word rather than per token.
- Data: FineWeb sample-10BT, text only. Every document starts from a zero state.
- The configuration grew during training, always resuming from the latest weights: one layer with a 512-tick
  average and a 1,024-tick recall ring from scratch; the ring removed at step 1,065,312; the second layer added
  as the identity at 1,127,936; the slow windows shortened to 16 / 64 ticks by 1,456,944; then the learning
  rate stepped down by half cosines, 0.02 → 0.01 → 0.005 → 0.0025, from 1,501,536. The
  [spec](https://github.com/siliconperception/vla/blob/main/docs/spec/README.md) lists every step.

## Evaluation (at the published step, 1,680,000)

The reference is EleutherAI's [pythia-70m](https://huggingface.co/EleutherAI/pythia-70m): a transformer of a
similar total size (70 M parameters, 19 M of them outside the token embedding and output layer) with the same
tokenizer, so losses per token compare directly. Pythia publishes checkpoints from early in training, so it is
shown at about this model's training tokens (steps 128 and 256 bracket it) as well as fully trained. Every model
is scored on the same documents and pairs, by the same rule.

| | **this model** | pythia-70m | pythia-70m | pythia-70m |
|---|---|---|---|---|
| training tokens | **420 M** | 268 M (step 128) | 537 M (step 256) | 300 B (final) |
| FineWeb held-out (100 documents, nats/token) | **4.613** | 7.420 | 6.355 | 3.731 |
| BabyLM 2026 dev (100 pieces, nats/token) | **4.608** | 6.866 | 5.718 | 3.250 |
| BLiMP (1,005 pairs from all 67 paradigms), % | **70.3** | 51.8 | 51.4 | 75.7 |
| ComVE (999 pairs, common sense), % | **64.5** | 56.5 | 57.1 | 69.7 |

Losses are the mean over documents of each document's mean loss per token, from a zero state (this model) or a
bare document start (pythia); a document with any token over 20 nats is counted as a runaway and left out
(2 % of the FineWeb documents for this model). Pythia was trained on the Pile, this model on FineWeb, so the FineWeb row is
in-domain for this model only. Matched tokens are not matched training: pythia's 268 M and 537 M tokens are only
128 and 256 optimizer updates of 2 M tokens each, still inside its learning-rate warm-up, while this model's are
1,680,000 updates of 250 tokens. Fully trained pythia-70m is the fair reference, and this model is still well
short of it. A pair is right when the model gives the correct sentence the lower total loss,
each sentence read without context. For scale on the pairs: babyllama-10m-2024 (trained on 10 M words) scores
70.0 / 63.7 and SmolLM2-135M 80.9 / 79.3.

## Samples

From the prompt in bold, with these weights. Locally fluent, not yet coherent:

> **My grandmother's recipe for apple pie starts with** almond and olive oil, green tea and apple, salt, garlic. I added a pair of the salsa cheese, and the balsamic vinegar in a pureed, salsa.

> **The colors of the rainbow are** beautiful and unique. It is a place of mystery, with light tones that lightens the sunlight in it and its speciality.

## Limits

A small model early in training: it writes locally fluent text that is often not factual or consistent. Not
instruction-tuned, not safety filtered beyond its training corpora. The voice and image decoders are present but
this model has been trained on text only.

## License

MIT, Copyright (c) 2024-2026 Silicon Perception Inc. The license covers the software and these weights and grants
no patent rights; see [PATENTS](https://github.com/siliconperception/vla/blob/main/PATENTS). Frozen third-party
weights inside: EleutherAI [pythia-31m](https://huggingface.co/EleutherAI/pythia-31m) embedding and output
layer (Apache-2.0).
