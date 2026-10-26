# v474_v472_babylm_lanes — noticed

## 2026-10-26 11:25, step 9817400 (91K steps in)
- Held-out: fineweb 4.560 -> 4.807 (9.74M) -> 4.827 (9.80M), forgetting is flattening; babylm docs 4.687 -> 3.415;
  lanes 4.234 -> 4.008. Train loss ~3.4 docs / ~3.8 lanes.
- EVALM 9.8M: BLiMP 67.4 / ComVE 65.1 (v472 68.5 / 65.7) -- within noise, no gain yet.
- EVALC 53.0%, EVALH own +0.357 (from +0.336).
- GENSCORE min_p 0.0076-0.0082 (v472) -> 0.0105-0.0125 (9.78-9.80M) -> 0.0093-0.0100 (9.81M): rose, now easing back.
- GEN from <NUL> is almost all Simple Wiki (19/45 bios/places/communes, 5/45 CHILDES dialogue, 0 Switchboard):
  91% of marked documents are wiki articles (110,286 + 3,843 appended to open_subtitles of 124,895), so the
  reset prior is "wiki article". Subtitles/BNC live only in lanes, which never reset, so GEN cannot show them.
- Wiki GEN is fluent but confabulated (born 1940, "won in 1991", "born ... in 1962"; He/She swaps).
- TXT-SAMPLE labels work: [babylm row r] and [babylm_lanes:open_subtitles_1 row r].
