# (g, r) response surface, batch 1 (2026-10-02)
g = --linout_gain (init scale of the single linout conv), r = register gain = g * --dff_write_scale.
Metric: mean training loss over steps 5-10K, matched data (seed 20261002, --no-shuffle --workers 1).

| run  | g    | r      | 5-10K |
|------|-----:|-------:|------:|
| v234 | 2.00 | 1.0000 | 6.418 |
| v238 | 2.00 | 0.7071 | 6.365 |
| v239 | 2.00 | 0.5000 | 6.318 |
| v242 | 2.00 | 0.3536 | 6.274 |
| v243 | 2.00 | 0.2500 | 6.240 |
| v240 | 2.83 | 1.0000 | 6.330 |
| v241 | 2.83 | 0.7071 | 6.280 |
| v245 | 2.83 | 0.5000 | 6.228 |
| v250 | 2.83 | 0.1250 | 6.120 |
| v251 | 2.83 | 0.0625 | 6.116 |
| v252 | 4.00 | 0.2500 | 6.076 |
| v253 | 4.00 | 0.1250 | 6.063 |
| v254 | 5.66 | 0.2500 | 6.023 |
| v255 | 5.66 | 0.1250 | 5.997 |
| v249 | 2.83 | 0      | 6.340 (no memory; not in fit) |

Fit loss = a + b lg + c lg^2 + d lr + e lr^2 + f lg lr (lg = log2 g, lr = log2 r): rms 0.0041, max |res| 0.0106.
Best r at each g: 2.83 -> 0.079, 4 -> 0.091, 5.66 -> 0.105, 8 -> 0.121 (extrapolated).
g: still improving ~0.055 per sqrt(2) step at 5.66; fitted curvature is weak, so the g optimum is not located.

## Batch 2 (5-10K training loss)
| run  | g     | r    | decoder lr | 5-10K | dff_max |
|------|------:|-----:|-----------:|------:|--------:|
| v256 | 8     | 0.12 | x1         | 5.996 | 0.16 |
| v257 | 11.3  | 0.14 | x1         | 6.024 | 0.53 |
| v258 | 2.83  | 0.08 | x4         | 5.998 | 0.11 |
| v259 | 2.83  | 0.08 | x16        | 5.973 | 0.10 |
g saturates at ~5.66-8 and turns over by 11.3. A decoder lr multiplier at g=2.83 reproduces it
(x4 ~ g x2, i.e. the g^2 scaling) and x16 beats every large-g run.
