#!/usr/bin/env python
"""Rank lr-sweep runs by extrapolated loss, and check gradient/DFF stability.

Picking the lowest loss at the end of a short sweep point is the wrong criterion: a
high lr wins early and flattens, a low lr trails early and is still descending. What
matters for the 4M-step run is where each curve is *headed*.

So fit the usual scaling-law form to each run

    L(t) = L_inf + A * t**-alpha

and extrapolate. For a fixed alpha this is linear in (L_inf, A), so it is a 2x2 least
squares solve; alpha is found by scanning. No scipy needed.

Extrapolating 55k -> 4M is a 73x extension and is only as good as the form. Run
    python sweep_analyze.py --validate log/log.2026.07.31-16.07.08
to fit a long run's first --fit_steps and score the prediction against what it
actually did, which puts an honest error bar on every number below.

Two forms are fitted, because on the baseline they disagree on the absolute answer
but not on the shape:

    power   L = L_inf + A * t**-alpha      (L_inf unconstrained)
    log     L = a + b * ln t               (b < 0; the drop per e-fold of steps)

Measured against log.2026.07.31-16.07.08, fitting 5k..55k and predicting 982k: log
-linear +1.2%, power +3.3%, both over-predicting (conservative). Constraining
L_inf >= 0 was much worse (+17.6%) and is not offered.

But the same check over other windows (5k..30k, 20k..55k) swings the 4M number
between 0.54 and 1.37. So treat the absolute extrapolated loss as indicative only.
What survives that sensitivity is the *ordering*: every run here is fitted over an
identical window with identical forms, so the systematic bias is common-mode. Rank
on it, don't quote it. If the two forms disagree on the winner, the sweep has not
separated those points and the tie should be broken on stability instead.

Stability thresholds are calibrated against the baseline rather than guessed, because
the obvious rule ("grad still rising = bad") is wrong here. Over 5k..55k -- the exact
window the sweep gives -- the known-good lr 0.01 baseline has grad +8.6% and RISING.
Grad norm climbs through the first ~100k steps of a healthy run (5.20 -> 6.48), then
flattens and decays. Disqualifying on that would have rejected the one lr we know
trains cleanly to 982k. So:

    grad     rising is normal early. Flag only above +25% (baseline: +8.6%).
    dff_std  the real signal, and the one this codebase has actually blown up on
             (dff_std -> 21, then NaN). Baseline holds 0.72 to within +-1.5% over
             every window from 5k..20k out to 5k..982k. Flag above +10%, or on an
             absolute level above 2.0.

Absolute grad *level* is not comparable across lr and is not used: under BatchNorm
scale-invariance g ~ 1/||w||, and ||w||^2 grows as lr^2*||g||^2, so a lower lr keeps
||w|| smaller and its grad norm correspondingly larger. A low-lr run reading 2x the
baseline's grad norm is that effect, not instability.

usage:
    python sweep_analyze.py                       # rank log/sweep/*.log
    python sweep_analyze.py --target 4000000      # extrapolation horizon
    python sweep_analyze.py --validate <log>      # score the method on a long run
"""

import argparse
import glob
import os
import re
import sys

import numpy as np

STEP_RE = re.compile(r'^STEP\s')


def parse(path):
    """-> (step, loss, grad, dff_std) arrays from a vla.py log."""
    s, l, g, d = [], [], [], []
    with open(path, errors='replace') as f:
        for line in f:
            if not STEP_RE.match(line):
                continue
            t = line.split()
            try:
                kv = {t[i]: float(t[i + 1]) for i in range(len(t) - 1)
                      if t[i] in ('loss', 'grad', 'dff_std')}
                s.append(int(t[1]))
                l.append(kv['loss'])
                g.append(kv['grad'])
                d.append(kv['dff_std'])
            except (ValueError, KeyError, IndexError):
                continue
    o = np.argsort(s)
    return (np.array(s, float)[o], np.array(l)[o],
            np.array(g)[o], np.array(d)[o])


