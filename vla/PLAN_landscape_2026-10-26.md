# Project landscape (2026-10-26)

A step back from the run-by-run plans: the objective, where the model stands, what has been learned, and the open bets. The detailed plans stay where they are: PLAN_memory_2026-10-25.md (memory in the weights), PLAN_consolidated_2026-10-24.md (scoreboard, prompting), PLAN_interaction_2026-10-24.md (free-running, question/answer), PLAN.txt (register history to 2026-10-10).

## 1. The objective, worked backward

| Stage | Target | Status |
|---|---|---|
| **End** | Single-chip ASIC VLA, no external parts, ≥ 100 Hz. Inputs: audio, video, time series. Outputs: audio, time-series actions. A prompt interface and a monitor interface on the inner voice | Architecture is chip-shaped (shared-kernel CNN on a 7×7 grid, DFF registers, 1-tick gradient). Video + audio in, three token streams, worked at 25 Hz (v443–v453). No time series, no audio or action output yet |
| **Intermediate** | Text-only model a person can chat with: not smart, but everyday common sense | Not there. Free-running text is fluent-ish; the model does **not** take up human text (see §3) |
| **Training phase 2** (TBD) | Fine-tuning, RL, or interactive learning, possibly on Q&A data or with a live AI teacher | Not started; the question/answer pilot (PLAN_interaction §3) is designed, not run |
| **Pretraining** (now) | A good base for phase 2 | v472 on FineWeb sample-10BT |

Budgets (soft): ≈ 100M weights for the ASIC, ≈ 15M for an FPGA, the frozen token embedding and lm_head not counted. Registers are cheap (state, not weights).

## 2. Where the model stands (v472, 2026-10-26)

- **Architecture:** pythia-31m tokenizer (embedding and lm_head frozen, 12.9M each) → token grid 7×7 → ctx_cat (concat of token grid + 5 register reads → 384) → ContextCNN 8 × (3×3 conv, BatchNorm, ReLU) → 512 → five DFF registers as a Laplacian-pyramid cascade (windows 128 / 32 / 8 / 2 s at 25 Hz, plus a plain copy) → decoder tree → lm_head. Three stream decoders (text / voice / image) kept from the video work. **20.1M trainable.**
- **Training:** SGD, lr 0.01 constant, batch 250, 1-token gradient horizon (state detached), loss divided by word count, `<NUL>` targets on the idle voice/image streams. ≈ 20 steps/s on the single RTX 4090 ≈ 430M tokens/day.
- **History:** ≈ 9.55M steps ≈ 2.4B tokens, about 120 tokens per trainable weight (part of it video). The lineage runs v395 (text) → v398–v413 (images) → v421–v453 (video + audio) → v455 (text only, FineWeb) → v472.
- **Scores:**
  - Held-out FineWeb EVAL ≈ 4.56 (100 docs), level with v461/v462 at 8.65M. It has been essentially flat for about 1M steps.
  - GEN fluency is held at 100% by the min_p controller; min_p ≈ 0.008 (lower is better).
  - EVALM: BLiMP 67–70%, ComVE 64–67%, flat within noise from v442 to now (≈ 4M steps). pythia-70m scores 75.7 / 69.8.
  - EVALH own ≈ +0.35: the model holds and re-takes its own topic.
  - EVALL: 10K-token free runs are stable (fluency ≈ 70–87% depending on the eval path, no drift).

## 3. What has been learned (the load-bearing findings)

1. **The recurrent CNN works as a language model, slowly.** Loss keeps falling, but the curve is near flat, and grammar and common-sense probes (EVALM) haven't moved in 4M steps. Either capacity (20M weights) or data/objective is the limit; the planned capacity test (synthetic biographies) would tell which. It was never run.
2. **Free-running works; absorbing human text doesn't.** From a zero state the model writes on-topic and holds its topic. Fed a human prompt, it does not carry it forward:
   - EVALG delta ≈ −0.01 on every checkpoint.
   - EVALC 54–57%, near chance.
   - Benchmarks that score answers given a context (PIQA, HellaSwag, COPA) were at chance for every design.
   - Tuning the start state by backprop (`--prompt_tune`) memorizes the prompt but makes the continuation worse.

   **This is the main obstacle to the chat milestone.** The leading suspect is the 1-token gradient horizon: nothing in training rewards keeping information for a later token beyond what the leaky registers do by default.
