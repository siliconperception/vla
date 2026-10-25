# Consolidated plan (2026-10-24): training metrics and prompt optimization

Supersedes the orderings in PLAN_interaction_2026-10-24.md (its reasoning still stands).

## Where things stand

- **Live run:** v460 `v460_v455_shards14_40M` = v455 on 14 fineweb shards, no write gate (the gate was reverted 2026-10-24: no gain in EVALG delta, drifted 77 → 67% in 50K-token free runs).
- **What works:** free-running from a zero state. GEN fluency is about 75% in long free runs, flat over 50K tokens (v455). EVALH `own` is about +0.33–0.40: the model holds and re-takes its own topic.
- **What doesn't:** absorbing human text. EVALG delta is about −0.01 on every checkpoint, and EVALC is 54–57%.
- **Sentence-level knowledge (EVALM, new):** BLiMP 67–70%, ComVE 64–66%. These are flat within noise from v442 to v459 (2.9M steps); pythia-70m gets 75.7 / 69.8. Winogrande is at chance up to pythia-160m, so it's dropped.

## A. Training scoreboard (every eval)

| Role | Metric | What it answers |
|---|---|---|
| Guard rail | EVAL loss | Is it still learning text? |
| Primary: free-running | GENSCORE fluency + **min_p** (lower = better) | Is free text fluent without truncation help? |
| Primary: free-running | EVALH `own` / `topic` (100 samples) | Does it hold its own topic? |
| Primary: free-running | **FREE-short** (new, `--eval_free`): 8 streams × 10K tokens, no reset; last-window fluency and drift (last − first) | Does it stay stable when run continuously? |
| Primary: knowledge | **EVALM** (`--eval_pairs 1000`): BLiMP by field, ComVE | Grammar and common sense, in the model's own regime |
| Primary: prompting | **Uptake table** (section B) | Can the model be steered? |
| Watch-only | EVALG cold delta, EVALC, EVALX, EVALR, EVALI | Diagnostics |

EVALM and FREE-short join the training evals at the next relaunch, so v460 isn't touched for them. EVALM costs about 1 min. FREE-short runs on the `--eval_rare` cadence, about 3 min.

## B. Prompt optimization: one table, every method scored the same way

The same 50 EVALG prompts, the same judge (Qwen2.5-1.5B), the same 128-token continuation. Per method: **delta** (judge nats of the continuation without the prompt minus with it), fluency, rep1, and for P2 the prompt NLL reached.

| | Method | Model change | Status |
|---|---|---|---|
| P0 | Cold: read the prompt from a zero state (today's EVALG) | none | delta ≈ −0.01 |
| P1 | Warm start: free-run K tokens, then read the prompt as an interruption | none | to do |
| P2 | **State tuning:** optimize the initial registers (5 × 512 × 7 × 7 = 125K numbers) by gradient so the model predicts the prompt, then continue | none (weights frozen) | **next** |
| P3 | Selection: N free-runs from zero, the judge picks the best fit to the prompt | none | upper bound on what's reachable |

**P2 details:**
- `model.step` doesn't detach, so BPTT through the prompt at inference needs no change to training code.
- Adam on h0, about 100 iterations over the 128-token prompt, all 50 prompts as one batch: minutes on the shared GPU.
- Regularize h0 toward states the model actually visits (match per-register RMS from free runs, or L2), so the tuned state stays in distribution.
- Variants: (a) tune h0, then teacher-force the prompt and continue; (b) tune the state *at the end* of the prompt, then continue.
- **Two readouts:** how far prompt NLL falls (can the state encode the prompt at all?), and continuation delta (does the model carry it forward?).

**Decision rule:**
- **P2 delta clearly > 0 (≳ +0.1):** prompting is solved enough to go on to the question/answer pilot and context-conditioned common-sense probes. P2 is also the FPGA-friendly form, since the chip can load a precomputed state.
- **Prompt NLL falls but delta stays ≈ 0:** the state can hold the prompt, but the dynamics don't use it, which points to training (e.g. the 1-token gradient horizon). That would be the key finding.
- **Prompt NLL barely falls:** the state can't represent arbitrary text, so the limit is capacity.

## C. Knowledge and capacity

- **EVALM is flat, so the question is whether that's capacity or data/objective.** The synthetic-biography capacity test (bits stored per parameter) answers it directly; it's small and runs alongside the trainer.
- **Common-sense judging of free-run text:** an instruct LM counts world-model violations in FREE/GEN text. That needs Qwen2.5-3B-Instruct downloaded (about 6 GB; fits next to the trainer).

## D. Later

- The question → external answer → continue pilot (PLAN_interaction §3), using whichever of P1–P3 wins.
- `--continuous` text training (no state reset at documents), judged by FREE.
- Active learning with replay and EMA slow weights (EVALR: an SGD imprint lasts about 2K steps).

## Order

1. **P2 state tuning plus P1 warm start** (`--prompt_tune`), scored as the uptake table on a v460 checkpoint copy.
2. Add `--eval_free` (FREE-short); add it and `--eval_pairs 1000` to the training evals at the next relaunch.
3. The question/answer pilot with the best prompting method.
4. Capacity test.
5. Instruct-LM common-sense judging.
