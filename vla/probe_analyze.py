#!/usr/bin/env python
"""Analyse the replicated lr probes: how sharp is the minimum, relative to the noise?

The sweep's weakness was that every lr ran once, so the winning margin (0.10) could not
be compared against the run-to-run spread. These probes replicate each lr across seeds,
which makes three things measurable:

  sigma_run   pooled within-lr standard deviation across seeds. This is the noise floor.
  curve       mean loss per lr, with the standard error of that mean.
  sharpness   curvature of a parabola in log10(lr), and -- the part that matters --
              the depth of the minimum expressed in units of sigma_run.

A minimum is "sharp" only if moving one grid step away costs more than sigma_run. If it
does not, the honest answer is a plateau and any lr in the flat region will do.
"""

import argparse
import glob
import os
import re

import numpy as np

import sweep_analyze as sa


def load(d, tail):
    """-> {lr: {seed: mean_loss}} using the last `tail` steps of each probe."""
    out = {}
    for p in sorted(glob.glob(os.path.join(d, 'lr_*_s*.log'))):
        m = re.search(r'lr_([0-9.]+)_s(\d+)\.log$', os.path.basename(p))
        if not m:
            continue
        lr, seed = float(m.group(1)), int(m.group(2))
        step, loss, grad, dff = sa.parse(p)
        if len(step) < 20:
            continue
        k = step >= step[-1] - tail
        out.setdefault(lr, {})[seed] = (float(np.mean(loss[k])),
                                        float(np.mean(dff[k])),
                                        int(step[-1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='log/probe')
    ap.add_argument('--tail', type=int, default=5000,
                    help='average the loss over this many final steps')
    args = ap.parse_args()

    data = load(args.dir, args.tail)
    if not data:
        raise SystemExit(f'no probe logs in {args.dir}')
    lrs = sorted(data)
    seeds = sorted({s for v in data.values() for s in v})

    print(f'probe results — mean loss over the last {args.tail} steps\n')
    hdr = f'{"lr":>8} ' + ' '.join(f'{("s%d" % (s % 100)):>8}' for s in seeds) + \
          f' {"mean":>8} {"sd":>7} {"sem":>7} {"n":>3}'
    print(hdr)
    print('-' * len(hdr))

    means, sems, sds, ns = {}, {}, {}, {}
    for lr in lrs:
        vals = [data[lr][s][0] for s in seeds if s in data[lr]]
        cells = ' '.join(f'{data[lr][s][0]:>8.4f}' if s in data[lr] else f'{"-":>8}'
                         for s in seeds)
        mu = float(np.mean(vals))
        sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else float('nan')
        sem = sd / np.sqrt(len(vals)) if len(vals) > 1 else float('nan')
        means[lr], sds[lr], sems[lr], ns[lr] = mu, sd, sem, len(vals)
        print(f'{lr:>8.4f} {cells} {mu:>8.4f} '
              f'{sd if sd == sd else 0:>7.4f} {sem if sem == sem else 0:>7.4f} '
              f'{len(vals):>3}')

    rep = [lr for lr in lrs if ns[lr] > 1]
    if not rep:
        print('\nonly one seed so far — no variance estimate yet; the curve below is '
              'provisional')
        sigma = float('nan')
    else:
        # pooled within-lr sd: the noise floor a real lr effect has to clear
        dof = sum(ns[lr] - 1 for lr in rep)
        pooled = sum((ns[lr] - 1) * sds[lr] ** 2 for lr in rep) / dof
        sigma = float(np.sqrt(pooled))
        print(f'\nsigma_run (pooled within-lr sd, {dof} dof) = {sigma:.4f}')

    best = min(lrs, key=lambda k: means[k])
    print(f'\nbest sampled lr: {best:.4f}  (loss {means[best]:.4f})')

    # depth of the minimum in units of the noise
    print(f'\ncost of moving away from lr {best:.4f}:')
    print(f'{"lr":>8} {"delta":>8} {"in sigma":>10}')
    for lr in lrs:
        if lr == best:
            continue
        d = means[lr] - means[best]
        z = d / sigma if sigma == sigma and sigma > 0 else float('nan')
        print(f'{lr:>8.4f} {d:>+8.4f} {z:>9.1f}s' if z == z
              else f'{lr:>8.4f} {d:>+8.4f} {"-":>10}')

    # parabola in log10(lr)
    if len(lrs) >= 3:
        x = np.log10(lrs)
        y = np.array([means[lr] for lr in lrs])
        a, b, c = np.polyfit(x, y, 2)
        print(f'\nparabola in log10(lr): curvature a = {a:+.3f}')
        if a > 0:
            vert = 10 ** (-b / (2 * a))
            print(f'  vertex (estimated optimum) = {vert:.4f}')
            # how far must lr move for the fitted loss to rise by one sigma?
            if sigma == sigma and sigma > 0:
                half = np.sqrt(sigma / a)      # in decades
                print(f'  loss rises by 1 sigma_run at {vert * 10 ** -half:.4f} '
                      f'and {vert * 10 ** half:.4f}')
                print(f'  -> anything in that band is statistically indistinguishable '
                      f'from the optimum')
        else:
            print('  curvature is negative — these points do not describe a minimum')

    # stability sanity check
    print('\ndff_std (max across seeds):')
    for lr in lrs:
        dv = max(data[lr][s][1] for s in data[lr])
        flag = '  <-- above threshold' if dv > sa.DFF_ABS else ''
        print(f'{lr:>8.4f} {dv:>8.3f}{flag}')


if __name__ == '__main__':
    main()