3. **Registers:**
   - The 5-register Laplacian cascade with RMS read norm is the best design found.
   - Read norm alone was worth 0.22 nats.
   - Learned windows drift slow-first.
   - Without the slow pair of registers, long-term weight memory halves (3b).
   - Changing the ladder 2× either way leaves forgetting unchanged (3c).
   - Slower registers help long free runs in the one-shot eval, though not yet in v472's in-training EVALL.
4. **Memory in the weights:**
   - Forgetting follows a power law, memory ≈ 0.106·(age/5K steps)^−0.44, like human forgetting. It is interference, not decay.
   - Memory per token barely depends on batch size; lr scales the amount written but not the shape of the curve.
   - Batch 1 is feasible at a low lr. The held-out cost is −0.04 at lr 1e-5, against −0.29 at 4e-5.
   - Frozen BatchNorm (what an FPGA or a batch-1 learner would run) costs ≈ 0.07, growing with position in the document. **Normalization is a hardware and continual-learning issue to settle.**
5. **Multimodal lessons** (from v421–v453):
   - Hearing was barely used unless training forced it.
   - Self-feedback of the model's own words on caption ticks hurt.
   - Resetting the state per clip helped.
   - Predicting `<NUL>` beat masking the loss.
   - A fixed log-mel front end (no weights) is the hardware-friendly choice.
   - Register windows are set in seconds (`--ctx_tau`), so a model can move from 25 Hz to 100 Hz without retraining from scratch.
6. **Sampling:** without min_p truncation, free text is about 50% fluent. With min_p ≈ 0.01 the controller holds it at 100%. In hardware, sampling is a small fixed block.
7. **Data:** sample-10BT, 14 shards, is about 1 pass in 40M steps. Samples drift into web boilerplate: event listings, legal disclaimers, shop text. Little of FineWeb is dialogue or everyday physical common sense.

## 4. Register clock rates (the question of 2026-10-26)

- **Tried once:** `--ctx_every N1,N2,...` (2026-10-10, old code, removed in the 2026-10-14 rewrite). Register k updated once every N_k tokens, writing the box-average of its input over those tokens at rate 1−(1−1/W)^N, so its window stayed W tokens. It was a short test in the v346–v364 SimpleStories / fineweb-edu register series, logged only as "tried, not adopted". The numbers weren't kept.
- **Why it's worth reopening now:** at ≥ 100 Hz the slow register's window is 12,800 ticks (128 s), and an exponential moving average at rate 1/12,800 needs ≥ 14 fractional bits to move at all. Updating it every N ticks (rate N/12,800, box-averaged input) is the standard multi-rate fix (cf. Clockwork RNN). It also lets the slow part of the ContextCNN read run on a slow clock. It costs little to test: a warm-start from v472 at a 2× or 4× decimation of the slow pair, scored like 3c.
- **Related:**
  - `--datarep N` (Sept, v72–v77) gave the model N ticks per token, the opposite direction.
  - `--clock_hz 25` runs the whole model on a fixed clock, so text arrives at variable rates.

## 5. Open questions and bold bets

One GPU means about one 3-hour or one 3-day experiment at a time, so each bet below is chosen to decide something.

**A. Data: is FineWeb the right pretraining distribution for a common-sense chat model?** On disk:
- **BabyLM-2026-Strict:** 100M words, ≈ 130M tokens; child-directed speech (CHILDES), spoken BNC, Switchboard, OpenSubtitles, Simple Wikipedia, Gutenberg. One pass is ≈ 7 h. BLiMP, which EVALM already uses, is BabyLM's own benchmark, and the BabyLM baseline models are cached (babyllama-10m/100m-2024, the gpt-bert baselines), so the results are externally comparable.
- SimpleStories, TinyStories, Cosmopedia, tiny-textbooks, LittleCurriculum, smol-smoltalk (chat), the Pile, C4, dclm-edu.

Bets:
1. **Score the BabyLM baselines and pythia-14m/31m with EVALM** (minutes, CPU or shared GPU). This gives the yardstick for "common sense per weight".
2. **Fork v472 onto BabyLM** (continued pretraining, about 1–3 passes, 7–20 h). Watch EVALM, EVALH, GEN samples, and a BabyLM held-out loss. The question: does a spoken, everyday distribution move BLiMP and ComVE, which FineWeb hasn't in 4M steps?
3. **BabyLM from scratch** (Strict track, about 10 passes ≈ 3 days). A clean architecture comparison against published 10M–100M-word results. It is also a fast iteration loop for architecture bets, since a pass is 7 h, not 3 days.

