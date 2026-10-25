# Plan: short- vs long-term memory in the weights (2026-10-25)

**Goal (user):** training is treated as continual learning, as in humans. Find a knob that moves the balance between short- and long-term memory *in the weights*. The DFF registers handle real-time in-context memory; this plan is about what SGD writes into the weights. The user's framing: the learning rule stays fixed, but SGD and backprop can be modulated.

**Score for every experiment:**
- **Paired forgetting curve** (`vla.py --doc_score`, `log/sweeps/forgetting_2026-10-25/pair.py`): document-specific memory at ages ~5K, 20K, 65K, 200K and 500K steps. This is *episodic* memory.
- **Held-out loss and EVALM:** *semantic* memory, the part that generalizes.
- **EVALL:** free-running quality.

More episodic memory is only a win if semantic memory doesn't pay for it.

## Baseline (v461, measured 2026-10-25)

Document-specific memory, nats/token, ±1 s.e.:

| Age (steps) | Memory |
|---|---|
| 5K | +0.106 ± 0.009 |
| 20K | +0.064 ± 0.014 |
| 65K | +0.041 ± 0.007 |
| 200K | +0.030 ± 0.005 |
| 500K | +0.014 ± 0.004 |

Held-out improvement over the same 700K steps: +0.010.

Forgetting follows a power law, about 0.106·(age/5K)^−0.44, which is the human (Ebbinghaus/Wixted) shape. Forgetting is interference, not decay: weight decay is 0. That is one snapshot (cross-sectional), so a time series is needed.

## Steps

| # | Step | Status |
|---|---|---|
| 0 | **Snapshot watcher** (`exp/snapwatch.sh <run>`): copy the checkpoint every 100K steps, for longitudinal per-document curves | running (v461, then v462 from 08:56); restart it for each new run |
| 1 | **Weight EMA, measurement only** (`--weight_ema 10000,100000`, `--use_ema T`): slow copies of the weights. EVAL lines `fineweb~ema10K` / `~ema100K` at every eval; offline `--doc_score --use_ema T` gives each copy's forgetting curve. Training is unchanged. **v462** = v461 + `--weight_ema 10000,100000` | **running:** v462 `v462_v461_wema_40M` launched 2026-10-25 08:53 from checkpoint/v461_v460_evalfree_40M.step8646887.pt |
| 2 | **Analysis A:** longitudinal forgetting curves from the snapshots (same documents tracked over time). Fit the power law, and check whether the exponent drifts with training time | after 2–3 snapshots (≥ 300K steps) |
| 3b | **Is weight memory keyed on the DFF register context?** Paired curve with registers read as their mean (`--doc_score --doc_ablate`) | **done** (log/sweeps/ctxmem_2026-10-25): yes. Without the 64 s + 16 s pair, long-term memory (200K–500K) and the held-out gain about halve; the 64 s register alone changes nothing; without the fast pair, short-term memory is nearly gone. The register ladder plausibly shapes what the weights keep |
| 3c | **DFF register ladder change, warm-started** (e.g. `--ctx_tau 128,32,8,2`, or a slower 5th register) from the same checkpoint; score its forgetting curve against the control. No from-scratch retrain is needed: the rates aren't in the checkpoint (loss with no adaptation: 4.569 trained ladder, 4.603 2× slower, 4.583 2× faster); a different register *count* needs a small widening change | proposed (user, 2026-10-25) |
| 3 | **Analysis B:** EMA vs live weights. Per average: held-out loss, forgetting curve (short-term part removed?), EVALM. Tells what a slow copy keeps, and predicts what step 6 buys | after ~300K steps of v462 (the 100K average needs ~3τ to forget its start) |
| — | *(EMA steps 1/3 on hold: user, 2026-10-25, "disregard the weight-ema changes for now". v462 still carries `--weight_ema`, which is harmless.)* | — |
| 4 | **Spaced replay** (`--replay` to build): re-feed recorded documents at ages ~2K / 20K / 200K in a small share of rows; compare replayed vs not at 500K. Does one well-timed replay move a memory into the long tail? | to do, training change |
| 5 | **Batch-size ladder toward batch 1** (the deployed continual learner is batch 1): B = 250, 250 with frozen BatchNorm, 32, 4, 1; lr ∝ B (lr/B = 4e-5); `--bn_frozen` below 250; 1M training tokens each (≈ 11 h of robot time at 25 tokens/s) from v462's step-8723091 checkpoint; every document recorded; paired forgetting curve with **age in tokens** (log/sweeps/batch_2026-10-25: queue.sh, score.sh, pair_tokens.py). Runs v463–v467, then v462 resumes | **running** from 2026-10-25 10:04: v463–v466 done, v467 (B = 1) due ≈12:10; scoring under way |
| 5+ | Later cells: lr 0.005 at B = 250, B = 500 at lr 0.01 / 0.02 (temperature vs update count); B = 1 on one continuous stream (`--continuous`, no resets), i.e. full deployment conditions; replay as the "batch" of a batch-1 learner | after 5 |
| 6 | **Fast + slow weights** W = W_slow + W_fast (the explicit knob: the fast copy has a high LR and decays, the slow copy has a low LR; inference uses the sum) | after 3–5 show the direction |
| — | Other modulation dials, kept in reserve (Lookahead-style pull toward a slow copy, 5b, dropped by the user): per-token/per-document write gain (salience, surprise), per-weight plasticity (EWC-style, Adam vs SGD), momentum | — |

Rules: one trainer on the GPU at a time. Each training-change experiment gets its own vNNN, runs from the same checkpoint for about 300–500K steps, and is scored as above.

## Status log

- **2026-10-25:** baseline curve measured (commit b9dd652); watcher started on v461; `--weight_ema` built and tested on the CPU (commit b64af9c).
- **2026-10-25 08:53:** v461 stopped at 8646887 (SIGTERM save; copy `.step8646887.pt`, which serves as the pre-read checkpoint for v462's documents). v462 launched with `--weight_ema 10000,100000`; the EMA costs nothing measurable (22.7 steps/s). The watcher pattern is anchored (`^python vla.py`) after shells quoting it kept the v461 watcher alive. Note: grep `corpus fineweb ` (with the space) for the live EVAL line; the averages log as `fineweb~ema10K` / `~ema100K`.
- **Next checkpoints:** snapshots at 8.7M, 8.8M, ... (watcher). Analysis B is meaningful from about 8.95M (3τ for the 100K average).
- **2026-10-25 10:04:** 3b done (commit 02ee893). The DFF ladder change warm-starts (no from-scratch run needed). `--bn_frozen`, `--doc_keep`, and a save at the last `--run_steps` step were tested on the CPU at batch 1 (≈15 steps/s on the CPU). v462 stopped at 8723091 (snapshot 8.7M taken); the batch ladder queue started.

- **2026-10-25 11:25:** ladder rungs v463–v466 done; v467 (batch 1) running at ≈200 steps/s, due ≈12:10, then v462 resumes. Training loss: batch 4 flat at ≈4.58; batch 1 rose 4.63 → 4.72 over its first 100K tokens and has stayed there (watch). Scoring of v463–v466 has started (score.log). v463 (batch 250): held-out −0.003 ± 0.002; memory +0.199 (0–30K tokens), +0.195 (30–100K), +0.170 (100–300K), +0.129 (300K+).
