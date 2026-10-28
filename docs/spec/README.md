# VLA functional specification (model)

This is what the model computes, tick by tick, for the published configuration (`siliconperception/vla`,
run v485). It specifies the function, not an implementation. `vla.py` is the reference: where this text and the
code disagree, the code is right and this text is a bug.

## Dimensions

| Symbol | Value | Meaning |
|---|---|---|
| S | 7 | grid side (positions S × S = 49) |
| N | 512 | register channels |
| C | 384 | working channels of the state update |
| E | 256 | token embedding width (pythia-31m) |
| V | 50,304 | vocabulary (pythia-31m BPE) |
| K | 5 | registers |
| W | 530.4, 57.39, 15.27, 3.783, 1 | register windows, in ticks (learned; stored in the weights as θ, W = 1 + e^θ) |
| D | 8 | depth of the state update |
| f | 25 Hz | tick rate (21 s, 2.3 s, 0.61 s, 0.15 s windows) |

## State

K registers R_1 … R_K, each N × S × S, together N·K·S·S = 125,440 values. At the start of an example (the
`<NUL>` input) every register is set to zero.

## Inputs per tick

- **Token grid T** (E × S × S): the current token's embedding e (frozen, from pythia-31m), scaled to unit RMS
  over its E channels, copied to every grid position. A `<NUL>` or empty tick gives T = 0.
- **Image grid I** (2048 × S × S): a frozen ResNet-50 feature map of the current camera crop, each position
  scaled to unit RMS over its channels; refreshed at 2 Hz. Zero for text.
- **Audio grid A** (256 × S × S): fixed log-mel features of the last ~2 s of sound (no weights). Zero for text.
- **Voice and image token grids** (E × S × S each): the model's other two output streams fed back, built like T.
  Zero for text.

## One tick

1. **Read.** Each register is scaled by a constant: R̂_k = R_k / σ_k, where σ_k is the register's RMS measured
   over training (a stored buffer, fixed at inference).
2. **Mix.** X = Conv1×1( concat(T, I, A, T_voice, T_image, R̂_1 … R̂_K) ), from 256 + 2048 + 256 + 2·256 + 5·512
   = 5,632 channels to C = 384.
3. **Update.** For d = 1 … D: X ← ReLU( BN_d( Conv3×3_d(X) ) ), C → C, zero padding. At inference BN_d normalizes
   each channel with its stored running mean and variance (no learned scale or shift).
4. **Project.** O = Conv3×3(X), C → N, zero padding.
5. **Write** (a Laplacian-pyramid cascade). With S_0 = 0 and S_k = R'_1 + … + R'_k:
   - for k = 1 … K−1: R'_k = R_k + (O − S_{k−1} − R_k) / W_k
   - R'_K = O − S_{K−1} (W_K = 1: a plain write)

   so the registers always sum to O, and register k holds the part of O that varies on a time scale near W_k.
6. **Decode** (three independent decoders, one per stream: text, voice, image). Each is a linear tree of
   unpadded convolutions, 3×3 (N → 256, 7 → 5), 3×3 (256 → 256, 5 → 3), 3×3 (256 → E, 3 → 1), then the frozen
   pythia-31m output layer (E → V), plus one trained logit for `<NUL>` ("say nothing this tick").
7. **Emit.** Each stream samples its next token (min-p sampling at P = 0.0092 by default) or `<NUL>`.

## Training (for reference)

Weights are trained with one token per row per step, 250 rows, plain SGD (learning rate 0.04 in the latest
phase), cross-entropy normalized per word rather than per token, with truncated backpropagation through time over
16 steps. The windows W_k (k < K) are trained by Adam on θ_k: the sensitivities ∂R_k/∂(1/W_j) are carried forward
with the registers (exact for the write rule above, with O held fixed), so the gradient of the windows sees every
past tick, not only the last 16. Frozen: the token embedding, the output layer, the ResNet-50.

## Parameters

| Part | Parameters | Trained |
|---|---|---|
| Mix (1×1) | 2.16 M | yes |
| Update (8 × 3×3) | 10.63 M | yes |
| Project (3×3) | 1.77 M | yes |
| Decoders (3 trees + `<NUL>` heads) | 7.08 M | yes |
| Register windows θ | 4 | yes (Adam) |
| Token embedding | 12.88 M | frozen |
| Output layer (shared by the 3 decoders) | 12.88 M | frozen |
| ResNet-50 | 23.56 M | frozen |
