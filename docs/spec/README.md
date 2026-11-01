# VLA functional specification (model)

This is what the model computes, tick by tick, for the published configuration (`siliconperception/vla`,
run v533). It specifies the function, not an implementation. `vla.py` is the reference: where this text and the
code disagree, the code is right and this text is a bug.

## Dimensions

| Symbol | Value | Meaning |
|---|---|---|
| S | 7 | grid side (positions S × S = 49) |
| N | 512 | register channels, and the width of the layer's output |
| C | 384 | working channels of the state update |
| E | 256 | token embedding width (pythia-31m) |
| V | 50,304 | vocabulary (pythia-31m BPE) |
| L | 1 | recurrent layers |
| K | 2 | registers |
| W | 16, 1 | register windows, in ticks: the first is the starting point of its learned write rate (1/16), the second is fixed |
| D | 8 | depth of the state update |
| f | 25 Hz | tick rate in training (a 16-tick window is 0.64 s) |

## State

Two registers R₁, R₂ (each N × S × S): 2 · N · S · S = 50,176 values in all. The state never grows. At the start
of an example (the `<NUL>` input) both registers are set to zero.

## Inputs per tick

- **Token grid T** (E × S × S): the current token's embedding t (frozen, from pythia-31m), scaled to unit RMS
  over its E channels, copied to every grid position. A `<NUL>` or empty tick gives T = 0.
- **Audio grid A** (256 × S × S): fixed log-mel features of the last ~2 s of sound (no weights). Zero for text.
- **Voice and image token grids** (E × S × S each): the model's other two output streams fed back, built like T.
  Zero for text.

The multimodal design adds an image grid (a frozen ResNet-50 feature map); this configuration has none.

## One tick

The read of a register is the register scaled, per grid position, to unit RMS over its N channels:
R̂ = R / √(mean_c R² + 1e-6). `Update` below is D times X ← ReLU( BN_d( Conv3×3_d(X) ) ), C → C, zero padding,
where at inference BN_d normalizes each channel with its stored running mean and variance (no learned scale or
shift).

1. **Mix:** X = Conv1×1( concat(T, A, T_voice, T_image, R̂₁, R̂₂) ), 4·256 + 2·512 = 2,048 channels → C.
2. **Update** X, giving the working state h (C × S × S), then **project:** o = Conv3×3(h), C → N, zero padding.
3. **Write gate:** a = σ( Conv1×1_gate(h) ), C → N: one write rate in (0, 1) for every channel and grid position
   of R₁, recomputed every tick. Its weights were initialized to zero and its bias to logit(1/16) = −ln 15, so it
   started as the fixed rate 1/16 (a 16-tick average).
4. **Write the registers** as a Laplacian-pyramid cascade (⊙: elementwise):
   - R'₁ = R₁ + a ⊙ (o − R₁)
   - R'₂ = o − R'₁ (window 1: a plain write)

   so the registers always sum to the output: R₁ holds the slow part, an average whose window the model sets
   per channel and position, R₂ the rest.
5. **Decode** (three independent decoders, one per stream: text, voice, image). Each reads o and is a linear tree
   of unpadded convolutions, 3×3 (N → 256, 7 → 5), 3×3 (256 → 256, 5 → 3), 3×3 (256 → E, 3 → 1), then the frozen
   pythia-31m output layer (E → V), plus one trained logit for `<NUL>` ("say nothing this tick").
6. **Emit.** Each stream samples its next token or `<NUL>` by min-p sampling: only tokens with at least P times
   the top token's probability are kept. P is stored with the weights; training keeps adjusting it so that the
   model's own text from `<NUL>` scores a fluency of 100 (P = 0.0088 at step 3,043,841).

## Training (for reference)

Weights are trained with one token per row per step, 250 rows, SGD (at the published step: Nesterov momentum 0.95,
learning rate 0.001, the write gate's weights at 100 × that), cross-entropy normalized per word rather than per
token, with truncated backpropagation through time over 64 steps (activations recomputed per tick in the backward
pass). Text only (FineWeb sample-10BT). Frozen: the token embedding and the output layer. The configuration
changed during training, each change resuming from the latest weights; "a → b" for the learning rate is a half
cosine over the given steps, then held:

| Steps | Change |
|---|---|
| 0 | from scratch: one layer, register windows 512 and 1, plus a recall ring of 1,024 ticks read by attention; plain SGD, truncated backpropagation over 16 steps; learning rate 4e-4 → 0.02 over 20,000 steps |
| 1,065,312 | recall ring and attention removed |
| 1,127,936 | a second layer added in series as the identity (its projection zero-initialized, its mix passing the first layer's output through); its output added to the first layer's |
| 1,321,120 | both layers' slow windows 512 → 64 |
| 1,361,152 | both 64 → 16 |
| 1,456,944 | layer 2's slow window 16 → 64 |
| 1,501,536 | learning rate 0.02 → 0.01 over 20,000 steps |
| 1,581,808 | 0.01 → 0.005 |
| 1,653,648 | 0.005 → 0.0025 (the previous release, v511, is this configuration at step 1,680,000) |
| 2,219,568 | 0.0025 → 0.00125; momentum 0.1 |
| 2,263,328 | 0.00125 → 0.001; momentum 0.2 |
| 2,269,536 | Nesterov momentum 0.2 |
| 2,372,644 | momentum (not Nesterov) cycled from 0 to 0.9 every 40,000 steps |
| 2,538,191 | layer 2's slow window 64 → 256; momentum 0 |
| 2,566,001 | layer 2 removed (it never used its registers); the write gate added on the 16-tick register, starting at the fixed rate 1/16; truncated backpropagation 16 → 64 steps; learning rate 0.001 → 0.01 over 2,000 steps |
| 2,607,025 | the write gate's weights at 100 × the learning rate |
| 2,960,001 | momentum 0.5 |
| 2,987,329 | Nesterov momentum 0.95 |
| 2,994,305 | learning rate 0.001 (the published configuration) |

## Parameters

| Part | Parameters | Trained |
|---|---|---|
| Mix (1×1, 2,048 → 384) | 786,816 | yes |
| Update (8 × 3×3, with BN) | 10.62 M | yes |
| Project (3×3, 384 → 512) | 1.77 M | yes |
| Write gate (1×1, 384 → 512) | 197,120 | yes |
| Decoders (3 trees + `<NUL>` heads) | 7.08 M | yes |
| Token embedding | 12.88 M | frozen |
| Output layer (shared by the 3 decoders) | 12.88 M | frozen |
| **Total** | 46.21 M (20.45 M trained) | |
