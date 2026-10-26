# v475_v472_babylmseq_rs01 — noticed

## 2026-10-26 12:58, step 9804200 (78K steps in)
- Held-out FineWeb 4.560 -> 4.768 (9.74M) -> 4.765 -> 4.847 -> 4.804 (9.80M); v474 at 9.80M: 4.827. babylmseq 4.678 -> 3.683.
- EVALM 9.8M: BLiMP 69.3 / ComVE 64.7 (v472 68.5 / 65.7; v474 at 9.8M 67.4 / 65.1). No +2 yet.
- EVALH own +0.336 -> +0.416 / +0.401 (v474 +0.357). EVALC 52.0%.
- EVALL 9.8M fluency 85.7 -> 75.5 over 10K tokens, drift -10.2 (v474 9.8M: 84.4 -> 74.9, -9.6; v472 9.6M: 65-68, +2.4).
  BabyLM text lifts fluency in both runs; both now lose ~10 points over a 10K-token stream where v472 held flat.
- GENSCORE min_p 0.0060-0.0077 (v472 0.0076-0.0082, v474 0.0093-0.0125): best of the three.
- GEN (39 since start): 8 wiki bios/places, 7 CHILDES dialogue (v474: 19/45 wiki, 5/45 CHILDES) -- pieces put
  more dialogue at <NUL> than whole documents did.
- GEN at 9.802M mixes "Mother:/Child:" with "A:\t" Switchboard turns. Traced: simple_wiki.train.txt lines 512259-642735
  (130,477 lines, ~1.08M words) are Switchboard conversations appended to the Saramago article with no mark (the
  "1.08M-word unmarked Wiki stretch"); real Switchboard is ~1.33M words, not 0.25M. babylm_prep only maps 'A:\t' in
  switchboard.train.txt, so these keep the tab and are labelled simple_wiki. Fix in prep for the next data build
  (split the stretch off as its own document, map the tabs); not worth stopping v475 (~1% of words).
- CHILDES pieces keep inline [..] annotations (297K, e.g. "[don't]"); GEN reproduces them ("[Circola]").
