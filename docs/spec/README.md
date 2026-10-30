# VLA functional specification (model)

This is what the model computes, tick by tick, for the published configuration (`siliconperception/vla_v502`,
run v502). It specifies the function, not an implementation. `vla.py` is the reference: where this text and the
code disagree, the code is right and this text is a bug.

## Dimensions

| Symbol | Value | Meaning |
|---|---|---|
| S | 7 | grid side (positions S × S = 49) |
| N | 512 | register channels |
| C | 384 | working channels of the state update |
| E | 256 | token embedding width (pythia-31m) |
| V | 50,304 | vocabulary (pythia-31m BPE) |
| K | 2 | registers |
| W | 512, 1 | register windows, in ticks (fixed) |
| D | 8 | depth of the state update |
| L | 1,024 | recall ring length, in entries (one per tick) |
| R | 2 | channels of a ring entry (an entry is R × S × S = 98 values) |
| H, d | 8, 64 | attention heads and their width |
| f | 25 Hz | tick rate in training (a 20 s register window, a 41 s ring) |

## State

The registers R_1, R_2 (each N × S × S) and the ring entries e_1 … e_L (oldest first, each R × S × S),
together 2·N·S·S + L·R·S·S = 50,176 + 100,352 = 150,528 values. The state never grows. At the start of an example
(the `<NUL>` input) every register and every ring entry is set to zero; an all-zero entry is an empty slot.

## Inputs per tick

- **Token grid T** (E × S × S): the current token's embedding t (frozen, from pythia-31m), scaled to unit RMS
  over its E channels, copied to every grid position. A `<NUL>` or empty tick gives T = 0.
- **Audio grid A** (256 × S × S): fixed log-mel features of the last ~2 s of sound (no weights). Zero for text.
- **Voice and image token grids** (E × S × S each): the model's other two output streams fed back, built like T.
  Zero for text.

The multimodal design adds an image grid (a frozen ResNet-50 feature map); this configuration has none.

## One tick

1. **Recall.** One attention read of the ring, from the state before this tick:
   - query q = Q( concat(t̂, e_L) ), 256 + 98 → H·d, split into H heads q_h (t̂ the normalized token vector,
     e_L the newest entry, flattened);
   - for every slot j: key k_j = K e_j (98 → d); value v_j = V e_j + V′ e_{j+1} (98 → d each, e_{L+1} = 0), so a
     value also carries what followed its entry. One key and one value per slot serve all heads. Keys carry no
     position or age;
   - per head: scores s_hj = q_h · k_j / √d over the non-empty slots, plus a sink of score 0 and value 0;
     p_h = softmax over them; r_h = Σ_j p_hj v_j;
   - a = Out( concat(r_1 … r_H) ), H·d → E, then scaled to unit RMS over its E channels (ε = 1e-12) and copied to
     every grid position: the recall grid G (E × S × S).
2. **Read.** Each register is scaled, per grid position, to unit RMS over its N channels:
   R̂_k = R_k / √(mean_c R_k² + 1e-6).
3. **Mix.** X = Conv1×1( concat(T, A, T_voice, T_image, G, R̂_1, R̂_2) ), from 4·256 + 256 + 2·512 = 2,304
   channels to C = 384.
4. **Update.** For d = 1 … D: X ← ReLU( BN_d( Conv3×3_d(X) ) ), C → C, zero padding. At inference BN_d normalizes
   each channel with its stored running mean and variance (no learned scale or shift).
5. **Project.** O = Conv3×3(X), C → N, zero padding.
6. **Write the registers** (a Laplacian-pyramid cascade):
   - R'_1 = R_1 + (O − R_1) / W_1
   - R'_2 = O − R'_1 (W_2 = 1: a plain write)

   so the registers always sum to O: R_1 holds the slow part of O (a 512-tick average), R_2 the rest.
7. **Write the ring.** The new entry is Conv1×1( concat(T, O) ), E + N = 768 → R channels. The oldest entry e_1 is
   dropped, the others move one slot older, and the new entry becomes e_L.
8. **Decode** (three independent decoders, one per stream: text, voice, image). Each is a linear tree of
   unpadded convolutions, 3×3 (N → 256, 7 → 5), 3×3 (256 → 256, 5 → 3), 3×3 (256 → E, 3 → 1), then the frozen
   pythia-31m output layer (E → V), plus one trained logit for `<NUL>` ("say nothing this tick").
9. **Emit.** Each stream samples its next token or `<NUL>` by min-p sampling: only tokens with at least P times
   the top token's probability are kept. P is stored with the weights; training keeps adjusting it so that the
   model's own text from `<NUL>` scores a fluency of 100 (P = 0.0141 at step 1,000,000).

## Training (for reference)

Weights are trained from scratch with one token per row per step, 250 rows, plain SGD (learning rate rising along
a half cosine from 4e-4 to 0.02 over the first 20,000 steps, then held), cross-entropy normalized per word rather
than per token, with truncated backpropagation through time over 16 steps. Text only (FineWeb sample-10BT). Frozen:
the token embedding and the output layer.

## Parameters

| Part | Parameters | Trained |
|---|---|---|
| Recall: query (Q) | 181,760 | yes |
| Recall: key, value, next value (K, V, V′) | 18,944 | yes |
| Recall: output (Out) | 131,328 | yes |
| Ring entry (1×1) | 1,538 | yes |
| Mix (1×1) | 885,120 | yes |
| Update (8 × 3×3) | 10.62 M | yes |
| Project (3×3) | 1.77 M | yes |
| Decoders (3 trees + `<NUL>` heads) | 7.08 M | yes |
| Token embedding | 12.88 M | frozen |
| Output layer (shared by the 3 decoders) | 12.88 M | frozen |
| **Total** | 46.45 M (20.69 M trained) | |
