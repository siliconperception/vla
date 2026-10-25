# Plan: free-running, prompting and interaction (2026-10-24)

Context: during v459 (`v459_v455_rat4_shards14_40M`) the model reliably holds and re-takes a topic it chose itself, starting from a zero state (EVALH `own` ≈ +0.35–0.44). It does not absorb human-written prompts (EVALG `delta` ≈ −0.01 to −0.05 on every checkpoint). The user's direction: lean into what works (free-running from zero init), and get creative about prompting, e.g. stop generation at a "?", answer it externally, and see whether the model interacts. If that's feasible, it opens an active-learning track.

## 1. Training: score what works

Make free-running quality the primary scoreboard:
- **EVALH:** `self`, `topic` and `own`, i.e. whether the model holds and re-takes its own topic.
- **Sampling quality:** GENSCORE fluency, min_p and `rep1`.
- **EVAL loss:** as the guard rail.

EVALG `delta` and EVALC drop to watch-only; they measure following human text, which we're now treating as a separate problem. One tweak: EVALH's 50 samples are noisy, about ±0.05 on `topic`. Raise it to 100 at the next relaunch; it's cheap, about 35 s per eval.

## 2. Prompting: work with the model's own state, not against it

The evidence says a state the model reached by itself is in-distribution. A cold state that reads human text isn't. Three ways to use that, cheapest first:

- **Selection (no model change):** free-run N samples from the zero state and let a judge LM pick the one that best fits the prompt, or steer by picking among branches every K tokens. Prompting becomes search over what the model already does well. It's crude, but it works from day one, and it tells us how much of the prompt's topic is reachable at all.
- **Warm start:** free-run for a while, then feed the prompt. The registers are then in a state the model knows, and the prompt arrives as an "interruption" mid-thought. That's closer to how a person hears a question than starting from a blank state. It's a one-line change to `generate`, and EVALG can score it directly.
- **State tuning, the adaptive version:** at inference, optimize the initial register state, 5×512×7×7 ≈ 125K numbers, by gradient so that the model predicts the prompt text well, then free-run from it. It's prefix tuning on the state, with BPTT only through the prompt and only at inference. The weights are untouched, so it doesn't conflict with the 1-token training horizon. It's the most powerful option and I'd expect it to work best. It's also the most hardware-relevant: an FPGA could load a precomputed state.

**Skip a random init.** Training always starts documents from zero, so random states are out of distribution; that's the opposite of what's working.

## 3. Question → external answer → continue

**It's feasible.** In v459's recent GEN output, **41 of 123 samples contain a "?"**. The questions are semi-grammatical but real: "What do you think of a date that you're thinking about?", "The last book?", "We are a global consumer, right?". The pilot, offline so training is untouched:
1. Free-run from the zero state on a v459 checkpoint, about 200 times, stopping at the first "?".
2. Get an answer for each: one or two plain sentences, in the model's own register. Short and low-surprise is better, since we know high-surprise human text sends its state off course.
3. Feed the answer as input tokens, let the model continue for about 128 tokens, and score **answer uptake** = judge nats on the continuation without the answer minus with it. That's EVALG `delta`, but inside the model's own conversation.
4. Control: the same answer fed to a cold state. If uptake is positive in the warm case and not the cold one, the bottleneck is the cold start, not external text as such. That would be a key finding for all the prompting options above.

**Who answers:**
- **Claude, for the first ~30.** That's the quickest look and needs no setup. Also read the transcripts, since at this stage reading them tells more than the numbers.
- **A local instruct model at scale,** for hundreds of exchanges. The GPU has about 18 GB free next to v459, enough for Qwen2.5-3B-Instruct comfortably (about 6 GB). A 7B (about 15 GB) would risk OOM-killing the trainer, so it should go on the CPU or wait for a gap between runs.

## 4. The active-learning track, and what EVALR says about it

If uptake is positive, the loop writes itself: the model asks, the teacher answers, and we train on the exchange. That's curiosity-driven data: it chooses what it gets taught. **EVALR sets one hard constraint:** an SGD imprint lasts only about 2K steps, +0.19 nats, half gone by 10K, nothing after. Anything taught that way fades within a few thousand steps unless it's replayed or consolidated. So the track needs two pieces from the start:
- **A replay buffer** of good exchanges, re-fed on a schedule.
- **A slow copy of the weights,** an EMA, that keeps what survives. EVALR on taught versus untaught material then measures exactly what's being retained. The tool for that already exists.

