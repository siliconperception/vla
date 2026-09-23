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
           'a_std', 'i_std', 'epoch']
_NUM    = r'(-?[\d.]+(?:[eE][-+]?\d+)?)'

# GENSCORE lines carry the fluency of the periodic generation samples, scored by the frozen
# reference LM (--gen_score):
#   GENSCORE step        500 [<STX>]: nats 7.865 fluency -23% rep1 0.09
# Same units as the loss column -- nats per token -- so they belong on the loss panel, but
# they are a different quantity: the loss is our model's fit to REAL text, this is a
# reference model's opinion of the text OUR model wrote free-running. There is one line per
# --gen_prompts prompt per report, so several can share a step.
gs_pat = re.compile(r'^GENSCORE\s+step\s+(\d+).*?\bnats\s+' + r'(-?[\d.]+(?:[eE][-+]?\d+)?)')

# TRIGGER lines carry the --refresh stall detector (vla.py, arXiv:2403.02473). Two shapes:
#   TRIGGER step   128000 mean_std 2.2778 ... last_sum_delta +1.20 (abs 1.20) rel best 1.20 still 0/3
#   TRIGGER smolfwedu STALLED at epoch 20 -- retired 25 oldest, drew 25 fresh ...
# The periodic one is the series (it is the only shape carrying a step number); the STALLED
# one is an event, and its step is the last STEP line seen before it, which is exact to
# within --monitor. The per-epoch verdict lines are not parsed: the periodic line already
# reports the same numbers as last_sum_delta/best.
tg_pat = re.compile(r'^TRIGGER\s+step\s+(\d+).*?\(abs\s+' + _NUM + r'\).*?'
                    r'best\s+(?:none|' + _NUM + r').*?still\s+(\d+)/(\d+)')
st_pat = re.compile(r'^TRIGGER\s+\S+\s+STALLED')


def parselog(fn):
    global batch_size
    step_pat = re.compile(r'^STEP\s+(\d+)')
    wall_pat = re.compile(r'wall\s+(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+)')
    pats     = {k: re.compile(r'\b' + k + r'\s+' + _NUM) for k in _FIELDS}
    data     = {k: [] for k in ['step'] + _FIELDS}
    data['wall'] = []
    gs_step, gs_nats = [], []
    tg_step, tg_dabs, tg_best, tg_hold, tg_need = [], [], [], [], [0]
    rf_step = []
    last_step = [0.0]
    with open(fn, 'r') as f:
        for l in f:
            if l.startswith('TRIGGER'):
                mt = tg_pat.match(l)
                if mt:
                    tg_step.append(float(mt.group(1)))
                    tg_dabs.append(float(mt.group(2)))
                    tg_best.append(float(mt.group(3)) if mt.group(3) else np.nan)
                    tg_hold.append(float(mt.group(4)))
                    tg_need[0] = float(mt.group(5))
                elif st_pat.match(l):
                    rf_step.append(last_step[0])
                continue
            mg = gs_pat.match(l)
            if mg:
                gs_step.append(float(mg.group(1)))
                gs_nats.append(float(mg.group(2)))
                continue
            ms = step_pat.match(l)
            if ms:
                data['step'].append(float(ms.group(1)))
                last_step[0] = float(ms.group(1))
                mw = wall_pat.search(l)
                data['wall'].append(mw.group(1) if mw else '')
                for k in _FIELDS:
                    m = pats[k].search(l)
                    data[k].append(float(m.group(1)) if m else 0.0)
            elif l[0:4] == 'ARGS':
                match = re.search(r"batch=(\d+)", l)
                if match:
                    batch_size = int(match.group(1))
    out = {k: np.array(v)[args.head:] for k, v in data.items()}
    # NOT sliced by --head: that is a count of STEP samples, and these are keyed by step
    # number instead. They are filtered by step below, once the trim is known.
    out['gs_step'] = np.array(gs_step)
    out['gs_nats'] = np.array(gs_nats)
    out['tg_step'] = np.array(tg_step)
    out['tg_dabs'] = np.array(tg_dabs)
    out['tg_best'] = np.array(tg_best)
    out['tg_hold'] = np.array(tg_hold)
    out['tg_need'] = tg_need[0]
    out['rf_step'] = np.array(rf_step)
    return out

