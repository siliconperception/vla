"""Draw docs/figures/vla_v498.svg: one clock tick of the v498 model, 16:9 (1920 x 1080).

usage: python tools/figure_v498.py [OUT]"""
import sys

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


# ── canvas ────────────────────────────────────────────────────────────────────
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica, Arial, sans-serif">')
out.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M 0,0 L 10,5 L 0,10 z" fill="#212121"/></marker>'
           '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           '<line x1="0" y1="0" x2="0" y2="6" stroke="#757575" stroke-width="1.2"/></pattern></defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(30, 38, 'VLA v498 — one clock tick (40 ms): recurrent CNN + Legendre memories + recall attention', 22,
     anchor='start', weight='bold')
text(30, 62, 'n_hidden 512 · c_context 384 · 7×7 grid · depth 8 · 3 token streams · 25 Hz · state never reset '
     '(continuous) · 21.3M trainable · state 125,440 register + 100,352 ring values · image / audio encoders: future', 13,
     anchor='start', fill='#424242')

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
box(CX, 150, CW, 900, COL['cat'], ['concat  3×256 + 2048 + 256 + 256 + 5×512 = 5888'], size=12, vertical=True)
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
box(580, 220, 40, 240, COL['lin'], ['ctx_cat 1×1 5888→384'], vertical=True)
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
    top = 88 + 12 * i
    xr = SX + 104 + 22 + 14 * (2 - i)
    line([(SX + 104, y), (xr, y), (xr, top), (22 + 4 * i, top), (22 + 4 * i, ys[i]), (40, ys[i])])
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
    for nm, fy in zip(names, fys):
        flop(fx, fy, nm, size='')
        line([(1030, cy), (1030, fy + 23), (fx + 66, fy + 23)])            # A·m + B·x -> D
        line([(fx, fy + 30), (900, fy + 30), (900, y0 + 154), (cx, y0 + 154), (cx, cy + 27)],
             dash=True, color='#757575')                                    # Q -> the update
        reads.append((fx, fy + 16))
    return reads


reads = []
reads += lmu_group(668, 4096, '164 s', ('DFF_1', 'DFF_2'))
reads += lmu_group(836, 64, '2.6 s', ('DFF_3', 'DFF_4'))
flop(930, 1012, 'DFF_5', size='')
text(1012, 1024, 'copy (window 1): r ← x', 11, anchor='start', weight='bold')
line([(BX, 1035), (996, 1035)])
reads.append((930, 1028))
line([(BX, AY + 26), (BX, 1035)], arrow=False)
for k, (qx, qy) in enumerate(reads):                      # Q -> norm -> concat
    nx = 590
    line([(qx, qy), (nx + 36, qy)])
    box(nx, qy - 13, 36, 26, COL['norm'], ['norm'], size=9.5)
    line([(nx, qy), (CX + CW + 2, qy)])

# ── legend (lower left) ───────────────────────────────────────────────────────
LY = 560
out.append(f'<rect x="30" y="{LY}" width="440" height="490" rx="8" fill="#fafafa" stroke="#bdbdbd"/>')
text(48, LY + 26, 'Legend', 14, anchor='start', weight='bold')
items = [(COL['frozen'], True, 'frozen: embedding / lmhead (pythia-31m), ResNet-50'),
         (COL['rep'], False, 'RMS norm · replicate 1×1 → 7×7'),
         (COL['cat'], False, 'channel concatenation'),
         (COL['lin'], False, 'conv 1×1 / 3×3 (linear): ctx_cat, linout'),
         (COL['cnn'], False, 'conv 3×3 + BatchNorm + ReLU'),
         (COL['dec'], False, 'decoder convs 7→5→3→1 (linear)'),
         (COL['smp'], False, 'softmax + sample (+ <NUL> logit)'),
         (COL['attn'], False, 'recall attention: entry write, MQA read'),
         ('#fff3e0', False, 'ring of W = 1024 entries (fixed-size state)'),
         (COL['lmu'], False, 'Legendre update m ← A·m + B·x (fixed A, B)'),
         (COL['norm'], False, 'read scale 1/σ_k (running RMS)'),
         (COL['mel'], False, 'fixed DSP: log-mel'),
         ('#ffffff', False, 'media input: video frame (2 Hz), sound (16 kHz)')]
for i, (c, h, s) in enumerate(items):
    y = LY + 48 + 28 * i
    box(48, y, 26, 18, c, hatch=h, rx=2)
    text(86, y + 13, s, 12, anchor='start')
y = LY + 48 + 28 * len(items)
flop(48, y + 2, '', size='')
text(124, y + 22, 'D flip-flop register, clocked every tick', 12, anchor='start')
text(124, y + 38, '(never reset: --continuous)', 11, anchor='start', fill=COL['soft'])
line([(48, y + 64), (80, y + 64)])
text(86, y + 68, 'data / state path', 12, anchor='start')
line([(250, y + 64), (282, y + 64)], dash=True, color='#757575')
text(288, y + 68, 'old state into the update', 12, anchor='start')

out.append('</svg>')
open(sys.argv[1] if len(sys.argv) > 1 else 'docs/figures/vla_v498.svg', 'w').write('\n'.join(out))
