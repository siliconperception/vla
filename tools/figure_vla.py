"""Draw docs/figures/vla_<model>.svg: one clock tick of a VLA model, 16:9 (1920 x 1080).

usage: python tools/figure_vla.py [--model v498|v499|v502|v505|v511|v531|v533|v536|v538|v540|v541|v552|v564|v569] [--out OUT]

v498: recurrent CNN + two order-2 Legendre memories (4096, 64 ticks) + copy + recall attention, never
reset. v499: no registers, the recall attention's ring is the whole state, reset at each example.
v502: the residual cascade of an EMA (512 ticks) and the residual copy, read through per-sample RMSnorm,
+ recall attention, reset at each example. v505: two recurrent layers in series, each with that cascade, no
recall attention; 1920 x 2160, two 16:9 panes: the whole tick on top, one layer zoomed in below. v511: v505
with the layers' EMA windows 16 (layer 1) and 64 (layer 2) ticks. v531: one layer, its EMA (16 ticks to start)
written at a learned rate per channel and position (--write_gate), plus the residual copy. v533: v531's
architecture, trained on with SGD lr 0.001 and Nesterov momentum 0.95. v536: --convdelta 6 --lm, a
text-only model of 6 residual blocks of per-tick convs, each carrying a gated delta-rule matrix memory per grid
position, trained a window at a time; 1920 x 2160, the whole model above and one block below. v538: v536
with --grid_hist 8 (the input grid a learned map of the last 8 tokens, starting as concentric rings) and
--reset_prob 0.5 (half the training documents start unreset: a stress test for perception discontinuities).
v540: v538 with a third conv 3x3 + BN + ReLU in every block (--cd_convs 3).
v541: v540's model, trained at a 10x lower learning rate (--lr_final 0.0001); drawn as v540.
v552: v540 without the time conv's FIFO (--cd_taps 1: a per-channel scale of RMS(x)), write strength
beta in (0, 2) (--cd_neg), decay windows within x2 of fixed bases (--cd_band 2, --cd_windows), every
document reset in training.
v564: 3 ConvDelta blocks of 7 conv 3x3 + BN + ReLU layers each (--convdelta 3 --cd_convs 7), no time conv
(--cd_taps 0), the token replicated to every grid position (no --grid_hist), every document reset.
v569: 7 blocks of 7 convs at 256 channels (--c_context 256 --convdelta 7 --cd_convs 7), each block's
memory first, then its convs (--cd_delta_first); otherwise as v564."""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--model', default='v498', choices=('v498', 'v499', 'v502', 'v505', 'v511', 'v531', 'v533', 'v536', 'v538', 'v540', 'v541', 'v552', 'v564', 'v569'))
ap.add_argument('--out', default=None)
a = ap.parse_args()
NAME = a.model                            # the title and file name
if a.model == 'v541':
    a.model = 'v540'                      # same model as v540
LMU = a.model == 'v498'                   # Legendre memories + copy
CASC = a.model == 'v502'                  # EMA + residual copy, RMSnorm reads
REGS = LMU or CASC                        # (v499: the ring alone)
CAT = {'v498': ('3×256 + 2048 + 256 + 256 + 5×512', 5888), 'v499': ('3×256 + 2048 + 256 + 256', 3328),
       'v502': ('3×256 + 2048 + 256 + 256 + 2×512', 4352), 'v505': ('', 0), 'v511': ('', 0),
       'v531': ('', 0), 'v533': ('', 0), 'v536': ('', 0), 'v538': ('', 0), 'v540': ('', 0), 'v552': ('', 0), 'v564': ('', 0), 'v569': ('', 0)}[a.model]
EMA1, EMA2 = (16, 64) if a.model == 'v511' else (512, 512)    # two-layer models: each layer's EMA window

W, H = 1920, 1080
out = []
COL = dict(frozen='#e0e0e0', rep='#ce93d8', cat='#90a4ae', lin='#64b5f6', cnn='#81c784', dec='#4dd0e1',
           media='#ffffff', smp='#f48fb1', lmu='#fff176', norm='#bcaaa4', attn='#ffb74d', mel='#fff9c4',
           ink='#212121', soft='#616161', gate='#ff8a65', tconv='#b39ddb')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=12, anchor='middle', weight='normal', fill=COL['ink'], rotate=None):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate else ''
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
               f'fill="{fill}"{tr}>{esc(s)}</text>')


def box(x, y, w, h, fill, lines=(), size=11, hatch=False, rx=3, vertical=False, dash=False):
    st = ' stroke-dasharray="5,3"' if dash else ''
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{COL["ink"]}" '
               f'stroke-width="1.2"{st}/>')
    if hatch:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#hatch)" opacity="0.5"/>')
    if vertical:
        cx, cy = x + w / 2, y + h / 2
        for i, s in enumerate(lines):
            text(cx + 4 + (i - (len(lines) - 1) / 2) * (size + 2), cy, s, size, rotate=-90,
                 weight='bold' if i == 0 else 'normal')
    else:
        n = len(lines)
        for i, s in enumerate(lines):
            text(x + w / 2, y + h / 2 + 4 + (i - (n - 1) / 2) * (size + 3), s, size if i == 0 else size - 1.5,
                 weight='bold' if i == 0 else 'normal', fill=COL['ink'] if i == 0 else '#424242')


def line(pts, color=COL['ink'], arrow=True, width=1.4, dash=False):
    d = ' '.join(f'{"M" if i == 0 else "L"} {x},{y}' for i, (x, y) in enumerate(pts))
    st = ' stroke-dasharray="5,3"' if dash else ''
    mk = ' marker-end="url(#arr)"' if arrow else ''
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{st}{mk}/>')


def dot(x, y):
    out.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{COL["ink"]}"/>')


def mux(x, y):
    out.append(f'<path d="M {x},{y - 15} L {x + 34},{y - 9} L {x + 34},{y + 9} L {x},{y + 15} z" fill="#e0e0e0" '
               f'stroke="{COL["ink"]}" stroke-width="1.2"/>')


def flop(x, y, name, size='512×7×7'):
    """A D flip-flop register symbol at (x, y), 64 x 46."""
    out.append(f'<rect x="{x}" y="{y}" width="64" height="46" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
    out.append(f'<path d="M {x + 26},{y + 46} L {x + 32},{y + 39} L {x + 38},{y + 46}" fill="none" '
               f'stroke="{COL["ink"]}" stroke-width="1.1"/>')
    text(x + 9, y + 13, 'Q', 10, anchor='start')
    text(x + 55, y + 13, 'D', 10, anchor='end')
    text(x + 32, y + 30, name, 12, weight='bold')
    text(x + 32, y - 5, size, 9.5, fill=COL['soft'])


DEFS = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M 0,0 L 10,5 L 0,10 z" fill="#212121"/></marker>'
        '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#757575" stroke-width="1.2"/></pattern></defs>')


def legend(x, y, items, flop_note, w=460):
    """Legend box at (x, y): items [(fill, hatch, label)], then the register symbol and the line styles."""
    h = 48 + 28 * len(items) + 64 + 24
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
    text(x + 18, y + 26, 'Legend', 14, anchor='start', weight='bold')
    for i, (c, hch, s) in enumerate(items):
        yy = y + 48 + 28 * i
        box(x + 18, yy, 26, 18, c, hatch=hch, rx=2)
        text(x + 56, yy + 13, s, 12, anchor='start')
    yy = y + 48 + 28 * len(items)
    flop(x + 18, yy + 2, '', size='')
    text(x + 94, yy + 22, 'D flip-flop register, clocked every tick', 12, anchor='start')
    text(x + 94, yy + 38, flop_note, 11, anchor='start', fill=COL['soft'])
    yy += 70
    line([(x + 18, yy), (x + 50, yy)])
    text(x + 56, yy + 4, 'data / state path', 12, anchor='start')
    line([(x + 220, yy), (x + 252, yy)], dash=True, color='#757575')
    text(x + 258, yy + 4, 'old state into the update', 12, anchor='start')


def layer_block(x0, y0, name, cat, ins, cy, ema):
    """Pane A: one recurrent layer as a 360 x 390 block at (x0, y0): concat, ctx_cat, 8 convs, linout and
    its two registers fed back (the cascade itself is drawn in pane B). ins: the y of each input entering
    the concat; cy: the main path. -> the output point."""
    out.append(f'<rect x="{x0}" y="{y0}" width="360" height="390" rx="10" fill="#f5f9ff" stroke="{COL["ink"]}" '
               f'stroke-width="1.6"/>')
    text(x0 + 180, y0 - 12, name, 15, weight='bold')
    cx = x0 + 22                                          # concat
    box(cx, y0 + 24, 30, 250, COL['cat'], [f'concat {cat}'], size=10, vertical=True)
    for y in ins:
        line([(x0, y), (cx, y)])
    line([(cx + 30, cy), (x0 + 72, cy)])
    box(x0 + 72, cy - 70, 24, 140, COL['lin'], ['ctx_cat 1×1'], size=10, vertical=True)
    xx = x0 + 112
    line([(x0 + 96, cy), (xx, cy)])
    for k in range(8):
        box(xx, cy - 55, 13, 110, COL['cnn'], rx=2)
        if k < 7:
            line([(xx + 13, cy), (xx + 19, cy)], arrow=False)
        xx += 19
    text(x0 + 187, cy - 64, '8 × conv 3×3+BN+ReLU', 10.5)
    line([(xx - 6, cy), (x0 + 276, cy)])
    box(x0 + 276, cy - 70, 24, 140, COL['lin'], ['linout 3×3'], size=10, vertical=True)
    bx = x0 + 326                                         # output tap
    line([(x0 + 300, cy), (x0 + 360, cy)], arrow=False)
    dot(bx, cy)
    ry = y0 + 300                                         # the two registers
    f1, f2 = x0 + 110, x0 + 210
    dot(bx, ry - 10)
    line([(bx, cy), (bx, ry + 23), (f2 + 66, ry + 23)])
    line([(bx, ry - 10), (f1 + 82, ry - 10), (f1 + 82, ry + 23), (f1 + 66, ry + 23)])
    flop(f1, ry, 'DFF_1', size='')
    flop(f2, ry, 'DFF_2', size='')
    text(f1 + 32, ry + 62, f'EMA {ema}', 10, fill=COL['soft'])
    text(f2 + 32, ry + 62, 'copy', 10, fill=COL['soft'])
    line([(f1, ry + 16), (cx + 10, ry + 16), (cx + 10, y0 + 276)], dash=True, color='#757575')
    line([(f2, ry + 16), (f2 - 14, ry + 16), (f2 - 14, ry + 72), (cx + 20, ry + 72), (cx + 20, y0 + 276)],
         dash=True, color='#757575')
    return x0 + 360, cy