print('loading log file')
d = parselog(args.log)
print('steps', d['step'].shape[0])
print('batch_size', batch_size)

step = d['step']
loss = d['loss']
grad = d['grad']
lr   = d['lr']
epoch = d['epoch']
gs_step, gs_nats = d['gs_step'], d['gs_nats']
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
    epoch = epoch[cut:]
    if gs_step.size:                       # by STEP NUMBER: these are not per-sample rows
        _keep   = gs_step >= step[0]
        gs_step, gs_nats = gs_step[_keep], gs_nats[_keep]
    for _k in ('tg_step', 'rf_step'):      # likewise, and the TRIGGER series travel together
        if d[_k].size:
            _keep = d[_k] >= step[0]
            if _k == 'tg_step':
                d['tg_dabs'], d['tg_best'] = d['tg_dabs'][_keep], d['tg_best'][_keep]
                d['tg_hold'] = d['tg_hold'][_keep]
            d[_k] = d[_k][_keep]

window_size = 10
weights = np.ones(window_size) / window_size
loss_mean = np.convolve(loss, weights, mode='same')

#fig = plt.figure(figsize=(10,40))
plt.style.use('dark_background')
# --verbose shows all six panels; otherwise loss, grad, the DFF state (std + mean) and lr.
# The DFF panel is third in BOTH layouts, so --verbose is unchanged by its promotion: it
# is the one panel that says whether the recurrent state is healthy, and a run that is
# quietly drifting toward a blow-up shows it here long before the loss moves. The lr is
# fourth in both for the same reason: with cyclic and ramped schedules (v117-v119) the
# loss and the state cannot be read without knowing where the schedule was at that step.
nplots = 7 if args.verbose else 4
fig = plt.figure(figsize=(12, 16 if args.verbose else 11))
if title:
    fig.suptitle(title)
