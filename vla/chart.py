# Copyright (c) 2024 Silicon Perception Inc (www.siliconperception.com)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import numpy as np ; print('numpy ' + np.__version__)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#from matplotlib.ticker import MultipleLocator
#from matplotlib.ticker import FuncFormatter
import re
import datetime

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--head', help='remove first head lines from log',default=0, type=int)
parser.add_argument('--log',help='log file name',default='log')
parser.add_argument('--verbose', default=False, action='store_true')
parser.add_argument('--batch', default=False, action='store_true',
                    help='overlay the per-step batch size on the grad panel (secondary y axis)')
parser.add_argument('--outliers', default=False, action='store_true',
                    help='plot every sample. By default the leading samples are dropped until '
                         'the body of the run reaches at least half the height of the loss and '
                         'grad panels, so the startup transient does not set their scale')
parser.add_argument('--sigma', default=0.0, type=float,
                    help='instead of scaling the loss and grad panels to the samples drawn, cap '
                         'them at the median + N standard deviations of the last 1000 samples '
                         '(2 is a readable zoom on the live region); anything above the cap is '
                         'clipped')
args = parser.parse_args()
print(args)
batch_size=0

# STEP lines look like:
#   STEP 100 wall <date> <time> loss <v> grad <v> lr <v> dff_mean <v> dff_std <v> \
#        dff_max <v> dff_zeros <v> batch <v> examples <v> a_std <v> i_std <v> \
#        [loss_txt <v> loss_av <v>]
# Parse each numeric field by name so the layout is robust to the date/time tokens
# and to optional mix-mode fields.
_FIELDS = ['batch', 'loss', 'grad', 'lr', 'dff_mean', 'dff_std', 'dff_max', 'dff_zeros',
           'a_std', 'i_std']
_NUM    = r'(-?[\d.]+(?:[eE][-+]?\d+)?)'

def parselog(fn):
    global batch_size
    step_pat = re.compile(r'^STEP\s+(\d+)')
    wall_pat = re.compile(r'wall\s+(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+)')
    pats     = {k: re.compile(r'\b' + k + r'\s+' + _NUM) for k in _FIELDS}
    data     = {k: [] for k in ['step'] + _FIELDS}
    data['wall'] = []
    with open(fn, 'r') as f:
        for l in f:
            ms = step_pat.match(l)
            if ms:
                data['step'].append(float(ms.group(1)))
                mw = wall_pat.search(l)
                data['wall'].append(mw.group(1) if mw else '')
                for k in _FIELDS:
                    m = pats[k].search(l)
                    data[k].append(float(m.group(1)) if m else 0.0)
            elif l[0:4] == 'ARGS':
                match = re.search(r"batch=(\d+)", l)
                if match:
                    batch_size = int(match.group(1))
    return {k: np.array(v)[args.head:] for k, v in data.items()}

print('loading log file')
d = parselog(args.log)
print('steps', d['step'].shape[0])
print('batch_size', batch_size)

step = d['step']
loss = d['loss']
grad = d['grad']
lr   = d['lr']
mean = d['dff_mean']
std  = d['dff_std']
dmax = d['dff_max']
zero = d['dff_zeros']
# per-step batch size. Logs written before the STEP line carried it have no batch field
# (parsed as 0), so fall back to the single value scraped from the ARGS line.
bs = d['batch']
if not bs.any():
    bs = np.full(step.shape, float(batch_size))
print('batch', 'constant' if bs.min() == bs.max() else f'{bs.min():.0f}..{bs.max():.0f}')

# total wall-clock elapsed and average training steps/sec (from the STEP wall timestamps)
title = None
walls = d['wall']
if walls.size >= 2 and walls[0] and walls[-1]:
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    try:
        t0 = datetime.datetime.strptime(str(walls[0]),  fmt)
        t1 = datetime.datetime.strptime(str(walls[-1]), fmt)
        elapsed = (t1 - t0).total_seconds()
        nsteps  = float(step[-1] - step[0])
        sps     = nsteps / elapsed if elapsed > 0 else 0.0
        title   = f'elapsed {datetime.timedelta(seconds=int(elapsed))}   {sps:.2f} steps/s'
    except ValueError:
        title = None
print('title:', title)

#grad = np.clip(grad, 0, 10)

