#!/usr/bin/env python
"""Fit L(N) = E + A*N**-alpha to held-out loss vs training tokens.

The question this answers: is VLA's loss FLAT or still DECREASING?  Comparing endpoints
against pythia is unfair -- pythia-31m saw ~300B tokens, VLA ~25M -- so what matters is
the slope and the irreducible floor E, not the value at one point.

Also fits the same form to the bigram-vs-fit-size curve from exp/ngram.py, because the
relevant claim is not "VLA beats a bigram today" but "VLA is on a steeper trajectory".

Usage: python exp/scaling.py  (data is inline; edit as new checkpoints are scored)
"""
import numpy as np
# no scipy in this env; grid E then solve the remaining log-linear problem exactly.
# For fixed E, log(L-E) = log A - alpha*log N is linear, so least squares is closed form.

def law(N, E, A, al): return E + A * np.power(N, -al)

def fit(N, L, tag, targets=()):
    N = np.asarray(N, float); L = np.asarray(L, float)
    best = None
    lo, hi = 0.0, float(min(L)) - 1e-6
    for _ in range(6):                       # successive refinement on E
        for E0 in np.linspace(lo, hi, 400):
            y = L - E0
            if np.any(y <= 0): continue
            X = np.log(N); Y = np.log(y)
            al, b = np.polyfit(X, Y, 1)
            al = -al; A = float(np.exp(b))
            if al <= 0: continue
            pa = np.array([E0, A, al])
            r = float(np.sqrt(np.mean((law(N, *pa) - L)**2)))
            if best is None or r < best[1]: best = (pa, r)
        Eb = best[0][0]; w = (hi - lo) / 20.0
        lo, hi = max(0.0, Eb - w), min(float(min(L)) - 1e-6, Eb + w)
    p, r = best
    E, A, al = p
    print(f'{tag}')
    print(f'  L(N) = {E:.4f} + {A:.4g} * N^-{al:.4f}     rms {r:.4f}')
    print(f'  irreducible floor E = {E:.4f} nats   (ppl {np.exp(E):.1f})')
    # nats per doubling, evaluated at the last measured point
    Nl = N[-1]
    print(f'  local slope at N={Nl/1e6:.0f}M: {law(Nl,*p)-law(2*Nl,*p):.4f} nats per doubling')
    for t in targets:
        if t <= E:
            print(f'  target {t:.4f}: UNREACHABLE -- below the fitted floor {E:.4f}')
        else:
            Nt = ((t - E) / A) ** (-1.0/al)
            print(f'  target {t:.4f}: needs {Nt:.3g} tokens ({Nt/Nl:.0f}x the last point)')

    # -- competing forms, so the choice is decided by fit rather than assumed --
    # log-linear  L = a - b*ln N   has NO floor: it predicts loss -> -inf, which is
    # physically impossible (loss cannot go below the entropy of the text). It can
    # still be the better DESCRIPTION over a narrow range, and a constant
    # nats-per-doubling is exactly its signature, so it is worth testing directly.
    b_ll, a_ll = np.polyfit(np.log(N), L, 1)
    r_ll = float(np.sqrt(np.mean((a_ll + b_ll*np.log(N) - L)**2)))
    print(f'  [log-linear]  L = {a_ll:.4f} - {-b_ll:.4f}*ln N   rms {r_ll:.4f}   '
          f'({-b_ll*np.log(2):.4f} nats/doubling, CONSTANT, no floor)')
    for t in targets:
        Nt = float(np.exp((t - a_ll)/b_ll))
        print(f'     target {t:.4f}: needs {Nt:.3g} tokens ({Nt/Nl:.0f}x)')
    # pure power law (floor pinned at 0)
    al0, b0 = np.polyfit(np.log(N), np.log(L), 1)
    r_pp = float(np.sqrt(np.mean((np.exp(b0)*N**al0 - L)**2)))
    print(f'  [pure power]  L = {np.exp(b0):.4g}*N^{al0:.4f}   rms {r_pp:.4f}')
    print(f'  BEST BY RMS: ' + min([('floor power',r),('log-linear',r_ll),('pure power',r_pp)],
                                   key=lambda z: z[1])[0])
    return p

# ---- filled in from exp/score.py runs; tokens = steps * 250 (batch 250, 1 token/step)
if __name__ == '__main__':
    import sys, json
    d = json.load(open('exp/scaling_data.json'))
    for tag, rows in d.items():
        N = [r[0] for r in rows]; L = [r[1] for r in rows]
        fit(N, L, tag, targets=(3.8183,))
        print()