## Suggested order

1. **Offline (CPU plus Claude's answers):** the question/answer pilot on about 30 questions, plus the warm-start variant of EVALG.
2. **If warm uptake is positive:** scale it with a local instruct model, and prototype state tuning.
3. **If either works:** design the active-learning loop around replay and consolidation.

v459 keeps training throughout.

## Measurements behind this plan (v459, steps 7.82M–8.08M)

EVALR gain vs held-out (nats/token), mean over 14 evals: 0–2K steps since read **+0.19** (14/14 positive), 2K–10K **+0.08**, 10K–50K −0.03, 50K–200K −0.03, 200K–1M −0.05 (4 evals). Verbatim overlap `ovl` stays 0.01–0.02 in every band.

## Future goal (user, 2026-10-24): continuous running and continuous learning

The application is embodied AI. The VLA runs continuously, with no state reset between "examples", and eventually it learns continuously while deployed. Training today is episodic (the state resets at every example's `<NUL>`), so that gap needs closing. Constraints already known: the registers are leaky averages with bounded memory (slowest window 64 s), and the 1-token gradient horizon makes on-chip learning cheap (no BPTT memory). EVALR shows an SGD imprint lasts about 2K steps, so on-line learning will need replay and slow (consolidated) weights.

## Follow-up (2026-10-24): the user's three points, and the revised order

**1. Parameter efficiency: plausible, so measure it.** The ~2 bits per parameter figure comes from transformers. Nothing measures it for a recurrent CNN, so whether ours does better is open.
- **Against:** storing *distinct* facts needs distinct free parameters. Weight sharing reuses each weight at 49 positions and every step, which multiplies compute, not storage.
- **For:** common sense is mostly *rules*, not facts ("cups hold liquid", "people answer questions"). Shared weights applied everywhere are a strong bias toward learning rules. That's where the CNN could beat a transformer on what a parameter is worth.

**Test:** a synthetic-biography capacity test. N made-up people with a few attributes each, in a fixed template. Train until the loss stops falling, then count the bits stored from teacher-forced loss on the attribute tokens. Training and test text share one format, so it's in-distribution and needs no prompting. It's the quantitative version of the v280 memorization test, small enough to run on the GPU between long runs.

**2. EVALK needs prompting: agreed, with a way around it.** Likelihood probes like PIQA or HellaSwag score answers *given a context*, which is the same weakness (EVALC sits at 54–57%). They'd stay near chance. Two measurements work in the model's native regime instead:
- **Minimal pairs from a zero state.** Score two short complete sentences, each read from scratch, and check that the sensible one gets the lower loss: "She poured the milk into the glass" vs "She poured the glass into the milk". The only context is the sentence's own 10–20 tokens, and EVALX shows the model does use context at that range (+0.6 nats at 8–15 tokens). Sources: BLiMP for grammar, and existing "which sentence makes sense" common-sense pair sets (both small downloads).
- **Judging free-run output for common sense.** An instruct LM (Qwen2.5-3B-Instruct fits next to the trainer) reads GEN/EVALH samples and counts world-model violations: impossible physics, wrong social causality, contradictions. That measures what the model "believes" when it thinks on its own.

**3. Episodic training vs a continuously running VLA.** This is the biggest train/deploy gap.
- **Long free-run stability:** EVALH only runs 256 tokens; a deployed model runs for hours. Generate 10K–100K tokens with no reset, and track fluency, `rep1` and topic drift over time. The registers are leaky averages with a 64 s horizon, so it *should* stay stable. Nothing has tested that on text.
- **Continuous text training:** `--continuous` carries the state across document boundaries instead of resetting, so the model learns to "move on" mid-stream. The cost is that a document's start is no longer a clean slate, which could hurt the zero-init free-running that works now. The long free-run eval measures exactly that.
- **Continuous learning later:** the 1-token gradient horizon is an asset. On-device learning needs only one step of backprop per token and no memory of past states, so an FPGA can do it. EVALR says it also needs fast/slow weights (learn online in a small fast set, consolidate slowly) plus replay. That fits a three-level memory: registers for seconds, fast weights for minutes to hours, slow weights for general knowledge.

**Revised order:**
1. Long free-run stability eval, offline on a v459 checkpoint, as a standalone option like `--generate`.
2. Minimal pairs and free-run common-sense judging, as the common-sense scoreboard.
3. Capacity test (synthetic biographies).
4. The question/answer pilot (section 3 above).