ax1 = fig.add_subplot(nplots,1,1)
ax2 = fig.add_subplot(nplots,1,2, sharex=ax1)
# --batch overlays batch size on grad: the two move together when the run's --batch
# changes. Off by default -- the twin's own gridless scale reads as clutter otherwise.
ax2b = ax2.twinx() if args.batch else None
#ax1.set_ylim(bottom=0, top=np.log(50257))
# The panel scales to BOTH series: the generation score opens far above the loss (13 nats
# of word salad against a loss of 8) and settles toward it, so scaling to the loss alone
# would put every early point off-panel. ylim_top's cap still applies, so a run whose
# samples stay bad does not flatten the loss trace to read them.
_l_top = ylim_top(np.concatenate([loss, gs_nats]) if gs_nats.size else loss, 'loss')
ax1.set_ylim(bottom=0, top=_l_top)
ax1.plot(step, loss, '.w', linewidth=0.1,alpha=1.0, markersize=1)
if gs_nats.size:
    # scatter, not a line: several prompts are scored at the same step, and the spread
    # between them at one step is itself the reading -- a line would average it away.
    ax1.plot(gs_step, gs_nats, 'o', color='orange', markersize=1.5, alpha=0.7,
             linestyle='none', label='GENSCORE nats')
    # Rolling mean over the scatter. The per-sample spread is wide -- free-running
    # generation is stochastic and each point is one sample of ~200 tokens -- so the
    # question the scatter alone cannot answer is whether the CENTRE is moving. Centred and
    # 'valid', so the line spans only the steps that have a full window behind and ahead of
    # them: no half-window ramp at either end pretending to be a trend.
    _w = int(max(3, min(15, gs_nats.size // 10)))
    if gs_nats.size >= _w:
        _roll = np.convolve(gs_nats, np.ones(_w) / _w, mode='valid')
        _half = (_w - 1) // 2
        ax1.plot(gs_step[_half:_half + _roll.size], _roll, '-', color='#ffd699',
                 linewidth=1.5, alpha=0.9, label=f'GENSCORE mean ({_w})')
    ax1.legend(loc='upper right', fontsize=8, framealpha=0.3)
    _off = int((gs_nats > _l_top).sum()) if _l_top else 0
    if _off:
        print(f'GENSCORE: {_off}/{gs_nats.size} points above the loss axis top {_l_top:.4g}')
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

# DFF state: std and mean on ONE shared y axis, not a twin. They are the same quantity in
# the same units -- the spread of the register and where it sits -- so a shared scale is
# what makes them comparable: it shows at a glance whether the mean is small against the
# spread (a centred register) or riding out with it (a register drifting off zero), which
# two independently autoscaled axes actively hide.
ax3 = fig.add_subplot(nplots, 1, 3, sharex=ax1)
ax3.plot(step, std,  '-r', linewidth=1.0, alpha=0.5, label='std')
ax3.plot(step, mean, '-b', linewidth=1.0, alpha=0.5, label='mean')
# Top from std, which is non-negative and spikes at init the way grad does, so it gets the
# same capped top -- then raised if the mean runs above it. Bottom follows the mean below
# zero: under --linout the register is dense and SIGNED, and a bottom=0 axis would draw it
# off-panel.
_top = ylim_top(std, 'dff_std') or 1.0
_top = max(_top, float(mean.max()) * 1.05) if mean.size else _top
_bot = min(0.0, float(mean.min()) * 1.05) if mean.size else 0.0
# A negative mean has to be VISIBLY negative. Scaling the bottom to the mean alone is not
# enough when the two series differ in magnitude: v49 runs mean -0.005 against std 0.31, so
# a bottom of -0.005 is 1.6% of the panel, the tick reads 0.00 and the trace lies on the
# axis floor -- indistinguishable from a mean pinned at zero, which is the opposite reading.
# So whenever any sample is negative, at least NEG_SHARE of the panel goes below zero.
NEG_SHARE = 0.15
if _bot < 0:
    _bot = min(_bot, -NEG_SHARE * _top)
ax3.set_ylim(bottom=_bot, top=_top)
if _bot < 0:
    ax3.axhline(y=0, color='w', linewidth=0.5, alpha=0.3)   # sign reference for the mean
ax3.legend(loc='upper right', fontsize=8, framealpha=0.3)

ax1.set_ylabel('loss', color='w')
ax2.set_ylabel('grad', color='y')
ax3.set_ylabel('dff std / mean', color='w')

# twins are tracked separately: twinx hides their x axis, so the shared x-axis label has to
# land on a host subplot, never on a twin
ax4 = fig.add_subplot(nplots,1,4, sharex=ax1)
# %g, not a fixed decimal count: the schedules span 1e-6 floors to lr 2.0 peaks, and seven
# decimals reads as 2.0000000 at one end and 0.0000010 at the other.
ax4.yaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))

# PANEL 4 IS THE DATA CLOCK when the log has one: passes over the --subsample pool on the
# left axis, the --refresh stall detector on the right, and a vertical line wherever the
# pool actually turned over. Read together they answer the question --refresh exists to
# ask -- did the drift flatten, did that fire a refresh, and did the refresh restart it --
# which no other panel shows: loss and dff_std move so slowly at this scale that a refresh
# is invisible in them. A log with no epoch column and no TRIGGER lines (every run before
# --subsample) falls back to the lr trace this panel used to carry.
ax4b = None
# VARIES, not merely present: a streaming run logs epoch 1.000 for its whole life (the
# corpus never wraps), and a flat line at 1 is worth less than the lr trace it replaced.
# The panel takes over only for a run whose data actually cycles -- --subsample, --datarep,
# or a corpus small enough to wrap -- or one carrying detector lines.
_have_epoch = bool(epoch.size) and float(np.nanmax(epoch)) > float(np.nanmin(epoch))
if _have_epoch or d['tg_step'].size:
    if _have_epoch:
        ax4.plot(step, epoch, '-c', linewidth=2.0, alpha=0.6, label='epoch')
        ax4.set_ylim(bottom=0, top=float(np.nanmax(epoch)) * 1.05 + 1e-9)
    ax4.set_ylabel('epoch' + ('' if _have_epoch else ' (none)'), color='c')
    for _x in d['rf_step']:                # pool turnover: the event the detector caused
        ax4.axvline(_x, color='r', linewidth=1.0, alpha=0.55, linestyle='--')
    if d['tg_step'].size:
        # LOG scale: the drift decays by more than a decade over a run (measured 6.3 -> 0.3
        # at --subsample 100), so a linear twin pins the interesting flat tail to the axis.
        ax4b = ax4.twinx()
        ax4b.set_yscale('log')
        ax4b.plot(d['tg_step'], d['tg_dabs'], '-', color='orange', linewidth=1.5, alpha=0.8,
                  label='|sum delta|')
        if np.isfinite(d['tg_best']).any():
            # the running minimum IS the criterion under --refresh_mode rel: the detector
            # fires after --refresh_hold epochs in which this line did not step down.
            # DASHED, because while the run is still improving every epoch the running
            # minimum IS the current value and a solid line would hide underneath it --
            # the dashes are what say "no stall yet" at a glance.
            ax4b.plot(d['tg_step'], d['tg_best'], '--', color='w', linewidth=1.2, alpha=0.7,
                      label='best (running min)')
        ax4b.set_ylabel('|sum delta| / best', color='orange')
        ax4b.tick_params(axis='y', colors='orange')
        _nr = len(d['rf_step'])
        ax4b.legend(loc='upper right', fontsize=7, framealpha=0.2,
                    title=(f'{_nr} refresh' + ('es' if _nr != 1 else '')
                           + (f', hold {d["tg_need"]:.0f}' if d['tg_need'] else '')),
                    title_fontsize=7)
else:
    ax4.plot(step, lr, '-c', linewidth=2.0,alpha=0.5)
    ax4.set_ylim(bottom=0, top=(float(lr.max()) * 1.05 if lr.size and lr.max() > 0 else 1.0))
    ax4.set_ylabel('lr', color='c')

# y axis: minor ticks between the majors, and a hairline major gridline in the trace's own
# colour, so the grid reads as part of its plot instead of competing with the samples
for ax, color in ((ax1, 'w'), (ax2, 'y'), (ax3, 'r'), (ax4, 'c')):
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis='y', which='major', color=color, linewidth=1, alpha=0.2)