**B. Gradient horizon (architecture).** The 1-token horizon is the deepest assumption, and finding 2 points straight at it. Bet: truncated backprop through time over k = 4–16 ticks, as a fork of v472 at a smaller batch. Score it on EVALG delta and EVALC (prompt uptake), not only loss. If uptake moves, the chat milestone opens. On-chip learning cost would then depend on k, which matters for the deployed continual learner.

**C. Capacity.** 20M of a 100M budget is used. EVALM is flat, so either capacity or data limits it. The synthetic-biography capacity test (small, can share the GPU) answers that. A 2× widening (c_context 384 → 768) by warm-start widening is the matching bold run.

**D. Normalization.** Replace batch statistics with something that runs at batch 1: frozen BatchNorm folded into the convs, or a per-sample norm. Frozen BN costs 0.07 today. Settling it now avoids a mismatch later between training, the chip, and continual learning.

**E. Register clock decimation** (§4): warm-start, 3c-style, a few hours.

**F. Phase 2 readiness:** the question/answer pilot (PLAN_interaction §3) with the best prompting method, once A or B gives any prompt uptake.

**Suggested order:** A1 (minutes) → A2 (overnight, while thinking about B) → B (the decisive bet) → A3 or C, depending on what A2 and B show. E and D fit between them as short warm-starts.

## 6. Approximating the user's log reading (proposal)

The user's process: read the logs and the generated samples by eye, notice patterns and surprises, form an intuition. A mechanical approximation:

1. **`exp/logwatch.py <run>`, a surprise digest:**
   - For every metric line type (STEP, EVAL*, GENSCORE), the latest values against a rolling median ± MAD and the run's own trend. Flag jumps over 3 MAD, trend breaks, and new extremes.
   - All GEN samples since the last digest, with text features: person/pronoun mix, repetition, boilerplate share (URLs, ©, dates, lists), dialogue share, and the topic words that dominate.
   - The best and worst GENSCORE samples quoted verbatim.
2. **On every status check,** I read the digest *and* a handful of raw samples, and add a short "noticed" list: patterns, surprises, hypotheses. It is kept apart from the numbers and logged to log/notes/<run>.md, so it builds up over the run.
3. **Optionally on a timer** (/loop, every 2–3 h) while a run is live, so surprises surface without being asked.

Examples of what this would have caught by itself:
- v467's first-person voice traced to its last training documents.
- v469's EVALL fluency rising instead of falling.
- The STARTUP time jumping to 436 s with eval_at_start.

## 7. Bet tracker (kept current until every bet is closed)

| # | Bet | Status | Result / decision rule |
|---|---|---|---|
| 1 | Yardstick: reference LMs on EVALM | **closed** 2026-10-26 (log/sweeps/yardstick_2026-10-26) | v472 ≈ pythia-14m ≈ babyllama-10m (BLiMP ~69, ComVE ~65); babyllama-100m 74.1 / 68.8; TinyStories-33M best small ComVE 70.1 |
| 2 | v472 continued on BabyLM | **running**: v473 `v473_v472_babylm`, launched 2026-10-26 09:42 from v472 step 9726244, 1.5M steps (≈ 3 passes of ≈ 480K steps; ≈ 20 h). Data: exp/babylm_prep.py → /data/babylm2026_docs (200K docs, 96.7M words, 1/32 held out) | Watch EVALM per pass (BLiMP / ComVE vs 68.5 / 65.7), held-out babylm and fineweb, EVALH, EVALC, GEN samples. Success: ≥ +2 on BLiMP or ComVE (> 1 sd) without losing the free-running quality |
| 3 | Gradient horizon: truncated BPTT over k = 4–16 ticks | open (needs code) | Score on EVALG delta and EVALC (prompt uptake) |
| 4 | BabyLM from scratch (or capacity test / 2× widening) | open, after 2 and 3 | Depends on 2 and 3 |
| 5 | Short warm-starts: register clock decimation (`--ctx_every` revisited); batch-1-capable normalization | open | 3c-style score |