def fit_power(step, loss, alphas=None):
    """Least-squares fit of L = L_inf + A*t**-alpha. -> (L_inf, A, alpha, rmse).

    For fixed alpha the model is linear in (L_inf, A), so solve that exactly and
    scan alpha over a log grid. Coarse-to-fine: a second pass refines around the
    best coarse alpha.
    """
    if len(step) < 20:
        return None

    def solve(alpha):
        X = np.column_stack([np.ones_like(step), step ** -alpha])
        coef, *_ = np.linalg.lstsq(X, loss, rcond=None)
        resid = loss - X @ coef
        return coef, float(np.sqrt(np.mean(resid ** 2)))

    if alphas is None:
        alphas = np.logspace(np.log10(0.02), np.log10(2.0), 120)
    best = min((solve(a) + (a,) for a in alphas), key=lambda r: r[1])
    # refine around the coarse winner
    a0 = best[2]
    fine = np.linspace(max(0.01, a0 * 0.7), a0 * 1.4, 80)
    best = min([best] + [solve(a) + (a,) for a in fine], key=lambda r: r[1])
    (L_inf, A), rmse, alpha = best
    return float(L_inf), float(A), float(alpha), rmse


def predict(fit, t):
    L_inf, A, alpha, _ = fit
    return L_inf + A * float(t) ** -alpha


def fit_log(step, loss):
    """L = a + b*ln t. -> (a, b, rmse); b is the loss drop per e-fold of steps."""
    if len(step) < 20:
        return None
    X = np.column_stack([np.ones_like(step), np.log(step)])
    coef, *_ = np.linalg.lstsq(X, loss, rcond=None)
    rmse = float(np.sqrt(np.mean((loss - X @ coef) ** 2)))
    return float(coef[0]), float(coef[1]), rmse


def predict_log(fit, t):
    a, b, _ = fit
    return a + b * np.log(float(t))


def trend(step, y, frac=0.5):
    """Linear trend over the last `frac` of the run.

    -> (slope per 100k steps, relative change across that window, mean).
    A positive slope on grad or dff_std is the disqualifying signal.
    """
    n = len(step)
    if n < 20:
        return 0.0, 0.0, float(np.mean(y)) if n else 0.0
    i = int(n * (1 - frac))
    s, v = step[i:], y[i:]
    A = np.column_stack([np.ones_like(s), s])
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    slope = coef[1]
    span = s[-1] - s[0]
    mean = float(np.mean(v))
    rel = float(slope * span / mean) if mean else 0.0
    return float(slope * 1e5), rel, mean


# calibrated on the lr 0.01 baseline over 5k..55k: grad +8.6%, dff_std +0.4%
GRAD_TOL = 0.25
DFF_TOL = 0.10
DFF_ABS = 2.0


def verdict(rel, tol=0.05):
    """rel = fractional change across the trend window."""
    if rel > tol:
        return 'RISING'
    if rel < -tol:
        return 'falling'
    return 'stable'


def analyze(path, warmup, target, max_step=None):
    step, loss, grad, dff = parse(path)
    if len(step) == 0:
        return None
    if max_step:
        # compare every run over an identical window: fits over different window
        # lengths are not comparable, and this sweep mixes 50k and 55k runs
        k = step <= max_step
        step, loss, grad, dff = step[k], loss[k], grad[k], dff[k]
        if len(step) == 0:
            return None
    m = step >= warmup
    r = {'path': path, 'n': len(step), 'last_step': int(step[-1]),
         'loss_end': float(np.mean(loss[-50:])),
         'diverged': bool(re.search(r'HALT|non-finite|Traceback|Killed|out of memory',
                                    open(path, errors='replace').read()))}
    if m.sum() < 20:
        r['fit'] = None
        return r
    r['fit'] = fit_power(step[m], loss[m])
    r['pred'] = predict(r['fit'], target) if r['fit'] else None
    r['flog'] = fit_log(step[m], loss[m])
    r['pred_log'] = predict_log(r['flog'], target) if r['flog'] else None
    # window sensitivity: refit on the back 3/4 and see how far the answer moves
    m2 = m & (step >= warmup + (step[m][-1] - warmup) * 0.25)
    f2 = fit_log(step[m2], loss[m2]) if m2.sum() >= 20 else None
    r['pred_log2'] = predict_log(f2, target) if f2 else None
    r['grad'] = trend(step[m], grad[m])
    r['dff'] = trend(step[m], dff[m])
    # A fit predicting loss <= 0 is not a pessimistic estimate, it is an invalid one:
    # cross-entropy has a positive floor, so the log-linear form (which has no
    # asymptote) has run away. Seen on steep high-lr runs. Such a point keeps its
    # measured loss but is barred from the extrapolated ranking.
    r['bad_fit'] = ((r['pred_log'] is not None and r['pred_log'] <= 0)
                    or (r['pred'] is not None and r['pred'] <= 0)
                    or (r['pred_log2'] is not None and r['pred_log2'] <= 0))
    r['grad_v'] = verdict(r['grad'][1], GRAD_TOL)
    r['dff_v'] = verdict(r['dff'][1], DFF_TOL)
    r['dff_hot'] = r['dff'][2] > DFF_ABS
    return r


