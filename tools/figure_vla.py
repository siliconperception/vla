"""Draw docs/figures/vla_<model>.svg: one clock tick of a VLA model, 16:9 (1920 x 1080).

usage: python tools/figure_vla.py [--model v498|v499|v502|v505] [--out OUT]

v498: recurrent CNN + two order-2 Legendre memories (4096, 64 ticks) + copy + recall attention, never
reset. v499: no registers, the recall attention's ring is the whole state, reset at each example.
v502: the residual cascade of an EMA (512 ticks) and the residual copy, read through per-sample RMSnorm,
+ recall attention, reset at each example. v505: two recurrent layers in series, each with that cascade, no
recall attention; 1920 x 2160, two 16:9 panes: the whole tick on top, one layer zoomed in below."""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--model', default='v498', choices=('v498', 'v499', 'v502', 'v505'))
ap.add_argument('--out', default=None)
a = ap.parse_args()
LMU = a.model == 'v498'                   # Legendre memories + copy
CASC = a.model == 'v502'                  # EMA + residual copy, RMSnorm reads
REGS = LMU or CASC                        # (v499: the ring alone)
CAT = {'v498': ('3×256 + 2048 + 256 + 256 + 5×512', 5888), 'v499': ('3×256 + 2048 + 256 + 256', 3328),
       'v502': ('3×256 + 2048 + 256 + 256 + 2×512', 4352), 'v505': ('', 0)}[a.model]

W, H = 1920, 1080
out = []
COL = dict(frozen='#e0e0e0', rep='#ce93d8', cat='#90a4ae', lin='#64b5f6', cnn='#81c784', dec='#4dd0e1',
           media='#ffffff', smp='#f48fb1', lmu='#fff176', norm='#bcaaa4', attn='#ffb74d', mel='#fff9c4',
           ink='#212121', soft='#616161')


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


def layer_block(x0, y0, name, cat, ins, cy):
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
    text(f1 + 32, ry + 62, 'EMA 512', 10, fill=COL['soft'])
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
    text(30, 38, 'VLA v505 — one clock tick (40 ms): two recurrent CNN layers in series', 22, anchor='start',
         weight='bold')
    text(30, 62, 'A · the whole tick.  n_hidden 512 · c_context 384 · 7×7 grid · depth 8 per layer · 3 token '
         'streams · 25 Hz · each layer: EMA 512 + copy, RMSnorm reads · reset at each example · 33.2M trainable · '
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
    o1 = layer_block(520, 250, 'LAYER 1', '3×256 + 256 + 2×512 = 2048', list(ys) + [500], CY)
    BX = o1[0] + 40                                       # the o_1 tap
    line([o1, (BX, CY)], arrow=False)
    dot(BX, CY)
    text(BX - 4, CY - 10, 'o₁', 13, anchor='end', weight='bold')
    L2 = 1000
    line([(BX, CY), (L2, CY)], arrow=False)
    o2 = layer_block(L2, 250, 'LAYER 2', '512 + 2×512 = 1536', [CY], CY)
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
                           'Layer 2 started as the identity (linout zero-initialized): v505 began exactly as',
                           'the one-layer v504 at step 1,127,936.')):
        text(560, 820 + 20 * i + (10 if i > 1 else 0), s, 12.5, anchor='start', fill='#424242')

    out.append('<line x1="0" y1="1080" x2="1920" y2="1080" stroke="#9e9e9e" stroke-width="2"/>')

    # ── pane B: one layer ──────────────────────────────────────────────────
    out.append('<g transform="translate(0,1080)">')
    text(30, 46, 'B · one recurrent layer (layers 1 and 2 have the same structure; only their inputs differ)', 22,
         anchor='start', weight='bold')
    text(30, 70, 'its own weights · its own two registers (an EMA over 512 ticks, then the residual copy) · old '
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
    text(816, y0 + 92, 'DFF_1: r ← r + (x − r)/512', 12, anchor='start')
    text(816, y0 + 110, 'EMA, window 512 ticks (20.5 s)', 11, anchor='start', fill='#424242')
    text(816, y0 + 218, 'DFF_2: r ← x − S_1', 12, anchor='start')
    text(816, y0 + 236, 'residual copy (window 1)', 11, anchor='start', fill='#424242')
    f1, f2 = y0 + 44, y0 + 172
    c1y, s2y = f1 + 23, f2 + 23
    out.append(f'<circle cx="{ex}" cy="{c1y}" r="26" fill="{COL["lmu"]}" stroke="{COL["ink"]}" stroke-width="1.2"/>')
    text(ex, c1y - 2, 'EMA', 11, weight='bold')
    text(ex, c1y + 12, '/512', 10)
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
                     (COL['lmu'], False, 'EMA r ← r + (x − r)/W, W = 512 ticks'),
                     ('#ffffff', False, '(−) subtractor: x minus the EMA as just written')],
           '(reset to 0 at each example)', w=470)
    out.append('</g>')
    out.append('</svg>')
    open(a.out or f'docs/figures/vla_{a.model}.svg', 'w').write('\n'.join(out))


if a.model == 'v505':
    draw_v505()
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
open(a.out or f'docs/figures/vla_{a.model}.svg', 'w').write('\n'.join(out))
