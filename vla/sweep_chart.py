#!/usr/bin/env python
"""Plot the lr-sweep loss curves. Re-run any time; it draws whatever has landed.

    python sweep_chart.py [--out sweep_loss.png] [--stability]

x is log-scaled on purpose. sweep_analyze.py fits L = a + b*ln t, so on a log x
axis that model is a straight line: a steeper line is literally a faster drop, and
"which is dropping fastest" is read off the slope by eye instead of inferred.

lr is an ordered quantity, so the series take an ordinal ramp (one hue, light->dark
with increasing lr) rather than categorical hues -- adjacent lr values then read as
adjacent shades. Steps and surfaces are the data-viz reference palette, used as
documented; the light ramp starts at step 250, the lightest step clearing 2:1 on
this surface.
"""

import argparse
import glob
import os
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np                # noqa: E402

import sweep_analyze as sa        # noqa: E402

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK2 = '#52514e'
GRID = '#e3e2df'
# ordinal blue ramp, steps 250..700 (light surface: no lighter than 250)
RAMP = ['#86b6ef', '#6da7ec', '#5598e7', '#3987e5', '#2a78d6',
        '#256abf', '#1c5cab', '#184f95', '#0d366b']

BASELINE = 'log/log.2026.07.31-16.07.08'


def load(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, '*.log'))):
        m = re.search(r'lr_([0-9.]+)\.log$', os.path.basename(p))
        if not m:
            continue
        step, loss, grad, dff = sa.parse(p)
        if len(step) < 5:
            continue
        out.append({'lr': float(m.group(1)), 'lrs': m.group(1), 'step': step,
                    'loss': loss, 'grad': grad, 'dff': dff})
    return sorted(out, key=lambda r: r['lr'])


def place_labels(ax, items, gap_px=13):
    """Draw end-of-curve labels, nudged apart so near-equal finals stay readable.

    items: [(x, y, text, color)]. Sorted by y, then each label is pushed up only as
    far as it needs to clear the one below it, in display space so the spacing is
    honest regardless of the axis scale.
    """
    if not items:
        return
    items = sorted(items, key=lambda t: t[1])
    ys = [ax.transData.transform((x, y))[1] for x, y, _, _ in items]
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < gap_px:
            ys[i] = ys[i - 1] + gap_px
    for (x, y, text, color), ypx in zip(items, ys):
        xpx = ax.transData.transform((x, y))[0]
        yd = ax.transData.inverted().transform((xpx, ypx))[1]
        ax.annotate(f' {text}', (x, y), xytext=(x, yd), textcoords='data',
                    color=color, fontsize=9, va='center', ha='left',
                    fontweight='bold', zorder=20, annotation_clip=False)


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, which='major', color=GRID, lw=0.8, zorder=0)
    ax.grid(True, which='minor', color=GRID, lw=0.4, alpha=0.6, zorder=0)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='log/sweep')
    ap.add_argument('--out', default='sweep_loss.png')
    ap.add_argument('--xmin', type=int, default=300)
    ap.add_argument('--stability', action='store_true',
                    help='add a second panel with dff_std, the disqualifying signal')
    args = ap.parse_args()

    runs = load(args.dir)
    if not runs:
        raise SystemExit(f'no sweep logs in {args.dir}')

    n = 2 if args.stability else 1
    fig, axes = plt.subplots(n, 1, figsize=(11, 4.4 * n + 1.4), sharex=True,
                             gridspec_kw={'height_ratios': [3, 1.4][:n]})
    axes = np.atleast_1d(axes)
    fig.patch.set_facecolor(SURFACE)
    ax = axes[0]
    style(ax)

    # prior 982k run at lr 0.01, truncated to the sweep window: the reference for
    # "is this point ahead or behind". Drawn as an annotation, not a series.
    if os.path.exists(BASELINE):
        bs, bl, _, _ = sa.parse(BASELINE)
        k = bs <= max(r['step'][-1] for r in runs)
        if k.sum() > 5:
            ax.plot(bs[k], bl[k], color=INK2, lw=1.4, ls='--', zorder=3,
                    label='lr 0.01 — prior 982k run (reference)')

    ncol = len(runs)
    labels = []
    for i, r in enumerate(runs):
        c = RAMP[int(round(i * (len(RAMP) - 1) / max(1, ncol - 1)))] if ncol > 1 \
            else RAMP[4]
        r['c'] = c
        ax.plot(r['step'], r['loss'], color=c, lw=2.0, zorder=4 + i,
                label=f'lr {r["lrs"]}', solid_capstyle='round')
        labels.append((r['step'][-1], float(np.mean(r['loss'][-20:])), r['lrs'], c))

    ax.set_xscale('log')
    ax.set_xlim(args.xmin, max(r['step'][-1] for r in runs) * 1.45)
    # y range from the plotted window only, so the step-0 transient cannot set it
    vis = [r['loss'][r['step'] >= args.xmin] for r in runs]
    vis = np.concatenate([v for v in vis if len(v)])
    ax.set_ylim(min(vis.min(), 1.8) * 0.97, vis.max() * 1.03)
    ax.set_ylabel('loss  (mean over 100 steps)', color=INK2, fontsize=10)
    ax.text(0.0, 1.075, 'LR sweep — loss vs training step', transform=ax.transAxes,
            color=INK, fontsize=13, fontweight='bold', va='bottom')
    ax.text(0.0, 1.018,
            'log x: the fitted L = a + b·ln t is a straight line here, so a steeper '
            'line is a faster drop',
            transform=ax.transAxes, color=INK2, fontsize=9.5, va='bottom')
    leg = ax.legend(frameon=False, fontsize=9, labelcolor=INK2, loc='upper right',
                    ncol=2)
    leg.set_zorder(30)
    fig.canvas.draw()            # labels need final transforms
    place_labels(ax, labels)

    if args.stability:
        ax2 = axes[1]
        style(ax2)
        for r in runs:
            ax2.plot(r['step'], r['dff'], color=r['c'], lw=2.0, zorder=4)
        ax2.axhline(sa.DFF_ABS, color='#e34948', lw=1.2, ls=':', zorder=3)
        ax2.annotate(f' blow-up threshold {sa.DFF_ABS}', (args.xmin, sa.DFF_ABS),
                     color='#e34948', fontsize=8.5, va='bottom', ha='left')
        # the step-0 spike is 20x the steady value; scale to the steady band or the
        # panel becomes a single spike and a flat line
        # the transient runs several hundred steps, so scale off the settled window
        dv = np.concatenate([r['dff'][r['step'] >= 2000] for r in runs
                             if (r['step'] >= 2000).any()] or
                            [np.array([sa.DFF_ABS])])
        ax2.set_ylim(0, max(sa.DFF_ABS * 1.25, float(dv.max()) * 1.15))
        ax2.set_ylabel('dff_std', color=INK2, fontsize=10)
        ax2.set_title('state stability — dff_std (rising = the documented failure mode; '
                      'startup transient above the panel is clipped)',
                      color=INK2, fontsize=10, loc='left', pad=8)

    axes[-1].set_xlabel('training step (log scale)', color=INK2, fontsize=10)
    fig.tight_layout()
    fig.savefig(args.out, dpi=150, facecolor=SURFACE)
    print(f'wrote {args.out}  ({len(runs)} runs: '
          f'{", ".join(r["lrs"] for r in runs)})')


if __name__ == '__main__':
    main()