axes = [ax1, ax2, ax3, ax4]
twins = ([ax2b] if ax2b is not None else []) + ([ax4b] if ax4b is not None else [])
if args.verbose:
    ax5 = fig.add_subplot(nplots,1,5, sharex=ax1)
    ax6 = fig.add_subplot(nplots,1,6, sharex=ax1)
    ax7 = fig.add_subplot(nplots,1,7, sharex=ax1)
    ax5.plot(step, dmax, '-m', linewidth=2.0,alpha=0.5)
    ax6.set_ylim(bottom=0, top=1)
    ax6.plot(step, zero, '-g', linewidth=2.0,alpha=0.5)
    # lr kept here now that panel 4 is the data clock: with ramped and cyclic schedules the
    # loss and the state still cannot be read without knowing where the schedule was.
    ax7.yaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax7.plot(step, lr, '-c', linewidth=2.0, alpha=0.5)
    ax7.set_ylim(bottom=0, top=(float(lr.max()) * 1.05 if lr.size and lr.max() > 0 else 1.0))

    ax5.set_ylabel('dff_max', color='m')
    ax6.set_ylabel('sparsity', color='g')
    ax7.set_ylabel('lr', color='c')
    axes += [ax5, ax6, ax7]

# only the bottom subplot carries the shared x-axis label and tick labels
for ax in axes[:-1] + twins:
    ax.tick_params(labelbottom=False)
axes[-1].set_xlabel('step')

fig.tight_layout()
plt.show()