def draw_v505():
    """1920 x 2160: pane A (top, 16:9) the whole tick; pane B (bottom, 16:9) one recurrent layer."""
    W5, H5 = 1920, 2160
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W5}" height="{H5}" viewBox="0 0 {W5} {H5}" '
               f'font-family="Helvetica, Arial, sans-serif">')
    out.append(DEFS)
    out.append(f'<rect width="{W5}" height="{H5}" fill="#ffffff"/>')

    # ── pane A: the whole tick ──────────────────────────────────────────────
    text(30, 38, f'VLA {a.model} — one clock tick (40 ms): two recurrent CNN layers in series', 22, anchor='start',
         weight='bold')
    text(30, 62, 'A · the whole tick.  n_hidden 512 · c_context 384 · 7×7 grid · depth 8 per layer · 3 token '
         'streams · 25 Hz · each layer: EMA + copy (' + (f'EMA {EMA1}' if EMA1 == EMA2 else
         f'EMA {EMA1} in layer 1, {EMA2} in layer 2') + '), RMSnorm reads · reset at each example · 33.2M trainable · '
         'state 4 × 512×7×7 = 100,352 values', 13, anchor='start', fill='#424242')
    ys = (300, 350, 400)
    for y, nm in zip(ys, ('text', 'voice', 'image')):
        mux(40, y)
        line([(74, y), (128, y)])
        text(100, y - 6, nm, 10, fill=COL['soft'])
    box(130, 275, 150, 150, COL['frozen'], ['tok_embed (frozen)', 'pythia-31m 50304×256', 'shared by 3 streams'],
        hatch=True)
    for y in ys:
        line([(280, y), (318, y)])
    box(320, 275, 40, 150, COL['rep'], ['RMS · replicate 1×1→7×7'], size=11, vertical=True)
    text(440, ys[0] - 8, 'token grids 3 × 256×7×7', 10, fill=COL['soft'])
    box(40, 478, 90, 44, COL['media'], ['audio', '16 kHz'])
    line([(130, 500), (158, 500)])
    box(160, 478, 150, 44, COL['mel'], ['log-mel (fixed)', '64 mels · 10 ms hop'])
    line([(310, 500), (328, 500)])
    box(330, 483, 36, 34, COL['norm'], ['RMS'], size=10)
    text(440, 492, 'audio grid 256×7×7', 10, fill=COL['soft'])
    box(40, 560, 90, 44, COL['media'], ['frame', '2 fps'], dash=True)
    line([(130, 582), (158, 582)], dash=True, color='#9e9e9e')
    box(160, 560, 150, 44, COL['frozen'], ['image encoder', '(future)'], hatch=True, dash=True)
    for y in ys:
        line([(360, y), (520, y)], arrow=False)
    line([(366, 500), (520, 500)], arrow=False)

    CY = 430
    o1 = layer_block(520, 250, 'LAYER 1', '3×256 + 256 + 2×512 = 2048', list(ys) + [500], CY, EMA1)
    BX = o1[0] + 40                                       # the o_1 tap
    line([o1, (BX, CY)], arrow=False)
    dot(BX, CY)
    text(BX - 4, CY - 10, 'o₁', 13, anchor='end', weight='bold')
    L2 = 1000
    line([(BX, CY), (L2, CY)], arrow=False)
    o2 = layer_block(L2, 250, 'LAYER 2', '512 + 2×512 = 1536', [CY], CY, EMA2)
    AX = o2[0] + 56                                       # the adder
    line([o2, (AX - 18, CY)])
    text(o2[0] + 22, CY - 10, 'd₂', 13, anchor='start', weight='bold')
    out.append(f'<circle cx="{AX}" cy="{CY}" r="17" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
    text(AX, CY + 7, '+', 22, weight='bold')
    line([(BX, CY), (BX, 710), (AX, 710), (AX, CY + 19)])       # o_1 around layer 2
    text((BX + AX) / 2, 728, 'o₁: residual path around layer 2', 11, fill=COL['soft'])
    zx0, zy0, zx1, zy1 = L2 - 16, 222, L2 + 376, 668     # zoom marker
    out.append(f'<rect x="{zx0}" y="{zy0}" width="{zx1 - zx0}" height="{zy1 - zy0}" rx="14" fill="none" '
               f'stroke="#e65100" stroke-width="2" stroke-dasharray="8,5"/>')
    text(zx0 + 8, zy1 + 20, 'one layer, zoomed in: pane B ▼', 12, anchor='start', fill='#e65100', weight='bold')

    OX = AX + 17                                          # decoders, lmhead, sampling
    TX = OX + 40
    text(OX + 6, CY - 10, 'o', 13, anchor='start', weight='bold')
    rows = ((300, 'text_dec', 'THINK'), (CY, 'voc_dec', 'HEAR'), (560, 'img_dec', 'SEE'))
    line([(OX, CY), (TX, CY)], arrow=False)
    dot(TX, CY)
    line([(TX, rows[0][0]), (TX, rows[2][0])], arrow=False)
    DX = TX + 30
    HX = DX + 160
    for y, nm, kind in rows:
        line([(TX, y), (DX, y)])
        text(DX + 62, y - 40, nm, 11, weight='bold')
        xx = DX
        for lab in ('7→5', '5→3', '3→1'):
            box(xx, y - 30, 30, 60, COL['dec'], [lab], size=10, vertical=True)
            if xx < DX + 90:
                line([(xx + 30, y), (xx + 46, y)])
            xx += 46
        line([(xx - 16, y), (HX, y)])
    box(HX, 250, 40, 360, COL['frozen'], ['lmhead 256→50304 (frozen, shared)'], hatch=True, vertical=True)
    SX = HX + 66
    for y, nm, kind in rows:
        line([(HX + 40, y), (SX, y)])
        box(SX, y - 28, 96, 56, COL['smp'], ['softmax', f'sample · {kind}'], size=11)
    for i, (y, nm, kind) in enumerate(rows):            # nested feedback, no crossings
        top = 160 - 16 * i
        xr = SX + 96 + 12 + 12 * i
        xl = 30 - 8 * i
        line([(SX + 96, y), (xr, y), (xr, top), (xl, top), (xl, ys[i]), (40, ys[i])])
    text(1150, 104, 'each stream\'s sample → its next input (training: the dataset\'s)', 11, fill=COL['soft'])

    legend(30, 738, [(COL['frozen'], True, 'frozen: embedding / lmhead (pythia-31m)'),
                     (COL['rep'], False, 'RMS norm (per sample, per position) · replicate'),
                     (COL['cat'], False, 'channel concatenation'),
                     (COL['lin'], False, 'conv 1×1 / 3×3 (linear): ctx_cat, linout'),
                     (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
                     (COL['dec'], False, 'decoder convs 3×3, 7→5→3→1 (linear)'),
                     (COL['smp'], False, 'softmax + sample (+ <NUL> logit)')],
           '(every layer\'s, reset to 0 at each example)', w=470)
    for i, s in enumerate(('Only layer 1 sees the inputs: text, voice and image tokens and sound reach layer 2',
                           'only through o₁. Layer 2 adds d₂ to o₁, and the decoders read the sum o.',
                           'Layer 2 started as the identity (linout zero-initialized): it was added at step',
                           '1,127,936 to a trained one-layer model, which it began by computing exactly.')):
        text(560, 820 + 20 * i + (10 if i > 1 else 0), s, 12.5, anchor='start', fill='#424242')

    out.append('<line x1="0" y1="1080" x2="1920" y2="1080" stroke="#9e9e9e" stroke-width="2"/>')

    # ── pane B: one layer ──────────────────────────────────────────────────
    out.append('<g transform="translate(0,1080)">')
    text(30, 46, 'B · one recurrent layer (layers 1 and 2 have the same structure; only their inputs differ)', 22,
         anchor='start', weight='bold')
    text(30, 70, 'its own weights · its own two registers (an EMA over ' + (f'{EMA1} ticks' if EMA1 == EMA2 else
         f'W = {EMA1} ticks in layer 1, {EMA2} in layer 2') + ', then the residual copy) · old '
         'register values read through per-sample RMSnorm · registers reset to 0 at each example', 13,
         anchor='start', fill='#424242')
    CYb, CXb = 400, 560
    box(60, 140, 400, 210, '#f5f9ff', [], rx=8)
    text(80, 166, 'layer 1 inputs', 14, anchor='start', weight='bold')
    for i, s in enumerate(('token grids (text, voice, image): 3 × 256×7×7, RMS',
                           'audio grid (log-mel): 256×7×7, RMS',
                           'image grid (encoder): future')):
        text(80, 194 + 24 * i, s, 12, anchor='start', fill='#9e9e9e' if 'future' in s else COL['ink'])
    text(80, 290, 'concat: 3×256 + 256 + 2×512 = 2048', 12, anchor='start', weight='bold')
    text(80, 312, 'ctx_cat 1×1: 2048 → 384', 12, anchor='start')
    box(60, 390, 400, 130, '#f5f9ff', [], rx=8)
    text(80, 416, 'layer 2 input', 14, anchor='start', weight='bold')
    text(80, 442, 'o₁ (layer 1 output): 512×7×7, RMS', 12, anchor='start')
    text(80, 466, 'concat: 512 + 2×512 = 1536', 12, anchor='start', weight='bold')
    text(80, 488, 'ctx_cat 1×1: 1536 → 384', 12, anchor='start')
    line([(460, 245), (CXb, 245)])
    line([(460, 455), (CXb, 455)])
    box(CXb, 120, 50, 780, COL['cat'], ['concat: the layer\'s inputs + its 2 registers (RMS)'], size=12,
        vertical=True)
    line([(CXb + 50, CYb), (660, CYb)])
    box(660, CYb - 150, 44, 300, COL['lin'], ['ctx_cat 1×1 → 384'], size=12, vertical=True)
    x = 750
    line([(704, CYb), (x, CYb)])
    for k in range(8):
        box(x, CYb - 100, 40, 200, COL['cnn'], [f'{k + 1}'], size=11)
        if k < 7:
            line([(x + 40, CYb), (x + 62, CYb)])
        x += 62
    text(750 + (62 * 8 - 22) / 2, CYb - 116, 'ContextCNN: 8 × (conv 3×3 + BN + ReLU), 384→384', 14, weight='bold')
    text(750 + (62 * 8 - 22) / 2, CYb + 124, '384×7×7 throughout', 11, fill=COL['soft'])
    LX = x
    line([(x - 22, CYb), (LX, CYb)])
    box(LX, CYb - 150, 44, 300, COL['lin'], ['linout 3×3 384→512'], size=12, vertical=True)
    BXb = LX + 200
    line([(LX + 44, CYb), (BXb, CYb)], arrow=False)
    dot(BXb, CYb)
    text(BXb - 8, CYb - 10, 'x = 512×7×7', 11, anchor='end', fill=COL['soft'])
    line([(BXb, CYb), (1880, CYb)])
    box(1560, CYb - 160, 320, 120, '#ffffff', [], rx=8)
    text(1576, CYb - 132, 'the layer\'s output x', 13, anchor='start', weight='bold')
    text(1576, CYb - 108, 'layer 1: o₁, to layer 2 and the adder', 12, anchor='start')
    text(1576, CYb - 86, 'layer 2: d₂, added to o₁ to give o', 12, anchor='start')
    text(1576, CYb - 64, 'o: to the three decoders', 12, anchor='start')

    y0, fx, ex = 600, 1120, 1330                         # the register cascade
    out.append(f'<rect x="800" y="{y0}" width="660" height="270" rx="6" fill="#fffde7" stroke="#9e9e9e" '
               f'stroke-dasharray="6,4"/>')
    text(816, y0 + 22, 'residual cascade (Laplacian pyramid) · 2 × 512×7×7', 13, anchor='start', weight='bold')
    text(816, y0 + 92, 'DFF_1: r ← r + (x − r)/' + (f'{EMA1}' if EMA1 == EMA2 else 'W'), 12, anchor='start')
    if EMA1 == EMA2:
        text(816, y0 + 110, f'EMA, window {EMA1} ticks ({EMA1 / 25:g} s)', 11, anchor='start', fill='#424242')
    else:
        text(816, y0 + 110, f'EMA, W = {EMA1} ticks ({EMA1 / 25:g} s) in layer 1,', 11, anchor='start', fill='#424242')
        text(816, y0 + 126, f'{EMA2} ticks ({EMA2 / 25:g} s) in layer 2', 11, anchor='start', fill='#424242')
    text(816, y0 + 218, 'DFF_2: r ← x − S_1', 12, anchor='start')
    text(816, y0 + 236, 'residual copy (window 1)', 11, anchor='start', fill='#424242')
    f1, f2 = y0 + 44, y0 + 172
    c1y, s2y = f1 + 23, f2 + 23
    out.append(f'<circle cx="{ex}" cy="{c1y}" r="26" fill="{COL["lmu"]}" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(ex, c1y - 2, 'EMA', 11, weight='bold')
    text(ex, c1y + 12, f'/{EMA1}' if EMA1 == EMA2 else '/W', 10)
    line([(BXb, CYb), (BXb, s2y)], arrow=False)
    dot(BXb, c1y)
    line([(BXb, c1y), (ex + 28, c1y)])
    line([(ex - 26, c1y), (fx + 66, c1y)])
    flop(fx, f1, 'DFF_1', size='')
    line([(1100, f1 + 16), (1100, f1 + 76), (ex, f1 + 76), (ex, c1y + 28)], dash=True, color='#757575')
    out.append(f'<circle cx="{ex}" cy="{s2y}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(ex, s2y + 6, '−', 18, weight='bold')
    line([(BXb, s2y), (ex + 18, s2y)])
    dot(1280, c1y)
    line([(1280, c1y), (1280, s2y - 44), (ex, s2y - 44), (ex, s2y - 18)])
    text(1286, s2y - 50, 'S_1', 11, anchor='start', fill=COL['soft'])
    line([(ex - 16, s2y), (fx + 66, s2y)])
    flop(fx, f2, 'DFF_2', size='')
    for qy, d in ((f1 + 16, 1100), (f2 + 16, None)):      # Q -> RMS -> concat
        line([(fx, qy), (702, qy)])
        if d:
            dot(d, qy)
        box(664, qy - 13, 36, 26, COL['rep'], ['RMS'], size=9.5)
        line([(664, qy), (CXb + 52, qy)])
    text(700, f1 - 2, 'old registers (t−1)', 10.5, fill=COL['soft'])

    legend(30, 600, [(COL['rep'], False, 'RMS norm (per sample, per position)'),
                     (COL['cat'], False, 'channel concatenation'),
                     (COL['lin'], False, 'conv 1×1 / 3×3 (linear)'),
                     (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
                     (COL['lmu'], False, f'EMA r ← r + (x − r)/W, W = {EMA1} ticks' if EMA1 == EMA2 else
                      f'EMA r ← r + (x − r)/W, W = {EMA1} (layer 1) / {EMA2} (layer 2)'),
                     ('#ffffff', False, '(−) subtractor: x minus the EMA as just written')],
           '(reset to 0 at each example)', w=470)
    out.append('</g>')
    out.append('</svg>')
    open(a.out or f'docs/figures/vla_{NAME}.svg', 'w').write('\n'.join(out))


def draw_v531():
    """1920 x 1080: one recurrent layer, its EMA register written at a learned rate (the write gate)."""
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'font-family="Helvetica, Arial, sans-serif">')
    out.append(DEFS)
    out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    text(30, 38, f'VLA {a.model} — one clock tick (40 ms): one recurrent CNN layer, its EMA register written through a '
         'learned gate', 22, anchor='start', weight='bold')
    text(30, 62, 'n_hidden 512 · c_context 384 · 7×7 grid · depth 8 · 3 token streams · 25 Hz · EMA (16 ticks to '
         'start) + copy, RMSnorm reads · reset at each example · 20.5M trainable · state 2 × 512×7×7 = 50,176 values',
         13, anchor='start', fill='#424242')
    CY = 330
    ys = (215, 265, 315)                                  # inputs
    for y, nm in zip(ys, ('text', 'voice', 'image')):
        mux(40, y)
        line([(74, y), (128, y)])
        text(100, y - 6, nm, 10, fill=COL['soft'])
    box(130, 190, 150, 150, COL['frozen'], ['tok_embed (frozen)', 'pythia-31m 50304×256', 'shared by 3 streams'],
        hatch=True)
    for y in ys:
        line([(280, y), (318, y)])
    box(320, 190, 40, 150, COL['rep'], ['RMS · replicate 1×1→7×7'], size=11, vertical=True)
    text(430, ys[0] - 8, 'token grids 3 × 256×7×7', 10, fill=COL['soft'])
    box(40, 400, 90, 44, COL['media'], ['audio', '16 kHz'])
    line([(130, 422), (158, 422)])
    box(160, 400, 150, 44, COL['mel'], ['log-mel (fixed)', '64 mels · 10 ms hop'])
    line([(310, 422), (328, 422)])
    box(330, 405, 36, 34, COL['norm'], ['RMS'], size=10)
    text(430, 414, 'audio grid 256×7×7', 10, fill=COL['soft'])
    box(40, 480, 90, 44, COL['media'], ['frame', '2 fps'], dash=True)
    line([(130, 502), (158, 502)], dash=True, color='#9e9e9e')
    box(160, 480, 150, 44, COL['frozen'], ['image encoder', '(future)'], hatch=True, dash=True)

    CX, CW = 500, 48                                      # concat, ctx_cat, ContextCNN, linout
    box(CX, 150, CW, 740, COL['cat'], ['concat  3×256 + 256 + 2×512 = 2048'], size=12, vertical=True)
    for y in ys:
        line([(360, y), (CX, y)])
    line([(366, 422), (CX, 422)])
    line([(CX + CW, CY), (578, CY)])
    box(580, CY - 120, 40, 240, COL['lin'], ['ctx_cat 1×1 2048→384'], vertical=True)
    x = 660
    line([(620, CY), (x, CY)])
    for k in range(8):
        box(x, CY - 90, 36, 180, COL['cnn'])
        if k < 7:
            line([(x + 36, CY), (x + 58, CY)])
        x += 58
    text(660 + (58 * 8 - 22) / 2, CY - 104, 'ContextCNN: 8 × (conv 3×3 + BN + ReLU), 384→384', 13, weight='bold')
    text(660 + (58 * 8 - 22) / 2, CY + 112, '384×7×7 throughout', 11, fill=COL['soft'])
    HT = x + 4                                            # the working state h, tapped for the gate
    LX = HT + 40
    line([(x - 22, CY), (LX, CY)])
    dot(HT, CY)
    text(HT, CY - 10, 'h', 13, weight='bold')
    box(LX, CY - 120, 40, 240, COL['lin'], ['linout 3×3 384→512'], vertical=True)
    BX = LX + 110                                         # the output bus
    line([(LX + 40, CY), (BX, CY)], arrow=False)
    dot(BX, CY)
    text(BX - 8, CY - 8, 'x = 512×7×7', 10, anchor='end', fill=COL['soft'])

    DX = BX + 70                                          # decoders, lmhead, sampling
    rows = ((200, 'text_dec', 'THINK'), (CY, 'voc_dec', 'HEAR'), (460, 'img_dec', 'SEE'))
    line([(BX, rows[0][0]), (BX, rows[2][0])], arrow=False)
    HX = DX + 220
    for y, nm, kind in rows:
        line([(BX, y), (DX, y)])
        text(DX + 80, y - 42, nm, 12, weight='bold')
        xx = DX
        for lab in ('3×3 7→5', '3×3 5→3', '3×3 3→1'):
            box(xx, y - 32, 34, 64, COL['dec'], [lab], size=10, vertical=True)
            if xx < DX + 120:
                line([(xx + 34, y), (xx + 60, y)])
            xx += 60
        line([(xx - 26, y), (HX, y)])
    box(HX, 150, 44, 360, COL['frozen'], ['lmhead 256→50304 (frozen, shared)'], hatch=True, vertical=True)
    SX = HX + 90
    for y, nm, kind in rows:
        line([(HX + 44, y), (SX, y)])
        box(SX, y - 28, 104, 56, COL['smp'], ['softmax', f'sample · {kind}'])
    for i, (y, nm, kind) in enumerate(rows):            # each stream's sample is its next input
        top = 120 - 13 * i
        xr = SX + 104 + 18 + 16 * i
        xl = 34 - 7 * i
        line([(SX + 104, y), (xr, y), (xr, top), (xl, top), (xl, ys[i]), (40, ys[i])])
    text(SX - 300, 88, 'each stream\'s sample → its next input (training: the dataset\'s)', 11, fill=COL['soft'])

    y0 = 620                                              # the register cascade, written through the gate
    out.append(f'<rect x="640" y="{y0}" width="{BX + 40 - 640}" height="270" rx="6" fill="#fffde7" '
               f'stroke="#9e9e9e" stroke-dasharray="6,4"/>')
    text(656, y0 + 22, 'residual cascade (Laplacian pyramid) · 2 × 512×7×7', 13, anchor='start', weight='bold')
    text(656, y0 + 92, 'DFF_1: r ← r + a ⊙ (x − r)', 12, anchor='start')
    text(656, y0 + 110, 'an EMA at a learned rate a', 11, anchor='start', fill='#424242')
    text(656, y0 + 126, 'per channel and position', 11, anchor='start', fill='#424242')
    text(656, y0 + 218, 'DFF_2: r ← x − S_1', 12, anchor='start')
    text(656, y0 + 236, 'residual copy (window 1)', 11, anchor='start', fill='#424242')
    fx, ex = 900, HT
    f1, f2 = y0 + 50, y0 + 172
    c1y, s2y = f1 + 23, f2 + 23
    gy = 470                                              # the write gate: a = sigmoid(wgate(h))
    line([(HT, CY), (HT, gy)])
    box(HT - 62, gy, 124, 58, COL['gate'], ['write gate', 'wgate 1×1 384→512', 'σ'], size=11)
    line([(HT, gy + 58), (HT, c1y - 28)])
    text(HT + 8, gy + 84, 'a = 512×7×7 rate', 10.5, anchor='start', fill=COL['soft'])
    text(HT + 8, gy + 98, '(starts at 1/16)', 10.5, anchor='start', fill=COL['soft'])
    out.append(f'<circle cx="{ex}" cy="{c1y}" r="26" fill="{COL["lmu"]}" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(ex, c1y - 2, 'EMA', 11, weight='bold')
    text(ex, c1y + 12, '× a', 10)
    line([(BX, CY), (BX, s2y)], arrow=False)
    dot(BX, c1y)
    line([(BX, c1y), (ex + 28, c1y)])
    line([(ex - 26, c1y), (fx + 66, c1y)])
    flop(fx, f1, 'DFF_1', size='')
    line([(880, f1 + 16), (880, f1 + 76), (ex, f1 + 76), (ex, c1y + 28)], dash=True, color='#757575')
    out.append(f'<circle cx="{ex}" cy="{s2y}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(ex, s2y + 6, '−', 18, weight='bold')
    line([(BX, s2y), (ex + 18, s2y)])
    sx = (fx + 66 + ex - 26) / 2
    dot(sx, c1y)
    line([(sx, c1y), (sx, s2y - 40), (ex, s2y - 40), (ex, s2y - 18)])
    text(sx + 6, s2y - 46, 'S_1', 11, anchor='start', fill=COL['soft'])
    line([(ex - 16, s2y), (fx + 66, s2y)])
    flop(fx, f2, 'DFF_2', size='')
    for qy, d in ((f1 + 16, 880), (f2 + 16, None)):      # Q -> RMS -> concat
        line([(fx, qy), (628, qy)])
        if d:
            dot(d, qy)
        box(590, qy - 13, 36, 26, COL['rep'], ['RMS'], size=9.5)
        line([(590, qy), (CX + CW + 2, qy)])
    text(780, f1 - 4, 'old registers (t−1)', 10.5, fill=COL['soft'])

    nx, ny = BX + 70, 620                                 # notes
    out.append(f'<rect x="{nx}" y="{ny}" width="{1890 - nx}" height="270" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
    text(nx + 18, ny + 28, 'the write gate', 14, anchor='start', weight='bold')
    for i, s in enumerate(('A 1×1 conv on the working state h sets DFF_1\'s write rate for each of',
                           'its 512 channels at each of the 49 positions, every tick. It starts at',
                           'the fixed rate 1/16 (weights 0, bias −log 15): the model it was added to.',
                           'The copy register needs no rate; it holds whatever the EMA did not.',
                           '',
                           {'v531': 'Trained: SGD, lr 0.01, momentum 0.5 · BPTT 64 ticks · the gate at 100× lr.',
                            'v533': 'Trained: SGD, lr 0.001, Nesterov momentum 0.95 · BPTT 64 ticks · gate at 100× lr.'
                            }[a.model],
                           'One layer: v522\'s second layer dropped (it never used its registers).')):
        text(nx + 18, ny + 56 + 22 * i, s, 12, anchor='start', fill='#424242')

    legend(30, 590, [(COL['frozen'], True, 'frozen: embedding / lmhead (pythia-31m)'),
                     (COL['rep'], False, 'RMS norm (per sample, per position) · replicate'),
                     (COL['cat'], False, 'channel concatenation'),
                     (COL['lin'], False, 'conv 1×1 / 3×3 (linear): ctx_cat, linout'),
                     (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
                     (COL['gate'], False, 'write gate: conv 1×1 + sigmoid → rate a'),
                     (COL['lmu'], False, 'EMA r ← r + a ⊙ (x − r)'),
                     ('#ffffff', False, '(−) subtractor: x minus the EMA as just written'),
                     (COL['dec'], False, 'decoder convs 3×3, 7→5→3→1 (linear)'),
                     (COL['smp'], False, 'softmax + sample (+ <NUL> logit)')],
           '(reset to 0 at each example)', w=440)
    out.append('</svg>')
    open(a.out or f'docs/figures/vla_{NAME}.svg', 'w').write('\n'.join(out))


if a.model in ('v505', 'v511'):
    draw_v505()
    raise SystemExit(0)
def draw_v536():
    """1920 x 2160: pane A (top) the whole model, pane B (bottom) one block."""
    W5, H5 = 1920, 2160
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W5}" height="{H5}" viewBox="0 0 {W5} {H5}" '
               f'font-family="Helvetica, Arial, sans-serif">')
    out.append(DEFS)
    out.append(f'<rect width="{W5}" height="{H5}" fill="#ffffff"/>')

    # ── pane A: the whole model ─────────────────────────────────────────────
    V8 = a.model in ('v538', 'v540', 'v552')   # --grid_hist 8 (learned ring input)
    NC = 3 if a.model in ('v540', 'v552') else 2   # --cd_convs: conv 3x3 + BN + ReLU layers per block
    NF = a.model == 'v552'                # no FIFO, beta in (0, 2), banded windows, every document reset
    DF = a.model == 'v569'                # the memory first, then the convs; 7 blocks at 256 channels
    NT = a.model in ('v564', 'v569')      # no time conv at all, blocks of 7 convs, every document reset
    if NT:
        NC = 7
    NB = 7 if DF else 3 if NT else 6      # --convdelta: blocks
    CC = 256 if DF else 384               # --c_context
    text(30, 38, f'VLA {NAME} — one clock tick (40 ms): a ConvDelta language model, {NB} residual blocks of '
         'per-tick convs, each with a gated delta-rule memory per grid position', 22, anchor='start', weight='bold')
    text(30, 62, f'A · the whole model.  --lm: text only · C {CC} · 7×7 grid · {NB} blocks · H 6 heads × d 32 per position '
         '· 25 Hz · ' + ('33.95M trainable · fixed state 2,107,392 values · input: this token, copied to every grid position '
                         '· trained 256 ticks at a time, every document reset' if DF else
                         '33.05M trainable · fixed state 903,168 values · input: this token, copied to every grid position '
                         '· trained 256 ticks at a time, every document reset' if NT else
                         '29.98M trainable · fixed state 1,806,385 values · input: the last 8 tokens on a learned map '
                         '· trained 256 ticks at a time, every document reset' if NF else
                         ('29.97M' if NC == 3 else '22.01M') + ' trainable · fixed state 2,145,073 values · input: the last 8 tokens on a learned map '
                         '· trained 256 ticks at a time, half the documents unreset' if V8 else
                         '21.97M trainable · fixed state 2,145,024 values · trained a 256-tick window at a time'), 13,
         anchor='start', fill='#424242')
    CY = 400
    mux(40, CY)
    if V8:                                # the last 8 tokens, each embedded, mixed onto the grid by a[j, p]
        line([(74, CY), (82, CY), (82, CY - 84), (92, CY - 84)])     # the new token enters at t
        text(57, CY - 20, 'text', 10, fill=COL['soft'])
        for j in range(8):
            yy = CY - 96 + 24 * j
            out.append(f'<rect x="92" y="{yy}" width="44" height="24" fill="#ffffff" stroke="{COL["ink"]}" '
                       f'stroke-width="1.1"/>')
            text(114, yy + 16, 't' if j == 0 else f't−{j}', 10.5)
        text(114, CY - 104, 'last 8 tokens', 10, fill=COL['soft'])
        text(114, CY + 112, 'shift down a slot', 9.5, fill=COL['soft'])
        text(114, CY + 124, 'each tick (in the state)', 9.5, fill=COL['soft'])
        line([(136, CY), (150, CY)])
        box(150, CY - 75, 92, 150, COL['frozen'], ['tok_embed', '(frozen)', 'each token'], size=11, hatch=True)
        line([(242, CY), (254, CY)])
        box(254, CY - 60, 26, 120, COL['rep'], ['RMS'], size=10, vertical=True)
        line([(280, CY), (292, CY)])
        box(292, CY - 75, 34, 150, COL['lin'], ['ctx_cat 1×1 256→384'], size=10, vertical=True)
        line([(326, CY), (344, CY)])
        text(309, CY + 90, '8 × 384', 9.5, fill=COL['soft'])
        cs, gx, gy = 14, 346, CY - 49                     # the map's starting rings, as a 7x7 icon
        shade = ['#1a237e', '#3949ab', '#7986cb', '#c5cae9']
        for r_ in range(7):
            for c_ in range(7):
                k = 3 - max(abs(r_ - 3), abs(c_ - 3))
                out.append(f'<rect x="{gx + c_ * cs}" y="{gy + r_ * cs}" width="{cs}" height="{cs}" '
                           f'fill="{shade[k]}" stroke="#ffffff" stroke-width="0.6"/>')
        text(gx + 49, gy - 26, 'learned map a[j, p]', 11, weight='bold')
        text(gx + 49, gy - 12, '8 × 7×7, mixes the tokens', 9.5, fill=COL['soft'])
        text(gx + 49, gy + 114, 'start: rings, outer t', 9.5, fill=COL['soft'])
        text(gx + 49, gy + 127, '… centre t−3', 9.5, fill=COL['soft'])
        line([(gx + 98, CY), (480, CY)])
    else:
        line([(74, CY), (128, CY)])
        text(100, CY - 6, 'text', 10, fill=COL['soft'])
        box(130, CY - 75, 150, 150, COL['frozen'], ['tok_embed (frozen)', 'pythia-31m 50304×256'], hatch=True)
        line([(280, CY), (318, CY)])
        box(320, CY - 75, 40, 150, COL['rep'], ['RMS · replicate 1×1→7×7'], size=11, vertical=True)
        text(385, CY + 18, '256×7×7', 10, fill=COL['soft'])
        PX = 410
        line([(360, CY), (PX, CY)])
        box(PX, CY - 120, 40, 240, COL['lin'], [f'ctx_cat 1×1 256 → {CC}'], size=11, vertical=True)
        line([(PX + 40, CY), (480, CY)])
    box(480, CY - 120, 44, 240, COL['gate'], ['per position: × G + P'], size=11, vertical=True)
    x0 = 560
    line([(524, CY), (x0, CY)])
    BW, GAP = (96, 8) if DF else (220, 20) if NT else (100, 20)
    for i in range(NB):                                   # the blocks
        bx = x0 + i * (BW + GAP)
        if DF:                                            # the memory, then 7 convs
            out.append(f'<rect x="{bx}" y="{CY - 140}" width="{BW}" height="280" rx="8" fill="#f5f9ff" '
                       f'stroke="{COL["ink"]}" stroke-width="1.4"/>')
            text(bx + BW / 2, CY - 150, f'block {i + 1}', 12, weight='bold')
            line([(bx, CY), (bx + 9, CY)])
            out.append(f'<circle cx="{bx + 20}" cy="{CY}" r="11" fill="{COL["lmu"]}" stroke="{COL["ink"]}" '
                       f'stroke-width="1.2"/>')
            text(bx + 20, CY + 4, 'Δ', 11, weight='bold')
            out.append(f'<rect x="{bx + 5}" y="{CY + 62}" width="30" height="26" fill="#ffffff" '
                       f'stroke="{COL["ink"]}" stroke-width="1.2"/>')
            text(bx + 20, CY + 80, 'S', 11, weight='bold')
            line([(bx + 17, CY + 11), (bx + 17, CY + 62)])
            line([(bx + 24, CY + 62), (bx + 24, CY + 13)], dash=True, color='#757575')
            line([(bx + 31, CY), (bx + 40, CY)], arrow=False)
            for j in range(NC):
                cx_ = bx + 40 + 8 * j
                box(cx_, CY - 50, 6, 100, COL['cnn'], rx=1)
            line([(bx + 40 + 8 * NC - 2, CY), (bx + BW + GAP, CY)])
            text(bx + 66, CY + 72, f'{NC} × conv', 9.5, fill=COL['soft'])
            text(bx + BW / 2, CY + 118, '49×6×32×32', 9, fill=COL['soft'])
            continue
        if NT:                                            # 7 convs, then the memory; no time conv
            out.append(f'<rect x="{bx}" y="{CY - 140}" width="{BW}" height="280" rx="8" fill="#f5f9ff" '
                       f'stroke="{COL["ink"]}" stroke-width="1.4"/>')
            text(bx + BW / 2, CY - 150, f'block {i + 1}', 12, weight='bold')
            for j in range(NC):
                cx_ = bx + 10 + 20 * j
                line([(bx if not j else cx_ - 8, CY), (cx_, CY)], arrow=False)
                box(cx_, CY - 50, 12, 100, COL['cnn'], rx=2)
            line([(bx + 10 + 20 * NC - 8, CY), (bx + BW - 56, CY)])
            DXc = bx + BW - 42
            out.append(f'<circle cx="{DXc}" cy="{CY}" r="13" fill="{COL["lmu"]}" stroke="{COL["ink"]}" '
                       f'stroke-width="1.2"/>')
            text(DXc, CY + 4, 'Δ', 12, weight='bold')
            line([(DXc + 13, CY), (bx + BW + GAP, CY)])
            out.append(f'<rect x="{DXc - 20}" y="{CY + 62}" width="40" height="30" fill="#ffffff" '
                       f'stroke="{COL["ink"]}" stroke-width="1.2"/>')
            text(DXc, CY + 82, 'S', 12, weight='bold')
            line([(DXc - 4, CY + 13), (DXc - 4, CY + 62)])
            line([(DXc + 6, CY + 62), (DXc + 6, CY + 15)], dash=True, color='#757575')
            text(bx + 80, CY + 72, f'{NC} × conv 3×3', 10, fill=COL['soft'])
            text(DXc, CY + 118, '49×6×32×32', 9.5, fill=COL['soft'])
            continue
        out.append(f'<rect x="{bx}" y="{CY - 140}" width="{BW}" height="280" rx="8" fill="#f5f9ff" '
                   f'stroke="{COL["ink"]}" stroke-width="1.4"/>')
        text(bx + BW / 2, CY - 150, f'block {i + 1}', 12, weight='bold')
        line([(bx, CY), (bx + 8, CY)], arrow=False)
        box(bx + 8, CY - 40, 14, 80, COL['tconv'], rx=2)
        line([(bx + 22, CY), (bx + 30, CY)], arrow=False)
        cw = 12 if NC == 2 else 8                         # the convs, side by side in x 30 .. 58
        for j in range(NC):
            cx_ = bx + 30 + j * (28 - cw) // (NC - 1) if NC > 1 else bx + 30
            if j:
                line([(cx_ - (28 - cw) // (NC - 1) + cw, CY), (cx_, CY)], arrow=False)
            box(cx_, CY - 50, cw, 100, COL['cnn'], rx=2)
        line([(bx + 58, CY), (bx + 64, CY)])
        out.append(f'<circle cx="{bx + 78}" cy="{CY}" r="13" fill="{COL["lmu"]}" stroke="{COL["ink"]}" '
                   f'stroke-width="1.2"/>')
        text(bx + 78, CY + 4, 'Δ', 12, weight='bold')
        line([(bx + 91, CY), (bx + BW + GAP, CY)])
        out.append(f'<rect x="{bx + 58}" y="{CY + 62}" width="40" height="30" fill="#ffffff" stroke="{COL["ink"]}" '
                   f'stroke-width="1.2"/>')
        text(bx + 78, CY + 82, 'S', 12, weight='bold')
        line([(bx + 74, CY + 13), (bx + 74, CY + 62)])
        line([(bx + 84, CY + 62), (bx + 84, CY + 15)], dash=True, color='#757575')
        text(bx + BW / 2, CY + 118, '49×6×32×32', 9.5, fill=COL['soft'])
    text(x0 + NB * (BW + GAP) / 2 - GAP / 2, CY + 172, ('each block: delta-rule memory Δ with its state S → '
         f'{NC} × (conv 3×3 + BN + ReLU)' if DF else '') or (('each block:' if NT else 'each block: scaled RMS(x) added →' if NF else
         'each block: causal time conv (4 ticks) →') + f' {NC} × (conv 3×3 + BN + '
         'ReLU) → delta-rule memory Δ with its state S'), 12, fill='#424242')
    zx = x0 + (3 if DF else 1 if NT else 2) * (BW + GAP) - 8   # zoom marker on the middle block
    out.append(f'<rect x="{zx}" y="{CY - 172}" width="{BW + 16}" height="320" rx="12" fill="none" '
               f'stroke="#e65100" stroke-width="2" stroke-dasharray="8,5"/>')
    text(zx + 8, CY + 198, 'one block, zoomed in: pane B ▼', 12, anchor='start', fill='#e65100', weight='bold')
    LX = x0 + NB * (BW + GAP)                              # linout, then the decoder
    box(LX, CY - 120, 40, 240, COL['lin'], [f'linout 3×3 {CC} → 512'], size=11, vertical=True)
    BX = LX + 70
    line([(LX + 40, CY), (BX, CY)], arrow=False)
    dot(BX, CY)
    text(BX + 4, CY - 10, 'o', 13, anchor='start', weight='bold')
    DX = BX + 30
    line([(BX, CY), (DX, CY)])
    text(DX + 62, CY - 42, 'text_dec', 12, weight='bold')
    xx = DX
    for lab in ('3×3 7→5', '3×3 5→3', '3×3 3→1'):
        box(xx, CY - 34, 32, 68, COL['dec'], [lab], size=10, vertical=True)
        if xx < DX + 100:
            line([(xx + 32, CY), (xx + 50, CY)])
        xx += 50
    HX = xx + 10
    line([(xx - 18, CY), (HX, CY)])
    box(HX, CY - 120, 44, 240, COL['frozen'], ['lmhead 256 → 50304 (frozen)'], hatch=True, vertical=True)
    SX = HX + 80
    line([(HX + 44, CY), (SX, CY)])
    box(SX, CY - 30, 110, 60, COL['smp'], ['softmax', 'sample (+ <NUL>)'], size=11)
    line([(SX + 110, CY), (SX + 132, CY), (SX + 132, 140), (30, 140), (30, CY), (40, CY)])
    text(1100, 132, 'the sampled token → the next tick\'s input (training: the dataset\'s)', 11, fill=COL['soft'])

    legend(30, 640, [(COL['frozen'], True, 'frozen: embedding / lmhead (pythia-31m)'),
                     (COL['rep'], False, 'RMS norm' if V8 else 'RMS norm · replicate 1×1 → 7×7')] +
           ([('#3949ab', False, 'learned input map a[j, p]: tokens t … t−7 onto the grid')] if V8 else []) + [
                     (COL['lin'], False, 'conv 1×1 / 3×3 (linear): ctx_cat, linout'),
                     (COL['gate'], False, 'per-position gain G and bias P (learned)')] +
           ([] if NT else [(COL['tconv'], False, 'per-channel scale of RMS(x), this tick only (no FIFO)' if NF else
                            'causal depthwise conv over the last 4 ticks')]) + [
                     (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
                     (COL['lmu'], False, 'Δ: gated delta-rule memory update and read'),
                     (COL['dec'], False, 'decoder convs 3×3, 7→5→3→1 (linear)'),
                     (COL['smp'], False, 'softmax + sample (+ <NUL> logit)')],
           '(training: reset at half the document starts)' if V8 and not NF else
           '(S: reset to 0 at each document start)', w=560)
    if NC == 2:                           # (v540: no revision notes)
        nx = 650
        out.append(f'<rect x="{nx}" y="640" width="{1890 - nx}" height="380" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
        text(nx + 18, 668, 'how it differs from v536' if V8 else
             'how it differs from v533', 14, anchor='start', weight='bold')
        for i, s_ in enumerate((
                'The input grid shows the last 8 tokens, not one token copied to every cell: cell p holds Σⱼ a[j, p] · ctx_cat(token t−j)',
                'with a learned 8 × 7×7 map a, which starts as concentric rings (t on the outer ring, t−1, t−2 inward, t−3 at the',
                'centre; t−4 … t−7 at 0, free to be recruited). Neighbouring cells now hold neighbouring moments, so the 3×3 convs',
                'see tokens side by side and can form n-gram features in one layer. The 7 past token ids ride in the state.',
                '',
                'Stress test for perception discontinuities (--reset_prob 0.5): in training, half of the document starts reset',
                'the state and half do not, so the previous, unrelated document\'s memories carry straight on, marked only by',
                'the separator token, as when a robot\'s continuous perception jumps to a new scene, task or speaker. The model',
                'must learn to let go of stale context itself (the decay α and write strength β see the input). Evals still',
                'reset per document; EVALW measures the unreset case.',
                '',
                'Otherwise as v536: --lm, 6 ConvDelta blocks, AdamW (β 0.9, 0.95), lr warmed to 0.001, 32 × 256 tokens per update.',
        ) if V8 else (
                'No conv reads the state. The convs see only this tick\'s input to their block, so in training they run on all',
                '256 ticks of a window at once ([32·256, 384, 7, 7], in bf16), and the memories S, the only state carried',
                'from tick to tick, are trained over the whole window by a chunked parallel scan (their update is linear in',
                'S). The state carries on between windows. On the chip it runs one tick at a time, as v533 does.',
                '',
                'The state is an associative memory, not an average: each of the 49 positions holds 6 heads of 32×32',
                'key→value matrices per block, written by the delta rule and read by a query. The heads\' base decay windows',
                'start log-spaced from 4 to 4,096 ticks. The time conv carries the last 4 ticks (the copy register\'s job).',
                'G and P let the 49 columns differ, since every position gets the same token. A document start zeroes S.',
                '',
                '--lm: text only (no audio, image, voice or image streams; one decoder). AdamW (β 0.9, 0.95, no weight decay),',
                'lr warmed up to 0.001 over 1,000 updates of 32 × 256 tokens. State: 2,145,024 values, fixed for any context.')):
            text(nx + 18, 696 + 24 * i, s_, 12.5, anchor='start', fill='#424242')

    out.append('<line x1="0" y1="1080" x2="1920" y2="1080" stroke="#9e9e9e" stroke-width="2"/>')

    # ── pane B: one block ──────────────────────────────────────────────────
    out.append('<g transform="translate(0,1080)">')
    text(30, 46, f'B · one block (all {NB} have this structure, each with its own weights and memory)', 22,
         anchor='start', weight='bold')
    text(30, 70, f'x: {CC}×7×7 per tick · H = 6 heads of d = 32 at each of the 49 positions · every operation is per '
         'position except the 3×3 convs' + (' · fixed base windows w, log-spaced over the heads: 4 … 4,096 ticks '
                                            '(blocks 1–4), 64 … 16,384 (blocks 5–6)' if NF else ''),
         13, anchor='start', fill='#424242')
    CYb = 330
    text(40, CYb - 10, 'x', 14, anchor='start', weight='bold')
    text(40, CYb + 20, 'from below', 10, anchor='start', fill=COL['soft'])
    line([(60, CYb), (110, CYb)], arrow=False)
    dot(110, CYb)
    if DF:                                # the memory first: x goes straight to the projections
        pass
    elif NT:                              # no time conv: x goes straight to the convs
        cx_ = 150
        for j in range(NC):
            line([(110 if not j else cx_ - 32, CYb), (cx_, CYb)])
            box(cx_, CYb - 80, 40, 160, COL['cnn'], ['conv 3×3 · BN · ReLU'], size=11, vertical=True)
            cx_ += 72
        line([(cx_ - 32, CYb), (663, CYb)])
        line([(110, CYb), (110, CYb + 110), (680, CYb + 110), (680, CYb + 18)])
    else:
        line([(110, CYb), (140, CYb)])
        box(140, CYb - 17, 36, 34, COL['rep'], ['RMS'], size=10)
        line([(176, CYb), (230, CYb)])
    if NT:
        pass
    elif NF:                                # no FIFO: a per-channel scale of this tick's RMS(x)
        box(230, CYb - 50, 130, 100, COL['tconv'], ['per-channel scale', 'of RMS(x)', 'this tick only'], size=11)
    else:
        for j, fx in enumerate((350, 250, 150)):         # the time conv's FIFO of past inputs (in at the right)
            flop(fx, 130, f't−{j + 1}', size='')
        line([(196, CYb), (196, 190), (450, 190), (450, 153), (416, 153)])
        line([(350, 146), (330, 146), (330, 160), (316, 160)])
        line([(250, 146), (230, 146), (230, 160), (216, 160)])
        text(282, 118, 'last 3 ticks\' inputs (384×7×7 each)', 10.5, fill=COL['soft'])
        box(230, CYb - 50, 130, 100, COL['tconv'], ['causal time conv', 'depthwise, 4 taps', 'this tick + last 3'],
            size=11)
        for qx in (182, 282, 382):
            line([(qx - 32 + 32, 176), (qx - 32 + 32, CYb - 52)], dash=True, color='#757575')
    if not NT:
        line([(360, CYb), (393, CYb)])
        out.append(f'<circle cx="410" cy="{CYb}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
        text(410, CYb + 7, '+', 20, weight='bold')
        line([(110, CYb), (110, CYb + 90), (410, CYb + 90), (410, CYb + 18)])
        line([(426, CYb), (470, CYb)], arrow=False)
        dot(470, CYb)
        cx_ = 500 if NC == 2 else 484                         # the convs: 2 at 500, 580; 3 at 484, 544, 604
        for j in range(NC):
            line([(470 if not j else cx_ - (80 if NC == 2 else 60) + (44 if NC == 2 else 40), CYb), (cx_, CYb)])
            box(cx_, CYb - 80, 44 if NC == 2 else 40, 160, COL['cnn'], ['conv 3×3 · BN · ReLU'], size=11, vertical=True)
            cx_ += 80 if NC == 2 else 60
        line([(cx_ - (80 if NC == 2 else 60) + (44 if NC == 2 else 40), CYb), (663, CYb)])
    OX = -630 if DF else 0                                # --cd_delta_first: the memory section moves left
    if not DF:
        out.append(f'<circle cx="680" cy="{CYb}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
        text(680, CYb + 7, '+', 20, weight='bold')
        if not NT:
            line([(470, CYb), (470, CYb + 110), (680, CYb + 110), (680, CYb + 18)])
        text(562, CYb + 128, 'spatial mixing, per tick', 10.5, fill=COL['soft'])
    UX = 740 + OX
    if not DF:
        line([(696, CYb), (UX, CYb)], arrow=False)
        dot(UX, CYb)
        text(UX, CYb - 12, 'u', 14, weight='bold')
    AX = 1720 + OX                                        # the residual add after the read
    line([(UX, CYb), (AX - 18, CYb)])
    out.append(f'<circle cx="{AX}" cy="{CYb}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
    text(AX, CYb + 7, '+', 20, weight='bold')
    if DF:                                # then the convs, with their residual add
        line([(AX + 16, CYb), (AX + 50, CYb)], arrow=False)
        dot(AX + 50, CYb)
        text(AX + 50, CYb - 12, 'u', 14, weight='bold')
        cx_ = AX + 90
        for j in range(NC):
            line([(AX + 50 if not j else cx_ - 32, CYb), (cx_, CYb)])
            box(cx_, CYb - 80, 40, 160, COL['cnn'], ['conv 3×3 · BN · ReLU'], size=11, vertical=True)
            cx_ += 72
        line([(cx_ - 32, CYb), (1702, CYb)])
        out.append(f'<circle cx="1720" cy="{CYb}" r="16" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.3"/>')
        text(1720, CYb + 7, '+', 20, weight='bold')
        line([(AX + 50, CYb), (AX + 50, CYb + 110), (1720, CYb + 110), (1720, CYb + 18)])
        text((AX + 1720) / 2 + 25, CYb + 128, 'spatial mixing, per tick', 10.5, fill=COL['soft'])
        line([(1736, CYb), (1880, CYb)])
    else:
        line([(AX + 16, CYb), (1880, CYb)])
    text(1880, CYb - 12, 'x′ to the next block', 12, anchor='end', weight='bold')

    pr = (('q', 'query', 490, True), ('k', 'key', 550, True), ('v', 'value', 610, False),
          ('β', 'σ(·) (1 + tanh(·)): 0 … 2' if NF else 'write strength σ(·)', 670, False),
          ('α', 'window w · 2^(−tanh(·))' if NF else 'decay exp(−2 exp(λ) σ(·))', 730, False))
    line([(UX, CYb), (UX, 730)], arrow=False)
    for nm, desc, y, l2 in pr:
        line([(UX, y), (800 + OX, y)])
        box(800 + OX, y - 18, 190, 36, COL['lin'] if nm in 'qkv' else COL['gate'], [f'1×1 conv → {nm}', desc], size=11)
        if l2:
            line([(990 + OX, y), (1010 + OX, y)])
            box(1010 + OX, y - 13, 40, 26, COL['norm'], ['L2'], size=10)
    text(895 + OX, 452, 'per position: 6 heads × 32', 10.5, fill=COL['soft'])
    DX0, DY0, DW, DH = 1110 + OX, 520, 300, 240               # the delta-rule update
    box(DX0, DY0, DW, DH, COL['lmu'], [], rx=8)
    text(DX0 + DW / 2, DY0 + 30, 'gated delta rule', 14, weight='bold')
    text(DX0 + DW / 2, DY0 + 64, 'S ← α · S (I − β k kᵀ) + β v kᵀ', 14)
    text(DX0 + DW / 2, DY0 + 96, 'erase what k pointed at, write v there,', 11, fill='#424242')
    text(DX0 + DW / 2, DY0 + 114, 'decay the rest by α', 11, fill='#424242')
    if NF:
        text(DX0 + DW / 2, DY0 + 130, 'β > 1 reflects along k (tracks state)', 11, fill='#424242')
    text(DX0 + DW / 2, DY0 + 146, 'per position, per head: d×d = 32×32', 11, fill='#424242')
    text(DX0 + DW / 2, DY0 + 164, 'about 3d² MACs each per tick', 11, fill='#424242')
    text(DX0 + DW / 2, DY0 + 198, 'no weights of its own: S is state (fast weights),', 11, weight='bold')
    text(DX0 + DW / 2, DY0 + 216, 'learned only through the 1×1 convs feeding it', 11, weight='bold')
    for nm, desc, y, l2 in pr[1:]:
        line([(1050 + OX if l2 else 990 + OX, y), (DX0, y)])
    MX, MY = 1180 + OX, 820                                    # the memory register
    flop(MX, MY, 'S', size='49 × 6 × 32×32 = 301,056')
    line([(DX0 + DW - 60, DY0 + DH), (DX0 + DW - 60, MY + 23), (MX + 66, MY + 23)])
    line([(MX, MY + 16), (DX0 + 30, MY + 16), (DX0 + 30, DY0 + DH + 2)], dash=True, color='#757575')
    text(DX0 + 34, MY + 40, 'S (t−1)', 10.5, anchor='start', fill=COL['soft'])
    RX = 1440 + OX                                             # the read
    box(RX, 470, 110, 40, COL['lmu'], ['read  S q'], size=12)
    line([(1050 + OX, 490), (1080 + OX, 490), (1080 + OX, 440), (RX + 55, 440), (RX + 55, 468)])
    line([(DX0 + DW, 640), (RX + 55, 640), (RX + 55, 512)])
    text(DX0 + DW + 8, 632, 'S (t)', 10.5, anchor='start', fill=COL['soft'])
    box(RX + 140, 470, 80, 40, COL['lin'], ['1×1 out'], size=11)
    line([(RX + 110, 490), (RX + 140, 490)])
    line([(RX + 220, 490), (AX, 490), (AX, CYb + 18)])
    text(AX + 6, 420, 'y', 13, anchor='start', weight='bold')
    box(800 + OX, 790, 190, 50, '#ffffff', ['document start', 'S zeroed' if NF or NT else 'S and the FIFO zeroed'], size=11,
        dash=True)
    line([(895 + OX, 790), (895 + OX, 750)], dash=True, color='#757575')

    out.append(f'<rect x="1530" y="600" width="360" height="420" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
    text(1548, 628, 'training vs the chip', 14, anchor='start', weight='bold')
    for i, s_ in enumerate((
            *(('Training: the projections and the convs run',
               'on all 256 ticks of a window (32 rows) at once.') if DF else
              ('Training: everything before Δ runs on all',
               '256 ticks of a window (32 rows) at once.')),
            'q, k, v, β, α for the window go to a',
            'chunked scan (the WY form of the delta',
            'rule, Yang et al. 2024), giving every S q',
            'exactly. The state carries on between',
            'windows; the gradient stops at a window\'s start.',
            '',
            'Chip: one tick at a time. Per block it',
            'holds S, and does' if NF or NT else 'holds S and the 3-tick FIFO, and does',
            'the convs, five 1×1 projections and',
            '49 × 6 small 32×32 updates and reads.',
            'Same results as training, by construction.')):
        text(1548, 656 + 25 * i, s_, 12, anchor='start', fill='#424242')

    legend(1010 if DF else 30, 560, ([] if NT else [(COL['rep'], False, 'RMS norm (per position, over channels)')]) + [
                     (COL['norm'], False, 'L2: q, k scaled to unit length per head (keeps S bounded)'),
                     ] + ([] if NT else [(COL['tconv'], False, 'per-channel scale of RMS(x) (no FIFO)' if NF else
                                          'causal depthwise conv over time, 4 taps')]) + [
                     (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
                     (COL['lin'], False, 'conv 1×1 (linear): q, k, v, out'),
                     (COL['gate'], False, 'gates: β = σ(·)(1 + tanh(·)); α: window w · 2^(−tanh(·)), w fixed per head' if NF else
                      'gates: β = σ(·), α = exp(−2 exp(λ) σ(·)), λ per head'),
                     (COL['lmu'], False, 'delta-rule update / read (linear in S)'),
                     ('#ffffff', False, '(+) residual add')],
           '(S: reset at each document start)' if NF or NT else
           '(S and the FIFO; training: reset at half the document starts)' if V8 else
           '(S, and the FIFO: reset at each document start)', w=500 if DF else 640)
    out.append('</g>')
    out.append('</svg>')
    open(a.out or f'docs/figures/vla_{NAME}.svg', 'w').write('\n'.join(out))


if a.model in ('v531', 'v533'):
    draw_v531()
    raise SystemExit(0)
if a.model in ('v536', 'v538', 'v540', 'v552', 'v564', 'v569'):
    draw_v536()
    raise SystemExit(0)

# ── canvas ────────────────────────────────────────────────────────────────────
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica, Arial, sans-serif">')
out.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M 0,0 L 10,5 L 0,10 z" fill="#212121"/></marker>'
           '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           '<line x1="0" y1="0" x2="0" y2="6" stroke="#757575" stroke-width="1.2"/></pattern></defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
if LMU:
    text(30, 38, 'VLA v498 — one clock tick (40 ms): recurrent CNN + Legendre memories + recall attention', 22,
         anchor='start', weight='bold')
    text(30, 62, 'n_hidden 512 · c_context 384 · 7×7 grid · depth 8 · 3 token streams · 25 Hz · state never reset '
         '(continuous) · 21.3M trainable · state 125,440 register + 100,352 ring values · image / audio encoders: '
         'future', 13, anchor='start', fill='#424242')
elif CASC:
    text(30, 38, 'VLA v502 — one clock tick (40 ms): recurrent CNN + residual EMA cascade + recall attention', 22,
         anchor='start', weight='bold')
    text(30, 62, 'n_hidden 512 · c_context 384 · 7×7 grid · depth 8 · 3 token streams · 25 Hz · RMSnorm reads · '
         'reset at each example · 20.7M trainable · state 50,176 register + 100,352 ring values · image / audio '
         'encoders: future', 13, anchor='start', fill='#424242')
else:
    text(30, 38, 'VLA v499 — one clock tick (40 ms): recurrent CNN with recall attention as its only state', 22,
         anchor='start', weight='bold')
    text(30, 62, 'n_hidden 512 · c_context 384 · 7×7 grid · depth 8 · 3 token streams · 25 Hz · no registers · '
         'ring emptied at each example · 20.3M trainable · state 100,352 ring values · image / audio encoders: future',
         13, anchor='start', fill='#424242')

CY = 340                                  # main path centre line
# ── inputs ────────────────────────────────────────────────────────────────────
ys = (205, 255, 305)
for y, nm in zip(ys, ('text', 'voice', 'image')):
    mux(40, y)
    line([(74, y), (128, y)])
    text(100, y - 6, nm, 10, fill=COL['soft'])
box(130, 180, 150, 150, COL['frozen'], ['tok_embed (frozen)', 'pythia-31m 50304×256', 'shared by 3 streams'],
    hatch=True)
for y in ys:
    line([(280, y), (318, y)])
box(320, 180, 40, 150, COL['rep'], ['RMS · replicate 1×1→7×7'], size=11, vertical=True)

box(40, 395, 90, 44, COL['media'], ['audio', '16 kHz'])
line([(130, 417), (158, 417)])
box(160, 395, 150, 44, COL['mel'], ['log-mel (fixed)', '64 mels · 10 ms hop'])
line([(310, 417), (328, 417)])
box(330, 400, 36, 34, COL['norm'], ['RMS'], size=10)

# ── concat, ctx_cat, ContextCNN, linout ───────────────────────────────────────
CX, CW = 500, 48
box(CX, 150, CW, 900 if LMU else 760 if CASC else 510, COL['cat'], [f'concat  {CAT[0]} = {CAT[1]}'],
    size=12, vertical=True)
for y, s in zip(ys, ('256×7×7', '', '')):
    line([(360, y), (CX, y)])
line([(366, 417), (CX, 417)])
text(430, 410, 'audio grid 256×7×7', 10, fill=COL['soft'])
box(40, 470, 90, 44, COL['media'], ['frame', '2 fps · 3×224×224'])
line([(130, 492), (158, 492)])
box(160, 470, 150, 44, COL['frozen'], ['ResNet-50 (frozen)', 'a1_in1k'], hatch=True)
line([(310, 492), (328, 492)])
box(330, 475, 36, 34, COL['norm'], ['RMS'], size=10)
line([(366, 492), (CX, 492)])
text(430, 485, 'image grid 2048×7×7', 10, fill=COL['soft'])
text(430, ys[0] - 6, 'token grids', 10, fill=COL['soft'])

line([(CX + CW, CY), (578, CY)])
box(580, 220, 40, 240, COL['lin'], [f'ctx_cat 1×1 {CAT[1]}→384'], vertical=True)
x = 660
line([(620, CY), (x, CY)])
for k in range(8):
    box(x, 250, 36, 180, COL['cnn'])
    if k < 7:
        line([(x + 36, CY), (x + 58, CY)])
    x += 58
text(660 + (58 * 8 - 22) / 2, 236, 'ContextCNN: 8 × (conv 3×3 + BN + ReLU), 384→384', 13, weight='bold')
text(660 + (58 * 8 - 22) / 2, 452, '384×7×7 throughout', 11, fill=COL['soft'])
LX = x
line([(x - 22, CY), (LX, CY)])
box(LX, 220, 40, 240, COL['lin'], ['linout 3×3 384→512'], vertical=True)
BX = LX + 110                             # the linout output bus
line([(LX + 40, CY), (BX, CY)], arrow=False)
dot(BX, CY)
text(BX - 8, CY - 8, 'x = 512×7×7', 10, anchor='end', fill=COL['soft'])

# ── decoders, lmhead, sampling ────────────────────────────────────────────────
DX = BX + 70
rows = ((200, 'text_dec', 'THINK'), (CY, 'voc_dec', 'HEAR'), (480, 'img_dec', 'SEE'))
line([(BX, rows[0][0]), (BX, rows[2][0])], arrow=False)
HX = DX + 220
for y, nm, kind in rows:
    line([(BX, y), (DX, y)])
    text(DX + 80, y - 42, nm, 12, weight='bold')
    xx = DX
    for lab in ('3×3 7→5', '3×3 5→3', '3×3 3→1'):
        box(xx, y - 32, 34, 64, COL['dec'], [lab], size=10, vertical=True)
        if xx < DX + 120:
            line([(xx + 34, y), (xx + 60, y)])
        xx += 60
    line([(xx - 26, y), (HX, y)])
box(HX, 150, 44, 380, COL['frozen'], ['lmhead 256→50304 (frozen, shared)'], hatch=True, vertical=True)
SX = HX + 90
for y, nm, kind in rows:
    line([(HX + 44, y), (SX, y)])
    box(SX, y - 28, 104, 56, COL['smp'], ['softmax', f'sample · {kind}'])
# feedback: each stream's sample is its next input
for i, (y, nm, kind) in enumerate(rows):
    top = 114 - 13 * i                      # nested: THINK innermost, SEE outermost (no crossings)
    xr = SX + 104 + 18 + 16 * i
    xl = 34 - 7 * i
    line([(SX + 104, y), (xr, y), (xr, top), (xl, top), (xl, ys[i]), (40, ys[i])])
text(SX - 300, 82, 'each stream\'s sample → its next input (training: the dataset\'s)', 11, fill=COL['soft'])

# ── recall attention ──────────────────────────────────────────────────────────
AY = 585
EX = 1120                                 # the entry write, fed from the bus
box(EX, AY, 66, 52, COL['attn'], ['entry', '1×1 768→2'], size=11)
line([(BX, CY), (BX, AY + 26), (EX + 68, AY + 26)])
text(EX + 33, AY + 68, 'token grid + x', 9.5, fill=COL['soft'])
RX, RW = 850, 250                         # the ring
out.append(f'<rect x="{RX}" y="{AY}" width="{RW}" height="52" fill="#fff3e0" stroke="{COL["ink"]}" stroke-width="1.2"/>')
for k in range(1, 16):
    out.append(f'<line x1="{RX + k * RW / 16}" y1="{AY}" x2="{RX + k * RW / 16}" y2="{AY + 52}" stroke="#bdbdbd"/>')
text(RX + RW / 2, AY - 8, 'RING: last 1024 entries of 2×7×7 (fixed size)', 11, weight='bold')
text(RX + 18, AY + 66, 'oldest', 9.5, fill=COL['soft'])
text(RX + RW - 18, AY + 66, 'newest', 9.5, fill=COL['soft'])
line([(EX, AY + 26), (RX + RW + 2, AY + 26)])
box(630, AY - 6, 200, 64, COL['attn'], ['recall attention (MQA)', 'k = K·e (no age) · v = V·e + V′·e_next',
                                        '8 heads × 64 · q: token + newest'], size=11)
line([(RX, AY + 26), (832, AY + 26)])
box(578, AY + 9, 36, 34, COL['rep'], ['RMS'], size=10)
line([(630, AY + 26), (616, AY + 26)])
line([(578, AY + 26), (CX + CW + 2, AY + 26)])
text(596, AY - 2, 'recall grid', 10, fill=COL['soft'])


# ── Legendre memories and the copy ────────────────────────────────────────────
def lmu_group(y0, theta, secs, names):
    out.append(f'<rect x="640" y="{y0}" width="560" height="160" rx="6" fill="#fffde7" stroke="#9e9e9e" '
               f'stroke-dasharray="6,4"/>')
    text(656, y0 + 20, f'Legendre memory · order 2 · window {theta} ticks ({secs})', 12, anchor='start',
         weight='bold')
    text(656, y0 + 37, 'per channel m ← A·m + B·x · A 2×2, B 2×1 fixed · 2 × 512×7×7', 10.5,
         anchor='start', fill='#424242')
    fx, fys = 930, (y0 + 50, y0 + 104)
    cx, cy = 1120, y0 + 96
    out.append(f'<circle cx="{cx}" cy="{cy}" r="25" fill="{COL["lmu"]}" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(cx, cy - 2, 'A·m', 11, weight='bold')
    text(cx, cy + 12, '+ B·x', 10)
    line([(BX, cy), (cx + 27, cy)])
    line([(cx - 25, cy), (1030, cy)], arrow=False)
    reads = []
    for i, (nm, fy) in enumerate(zip(names, fys)):
        flop(fx, fy, nm, size='')
        line([(1030, cy), (1030, fy + 23), (fx + 66, fy + 23)])            # A·m + B·x -> D
        bx = 912 - 14 * i                                                   # Q -> the update
        line([(bx, fy + 16), (bx, y0 + 154), (cx, y0 + 154), (cx, cy + 27)], dash=True, color='#757575')
        reads.append((fx, fy + 16, bx))
    return reads


def cascade():
    """v502: DFF_1 an EMA of x over 512 ticks, DFF_2 the residual x - S_1 (S_1: DFF_1 as just written)."""
    y0 = 668
    out.append(f'<rect x="640" y="{y0}" width="560" height="236" rx="6" fill="#fffde7" stroke="#9e9e9e" '
               f'stroke-dasharray="6,4"/>')
    text(656, y0 + 20, 'residual cascade (Laplacian pyramid) · 2 × 512×7×7', 12, anchor='start', weight='bold')
    text(656, y0 + 88, 'DFF_1: r ← r + (x − r)/512', 11, anchor='start')
    text(656, y0 + 104, 'EMA, window 512 ticks (20.5 s)', 10.5, anchor='start', fill='#424242')
    text(656, y0 + 204, 'DFF_2: r ← x − S_1', 11, anchor='start')
    text(656, y0 + 220, 'residual copy (window 1)', 10.5, anchor='start', fill='#424242')
    fx = 930
    f1, f2 = y0 + 40, y0 + 156                     # the two flip-flops' tops
    c1y = f1 + 23                                  # EMA circle, on DFF_1's D line
    out.append(f'<circle cx="1120" cy="{c1y}" r="25" fill="{COL["lmu"]}" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(1120, c1y - 2, 'EMA', 11, weight='bold')
    text(1120, c1y + 12, '/512', 10)
    line([(BX, c1y), (1147, c1y)])
    line([(1095, c1y), (fx + 66, c1y)])            # S_1 -> DFF_1's D
    flop(fx, f1, 'DFF_1', size='')
    line([(912, f1 + 16), (912, f1 + 64), (1120, f1 + 64), (1120, c1y + 27)], dash=True, color='#757575')
    s2y = f2 + 23                                  # subtractor, on DFF_2's D line
    out.append(f'<circle cx="1120" cy="{s2y}" r="15" fill="#ffffff" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(1120, s2y + 6, '−', 18, weight='bold')
    line([(BX, s2y), (1137, s2y)])
    dot(1050, c1y)
    line([(1050, c1y), (1050, s2y - 40), (1120, s2y - 40), (1120, s2y - 17)])   # S_1 into the subtractor
    text(1056, s2y - 46, 'S_1', 10.5, anchor='start', fill=COL['soft'])
    line([(1105, s2y), (fx + 66, s2y)])
    flop(fx, f2, 'DFF_2', size='')
    line([(BX, AY + 26), (BX, s2y)], arrow=False)
    return [(fx, f1 + 16, 912), (fx, f2 + 16)]


reads = []
if CASC:
    reads += cascade()
if LMU:
    reads += lmu_group(668, 4096, '164 s', ('DFF_1', 'DFF_2'))
    reads += lmu_group(836, 64, '2.6 s', ('DFF_3', 'DFF_4'))
    flop(930, 1012, 'DFF_5', size='')
    text(1012, 1024, 'copy (window 1): r ← x', 11, anchor='start', weight='bold')
    line([(BX, 1035), (996, 1035)])
    reads.append((930, 1028))
    line([(BX, AY + 26), (BX, 1035)], arrow=False)
for k, (qx, qy, *bx) in enumerate(reads):                 # Q -> norm -> concat
    nx = 590
    line([(qx, qy), (nx + 36, qy)])
    if bx:
        dot(bx[0], qy)
    box(nx, qy - 13, 36, 26, COL['rep'] if CASC else COL['norm'], ['RMS' if CASC else 'norm'], size=9.5)
    line([(nx, qy), (CX + CW + 2, qy)])

# ── legend (lower left) ───────────────────────────────────────────────────────
LY = 560
out.append(f'<rect x="30" y="{LY}" width="440" height="{490 if LMU else 504 if CASC else 386}" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
text(48, LY + 26, 'Legend', 14, anchor='start', weight='bold')
items = [(COL['frozen'], True, 'frozen: embedding / lmhead (pythia-31m), ResNet-50'),
         (COL['rep'], False, 'RMS norm (per sample, per position) · replicate' if CASC else
          'RMS norm · replicate 1×1 → 7×7'),
         (COL['cat'], False, 'channel concatenation'),
         (COL['lin'], False, 'conv 1×1 / 3×3 (linear): ctx_cat, linout'),
         (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
         (COL['dec'], False, 'decoder convs 7→5→3→1 (linear)'),
         (COL['smp'], False, 'softmax + sample (+ <NUL> logit)'),
         (COL['attn'], False, 'recall attention: entry write, MQA read'),
         ('#fff3e0', False, 'ring of W = 1024 entries (fixed-size state)' if LMU else
          'ring of W = 1024 entries (fixed size), emptied per example' if CASC else
          'ring of W = 1024 entries: the whole state, emptied per example')]
if CASC:
    items += [(COL['lmu'], False, 'EMA r ← r + (x − r)/W, W = 512 ticks'),
              ('#ffffff', False, '(−) subtractor: x minus the EMA as just written')]
if LMU:
    items += [(COL['lmu'], False, 'Legendre update m ← A·m + B·x (fixed A, B)'),
              (COL['norm'], False, 'read scale 1/σ_k (running RMS)')]
items += [(COL['mel'], False, 'fixed DSP: log-mel'),
          ('#ffffff', False, 'media input: video frame (2 Hz), sound (16 kHz)')]
for i, (c, h, s) in enumerate(items):
    y = LY + 48 + 28 * i
    box(48, y, 26, 18, c, hatch=h, rx=2)
    text(86, y + 13, s, 12, anchor='start')
y = LY + 48 + 28 * len(items)
if REGS:
    flop(48, y + 2, '', size='')
    text(124, y + 22, 'D flip-flop register, clocked every tick', 12, anchor='start')
    text(124, y + 38, '(never reset: --continuous)' if LMU else '(reset to 0 at each example)', 11,
         anchor='start', fill=COL['soft'])
    y += 64
else:
    y += 4
line([(48, y), (80, y)])
text(86, y + 4, 'data / state path', 12, anchor='start')
if REGS:
    line([(250, y), (282, y)], dash=True, color='#757575')
    text(288, y + 4, 'old state into the update', 12, anchor='start')

out.append('</svg>')
open(a.out or f'docs/figures/vla_{NAME}.svg', 'w').write('\n'.join(out))