TAIL   = 1000   # trailing samples --sigma scales to
HALF   = 0.5    # share of the y range the body of the run has to reach
MAXCUT = 0.5    # never drop more than this share of the samples to get there
CAP    = 0.125  # where the body lands on a panel that has to be capped instead (see ylim_top)

def _fills(a):
    """How far the body of `a` reaches up a 0..max(a) axis, as a fraction of HALF: >= 1
    means the median sits at or above the half-height line."""
    top = float(a.max()) * 1.05
    return 0.0 if top <= 0 else float(np.median(a)) / (HALF * top)


def trim_start(series):
    """First sample index to plot. A run's startup transient sets the axis for the whole
    chart — loss opens at 5.5 and settles at 1.5, so 0..5.5 draws the part anyone is
    actually reading in the bottom quarter. Rather than clip the y axis to the live region
    (which hides the history and leaves the trace pinned under the axis top), drop leading
    samples until the body of what remains — its median — reaches at least half the axis
    height. The transient scrolls off the left, the top stays a real data value, and
    nothing is clipped.

    Each series asks for the smallest cut that works for it and the largest wins, so the
    x axis stays aligned across panels and no series is trimmed further than it needs. A
    series whose outliers are spread through the run (grad spikes) can never satisfy the
    test by trimming its front, so it asks for nothing rather than dragging the cut to the
    MAXCUT ceiling for no gain — ylim_top caps that panel instead."""
    n = min(s.size for s in series)
    if n < 10:
        return 0
    stride = max(1, n // 200)                  # 0.5% granularity is enough
    limit  = int(n * MAXCUT)

    def _first_k(a):
        for k in range(0, limit + 1, stride):
            if _fills(a[k:]) >= 1.0:
                return k
        return 0                               # unreachable: leave it to ylim_top
    return max(_first_k(s) for s in series)


def ylim_top(a, name=''):
    """Top y-limit: the largest sample drawn, +5% headroom, so the top is a real value and
    nothing goes off-panel. trim_start() has already dropped the startup transient, which
    is what made scaling to the max unreadable.

    Trimming only reaches outliers at the *start* of a run, and grad spikes recur all the
    way through one: after the cut its body can still sit at a tenth of panel height. When
    that happens the top is capped at the height that puts the median a CAP fraction up,
    and the spikes above it clip — the same trade the trim avoids, taken only on a panel
    that is unreadable without it. CAP sits well below the half the trim aims for: grad's
    scatter runs several times its own median, so a half-height body clips the excursions
    that are the reason to look at the panel at all.
    --sigma overrides both with a fixed zoom on the last TAIL samples."""
    if a.size == 0:
        return None
    if args.outliers:
        return float(a.max()) * 1.05 or 1.0
    if args.sigma:
        w   = a[-TAIL:]
        top = float(np.median(w)) + args.sigma * float(w.std())
    else:
        top  = float(a.max()) * 1.05
        body = float(np.median(a))
        if top > 0 and body < CAP * top:       # spikes the cut could not remove
            top = body / CAP
    if not np.isfinite(top) or top <= 0:
        return float(a.max()) * 1.05 or 1.0
    hidden = int((a > top).sum())
    if hidden:
        print(f'{name}: {hidden}/{a.size} samples above the axis top {top:.4g} '
              f'(max {a.max():.4g}), use --outliers to show them')
    return top

# Drop the startup transient (see trim_start) before anything is scaled or plotted. One cut
# for every series, so the shared x axis and the --verbose panels stay aligned with it.
cut = 0 if args.outliers else trim_start([loss, grad])
if cut:
    print(f'trimmed first {cut}/{step.size} samples (through step {step[cut - 1]:.0f}) so the '
          f'body of the run fills the upper half of the loss/grad panels; --outliers keeps them')
    step, loss, grad, lr = step[cut:], loss[cut:], grad[cut:], lr[cut:]
    mean, std, dmax, zero, bs = mean[cut:], std[cut:], dmax[cut:], zero[cut:], bs[cut:]

window_size = 10
weights = np.ones(window_size) / window_size
loss_mean = np.convolve(loss, weights, mode='same')

#fig = plt.figure(figsize=(10,40))
plt.style.use('dark_background')
# --verbose shows all six panels; otherwise loss, grad and the DFF state (std + mean).
# The DFF panel is third in BOTH layouts, so --verbose is unchanged by its promotion: it
# is the one panel that says whether the recurrent state is healthy, and a run that is
# quietly drifting toward a blow-up shows it here long before the loss moves.
nplots = 6 if args.verbose else 3
fig = plt.figure(figsize=(12, 14 if args.verbose else 9))
if title:
    fig.suptitle(title)
ax1 = fig.add_subplot(nplots,1,1)
ax2 = fig.add_subplot(nplots,1,2, sharex=ax1)
# --batch overlays batch size on grad: the two move together when the run's --batch
# changes. Off by default -- the twin's own gridless scale reads as clutter otherwise.
ax2b = ax2.twinx() if args.batch else None
#ax1.set_ylim(bottom=0, top=np.log(50257))
ax1.set_ylim(bottom=0, top=ylim_top(loss, 'loss'))
ax1.plot(step, loss, '.w', linewidth=0.1,alpha=1.0, markersize=1)
#ax1.plot(step, loss_mean, '-w', linewidth=1,alpha=0.8)
ax1.axhline(y=np.min(loss), color='g', linestyle='-',linewidth=1,label='min')
#ax2.plot(step, grad, '-y', linewidth=2.0,alpha=0.5)
ax2.plot(step, grad, '.y', linewidth=0.1,alpha=1.0, markersize=1)
ax2.set_ylim(bottom=0, top=ylim_top(grad, 'grad'))
if ax2b is not None:
    # piecewise constant (it only changes when a run is resumed at a different --batch)
    ax2b.plot(step, bs, '-', color='orange', linewidth=2.0, alpha=0.5, drawstyle='steps-post')
    ax2b.set_ylim(bottom=0, top=float(bs.max()) * 1.2 or 1)
    ax2b.set_ylabel('batch size', color='orange')

# DFF state: std on the host axis, mean on a twin. Same colours and styling the --verbose
# layout has always used for them, so charts from either mode read the same.
ax3  = fig.add_subplot(nplots, 1, 3, sharex=ax1)
ax3b = ax3.twinx()
ax3.plot(step, std, '-r', linewidth=1.0, alpha=0.5)
ax3b.plot(step, mean, '-b', linewidth=1.0, alpha=0.5)
# std is non-negative and spikes at init like grad does, so it gets the same capped top.
# mean is SIGNED under --linout (a dense signed register straddles zero), so its twin is
# left to autoscale rather than pinned at zero.
ax3.set_ylim(bottom=0, top=ylim_top(std, 'dff_std'))

ax1.set_ylabel('loss', color='w')
ax2.set_ylabel('grad', color='y')
ax3.set_ylabel('dff_std', color='r')
ax3b.set_ylabel('dff_mean', color='b')

# y axis: minor ticks between the majors, and a hairline major gridline in the trace's own
# colour, so the grid reads as part of its plot instead of competing with the samples
for ax, color in ((ax1, 'w'), (ax2, 'y'), (ax3, 'r')):
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis='y', which='major', color=color, linewidth=1, alpha=0.2)

# twins are tracked separately: twinx hides their x axis, so the shared x-axis label has to
# land on a host subplot, never on a twin
axes = [ax1, ax2, ax3]
twins = ([ax2b] if ax2b is not None else []) + [ax3b]
if args.verbose:
    ax4 = fig.add_subplot(nplots,1,4, sharex=ax1)
    ax5 = fig.add_subplot(nplots,1,5, sharex=ax1)
    ax6 = fig.add_subplot(nplots,1,6, sharex=ax1)
    ax4.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.7f'))
    ax4.plot(step, lr, '-c', linewidth=2.0,alpha=0.5)
    ax5.plot(step, dmax, '-m', linewidth=2.0,alpha=0.5)
    ax6.set_ylim(bottom=0, top=1)
    ax6.plot(step, zero, '-g', linewidth=2.0,alpha=0.5)

    ax4.set_ylabel('lr', color='c')
    ax5.set_ylabel('dff_max', color='m')
    ax6.set_ylabel('sparsity', color='g')
    axes += [ax4, ax5, ax6]

# only the bottom subplot carries the shared x-axis label and tick labels
for ax in axes[:-1] + twins:
    ax.tick_params(labelbottom=False)
axes[-1].set_xlabel('step')

fig.tight_layout()
plt.show()
