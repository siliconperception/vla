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
| 3 | **Analysis B:** EMA vs live weights. Per average: held-out loss, forgetting curve (short-term part removed?), EVALM. Tells what a slow copy keeps, and predicts what step 6 buys | after ~300K steps of v462 (the 100K average needs ~3τ to forget its start) |
| 4 | **Spaced replay** (`--replay` to build): re-feed recorded documents at ages ~2K / 20K / 200K in a small share of rows; compare replayed vs not at 500K. Does one well-timed replay move a memory into the long tail? | to do, training change |
| 5 | **Global learning-rate dial:** lr 0.005 vs 0.01 from the same checkpoint. Does it reshape the curve or only rescale it in step units? | to do, training change |
| 6 | **Fast + slow weights** W = W_slow + W_fast (the explicit knob: the fast copy has a high LR and decays, the slow copy has a low LR; inference uses the sum) | after 3–5 show the direction |
| — | Other modulation dials, kept in reserve: per-token/per-document write gain (salience, surprise), per-weight plasticity (EWC-style, Adam vs SGD), momentum | — |

Rules: one trainer on the GPU at a time. Each training-change experiment gets its own vNNN, runs from the same checkpoint for about 300–500K steps, and is scored as above.

## Status log

- **2026-10-25:** baseline curve measured (commit b9dd652); watcher started on v461; `--weight_ema` built and tested on the CPU (commit b64af9c).
- **2026-10-25 08:53:** v461 stopped at 8646887 (SIGTERM save; copy `.step8646887.pt`, which serves as the pre-read checkpoint for v462's documents). v462 launched with `--weight_ema 10000,100000`; the EMA costs nothing measurable (22.7 steps/s). The watcher pattern is anchored (`^python vla.py`) after shells quoting it kept the v461 watcher alive. Note: grep `corpus fineweb ` (with the space) for the live EVAL line; the averages log as `fineweb~ema10K` / `~ema100K`.
- **Next checkpoints:** snapshots at 8.7M, 8.8M, ... (watcher). Analysis B is meaningful from about 8.95M (3τ for the 100K average).