def lr_of(path):
    m = re.search(r'lr_([0-9.eE+-]+)\.log$', os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='log/sweep')
    ap.add_argument('--target', type=int, default=4_000_000,
                    help='extrapolation horizon in steps (the production run length)')
    ap.add_argument('--warmup', type=int, default=5000,
                    help='drop the initial transient before fitting')
    ap.add_argument('--baseline', default='log/log.2026.07.31-16.07.08',
                    help="prior lr 0.01 run, shown as '0.01*'; '' to omit")
    ap.add_argument('--max_step', type=int, default=50000,
                    help='truncate every run here so all fits share one window')
    ap.add_argument('--validate', default=None,
                    help='score the extrapolation on one long log instead of ranking')
    ap.add_argument('--fit_steps', type=int, default=55000,
                    help='--validate: fit only up to here, then score against the rest')
    args = ap.parse_args()

    # ── validation mode ───────────────────────────────────────────────────────
    if args.validate:
        step, loss, grad, dff = parse(args.validate)
        if len(step) == 0:
            sys.exit(f'no STEP lines in {args.validate}')
        m = (step >= args.warmup) & (step <= args.fit_steps)
        fit = fit_power(step[m], loss[m])
        if fit is None:
            sys.exit('not enough points to fit')
        L_inf, A, alpha, rmse = fit
        print(f'validating extrapolation on {args.validate}')
        print(f'  fit window     steps {args.warmup}..{args.fit_steps} '
              f'({int(m.sum())} points)')
        print(f'  fitted         L_inf {L_inf:.4f}  A {A:.4f}  alpha {alpha:.4f}  '
              f'rmse {rmse:.4f}')
        print(f'  actual range   steps {int(step[0])}..{int(step[-1])}')
        print()
        print(f'  {"step":>10} {"predicted":>10} {"actual":>10} {"err":>9} {"err%":>8}')
        for chk in (100_000, 200_000, 500_000, 982_000, int(step[-1])):
            sel = np.abs(step - chk) < 2500
            if not sel.any() or chk <= args.fit_steps:
                continue
            act = float(np.mean(loss[sel]))
            pr = predict(fit, chk)
            print(f'  {chk:>10} {pr:>10.4f} {act:>10.4f} '
                  f'{pr - act:>+9.4f} {100 * (pr - act) / act:>+7.1f}%')
        print()
        print(f'  extrapolated to {args.target}: {predict(fit, args.target):.4f}')
        return

    # ── ranking mode ──────────────────────────────────────────────────────────
    logs = sorted(glob.glob(os.path.join(args.dir, '*.log')),
                  key=lambda p: float(lr_of(p)) if re.match(r'^[\d.]+$', lr_of(p))
                  else 0.0)
    if not logs:
        sys.exit(f'no logs in {args.dir}')

    rows = []
    for p in logs:
        r = analyze(p, args.warmup, args.target, args.max_step)
        if r:
            r['lr'] = lr_of(p)
            rows.append(r)
    # the 0.01 baseline is not re-run in this sweep; fold its long log in, truncated
    # to the same window, so the table shows what the new points must beat
    if args.baseline and os.path.exists(args.baseline):
        rb = analyze(args.baseline, args.warmup, args.target, args.max_step)
        if rb:
            rb['lr'] = '0.01*'
            rows.append(rb)
    rows.sort(key=lambda r: float(r['lr'].rstrip('*')))

    tgt = f'{args.target // 1000}k'
    print(f'extrapolating to {args.target:,} steps (warmup {args.warmup} dropped)')
    print('absolute values are indicative only (+-~2x); the ordering is the result\n')
    hdr = (f'{"lr":>9} {"steps":>8} {"loss@end":>9} {"slope_b":>8} '
           f'{"L@%s(log)" % tgt:>11} {"L@%s(pow)" % tgt:>11} {"+-":>6} '
           f'{"grad":>7} {"dff_std":>8}  note')
    print(hdr)
    print('-' * len(hdr))
    for r in rows:
        if r['fit'] is None:
            print(f'{r["lr"]:>9} {r["last_step"]:>8} {r["loss_end"]:>9.4f} '
                  f'{"-":>8} {"-":>11} {"-":>11} {"-":>6} {"-":>7} {"-":>8}  too short')
            continue
        note = []
        if r['diverged']:
            note.append('DIVERGED')
        if r['grad_v'] == 'RISING':
            note.append('grad rising')
        if r.get('bad_fit'):
            note.append('FIT INVALID (L@4M<=0)')
        if r['dff_v'] == 'RISING':
            note.append('dff_std RISING')
        if r.get('dff_hot'):
            note.append(f'dff_std {r["dff"][2]:.1f} > {DFF_ABS}')
        sens = (abs(r['pred_log2'] - r['pred_log'])
                if r['pred_log2'] is not None else float('nan'))
        print(f'{r["lr"]:>9} {r["last_step"]:>8} {r["loss_end"]:>9.4f} '
              f'{r["flog"][1]:>8.4f} {r["pred_log"]:>11.4f} {r["pred"]:>11.4f} '
              f'{sens:>6.3f} {r["grad"][2]:>7.2f} {r["dff"][2]:>8.3f}  '
              f'{", ".join(note) if note else "ok"}')
    print('\nslope_b = loss drop per e-fold of steps (more negative = descending faster)')
    print('+-      = shift in L@%s when refitting on the back 3/4 of the window' % tgt)

    print(f'\ngrad / dff_std trend over the last half of each run.')
    print(f'thresholds calibrated on the lr 0.01 baseline, which reads grad +8.6% / '
          f'dff_std +0.4% over this same window:')
    print(f'  grad RISING above +{100 * GRAD_TOL:.0f}%, dff_std RISING above '
          f'+{100 * DFF_TOL:.0f}% or absolute level above {DFF_ABS}\n')
    print(f'{"lr":>9} {"grad mean":>10} {"grad chg":>9} {"":>8} '
          f'{"dff mean":>9} {"dff chg":>9}')
    for r in rows:
        if r['fit'] is None:
            continue
        print(f'{r["lr"]:>9} {r["grad"][2]:>10.2f} {100 * r["grad"][1]:>+8.1f}% '
              f'{r["grad_v"]:>8} {r["dff"][2]:>9.3f} {100 * r["dff"][1]:>+8.1f}% '
              f'{r["dff_v"]:>8}')

    ok = [r for r in rows
          if r['fit'] and not r['diverged']
          and r['grad_v'] != 'RISING' and r['dff_v'] != 'RISING'
          and not r.get('dff_hot') and not r.get('bad_fit')]
    if not ok:
        print('\nno stable runs to rank')
        return

    by_log = sorted(ok, key=lambda r: r['pred_log'])
    by_pow = sorted(ok, key=lambda r: r['pred'])
    print(f'\nranked by extrapolated loss @ {args.target:,} (stable runs only):')
    print(f'{"":>4} {"log-linear":>22}   {"power-law":>22}')
    for i in range(min(5, len(by_log))):
        a, b = by_log[i], by_pow[i]
        print(f'  {i + 1}. lr {a["lr"]:>8} {a["pred_log"]:>8.4f}   '
              f'lr {b["lr"]:>8} {b["pred"]:>8.4f}')

    if by_log[0]['lr'] == by_pow[0]['lr']:
        w = by_log[0]
        runner = by_log[1] if len(by_log) > 1 else None
        margin = (runner['pred_log'] - w['pred_log']) if runner else float('inf')
        sens = abs(w['pred_log2'] - w['pred_log']) if w['pred_log2'] else 0.0
        print(f'\nboth forms agree: lr {w["lr"]}')
        if runner and margin < sens:
            print(f'  BUT margin over lr {runner["lr"]} ({margin:.4f}) is inside this '
                  f'run\'s own window sensitivity ({sens:.4f}) -- treat as a tie '
                  f'and prefer the lower lr for stability margin')
        else:
            print(f'  margin over lr {runner["lr"]}: {margin:.4f} '
                  f'(window sensitivity {sens:.4f})' if runner else '')
    else:
        print(f'\nforms DISAGREE on the winner: log-linear says lr {by_log[0]["lr"]}, '
              f'power-law says lr {by_pow[0]["lr"]}')
        print('  the sweep has not separated these; break the tie on grad/dff_std '
              'stability and prefer the lower lr')


if __name__ == '__main__':
    main()
