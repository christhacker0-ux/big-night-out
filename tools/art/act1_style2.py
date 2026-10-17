#!/usr/bin/env python3
"""
Big Night Out -- Act 1 (Freshman) repainted in "style 2" (see Docs/ART_STYLE.md).

Paints every Act 1 background, character and prop sprite with tools/art/style2.py:
perspective rooms with grungy, lived-in surfaces, magenta / teal palette, warm lamp light, dark
out-of-focus foreground framing, and tall (6.5-head) characters.

This supersedes the Act 1 painters in paint.py and act1_more.py (those still run, but this script is
the source of truth for these files). Item icons are unchanged and still come from those scripts.

Usage:  python3 tools/art/act1_style2.py              # paint everything (~7 min; each background ~50 s)
        python3 tools/art/act1_style2.py dex lounge   # paint assets whose name contains these words
        python3 tools/art/act1_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into act1.json
        BNO_COMPOSITES=/some/dir python3 tools/art/act1_style2.py --composite [room ids]
                                                      # check images: room + sprites + Dex + hotspot boxes
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style2 import *  # noqa: F401,F403,E402
import style2  # noqa: E402

# Character heights (crown, px) at depth scale 1.0. NPC sprites are not depth-scaled by the game,
# so each is painted at the size it has at its feet position (see ART_STYLE.md).
DEX_H = 440


# =========================================================================== shared character bits
def hibiscus2(c, x, y, r, col, center=(255, 236, 90), clip=None, rot=0):
    for k in range(5):
        a = math.radians(k * 72 + rot)
        c.ink(ell(x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a), r * 0.55, r * 0.42, k * 72 + rot), col,
              lw=1.2, oc=dk(col, 0.45), shade=0.3, sw=r * 0.3, hi=0.3, ao=0, tex=0, wob=0.2, clip=clip)
    c.ink(ell(x, y, r * 0.22, r * 0.22), center, lw=0.8, oc=dk(col, 0.45), shade=0, hi=0, ao=0, tex=0, wob=0, clip=clip)


def leaf2(c, x, y, L, ang, col, clip=None):
    c.ink(ell(x, y, L, L * 0.36, ang), col, lw=1.0, oc=dk(col, 0.5), shade=0.3, sw=L * 0.3, hi=0.2, ao=0, tex=0, wob=0.2,
          clip=clip)


def folds(c, lines, col, w=1.8, opacity=0.7):
    for pts in lines:
        c.stroke(pts, w, col, taper=(0.3, 0.6), opacity=opacity, smooth=1)


def spiky_hair(b, n=9, length=1.5, sweep=-0.45, seed=0, a0=150, a1=335, hairline=None):
    """Spiky hair around the top / back of a 3/4 right-facing head (canvas px Sh).
    sweep < 0 sweeps the spikes backward (to the left)."""
    hx, hy, r, ry = b.hx, b.hy, b.r, b.ry
    rng = random.Random(seed)
    pts = []
    angs = np.linspace(a0, a1, n * 2 + 1)
    for i, a in enumerate(angs):
        ar = math.radians(a)
        if i % 2 == 0:
            pts.append((hx + math.cos(ar) * r * 1.02, hy + math.sin(ar) * ry * 0.98))
        else:
            rr = length * rng.uniform(0.86, 1.12)
            k = math.sin((a - a0) / (a1 - a0) * math.pi) * 0.7 + 0.3
            ar2 = ar + sweep * k
            pts.append((hx + math.cos(ar2) * r * rr, hy + math.sin(ar2) * ry * rr * 0.92))
    pts += hairline or [(hx + 0.86 * r, hy - 0.52 * ry), (hx + 0.55 * r, hy - 0.42 * ry), (hx + 0.3 * r, hy - 0.5 * ry),
                        (hx + 0.02 * r, hy - 0.3 * ry), (hx - 0.12 * r, hy + 0.05 * ry), (hx - 0.22 * r, hy + 0.3 * ry),
                        (hx - 0.6 * r, hy + 0.1 * ry), (hx - 0.86 * r, hy + 0.42 * ry)]
    return Sh([pts])


# =========================================================================== Dex Dooley (player)
SKIN_DEX = (255, 206, 168)
DEX_SHIRT = (28, 196, 200)


def paint_player_dex(height=DEX_H, name="player_dex.png", flip=False):
    W, Hc = 340, 580
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=214)
    b = Body(c, 150, Hc - 14, height, skin=SKIN_DEX,
             build=dict(shoulders=0.9, waist=0.86, hips=0.88, limbs=0.9, head=1.08, legs=1.03, neck=1.2),
             pose=dict(arm_n=2, fore_n=12, arm_f=10, fore_f=16, leg_n=-5, shin_n=5, leg_f=6, shin_f=-5, lean=5,
                       head_dx=0.6), seed=3)
    khaki, khaki_sh = (224, 192, 132), (168, 124, 104)
    hair, hair_sh = (246, 122, 36), (186, 62, 44)
    shirt = DEX_SHIRT
    prt = random.Random(9)

    def shirt_print(cl, step=36):
        bx0, by0, bx1, by1 = cl.bbox()
        cols = [(255, 84, 140), (255, 214, 60), (255, 128, 64), (252, 250, 240)]
        y = by0 + 4
        row = 0
        while y < by1 + 12:
            x = bx0 - 8 + (row % 2) * step / 2
            while x < bx1 + 12:
                xx, yy = x + prt.uniform(-5, 5), y + prt.uniform(-4, 4)
                rr = prt.uniform(7, 10)
                leaf2(c, xx + rr * 0.95, yy + rr * 0.5, rr * 0.95, 28, (40, 150, 84), clip=cl)
                leaf2(c, xx - rr * 0.75, yy + rr * 0.85, rr * 0.8, -40, (26, 118, 84), clip=cl)
                hibiscus2(c, xx, yy, rr, prt.choice(cols), clip=cl, rot=prt.uniform(0, 70))
                x += step
            y += step * 0.82
            row += 1

    def shirt_shade(sh, dx=10, dy=8, o=0.32):
        c.soft(Sh([[(x + dx, y + dy) for x, y in sh.polys[0]]]), (255, 255, 230), 0.0, 0)
        inv = Sh([[(x - dx, y - dy) for x, y in sh.polys[0]]])
        # darken where the shape shifted toward the light does not cover (shadow side)
        c.soft(sh, (36, 18, 96), o, 5, clip=sh) if False else None
        c.ink(sh, (36, 18, 96), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.0)

    # --- far arm (behind): bent, hand fidgeting at the belly
    c.ink(b.arm_shape(False), shade_col(SKIN_DEX, 0.9), lw=2.8, shade=0.5)
    b.hand(False, "relaxed", col=shade_col(SKIN_DEX, 0.92), thumb=-1)
    sl = b.sleeve(False, 0.55, 7.6, 7.2)
    c.ink(sl, dk(shirt, 0.82), lw=2.8, shade=0.4)
    shirt_print(sl)
    c.ink(sl, (20, 10, 70), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.25)
    c.ink(sl, (0, 0, 0, 0), lw=2.8, line_only=True)

    # --- legs (khakis), knees a little knocked
    for near in (False, True):
        col = khaki if near else mix(khaki, (150, 110, 130), 0.25)
        sh = b.leg_shape(near, w=(8.8, 6.0, 5.6))
        c.ink(sh, col, lw=3.0, shade=0.5, scol=khaki_sh, hi=0.35, rim=0.15)
        kn = b.knee_n if near else b.knee_f
        an = b.ankle_n if near else b.ankle_f
        folds(c, [b.Ps([(kn[0] - 1.8, kn[1] + 2.5), (kn[0] + 1.0, kn[1] + 0.2), (kn[0] - 0.4, kn[1] - 2.2)]),
                  b.Ps([(an[0] - 2.0, an[1] + 7), (an[0] + 1.6, an[1] + 6)]),
                  b.Ps([(b.hip_n[0] + 3, b.hip_y - 4), (b.hip_n[0] + 5, b.hip_y - 9)])], khaki_sh, 1.6, 0.7)
        b.shoe(near, (248, 246, 240), (236, 70, 64), "sneaker")
        x, y = an
        c.stroke(b.Ps([(x + 0.5, y - 0.6), (x + 4.5, y - 0.2), (x + 8.5, y - 1.8)]), 2.4, (230, 60, 64), taper=(0.2, 0.5))
        for k in range(3):
            c.stroke(b.Ps([(x + 1.6 + k * 1.5, y + 2.0 - k * 0.55), (x + 2.8 + k * 1.5, y + 0.9 - k * 0.55)]), 1.5, INK,
                     taper=(0, 0))
        c.ink(Sh([b.Ps([(an[0] - 3.3, an[1] + 5.0), (an[0] + 3.2, an[1] + 5.4), (an[0] + 3.4, an[1] + 2.2),
                        (an[0] - 3.4, an[1] + 1.6)])]), col, lw=2.6, shade=0.4, scol=khaki_sh)

    # --- neck
    c.ink(b.neck_shape(), SKIN_DEX, lw=2.8, shade=0.6, sw=8, scol=shade_col(SKIN_DEX, 0.7))
    nb = b.P(*b.neck_base)
    c.stroke([(nb[0] + b.u * 2.3, nb[1] - b.u * 3.4), (nb[0] + b.u * 2.7, nb[1] - b.u * 2.4)], 1.8,
             dk(SKIN_DEX, 0.7), taper=(0.2, 0.2))

    # --- torso: loud hibiscus shirt, untucked
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y - 3.5, flare=0.8, neck_open=1.2)])
    c.ink(torso, shirt, lw=0, shade=0, hi=0, ao=0)
    shirt_print(torso)
    bx0, by0, bx1, by1 = torso.bbox()
    # soft cel shadow (back + under the chest), warm light down the front
    c.soft(Sh([[(bx0 - 20, by0), (bx0 + (bx1 - bx0) * 0.36, by0), (bx0 + (bx1 - bx0) * 0.3, by1), (bx0 - 20, by1)]]),
           (36, 18, 100), 0.36, 7, clip=torso)
    c.soft(Sh([[(bx0, by1 - 26), (bx1, by1 - 30), (bx1, by1 + 10), (bx0, by1 + 10)]]), (36, 18, 100), 0.25, 8, clip=torso)
    c.soft(Sh([[(bx1 - 22, by0 + 20), (bx1 + 10, by0 + 20), (bx1 + 10, by1 - 30), (bx1 - 14, by1 - 30)]]),
           (255, 250, 220), 0.25, 6, clip=torso)
    c.ink(torso, (0, 0, 0, 0), lw=3.0, line_only=True)
    sy, sx = b.shoulder_y, b.lean_dx
    # open collar: skin V, two pointy collar flaps
    c.ink(Sh([b.Ps([(sx - 1.4, sy + 1.4), (sx + 3.2, sy + 1.0), (sx + 1.6, sy - 6.0)])]), SKIN_DEX, lw=2.2, shade=0.5,
          sw=6, scol=shade_col(SKIN_DEX, 0.7))
    for pts in ([(sx - 3.0, sy + 2.0), (sx + 0.4, sy - 0.6), (sx + 1.7, sy - 6.2), (sx - 1.2, sy - 4.2), (sx - 4.2, sy - 1.6)],
                [(sx + 2.4, sy + 1.2), (sx + 6.4, sy + 0.4), (sx + 6.0, sy - 3.2), (sx + 1.7, sy - 6.4)]):
        sh = Sh([b.Ps(pts)])
        c.ink(sh, shirt, lw=2.2, shade=0.0, hi=0)
        shirt_print(sh, 26)
        c.ink(sh, (255, 255, 240), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.12)
        c.ink(sh, (0, 0, 0, 0), lw=2.2, line_only=True)
    c.stroke(b.Ps([(sx + 1.7, sy - 6.4), (sx * 0.55 + 2.4, b.hip_y + 6), (2.6, b.hip_y - 3.4)]), 1.7, dk(shirt, 0.45),
             taper=(0.1, 0.1))
    for k, yy in enumerate((sy - 11, sy - 18, sy - 25)):
        f = (sy - yy) / (sy - b.hip_y)
        c.ink(ell(*b.P(sx * (1 - f) + 2.5 + f * 0.5 + 0.9, yy), 2.0, 2.0), (250, 246, 230), lw=1.2, shade=0.2, hi=0, ao=0,
              tex=0)
    folds(c, [b.Ps([(-2.5, b.hip_y + 8), (0.0, b.hip_y + 3), (-0.5, b.hip_y - 1.5)]),
              b.Ps([(4.0, b.hip_y + 9), (4.6, b.hip_y + 3.5)]),
              b.Ps([(b.sh_f[0] - 1, sy - 6), (b.sh_f[0] - 3.2, sy - 11)])], dk(shirt, 0.42), 1.7, 0.55)

    # --- head
    head = Sh([b.head_pts(jaw=1.05, chin=1.12, chin_drop=1.04)])
    c.ink(head, SKIN_DEX, lw=3.0, shade=0.5, sw=b.r * 0.45, scol=shade_col(SKIN_DEX, 0.72), hi=0.35, rim=0.18,
          rcol=(255, 170, 160))
    fa = b.face_anchor()
    r, ry = b.r, b.ry
    ex, ey = fa["eye_n"]
    b.cheeks(ex + r * 0.12, ey + ry * 0.42, r * 0.3, opacity=0.4)
    rng = random.Random(4)
    for _ in range(9):
        c.ink(ell(ex + rng.uniform(-r * 0.25, r * 0.8), ey + ry * rng.uniform(0.3, 0.48), 1.15, 1.15),
              (200, 112, 72), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
    b.eyes(iris=(70, 150, 90), look=(0.32, 0.05), lid=0.06, size=1.05)
    b.brows(col=hair_sh, lift_n=0.06, lift_f=0.04, tilt_n=0.9, tilt_f=0.6, w=r * 0.13)
    b.nose("long", 1.05)
    b.mouth("teeth", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.02, r * 0.6, r * 0.34)
    # sweat drop
    tx, ty = fa["top"]
    c.ink(blob([(tx + r * 1.25, ty + ry * 0.3), (tx + r * 1.38, ty + ry * 0.52), (tx + r * 1.34, ty + ry * 0.62),
                (tx + r * 1.18, ty + ry * 0.62), (tx + r * 1.14, ty + ry * 0.52)], 2), (170, 225, 255), lw=1.8, shade=0.3,
          hi=0.6, hw=2)
    # spiky orange hair
    hsh = spiky_hair(b, n=8, length=1.55, sweep=-0.42, seed=5)
    c.ink(hsh, hair, lw=3.0, shade=0.55, sw=r * 0.5, scol=hair_sh, hi=0.5, hw=r * 0.25, hcol=(255, 200, 112), rim=0.2,
          rcol=(255, 160, 120))
    hx, hy = b.hx, b.hy
    for k in range(6):
        a = math.radians(190 + k * 27)
        c.stroke([(hx + math.cos(a) * r * 0.55, hy + math.sin(a) * ry * 0.55),
                  (hx + math.cos(a - 0.35) * r * 1.15, hy + math.sin(a - 0.35) * ry * 1.1)], 1.7, hair_sh,
                 taper=(0.3, 0.7), opacity=0.75)
    b.ear(1.1, jug=1.0)

    # --- near arm: hanging, sleeve over the upper arm
    c.ink(b.arm_shape(True), SKIN_DEX, lw=3.0, shade=0.5, scol=shade_col(SKIN_DEX, 0.72), rim=0.15, rcol=(255, 170, 160))
    b.hand(True, "relaxed")
    sl = b.sleeve(True, 0.58, 8.0, 7.6)
    c.ink(sl, shirt, lw=0, shade=0.0, hi=0)
    shirt_print(sl)
    bx0, by0, bx1, by1 = sl.bbox()
    c.soft(Sh([[(bx0 - 10, by0), (bx0 + (bx1 - bx0) * 0.4, by0), (bx0 + (bx1 - bx0) * 0.4, by1), (bx0 - 10, by1)]]),
           (36, 18, 100), 0.3, 5, clip=sl)
    c.ink(sl, (0, 0, 0, 0), lw=3.0, line_only=True)
    folds(c, [[(bx0 + 6, by1 - 4), (bx0 + 14, by1 - 12)]], dk(shirt, 0.42), 1.5, 0.6)
    return finish_sprite(c, name, flip=flip)


# =========================================================================== outfit helpers
def legs(b, col, w=(8.6, 5.8, 5.2), scol=None, far_k=0.86, shoe=None, cuffs=None, folds_col=None, skin=False):
    """Both legs (far first). shoe(b, near) draws a shoe after each leg; cuffs = cuff colour."""
    c = b.c
    for near in (False, True):
        cc = col if near else mix(col, shade_col(col, 0.7), 1 - far_k)
        sh = b.leg_shape(near, w=w)
        c.ink(sh, cc, lw=c.lw, shade=0.5, scol=scol, hi=0.35, rim=0.12)
        kn = b.knee_n if near else b.knee_f
        an = b.ankle_n if near else b.ankle_f
        fc = folds_col or shade_col(col, 0.62)
        if not skin:
            folds(c, [b.Ps([(kn[0] - 1.8, kn[1] + 2.5), (kn[0] + 1.0, kn[1] + 0.2), (kn[0] - 0.4, kn[1] - 2.2)]),
                      b.Ps([(an[0] - 2.0, an[1] + 7), (an[0] + 1.6, an[1] + 6)])], fc, 1.6, 0.7)
        else:
            c.stroke(b.Ps([(kn[0] + 0.8, kn[1] + 1.0), (kn[0] + 1.6, kn[1] - 0.8)]), 1.4, shade_col(col, 0.6), taper=(0.3, 0.3))
        if shoe:
            shoe(b, near)
        if cuffs:
            c.ink(Sh([b.Ps([(an[0] - 3.3, an[1] + 5.0), (an[0] + 3.2, an[1] + 5.4), (an[0] + 3.4, an[1] + 2.2),
                            (an[0] - 3.4, an[1] + 1.6)])]), cuffs if near else mix(cuffs, shade_col(cuffs, 0.7), 1 - far_k),
                  lw=2.6, shade=0.4)


def soft_shade(c, sh, side="back", o=0.32, col=(36, 18, 100), frac=0.36, hi=0.22):
    """Soft cel shadow over a printed / patterned shape: the back third darker, a warm sheen on the front."""
    bx0, by0, bx1, by1 = sh.bbox()
    w = bx1 - bx0
    c.soft(Sh([[(bx0 - 30, by0 - 10), (bx0 + w * frac, by0 - 10), (bx0 + w * frac * 0.85, by1 + 10), (bx0 - 30, by1 + 10)]]),
           col, o, 7, clip=sh)
    c.soft(Sh([[(bx0, by1 - (by1 - by0) * 0.16), (bx1, by1 - (by1 - by0) * 0.2), (bx1, by1 + 10), (bx0, by1 + 10)]]), col,
           o * 0.7, 8, clip=sh)
    if hi:
        c.soft(Sh([[(bx1 - w * 0.2, by0 + 10), (bx1 + 10, by0 + 10), (bx1 + 10, by1 - 20), (bx1 - w * 0.12, by1 - 20)]]),
               (255, 250, 220), hi, 6, clip=sh)


def glasses(b, col=(200, 40, 60), round_=True, size=1.0, lw=None, tint=None):
    c = b.c
    fa = b.face_anchor()
    r = b.r * size
    lw = lw or max(2.4, b.r * 0.1)
    (ex, ey), (fx, fy) = fa["eye_n"], fa["eye_f"]
    if tint:
        c.ink(ell(ex, ey, r * 0.42, r * 0.42) if round_ else rrect(ex - r * 0.44, ey - r * 0.32, ex + r * 0.44, ey + r * 0.32, 6),
              tint, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
        c.ink(ell(fx, fy, r * 0.27, r * 0.4) if round_ else rrect(fx - r * 0.28, fy - r * 0.3, fx + r * 0.28, fy + r * 0.3, 5),
              tint, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
    for (x, y, rx, ry) in ((ex, ey, r * 0.42, r * 0.42), (fx, fy, r * 0.22, r * 0.4)):
        sh = ell(x, y, rx, ry) if round_ else rrect(x - rx, y - ry * 0.75, x + rx, y + ry * 0.75, 6)
        c.ink(sh, (0, 0, 0, 0), lw=lw, oc=col, line_only=True, wob=0.2, inner=0.5)
        c.ink(sh, (0, 0, 0, 0), lw=1.0, oc=INK, line_only=True, wob=0.2, inner=-0.9)
        c.stroke([(x - rx * 0.45, y + ry * 0.35), (x - rx * 0.05, y - ry * 0.4)], max(1.6, r * 0.06), (255, 255, 255),
                 opacity=0.55)
    c.stroke([(ex + r * 0.42, ey - r * 0.06), (fx - r * 0.22, fy - r * 0.08)], lw * 0.8, col)
    c.stroke([(ex - r * 0.44, ey - r * 0.04), (fa["ear"][0] + r * 0.05, fa["ear"][1] - r * 0.12)], lw * 0.8, col)


def cowboy_hat2(c, cx, cy, w, col=(150, 86, 46), tilt=-8, band=(70, 40, 26)):
    """3/4 cowboy hat; (cx, cy) = centre of the brim, w = brim width."""
    brim = Sh([rot_pts(chaikin([(cx - w * 0.5, cy + w * 0.02), (cx - w * 0.4, cy - w * 0.1), (cx, cy - w * 0.14),
                                (cx + w * 0.42, cy - w * 0.09), (cx + w * 0.56, cy - w * 0.04), (cx + w * 0.4, cy + w * 0.12),
                                (cx, cy + w * 0.16), (cx - w * 0.38, cy + w * 0.12)], 2), tilt, cx, cy)])
    crown = Sh([rot_pts(chaikin([(cx - w * 0.28, cy), (cx - w * 0.3, cy - w * 0.22), (cx - w * 0.22, cy - w * 0.36),
                                 (cx - w * 0.05, cy - w * 0.32), (cx + w * 0.04, cy - w * 0.38), (cx + w * 0.2, cy - w * 0.36),
                                 (cx + w * 0.3, cy - w * 0.22), (cx + w * 0.3, cy)], 2), tilt, cx, cy)])
    c.ink(brim, col, lw=3.0, shade=0.5, sw=w * 0.06, hi=0.4, hw=w * 0.03, rim=0.15)
    c.ink(crown, col, lw=3.0, shade=0.55, sw=w * 0.12, hi=0.45, hw=w * 0.06, rim=0.15)
    c.ink(Sh([rot_pts([(cx - w * 0.29, cy - w * 0.02), (cx + w * 0.3, cy - w * 0.02), (cx + w * 0.3, cy - w * 0.09),
                       (cx - w * 0.29, cy - w * 0.09)], tilt, cx, cy)]), band, lw=2.2, shade=0.2, clip=crown)
    c.stroke(rot_pts([(cx - w * 0.05, cy - w * 0.3), (cx + w * 0.02, cy - w * 0.2)], tilt, cx, cy), 1.8, shade_col(col, 0.5))
    bx, by = rot_pts([(cx + w * 0.12, cy - w * 0.055)], tilt, cx, cy)[0]
    c.ink(ell(bx, by, w * 0.035, w * 0.03), (240, 200, 90), lw=1.6)


def hair_strands(c, pts_list, col, w=1.8, o=0.7):
    for pts in pts_list:
        c.stroke(pts, w, col, taper=(0.3, 0.7), opacity=o, smooth=2)


# =========================================================================== Lacey Rae
def paint_lacey_rae(height=410, name="hs_lacey_rae.png"):
    W, Hc = 360, 600
    skin = (238, 178, 136)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=31)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.84, waist=0.74, hips=1.04, limbs=0.86, head=1.06, legs=1.04, neck=1.0, chest=1.4,
                        hand=0.92, foot=0.95),
             pose=dict(arm_n=-10, fore_n=34, arm_f=34, fore_f=-118, leg_n=-6, shin_n=2, leg_f=10, shin_f=-4, lean=-2,
                       head_dx=-0.2), seed=4)
    hair, hair_sh, hair_hi = (252, 204, 96), (206, 136, 52), (255, 236, 170)
    denim, denim_sh = (70, 112, 196), (40, 62, 140)
    pink = (255, 108, 168)
    boot = (140, 76, 42)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # long hair, back layer
    back_hair = blob([(hx - r * 0.9, hy - ry * 0.4), (hx + r * 0.3, hy - ry * 0.9), (hx + r * 0.6, hy - ry * 0.6),
                      (hx - r * 0.3, hy + ry * 0.5), (hx - r * 0.2, hy + ry * 1.6), (hx - r * 0.6, hy + ry * 2.6),
                      (hx - r * 1.3, hy + ry * 2.9), (hx - r * 1.5, hy + ry * 2.0), (hx - r * 1.35, hy + ry * 0.9),
                      (hx - r * 1.15, hy)], 2)
    c.ink(back_hair, hair, lw=3.0, shade=0.55, sw=r * 0.5, scol=hair_sh, hi=0.4, hw=r * 0.2, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 0.6, hy + ry * 0.2), (hx - r * 0.9, hy + ry * 1.5), (hx - r * 1.1, hy + ry * 2.6)],
                     [(hx - r * 1.0, hy), (hx - r * 1.3, hy + ry * 1.2), (hx - r * 1.3, hy + ry * 2.2)]], hair_sh)
    # far arm: hand on the hip, elbow forward
    c.ink(b.arm_shape(False), shade_col(skin, 0.9), lw=2.8, shade=0.5)
    b.hand(False, "fist", col=shade_col(skin, 0.9))
    sl = b.sleeve(False, 0.5, 7.2, 6.6)
    c.ink(sl, shade_col(pink, 0.85), lw=2.8, shade=0.4)
    # legs: jeans + cowboy boots
    def boots(bb, near):
        sh = bb.shoe(near, boot if near else shade_col(boot, 0.85), dk(boot, 0.6), "boot", length=1.05)
        an = bb.ankle_n if near else bb.ankle_f
        c.stroke(bb.Ps([(an[0] - 1.6, an[1] + 9), (an[0], an[1] + 6), (an[0] + 1.8, an[1] + 9)]), 1.6, (236, 196, 120),
                 taper=(0.2, 0.2))
        c.ink(Sh([bb.Ps([(an[0] - 2.4, an[1] - 1.2), (an[0] - 0.6, an[1] - 1.2), (an[0] - 0.8, an[1] - 4.3), (an[0] - 2.4, an[1] - 4.3)])]),
              (70, 40, 26), lw=2.0, shade=0.2)
    legs(b, denim, w=(9.0, 6.0, 6.0), scol=denim_sh, shoe=None)
    for near in (False, True):
        boots(b, near)
    # jeans hip + belt
    hips = Sh([b.Ps([(-5.4, b.hip_y + 4.5), (5.0, b.hip_y + 4.5), (5.4, b.hip_y - 3), (-5.6, b.hip_y - 3)])])
    c.ink(hips, denim, lw=3.0, shade=0.45, scol=denim_sh)
    c.ink(Sh([b.Ps([(-5.5, b.hip_y + 5.0), (5.1, b.hip_y + 5.0), (5.1, b.hip_y + 2.6), (-5.5, b.hip_y + 2.6)])]), (110, 58, 32), lw=2.2)
    bx_, by_ = b.P(2.6, b.hip_y + 3.8)
    c.ink(ell(bx_, by_, 9, 6.5), (244, 200, 80), lw=2, shade=0.3, hi=0.6, hw=2)
    # neck + torso (pink western shirt, knotted at the waist)
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.4, hem=b.hip_y + 5.5, flare=-0.6, neck_open=1.1)])
    c.ink(torso, pink, lw=3.0, shade=0.55, sw=18, hi=0.35, rim=0.2, rcol=(255, 190, 220))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.4, sy + 1.4), (sx + 3.2, sy + 1.0), (sx + 1.4, sy - 7.0)])]), skin, lw=2.2, shade=0.5, sw=6)
    # yoke piping + pearl snaps
    c.stroke(b.Ps([(b.sh_n[0] + 0.5, sy - 3.5), (sx - 1, sy - 5.5), (sx + 1.4, sy - 7.5), (sx + 3.6, sy - 5.5),
                   (b.sh_f[0] + 1.0, sy - 3.5)]), 2.0, (255, 236, 244), taper=(0.1, 0.1))
    for yy in (sy - 12, sy - 18):
        c.ink(ell(*b.P(sx * 0.8 + 1.8, yy), 2.2, 2.2), (255, 246, 248), lw=1.2, shade=0, hi=0.4)
    # knot
    kx, ky = b.P(1.0, b.hip_y + 6.5)
    c.ink(ell(kx, ky, 12, 9, -10), pink, lw=2.6, shade=0.5, sw=6)
    c.ink(blob([(kx - 4, ky + 6), (kx + 8, ky + 4), (kx + 14, ky + 24), (kx + 2, ky + 22)], 1), pink, lw=2.4, shade=0.5)
    # collar
    for pts in ([(sx - 3.2, sy + 1.8), (sx + 0.2, sy - 0.4), (sx + 1.4, sy - 6.8), (sx - 1.6, sy - 4.0), (sx - 4.2, sy - 1.6)],
                [(sx + 2.4, sy + 1.0), (sx + 6.0, sy + 0.2), (sx + 5.6, sy - 3.2), (sx + 1.4, sy - 7.0)]):
        c.ink(Sh([b.Ps(pts)]), (255, 246, 248), lw=2.2, shade=0.35, sw=4)
    folds(c, [b.Ps([(-3, b.hip_y + 14), (-1, b.hip_y + 9)]), b.Ps([(3.5, b.hip_y + 16), (2.5, b.hip_y + 10)])],
          shade_col(pink, 0.55), 1.6, 0.6)
    # head
    head = Sh([b.head_pts(jaw=0.95, chin=0.95, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.1, fa["eye_n"][1] + ry * 0.42, r * 0.28, opacity=0.4)
    b.eyes(iris=(60, 170, 100), look=(0.3, 0.1), lid=0.34, lashes=1, size=1.02, tilt=0.06)
    b.brows(col=(150, 90, 40), lift_n=0.12, lift_f=-0.02, tilt_n=-0.2, tilt_f=-0.4, w=r * 0.11)
    b.nose("button", 1.0)
    b.mouth("smirk", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.02, r * 0.52, r * 0.3, lip=(220, 60, 100))
    mx, my = fa["mouth"]
    c.ink(ell(mx + r * 0.45, my - ry * 0.12, 1.4, 1.4), INK, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)   # beauty mark
    b.ear(0.95)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.12, ey_ + r * 0.5, r * 0.12, r * 0.15), (0, 0, 0, 0), lw=2.4, oc=(240, 196, 80), line_only=True)
    # front hair: side-swept fringe and a lock over the shoulder
    fringe = blob([(hx - r * 1.05, hy + ry * 0.1), (hx - r * 0.9, hy - ry * 0.75), (hx - r * 0.1, hy - ry * 1.02),
                   (hx + r * 0.8, hy - ry * 0.8), (hx + r * 1.08, hy - ry * 0.35), (hx + r * 0.7, hy - ry * 0.48),
                   (hx + r * 0.25, hy - ry * 0.4), (hx - r * 0.3, hy - ry * 0.25), (hx - r * 0.55, hy + ry * 0.1),
                   (hx - r * 0.5, hy + ry * 0.7)], 2)
    c.ink(fringe, hair, lw=3.0, shade=0.45, sw=r * 0.4, scol=hair_sh, hi=0.5, hw=r * 0.25, hcol=hair_hi, rim=0.15)
    lock = blob([(hx - r * 0.55, hy + ry * 0.4), (hx - r * 0.25, hy + ry * 0.9), (hx - r * 0.2, hy + ry * 1.8),
                 (hx - r * 0.45, hy + ry * 2.4), (hx - r * 0.75, hy + ry * 1.9), (hx - r * 0.8, hy + ry * 1.0)], 2)
    c.ink(lock, hair, lw=2.8, shade=0.45, sw=r * 0.25, scol=hair_sh, hi=0.4, hw=r * 0.12, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 0.5, hy - ry * 0.85), (hx + r * 0.4, hy - ry * 0.75), (hx + r * 0.9, hy - ry * 0.45)],
                     [(hx - r * 0.55, hy + ry * 0.7), (hx - r * 0.42, hy + ry * 1.5), (hx - r * 0.5, hy + ry * 2.1)]], hair_sh)
    # cowboy hat
    cowboy_hat2(c, hx - r * 0.05, hy - ry * 0.72, r * 2.7, tilt=-9)
    # near arm: thumb hooked in the belt
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5, rim=0.15, rcol=(255, 170, 160))
    b.hand(True, "relaxed", size=0.95)
    sl = b.sleeve(True, 0.62, 7.6, 6.8)
    c.ink(sl, pink, lw=3.0, shade=0.5, sw=10, hi=0.3)
    ex2, ey2 = b.P(*((b.sh_n[0] + b.elbow_n[0] * 1.6) / 2.6, (b.sh_n[1] + b.elbow_n[1] * 1.6) / 2.6))
    c.ink(ell(ex2, ey2, 15, 7, -80), (255, 246, 248), lw=2.2, shade=0.3)
    wx, wy = b.P(*b.wrist_n)
    c.stroke([(wx - 8, wy - 4), (wx + 8, wy - 8)], 3.0, (60, 200, 200))
    return finish_sprite(c, name, flip=True)


# =========================================================================== more outfit helpers
def plaid(c, sh, base, lines=((150, 40, 56), (205, 90, 92)), step=14, angle=0, w=(3.0, 2.0), opacity=0.8):
    bx0, by0, bx1, by1 = sh.bbox()
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    L = max(bx1 - bx0, by1 - by0) * 0.8 + 20
    x = cx - L
    while x < cx + L:
        c.stroke(rot_pts([(x, cy - L), (x, cy + L)], angle, cx, cy), w[0], lines[0], taper=(0, 0), wob=0.3, smooth=0,
                 opacity=opacity) if True else None
        x += step
    y = cy - L
    while y < cy + L:
        c.stroke(rot_pts([(cx - L, y), (cx + L, y)], angle, cx, cy), w[1], lines[1], taper=(0, 0), wob=0.3, smooth=0,
                 opacity=opacity)
        y += step


def clip_draw(c, sh, fn):
    """Run fn(sub) on a temporary layer and composite it clipped to shape sh (keeps outlines intact)."""
    tmp = Canvas2(c.w, c.h, light=c.light, lw=c.lw, seed=c.seed + 5)
    fn(tmp)
    bx0, by0, bx1, by1 = sh.bbox()
    m = Image.new("L", c.img.size, 0)
    sh.render(ImageDraw.Draw(m), 0, 0, 0)
    a = ImageChops_multiply(tmp.img.getchannel("A"), m)
    tmp.img.putalpha(a)
    c.img.alpha_composite(tmp.img)


def skirt(b, col, hem_y, flare=2.0, waist=None, scol=None, pleats=0):
    c = b.c
    wy = waist if waist is not None else b.hip_y + 7
    pts = b.Ps([(-4.9 * b.b["waist"] - 0.4, wy), (4.6 * b.b["waist"] + 0.4, wy), (5.4 * b.b["hips"] + 0.4, b.hip_y + 1),
                (5.4 * b.b["hips"] + flare, hem_y), (-5.6 * b.b["hips"] - flare, hem_y - 0.6), (-5.6 * b.b["hips"] - 0.4, b.hip_y + 1)])
    sh = Sh([chaikin(pts, 1)])
    c.ink(sh, col, lw=c.lw, shade=0.5, scol=scol, hi=0.3)
    for k in range(pleats):
        t = (k + 1) / (pleats + 1)
        x0 = -4.5 + 9 * t
        c.stroke(b.Ps([(x0 * 0.9, b.hip_y), (x0 * 1.2, hem_y + 0.5)]), 1.6, shade_col(col, 0.55), taper=(0.4, 0.1),
                 opacity=0.7)
    return sh


def possum_head(c, cx, cy, s=1.0, tilt=0):
    """Mascot possum head (costume piece), centre (cx, cy), roughly 110*s wide."""
    grey, grey_sh = (170, 168, 182), (120, 116, 140)
    for ex in (-1, 1):
        c.ink(ell(cx + ex * 40 * s, cy - 40 * s, 20 * s, 18 * s, ex * 20), (60, 56, 70), lw=3, shade=0.4)
        c.ink(ell(cx + ex * 40 * s, cy - 40 * s, 11 * s, 10 * s, ex * 20), (240, 150, 170), lw=0, shade=0.3)
    head = blob([(cx - 54 * s, cy - 10 * s), (cx - 40 * s, cy - 44 * s), (cx, cy - 52 * s), (cx + 40 * s, cy - 44 * s),
                 (cx + 54 * s, cy - 10 * s), (cx + 40 * s, cy + 24 * s), (cx + 12 * s, cy + 46 * s), (cx - 12 * s, cy + 46 * s),
                 (cx - 40 * s, cy + 24 * s)], 2)
    c.ink(head, grey, lw=3.2, shade=0.5, sw=20 * s, scol=grey_sh, hi=0.4, rim=0.2)
    c.ink(blob([(cx - 30 * s, cy), (cx, cy - 22 * s), (cx + 30 * s, cy), (cx + 14 * s, cy + 40 * s), (cx - 14 * s, cy + 40 * s)], 2),
          (246, 244, 248), lw=2.4, shade=0.3)
    c.ink(ell(cx, cy + 40 * s, 10 * s, 7 * s), (240, 120, 150), lw=2.4, shade=0.3, hi=0.6, hw=3)
    for ex in (-1, 1):
        c.ink(ell(cx + ex * 18 * s, cy - 8 * s, 9 * s, 10 * s), (24, 14, 24), lw=2.2, shade=0, hi=0)
        c.ink(ell(cx + ex * 18 * s - 3 * s, cy - 11 * s, 3 * s, 3 * s), (255, 255, 255), lw=0, shade=0, hi=0)
    c.stroke([(cx - 8 * s, cy + 50 * s), (cx, cy + 54 * s), (cx + 8 * s, cy + 50 * s)], 2.0)
    for k in (-1, 1):
        c.ink(rect(cx + k * 5 * s - 3 * s, cy + 50 * s, cx + k * 5 * s + 3 * s, cy + 58 * s), (255, 255, 250), lw=1.6)
    # neck hole rim
    c.ink(ell(cx, cy + 44 * s, 26 * s, 8 * s), (60, 56, 70), lw=2.4, shade=0, hi=0)


# =========================================================================== Gil (sleepy roommate in a bathrobe)
def paint_gil(height=400, name="hs_gil.png"):
    W, Hc = 360, 600
    skin = (176, 116, 82)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=41)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=0.92, hips=0.95, limbs=0.95, head=1.06, legs=1.0, neck=1.0),
             pose=dict(arm_n=10, fore_n=62, arm_f=-8, fore_f=12, leg_n=-4, shin_n=3, leg_f=5, shin_f=-3, lean=6,
                       head_dx=1.2, head_dy=-1.0), seed=4)
    robe, robe_sh = (186, 56, 70), (120, 30, 60)
    pj = (120, 160, 236)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (behind) in a robe sleeve
    c.ink(b.arm_shape(False), shade_col(skin, 0.85), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.85))
    sl = b.sleeve(False, to_wrist=True, w0=8.6, w1=8.0, cuff=8.4)
    c.ink(sl, shade_col(robe, 0.8), lw=2.8, shade=0.4)
    # striped pyjama legs + slippers
    def slipper(bb, near):
        bb.shoe(near, (160, 156, 176) if near else (130, 126, 150), kind="slipper", length=1.08)
    legs(b, pj, w=(8.6, 6.6, 6.4), shoe=slipper)
    for near in (False, True):
        sh = b.leg_shape(near, w=(8.6, 6.6, 6.4))
        hp, kn, an = (b.hip_n, b.knee_n, b.ankle_n) if near else (b.hip_f, b.knee_f, b.ankle_f)
        def stripes(tc, hp=hp, an=an):
            x0_, y0_ = b.P(hp[0] - 6, hp[1])
            x1_, y1_ = b.P(an[0] + 6, an[1])
            x = min(x0_, x1_) - 20
            while x < max(x0_, x1_) + 20:
                tc.stroke([(x, y0_), (x + (x1_ - x0_) * 0.0 + 2, y1_ + 20)], 3.4, (244, 246, 255), taper=(0, 0), smooth=0)
                x += 11
        clip_draw(c, sh, stripes)
        c.ink(sh, (0, 0, 0, 0), lw=3.0, line_only=True)
    # robe body (long, belted)
    c.ink(b.neck_shape(), skin, lw=2.8, shade=0.6, sw=7)
    robe_sh_ = Sh([b.torso_pts(slack=1.8, hem=b.hip_y - 18, flare=2.2, neck_open=1.6)])
    c.ink(robe_sh_, robe, lw=0, shade=0, hi=0)
    clip_draw(c, robe_sh_, lambda t: plaid(t, robe_sh_, robe, step=15, angle=4))
    soft_shade(c, robe_sh_, o=0.35)
    c.ink(robe_sh_, (0, 0, 0, 0), lw=3.0, line_only=True)
    sy, sx = b.shoulder_y, b.lean_dx
    # pyjama top V + shawl collar
    c.ink(Sh([b.Ps([(sx - 1.6, sy + 1.4), (sx + 3.6, sy + 1.0), (sx + 1.6, sy - 9)])]), pj, lw=2.2, shade=0.4)
    for pts in ([(sx - 3.0, sy + 2.0), (sx + 0.6, sy + 0.4), (sx + 1.4, sy - 9.5), (sx + 0.2, b.hip_y + 9), (sx - 2.2, b.hip_y + 12),
                 (sx - 2.6, sy - 6)],
                [(sx + 2.6, sy + 1.4), (sx + 6.0, sy + 0.4), (sx + 5.4, sy - 6), (sx + 1.8, b.hip_y + 10), (sx + 1.4, sy - 9.5)]):
        c.ink(Sh([chaikin(b.Ps(pts), 1)]), (236, 196, 150), lw=2.4, shade=0.45, sw=6, hi=0.3)
    # belt + knot + pocket
    c.ink(Sh([b.Ps([(-6.4, b.hip_y + 9.5), (5.8, b.hip_y + 9.5), (5.6, b.hip_y + 6.8), (-6.2, b.hip_y + 6.8)])]), robe_sh,
          lw=2.4, shade=0.3)
    kx, ky = b.P(2.4, b.hip_y + 8)
    c.ink(ell(kx, ky, 8, 7), robe_sh, lw=2.4)
    c.ink(blob([(kx - 3, ky + 4), (kx + 3, ky + 4), (kx + 6, ky + 46), (kx - 2, ky + 44)], 1), robe_sh, lw=2.2, shade=0.3)
    c.ink(blob([(kx + 2, ky + 4), (kx + 8, ky + 4), (kx + 16, ky + 36), (kx + 8, ky + 38)], 1), robe_sh, lw=2.2, shade=0.3)
    folds(c, [b.Ps([(-3, b.hip_y + 3), (-4, b.hip_y - 12)]), b.Ps([(3, b.hip_y + 2), (4.5, b.hip_y - 14)])], robe_sh, 1.8, 0.7)
    # head
    head = Sh([b.head_pts(jaw=1.0, chin=1.0)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.35, rim=0.15, rcol=(240, 150, 120))
    fa = b.face_anchor()
    # stubble
    rng = random.Random(8)
    c.soft(Sh([[(hx - r * 0.2, hy + ry * 0.6), (hx + r * 0.6, hy + ry * 0.62), (hx + r * 1.0, hy + ry * 0.5), (hx + r * 0.9, hy + ry * 1.2),
                (hx + r * 0.2, hy + ry * 1.2), (hx - r * 0.4, hy + ry * 0.9)]]), shade_col(skin, 0.5), 0.35, 4, clip=head)
    for _ in range(26):
        a = rng.uniform(0.3, 2.6)
        c.ink(ell(hx + r * 0.3 + math.cos(a) * r * rng.uniform(0.2, 0.62), hy + ry * 0.66 + math.sin(a) * ry * rng.uniform(0.0, 0.38),
                  0.6, 0.6), shade_col(skin, 0.45), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=head, opacity=0.6)
    b.eyes(iris=(90, 60, 40), look=(0.25, 0.25), lid=0.55, lower=0.12, size=1.0)
    # eye bags
    for (ex, ey), k in ((fa["eye_n"], 1.0), (fa["eye_f"], 0.65)):
        c.stroke([(ex - r * 0.22 * k, ey + ry * 0.36), (ex, ey + ry * 0.42), (ex + r * 0.22 * k, ey + ry * 0.36)], 1.5,
                 shade_col(skin, 0.55), taper=(0.3, 0.3))
    b.brows(col=(40, 26, 24), lift_n=-0.02, lift_f=-0.02, tilt_n=0.25, tilt_f=0.2, w=r * 0.13)
    b.nose("round", 1.05)
    b.mouth("flat", fa["mouth"][0], fa["mouth"][1] + ry * 0.04, r * 0.45, r * 0.2)
    b.ear(1.0)
    # messy short hair
    hairsh = blob([(hx - r * 1.04, hy + ry * 0.25), (hx - r * 1.12, hy - ry * 0.4), (hx - r * 0.85, hy - ry * 0.95),
                   (hx - r * 0.3, hy - ry * 1.25), (hx + r * 0.1, hy - ry * 1.12), (hx + r * 0.45, hy - ry * 1.3),
                   (hx + r * 0.9, hy - ry * 1.0), (hx + r * 1.0, hy - ry * 0.55), (hx + r * 0.6, hy - ry * 0.62),
                   (hx + r * 0.2, hy - ry * 0.55), (hx - r * 0.1, hy - ry * 0.35), (hx - r * 0.25, hy + ry * 0.1),
                   (hx - r * 0.55, hy - ry * 0.05), (hx - r * 0.75, hy + ry * 0.35)], 1)
    c.ink(hairsh, (54, 36, 32), lw=3.0, shade=0.5, sw=r * 0.4, scol=(30, 18, 24), hi=0.4, hw=r * 0.2, hcol=(110, 80, 70))
    for k in range(5):
        a = math.radians(200 + k * 30)
        c.stroke([(hx + math.cos(a) * r * 0.4, hy + math.sin(a) * ry * 0.5), (hx + math.cos(a) * r * 0.95, hy + math.sin(a) * ry * 1.05)],
                 1.4, (110, 80, 70), taper=(0.3, 0.7), opacity=0.6)
    # near arm: holding a steaming mug forward
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    sl = b.sleeve(True, to_wrist=True, w0=9.4, w1=8.8, cuff=9.4)
    c.ink(sl, robe, lw=0, shade=0, hi=0)
    clip_draw(c, sl, lambda t: plaid(t, sl, robe, step=15, angle=30))
    soft_shade(c, sl, o=0.3)
    c.ink(sl, (0, 0, 0, 0), lw=3.0, line_only=True)
    wx, wy = b.P(*b.wrist_n)
    mug = rrect(wx + 4, wy - 34, wx + 40, wy + 6, 6)
    c.ink(ell(wx + 44, wy - 14, 10, 12), (0, 0, 0, 0), lw=4.5, oc=(240, 240, 236), line_only=True)
    c.ink(mug, (240, 240, 236), lw=3.0, shade=0.45, sw=10, hi=0.4)
    c.ink(ell(wx + 22, wy - 33, 17, 4), (90, 50, 30), lw=2.0)
    c.label(wx + 22, wy - 14, "#1", 11, (200, 50, 60), mirror=True)
    b.hand(True, "hold", d=(1.0, 0.1))
    for k in range(3):
        sx0 = wx + 12 + k * 10
        c.stroke([(sx0, wy - 42), (sx0 - 6, wy - 58), (sx0 + 4, wy - 74), (sx0 - 2, wy - 88)], 2.2, (255, 255, 255),
                 opacity=0.6, taper=(0.3, 0.6))
    return finish_sprite(c, name, flip=True)


# =========================================================================== Ivy (shy poet, round glasses, braid)
def paint_ivy(height=380, name="hs_ivy.png"):
    W, Hc = 360, 600
    skin = (252, 214, 186)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=51)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.8, waist=0.78, hips=0.98, limbs=0.84, head=1.1, legs=1.0, neck=0.95, chest=0.8,
                        hand=0.9, foot=0.92),
             pose=dict(arm_n=12, fore_n=96, arm_f=10, fore_f=150, leg_n=-2, shin_n=1, leg_f=-6, shin_f=8, lean=4,
                       head_dx=0.8, head_dy=-1.2), seed=5)
    hair, hair_sh, hair_hi = (130, 76, 46), (82, 44, 34), (190, 130, 80)
    card = (230, 176, 50)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # back hair
    c.ink(blob([(hx - r * 1.05, hy + ry * 0.4), (hx - r * 1.12, hy - ry * 0.5), (hx - r * 0.6, hy - ry * 1.0), (hx + r * 0.3, hy - ry * 1.0),
                (hx + r * 0.6, hy), (hx - r * 0.4, hy + ry * 0.9)], 2), hair, lw=3.0, shade=0.5, sw=r * 0.4, scol=hair_sh)
    # far arm under the book
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    c.ink(b.sleeve(False, to_wrist=True, w0=8.0, w1=7.0, cuff=6.4), shade_col(card, 0.82), lw=2.8, shade=0.4)
    # legs: white knee socks + mary janes
    def mj(bb, near):
        bb.shoe(near, (110, 60, 40) if near else (90, 50, 36), (60, 34, 24), "shoe", length=0.95)
    legs(b, skin, w=(7.6, 5.0, 4.0), shoe=None, skin=True)
    for near in (False, True):
        an = b.ankle_n if near else b.ankle_f
        kn = b.knee_n if near else b.knee_f
        sock = limb(b.Ps([(kn[0] + (an[0] - kn[0]) * 0.1, kn[1] - 1.5), an]), [5.4 * b.u * 0.84, 4.4 * b.u * 0.84], smooth=0)
        c.ink(sock, (250, 250, 244) if near else (220, 220, 230), lw=2.8, shade=0.45)
        c.stroke(b.Ps([(kn[0] - 2.2, kn[1] - 2.2), (kn[0] + 2.4, kn[1] - 1.6)]), 1.6, (200, 200, 220))
        mj(b, near)
        c.stroke(b.Ps([(an[0] - 1.2, an[1] + 0.8), (an[0] + 3.6, an[1] - 0.4)]), 2.0, (60, 34, 24))
    # plaid skirt
    sk = skirt(b, (40, 120, 90), b.hip_y - 19, flare=2.6, pleats=0)
    clip_draw(c, sk, lambda t: plaid(t, sk, None, lines=((24, 80, 60), (220, 200, 90)), step=13, w=(3.0, 1.6), opacity=0.75))
    soft_shade(c, sk, o=0.3, hi=0.1)
    c.ink(sk, (0, 0, 0, 0), lw=3.0, line_only=True)
    for k in range(5):
        x0 = -5 + 2.4 * k
        c.stroke(b.Ps([(x0, b.hip_y + 2), (x0 * 1.25, b.hip_y - 18.5)]), 1.6, (20, 60, 50), taper=(0.5, 0.1), opacity=0.7)
    # torso: white blouse + mustard cardigan
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y + 3.5, flare=0.6, neck_open=1.0)])
    c.ink(torso, card, lw=3.0, shade=0.55, sw=18, hi=0.35, tex=0.12)
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.8, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 3.6, b.hip_y + 4), (sx + 0.6, b.hip_y + 4)])]),
          (250, 248, 240), lw=2.2, shade=0.3)
    for pts in ([(sx - 2.6, sy + 1.8), (sx + 0.4, sy - 0.4), (sx - 0.2, sy - 3.4), (sx - 3.2, sy - 1.6)],
                [(sx + 2.0, sy + 1.4), (sx + 5.0, sy + 0.6), (sx + 4.6, sy - 2.2), (sx + 1.8, sy - 2.8)]):
        c.ink(Sh([b.Ps(pts)]), (255, 255, 250), lw=2.0, shade=0.2)
    for k in range(4):
        c.ink(ell(*b.P(sx + 3.6 - k * 0.1, sy - 6 - k * 5.5), 2.2, 2.2), (150, 90, 40), lw=1.2)
    c.stroke(b.Ps([(sx + 2.8, sy + 0.8), (sx + 3.0, b.hip_y + 3.5)]), 1.6, shade_col(card, 0.55))
    # head
    head = Sh([b.head_pts(jaw=0.92, chin=0.9, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.76), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.1, fa["eye_n"][1] + ry * 0.42, r * 0.34, opacity=0.55)
    b.cheeks(fa["eye_f"][0], fa["eye_f"][1] + ry * 0.42, r * 0.2, opacity=0.45)
    rng = random.Random(3)
    for _ in range(6):
        ex, ey = fa["eye_n"]
        c.ink(ell(ex + rng.uniform(-r * 0.2, r * 0.7), ey + ry * rng.uniform(0.32, 0.46), 1.0, 1.0), (210, 130, 100), lw=0, shade=0,
              hi=0, ao=0, tex=0, wob=0)
    b.eyes(iris=(110, 150, 70), look=(0.2, 0.42), lid=0.3, size=1.0, lashes=1)
    b.brows(col=hair_sh, lift_n=0.06, lift_f=0.04, tilt_n=0.6, tilt_f=0.5, w=r * 0.1)
    b.nose("button", 0.95)
    b.mouth("worried", fa["mouth"][0], fa["mouth"][1] + ry * 0.03, r * 0.34, r * 0.18)
    b.ear(0.9)
    glasses(b, (196, 44, 60), True, 1.05, lw=b.r * 0.08)
    # hair: centre-parted, braid over the far shoulder
    front = blob([(hx - r * 1.08, hy + ry * 0.35), (hx - r * 1.1, hy - ry * 0.5), (hx - r * 0.6, hy - ry * 1.02),
                  (hx + r * 0.3, hy - ry * 1.02), (hx + r * 0.95, hy - ry * 0.6), (hx + r * 1.05, hy - ry * 0.2),
                  (hx + r * 0.7, hy - ry * 0.5), (hx + r * 0.1, hy - ry * 0.55), (hx - r * 0.3, hy - ry * 0.25),
                  (hx - r * 0.45, hy + ry * 0.4), (hx - r * 0.7, hy + ry * 0.7)], 2)
    c.ink(front, hair, lw=3.0, shade=0.45, sw=r * 0.4, scol=hair_sh, hi=0.45, hw=r * 0.22, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 0.2, hy - ry * 0.95), (hx + r * 0.5, hy - ry * 0.7), (hx + r * 0.9, hy - ry * 0.35)],
                     [(hx - r * 0.4, hy - ry * 0.9), (hx - r * 0.9, hy - ry * 0.4), (hx - r * 0.95, hy + ry * 0.3)]], hair_sh)
    bx_, by_ = hx - r * 0.25, hy + ry * 0.85
    for k in range(6):
        y_ = by_ + k * r * 0.42
        x_ = bx_ + k * r * 0.06 + (r * 0.08 if k % 2 else -r * 0.08)
        c.ink(ell(x_, y_, r * 0.28, r * 0.26, 30 if k % 2 else -30), hair, lw=2.6, shade=0.5, sw=r * 0.12, scol=hair_sh, hi=0.4)
    tip = (bx_ + r * 0.36, by_ + r * 2.6)
    c.ink(ell(tip[0], tip[1] - r * 0.1, r * 0.12, r * 0.08), (220, 60, 80), lw=2.0)
    c.ink(blob([(tip[0] - r * 0.12, tip[1]), (tip[0] + r * 0.12, tip[1]), (tip[0] + r * 0.18, tip[1] + r * 0.4), (tip[0] - r * 0.14, tip[1] + r * 0.36)], 1),
          hair, lw=2.2, shade=0.4)
    # the POEMS book hugged to the chest, then the near arm over it
    bk_x, bk_y = b.P(sx + 4.6, sy - 13)
    book = Sh([rot_pts([(bk_x - 34, bk_y - 46), (bk_x + 30, bk_y - 46), (bk_x + 30, bk_y + 40), (bk_x - 34, bk_y + 40)], 8, bk_x, bk_y)])
    c.ink(Sh([rot_pts([(bk_x + 30, bk_y - 46), (bk_x + 40, bk_y - 40), (bk_x + 40, bk_y + 46), (bk_x + 30, bk_y + 40)], 8, bk_x, bk_y)]),
          (250, 246, 230), lw=2.4, shade=0.3)
    c.ink(book, (50, 120, 90), lw=3.0, shade=0.45, sw=14, hi=0.4)
    c.label(bk_x - 4, bk_y - 14, "POEMS", 11, (255, 236, 160), angle=-8, mirror=True)
    c.ink(ell(bk_x - 2, bk_y + 14, 9, 9), (255, 236, 160), lw=1.6)
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    sl = b.sleeve(True, to_wrist=True, w0=8.4, w1=7.4, cuff=6.6)
    c.ink(sl, card, lw=3.0, shade=0.5, sw=10, hi=0.35, tex=0.12)
    b.hand(True, "relaxed", size=0.9, d=(0.3, 1.0))
    return finish_sprite(c, name, flip=True)


# =========================================================================== Ms. Hush (head librarian)
def paint_ms_hush(height=372, name="hs_ms_hush.png"):
    W, Hc = 360, 600
    skin = (246, 206, 180)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=61)
    b = Body(c, 150, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.86, waist=0.95, hips=1.12, limbs=0.88, head=1.08, legs=0.96, neck=0.9, chest=0.6,
                        hand=0.92, foot=0.9),
             pose=dict(arm_n=34, fore_n=118, arm_f=-6, fore_f=60, leg_n=-2, shin_n=1, leg_f=4, shin_f=-1, lean=7,
                       head_dx=1.4, head_dy=-1.5), seed=6)
    cardi, blouse, skirt_c = (120, 70, 160), (214, 190, 240), (130, 92, 60)
    grey, grey_sh = (214, 214, 226), (150, 150, 176)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm holding a blue book against her side
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    wx, wy = b.P(*b.wrist_f)
    c.ink(Sh([rot_pts([(wx - 10, wy - 40), (wx + 44, wy - 40), (wx + 44, wy + 26), (wx - 10, wy + 26)], -10, wx, wy)]),
          (60, 110, 200), lw=2.8, shade=0.4, hi=0.3)
    b.hand(False, "hold", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.2, w1=7.4, cuff=6.6), shade_col(cardi, 0.82), lw=2.8, shade=0.4)
    # legs: stockings + sensible shoes
    def shoes(bb, near):
        bb.shoe(near, (90, 50, 40) if near else (70, 40, 34), (50, 30, 24), "shoe", length=0.95)
    legs(b, (230, 200, 180), w=(7.0, 4.8, 3.9), shoe=shoes, skin=True)
    # long A-line skirt
    sk = skirt(b, skirt_c, b.hip_y - 30, flare=1.2, pleats=4)
    rng = random.Random(4)
    clip_draw(c, sk, lambda t: [t.stroke([(x, sk.bbox()[1]), (x + 6, sk.bbox()[3])], 1.4, shade_col(skirt_c, 0.7), opacity=0.4)
                                for x in np.arange(sk.bbox()[0], sk.bbox()[2], 9)])
    c.ink(sk, (0, 0, 0, 0), lw=3.0, line_only=True)
    # torso: lavender blouse, purple cardigan, pearls
    c.ink(b.neck_shape(0.85), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y + 5, flare=1.2, neck_open=1.0)])
    c.ink(torso, cardi, lw=3.0, shade=0.55, sw=18, hi=0.35, tex=0.12)
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 2.0, sy + 1.6), (sx + 3.2, sy + 1.2), (sx + 4.2, b.hip_y + 5), (sx + 0.4, b.hip_y + 5)])]), blouse,
          lw=2.2, shade=0.35)
    c.ink(Sh([chaikin(b.Ps([(sx - 2.4, sy + 2.0), (sx + 0.6, sy + 0.2), (sx + 1.6, sy + 2.2), (sx + 4.0, sy + 0.8), (sx + 4.4, sy + 2.6),
                            (sx + 0.8, sy + 3.4)]), 1)]), blouse, lw=2.2, shade=0.3)
    for k in range(9):
        a = math.radians(200 - k * 22)
        px_, py_ = b.P(sx + 1.2 + math.cos(a) * 3.0, sy - 2.2 + math.sin(a) * 3.2)
        c.ink(ell(px_, py_, 2.8, 2.8), (252, 248, 240), lw=1.2, shade=0.3, hi=0.6, hw=1.2)
    c.ink(ell(*b.P(sx + 3.5, sy - 5), 5, 6), (120, 220, 200), lw=2.0, hi=0.6, hw=2)   # brooch
    for yy in (sy - 9, sy - 15, sy - 21):
        c.ink(ell(*b.P(sx * 0.7 + 4.6, yy), 2.2, 2.2), (230, 200, 120), lw=1.2)
    # head
    head = Sh([b.head_pts(jaw=0.98, chin=0.92, cheek=0.96)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    for (ex, ey) in (fa["eye_n"],):
        c.stroke([(ex - r * 0.35, ey + ry * 0.32), (ex - r * 0.1, ey + ry * 0.4)], 1.4, shade_col(skin, 0.6))
        c.stroke([(fa["mouth"][0] - r * 0.4, fa["mouth"][1] - ry * 0.1), (fa["mouth"][0] - r * 0.32, fa["mouth"][1] + ry * 0.08)], 1.4,
                 shade_col(skin, 0.6))
    b.cheeks(fa["eye_n"][0] + r * 0.05, fa["eye_n"][1] + ry * 0.42, r * 0.26, opacity=0.35)
    b.eyes(iris=(90, 100, 140), look=(0.45, 0.0), lid=0.42, size=0.95, lashes=1, tilt=-0.08)
    b.brows(col=(150, 150, 170), lift_n=0.16, lift_f=0.14, tilt_n=-0.6, tilt_f=-0.5, w=r * 0.11)
    b.nose("hook", 1.0)
    b.mouth("o", fa["mouth"][0] + r * 0.04, fa["mouth"][1], r * 0.4, r * 0.3)
    b.ear(0.9)
    # grey hair + tight bun
    c.ink(ell(hx - r * 0.55, hy - ry * 1.02, r * 0.55, r * 0.5), grey, lw=3.0, shade=0.5, sw=r * 0.3, scol=grey_sh, hi=0.4)
    c.stroke([(hx - r * 0.9, hy - ry * 1.05), (hx - r * 0.55, hy - ry * 0.95), (hx - r * 0.3, hy - ry * 1.12)], 1.6, grey_sh)
    c.ink(blob([(hx - r * 1.06, hy + ry * 0.3), (hx - r * 1.12, hy - ry * 0.45), (hx - r * 0.6, hy - ry * 0.98),
                (hx + r * 0.35, hy - ry * 1.0), (hx + r * 0.98, hy - ry * 0.55), (hx + r * 0.5, hy - ry * 0.55),
                (hx - r * 0.1, hy - ry * 0.45), (hx - r * 0.3, hy + ry * 0.05), (hx - r * 0.6, hy + ry * 0.4)], 2), grey, lw=3.0,
          shade=0.45, sw=r * 0.4, scol=grey_sh, hi=0.45, hw=r * 0.2, hcol=(250, 250, 255))
    hair_strands(c, [[(hx - r * 0.7, hy - ry * 0.8), (hx + r * 0.1, hy - ry * 0.85), (hx + r * 0.7, hy - ry * 0.6)],
                     [(hx - r * 0.9, hy - ry * 0.3), (hx - r * 0.5, hy - ry * 0.7)]], grey_sh)
    c.stroke([(hx - r * 0.4, hy - ry * 1.3), (hx - r * 0.75, hy - ry * 0.85)], 2.6, (200, 60, 80))  # pencil in the bun
    # cat-eye glasses on a chain
    glasses(b, (200, 40, 70), False, 1.0, lw=b.r * 0.1)
    ear = fa["ear"]
    c.stroke([ear, (ear[0] + r * 0.1, ear[1] + ry * 0.9), (b.P(sx + 1, sy - 4)[0], b.P(sx + 1, sy - 4)[1]),
              (fa["eye_f"][0] + r * 0.3, fa["eye_f"][1] + ry * 0.2)], 1.2, (230, 196, 90), taper=(0, 0), opacity=0.8)
    # near arm: finger to the lips - SHHH
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.4, w1=7.6, cuff=6.8), cardi, lw=3.0, shade=0.5, sw=10, hi=0.35, tex=0.12)
    b.hand(True, "point", size=0.95, d=(0.15, -1.0), thumb=-1)
    return finish_sprite(c, name, flip=False)


# =========================================================================== Roxy Vale (TV host)
def paint_roxy_vale(height=408, name="hs_roxy_vale.png"):
    W, Hc = 360, 600
    skin = (240, 196, 160)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=71)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.86, waist=0.72, hips=1.02, limbs=0.84, head=1.04, legs=1.06, neck=1.0, chest=1.3,
                        hand=0.92, foot=0.9),
             pose=dict(arm_n=14, fore_n=128, arm_f=-12, fore_f=24, leg_n=4, shin_n=-2, leg_f=-8, shin_f=6, lean=-3,
                       head_dx=0.2), seed=7)
    blazer, blazer_hi = (236, 46, 140), (255, 140, 200)
    hair, hair_sh, hair_hi = (96, 30, 80), (56, 14, 52), (170, 70, 140)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (behind), hand on the hip
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.0, w1=7.0, cuff=6.2), shade_col(blazer, 0.8), lw=2.8, shade=0.4)
    # legs + pink heels
    def heels(bb, near):
        bb.shoe(near, (255, 70, 150) if near else (210, 50, 120), kind="heel", heel_col=(200, 30, 100), length=0.95)
    legs(b, skin, w=(7.2, 4.9, 3.6), shoe=heels, skin=True)
    # black pencil skirt
    sk = skirt(b, (40, 30, 50), b.hip_y - 18, flare=-1.0, waist=b.hip_y + 7)
    c.ink(sk, (0, 0, 0, 0), lw=0, shade=0, hi=0)
    c.stroke(b.Ps([(2.0, b.hip_y - 10), (2.6, b.hip_y - 18)]), 1.6, (90, 80, 110))
    # torso: sparkly blazer over a black top
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.8, hem=b.hip_y + 1.5, flare=0.8, neck_open=1.2)])
    c.ink(torso, blazer, lw=3.0, shade=0.55, sw=18, hi=0.4, hcol=blazer_hi, rim=0.2, rcol=(255, 190, 230))
    rng = random.Random(9)
    bx0, by0, bx1, by1 = torso.bbox()
    for _ in range(70):
        x_, y_ = rng.uniform(bx0, bx1), rng.uniform(by0, by1)
        c.ink(ell(x_, y_, 1.4, 1.4), (255, 230, 250), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=torso, opacity=0.8)
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 2.0, sy + 1.6), (sx + 3.4, sy + 1.2), (sx + 3.4, b.hip_y + 8), (sx + 0.4, b.hip_y + 8)])]), (30, 24, 40),
          lw=2.2, shade=0.2)
    c.ink(Sh([b.Ps([(sx - 1.6, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 1.0, sy - 4.5)])]), skin, lw=2.0, shade=0.4)
    for pts in ([(sx - 3.0, sy + 2.0), (sx - 0.6, sy + 0.6), (sx + 0.6, b.hip_y + 9), (sx - 2.0, sy - 8)],
                [(sx + 3.0, sy + 1.4), (sx + 5.8, sy + 0.6), (sx + 4.2, sy - 7), (sx + 3.2, b.hip_y + 9)]):
        c.ink(Sh([b.Ps(pts)]), hi_col(blazer, 0.15), lw=2.4, shade=0.35, sw=6, hi=0.4)
    c.ink(ell(*b.P(sx + 1.0, sy - 2.0), 5, 5), (255, 220, 90), lw=1.6, hi=0.6, hw=2)   # necklace pendant
    c.stroke([b.P(sx - 1.2, sy + 0.8), b.P(sx + 1.0, sy - 1.4), b.P(sx + 3.0, sy + 0.6)], 1.2, (255, 220, 90), smooth=1)
    # head
    head = Sh([b.head_pts(jaw=0.95, chin=0.95, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.44, r * 0.3, (255, 100, 150), 0.45)
    # eyeshadow
    for (ex, ey), k in ((fa["eye_n"], 1.0), (fa["eye_f"], 0.65)):
        c.soft(ell(ex, ey - ry * 0.22, r * 0.34 * k, ry * 0.2), (180, 60, 200), 0.5, 3)
    b.eyes(iris=(150, 70, 190), look=(0.35, 0.05), lid=0.16, size=1.06, lashes=1)
    b.brows(col=hair_sh, lift_n=0.12, lift_f=0.1, tilt_n=-0.1, tilt_f=-0.2, w=r * 0.11)
    b.nose("button", 0.95)
    b.mouth("grin", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.03, r * 0.66, r * 0.42, open_col=(150, 20, 60))
    mx, my = fa["mouth"]
    c.stroke(bez((mx - r * 0.32, my - ry * 0.05), (mx, my - ry * 0.12), (mx + r * 0.33, my - ry * 0.1), 10), 2.6, (220, 30, 100),
             opacity=0.8)
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.1, ey_ + r * 0.62, r * 0.2, r * 0.24), (0, 0, 0, 0), lw=3.2, oc=(250, 206, 70), line_only=True)
    # glossy plum bob with a side sweep
    bob = blob([(hx - r * 1.2, hy + ry * 0.7), (hx - r * 1.25, hy - ry * 0.3), (hx - r * 0.85, hy - ry * 1.0), (hx - r * 0.1, hy - ry * 1.15),
                (hx + r * 0.75, hy - ry * 0.95), (hx + r * 1.15, hy - ry * 0.45), (hx + r * 1.18, hy + ry * 0.1),
                (hx + r * 0.95, hy - ry * 0.25), (hx + r * 0.6, hy - ry * 0.55), (hx + r * 0.1, hy - ry * 0.55),
                (hx - r * 0.25, hy - ry * 0.2), (hx - r * 0.3, hy + ry * 0.45), (hx - r * 0.55, hy + ry * 0.85),
                (hx - r * 0.9, hy + ry * 0.95)], 2)
    c.ink(bob, hair, lw=3.0, shade=0.5, sw=r * 0.45, scol=hair_sh, hi=0.55, hw=r * 0.25, hcol=hair_hi, rim=0.25,
          rcol=(255, 140, 220))
    hair_strands(c, [[(hx - r * 0.6, hy - ry * 0.95), (hx + r * 0.3, hy - ry * 0.9), (hx + r * 1.0, hy - ry * 0.35)],
                     [(hx - r * 1.0, hy - ry * 0.5), (hx - r * 0.95, hy + ry * 0.3), (hx - r * 0.7, hy + ry * 0.8)]],
                 hair_hi, w=2.2, o=0.6)
    # near arm: microphone held up near the chin
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.4, w1=7.6, cuff=6.6), blazer, lw=3.0, shade=0.5, sw=10, hi=0.4, hcol=blazer_hi)
    wx, wy = b.P(*b.wrist_n)
    c.ink(limb([(wx + 8, wy + 20), (wx + 14, wy - 30)], [11, 9], smooth=0), (40, 40, 50), lw=2.6, shade=0.4, hi=0.4)
    c.ink(ell(wx + 15, wy - 40, 15, 17), (200, 200, 214), lw=2.8, shade=0.5, sw=8, hi=0.6, hw=4)
    for k in range(-2, 3):
        c.stroke([(wx + 4, wy - 40 + k * 5), (wx + 26, wy - 40 + k * 5)], 1.0, (120, 120, 140), opacity=0.7)
    c.ink(rect(wx + 6, wy - 22, wx + 22, wy - 14), (255, 70, 150), lw=1.8)
    b.hand(True, "fist", size=0.95, d=(0.2, -1.0))
    for k in range(4):   # sparkle
        x_, y_ = b.P(-12 + k * 6, 60 + (k % 2) * 10)
        c.stroke([(x_ - 5, y_), (x_ + 5, y_)], 1.6, (255, 250, 200))
        c.stroke([(x_, y_ - 5), (x_, y_ + 5)], 1.6, (255, 250, 200))
    return finish_sprite(c, name, flip=True)


# =========================================================================== Boomer (sleepwalking linebacker)
def paint_boomer(height=430, name="hs_boomer.png"):
    W, Hc = 460, 640
    skin = (232, 176, 140)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.2, seed=81)
    b = Body(c, 190, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.45, waist=1.4, hips=1.3, limbs=1.45, head=0.92, legs=0.95, neck=1.5, chest=2.0, belly=3.2,
                        hand=1.15, foot=1.1),
             pose=dict(arm_n=72, fore_n=8, arm_f=64, fore_f=16, leg_n=-4, shin_n=2, leg_f=6, shin_f=-3, lean=-2,
                       head_dx=1.6, head_dy=-1.5), seed=8)
    pj, pj_sh = (90, 130, 220), (50, 70, 160)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy

    def dots(sh, step=26, rad=4.4):
        def fn(t):
            bx0, by0, bx1, by1 = sh.bbox()
            y = by0
            row = 0
            while y < by1 + step:
                x = bx0 + (row % 2) * step / 2
                while x < bx1 + step:
                    t.ink(ell(x, y, rad, rad), (255, 220, 80), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
                    x += step
                y += step * 0.86
                row += 1
        clip_draw(c, sh, fn)
    # far arm (behind), reaching forward
    fa_sh = b.arm_shape(False)
    c.ink(fa_sh, shade_col(skin, 0.86), lw=3.0, shade=0.4)
    b.hand(False, "open", col=shade_col(skin, 0.86), size=1.1)
    sl = b.sleeve(False, to_wrist=True, w0=11.5, w1=10.0, cuff=9.4)
    c.ink(sl, shade_col(pj, 0.82), lw=3.0, shade=0.4)
    dots(sl)
    c.ink(sl, (0, 0, 0, 0), lw=3.0, line_only=True)
    # legs
    def slip(bb, near):
        bb.shoe(near, (150, 96, 60) if near else (120, 76, 50), kind="slipper", length=1.0)
    for near in (False, True):
        sh = b.leg_shape(near, w=(9.6, 7.8, 7.2))
        c.ink(sh, pj if near else shade_col(pj, 0.85), lw=3.2, shade=0.5, scol=pj_sh, hi=0.3)
        dots(sh)
        c.ink(sh, (0, 0, 0, 0), lw=3.2, line_only=True)
        slip(b, near)
    # torso: big pyjama top with buttons
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=10)
    torso = Sh([b.torso_pts(slack=1.2, hem=b.hip_y - 3, flare=1.0, neck_open=1.3)])
    c.ink(torso, pj, lw=0, shade=0, hi=0)
    dots(torso)
    soft_shade(c, torso, o=0.35)
    c.ink(torso, (0, 0, 0, 0), lw=3.2, line_only=True)
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 2.0, sy + 1.6), (sx + 3.6, sy + 1.2), (sx + 1.6, sy - 5.0)])]), skin, lw=2.4, shade=0.5)
    for pts in ([(sx - 3.4, sy + 2.0), (sx + 0.0, sy + 0.0), (sx + 1.6, sy - 5.4), (sx - 1.4, sy - 4.0), (sx - 4.6, sy - 1.4)],
                [(sx + 2.8, sy + 1.2), (sx + 6.6, sy + 0.4), (sx + 6.2, sy - 3.0), (sx + 1.6, sy - 5.6)]):
        c.ink(Sh([b.Ps(pts)]), (240, 240, 250), lw=2.4, shade=0.3)
    for k in range(4):
        f = k / 4
        c.ink(ell(*b.P(sx * (1 - f) + 2.2 + b.b["belly"] * f * 0.6 + 1.0, sy - 8 - k * 7.5), 3.2, 3.2), (250, 250, 240), lw=1.4)
    # head (bald), nightcap
    head = Sh([b.head_pts(jaw=1.25, chin=1.1, cheek=1.05)])
    c.ink(head, skin, lw=3.2, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.4, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.45, r * 0.32, opacity=0.4)
    b.eyes(closed=True, size=1.0)
    b.brows(col=(120, 80, 60), lift_n=-0.05, lift_f=-0.05, tilt_n=0.3, tilt_f=0.2, w=r * 0.15)
    b.nose("round", 1.15)
    b.mouth("o", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.55, r * 0.42)
    mx, my = fa["mouth"]
    c.ink(blob([(mx - r * 0.02, my + ry * 0.2), (mx + r * 0.06, my + ry * 0.2), (mx + r * 0.06, my + ry * 0.5), (mx, my + ry * 0.55)], 1),
          (190, 230, 255), lw=1.4, shade=0.2, hi=0.5)   # drool
    b.ear(1.0)
    cap_pts = [(hx - r * 1.1, hy - ry * 0.3), (hx - r * 0.95, hy - ry * 1.0), (hx - r * 0.2, hy - ry * 1.25), (hx + r * 0.6, hy - ry * 1.1),
               (hx + r * 1.05, hy - ry * 0.55), (hx + r * 0.2, hy - ry * 0.6), (hx - r * 0.6, hy - ry * 0.35)]
    tail = [(hx - r * 0.5, hy - ry * 1.15), (hx - r * 1.4, hy - ry * 1.5), (hx - r * 2.0, hy - ry * 1.0), (hx - r * 2.1, hy - ry * 0.3),
            (hx - r * 1.7, hy - ry * 0.1), (hx - r * 1.5, hy - ry * 0.7), (hx - r * 1.05, hy - ry * 0.75)]
    capsh = blob(cap_pts, 2) + blob(tail, 2)
    c.ink(capsh, (220, 50, 60), lw=3.2, shade=0.5, sw=r * 0.4, hi=0.4)
    clip_draw(c, capsh, lambda t: [t.stroke([(x, hy - ry * 2), (x - r * 0.6, hy + ry * 0.2)], r * 0.18, (250, 246, 240), taper=(0, 0))
                                   for x in np.arange(hx - r * 3, hx + r * 2, r * 0.5)])
    c.ink(capsh, (0, 0, 0, 0), lw=3.2, line_only=True)
    c.ink(Sh([chaikin([(hx - r * 1.12, hy - ry * 0.1), (hx - r * 0.95, hy - ry * 0.58), (hx + r * 0.2, hy - ry * 0.72), (hx + r * 1.1, hy - ry * 0.62),
                       (hx + r * 1.12, hy - ry * 0.4), (hx + r * 0.2, hy - ry * 0.45), (hx - r * 0.8, hy - ry * 0.3), (hx - r * 1.0, hy + ry * 0.1)], 1)]),
          (250, 246, 240), lw=3.0, shade=0.4)
    c.ink(ell(hx - r * 2.0, hy - ry * 0.15, r * 0.36, r * 0.36), (250, 246, 240), lw=3.0, shade=0.4, hi=0.3)
    # Zzz
    for k, (dx, dy, sz) in enumerate(((1.4, -1.5, 15), (1.9, -2.0, 20), (2.5, -2.6, 26))):
        c.text(hx + r * dx, hy + ry * dy, "Z", sz, (240, 240, 255), stroke=1.5, sc=INK)
    # near arm reaching forward, hugging the air
    c.ink(b.arm_shape(True), skin, lw=3.2, shade=0.5)
    sl = b.sleeve(True, to_wrist=True, w0=12.0, w1=10.6, cuff=10.0)
    c.ink(sl, pj, lw=0, shade=0, hi=0)
    dots(sl)
    soft_shade(c, sl, o=0.3)
    c.ink(sl, (0, 0, 0, 0), lw=3.2, line_only=True)
    b.hand(True, "open", size=1.1)
    return finish_sprite(c, name, flip=False)


# =========================================================================== Doreen (night cook)
def paint_doreen(height=392, name="hs_doreen.png"):
    W, Hc = 380, 620
    skin = (140, 88, 62)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=91)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.1, waist=1.15, hips=1.25, limbs=1.2, head=1.04, legs=0.96, neck=1.05, chest=1.6, belly=1.6,
                        hand=1.08, foot=1.0),
             pose=dict(arm_n=18, fore_n=62, arm_f=-10, fore_f=12, leg_n=-6, shin_n=2, leg_f=8, shin_f=-4, lean=-2,
                       head_dx=0.5), seed=9)
    white, white_sh = (246, 244, 240), (190, 186, 210)
    apron = (60, 150, 110)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm, hand on hip (behind)
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.86))
    c.ink(b.sleeve(False, 0.5, 9.2, 8.6), shade_col(white, 0.82), lw=2.8, shade=0.4)
    # white trousers + purple shoes
    def shoes(bb, near):
        bb.shoe(near, (130, 70, 190) if near else (100, 56, 150), (240, 240, 240), "sneaker")
    legs(b, white, w=(9.4, 7.0, 6.4), scol=white_sh, shoe=shoes)
    # torso: white cook's tunic
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=8)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y - 3, flare=1.4, neck_open=0.9)])
    c.ink(torso, white, lw=3.0, shade=0.55, sw=18, scol=white_sh, hi=0.3)
    sy, sx = b.shoulder_y, b.lean_dx
    # apron: bib + skirt, name tag
    ap = Sh([chaikin(b.Ps([(sx - 0.2, sy - 4), (sx + 5.0, sy - 4), (sx + 6.6, b.hip_y + 10), (6.2 * b.b["hips"] + 2.0, b.hip_y - 20),
                           (-4.6 * b.b["hips"], b.hip_y - 20), (-3.6, b.hip_y + 9), (sx - 1.0, sy - 10)]), 1)])
    c.ink(ap, apron, lw=3.0, shade=0.55, sw=16, hi=0.35)
    c.stroke(b.Ps([(sx - 0.2, sy - 4), (sx - 2.0, sy + 1.2)]), 3.0, apron)
    c.stroke(b.Ps([(-4.8, b.hip_y + 9.5), (sx + 6.6, b.hip_y + 10)]), 3.2, shade_col(apron, 0.6))
    c.ink(ell(*b.P(sx + 3.2, sy - 12), 13, 13), (255, 236, 160), lw=2.2, shade=0.3)
    c.label(*b.P(sx + 3.2, sy - 12), "D", 13, (60, 100, 70))
    tx_, ty_ = b.P(sx + 0.6, sy - 3.6)
    c.ink(rrect(tx_ - 22, ty_ - 8, tx_ + 22, ty_ + 8, 3), (250, 250, 250), lw=1.8)
    c.label(tx_, ty_, "DOREEN", 7, (40, 40, 60), "Bold")
    for k in range(3):   # grease stains
        x_, y_ = b.P(2 + k * 2.4, b.hip_y - 4 - k * 4)
        c.soft(ell(x_, y_, 8, 6), (90, 60, 30), 0.25, 2, clip=ap)
    # head
    head = Sh([b.head_pts(jaw=1.05, chin=1.0, cheek=1.02)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.7), hi=0.35, rim=0.15, rcol=(240, 150, 120))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.45, r * 0.3, (230, 90, 90), 0.35)
    b.eyes(iris=(90, 56, 30), look=(0.35, 0.1), lid=0.25, size=1.0, lashes=1)
    b.brows(col=(40, 20, 20), lift_n=0.2, lift_f=0.14, tilt_n=-0.4, tilt_f=-0.5, w=r * 0.13)
    b.nose("round", 1.05)
    b.mouth("smile", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.58, r * 0.32, lip=(150, 60, 70))
    b.ear(0.95)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.05, ey_ + r * 0.5, r * 0.09, r * 0.09), (250, 210, 90), lw=1.6)
    # red hair in a bun under a hairnet
    hair, hair_sh = (200, 60, 40), (130, 30, 30)
    hs = blob([(hx - r * 1.08, hy + ry * 0.2), (hx - r * 1.2, hy - ry * 0.6), (hx - r * 0.7, hy - ry * 1.15), (hx + r * 0.2, hy - ry * 1.2),
               (hx + r * 0.95, hy - ry * 0.7), (hx + r * 1.02, hy - ry * 0.35), (hx + r * 0.5, hy - ry * 0.5), (hx - r * 0.2, hy - ry * 0.35),
               (hx - r * 0.5, hy + ry * 0.2)], 2) + ell(hx - r * 0.75, hy - ry * 1.15, r * 0.62, r * 0.55)
    c.ink(hs, hair, lw=3.0, shade=0.5, sw=r * 0.4, scol=hair_sh, hi=0.45, hw=r * 0.2)
    clip_draw(c, hs, lambda t: ([t.stroke([(x, hy - ry * 2), (x + r * 1.0, hy + ry * 0.4)], 1.2, (250, 250, 250), taper=(0, 0), opacity=0.7)
                                 for x in np.arange(hx - r * 3, hx + r * 2, r * 0.22)] +
                                [t.stroke([(x, hy - ry * 2), (x - r * 1.0, hy + ry * 0.4)], 1.2, (250, 250, 250), taper=(0, 0), opacity=0.7)
                                 for x in np.arange(hx - r * 2, hx + r * 3, r * 0.22)]))
    c.ink(hs, (0, 0, 0, 0), lw=3.0, line_only=True)
    # near arm: big forearm, giant spatula raised
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, 0.5, 9.6, 9.0), white, lw=3.0, shade=0.5, scol=white_sh)
    wx, wy = b.P(*b.wrist_n)
    gx, gy = wx + 14, wy - 4
    dx_, dy_ = 0.5, -0.87
    top_ = (gx + dx_ * 110, gy + dy_ * 110)
    c.ink(limb([(gx - dx_ * 22, gy - dy_ * 22), top_], [9, 8], smooth=0), (60, 40, 30), lw=2.6, shade=0.4)
    blade = Sh([rot_pts([(top_[0] - 28, top_[1] - 78), (top_[0] + 28, top_[1] - 78), (top_[0] + 28, top_[1] + 4), (top_[0] - 28, top_[1] + 4)],
                        30, top_[0], top_[1])])
    c.ink(blade, (210, 214, 226), lw=3.0, shade=0.5, sw=12, hi=0.5)
    for k in range(3):
        c.ink(Sh([rot_pts([(top_[0] - 18 + k * 15, top_[1] - 66), (top_[0] - 11 + k * 15, top_[1] - 66), (top_[0] - 11 + k * 15, top_[1] - 14),
                           (top_[0] - 18 + k * 15, top_[1] - 14)], 30, top_[0], top_[1])]), (120, 124, 140), lw=1.6)
    b.hand(True, "fist", size=1.0, d=(1.0, -0.2))
    return finish_sprite(c, name, flip=False)


# =========================================================================== Kyle (in the possum suit)
def paint_kyle(height=396, name="hs_kyle.png"):
    W, Hc = 420, 620
    skin = (250, 210, 176)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=101)
    b = Body(c, 190, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.2, waist=1.35, hips=1.35, limbs=1.55, head=1.0, legs=0.95, neck=1.0, chest=1.0, belly=2.2,
                        hand=1.15, foot=1.25),
             pose=dict(arm_n=8, fore_n=48, arm_f=-14, fore_f=30, leg_n=-6, shin_n=3, leg_f=8, shin_f=-4, lean=6,
                       head_dx=1.0, head_dy=-0.6), seed=10)
    grey, grey_sh = (168, 166, 182), (116, 112, 140)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # tail behind
    tx, ty = b.P(-6, b.hip_y - 2)
    tail = limb([(tx, ty), (tx - 50, ty + 30), (tx - 80, ty + 10), (tx - 96, ty - 30), (tx - 80, ty - 50)], [18, 15, 12, 9, 6], smooth=2)
    c.ink(tail, (240, 160, 180), lw=3.0, shade=0.5, hi=0.4)
    # far arm
    c.ink(b.arm_shape(False), shade_col(grey, 0.84), lw=3.0, shade=0.4)
    b.hand(False, "relaxed", col=(140, 136, 160), size=1.1)
    # suit legs + big feet
    def feet(bb, near):
        an = bb.ankle_n if near else bb.ankle_f
        x, y = an
        sh = blob(bb.Ps([(x - 4, y + 3), (x + 4, y + 3), (x + 13, y - 1), (x + 13, y - 4.4), (x - 4, y - 4.4)]), 2)
        c.ink(sh, (130, 126, 150) if near else (110, 106, 130), lw=3.0, shade=0.5)
        for k in range(3):
            c.ink(ell(*bb.P(x + 13, y - 1.0 - k * 1.3), 4, 3.2), (240, 160, 180), lw=1.6)
    legs(b, grey, w=(10.5, 8.6, 8.0), scol=grey_sh, shoe=feet)
    # suit body with white belly
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=8)
    torso = Sh([b.torso_pts(slack=1.8, hem=b.hip_y - 4, flare=1.6, neck_open=0.8)])
    c.ink(torso, grey, lw=3.0, shade=0.55, sw=22, scol=grey_sh, hi=0.3, tex=0.2)
    sy, sx = b.shoulder_y, b.lean_dx
    belly = blob(b.Ps([(sx + 0.5, sy - 4), (sx + 6.5, sy - 6), (sx + 7.5 + b.b["belly"], b.hip_y + 8), (5.5, b.hip_y - 3), (-1.5, b.hip_y - 2),
                       (-1.8, b.hip_y + 12)]), 2)
    c.ink(belly, (246, 244, 250), lw=2.6, shade=0.45, sw=16, hi=0.2, tex=0.2)
    rng = random.Random(5)
    for _ in range(40):   # fur tufts
        x_, y_ = rng.uniform(*torso.bbox()[0::2]), rng.uniform(*torso.bbox()[1::2])
        c.stroke([(x_, y_), (x_ + rng.uniform(-4, 4), y_ + 8)], 1.4, grey_sh, opacity=0.5, taper=(0.3, 0.7))
    c.ink(ell(*b.P(sx + 1.2, sy + 0.4), 22, 7), (90, 86, 110), lw=2.4)   # neck ring of the suit
    # head: tired, sweaty, red headband
    head = Sh([b.head_pts(jaw=1.0, chin=1.0)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.42, r * 0.36, (255, 110, 110), 0.55)
    b.eyes(iris=(80, 140, 90), look=(0.3, 0.3), lid=0.5, lower=0.1, size=1.0)
    b.brows(col=(150, 100, 50), lift_n=0.02, lift_f=0.0, tilt_n=0.7, tilt_f=0.6, w=r * 0.11)
    b.nose("round", 1.0)
    b.mouth("frown", fa["mouth"][0], fa["mouth"][1] + ry * 0.06, r * 0.42, r * 0.22)
    b.ear(0.95)
    hair = (226, 170, 90)
    c.ink(blob([(hx - r * 1.05, hy + ry * 0.2), (hx - r * 1.12, hy - ry * 0.5), (hx - r * 0.5, hy - ry * 1.1), (hx + r * 0.4, hy - ry * 1.08),
                (hx + r * 1.0, hy - ry * 0.6), (hx + r * 0.6, hy - ry * 0.45), (hx, hy - ry * 0.4), (hx - r * 0.4, hy + ry * 0.1)], 2), hair,
          lw=3.0, shade=0.45, sw=r * 0.35, scol=(170, 110, 50), hi=0.4)
    band = Sh([[(hx - r * 1.1, hy - ry * 0.45), (hx + r * 1.02, hy - ry * 0.62), (hx + r * 1.0, hy - ry * 0.4), (hx - r * 1.1, hy - ry * 0.2)]])
    c.ink(band, (220, 40, 50), lw=2.6, shade=0.4, hi=0.3)
    for (dx, dy) in ((1.15, -0.1), (1.25, 0.3), (-0.2, -0.05)):
        x_, y_ = hx + r * dx, hy + ry * dy
        c.ink(blob([(x_, y_ - 6), (x_ + 4, y_ + 2), (x_, y_ + 5), (x_ - 4, y_ + 2)], 1), (170, 225, 255), lw=1.6, hi=0.6, hw=1.5)
    # near arm hugging the possum head
    c.ink(b.arm_shape(True), grey, lw=3.0, shade=0.5, scol=grey_sh)
    wx, wy = b.P(*b.wrist_n)
    possum_head(c, wx + 6, wy - 40, 0.82)
    b.hand(True, "relaxed", col=(150, 146, 170), size=1.1)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Percival Thorne (slam poet)
def paint_percival_thorne(height=420, name="hs_percival_thorne.png"):
    W, Hc = 380, 620
    skin = (244, 214, 196)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=111)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.88, waist=0.82, hips=0.86, limbs=0.85, head=1.02, legs=1.05, neck=1.1),
             pose=dict(arm_n=-4, fore_n=40, arm_f=26, fore_f=120, leg_n=-6, shin_n=4, leg_f=8, shin_f=-5, lean=-5,
                       head_dx=-0.6, head_dy=0.5), seed=11)
    black, black_sh = (46, 38, 58), (22, 16, 30)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm raised, snapping fingers
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.88), d=(0.2, -1.0))
    wx, wy = b.P(*b.wrist_f)
    for k in range(3):
        a = math.radians(-60 + k * 40)
        c.stroke([(wx + 10 + math.cos(a) * 18, wy - 24 + math.sin(a) * 18), (wx + 10 + math.cos(a) * 30, wy - 24 + math.sin(a) * 30)], 2.2,
                 (255, 250, 200))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.0, w1=7.2, cuff=6.4), mix(black, black_sh, 0.4), lw=2.8, shade=0.3)
    # skinny black jeans + pointy boots
    def boots(bb, near):
        bb.shoe(near, (40, 30, 40) if near else (30, 22, 32), (20, 14, 20), "shoe", length=1.15)
    legs(b, (60, 56, 76), w=(7.4, 5.2, 4.6), scol=black_sh, shoe=boots)
    # black turtleneck + long coat
    c.ink(b.neck_shape(1.05), black, lw=2.8, shade=0.5)
    coat = Sh([b.torso_pts(slack=1.4, hem=b.hip_y - 20, flare=2.6, neck_open=1.4)])
    c.ink(coat, (64, 48, 78), lw=3.0, shade=0.55, sw=20, hi=0.3, rim=0.25, rcol=(170, 140, 220))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.8, sy + 2.4), (sx + 3.4, sy + 2.0), (sx + 4.0, b.hip_y - 4), (sx - 0.4, b.hip_y - 4)])]), black, lw=2.4,
          shade=0.4)
    for pts in ([(sx - 3.2, sy + 1.6), (sx - 1.2, sy + 0.8), (sx - 0.6, b.hip_y + 4), (sx - 3.0, sy - 10)],
                [(sx + 3.6, sy + 1.2), (sx + 6.4, sy + 0.2), (sx + 5.0, sy - 10), (sx + 3.8, b.hip_y + 4)]):
        c.ink(Sh([b.Ps(pts)]), (80, 62, 96), lw=2.4, shade=0.4, sw=6, hi=0.3)
    # red scarf, long ends
    sc = (210, 40, 56)
    c.ink(blob(b.Ps([(sx - 3.4, sy + 2.6), (sx + 4.4, sy + 2.4), (sx + 5.0, sy - 1.6), (sx - 2.6, sy - 1.8)]), 2), sc, lw=2.8, shade=0.5, hi=0.3)
    c.ink(blob(b.Ps([(sx + 2.6, sy - 1.0), (sx + 5.4, sy - 1.4), (sx + 5.4, sy - 24), (sx + 2.4, sy - 22)]), 1), sc, lw=2.8, shade=0.5, hi=0.3)
    for k in range(4):
        c.stroke(b.Ps([(sx + 2.6, sy - 5 - k * 5), (sx + 5.4, sy - 6 - k * 5)]), 1.6, (250, 230, 230), opacity=0.7)
    for k in range(4):
        c.stroke(b.Ps([(sx + 2.6 + k * 0.8, sy - 22.5), (sx + 2.8 + k * 0.8, sy - 25)]), 1.6, sc)
    # head
    head = Sh([b.head_pts(jaw=1.0, chin=1.15, cheek=0.96, chin_drop=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.eyes(iris=(70, 70, 110), look=(0.4, 0.0), lid=0.48, size=0.98, tilt=0.1)
    b.brows(col=(30, 20, 30), lift_n=0.18, lift_f=0.0, tilt_n=-0.5, tilt_f=-0.6, w=r * 0.12)
    b.nose("long", 1.0)
    b.mouth("smirk", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.45, r * 0.24)
    mx, my = fa["mouth"]
    c.ink(blob([(mx - r * 0.05, my + ry * 0.18), (mx + r * 0.3, my + ry * 0.16), (mx + r * 0.2, my + ry * 0.48), (mx + r * 0.05, my + ry * 0.5)], 1),
          (40, 26, 30), lw=1.8, shade=0.2)   # goatee
    c.stroke([(mx - r * 0.25, my - ry * 0.12), (mx + r * 0.1, my - ry * 0.2), (mx + r * 0.38, my - ry * 0.14)], 2.2, (40, 26, 30))  # thin moustache
    b.ear(0.92)
    c.ink(blob([(hx - r * 1.05, hy + ry * 0.35), (hx - r * 1.1, hy - ry * 0.4), (hx - r * 0.6, hy - ry * 0.75), (hx + r * 0.2, hy - ry * 0.7),
                (hx + r * 0.7, hy - ry * 0.4), (hx + r * 0.2, hy - ry * 0.38), (hx - r * 0.35, hy - ry * 0.2), (hx - r * 0.5, hy + ry * 0.45)], 2),
          (30, 22, 30), lw=3.0, shade=0.4, hi=0.3, hcol=(90, 70, 100))
    # beret, tilted
    bx_, by_ = hx + r * 0.05, hy - ry * 0.75
    beret = blob([(bx_ - r * 1.25, by_ + r * 0.15), (bx_ - r * 1.0, by_ - r * 0.45), (bx_ - r * 0.2, by_ - r * 0.7), (bx_ + r * 0.8, by_ - r * 0.5),
                  (bx_ + r * 1.2, by_ - r * 0.1), (bx_ + r * 0.9, by_ + r * 0.2), (bx_ - r * 0.3, by_ + r * 0.25)], 2)
    c.ink(beret, (34, 28, 44), lw=3.0, shade=0.5, sw=r * 0.3, hi=0.4, hcol=(110, 90, 140), rim=0.25, rcol=(170, 140, 220))
    c.stroke([(bx_ - r * 0.15, by_ - r * 0.68), (bx_ - r * 0.1, by_ - r * 0.95)], 3.4, (34, 28, 44))
    # near arm: holding Ivy's notebook (daisy on the cover)
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    wx, wy = b.P(*b.wrist_n)
    nb = Sh([rot_pts([(wx - 6, wy - 10), (wx + 44, wy - 10), (wx + 44, wy + 52), (wx - 6, wy + 52)], -14, wx, wy)])
    c.ink(nb, (60, 120, 80), lw=2.8, shade=0.4, hi=0.4)
    dcx, dcy = rot_pts([(wx + 19, wy + 20)], -14, wx, wy)[0]
    for k in range(8):
        a = math.radians(k * 45)
        c.ink(ell(dcx + math.cos(a) * 7, dcy + math.sin(a) * 7, 5, 2.6, k * 45), (255, 255, 255), lw=1.0)
    c.ink(ell(dcx, dcy, 3.4, 3.4), (255, 210, 60), lw=1.0)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.6, w1=7.8, cuff=7.0), (70, 54, 86), lw=3.0, shade=0.5, sw=10, hi=0.3)
    b.hand(True, "hold", size=0.95)
    return finish_sprite(c, name, flip=True)


# =========================================================================== shared room bits
WALL_PINK = (206, 74, 150)
WALL_PINK_D = (150, 46, 120)
BRICK = (176, 70, 88)
MORTAR = (96, 36, 76)
LAYOUT = {}   # room id -> dict(walkable=[px...], hotspots={(name, n): dict(box=(x0,y0,x1,y1), stand=(x,y))}, entries=...)


def grunge_wall(sub, w, h, base, seed=0, chips=5, stains=4, cracks=3, floor_y=None, posters=(), top_dark=True,
                brick=BRICK, mortar=MORTAR):
    """Full grunge treatment for a flat wall canvas of size w x h."""
    rng = random.Random(seed)
    plaster_wall(sub, hi_col(base, 0.06), shade_col(base, 0.86), seed=seed, w=w, h=h)
    for _ in range(stains):
        stain(sub, rng.uniform(0.05, 0.95) * w, rng.uniform(0.05, 0.6) * h, rng.uniform(30, 90), (70, 20, 60),
              rng.uniform(0.12, 0.22), drips=rng.randint(0, 3), seed=rng.randint(0, 999))
    for _ in range(chips):
        chip(sub, rng.uniform(0.05, 0.95) * w, rng.uniform(0.08, 0.85) * h, rng.uniform(26, 60), brick, mortar, base,
             seed=rng.randint(0, 999))
    for _ in range(cracks):
        crack(sub, rng.uniform(0.05, 0.95) * w, rng.uniform(0.0, 0.3) * h, rng.uniform(60, 160), rng.uniform(60, 120),
              shade_col(base, 0.35), 2.0, seed=rng.randint(0, 999), branches=2, opacity=0.7)
    if floor_y is not None:
        grime_gradient(sub, 0, w, floor_y, 110, (50, 14, 50), 0.35)
        scuffs(sub, 0, w, floor_y - 10, int(w / 40), seed=seed + 3, opacity=0.25, spread=60)
    if top_dark:
        sub.ink(rect(0, 0, w, h * 0.25), ("vy", 0, h * 0.25, (40, 14, 60), (40, 14, 60, 0)), lw=0, shade=0, hi=0, ao=0,
                tex=0, wob=0, opacity=0.35)


def skirting(sub, w, y, h=26, col=(110, 50, 90)):
    sub.ink(rect(-5, y - h, w + 5, y + 2), col, lw=2.6, shade=0.3, sw=8, hi=0.4, hw=4, tex=0.12, wob=0.5)


def warm_window_glow(c, quad, col=(120, 160, 255), strength=0.25):
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    c.glow2(sum(xs) / 4, sum(ys) / 4, (max(xs) - min(xs)) * 0.9, col, strength)


def box_px(x0, y0, x1, y1):
    return (x0, y0, x1, y1)


# =========================================================================== 1. Dex's dorm room (214)
def paint_dex_room():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(-0.4, -0.92), lw=3.4, seed=214)
    y_top, y_bot = 762, 975
    vp = (900, vp_for_walk(y_top, y_bot))
    R = Room(c, vp, (430, 250, 1430, 680), fc=1000)
    Wb, Hb = R.Wb, R.Hb
    rng = random.Random(214)

    # ---------------- ceiling: stained concrete slab with seams
    def ceil(sub):
        w, h = sub.w, sub.h
        plaster_wall(sub, (96, 56, 110), (70, 40, 92), seed=5, w=w, h=h)
        for k in range(1, 8):
            y = sub.by(k * 110)
            sub.stroke([(0, y), (w, y)], 3, (40, 20, 50), opacity=0.5, taper=(0, 0))
        for _ in range(5):
            stain(sub, rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 110), (40, 16, 40), 0.25, 0, rng.randint(0, 99))
        cobweb(sub, 4, h - 4, 120, "bl", opacity=0.4)
    # ---------------- left wall: window above the bed, corkboard, posters
    def left(sub):
        w, h = sub.w, sub.h
        grunge_wall(sub, w, h, mix(WALL_PINK, (150, 50, 130), 0.3), seed=11, chips=4, stains=3, floor_y=h)
        skirting(sub, w, h)
        # window (Z 40..230, Y 170..370)
        x0, x1 = sub.ax(230), sub.ax(40)
        y0, y1 = sub.by(370), sub.by(170)
        sub.ink(rect(x0 - 22, y0 - 22, x1 + 22, y1 + 22), (230, 200, 220), lw=3.0, shade=0.4, hi=0.3)
        night_sky(sub, x0, y0, x1, y1, seed=3)
        for xx in (x0 + (x1 - x0) / 2,):
            sub.ink(rect(xx - 7, y0, xx + 7, y1), (230, 200, 220), lw=2.6, shade=0.3)
        sub.ink(rect(x0, y0 + (y1 - y0) * 0.45 - 7, x1, y0 + (y1 - y0) * 0.45 + 7), (230, 200, 220), lw=2.6, shade=0.3)
        sub.stroke([(x0 + 20, y1 - 20), (x0 + 90, y0 + 20)], 10, (255, 255, 255), opacity=0.12)
        sub.ink(rect(x0 - 40, y1 + 14, x1 + 40, y1 + 36), (236, 206, 226), lw=2.8, shade=0.5, sw=8, hi=0.3)
        # curtains (teal, droopy)
        for side in (0, 1):
            cx0 = x0 - 70 if side == 0 else x1 - 30
            cx1 = x0 + 40 if side == 0 else x1 + 80
            pts = [(cx0, y0 - 40), (cx1, y0 - 40), (cx1 - (20 if side == 0 else -20), y1 + 30), (cx0 + 6, y1 + 46)]
            sub.ink(blob(pts, 1), (40, 170, 170), lw=3.0, shade=0.55, sw=30, hi=0.4, rim=0.2)
            for k in range(1, 4):
                fx = cx0 + (cx1 - cx0) * k / 4
                sub.stroke([(fx, y0 - 30), (fx + rng.uniform(-8, 8), y1 + 30)], 2.2, (20, 100, 110), opacity=0.7)
        sub.ink(rect(x0 - 90, y0 - 50, x1 + 100, y0 - 38), (90, 70, 90), lw=2.4, shade=0.3)
        # corkboard with notes (Z 260..400)
        cx0, cx1 = sub.ax(420), sub.ax(270)
        cy0, cy1 = sub.by(330), sub.by(210)
        sub.ink(rect(cx0 - 10, cy0 - 10, cx1 + 10, cy1 + 10), (120, 70, 50), lw=2.8, shade=0.3)
        sub.ink(rect(cx0, cy0, cx1, cy1), (200, 150, 100), lw=2.0, shade=0.2, tex=0.4)
        for k in range(6):
            nx_, ny_ = rng.uniform(cx0 + 20, cx1 - 40), rng.uniform(cy0 + 15, cy1 - 40)
            sub.ink(Sh([rot_pts([(nx_, ny_), (nx_ + 46, ny_), (nx_ + 46, ny_ + 40), (nx_, ny_ + 40)], rng.uniform(-10, 10), nx_, ny_)]),
                    rng.choice([(255, 240, 140), (160, 230, 255), (255, 170, 200), (250, 250, 240)]), lw=1.8, shade=0.2)
            sub.ink(ell(nx_ + 22, ny_ + 3, 4, 4), (220, 40, 60), lw=1.4, shade=0, hi=0.5)
        # pennant
        px0, py0 = sub.ax(640), sub.by(330)
        sub.ink(Sh([[(px0, py0), (px0 + 280, py0 + 40), (px0, py0 + 80)]]), (240, 200, 60), lw=3, shade=0.4, sw=20)
        sub.text(px0 + 100, py0 + 40, "GO POSSUMS", 18, (120, 30, 80), angle=-8)

    # ---------------- right wall: the door to the hallway
    def right(sub):
        w, h = sub.w, sub.h
        grunge_wall(sub, w, h, hi_col(WALL_PINK, 0.04), seed=12, chips=3, stains=3, floor_y=h)
        skirting(sub, w, h)
        x0, x1 = sub.ax(150), sub.ax(330)
        y0, y1 = sub.by(290), sub.by(0)
        def sign(cc, cx, cy):
            poster_rect = wonky(cx - 50, cy - 40, cx + 50, cy + 20, 2, rng)
            cc.ink(poster_rect, (255, 236, 120), lw=2.2, shade=0.2)
            cc.text(cx, cy - 22, "KNOCK", 16, (150, 40, 60))
            cc.text(cx, cy + 2, "FIRST!", 16, (150, 40, 60))
        flat_door(sub, x0, y0, x1, y1, (66, 150, 160), frame=(232, 196, 214), knob="L", sign=sign, seed=4)
        # light switch, coat hooks with a hoodie
        sub.ink(rrect(sub.ax(370) - 12, sub.by(150) - 20, sub.ax(370) + 12, sub.by(150) + 20, 4), (240, 230, 220), lw=2.2)
        sub.ink(rect(sub.ax(60) - 50, sub.by(250) - 8, sub.ax(60) + 50, sub.by(250) + 8), (120, 70, 50), lw=2.4)
        hood = [(sub.ax(60) - 30, sub.by(250)), (sub.ax(60) + 30, sub.by(250)), (sub.ax(60) + 50, sub.by(80)),
                (sub.ax(60) - 46, sub.by(70))]
        sub.ink(blob(hood, 2), (120, 60, 170), lw=3, shade=0.55, sw=30, hi=0.3)
        poster(sub, sub.ax(470), sub.by(260), 120, 160, (40, 40, 60),
               lambda p, w_, h_: (p.ink(ell(w_ / 2, h_ * 0.45, w_ * 0.3, w_ * 0.3), (255, 90, 150), lw=2),
                                  p.text(w_ / 2, h_ * 0.85, "MOON PIGS", 14, (255, 230, 120))), angle=4, seed=8, peel="br")

    # ---------------- floor: worn planks
    def floor(sub):
        w, h = sub.w, sub.h
        planks(sub, (156, 88, 84), 0, 0, w, h, pw=38 * sub.density, seed=21, vertical=True)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.5, seed=214)

    # ---------------- back wall (screen space)
    x0, y0, x1, y1 = R.back
    grunge_wall(c, 0, 0, WALL_PINK, seed=13, chips=0, stains=0, cracks=0, top_dark=False) if False else None
    sub_w, sub_h = x1 - x0, y1 - y0

    def back(sub):
        grunge_wall(sub, sub_w, sub_h, WALL_PINK, seed=13, chips=6, stains=4, cracks=3, floor_y=sub_h)
        skirting(sub, sub_w, sub_h)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=13)
    R.ao(0.45)
    R.edges(w=4.0)
    # ceiling beams
    for z0 in (30, 250):
        R.ink_box(0, Wb, Hb - 30, Hb + 1, z0, z0 + 34, (130, 76, 112), side=(90, 46, 86), seed=z0)

    P = R.pt
    # band poster above the dresser, calendar, clock, pennant
    poster(c, *P(250, 300), 130, 170, (40, 30, 70),
           lambda p, w_, h_: (p.ink(rrect(w_ * 0.2, h_ * 0.25, w_ * 0.8, h_ * 0.62, 10), (250, 190, 70), lw=2.4),
                              p.ink(ell(w_ * 0.38, h_ * 0.4, 5, 6), (40, 20, 30), lw=0),
                              p.ink(ell(w_ * 0.62, h_ * 0.4, 5, 6), (40, 20, 30), lw=0),
                              p.stroke([(w_ * 0.35, h_ * 0.52), (w_ * 0.5, h_ * 0.48), (w_ * 0.65, h_ * 0.52)], 2.4),
                              p.text(w_ / 2, h_ * 0.12, "THE GRUMPY", 12, (255, 236, 120)),
                              p.text(w_ / 2, h_ * 0.75, "TOASTERS", 15, (255, 120, 170)),
                              p.text(w_ / 2, h_ * 0.9, "LIVE & CRISPY", 8, (200, 220, 255), "Bold")),
           angle=-3, seed=2, peel="tr")
    poster(c, *P(870, 330), 90, 110, (250, 248, 236),
           lambda p, w_, h_: (p.ink(rect(0, 0, w_, h_ * 0.25), (220, 60, 80), lw=0),
                              p.text(w_ / 2, h_ * 0.13, "SEPT", 12, (255, 255, 255)),
                              [p.stroke([(w_ * (0.12 + (k % 5) * 0.18), h_ * (0.4 + (k // 5) * 0.18)),
                                         (w_ * (0.2 + (k % 5) * 0.18), h_ * (0.48 + (k // 5) * 0.18))], 2.0, (200, 40, 60))
                               for k in range(11)]), angle=3, seed=3)
    # clock
    cx_, cy_ = P(960, 360)
    c.ink(ell(cx_, cy_, 30, 30), (250, 240, 220), lw=3.2, shade=0.4, sw=10, hi=0.3)
    c.stroke([(cx_, cy_), (cx_, cy_ - 20)], 3)
    c.stroke([(cx_, cy_), (cx_ + 14, cy_ + 6)], 3)
    # shelf above the desk with books, plant and trophy
    sx0, sy_ = P(540, 260)
    sx1, _ = P(790, 260)
    book_row(c, sx0 + 6, sx0 + 150, sy_ - 4, 40, 64, rng, BOOK_COLS)
    c.ink(rrect(sx0 + 175, sy_ - 34, sx0 + 215, sy_ - 2, 6), (210, 90, 70), lw=2.6, shade=0.4)
    for k in range(6):
        a = math.radians(-150 + k * 24)
        c.ink(ell(sx0 + 195 + math.cos(a) * 18, sy_ - 40 + math.sin(a) * 16, 12, 5, math.degrees(a)), (60, 180, 90), lw=2,
              shade=0.4)
    shelf(c, sx0, sx1, sy_, 18, (150, 90, 70))
    # string lights across the back wall
    lights = string_lights2(c, [P(0, 420), P(250, 405), P(500, 420), P(750, 405), P(1000, 420)], sag=36, seed=5)
    # pipe along the top of the back wall + down the right corner, with drips
    pipe(c, [P(0, 395), P(Wb - 20, 395), P(Wb - 20, 0)], w=24, col=(110, 170, 180), brackets=[P(300, 395), P(700, 395)])
    c.ink(rect(*P(Wb - 60, 410), *P(Wb - 40, 380)), (90, 90, 110), lw=2)
    stain(c, *P(Wb - 70, 360), 40, (60, 20, 60), 0.2, 2, 9)

    # ---------------- furniture (3-D boxes, back to front)
    WOOD = (150, 90, 70)
    for fp in ((190, 370, 0, 85), (400, 490, 0, 82), (520, 790, 0, 108), (600, 690, 120, 198), (0, 175, 124, 412)):
        R.contact(*fp, strength=0.5)
    # dresser (left of back wall)
    f = R.ink_box(190, 370, 0, 150, 0, 85, (190, 110, 90), seed=1)
    fr = f["front"]
    for k in range(3):
        yy0 = 10 + k * 46
        q = [R.pt(200, yy0 + 40, 85), R.pt(360, yy0 + 40, 85), R.pt(360, yy0 + 2, 85), R.pt(200, yy0 + 2, 85)]
        c.ink(Sh([q]), (176, 98, 82), lw=2.4, shade=0.3, hi=0.3)
        hx_, hy_ = R.pt(280, yy0 + 22, 85)
        c.ink(rrect(hx_ - 14, hy_ - 4, hx_ + 14, hy_ + 4, 3), (236, 196, 90), lw=2)
    # sock hanging out of a drawer
    sx_, sy2 = R.pt(330, 104, 86)
    c.ink(blob([(sx_, sy2), (sx_ + 22, sy2), (sx_ + 26, sy2 + 40), (sx_ + 40, sy2 + 52), (sx_ + 20, sy2 + 60), (sx_ + 6, sy2 + 40)], 2),
          (240, 240, 230), lw=2.4, shade=0.4)
    # fishbowl + trophy on the dresser
    bx_, by_ = R.pt(240, 150, 40)
    c.ink(ell(bx_, by_ - 30, 34, 30), (150, 220, 240, 180), lw=2.8, shade=0.3, hi=0.6, hw=6)
    c.ink(ell(bx_ + 6, by_ - 22, 9, 6), (255, 140, 40), lw=1.8)
    tx_, ty_ = R.pt(330, 150, 40)
    c.ink(Sh([[(tx_ - 18, ty_ - 60), (tx_ + 18, ty_ - 60), (tx_ + 8, ty_ - 30), (tx_ - 8, ty_ - 30)]]), (240, 196, 70), lw=2.6,
          shade=0.4, hi=0.6, hw=4)
    c.ink(rect(tx_ - 12, ty_ - 30, tx_ + 12, ty_ - 4), (120, 70, 60), lw=2.4)
    # mini fridge + lava lamp
    R.ink_box(400, 490, 0, 106, 0, 82, (236, 232, 236), seed=2)
    mx_, my_ = R.pt(445, 60, 82)
    for k, col in enumerate([(255, 80, 120), (60, 200, 220), (255, 220, 80)]):
        c.ink(ell(mx_ - 20 + k * 18, my_ - 10 + (k % 2) * 12, 7, 7), col, lw=2)
    lx_, ly_ = R.pt(445, 106, 40)
    c.ink(Sh([[(lx_ - 10, ly_), (lx_ + 10, ly_), (lx_ + 6, ly_ - 18), (lx_ - 6, ly_ - 18)]]), (90, 80, 110), lw=2.4)
    c.ink(blob([(lx_ - 6, ly_ - 18), (lx_ + 6, ly_ - 18), (lx_ + 12, ly_ - 56), (lx_ + 4, ly_ - 76), (lx_ - 4, ly_ - 76),
                (lx_ - 12, ly_ - 56)], 2), (255, 110, 190), lw=2.6, shade=0.3, hi=0.6, hw=4)
    c.ink(ell(lx_, ly_ - 46, 5, 7), (255, 220, 120), lw=0)
    c.glow2(lx_, ly_ - 46, 120, (255, 90, 190), 0.35)
    # desk with drawer unit, laptop, lamp, the letter
    R.ink_box(520, 790, 126, 138, 0, 108, WOOD, top=(186, 120, 90), seed=3)
    for lxx in (530, 676):
        R.ink_box(lxx, lxx + 14, 0, 126, 92, 106, shade_col(WOOD, 0.8), seed=4)
    R.ink_box(690, 790, 0, 126, 4, 106, (170, 100, 80), seed=5)
    for k in range(2):
        q = [R.pt(698, 116 - k * 58, 106), R.pt(782, 116 - k * 58, 106), R.pt(782, 64 - k * 58, 106), R.pt(698, 64 - k * 58, 106)]
        c.ink(Sh([q]), (180, 110, 86), lw=2.2, shade=0.3, hi=0.3)
        hx_, hy_ = R.pt(740, 92 - k * 58, 106)
        c.ink(rrect(hx_ - 12, hy_ - 4, hx_ + 12, hy_ + 4, 3), (236, 196, 90), lw=2)
    # the letter from Uncle Vic, taped to the drawer
    lx_, ly_ = R.pt(712, 112, 107)
    c.ink(Sh([rot_pts([(lx_, ly_), (lx_ + 56, ly_), (lx_ + 56, ly_ + 38), (lx_, ly_ + 38)], -6, lx_, ly_)]), (252, 248, 236),
          lw=2.2, shade=0.2)
    c.stroke([(lx_ + 2, ly_ + 2), (lx_ + 28, ly_ + 22), (lx_ + 54, ly_ - 4)], 1.6, (180, 160, 150))
    c.ink(rect(lx_ + 18, ly_ - 6, lx_ + 38, ly_ + 4), (236, 230, 200, 210), lw=0)
    c.ink(ell(lx_ + 36, ly_ + 26, 6, 6), (220, 40, 60), lw=1.4)
    # laptop
    q = [R.pt(560, 138, 30), R.pt(660, 138, 30), R.pt(660, 138, 86), R.pt(560, 138, 86)]
    c.ink(Sh([q]), (80, 80, 100), lw=2.4, shade=0.2)
    scr = [R.pt(560, 220, 26), R.pt(660, 220, 26), R.pt(660, 138, 30), R.pt(560, 138, 30)]
    c.ink(Sh([scr]), (60, 60, 80), lw=2.6)
    inner = [R.pt(566, 214, 26.5), R.pt(654, 214, 26.5), R.pt(654, 144, 29.5), R.pt(566, 144, 29.5)]
    c.ink(Sh([inner]), (90, 230, 230), lw=1.6, shade=0.2, hi=0.4)
    hx_, hy_ = R.pt(610, 186, 27)
    c.ink(blob([(hx_, hy_ + 12), (hx_ - 16, hy_ - 2), (hx_ - 10, hy_ - 12), (hx_, hy_ - 6), (hx_ + 10, hy_ - 12), (hx_ + 16, hy_ - 2)], 1),
          (255, 80, 140), lw=1.6, shade=0.2)
    tx_, ty_ = R.pt(610, 158, 28)
    c.text(tx_, ty_, "SPEED DATERS", 7, (30, 60, 80))
    c.glow2(*R.pt(610, 180, 30), 150, (90, 230, 230), 0.3)
    # desk lamp
    bx_, by_ = R.pt(760, 138, 40)
    c.ink(ell(bx_, by_, 22, 7), (60, 160, 120), lw=2.4)
    c.stroke([(bx_, by_), (bx_ - 10, by_ - 50), (bx_ - 34, by_ - 70)], 5, INK)
    c.stroke([(bx_, by_), (bx_ - 10, by_ - 50), (bx_ - 34, by_ - 70)], 2.4, (60, 160, 120))
    c.ink(Sh([rot_pts([(bx_ - 60, by_ - 74), (bx_ - 20, by_ - 90), (bx_ - 10, by_ - 64), (bx_ - 46, by_ - 50)], 0, bx_, by_)]),
          (60, 160, 120), lw=2.6, shade=0.4, hi=0.4)
    c.light_cone((bx_ - 30, by_ - 56), (bx_ - 140, by_ + 8), (bx_ + 20, by_ + 14), strength=0.45, blur_px=12)
    # mug + papers
    mx_, my_ = R.pt(600, 138, 96)
    c.ink(rrect(mx_ - 12, my_ - 28, mx_ + 12, my_, 4), (240, 90, 120), lw=2.4, shade=0.4)
    for k in range(3):
        px_, py_ = R.pt(680 - k * 12, 139, 70 + k * 6)
        c.ink(Sh([rot_pts([(px_ - 24, py_ - 6), (px_ + 24, py_ - 6), (px_ + 24, py_ + 6), (px_ - 24, py_ + 6)], k * 8 - 8, px_, py_)]),
              (248, 246, 236), lw=1.8)
    # desk chair (pulled out)
    R.ink_box(600, 690, 56, 70, 120, 196, (60, 170, 180), seed=6)
    R.ink_box(606, 684, 70, 150, 186, 198, (60, 170, 180), seed=7)
    cx_, cy_ = R.pt(645, 30, 160)
    c.stroke([(cx_, cy_ - 30), (cx_, cy_ + 10)], 6, INK)
    for dx in (-36, 0, 36):
        c.stroke([(cx_, cy_ + 10), (cx_ + dx, cy_ + 22)], 5, INK)
        c.ink(ell(cx_ + dx, cy_ + 24, 6, 5), (40, 30, 50), lw=0)
    # mirror (leaning on the back wall, right)
    mq = R.box(880, 960, 30, 330, 0, 14)
    c.ink(Sh([mq["front"]]), (236, 196, 90), lw=3.2, shade=0.4, hi=0.5)
    inner = [R.pt(890, 318, 14.5), R.pt(950, 318, 14.5), R.pt(950, 42, 14.5), R.pt(890, 42, 14.5)]
    c.ink(Sh([inner]), ("v", (190, 230, 240), (120, 150, 200)), lw=2.2, shade=0.2, hi=0)
    c.stroke([R.pt(900, 120, 15), R.pt(930, 290, 15)], 8, (255, 255, 255), opacity=0.35)
    c.stroke([R.pt(915, 80, 15), R.pt(940, 200, 15)], 4, (255, 255, 255), opacity=0.3)
    post = R.pt(940, 300, 15)
    c.ink(Sh([rot_pts([(post[0] - 16, post[1]), (post[0] + 16, post[1]), (post[0] + 16, post[1] + 22), (post[0] - 16, post[1] + 22)], 8,
                      post[0], post[1])]), (255, 236, 120), lw=1.8)
    # bed along the left wall
    R.ink_box(0, 175, 0, 44, 140, 410, (110, 60, 120), seed=8)            # frame
    R.ink_box(0, 175, 0, 160, 124, 140, (130, 70, 140), seed=9)           # headboard
    R.ink_box(0, 175, 0, 86, 396, 412, (130, 70, 140), seed=10)           # footboard
    f = R.ink_box(4, 171, 40, 66, 140, 396, (240, 236, 230), seed=11)     # mattress
    # blanket: rumpled teal duvet hanging over the side
    top = R.box(4, 171, 40, 72, 200, 396)
    t = top["top"]
    blanket = [t[0], t[1], t[2], R.pt(178, 30, 396), R.pt(178, 26, 300), R.pt(178, 34, 200), t[3]]
    blanket = [t[0], t[1], R.pt(178, 70, 396), R.pt(180, 30, 396), R.pt(180, 26, 300), R.pt(180, 36, 200), R.pt(171, 72, 200)]
    c.ink(blob([R.pt(4, 74, 200), R.pt(171, 76, 200), R.pt(182, 40, 210), R.pt(184, 22, 300), R.pt(180, 30, 400),
                R.pt(171, 74, 404), R.pt(4, 72, 400)], 2), (40, 160, 170), lw=3.4, shade=0.55, sw=30, hi=0.4, rim=0.2)
    for k in range(4):
        a = R.pt(20 + k * 40, 74, 220 + k * 30)
        b_ = R.pt(60 + k * 30, 74, 330 + k * 15)
        c.stroke([a, b_], 2.4, (20, 100, 120), opacity=0.7)
    # pillow
    c.ink(blob([R.pt(20, 70, 146), R.pt(160, 70, 146), R.pt(160, 96, 150), R.pt(140, 98, 186), R.pt(30, 98, 190), R.pt(14, 90, 170)], 2),
          (250, 246, 240), lw=3, shade=0.4, sw=10)
    # floor rug
    rug = [R.pt(330 + 260 * math.cos(a), 0, 380 + 120 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    c.ink(Sh([rug]), (210, 60, 120), lw=3.2, shade=0.2, hi=0.1, tex=0.25)
    for k, col in ((0.78, (40, 190, 190)), (0.55, (250, 200, 80)), (0.32, (60, 30, 90))):
        rr = [R.pt(330 + 260 * k * math.cos(a), 0, 380 + 120 * k * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
        c.ink(Sh([rr]), col, lw=2.0, shade=0.1, hi=0.0, tex=0.25)
    # clutter on the floor
    pz = R.box(200, 290, 0, 8, 430, 500)
    c.ink(Sh([pz["top"]]), (220, 180, 120), lw=2.6, shade=0.2)
    c.ink(Sh([pz["front"]]), (190, 150, 100), lw=2.2)
    px_, py_ = R.pt(245, 8, 465)
    c.text(px_, py_, "PIZZA", 13, (200, 50, 50), angle=4)
    for (X, Z, col) in ((560, 440, (240, 240, 230)), (840, 300, (120, 60, 170)), (220, 560, (250, 250, 240))):
        x_, y_ = R.pt(X, 0, Z)
        k = R.k(Z)
        c.ink(blob([(x_ - 22 * k, y_), (x_ - 8 * k, y_ - 14 * k), (x_ + 18 * k, y_ - 10 * k), (x_ + 26 * k, y_ + 2 * k),
                    (x_ + 4 * k, y_ + 8 * k)], 2), col, lw=2.6, shade=0.5, sw=8)
    # crumpled paper balls near the desk
    for X, Z in ((800, 200), (770, 240), (470, 160)):
        x_, y_ = R.pt(X, 8, Z)
        c.ink(ell(x_, y_, 11, 9), (246, 244, 236), lw=2.2, shade=0.4)
        c.stroke([(x_ - 6, y_ - 2), (x_ + 2, y_ + 3), (x_ + 6, y_ - 4)], 1.2, (150, 140, 150))
    # backpack slumped against the dresser
    x_, y_ = R.pt(390, 0, 130)
    c.ink(blob([(x_ - 36, y_), (x_ - 40, y_ - 60), (x_ - 20, y_ - 84), (x_ + 22, y_ - 84), (x_ + 38, y_ - 56), (x_ + 36, y_)], 2),
          (230, 120, 40), lw=3, shade=0.55, sw=20, hi=0.3)
    c.ink(rrect(x_ - 22, y_ - 40, x_ + 22, y_ - 10, 6), (210, 100, 30), lw=2.4)

    # trash can by the desk with paper overflowing
    R.contact(800, 850, 120, 170, 0.5)
    tc = R.box(800, 850, 0, 70, 120, 170)
    c.ink(Sh([tc["front"]]), (90, 170, 120), lw=2.8, shade=0.4, hi=0.3)
    if "left" in tc:
        c.ink(Sh([tc["left"]]), (60, 120, 90), lw=2.8, shade=0.3)
    c.ink(Sh([tc["top"]]), (30, 20, 40), lw=2.6)
    for k in range(4):
        x_, y_ = R.pt(810 + k * 12, 74 + (k % 2) * 8, 140 + k * 6)
        c.ink(ell(x_, y_, 10, 8), (246, 244, 236), lw=2.0, shade=0.4)
    # guitar leaning on the right wall near the back
    gx, gy = R.pt(Wb - 22, 0, 60)
    gt = R.pt(Wb - 10, 210, 40)
    c.stroke([(gx - 6, gy - 120), gt], 14, INK, taper=(0, 0))
    c.stroke([(gx - 6, gy - 120), gt], 8, (120, 70, 50), taper=(0, 0))
    c.ink(rrect(gt[0] - 10, gt[1] - 26, gt[0] + 10, gt[1] + 4, 4), (60, 40, 40), lw=2.4)
    body = blob([(gx - 50, gy - 6), (gx - 58, gy - 60), (gx - 34, gy - 100), (gx - 10, gy - 92), (gx + 12, gy - 120),
                 (gx + 30, gy - 96), (gx + 26, gy - 40), (gx + 8, gy)], 2)
    c.ink(body, (230, 120, 40), lw=3.0, shade=0.5, sw=24, hi=0.4, rim=0.2)
    c.ink(ell(gx - 14, gy - 58, 12, 12), (40, 20, 30), lw=2)
    c.stroke([(gx - 6, gy - 120), (gx - 18, gy - 20)], 1.2, (240, 240, 220), opacity=0.8)
    # laundry pile by the door
    lp = R.pt(Wb - 60, 0, 380)
    k = R.k(380)
    for j, col in enumerate([(80, 60, 160), (250, 200, 80), (230, 80, 110), (60, 170, 170)]):
        ox_ = (j - 1.5) * 20 * k
        c.ink(blob([(lp[0] + ox_ - 40 * k, lp[1]), (lp[0] + ox_ - 30 * k, lp[1] - (30 + j * 6) * k), (lp[0] + ox_, lp[1] - (44 + j * 4) * k),
                    (lp[0] + ox_ + 34 * k, lp[1] - 24 * k), (lp[0] + ox_ + 40 * k, lp[1])], 2), col, lw=3.0, shade=0.55, sw=14 * k,
              hi=0.3)
    # stack of books on the floor + sneakers
    bx_, by_ = R.pt(860, 0, 240)
    for j in range(4):
        col = BOOK_COLS[j * 2 % len(BOOK_COLS)]
        c.ink(Sh([rot_pts([(bx_ - 34, by_ - 14 - j * 14), (bx_ + 34, by_ - 14 - j * 14), (bx_ + 34, by_ - j * 14), (bx_ - 34, by_ - j * 14)],
                          (j % 2) * 6 - 3, bx_, by_ - j * 14)]), col, lw=2.4, shade=0.4, hi=0.3)

    # ---------------- ceiling stuff: cables, pendant lamp, cobwebs
    cable(c, R.pt(0, Hb, 120), R.pt(520, Hb, 280), sag=40, w=7, col=(50, 40, 80))
    cable(c, R.pt(520, Hb, 280), R.pt(Wb, Hb, 160), sag=70, w=6, col=(40, 120, 130))
    hanging_cable(c, R.pt(840, Hb, 120), 120, sway=18, w=5, col=(60, 40, 90), seed=3)
    lamp_x, lamp_y = R.pt(520, Hb - 90, 280)
    ceil_pt = R.pt(520, Hb, 280)
    pendant_lamp(c, lamp_x, ceil_pt[1], lamp_y, w=130, col=(240, 200, 60), cone_to=1000, cone_w=420, cone_strength=0.2)
    cobweb(c, *R.pt(0, Hb, 0), 110, "tl", opacity=0.5)
    cobweb(c, *R.pt(Wb, Hb, 0), 90, "tr", opacity=0.45)
    cobweb(c, *R.pt(Wb, 0, 0), 60, "tr", opacity=0.3)
    hanging_web(c, *R.pt(300, Hb, 30), 50)

    # ---------------- lighting
    lx, ly = lamp_x, lamp_y
    room_grade(c, lights=[(lx, ly + 260, 760, 0.5), (1150, 560, 300, 0.4), (R.pt(445, 140, 40)[0], 560, 260, 0.35, (255, 120, 200)),
                          (R.pt(0, 270, 130)[0], 380, 260, 0.25, (140, 160, 255))],
               ambient=0.98, vign=0.55, top_dark=0.3, bottom_dark=0.3)
    c.glow2(lx, ly + 30, 220, GLOW, 0.35)
    c.painterly(0.05)

    # ---------------- foreground (out of focus, outside the walkable band)
    def fg(sub):
        fg_table_edge(sub, 1480, 2000, 1010, 120)
        fg_bottles(sub, 1560, 1030, 4, 1.0, seed=3)
        fg_chair_back(sub, 1880, 880, 300, 320)
        fg_chair_back(sub, 110, 900, 360, 300)
        fg_plant(sub, 300, 1110, 260, seed=4)
        fg_cable(sub, [(-20, 1040), (400, 1062), (800, 1074), (1300, 1100)], 18)
        fg_lamp_top(sub, 1540, 70, 360)
    fg_paint(c, fg, blur_px=3)

    c.save_png("bg_dex_room.png")


# =========================================================================== shared room props
def panel_light(c, R, X0, X1, Z0, Z1, on=True, cone=0.22, floor_y=1000, flicker=False):
    """Fluorescent ceiling panel (box under the ceiling) with glow and a soft light cone."""
    Hb = R.Hb
    f = R.box(X0, X1, Hb - 14, Hb, Z0, Z1)
    for name in ("left", "right", "front"):
        if name in f:
            c.ink(Sh([f[name]]), (200, 196, 210), lw=2.4, shade=0.3, hi=0.2, tex=0.05)
    face = f.get("bottom")
    if face:
        col = (250, 250, 230) if on else (150, 150, 170)
        c.ink(Sh([face]), col, lw=2.6, shade=0.15, hi=0, ao=0, tex=0.02)
        for k in (0.33, 0.66):
            a = R.pt(X0 + (X1 - X0) * k, Hb - 14, Z0)
            b_ = R.pt(X0 + (X1 - X0) * k, Hb - 14, Z1)
            c.stroke([a, b_], 1.6, (200, 196, 210), taper=(0, 0))
        if on:
            cx = sum(p[0] for p in face) / 4
            cy = sum(p[1] for p in face) / 4
            w = max(p[0] for p in face) - min(p[0] for p in face)
            c.glow2(cx, cy + 10, w * 1.1, (255, 250, 220), 0.45 if not flicker else 0.25, sy=0.5)
            if cone:
                c.light_cone((cx, cy), (cx - w * 1.2, floor_y), (cx + w * 1.2, floor_y), (255, 246, 210), cone, 40)


def exit_sign(c, x, y, w=90, text="EXIT", col=(60, 230, 120)):
    c.ink(rrect(x - w / 2, y - 18, x + w / 2, y + 18, 4), (30, 40, 40), lw=2.6, shade=0.2)
    c.text(x, y, text, 15, col)
    c.glow2(x, y, w * 1.3, col, 0.35)


def vending_machine(c, R, X0, X1, Z0, Z1, H=300, col=(220, 50, 70), seed=0):
    rng = random.Random(seed)
    f = R.ink_box(X0, X1, 0, H, Z0, Z1, col, side=shade_col(col, 0.6), seed=seed)
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    w, h = x1 - x0, y1 - y0
    gx0, gy0, gx1, gy1 = x0 + w * 0.08, y0 + h * 0.16, x0 + w * 0.68, y0 + h * 0.74
    c.ink(rect(gx0, gy0, gx1, gy1), (40, 50, 80), lw=2.6, shade=0.2)
    for r_ in range(5):
        yy = gy0 + (gy1 - gy0) * (r_ + 0.8) / 5.3
        c.stroke([(gx0 + 4, yy + 6), (gx1 - 4, yy + 6)], 2.2, (150, 150, 170), taper=(0, 0))
        for k in range(4):
            xx = gx0 + 10 + k * (gx1 - gx0 - 20) / 4
            cc = rng.choice([(255, 210, 60), (60, 200, 220), (255, 120, 160), (140, 230, 100), (250, 250, 240)])
            c.ink(rrect(xx, yy - 16, xx + (gx1 - gx0) / 4 - 10, yy + 5, 3), cc, lw=1.6, shade=0.3)
    c.stroke([(gx0 + 8, gy1 - 10), (gx0 + (gx1 - gx0) * 0.4, gy0 + 10)], 10, (255, 255, 255), opacity=0.15)
    c.ink(rect(x0 + w * 0.74, y0 + h * 0.2, x0 + w * 0.92, y0 + h * 0.5), (60, 60, 70), lw=2.2)
    for k in range(3):
        for j in range(2):
            c.ink(ell(x0 + w * (0.79 + j * 0.08), y0 + h * (0.25 + k * 0.08), 4, 4), (230, 230, 230), lw=1.2)
    c.ink(rect(x0 + w * 0.1, y0 + h * 0.8, x0 + w * 0.66, y0 + h * 0.9), (30, 30, 40), lw=2.2)
    c.ink(rrect(x0 + w * 0.06, y0 + h * 0.02, x1 - w * 0.06, y0 + h * 0.12, 4), (255, 236, 120), lw=2.2)
    c.text((x0 + x1) / 2, y0 + h * 0.07, "SNAX!", 18, (200, 40, 60))
    c.glow2((gx0 + gx1) / 2, (gy0 + gy1) / 2, w * 1.1, (120, 200, 255), 0.25)
    return f


def bunting2(c, a, b, letters, colors, sag=50, size=30):
    pts = cable(c, a, b, sag=sag, w=2.6, col=(60, 50, 70), outline=False)
    n = len(letters)
    for i, L in enumerate(letters):
        q = pts[int((i + 0.5) / n * (len(pts) - 1))]
        col = colors[i % len(colors)]
        c.ink(Sh([[(q[0] - size * 0.5, q[1]), (q[0] + size * 0.5, q[1]), (q[0], q[1] + size * 1.1)]]), col, lw=2.2, shade=0.35)
        c.text(q[0], q[1] + size * 0.35, L, size * 0.42, (255, 255, 255))


def balloon(c, x, y, r, col, string_to):
    c.stroke([(x, y + r * 1.15), string_to], 1.4, (240, 240, 240), opacity=0.8)
    c.ink(ell(x, y, r * 0.88, r), col, lw=2.6, shade=0.5, sw=r * 0.5, hi=0.5, hw=r * 0.25, rim=0.2)
    c.ink(Sh([[(x - 4, y + r * 0.98), (x + 4, y + r * 0.98), (x, y + r * 1.15)]]), col, lw=1.6)


def corkboard(c, x0, y0, x1, y1, notes, seed=0):
    rng = random.Random(seed)
    c.ink(rect(x0 - 12, y0 - 12, x1 + 12, y1 + 12), (130, 80, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(x0, y0, x1, y1), (196, 146, 96), lw=2.0, shade=0.2, tex=0.4)
    for (nx_, ny_, w, h, col, lines) in notes:
        a = rng.uniform(-6, 6)
        sh = Sh([rot_pts([(nx_, ny_), (nx_ + w, ny_), (nx_ + w, ny_ + h), (nx_, ny_ + h)], a, nx_, ny_)])
        c.ink(sh, col, lw=1.8, shade=0.25, hi=0.2)
        for k, L in enumerate(lines):
            tx, ty = rot_pts([(nx_ + w / 2, ny_ + 14 + k * 13)], a, nx_, ny_)[0]
            c.text(tx, ty, L, 8.5, (60, 40, 60), "Bold", angle=-a)
        c.ink(ell(*rot_pts([(nx_ + w / 2, ny_ + 3)], a, nx_, ny_)[0], 3.5, 3.5), (220, 40, 60), lw=1.2, hi=0.5)


def fire_extinguisher(c, x, y_floor, h=90):
    c.ink(rrect(x - 14, y_floor - h, x + 14, y_floor, 10), (220, 40, 50), lw=2.6, shade=0.5, hi=0.5, hw=4)
    c.ink(rect(x - 8, y_floor - h - 14, x + 8, y_floor - h + 2), (40, 40, 40), lw=2.2)
    c.stroke([(x + 6, y_floor - h - 8), (x + 22, y_floor - h + 10), (x + 18, y_floor - h + 40)], 3.4, INK)


# =========================================================================== 2. Dorm hallway
def paint_dorm_hallway():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(-0.3, -0.95), lw=3.4, seed=216)
    y_top, y_bot = 762, 975
    vp = (960, vp_for_walk(y_top, y_bot))
    R = Room(c, vp, (230, 240, 1690, 690), fc=1000)
    Wb, Hb = R.Wb, R.Hb
    rng = random.Random(216)
    WALL = (220, 84, 156)
    TEAL_W = (40, 150, 160)

    def ceil(sub):
        w, h = sub.w, sub.h
        sub.ink(rect(0, 0, w, h), (132, 112, 150), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 90 * sub.density
        for x in np.arange(0, w, step):
            sub.stroke([(x, 0), (x, h)], 2.6, (120, 110, 130), taper=(0, 0))
        for y in np.arange(0, h, step * 0.8):
            sub.stroke([(0, y), (w, y)], 2.6, (120, 110, 130), taper=(0, 0))
        for _ in range(8):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            stain(sub, x, y, rng.uniform(30, 70), (120, 80, 40), 0.25, 0, rng.randint(0, 99))
        # a missing tile
        x, y = sub.ax(1300), sub.by(160)
        sub.ink(rect(x, y, x + step, y + step * 0.8), (30, 16, 40), lw=2.4)

    def wall_paint(sub, w, h, seed):
        grunge_wall(sub, w, h, WALL, seed=seed, chips=4, stains=3, floor_y=h)
        # teal lower half (dado) with a rail
        y0 = h * 0.6
        sub.ink(rect(-4, y0, w + 4, h), TEAL_W, lw=0, shade=0, hi=0, ao=0, tex=0.15, wob=0)
        for _ in range(3):
            chip(sub, rng.uniform(0, w), rng.uniform(y0 + 30, h - 30), rng.uniform(20, 40), BRICK, MORTAR, TEAL_W, seed=rng.randint(0, 99))
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)
        sub.ink(rect(-4, y0 - 10, w + 4, y0 + 8), (250, 200, 90), lw=2.4, shade=0.4, hi=0.4)
        skirting(sub, w, h, col=(40, 70, 90))

    def left(sub):
        wall_paint(sub, sub.w, sub.h, 21)
        x0, x1 = sub.ax(330), sub.ax(150)
        y0, y1 = sub.by(290), sub.by(0)
        def sign(cc, cx, cy):
            cc.ink(rrect(cx - 34, cy - 50, cx + 34, cy - 18, 5), (240, 200, 80), lw=2.4)
            cc.text(cx, cy - 34, "214", 18, (80, 40, 30))
            cc.ink(wonky(cx - 44, cy - 6, cx + 44, cy + 50, 2, rng), (250, 248, 236), lw=2.2)
            cc.text(cx, cy + 12, "DEX +", 12, (60, 60, 120))
            cc.text(cx, cy + 32, "???", 12, (60, 60, 120))
        flat_door(sub, x0, y0, x1, y1, (60, 90, 190), frame=(236, 220, 230), knob="R", sign=sign, seed=3)

    def right(sub):
        wall_paint(sub, sub.w, sub.h, 22)
        # stairwell doorway (open fire door, dark stairs beyond)
        x0, x1 = sub.ax(90), sub.ax(300)
        y0, y1 = sub.by(300), sub.by(0)
        sub.ink(rect(x0 - 24, y0 - 24, x1 + 24, y1), (200, 196, 210), lw=3.0, shade=0.4)
        sub.ink(rect(x0, y0, x1, y1), (30, 20, 50), lw=2.6)
        for k in range(6):
            yy = y0 + (y1 - y0) * (0.3 + k * 0.12)
            sub.ink(rect(x0, yy, x1 - k * 20, yy + 18), (70, 60, 100), lw=2.0, shade=0.3)
        sub.stroke([(x0 + 20, y0 + 60), (x1 - 40, y1 - 40)], 6, (160, 160, 180))
        exit_sign(sub, (x0 + x1) / 2, y0 - 60, 120, "STAIRS")

    def floor(sub):
        tiles(sub, (90, 170, 170), (60, 130, 140), 0, 0, sub.w, sub.h, size=52 * sub.density, seed=7, chipped=0.1)
        # worn runner carpet along the hallway
        y0, y1 = sub.by(190), sub.by(330)
        def pat(t):
            for x in np.arange(0, sub.w, 40 * sub.density):
                t.ink(Sh([[(x, (y0 + y1) / 2), (x + 20 * sub.density, y0 + 30), (x + 40 * sub.density, (y0 + y1) / 2),
                           (x + 20 * sub.density, y1 - 30)]]), (190, 120, 60), lw=1.6, shade=0.1, hi=0, ao=0, tex=0.3)
        sub.ink(rect(-10, y0, sub.w + 10, y1), (140, 40, 80), lw=3.0, shade=0.1, hi=0.1, tex=0.3)
        carpet(sub, (140, 40, 80), 0, y0 + 14, sub.w, y1 - 14, seed=8, pattern=pat)
        sub.stroke([(0, y0 + 12), (sub.w, y0 + 12)], 3, (250, 190, 70), taper=(0, 0))
        sub.stroke([(0, y1 - 12), (sub.w, y1 - 12)], 3, (250, 190, 70), taper=(0, 0))

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=216)

    def back(sub):
        wall_paint(sub, sub.w, sub.h, 23)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=23)
    R.ao(0.5)
    R.edges(w=4.0)
    P = R.pt

    # lounge doorway (open, warm glow, couch glimpse)
    lx0, ly0 = P(160, 300)
    lx1, ly1 = P(380, 0)
    c.ink(rect(lx0 - 18, ly0 - 18, lx1 + 18, ly1), (236, 220, 230), lw=3.0, shade=0.4)
    c.ink(rect(lx0, ly0, lx1, ly1), ("v", (150, 70, 60), (90, 40, 60)), lw=2.6)
    c.ink(rect(lx0, ly1 - 70, lx1, ly1), (180, 60, 60), lw=0)
    for k in range(5):
        c.ink(rect(lx0 + k * 44, ly1 - 70, lx0 + k * 44 + 22, ly1), (240, 220, 200), lw=0, opacity=0.6)
    c.ink(rrect(lx0 + 40, ly1 - 120, lx1 - 30, ly1 - 60, 10), (90, 160, 90), lw=2.6, shade=0.4)
    c.ink(rect(lx0 + 150, ly0 + 60, lx0 + 162, ly1 - 70), (60, 40, 30), lw=2.0)
    c.ink(Sh([[(lx0 + 132, ly0 + 40), (lx0 + 180, ly0 + 40), (lx0 + 170, ly0 + 70), (lx0 + 142, ly0 + 70)]]), (255, 220, 120), lw=2.2)
    c.glow2(lx0 + 156, ly0 + 70, 160, GLOW, 0.4)
    c.ink(rrect((lx0 + lx1) / 2 - 70, ly0 - 74, (lx0 + lx1) / 2 + 70, ly0 - 34, 6), (40, 40, 80), lw=2.6, shade=0.3)
    c.text((lx0 + lx1) / 2, ly0 - 54, "LOUNGE", 20, (255, 220, 120))
    # Room 216 sits here as its own sprite (hs_room_216): leave the wall bare, add a door mat
    mx0, my0 = P(590, 0, 6)
    mx1, my1 = P(750, 0, 40)
    c.ink(Sh([[P(590, 0, 6), P(750, 0, 6), P(756, 0, 46), P(584, 0, 46)]]), (150, 90, 60), lw=2.4, shade=0.3, tex=0.3)
    # bulletin board
    bx0, by0 = P(770, 300)
    bx1, by1 = P(1010, 150)
    corkboard(c, bx0, by0, bx1, by1,
              [(bx0 + 14, by0 + 14, 70, 60, (255, 240, 140), ["LOST:", "MY", "DIGNITY"]),
               (bx0 + 96, by0 + 10, 70, 56, (255, 160, 200), ["BAND", "TRYOUTS"]),
               (bx0 + 176, by0 + 16, 62, 64, (160, 230, 255), ["FREE", "PIZZA*", "*maybe"]),
               (bx0 + 30, by0 + 82, 80, 56, (190, 255, 170), ["SPEED", "DATING!"]),
               (bx0 + 130, by0 + 86, 80, 52, (250, 250, 240), ["QUIET", "HOURS", "lol"])], seed=4)
    # fire extinguisher, water fountain
    fire_extinguisher(c, *P(1100, 140), 90)
    fx_, fy_ = P(1130, 110)
    c.ink(rrect(fx_, fy_ - 20, fx_ + 70, fy_ + 16, 6), (210, 214, 226), lw=2.6, shade=0.4, hi=0.4)
    c.ink(rect(fx_ + 26, fy_ + 16, fx_ + 44, P(0, 0)[1]), (180, 184, 200), lw=2.4, shade=0.3)
    # bunting + balloons
    bunting2(c, P(380, 400), P(1000, 400), "PARTY!!", [(255, 90, 150), (255, 210, 60), (60, 210, 210), (170, 110, 255)], sag=60)
    for k, (dx, col) in enumerate(((0, (255, 80, 120)), (36, (255, 220, 60)), (18, (80, 160, 255)))):
        balloon(c, P(1040, 340)[0] + dx, P(1040, 340)[1] - k * 14, 26, col, P(1030, 300))
    # vending machine (against the back wall, right)
    vending_machine(c, R, 1220, 1360, 0, 110, 300, (220, 50, 70), seed=2)
    R.contact(1220, 1360, 0, 110, 0.5)
    # trash can + recycling
    R.contact(1380, 1430, 10, 60, 0.5)
    R.ink_box(1380, 1430, 0, 80, 10, 60, (60, 120, 200), seed=3)
    # drinks table (folding table with snacks), mid-floor
    R.contact(860, 1100, 170, 240, 0.5)
    tf = R.ink_box(860, 1100, 66, 72, 170, 240, (240, 240, 240), seed=4)
    cloth = [R.pt(856, 74, 168), R.pt(1104, 74, 168), R.pt(1104, 74, 242), R.pt(1104, 30, 244), R.pt(980, 40, 245), R.pt(856, 30, 244)]
    c.ink(blob(cloth, 1), (230, 60, 70), lw=2.8, shade=0.4, hi=0.3)
    clip_draw(c, blob(cloth, 1), lambda t: [t.stroke([(x, 600), (x, 900)], 9, (255, 255, 255), taper=(0, 0), opacity=0.8)
                                            for x in np.arange(900, 1500, 26)])
    c.ink(blob(cloth, 1), (0, 0, 0, 0), lw=2.8, line_only=True)
    for lxx in (870, 1086):
        for lzz in (176, 234):
            a = R.pt(lxx, 66, lzz)
            b_ = R.pt(lxx, 0, lzz)
            c.stroke([a, b_], 4, INK, taper=(0, 0))
    for k, (X, Z, col, kind) in enumerate(((890, 200, (255, 200, 60), "bottle"), (930, 190, (60, 200, 120), "bottle"), (970, 210, (240, 240, 240), "bowl"),
                                           (1020, 195, (255, 240, 80), "lemons"), (1060, 205, (60, 140, 255), "cups"))):
        x_, y_ = R.pt(X, 74, Z)
        if kind == "bottle":
            c.ink(blob([(x_ - 8, y_), (x_ - 8, y_ - 30), (x_ - 3, y_ - 40), (x_ - 3, y_ - 52), (x_ + 3, y_ - 52), (x_ + 3, y_ - 40), (x_ + 8, y_ - 30), (x_ + 8, y_)], 1),
                  col, lw=2.2, shade=0.4, hi=0.5, hw=2)
        elif kind == "bowl":
            c.ink(Sh([[(x_ - 22, y_ - 14), (x_ + 22, y_ - 14), (x_ + 14, y_), (x_ - 14, y_)]]), col, lw=2.2, shade=0.4)
            c.ink(ell(x_, y_ - 15, 20, 5), (240, 180, 60), lw=1.6)
        elif kind == "lemons":
            for j in range(3):
                c.ink(ell(x_ - 10 + j * 10, y_ - 6 - (j % 2) * 6, 7, 6), col, lw=1.8, shade=0.4, hi=0.5)
        else:
            for j in range(3):
                c.ink(Sh([[(x_ - 6 + j * 2, y_ - 18 - j * 8), (x_ + 6 + j * 2, y_ - 18 - j * 8), (x_ + 5 + j * 2, y_ - j * 8), (x_ - 5 + j * 2, y_ - j * 8)]]),
                      (220, 40, 60), lw=1.6, shade=0.3)
    rx_, ry_ = R.pt(980, 74, 236)
    c.ink(Sh([rot_pts([(rx_ - 26, ry_ - 2), (rx_ + 26, ry_ - 2), (rx_ + 26, ry_ + 16), (rx_ - 26, ry_ + 16)], -4, rx_, ry_)]), (250, 248, 236), lw=1.6)
    # floor junk: cups, chip bag, sock
    for X, Z, col in ((420, 330, (220, 40, 60)), (1300, 420, (220, 40, 60)), (700, 260, (60, 140, 255))):
        x_, y_ = R.pt(X, 0, Z)
        k = R.k(Z)
        c.ink(Sh([[(x_ - 10 * k, y_ - 6 * k), (x_ + 12 * k, y_ - 10 * k), (x_ + 14 * k, y_ + 2 * k), (x_ - 8 * k, y_ + 6 * k)]]), col, lw=2.2, shade=0.4)
    # ceiling: panel lights, pipes, cables
    lamps = []
    for X0 in (160, 640, 1120):
        panel_light(c, R, X0, X0 + 200, 100, 200, cone=0.22, flicker=(X0 == 1120))
        lamps.append(R.pt(X0 + 100, Hb - 14, 150))
    # clutter: pizza box, skateboard, laundry bag
    pz = R.box(1300, 1400, 0, 8, 330, 420)
    c.ink(Sh([pz["top"]]), (220, 180, 120), lw=2.6, shade=0.2)
    c.ink(Sh([pz["front"]]), (190, 150, 100), lw=2.2)
    sk = [R.pt(330, 6, 230), R.pt(520, 6, 260), R.pt(520, 6, 290), R.pt(330, 6, 262)]
    c.ink(blob(sk, 1), (60, 200, 200), lw=2.6, shade=0.3, hi=0.3)
    for X, Z in ((360, 236), (500, 265), (360, 268), (500, 296)):
        c.ink(ell(*R.pt(X, 0, Z), 7, 5), (250, 220, 60), lw=1.8)
    lb = R.pt(80, 0, 120)
    c.ink(blob([(lb[0] - 50, lb[1]), (lb[0] - 56, lb[1] - 70), (lb[0] - 10, lb[1] - 110), (lb[0] + 30, lb[1] - 90), (lb[0] + 50, lb[1])], 2),
          (240, 200, 90), lw=3.0, shade=0.55, sw=24, hi=0.3)
    pipe(c, [P(0, Hb - 40, 40), P(Wb, Hb - 40, 40)], w=22, col=(170, 120, 190), brackets=[P(400, Hb - 40, 40), P(1000, Hb - 40, 40)])
    cable(c, P(0, Hb, 260), P(700, Hb, 330), sag=60, w=7, col=(40, 30, 70))
    cable(c, P(700, Hb, 330), P(Wb, Hb, 220), sag=40, w=6, col=(40, 130, 130))
    hanging_cable(c, P(1250, Hb, 280), 130, sway=-14, w=6, col=(40, 30, 70), seed=4)
    cobweb(c, *P(0, Hb, 0), 100, "tl")
    cobweb(c, *P(Wb, Hb, 0), 110, "tr")
    cobweb(c, *P(Wb, 0, 0), 60, "tr", opacity=0.3)
    stain(c, *P(600, 380), 50, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(500, 620, 520, 0.4), (980, 600, 520, 0.4), (P(270, 150)[0], 560, 300, 0.45, (255, 170, 90)),
                          (1680, 600, 260, 0.2, (90, 255, 160))],
               ambient=0.92, vign=0.62, top_dark=0.45, bottom_dark=0.35)
    for k, (x, y) in enumerate(lamps):
        c.glow2(x, y, 260, (255, 246, 210), 0.5 if k < 2 else 0.25, sy=0.4)
        c.glow2(x, y, 120, (255, 255, 240), 0.6 if k < 2 else 0.3, sy=0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 80, 1100, 340, seed=7)
        fg_bottles(sub, 1660, 1090, 5, 1.1, seed=8)
        fg_chair_back(sub, 1900, 900, 280, 320)
        fg_cable(sub, [(300, 1100), (700, 1050), (1100, 1070), (1500, 1110)], 18)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_dorm_hallway.png")



# =========================================================================== layouts (px) -> act1.json
Y_TOP, Y_BOT = 762, 975
LAYOUT["dex_room"] = dict(
        walk_px=[(470, Y_TOP), (1520, Y_TOP), (1680, 930), (1600, Y_BOT), (380, Y_BOT), (360, 880), (430, 868)],
        hotspots={
            ("Bed", 0): dict(box=(110, 560, 560, 860), stand=(480, 890)),
            ("Mirror", 0): dict(box=(1285, 350, 1385, 655), stand=(1335, 790)),
            ("Desk", 0): dict(box=(925, 470, 1240, 735), stand=(1080, 790)),
            ("Door to hallway", 0): dict(box=(1515, 360, 1700, 800), stand=(1520, 850)),
        },
        entries={"start": (760, 900), "from_hallway": (1500, 860)})

LAYOUT["dorm_hallway"] = dict(
        walk_px=[(120, Y_TOP), (1800, Y_TOP), (1800, 900), (1640, Y_BOT), (300, Y_BOT), (150, 900)],
        hotspots={
            ("Your door", 0): dict(box=(20, 330, 200, 820), stand=(250, 880)),
            ("Lounge", 0): dict(box=(375, 370, 625, 692), stand=(500, 790)),
            ("Room 216", 0): dict(sprite="hs_room_216", feet=(900, 690), stand=(900, 790)),
            ("Lacey Rae", 0): dict(npc="hs_lacey_rae", feet=(690, 948), stand=(520, 935)),
            ("Gil", 0): dict(npc="hs_gil", feet=(1040, 946), stand=(1220, 935)),
            ("Vending machine", 0): dict(box=(1500, 385, 1690, 705), stand=(1560, 800)),
            ("Drinks table", 0): dict(box=(1120, 590, 1450, 760), stand=(1330, 800)),
            ("Stairs", 0): dict(box=(1740, 300, 1920, 870), stand=(1740, 880)),
        },
        entries={"start": (260, 900), "from_room": (260, 900), "from_lounge": (500, 800), "from_stairs": (1720, 880),
                 "from_gil_room": (900, 800)})


# =========================================================================== props (sprites)
def sprite_grade(c, f=0.88, tint=(0.94, 0.86, 1.0)):
    """Darken / tint a prop sprite so it sits in the graded background."""
    t = np.array(tint, np.float32) * f
    c.grade(lambda rgb, xs, ys: rgb * t[None, None, :])


def paint_room_216(name="hs_room_216.png"):
    w, h = 140, 300
    c = Canvas2(w + 60, h + 40, light=(-0.3, -0.95), lw=3.2, seed=216)
    x0, y0, x1, y1 = 30, 26, 30 + w, 26 + h

    def sign(cc, cx, cy):
        cc.ink(rrect(cx - 30, cy - 52, cx + 30, cy - 22, 5), (240, 200, 80), lw=2.4, shade=0.3, hi=0.4)
        cc.text(cx, cy - 37, "216", 17, (80, 40, 30))
        cc.ink(Sh([rot_pts([(cx - 44, cy - 6), (cx + 44, cy - 6), (cx + 44, cy + 56), (cx - 44, cy + 56)], -4, cx, cy)]), (250, 248, 236), lw=2.2,
               shade=0.2)
        cc.text(cx, cy + 8, "DO NOT", 11, (190, 40, 50), angle=-4)
        cc.text(cx, cy + 26, "DISTURB", 11, (190, 40, 50), angle=-4)
        cc.text(cx, cy + 44, "(EVER)", 8, (60, 60, 90), "Bold", angle=-4)
    flat_door(c, x0, y0, x1, y1, (70, 140, 100), frame=(236, 220, 230), knob="R", sign=sign, seed=6)
    # a sock on the knob, stickers, a sliver of light under the door
    kx, ky = x1 - w * 0.12, y0 + h * 0.55
    c.ink(blob([(kx - 6, ky + 4), (kx + 6, ky + 4), (kx + 8, ky + 40), (kx + 20, ky + 52), (kx + 4, ky + 58), (kx - 6, ky + 40)], 2), (250, 250, 240),
          lw=2.4, shade=0.4)
    c.stroke([(kx - 6, ky + 14), (kx + 7, ky + 14)], 3, (220, 50, 60))
    c.ink(ell(x0 + 34, y0 + h * 0.66, 13, 13), (255, 220, 60), lw=2.0)
    c.ink(rrect(x0 + 24, y0 + h * 0.78, x0 + 70, y0 + h * 0.84, 4), (60, 200, 220), lw=1.8)
    c.label(x0 + 47, y0 + h * 0.81, "VINYL 4 LIFE", 5, (20, 40, 60), "Bold")
    c.ink(rect(x0 + 6, y1 - 6, x1 - 6, y1 + 1), (255, 220, 140), lw=0)
    sprite_grade(c, 0.86)
    return finish_sprite(c, name, margin=2)


def paint_union_sign(name="hs_student_union.png"):
    c = Canvas2(220, 330, light=(-0.3, -0.95), lw=3.2, seed=33)
    wood, H = (176, 116, 64), 320
    c.soft(ell(110, H - 4, 46, 8), (30, 8, 40), 0.4, 4)
    c.ink(rect(102, 40, 118, H - 4), wood, lw=3.0, shade=0.5, sw=6, hi=0.4)
    c.ink(Sh([[(18, 52), (176, 46), (206, 78), (178, 108), (18, 104)]]), (50, 150, 120), lw=3.2, shade=0.5, sw=14, hi=0.4)
    c.text(100, 66, "STUDENT", 15, (255, 250, 230))
    c.text(98, 90, "UNION", 18, (255, 250, 230))
    c.ink(Sh([[(200, 126), (52, 130), (16, 152), (52, 176), (200, 172)]]), (236, 150, 60), lw=3.2, shade=0.5, sw=12, hi=0.4)
    c.text(122, 152, "food", 17, (80, 30, 20), "Italic")
    # tiny possum doodle + flyer stapled to the post + moss
    c.ink(ell(160, 152, 10, 8), (170, 168, 184), lw=1.8)
    c.ink(ell(152, 145, 4, 4), (170, 168, 184), lw=1.4)
    c.ink(ell(168, 145, 4, 4), (170, 168, 184), lw=1.4)
    c.ink(Sh([rot_pts([(88, 200), (132, 200), (132, 254), (88, 254)], 6, 110, 226)]), (255, 236, 120), lw=2.0)
    c.text(110, 216, "LOST", 8, (190, 40, 60))
    c.text(110, 232, "GLOVE", 8, (190, 40, 60))
    c.ink(Sh([[(96, H - 30), (126, H - 34), (124, H - 4), (98, H - 4)]]), (70, 120, 60), lw=0, opacity=0.6)
    c.ink(ell(66, 30, 18, 16), (60, 200, 220), lw=2.6, shade=0.4, hi=0.5) if False else None
    sprite_grade(c, 0.9, (0.98, 0.88, 0.96))
    return finish_sprite(c, name, margin=2)


def draw_alarm(c, cx, cy, s=1.0):
    red = (226, 50, 56)
    for ex in (-1, 1):
        c.ink(ell(cx + ex * 20 * s, cy - 27 * s, 12 * s, 9 * s, ex * 25), (236, 200, 80), lw=2.6, shade=0.4, hi=0.5)
    c.ink(rect(cx - 2.5 * s, cy - 40 * s, cx + 2.5 * s, cy - 28 * s), (200, 160, 60), lw=2)
    for ex in (-1, 1):
        c.stroke([(cx + ex * 16 * s, cy + 22 * s), (cx + ex * 23 * s, cy + 33 * s)], 5 * s, (60, 60, 66))
    c.ink(ell(cx, cy, 28 * s, 28 * s), red, lw=3.0, shade=0.55, sw=10 * s, hi=0.45, hw=5 * s, rim=0.2)
    c.ink(ell(cx, cy, 21 * s, 21 * s), (250, 248, 236), lw=2.6, shade=0.3, sw=6)
    for k in range(12):
        a = math.radians(k * 30)
        c.stroke([(cx + 16 * s * math.cos(a), cy + 16 * s * math.sin(a)), (cx + 19 * s * math.cos(a), cy + 19 * s * math.sin(a))], 1.6, INK,
                 taper=(0, 0))
    c.stroke([(cx, cy), (cx, cy - 13 * s)], 2.6, INK, taper=(0, 0))
    c.stroke([(cx, cy), (cx + 9 * s, cy + 4 * s)], 2.6, INK, taper=(0, 0))
    c.text(cx, cy + 9 * s, "GAME DAY", 4 * s, (190, 40, 50))


def paint_alarm_clock_prop(name="hs_alarm_clock.png"):
    c = Canvas2(90, 100, lw=2.8, seed=5)
    draw_alarm(c, 45, 52, 1.0)
    sprite_grade(c, 0.92)
    return finish_sprite(c, name, margin=2)


def paint_air_freshener_prop(name="hs_air_freshener.png"):
    c = Canvas2(70, 130, lw=2.6, seed=6)
    cx, top, s_ = 35, 44, 1.0
    g = (60, 170, 86)
    c.stroke([(cx, 6), (cx, top + 4)], 1.8, (244, 240, 226), taper=(0, 0))
    tree = Sh([[(cx, top), (cx + 12, top + 16), (cx + 6, top + 16), (cx + 18, top + 34), (cx + 9, top + 34), (cx + 22, top + 54), (cx + 4, top + 54),
                (cx + 4, top + 64), (cx - 4, top + 64), (cx - 4, top + 54), (cx - 22, top + 54), (cx - 9, top + 34), (cx - 18, top + 34), (cx - 6, top + 16),
                (cx - 12, top + 16)]])
    c.ink(tree, g, lw=2.6, shade=0.5, sw=8, hi=0.4)
    c.ink(rrect(cx - 12, top + 36, cx + 12, top + 46, 2), (250, 248, 236), lw=1.4)
    sprite_grade(c, 0.92)
    return finish_sprite(c, name, margin=2)


def paint_frisbee(name="hs_frisbee.png"):
    c = Canvas2(110, 60, lw=2.8, seed=7)
    col = (255, 120, 30)
    c.soft(ell(55, 44, 46, 9), (30, 8, 40), 0.45, 3)
    c.ink(ell(55, 34, 44, 14), shade_col(col, 0.75), lw=2.8, shade=0.3)
    c.ink(ell(55, 30, 44, 13), col, lw=2.8, shade=0.4, sw=6, hi=0.6, hw=4, rim=0.2)
    c.ink(ell(55, 30, 26, 7), hi_col(col, 0.2), lw=1.6, shade=0.2)
    c.stroke([(36, 28), (46, 24)], 2.4, (255, 240, 200), opacity=0.8)
    for k in range(3):   # grass blades over the edge
        x = 22 + k * 30
        c.stroke([(x, 46), (x + 3, 34)], 2.4, (60, 150, 70), taper=(0, 0.8))
    return finish_sprite(c, name, margin=2)


# =========================================================================== layout -> act1.json, composites
NPC_REL = {"hs_lacey_rae": 0.95, "hs_gil": 0.93, "hs_ivy": 0.88, "hs_ms_hush": 0.86, "hs_roxy_vale": 0.95,
           "hs_boomer": 1.02, "hs_doreen": 0.92, "hs_kyle": 0.94, "hs_percival_thorne": 0.98}
NPC_FN = {"hs_lacey_rae": paint_lacey_rae, "hs_gil": paint_gil, "hs_ivy": paint_ivy, "hs_ms_hush": paint_ms_hush,
          "hs_roxy_vale": paint_roxy_vale, "hs_boomer": paint_boomer, "hs_doreen": paint_doreen, "hs_kyle": paint_kyle,
          "hs_percival_thorne": paint_percival_thorne}


def walk_y(room_id):
    return LAYOUT[room_id].get("walk_y", (Y_TOP, Y_BOT))


def npc_height(npc):
    """Crown height (px) for an NPC sprite, from the depth scale at its feet (first room it appears in)."""
    for rid, L in LAYOUT.items():
        for key, h in L["hotspots"].items():
            if h.get("npc") == npc:
                yt, yb = walk_y(rid)
                return round(DEX_H * depth_scale(h["feet"][1], yt, yb) * NPC_REL[npc])
    return round(DEX_H * 0.93 * NPC_REL.get(npc, 1.0))


def paint_npc(npc):
    return NPC_FN[npc](height=npc_height(npc))


def _sprite_size(name):
    im = Image.open(os.path.join(OUT_DIR, name + ".png"))
    return im.size


def write_layout(path=None):
    import json
    path = path or os.path.join(ROOT, "Assets", "_Project", "World", "act1.json")
    data = json.load(open(path))
    for room in data["rooms"]:
        L = LAYOUT.get(room["id"])
        if not L:
            continue
        room["walkable"] = [v for p in L["walk_px"] for v in px_to_world(*p)]
        for e in room.get("entries", []):
            if e["name"] in L["entries"]:
                e["pos"] = list(px_to_world(*L["entries"][e["name"]]))
        seen = {}
        for h in room["hotspots"]:
            n = seen.get(h["name"], 0)
            seen[h["name"]] = n + 1
            spec = L["hotspots"].get((h["name"], n))
            if not spec:
                print("  (no layout for", room["id"], h["name"], n, ")")
                continue
            if "npc" in spec or "sprite" in spec:
                nm = spec.get("npc") or spec["sprite"]
                w, hh = _sprite_size(nm)
                fx, fy = spec["feet"]
                if "npc" in spec:
                    bw = spec.get("w", 1.9)
                else:
                    bw = round(w / 100, 2)
                h["feet"] = list(px_to_world(fx, fy))
                h["size"] = [bw, round(hh / 100, 2)]
            else:
                x0, y0, x1, y1 = spec["box"]
                h["feet"] = list(px_to_world((x0 + x1) / 2, y1))
                h["size"] = [round((x1 - x0) / 100, 2), round((y1 - y0) / 100, 2)]
            h["standAt"] = list(px_to_world(*spec["stand"]))
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    print("updated", os.path.relpath(path, ROOT))


COMPOSITE_DIR = os.environ.get("BNO_COMPOSITES", os.path.join(ROOT, "..", "composites"))


def composite(room_id, out_dir=None, boxes=True):
    """Background + NPC sprites at their feet (unscaled, like the game) + Dex (depth-scaled) at each
    stand point and at the back of the walkable area, with hotspot boxes and the walkable outline."""
    import json
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(os.path.join(ROOT, "Assets", "_Project", "World", "act1.json")))
    room = [r for r in data["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))
    items = []
    import re as _re
    names = [h["name"] for h in room["hotspots"]]
    for h in room["hotspots"]:
        if h.get("showWhenFlag") and names.count(h["name"]) > 1:
            continue
        slug = _re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx, False))
    stands = [world_to_px(*h["standAt"]) for h in room["hotspots"] if not h.get("showWhenFlag")]
    stands = sorted(stands, key=lambda p: -p[1])[:2] + [((wp[0][0] + wp[1][0]) / 2, yt)]
    for (sx, sy) in stands:
        k = 1.0 - 0.4 * (yb - sy) / max(1, yb - yt)
        im = dex.resize((int(dex.width * k), int(dex.height * k)), Image.LANCZOS)
        items.append((sy, im, sx, True))
    for fy, im, fx, is_dex in sorted(items, key=lambda t: t[0]):
        bg.alpha_composite(im, (int(fx - im.width / 2), int(fy - im.height)))
    if boxes:
        ov = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.polygon(wp, outline=(80, 255, 120, 255))
        d.line(wp + [wp[0]], fill=(80, 255, 120, 220), width=3)
        for h in room["hotspots"]:
            fx, fy = world_to_px(*h["feet"])
            w, hh = h["size"][0] * 100, h["size"][1] * 100
            col = (255, 230, 60, 255) if not h.get("showWhenFlag") else (120, 200, 255, 255)
            d.rectangle([fx - w / 2, fy - hh, fx + w / 2, fy], outline=col, width=3)
            sx, sy = world_to_px(*h["standAt"])
            d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 80, 80, 255))
            d.text((fx - w / 2 + 4, fy - hh + 4), h["name"], fill=col)
        for e in room.get("entries", []):
            ex, ey = world_to_px(*e["pos"])
            d.rectangle([ex - 6, ey - 6, ex + 6, ey + 6], fill=(80, 160, 255, 255))
        bg.alpha_composite(ov)
    out = os.path.join(out_dir, "composite_%s.png" % room_id)
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


# =========================================================================== shared helpers for the remaining rooms
def std_room(seed, vp_x=960, back=(330, 250, 1590, 690), light=(-0.3, -0.95), fc=1000):
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=light, lw=3.4, seed=seed)
    R = Room(c, (vp_x, vp_for_walk(Y_TOP, Y_BOT)), back, fc=fc)
    return c, R, random.Random(seed)


def two_tone_wall(sub, w, h, top, low, seed, rail=(250, 200, 90), split=0.58, chips=4, stains=3, low_kind="paint"):
    """Plaster upper wall + a darker dado (paint or wood panels) with a rail and skirting."""
    rng = random.Random(seed)
    grunge_wall(sub, w, h, top, seed=seed, chips=chips, stains=stains, floor_y=h)
    y0 = h * split
    if low_kind == "wood":
        wainscot(sub, -6, w + 6, y0, h, low, seed=seed, panel_w=150 * getattr(sub, "density", 1.0))
    else:
        sub.ink(rect(-4, y0, w + 4, h), low, lw=0, shade=0, hi=0, ao=0, tex=0.15, wob=0)
        for _ in range(3):
            chip(sub, rng.uniform(0, w), rng.uniform(y0 + 30, h - 30), rng.uniform(20, 40), BRICK, MORTAR, low,
                 seed=rng.randint(0, 99))
        sub.ink(rect(-4, y0 - 10, w + 4, y0 + 8), rail, lw=2.4, shade=0.4, hi=0.4)
    scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)
    skirting(sub, w, h, col=shade_col(low, 0.7))


def window_flat(sub, x0, y0, x1, y1, frame=(230, 200, 220), seed=3, mullions=1, transoms=1, sky=None, curtains=None,
                sill=True):
    """A night window (flat space) with frame, mullions, glare, sill and optional curtains."""
    rng = random.Random(seed)
    sub.ink(rect(x0 - 20, y0 - 20, x1 + 20, y1 + 20), frame, lw=3.0, shade=0.4, hi=0.3)
    (sky or night_sky)(sub, x0, y0, x1, y1, seed=seed)
    for k in range(1, mullions + 1):
        xx = x0 + (x1 - x0) * k / (mullions + 1)
        sub.ink(rect(xx - 6, y0, xx + 6, y1), frame, lw=2.4, shade=0.3)
    for k in range(1, transoms + 1):
        yy = y0 + (y1 - y0) * k / (transoms + 1)
        sub.ink(rect(x0, yy - 6, x1, yy + 6), frame, lw=2.4, shade=0.3)
    sub.stroke([(x0 + 20, y1 - 20), (x0 + (x1 - x0) * 0.3, y0 + 20)], 10, (255, 255, 255), opacity=0.12)
    if sill:
        sub.ink(rect(x0 - 36, y1 + 14, x1 + 36, y1 + 34), hi_col(frame, 0.1), lw=2.8, shade=0.5, sw=8, hi=0.3)
    if curtains:
        for side in (0, 1):
            cx0 = x0 - 64 if side == 0 else x1 - 26
            cx1 = x0 + 36 if side == 0 else x1 + 74
            pts = [(cx0, y0 - 40), (cx1, y0 - 40), (cx1 - (18 if side == 0 else -18), y1 + 30), (cx0 + 6, y1 + 46)]
            sub.ink(blob(pts, 1), curtains, lw=3.0, shade=0.55, sw=30, hi=0.4, rim=0.2)
            for k in range(1, 4):
                fx = cx0 + (cx1 - cx0) * k / 4
                sub.stroke([(fx, y0 - 30), (fx + rng.uniform(-8, 8), y1 + 30)], 2.2, shade_col(curtains, 0.5), opacity=0.7)
        sub.ink(rect(x0 - 84, y0 - 50, x1 + 94, y0 - 38), (90, 70, 90), lw=2.4, shade=0.3)


def doorway_flat(sub, x0, y0, x1, y1, inside=((80, 150, 160), (40, 80, 100)), frame=(236, 220, 230), door_col=None,
                 open_side="L"):
    """An open doorway with a glimpse of light beyond and the door swung open (flat space)."""
    sub.ink(rect(x0 - 22, y0 - 22, x1 + 22, y1), frame, lw=3.0, shade=0.4, sw=10, hi=0.3)
    sub.ink(rect(x0, y0, x1, y1), ("v", inside[0], inside[1]), lw=2.6, shade=0.2, hi=0)
    # floor beyond + light spill
    sub.ink(Sh([[(x0, y1 - (y1 - y0) * 0.16), (x1, y1 - (y1 - y0) * 0.16), (x1, y1), (x0, y1)]]), shade_col(inside[0], 0.7),
            lw=0, shade=0, hi=0, ao=0)
    sub.glow2((x0 + x1) / 2, y0 + (y1 - y0) * 0.3, (x1 - x0) * 0.9, hi_col(inside[0], 0.4), 0.35)
    if door_col:
        w = (x1 - x0) * 0.32
        if open_side == "L":
            pts = [(x0, y0), (x0 + w, y0 + 26), (x0 + w, y1 + 10), (x0, y1)]
        else:
            pts = [(x1 - w, y0 + 26), (x1, y0), (x1, y1), (x1 - w, y1 + 10)]
        sub.ink(Sh([pts]), door_col, lw=2.8, shade=0.45, sw=20, hi=0.3)


def crt_tv(c, x0, y0, x1, y1, screen=(90, 230, 220), seed=0, text=None):
    """Chunky old TV, front face (x0..x1, y0..y1) in screen space with a fake depth to the right."""
    rng = random.Random(seed)
    d = (x1 - x0) * 0.12
    c.ink(Sh([[(x1, y0 + 6), (x1 + d, y0 + 18), (x1 + d, y1 - 8), (x1, y1)]]), (60, 50, 70), lw=2.8, shade=0.3)
    c.ink(rrect(x0, y0, x1, y1, 14), (90, 80, 100), lw=3.2, shade=0.45, sw=16, hi=0.35, rim=0.15)
    sx0, sy0, sx1, sy1 = x0 + 16, y0 + 16, x1 - 50, y1 - 16
    c.ink(rrect(sx0, sy0, sx1, sy1, 18), screen, lw=2.8, shade=0.4, sw=20, hi=0, ao=0)
    for yy in np.arange(sy0 + 6, sy1 - 4, 5):
        c.stroke([(sx0 + 8, yy), (sx1 - 8, yy)], 1.0, (255, 255, 255), opacity=0.12, taper=(0, 0))
    for _ in range(60):
        px, py = rng.uniform(sx0 + 10, sx1 - 10), rng.uniform(sy0 + 10, sy1 - 10)
        c.ink(rect(px, py, px + 3, py + 2), (255, 255, 255), lw=0, shade=0, hi=0, ao=0, opacity=0.6)
    c.stroke([(sx0 + 14, sy1 - 14), (sx0 + (sx1 - sx0) * 0.35, sy0 + 12)], 10, (255, 255, 255), opacity=0.2)
    if text:
        c.text((sx0 + sx1) / 2, (sy0 + sy1) / 2, text, 16, (20, 60, 60))
    for k in range(2):
        c.ink(ell(x1 - 26, y0 + 40 + k * 34, 9, 9), (200, 190, 200), lw=2.0, shade=0.4, hi=0.5)
    c.ink(rect(x1 - 38, y1 - 46, x1 - 14, y1 - 34), (40, 30, 50), lw=1.6)
    # rabbit ears
    for ang in (-30, 26):
        a = math.radians(-90 + ang)
        bx, by = (x0 + x1) / 2 + 10, y0
        c.stroke([(bx, by), (bx + math.cos(a) * 110, by + math.sin(a) * 110)], 3.4, (70, 70, 80))
    c.ink(ell((x0 + x1) / 2 + 10, y0 - 4, 18, 9), (60, 50, 70), lw=2.2)
    c.glow2((sx0 + sx1) / 2, (sy0 + sy1) / 2, (x1 - x0) * 1.2, screen, 0.4)


def couch(c, R, X0, X1, Z0, Z1, col=(70, 150, 120), seed=0, seat_y=56, back_y=150, arm_y=96):
    """Saggy three-seater against the back wall: base, backrest, arms, seat cushions, a throw pillow."""
    R.contact(X0, X1, Z0, Z1, 0.55)
    dk_ = shade_col(col, 0.72)
    R.ink_box(X0 + 18, X1 - 18, 0, back_y, Z0, Z0 + 30, dk_, seed=seed)                 # backrest
    R.ink_box(X0, X1, 10, seat_y - 10, Z0 + 20, Z1, col, seed=seed + 1)                 # base
    n = 3
    cw = (X1 - X0 - 60) / n
    for i in range(n):
        xa, xb = X0 + 30 + i * cw + 3, X0 + 30 + (i + 1) * cw - 3
        sag = 6 if i == 1 else 0
        f = R.box(xa, xb, seat_y - 14 - sag, seat_y + 6 - sag, Z0 + 30, Z1 - 4)
        c.ink(blob(f["top"] if "top" in f else f["front"], 2), hi_col(col, 0.1), lw=2.8, shade=0.3, hi=0.35, tex=0.15)
        c.ink(blob(f["front"], 2), col, lw=2.8, shade=0.4, sw=8, hi=0.2, tex=0.15)
        bf = R.box(xa + 4, xb - 4, seat_y, back_y - 10, Z0 + 18, Z0 + 40)
        c.ink(blob(bf["front"], 3), hi_col(col, 0.05), lw=2.8, shade=0.5, sw=26, hi=0.3, rim=0.15, tex=0.15)
    for xa, xb in ((X0, X0 + 34), (X1 - 34, X1)):
        f = R.box(xa, xb, 0, arm_y, Z0 + 14, Z1 + 4)
        for name in ("left", "right"):
            if name in f:
                c.ink(blob(f[name], 2), dk_, lw=2.8, shade=0.3, tex=0.15)
        if "top" in f:
            c.ink(blob(f["top"], 2), hi_col(col, 0.15), lw=2.6, shade=0.2, tex=0.15)
        c.ink(blob(f["front"], 2), col, lw=2.8, shade=0.45, sw=10, hi=0.3, tex=0.15)
    # a split seam with stuffing
    sx, sy = R.pt(X0 + 30 + cw * 1.5, seat_y - 2, Z1 - 30)
    c.ink(ell(sx, sy, 16, 6), (250, 246, 230), lw=1.8, shade=0.3)
    c.stroke([(sx - 22, sy), (sx + 22, sy + 2)], 1.6, INK, opacity=0.8)
    return R.pt(X0, back_y, Z0), R.pt(X1, back_y, Z0)


# =========================================================================== 3. Lounge
def paint_lounge():
    c, R, rng = std_room(310, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (196, 70, 150)
    LOW = (96, 50, 120)

    def ceil(sub):
        plaster_wall(sub, (110, 66, 120), (80, 44, 100), seed=31, w=sub.w, h=sub.h)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 110), (60, 30, 30), 0.25, 0,
                  rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (130, 40, 120), 0.25), LOW, 32, low_kind="wood")
        x0, x1 = sub.ax(280), sub.ax(100)
        y0, y1 = sub.by(300), sub.by(0)
        doorway_flat(sub, x0, y0, x1, y1, inside=((90, 180, 180), (50, 110, 120)), door_col=(60, 90, 190), open_side="R")
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 150, "HALLWAY")
        poster(sub, sub.ax(420), sub.by(300), 130, 170, (255, 230, 120),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.18, "KARAOKE", 16, (200, 40, 90)),
                                  p.text(w_ / 2, h_ * 0.34, "NIGHT", 16, (200, 40, 90)),
                                  p.ink(ell(w_ / 2, h_ * 0.62, w_ * 0.18, w_ * 0.18), (60, 60, 80), lw=2),
                                  p.ink(rect(w_ / 2 - 4, h_ * 0.7, w_ / 2 + 4, h_ * 0.9), (60, 60, 80), lw=1.6),
                                  p.text(w_ / 2, h_ * 0.95, "THURS (ALWAYS)", 8, (90, 40, 80), "Bold")),
               angle=-4, seed=12, peel="tr")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 33, low_kind="wood")
        x0, x1 = sub.ax(70), sub.ax(260)
        y0, y1 = sub.by(380), sub.by(170)
        window_flat(sub, x0, y0, x1, y1, seed=9, curtains=(220, 170, 60))
        # radiator
        rx0, rx1 = sub.ax(80), sub.ax(250)
        sub.ink(rrect(rx0, sub.by(120), rx1, sub.by(24), 6), (200, 196, 210), lw=2.6, shade=0.4, hi=0.3)
        for xx in np.arange(rx0 + 12, rx1 - 6, 16):
            sub.stroke([(xx, sub.by(114)), (xx, sub.by(30))], 2.0, (130, 126, 150), taper=(0, 0))

    def floor(sub):
        planks(sub, (150, 84, 80), 0, 0, sub.w, sub.h, pw=40 * sub.density, seed=34, vertical=True)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=310)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 35, chips=6, stains=4, low_kind="wood")
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=35)
    R.ao(0.5)
    R.edges(w=4.0)

    # big rug in front of the couch
    rug = [P(80, 0, 110), P(1120, 0, 110), P(1160, 0, 420), P(40, 0, 420)]
    c.ink(blob(rug, 1), (60, 140, 150), lw=3.0, shade=0.15, hi=0.05, tex=0.3)
    inner = [P(120, 0, 130), P(1080, 0, 130), P(1110, 0, 400), P(90, 0, 400)]
    c.ink(blob(inner, 1), (230, 180, 70), lw=2.2, shade=0.1, hi=0, tex=0.3, opacity=0.9)
    inner2 = [P(150, 0, 150), P(1050, 0, 150), P(1070, 0, 380), P(130, 0, 380)]
    c.ink(blob(inner2, 1), (60, 140, 150), lw=2.0, shade=0.1, hi=0, tex=0.3)
    for k in range(8):
        a, b_ = P(170 + k * 110, 0, 160), P(160 + k * 115, 0, 370)
        c.stroke([a, b_], 2.0, (40, 100, 110), opacity=0.5)

    # posters / art on the back wall
    poster(c, *P(430, 330), 230, 120, (250, 240, 220),
           lambda p, w_, h_: (p.ink(rect(8, 8, w_ - 8, h_ - 8), ("v", (255, 160, 90), (200, 60, 120)), lw=1.6),
                              p.ink(ell(w_ * 0.5, h_ * 0.62, w_ * 0.18, h_ * 0.22), (255, 230, 120), lw=0),
                              [p.ink(Sh([[(w_ * (0.1 + k * 0.2), h_ * 0.92), (w_ * (0.2 + k * 0.2), h_ * 0.55),
                                          (w_ * (0.3 + k * 0.2), h_ * 0.92)]]), (90, 30, 90), lw=1.6) for k in range(4)],
                              p.text(w_ / 2, h_ * 0.2, "VISIT LAKE GLOOM", 12, (60, 20, 60))),
           angle=1.5, seed=31)
    poster(c, *P(690, 330), 110, 150, (40, 40, 70),
           lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.2, "NO", 22, (255, 230, 120)),
                              p.text(w_ / 2, h_ * 0.42, "NAPPING", 13, (255, 230, 120)),
                              p.text(w_ / 2, h_ * 0.6, "ON THE", 11, (255, 140, 180)),
                              p.text(w_ / 2, h_ * 0.78, "COUCH", 16, (255, 140, 180))), angle=-5, seed=32, peel="bl")
    # sign-up board (hotspot "Sign-up sheet")
    bx0, by0 = P(1110, 330)
    bx1, by1 = P(1225, 150)
    c.ink(rect(bx0 - 12, by0 - 12, bx1 + 12, by1 + 12), (130, 80, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(bx0, by0, bx1, by1), (196, 146, 96), lw=2.0, shade=0.2, tex=0.4)
    sh_ = Sh([rot_pts([(bx0 + 14, by0 + 18), (bx1 - 14, by0 + 18), (bx1 - 14, by1 - 14), (bx0 + 14, by1 - 14)], 3, bx0, by0)])
    c.ink(sh_, (252, 250, 240), lw=2.0, shade=0.2)
    c.text((bx0 + bx1) / 2, by0 + 36, "BIG NIGHT", 11, (200, 40, 90))
    c.text((bx0 + bx1) / 2, by0 + 50, "SIGN-UP", 10, (60, 60, 120))
    for k in range(6):
        yy = by0 + 66 + k * 16
        c.stroke([(bx0 + 24, yy), (bx1 - 20 - (k * 7) % 20, yy + 2)], 1.6, (90, 90, 150) if k < 4 else (200, 200, 210))
    c.ink(rect((bx0 + bx1) / 2 - 18, by0 + 8, (bx0 + bx1) / 2 + 18, by0 + 24), (236, 230, 200, 220), lw=0)
    c.stroke([(bx1 - 4, by0 + 40), (bx1 + 30, by1 - 20)], 1.6, (220, 220, 230))     # pen on a string
    c.ink(rect(bx1 + 24, by1 - 30, bx1 + 32, by1 + 10), (60, 120, 220), lw=1.6)

    # couch against the back wall
    couch(c, R, 220, 640, 0, 104, col=(220, 120, 60), seed=4)
    # throw pillows + a sleeping bag lump
    for X, col in ((300, (60, 170, 170)), (590, (250, 220, 80))):
        x_, y_ = P(X, 82, 60)
        c.ink(blob([(x_ - 30, y_ + 12), (x_ - 34, y_ - 22), (x_ - 2, y_ - 30), (x_ + 30, y_ - 20), (x_ + 26, y_ + 14)], 2),
              col, lw=2.8, shade=0.5, sw=12, hi=0.3)
    # floor lamp at the couch end (warm cone)
    lxx, lyy = P(160, 0, 40)
    ltop = P(160, 270, 40)
    c.stroke([(lxx, lyy), ltop], 6, INK, taper=(0, 0))
    c.stroke([(lxx, lyy), ltop], 3, (180, 150, 90), taper=(0, 0))
    c.ink(ell(lxx, lyy, 30, 8), (60, 40, 50), lw=2.4)
    c.light_cone((ltop[0], ltop[1] + 10), (ltop[0] - 170, lyy + 30), (ltop[0] + 170, lyy + 30), strength=0.25, blur_px=30)
    c.ink(Sh([[(ltop[0] - 30, ltop[1] - 46), (ltop[0] + 30, ltop[1] - 46), (ltop[0] + 52, ltop[1] + 10),
               (ltop[0] - 52, ltop[1] + 10)]]), (255, 214, 140), lw=3.0, shade=0.4, sw=14, hi=0.4)
    floor_lamp_glow = (ltop[0], ltop[1] - 10)
    # coffee table with pizza box, cans, cards
    R.contact(300, 600, 140, 210, 0.5)
    R.ink_box(300, 600, 36, 46, 140, 210, (130, 80, 60), top=(170, 110, 80), seed=6)
    for lx_ in (310, 586):
        for lz in (146, 202):
            c.stroke([P(lx_, 36, lz), P(lx_, 0, lz)], 5, INK, taper=(0, 0))
    pz = R.box(330, 440, 46, 54, 150, 200)
    c.ink(Sh([pz["top"]]), (230, 190, 130), lw=2.4, shade=0.2)
    c.ink(Sh([pz["front"]]), (190, 150, 100), lw=2.0)
    c.text(*P(385, 54, 175), "PIZZA", 11, (200, 50, 50))
    for X, Z, col in ((480, 170, (220, 40, 60)), (520, 160, (60, 140, 255)), (560, 190, (240, 200, 60))):
        x_, y_ = P(X, 46, Z)
        c.ink(rrect(x_ - 7, y_ - 24, x_ + 7, y_, 3), col, lw=2.0, shade=0.4, hi=0.5, hw=2)
    # TV on a cabinet (hotspot "TV")
    R.contact(790, 1030, 0, 70, 0.5)
    R.ink_box(790, 1030, 0, 90, 0, 70, (120, 70, 110), seed=7)
    for k in range(2):
        q = [P(800 + k * 115, 80, 70), P(905 + k * 115, 80, 70), P(905 + k * 115, 12, 70), P(800 + k * 115, 12, 70)]
        c.ink(Sh([q]), (140, 86, 124), lw=2.2, shade=0.3, hi=0.3)
    for k in range(5):          # stacked game cases / VHS on the shelf
        x_, y_ = P(820 + k * 18, 20, 70)
        c.ink(rect(x_, y_ - 50, x_ + 14, y_), BOOK_COLS[k], lw=1.6, shade=0.3)
    tx0, ty0 = P(820, 232, 30)
    tx1, ty1 = P(1000, 92, 30)
    crt_tv(c, tx0, ty0, tx1, ty1, seed=8)
    tv_glow = ((tx0 + tx1) / 2, (ty0 + ty1) / 2)
    # game console + tangled controllers on the floor
    x_, y_ = P(900, 0, 120)
    c.ink(rrect(x_ - 40, y_ - 16, x_ + 40, y_, 5), (60, 60, 70), lw=2.4, shade=0.3)
    cable(c, (x_ - 30, y_ - 8), P(760, 0, 200), sag=-10, w=3, col=(30, 30, 40))
    cable(c, (x_ + 30, y_ - 8), P(1040, 0, 220), sag=-14, w=3, col=(30, 30, 40))
    for X, Z in ((760, 200), (1040, 220)):
        q = P(X, 0, Z)
        c.ink(blob([(q[0] - 18, q[1]), (q[0] - 14, q[1] - 12), (q[0] + 14, q[1] - 12), (q[0] + 18, q[1])], 1), (80, 80, 96),
              lw=2.2, shade=0.3)
    # beanbag (right of the TV) + a ping-pong paddle
    bx_, by_ = P(1140, 0, 130)
    c.ink(blob([(bx_ - 80, by_), (bx_ - 90, by_ - 50), (bx_ - 40, by_ - 100), (bx_ + 30, by_ - 96), (bx_ + 84, by_ - 46),
                (bx_ + 80, by_)], 2), (130, 60, 170), lw=3.2, shade=0.55, sw=30, hi=0.35, rim=0.2)
    R.contact(1060, 1220, 110, 150, 0.4)
    # mini plant in the corner + stack of board games
    x_, y_ = P(40, 0, 30)
    for j in range(4):
        c.ink(Sh([rot_pts([(x_ - 34, y_ - 16 - j * 16), (x_ + 34, y_ - 16 - j * 16), (x_ + 34, y_ - j * 16), (x_ - 34, y_ - j * 16)],
                          (j % 2) * 5 - 2, x_, y_ - j * 16)]), BOOK_COLS[(j * 3) % len(BOOK_COLS)], lw=2.4, shade=0.4, hi=0.3)
    # ceiling: beams, pendant lamp, string lights, cables
    for z0 in (60, 300):
        R.ink_box(0, Wb, Hb - 30, Hb + 1, z0, z0 + 36, (120, 70, 104), side=(84, 44, 80), seed=z0)
    lamp_x, lamp_y = P(450, Hb - 110, 180)
    pendant_lamp(c, lamp_x, P(450, Hb, 180)[1], lamp_y, w=130, col=(60, 170, 170), cone_to=960, cone_w=380, cone_strength=0.22)
    string_lights2(c, [P(0, 400), P(300, 390), P(630, 405), P(960, 390), P(Wb, 400)], sag=34, seed=7)
    pipe(c, [P(0, Hb - 26, 0), P(Wb, Hb - 26, 0)], w=20, col=(110, 170, 180), brackets=[P(300, Hb - 26), P(900, Hb - 26)])
    cable(c, P(0, Hb, 200), P(700, Hb, 330), sag=60, w=7, col=(40, 30, 70))
    hanging_cable(c, P(1050, Hb, 250), 140, sway=-16, w=6, col=(40, 120, 130), seed=6)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    stain(c, *P(760, 380), 60, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(lamp_x, lamp_y + 200, 620, 0.45), (floor_lamp_glow[0], floor_lamp_glow[1] + 60, 360, 0.4),
                          (tv_glow[0], tv_glow[1], 360, 0.35, (90, 230, 220)),
                          (P(Wb, 270, 170)[0], 420, 260, 0.2, (140, 160, 255))],
               ambient=0.94, vign=0.6, top_dark=0.4, bottom_dark=0.35)
    c.glow2(lamp_x, lamp_y + 30, 200, GLOW, 0.3)
    c.glow2(*floor_lamp_glow, 160, GLOW, 0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_chair_back(sub, 60, 920, 360, 300)
        fg_plant(sub, 1840, 1100, 330, seed=11, flip=True)
        fg_table_edge(sub, 1000, 1500, 1012, 120)
        fg_bottles(sub, 1100, 1030, 3, 0.9, seed=5)
        fg_cable(sub, [(300, 1100), (600, 1060), (900, 1080)], 16)
        fg_lamp_top(sub, 1450, 64, 340)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_lounge.png")


LAYOUT["lounge"] = dict(
        walk_px=[(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)],
        hotspots={
            ("Hallway", 0): dict(box=(70, 370, 270, 790), stand=(250, 830)),
            ("Couch", 0): dict(box=(500, 500, 980, 730), stand=(740, 790)),
            ("TV", 0): dict(box=(1120, 440, 1370, 700), stand=(1245, 790)),
            ("Sign-up sheet", 0): dict(box=(1430, 350, 1560, 550), stand=(1495, 790)),
            ("Boomer", 0): dict(npc="hs_boomer", feet=(480, 945), stand=(720, 935)),
        },
        entries={"from_hallway": (290, 880)})


# =========================================================================== 4. Gil's room (216)
def paint_gil_room():
    c, R, rng = std_room(216 * 3, back=(360, 250, 1560, 690), light=(0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 70, 160)          # Gil's side: purple, a shade moodier than Dex's room
    LOW = (60, 120, 130)

    def ceil(sub):
        plaster_wall(sub, (100, 60, 120), (74, 40, 96), seed=41, w=sub.w, h=sub.h)
        for k in range(1, 8):
            y = sub.by(k * 110)
            sub.stroke([(0, y), (sub.w, y)], 3, (40, 20, 50), opacity=0.5, taper=(0, 0))
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 110), (60, 30, 30), 0.25, 0,
                  rng.randint(0, 99))
        # glow-in-the-dark stars stuck to the ceiling
        for _ in range(14):
            x, y = rng.uniform(0, sub.w), rng.uniform(0, sub.h)
            r = rng.uniform(8, 14)
            sub.ink(Sh([[(x + math.cos(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45),
                          y + math.sin(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45)) for i in range(10)]]),
                    (200, 255, 190), lw=1.4, shade=0, hi=0, ao=0, opacity=0.8)

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (110, 40, 120), 0.3), LOW, 42)
        # sax poster above the top bunk ("Bunk bed" hotspot)
        poster(sub, sub.ax(170), sub.by(390), 150, 120, (30, 30, 60),
               lambda p, w_, h_: (p.ink(Sh([[(w_ * 0.3, h_ * 0.15), (w_ * 0.4, h_ * 0.12), (w_ * 0.5, h_ * 0.62),
                                             (w_ * 0.64, h_ * 0.7), (w_ * 0.74, h_ * 0.5), (w_ * 0.84, h_ * 0.52),
                                             (w_ * 0.76, h_ * 0.82), (w_ * 0.56, h_ * 0.86), (w_ * 0.42, h_ * 0.7)]]),
                                         (240, 190, 60), lw=2.0, shade=0.4, hi=0.5),
                                  p.text(w_ / 2, h_ * 0.93, "SMOOTH SAX VOL.9", 9, (255, 140, 180))),
               angle=-3, seed=41, peel="br")
        poster(sub, sub.ax(420), sub.by(300), 110, 140, (255, 230, 120),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.3, "I'M", 18, (60, 40, 120)),
                                  p.text(w_ / 2, h_ * 0.52, "NOT A", 14, (60, 40, 120)),
                                  p.text(w_ / 2, h_ * 0.74, "MORNING", 13, (200, 40, 90)),
                                  p.text(w_ / 2, h_ * 0.9, "PERSON", 13, (200, 40, 90))), angle=4, seed=42)

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 43)
        x0, x1 = sub.ax(100), sub.ax(290)
        y0, y1 = sub.by(300), sub.by(0)

        def sign(cc, cx, cy):
            cc.ink(rrect(cx - 34, cy - 50, cx + 34, cy - 18, 5), (240, 200, 80), lw=2.4)
            cc.text(cx, cy - 34, "216", 18, (80, 40, 30))
        flat_door(sub, x0, y0, x1, y1, (50, 110, 90), frame=(220, 200, 210), knob="L", sign=sign, seed=44)
        # bathrobe hook + towel
        hx = sub.ax(340)
        sub.ink(rect(hx - 30, sub.by(250) - 6, hx + 30, sub.by(250) + 6), (120, 70, 50), lw=2.2)
        sub.ink(blob([(hx - 24, sub.by(250)), (hx + 24, sub.by(250)), (hx + 30, sub.by(120)), (hx - 28, sub.by(110))], 2),
                (240, 220, 80), lw=2.8, shade=0.5, sw=20, hi=0.3)

    def floor(sub):
        carpet(sub, (110, 60, 110), 0, 0, sub.w, sub.h, seed=45)
        for _ in range(16):
            x, y = rng.uniform(0, sub.w), rng.uniform(0, sub.h)
            stain(sub, x, y, rng.uniform(20, 50), (60, 30, 60), 0.18, 0, rng.randint(0, 99))

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=216 * 3)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 46, chips=6, stains=5)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=46)
    R.ao(0.5)
    R.edges(w=4.0)

    # window (back wall, right) - the air freshener hangs off its latch (separate sprite)
    wx0, wy0 = P(880, 390)
    wx1, wy1 = P(1100, 150)
    c.ink(rect(wx0 - 20, wy0 - 20, wx1 + 20, wy1 + 20), (220, 200, 220), lw=3.0, shade=0.4, hi=0.3)
    night_sky(c, wx0, wy0, wx1, wy1, seed=46)
    c.ink(rect((wx0 + wx1) / 2 - 6, wy0, (wx0 + wx1) / 2 + 6, wy1), (220, 200, 220), lw=2.4, shade=0.3)
    c.ink(rect(wx0, (wy0 + wy1) / 2 - 6, wx1, (wy0 + wy1) / 2 + 6), (220, 200, 220), lw=2.4, shade=0.3)
    latch = ((wx0 + wx1) / 2, (wy0 + wy1) / 2)
    c.ink(rrect(latch[0] - 12, latch[1] - 8, latch[0] + 12, latch[1] + 6, 3), (230, 200, 90), lw=2.0, shade=0.4, hi=0.5)
    c.stroke([(wx0 + 16, wy1 - 16), (wx0 + 70, wy0 + 16)], 10, (255, 255, 255), opacity=0.12)
    c.ink(rect(wx0 - 34, wy1 + 14, wx1 + 34, wy1 + 34), (230, 210, 226), lw=2.8, shade=0.5, sw=8, hi=0.3)
    # wilted plant + empty bottles on the sill
    px_, py_ = wx0 + 30, wy1 + 14
    c.ink(Sh([[(px_ - 16, py_ - 26), (px_ + 16, py_ - 26), (px_ + 12, py_), (px_ - 12, py_)]]), (200, 100, 70), lw=2.2, shade=0.4)
    for a in (-150, -120, -40, -10):
        r_ = math.radians(a)
        c.stroke([(px_, py_ - 26), (px_ + math.cos(r_) * 30, py_ - 26 + math.sin(r_) * 14 + 22)], 3, (110, 140, 60))
    for k, col in enumerate(((90, 160, 90), (150, 90, 60), (90, 160, 90))):
        bx = wx1 - 30 - k * 22
        c.ink(blob([(bx - 7, py_), (bx - 7, py_ - 26), (bx - 3, py_ - 34), (bx - 3, py_ - 44), (bx + 3, py_ - 44), (bx + 3, py_ - 34),
                    (bx + 7, py_ - 26), (bx + 7, py_)], 1), col, lw=2.0, shade=0.4, hi=0.5, hw=2)
    # curtain: a single droopy bedsheet nailed up
    poster(c, wx1 + 110, wy0 + 90, 100, 130, (90, 200, 200),
           lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.25, "QUIET", 15, (40, 30, 80)), p.text(w_ / 2, h_ * 0.45, "PLEASE", 13, (40, 30, 80)),
                              p.text(w_ / 2, h_ * 0.7, "(sax", 11, (200, 40, 90)), p.text(w_ / 2, h_ * 0.86, "practice)", 11, (200, 40, 90))),
           angle=5, seed=47, peel="tl")
    # records / album covers on the back wall
    for k, (X, Y, col) in enumerate(((440, 330, (255, 120, 160)), (560, 350, (90, 200, 220)), (680, 330, (250, 210, 70)))):
        x_, y_ = P(X, Y)
        c.ink(Sh([rot_pts([(x_ - 48, y_ - 48), (x_ + 48, y_ - 48), (x_ + 48, y_ + 48), (x_ - 48, y_ + 48)], (k - 1) * 4, x_, y_)]),
              col, lw=2.6, shade=0.3, hi=0.3)
        c.ink(ell(x_ + 4, y_ + 2, 30, 30), (30, 24, 40), lw=2.0, shade=0.2, hi=0.3)
        c.ink(ell(x_ + 4, y_ + 2, 9, 9), shade_col(col, 0.9), lw=1.4)
    # shelf for the alarm clock (sprite sits on it)
    sx0, sy_ = P(760, 150)
    sx1, _ = P(880, 150)
    shelf(c, sx0 - 20, sx1 + 10, sy_, 16, (130, 80, 60))
    book_row(c, sx0 - 14, sx0 + 34, sy_ - 2, 30, 46, rng, BOOK_COLS, lean_last=False)
    # turntable cabinet (hotspot "Turntable")
    R.contact(480, 700, 0, 80, 0.5)
    R.ink_box(480, 700, 0, 100, 0, 80, (90, 60, 50), top=(130, 90, 70), seed=47)
    for k in range(3):                # LP spines in the cubbies
        x_, y_ = P(500 + k * 66, 10, 80)
        for j in range(7):
            c.ink(rect(x_ + j * 8, y_ - 70, x_ + j * 8 + 6, y_), BOOK_COLS[(j + k) % len(BOOK_COLS)], lw=1.2, shade=0.2)
    tt = R.box(510, 670, 100, 116, 12, 70)
    c.ink(Sh([tt["front"]]), (50, 40, 50), lw=2.4, shade=0.2)
    c.ink(Sh([tt["top"]]), (70, 60, 76), lw=2.4, shade=0.2, hi=0.2)
    plx, ply = P(570, 116, 40)
    c.ink(ell(plx, ply, 56, 12), (30, 24, 34), lw=2.4, shade=0.2, hi=0.4)
    c.ink(ell(plx, ply, 18, 4), (255, 90, 120), lw=1.4)
    tax, tay = P(650, 116, 26)
    c.stroke([(tax, tay - 14), (tax - 18, tay - 4), (plx + 28, ply - 2)], 3.4, (200, 200, 210))
    # speakers on both sides
    for X0 in (420, 710):
        R.ink_box(X0, X0 + 52, 0, 150, 6, 60, (60, 50, 60), seed=X0)
        x_, y_ = P(X0 + 26, 100, 60)
        c.ink(ell(x_, y_, 18, 18), (30, 24, 34), lw=2.2, shade=0.2, hi=0.4)
        x_, y_ = P(X0 + 26, 40, 60)
        c.ink(ell(x_, y_, 22, 22), (30, 24, 34), lw=2.2, shade=0.2, hi=0.4)
    # bunk bed against the left wall (X 0..210, Z 40..330)
    WOOD = (150, 96, 70)
    R.contact(0, 210, 40, 330, 0.55)
    for X in (6, 196):
        for Z in (44, 316):
            R.ink_box(X, X + 14, 0, 360, Z, Z + 14, WOOD, seed=int(X + Z))
    for Y0 in (40, 230):
        R.ink_box(0, 210, Y0, Y0 + 20, 44, 330, shade_col(WOOD, 0.85), seed=Y0)
        top = R.box(4, 206, Y0 + 20, Y0 + 44, 50, 324)
        c.ink(Sh([top["front"]]), (240, 236, 226), lw=2.6, shade=0.3)
        if "top" in top:
            c.ink(Sh([top["top"]]), (250, 246, 236), lw=2.6, shade=0.2)
        if "right" in top:
            c.ink(Sh([top["right"]]), (220, 214, 204), lw=2.4, shade=0.2)
    # bottom bunk: plaid blanket heap (Boomer's), top bunk: Gil's tangled duvet
    heap = [P(10, 66, 120), P(200, 70, 110), P(214, 40, 160), P(214, 30, 300), P(196, 70, 326), P(20, 72, 320)]
    c.ink(blob(heap, 2), (190, 60, 70), lw=3.2, shade=0.55, sw=26, hi=0.35)
    clip_draw(c, blob(heap, 2), lambda t: [t.stroke([P(X, 80, 100), P(X + 30, 30, 340)], 4, (240, 200, 90), taper=(0, 0), opacity=0.7)
                                          for X in range(0, 240, 40)])
    c.ink(blob(heap, 2), (0, 0, 0, 0), lw=3.2, line_only=True)
    duvet = [P(10, 254, 90), P(200, 258, 80), P(214, 236, 140), P(214, 210, 260), P(196, 256, 326), P(20, 260, 320)]
    c.ink(blob(duvet, 2), (60, 150, 200), lw=3.2, shade=0.55, sw=26, hi=0.35, rim=0.15)
    c.ink(blob([P(30, 258, 60), P(160, 260, 56), P(160, 284, 66), P(30, 284, 70)], 2), (250, 246, 240), lw=2.8, shade=0.4)
    # ladder up the front of the bunk
    for Z in (290, 322):
        c.stroke([P(214, 0, Z), P(214, 260, Z)], 6, INK, taper=(0, 0))
        c.stroke([P(214, 0, Z), P(214, 260, Z)], 3, hi_col(WOOD, 0.2), taper=(0, 0))
    for Y in range(40, 260, 50):
        c.stroke([P(214, Y, 290), P(214, Y, 322)], 5, INK, taper=(0, 0))
    # sock dangling from the top bunk
    sx_, sy2 = P(212, 236, 220)
    c.ink(blob([(sx_, sy2), (sx_ + 16, sy2), (sx_ + 18, sy2 + 46), (sx_ + 34, sy2 + 58), (sx_ + 14, sy2 + 66), (sx_ + 2, sy2 + 44)], 2),
          (250, 250, 240), lw=2.4, shade=0.4)
    # record crate on the floor (hotspot "Record crate")
    R.contact(280, 400, 110, 190, 0.5)
    f = R.ink_box(280, 400, 0, 60, 110, 190, (200, 150, 90), seed=48)
    for k in range(3):
        a, b_ = P(284, 14 + k * 18, 190), P(396, 14 + k * 18, 190)
        c.stroke([a, b_], 2.0, shade_col((200, 150, 90), 0.6), opacity=0.8)
    for k in range(8):
        x_, y_ = P(292 + k * 13, 60, 150)
        c.ink(Sh([rot_pts([(x_ - 5, y_ - 40), (x_ + 5, y_ - 40), (x_ + 5, y_), (x_ - 5, y_)], -10 + k * 3, x_, y_)]),
              BOOK_COLS[k % len(BOOK_COLS)], lw=1.6, shade=0.3)
    x_, y_ = P(340, 60, 190)
    c.text(x_, y_ + 26, "JAZZ?", 11, (90, 40, 30))
    # lava lamp + mini fridge in the right corner, laundry mountain by the door
    R.ink_box(1110, 1190, 0, 96, 10, 80, (236, 232, 236), seed=49)
    lx_, ly_ = P(1150, 96, 40)
    c.ink(blob([(lx_ - 6, ly_ - 4), (lx_ + 6, ly_ - 4), (lx_ + 12, ly_ - 46), (lx_ + 4, ly_ - 66), (lx_ - 4, ly_ - 66),
                (lx_ - 12, ly_ - 46)], 2), (90, 230, 160), lw=2.6, shade=0.3, hi=0.6, hw=4)
    c.glow2(lx_, ly_ - 36, 120, (90, 255, 170), 0.3)
    lp = P(Wb - 70, 0, 360)
    k = R.k(360)
    for j, col in enumerate([(200, 60, 70), (60, 150, 200), (240, 220, 80), (250, 250, 240)]):
        ox_ = (j - 1.5) * 22 * k
        c.ink(blob([(lp[0] + ox_ - 44 * k, lp[1]), (lp[0] + ox_ - 30 * k, lp[1] - (40 + j * 8) * k), (lp[0] + ox_, lp[1] - (56 + j * 5) * k),
                    (lp[0] + ox_ + 36 * k, lp[1] - 28 * k), (lp[0] + ox_ + 44 * k, lp[1])], 2), col, lw=3.0, shade=0.55, sw=14 * k,
              hi=0.3)
    # floor clutter: mugs, pizza crust, sheet music
    for X, Z in ((720, 170), (980, 200)):
        x_, y_ = P(X, 0, Z)
        c.ink(rrect(x_ - 10, y_ - 22, x_ + 10, y_, 4), (240, 240, 230), lw=2.2, shade=0.4)
        c.ink(ell(x_ + 13, y_ - 12, 5, 6), (0, 0, 0, 0), lw=2.0, line_only=True)
    for k in range(4):
        x_, y_ = P(820 + k * 40, 0, 230 + (k % 2) * 20)
        c.ink(Sh([rot_pts([(x_ - 22, y_ - 6), (x_ + 22, y_ - 6), (x_ + 22, y_ + 6), (x_ - 22, y_ + 6)], k * 20 - 30, x_, y_)]),
              (250, 248, 236), lw=1.8)
    # ceiling: bare bulb, cables, cobwebs
    bx_, by_ = P(640, Hb - 120, 220)
    bulb(c, bx_, by_, 11, cord_from=P(640, Hb, 220))
    c.light_cone((bx_, by_ + 10), (bx_ - 520, 1000), (bx_ + 520, 1000), strength=0.18, blur_px=36)
    cable(c, P(0, Hb, 160), P(640, Hb, 220), sag=50, w=6, col=(40, 30, 70))
    cable(c, P(640, Hb, 220), P(Wb, Hb, 120), sag=60, w=6, col=(40, 120, 130))
    pipe(c, [P(0, Hb - 24, 0), P(Wb, Hb - 24, 0)], w=20, col=(170, 120, 190), brackets=[P(300, Hb - 24), P(900, Hb - 24)])
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    hanging_web(c, *P(980, Hb, 30), 60)

    room_grade(c, lights=[(bx_, by_ + 220, 700, 0.45), (lx_, ly_ - 30, 220, 0.3, (90, 255, 170)),
                          ((wx0 + wx1) / 2, (wy0 + wy1) / 2, 300, 0.25, (140, 160, 255))],
               ambient=0.92, vign=0.6, top_dark=0.4, bottom_dark=0.35)
    c.glow2(bx_, by_, 120, (255, 246, 210), 0.5)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 120, 1040, 4, 1.05, seed=21)
        fg_chair_back(sub, 1860, 900, 320, 300)
        fg_table_edge(sub, 600, 1150, 1015, 120)
        fg_cable(sub, [(1100, 1100), (1400, 1060), (1700, 1090)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_gil_room.png")


LAYOUT["gil_room"] = dict(
        walk_px=[(400, Y_TOP), (1680, Y_TOP), (1800, 880), (1720, Y_BOT), (260, Y_BOT), (200, 890), (390, 830)],
        hotspots={
            ("Door to hallway", 0): dict(box=(1620, 360, 1800, 790), stand=(1640, 850)),
            ("Bunk bed", 0): dict(box=(80, 200, 560, 810), stand=(560, 850)),
            ("Record crate", 0): dict(box=(610, 640, 780, 750), stand=(700, 800)),
            ("Boomer", 0): dict(npc="hs_boomer", feet=(760, 945), stand=(1010, 935)),
            ("Turntable", 0): dict(box=(830, 500, 1070, 640), stand=(950, 790)),
            ("Alarm clock", 0): dict(sprite="hs_alarm_clock", feet=(1200, 540), stand=(1200, 790)),
            ("Air freshener", 0): dict(sprite="hs_air_freshener", feet=(1350, 522), stand=(1350, 790)),
        },
        entries={"from_hallway": (1620, 900)})


# =========================================================================== 5. Library
def bookcase(c, R, X0, X1, Y1, Z0, Z1, rng, wood=(120, 70, 60), shelves=5, gaps=0.08, dust=False):
    """Tall bookcase standing against the back wall, filled with wobbly book rows."""
    R.contact(X0, X1, Z0, Z1, 0.55)
    f = R.ink_box(X0, X1, 0, Y1, Z0, Z1, wood, seed=int(X0))
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    k = R.k(Z1)
    t = 12 * k
    c.ink(rect(x0 + t, y0 + t, x1 - t, y1 - t * 0.6), shade_col(wood, 0.45), lw=2.4, shade=0.2, hi=0, ao=0.2)
    hs = (y1 - y0 - 2 * t) / shelves
    for i in range(shelves):
        yb = y0 + t + hs * (i + 1)
        book_row(c, x0 + t + 4, x1 - t - 4, yb - 6 * k, hs * 0.55, hs * 0.86, rng,
                 [mix(col, (60, 30, 70), 0.25 if not dust else 0.45) for col in BOOK_COLS])
        if rng.random() < gaps * 6:
            gx = rng.uniform(x0 + t + 10, x1 - t - 60)
            c.ink(rect(gx, yb - hs * 0.9, gx + rng.uniform(26, 50), yb - 6 * k), shade_col(wood, 0.4), lw=0, shade=0, hi=0, ao=0)
        c.ink(rect(x0 + t * 0.5, yb - 6 * k, x1 - t * 0.5, yb + 4 * k), hi_col(wood, 0.1), lw=2.2, shade=0.3, hi=0.4, hw=2)
        if dust:
            hanging_web(c, rng.uniform(x0 + 30, x1 - 30), yb + 2, rng.uniform(18, 40), opacity=0.35)
    return f


def banker_lamp(c, x, y, s=1.0, col=(40, 150, 90)):
    c.stroke([(x, y), (x, y - 40 * s)], 4 * s, (200, 170, 80))
    c.ink(ell(x, y, 22 * s, 6 * s), (200, 170, 80), lw=2.2, shade=0.4, hi=0.4)
    c.ink(blob([(x - 40 * s, y - 34 * s), (x - 30 * s, y - 52 * s), (x + 30 * s, y - 52 * s), (x + 40 * s, y - 34 * s)], 1), col,
          lw=2.6, shade=0.4, hi=0.6, hw=4, rim=0.2)
    c.glow2(x, y - 30 * s, 150 * s, GLOW, 0.45)
    c.light_cone((x, y - 34 * s), (x - 90 * s, y + 40 * s), (x + 90 * s, y + 40 * s), strength=0.35, blur_px=14)


def paint_library():
    c, R, rng = std_room(500, back=(300, 200, 1620, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (170, 60, 130)
    WOOD = (120, 70, 60)

    def ceil(sub):
        plaster_wall(sub, (96, 60, 110), (70, 40, 90), seed=51, w=sub.w, h=sub.h)
        step = 140 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.ink(rect(x - 8, 0, x + 8, sub.h), (120, 76, 70), lw=2.2, shade=0.3, hi=0.3)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 110), (60, 30, 30), 0.25, 0, rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (110, 40, 120), 0.3), (110, 60, 56), 52, low_kind="wood", split=0.62)
        x0, x1 = sub.ax(280), sub.ax(100)
        y0, y1 = sub.by(300), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (120, 60, 50), frame=(200, 160, 120), knob="R", window=True, seed=53)
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 110, "EXIT")
        poster(sub, sub.ax(400), sub.by(330), 120, 150, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.2, "READ", 18, (40, 120, 140)),
                                  p.text(w_ / 2, h_ * 0.4, "MORE", 18, (40, 120, 140)),
                                  p.ink(rect(w_ * 0.3, h_ * 0.55, w_ * 0.7, h_ * 0.8), (220, 60, 90), lw=1.6),
                                  p.text(w_ / 2, h_ * 0.92, "(or at least hold one)", 6.5, (90, 40, 80), "Bold")),
               angle=-3, seed=54, peel="tr")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.03), (110, 60, 56), 55, low_kind="wood", split=0.62)
        # tall window
        x0, x1 = sub.ax(60), sub.ax(260)
        y0, y1 = sub.by(440), sub.by(200)
        window_flat(sub, x0, y0, x1, y1, frame=(220, 196, 170), seed=56, mullions=1, transoms=2)

    def floor(sub):
        tiles(sub, (130, 60, 80), (200, 170, 140), 0, 0, sub.w, sub.h, size=64 * sub.density, seed=57, chipped=0.06)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=500)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, (110, 60, 56), 58, chips=6, stains=4, low_kind="wood", split=0.62)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=58)
    R.ao(0.5)
    R.edges(w=4.0)

    # long runner rug down the middle
    rug = [P(220, 0, 230), P(1120, 0, 230), P(1140, 0, 470), P(200, 0, 470)]
    c.ink(blob(rug, 1), (60, 110, 120), lw=3.0, shade=0.15, hi=0.05, tex=0.3)
    c.ink(blob([P(250, 0, 250), P(1090, 0, 250), P(1110, 0, 450), P(230, 0, 450)], 1), (0, 0, 0, 0), lw=2.4, line_only=True)

    # bookcases along the back wall (the middle block = hotspot "Bookshelves")
    bookcase(c, R, 190, 420, 300, 0, 50, rng, WOOD)
    bookcase(c, R, 640, 980, 420, 0, 56, rng, WOOD, shelves=6)
    bookcase(c, R, 1100, 1300, 300, 0, 50, rng, WOOD)
    # "SILENCE" sign + clock between the bookcases
    sx_, sy_ = P(530, 380)
    c.ink(rrect(sx_ - 90, sy_ - 26, sx_ + 90, sy_ + 26, 6), (40, 30, 60), lw=2.8, shade=0.3, hi=0.2)
    c.text(sx_, sy_, "SILENCE", 24, (255, 220, 120))
    c.glow2(sx_, sy_, 160, (255, 200, 120), 0.18)
    cx_, cy_ = P(530, 270)
    c.ink(ell(cx_, cy_, 34, 34), (250, 240, 220), lw=3.2, shade=0.4, sw=10, hi=0.3)
    c.stroke([(cx_, cy_), (cx_, cy_ - 22)], 3)
    c.stroke([(cx_, cy_), (cx_ - 16, cy_ + 6)], 3)
    # bust on top of the right bookcase, plant on the left one
    bx_, by_ = P(1200, 300, 25)
    c.stroke([(bx_, by_), (bx_, by_ - 24)], 5, (200, 170, 80))
    c.ink(ell(bx_, by_, 20, 6), (200, 170, 80), lw=2.2, shade=0.4)
    c.ink(ell(bx_, by_ - 56, 32, 32), (70, 150, 200), lw=2.8, shade=0.55, sw=12, hi=0.5, rim=0.2)
    c.ink(blob([(bx_ - 14, by_ - 76), (bx_ + 6, by_ - 80), (bx_ + 12, by_ - 60), (bx_ - 4, by_ - 44), (bx_ - 18, by_ - 56)], 2),
          (110, 190, 90), lw=1.6, shade=0.3, atop=True)
    c.stroke([(bx_ - 34, by_ - 40), (bx_ + 4, by_ - 96)], 3, (200, 170, 80))
    px_, py_ = P(300, 300, 25)
    c.ink(rrect(px_ - 22, py_ - 34, px_ + 22, py_, 6), (200, 100, 70), lw=2.4, shade=0.4)
    for k in range(7):
        a = math.radians(-160 + k * 23)
        c.ink(ell(px_ + math.cos(a) * 26, py_ - 44 + math.sin(a) * 22, 16, 6, math.degrees(a)), (70, 170, 90), lw=2, shade=0.4)
    # ceiling hatch to the stacks + rolling ladder (hotspot "Ladder to the stacks")
    hx0, hx1 = 1000, 1100
    hatch = [P(hx0, Hb, 10), P(hx1, Hb, 10), P(hx1, Hb, 110), P(hx0, Hb, 110)]
    c.ink(Sh([hatch]), (40, 24, 40), lw=3.0, shade=0.1, hi=0)
    c.glow2(*P(1050, Hb, 60), 120, GLOW, 0.35)
    c.ink(Sh([[P(hx0, Hb, 10), P(hx1, Hb, 10), P(hx1, Hb + 40, 0), P(hx0, Hb + 40, 0)]]), (130, 80, 60), lw=2.6, shade=0.3)
    for X in (1010, 1090):
        a, b_ = P(X, 0, 90), P(X, Hb, 30)
        c.stroke([a, b_], 12, INK, taper=(0, 0))
        c.stroke([a, b_], 7, (180, 120, 70), taper=(0, 0))
    for k in range(1, 14):
        t = k / 14
        Y = Hb * t
        Z = 90 - 60 * t
        c.stroke([P(1010, Y, Z), P(1090, Y, Z)], 7, INK, taper=(0, 0))
        c.stroke([P(1010, Y, Z), P(1090, Y, Z)], 3.4, (200, 140, 80), taper=(0, 0))
    for X in (1010, 1090):
        c.ink(ell(*P(X, 0, 92), 9, 7), (60, 60, 70), lw=2.0)
    hs = P(1050, Hb - 30, 40)
    c.ink(rrect(hs[0] - 70, hs[1] - 16, hs[0] + 70, hs[1] + 16, 4), (255, 230, 120), lw=2.2, shade=0.2)
    c.text(hs[0], hs[1], "STACKS: STAFF ONLY", 10, (150, 40, 60))
    # card catalogue (back-left corner)
    R.contact(30, 170, 0, 70, 0.5)
    f = R.ink_box(30, 170, 0, 150, 0, 70, (150, 96, 64), seed=59)
    for r_ in range(4):
        for col_ in range(3):
            X = 40 + col_ * 44
            Y = 14 + r_ * 34
            q = [P(X + 2, Y + 30, 70), P(X + 40, Y + 30, 70), P(X + 40, Y + 2, 70), P(X + 2, Y + 2, 70)]
            c.ink(Sh([q]), (176, 116, 80), lw=1.8, shade=0.3, hi=0.3)
            hx_, hy_ = P(X + 21, Y + 12, 70)
            c.ink(rrect(hx_ - 6, hy_ - 2, hx_ + 6, hy_ + 3, 2), (236, 196, 90), lw=1.2)
    # one drawer pulled out with cards
    q = P(84, 116, 70)
    k = R.k(70)
    c.ink(Sh([[(q[0] - 20 * k, q[1]), (q[0] + 20 * k, q[1]), (q[0] + 24 * k, q[1] + 26), (q[0] - 24 * k, q[1] + 26)]]), (176, 116, 80),
          lw=2.0, shade=0.3)
    for j in range(5):
        c.ink(rect(q[0] - 16 * k + j * 7, q[1] - 10, q[0] - 10 * k + j * 7, q[1] + 6), (250, 248, 236), lw=1.0)
    # circulation desk (hotspot "Front desk")
    R.contact(250, 600, 120, 220, 0.55)
    R.ink_box(250, 600, 0, 110, 120, 220, (110, 60, 50), top=(170, 110, 80), seed=60)
    for k in range(4):
        q = [P(266 + k * 84, 96, 220), P(334 + k * 84, 96, 220), P(334 + k * 84, 14, 220), P(266 + k * 84, 14, 220)]
        c.ink(Sh([q]), (130, 74, 60), lw=2.2, shade=0.2, hi=0.3, light=(0.45, 0.89))
    # bell, stamp, book stack, "RETURNS" slot, banker lamp, nameplate
    bx_, by_ = P(300, 110, 170)
    c.ink(Sh([[(bx_ - 16, by_), (bx_ + 16, by_), (bx_ + 12, by_ - 16), (bx_, by_ - 22), (bx_ - 12, by_ - 16)]]), (236, 196, 90), lw=2.2,
          shade=0.4, hi=0.6)
    for j in range(5):
        x_, y_ = P(420, 110, 160)
        c.ink(Sh([rot_pts([(x_ - 34, y_ - 12 - j * 12), (x_ + 34, y_ - 12 - j * 12), (x_ + 34, y_ - j * 12), (x_ - 34, y_ - j * 12)],
                          (j % 2) * 5 - 2, x_, y_ - j * 12)]), BOOK_COLS[j % len(BOOK_COLS)], lw=2.2, shade=0.4, hi=0.3)
    banker_lamp(c, *P(540, 110, 150), 1.0)
    npx, npy = P(425, 70, 221)
    c.ink(rrect(npx - 60, npy - 16, npx + 60, npy + 16, 4), (236, 196, 90), lw=2.2, shade=0.3, hi=0.4)
    c.text(npx, npy, "MS. HUSH", 13, (60, 30, 30))
    # reading table (right) with lamps, open books, a sleeping laptop
    for X in (1120, 1240):          # chairs on the far side
        R.ink_box(X - 22, X + 22, 0, 130, 96, 108, (90, 50, 40), seed=X)
        R.ink_box(X - 22, X + 22, 40, 48, 96, 130, (110, 64, 50), seed=X + 1)
    R.contact(1080, 1280, 120, 220, 0.55)
    R.ink_box(1080, 1280, 66, 76, 120, 220, WOOD, top=(170, 110, 80), seed=61)
    for X in (1092, 1266):
        for Z in (126, 214):
            c.stroke([P(X, 66, Z), P(X, 0, Z)], 6, INK, taper=(0, 0))
    banker_lamp(c, *P(1130, 76, 160), 0.9)
    banker_lamp(c, *P(1240, 76, 160), 0.9, col=(60, 120, 180))
    for X, Z in ((1170, 190), (1215, 180)):
        x_, y_ = P(X, 76, Z)
        c.ink(Sh([[(x_ - 26, y_ - 4), (x_, y_ - 10), (x_ + 26, y_ - 4), (x_ + 24, y_ + 6), (x_, y_), (x_ - 24, y_ + 6)]]), (250, 246, 230),
              lw=1.8, shade=0.2)
    # pendant lamps
    lamps = []
    for X, Z in ((380, 240), (900, 260)):
        lx, ly = P(X, Hb - 120, Z)
        pendant_lamp(c, lx, P(X, Hb, Z)[1], ly, w=120, col=(40, 140, 90), cone_to=980, cone_w=360, cone_strength=0.2)
        lamps.append((lx, ly))
    cable(c, P(0, Hb, 120), P(700, Hb, 240), sag=40, w=6, col=(40, 30, 70))
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    hanging_web(c, *P(700, Hb, 20), 70)
    stain(c, *P(1040, 450), 60, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 220, 520, 0.4), (lamps[1][0], lamps[1][1] + 220, 520, 0.4),
                          (P(1180, 120, 160)[0], P(1180, 120, 160)[1], 360, 0.35),
                          (P(1050, Hb, 60)[0], P(1050, Hb, 60)[1] + 30, 220, 0.3),
                          (P(Wb, 300, 160)[0], 400, 300, 0.2, (140, 160, 255))],
               ambient=0.92, vign=0.6, top_dark=0.4, bottom_dark=0.35)
    for lx, ly in lamps:
        c.glow2(lx, ly + 30, 180, GLOW, 0.3)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 60, 1100, 360, seed=31)
        fg_table_edge(sub, 1300, 1980, 1010, 120)
        for j in range(3):      # stack of books on the near table edge
            sub.ink(rect(1440 + j * 6, 1056 - j * 26, 1640 - j * 8, 1082 - j * 26), FG, lw=0, shade=0.2, hi=0.2, ao=0)
        fg_cable(sub, [(200, 1100), (500, 1070), (900, 1090)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_library.png")


LAYOUT["library"] = dict(
        walk_px=[(170, Y_TOP), (1780, Y_TOP), (1880, 880), (1860, Y_BOT), (250, Y_BOT), (110, 880)],
        hotspots={
            ("Exit", 0): dict(box=(40, 360, 240, 790), stand=(250, 850)),
            ("Front desk", 0): dict(box=(430, 580, 890, 760), stand=(660, 800)),
            ("Ms. Hush", 0): dict(npc="hs_ms_hush", feet=(1290, 945), stand=(1470, 935)),
            ("Bookshelves", 0): dict(box=(940, 260, 1280, 690), stand=(1110, 790)),
            ("Reading table", 0): dict(box=(1490, 600, 1760, 760), stand=(1620, 800)),
            ("Ivy", 0): dict(npc="hs_ivy", feet=(1800, 945), stand=(1640, 935)),
            ("Ladder to the stacks", 0): dict(box=(1300, 200, 1400, 690), stand=(1350, 790)),
            ("Card catalogue", 0): dict(box=(280, 530, 440, 710), stand=(380, 790)),
            ("Ms. Hush", 1): dict(npc="hs_ms_hush", feet=(500, 945), stand=(700, 935)),
        },
        entries={"from_campus": (280, 900), "from_stacks": (1350, 800)})


# =========================================================================== 6. Student union (grill)
def paint_student_union():
    c, R, rng = std_room(600, back=(330, 240, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (214, 86, 150)
    LOW = (40, 140, 150)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (120, 100, 140), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 90 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 2.6, (100, 90, 120), taper=(0, 0))
        for y in np.arange(0, sub.h, step * 0.8):
            sub.stroke([(0, y), (sub.w, y)], 2.6, (100, 90, 120), taper=(0, 0))
        for _ in range(9):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (120, 80, 40), 0.25, 0, rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (150, 50, 130), 0.25), LOW, 61)
        x0, x1 = sub.ax(290), sub.ax(100)
        y0, y1 = sub.by(310), sub.by(0)
        # glass double doors onto the quad (night outside)
        sub.ink(rect(x0 - 22, y0 - 22, x1 + 22, y1), (200, 196, 210), lw=3.0, shade=0.4)
        night_sky(sub, x0, y0, x1, y1, seed=62, bot=(120, 60, 140))
        xm = (x0 + x1) / 2
        for xx in (x0, xm, x1):
            sub.ink(rect(xx - 8, y0, xx + 8, y1), (200, 196, 210), lw=2.4, shade=0.3)
        for xx in (xm - 30, xm + 30):
            sub.ink(rrect(xx - 5, y0 + (y1 - y0) * 0.45, xx + 5, y0 + (y1 - y0) * 0.6, 3), (230, 230, 240), lw=2.0)
        sub.stroke([(x0 + 20, y1 - 30), (xm - 20, y0 + 30)], 10, (255, 255, 255), opacity=0.14)
        exit_sign(sub, xm, y0 - 50, 110, "QUAD")
        poster(sub, sub.ax(420), sub.by(320), 110, 140, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.2, "TRY THE", 12, (40, 120, 140)),
                                  p.text(w_ / 2, h_ * 0.42, "POSSUM", 16, (200, 40, 90)),
                                  p.text(w_ / 2, h_ * 0.6, "WAFFLE", 16, (200, 40, 90)),
                                  p.text(w_ / 2, h_ * 0.85, "it's not possum", 7, (90, 40, 80), "Bold")),
               angle=-4, seed=63, peel="br")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 64)
        for k, (za, zb) in enumerate(((50, 200), (240, 390))):
            window_flat(sub, sub.ax(za), sub.by(380), sub.ax(zb), sub.by(180), seed=65 + k, mullions=1, transoms=0)

    def floor(sub):
        tiles(sub, (90, 180, 180), (236, 226, 200), 0, 0, sub.w, sub.h, size=58 * sub.density, seed=66, chipped=0.1)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=600)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 67, chips=6, stains=4)
        # white tile splash-back behind the grill
        x0, x1 = sub.ax(40), sub.ax(640)
        y0, y1 = sub.by(250), sub.by(100)
        tiles(sub, (236, 232, 226), (220, 216, 210), x0, y0, x1, y1, size=30, seed=68, chipped=0.15)
        for _ in range(5):
            stain(sub, rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(20, 50), (120, 80, 40), 0.3, 2, rng.randint(0, 99))
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=67)
    R.ao(0.5)
    R.edges(w=4.0)

    # menu board (hotspot "Menu board")
    mx0, my0 = P(120, 436)
    mx1, my1 = P(560, 296)
    c.ink(rect(mx0 - 14, my0 - 14, mx1 + 14, my1 + 14), (60, 40, 40), lw=3.2, shade=0.4, hi=0.3)
    c.ink(rect(mx0, my0, mx1, my1), (30, 40, 40), lw=2.4, shade=0.2, tex=0.3)
    c.text((mx0 + mx1) / 2, my0 + 22, "THE GREASY POSSUM GRILL", 16, (255, 220, 120))
    items = [("POSSUM WAFFLE", "3.50"), ("SOUP OF THE DAY", "???"), ("FRIES (ONE SIZE: HUGE)", "2.00"),
             ("MYSTERY BURGER", "4.00"), ("COFFEE-ADJACENT", "1.00")]
    for k, (a, b_) in enumerate(items):
        y = my0 + 50 + k * 18
        c.text(mx0 + 20, y, a, 10, (230, 240, 240), "Bold", anchor="lm")
        c.text(mx1 - 20, y, b_, 10, (255, 140, 180), "Bold", anchor="rm")
    c.ink(rect(mx1 - 120, my0 + 40, mx1 - 30, my0 + 60), (30, 40, 40), lw=0, shade=0, hi=0, ao=0, opacity=0.0)
    c.stroke([(mx0 + 230, my0 + 88), (mx1 - 60, my0 + 88)], 2.2, (255, 255, 255), opacity=0.8)   # crossed-out price
    c.glow2((mx0 + mx1) / 2, (my0 + my1) / 2, 300, (255, 230, 160), 0.15)
    # extractor hood above the grill
    hood = R.box(40, 640, 262, 280, 0, 70)
    c.ink(Sh([hood["bottom"]]) if "bottom" in hood else Sh([hood["front"]]), (150, 150, 160), lw=2.6, shade=0.2)
    c.ink(Sh([hood["front"]]), (190, 190, 200), lw=2.8, shade=0.3, hi=0.4)
    # grill counter (hotspot "Grill counter")
    R.contact(40, 640, 0, 90, 0.55)
    R.ink_box(40, 640, 0, 110, 0, 90, (200, 200, 210), top=(150, 150, 160), seed=69)
    for k in range(5):
        q = [P(56 + k * 118, 96, 90), P(150 + k * 118, 96, 90), P(150 + k * 118, 14, 90), P(56 + k * 118, 14, 90)]
        c.ink(Sh([q]), (180, 180, 192), lw=2.0, shade=0.3, hi=0.3)
    c.ink(Sh([[P(40, 80, 91), P(640, 80, 91), P(640, 60, 91), P(40, 60, 91)]]), (220, 60, 80), lw=2.0, shade=0.3)   # red stripe
    # griddle with sizzling things + steam
    gq = [P(60, 112, 10), P(300, 112, 10), P(300, 112, 80), P(60, 112, 80)]
    c.ink(Sh([gq]), (60, 56, 64), lw=2.4, shade=0.2, hi=0.3)
    for X, Z in ((100, 40), (160, 55), (220, 35)):
        x_, y_ = P(X, 114, Z)
        c.ink(ell(x_, y_, 20, 7), (160, 90, 50), lw=2.0, shade=0.4, hi=0.3)
    for X in (110, 190, 260):
        x_, y_ = P(X, 120, 40)
        c.stroke([(x_, y_), (x_ - 8, y_ - 30), (x_ + 6, y_ - 60), (x_ - 4, y_ - 90)], 6, (255, 255, 255), opacity=0.25)
    # possum waffle iron
    wx_, wy_ = P(380, 110, 40)
    c.ink(ell(wx_, wy_ - 10, 46, 16), (60, 60, 70), lw=2.6, shade=0.4, hi=0.4)
    c.ink(blob([(wx_ - 40, wy_ - 16), (wx_ - 34, wy_ - 50), (wx_, wy_ - 62), (wx_ + 34, wy_ - 50), (wx_ + 40, wy_ - 16)], 2),
          (120, 120, 130), lw=2.6, shade=0.5, hi=0.5)
    for dx in (-24, 24):        # ears
        c.ink(ell(wx_ + dx, wy_ - 58, 12, 12), (120, 120, 130), lw=2.4, shade=0.4)
        c.ink(ell(wx_ + dx, wy_ - 58, 6, 6), (255, 160, 180), lw=1.2)
    c.ink(ell(wx_, wy_ - 34, 8, 6), (255, 160, 180), lw=1.6)
    c.stroke([(wx_ + 40, wy_ - 30), (wx_ + 80, wy_ - 40)], 6, INK)
    # soup pot
    sx_, sy_ = P(520, 110, 40)
    c.ink(rrect(sx_ - 40, sy_ - 64, sx_ + 40, sy_, 8), (190, 190, 200), lw=2.8, shade=0.5, sw=16, hi=0.5)
    c.ink(ell(sx_, sy_ - 64, 40, 9), (140, 170, 60), lw=2.4, shade=0.2)
    c.ink(ell(sx_ + 10, sy_ - 66, 7, 3), (200, 230, 90), lw=0, shade=0, hi=0)
    for dx in (-46, 46):
        c.ink(rrect(sx_ + dx - 8, sy_ - 54, sx_ + dx + 8, sy_ - 46, 3), (150, 150, 160), lw=2.0)
    c.stroke([(sx_ + 10, sy_ - 64), (sx_ + 26, sy_ - 120)], 5, INK)
    c.stroke([(sx_ + 10, sy_ - 64), (sx_ + 26, sy_ - 120)], 2.6, (180, 130, 90))
    for k in range(2):
        x_ = sx_ - 16 + k * 26
        c.stroke([(x_, sy_ - 70), (x_ - 6, sy_ - 100), (x_ + 6, sy_ - 130)], 6, (200, 255, 160), opacity=0.25)
    # napkin dispenser + ketchup at the counter end
    nx_, ny_ = P(600, 110, 50)
    c.ink(rrect(nx_ - 16, ny_ - 30, nx_ + 16, ny_, 3), (200, 200, 210), lw=2.2, shade=0.4, hi=0.5)
    c.ink(Sh([[(nx_ + 26, ny_), (nx_ + 26, ny_ - 30), (nx_ + 30, ny_ - 40), (nx_ + 34, ny_ - 30), (nx_ + 34, ny_)]]), (220, 40, 50),
          lw=2.0, shade=0.4, hi=0.5)
    # soda fountain (hotspot "Soda fountain") on a cabinet, with OUT OF ORDER signs
    R.contact(780, 950, 0, 70, 0.5)
    R.ink_box(780, 950, 0, 90, 0, 70, (60, 140, 150), seed=70)
    f = R.ink_box(800, 930, 90, 220, 6, 60, (230, 60, 80), seed=71)
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    c.ink(rect(x0 + 10, y0 + 12, x1 - 10, y0 + 46), (255, 236, 160), lw=2.2, shade=0.2)
    c.text((x0 + x1) / 2, y0 + 29, "FIZZ", 16, (200, 40, 60))
    for k in range(3):
        xx = x0 + 24 + k * (x1 - x0 - 48) / 2
        c.ink(rect(xx - 8, y0 + 60, xx + 8, y0 + 86), (200, 200, 210), lw=2.0, shade=0.3, hi=0.5)
        c.stroke([(xx, y0 + 86), (xx, y0 + 96)], 4, (200, 200, 210))
    for k, (dx, dy, a) in enumerate(((-6, 50, -8), (14, 96, 6))):
        cx_, cy_ = (x0 + x1) / 2 + dx, y0 + dy
        c.ink(Sh([rot_pts([(cx_ - 50, cy_ - 16), (cx_ + 50, cy_ - 16), (cx_ + 50, cy_ + 16), (cx_ - 50, cy_ + 16)], a, cx_, cy_)]),
              (252, 250, 240), lw=1.8, shade=0.2)
        c.text(cx_, cy_ - 4, "OUT OF", 9, (200, 30, 50), angle=-a)
        c.text(cx_, cy_ + 8, "ORDER" if k == 0 else "ORDER (2)", 9, (200, 30, 50), angle=-a)
    c.ink(Sh([[(x0 + 6, y1), (x1 - 6, y1), (x1 - 2, y1 + 4), (x0 + 2, y1 + 4)]]), (180, 180, 190), lw=1.6)
    # puddle under it
    px_, py_ = P(860, 0, 100)
    c.ink(blob([(px_ - 50, py_), (px_ - 20, py_ - 10), (px_ + 30, py_ - 8), (px_ + 60, py_ + 2), (px_ + 10, py_ + 10)], 2),
          (150, 220, 230, 200), lw=1.6, shade=0, hi=0.5, hw=3)
    # bulletin board (hotspot "Bulletin board") with the STACKS SLAM poster
    bx0, by0 = P(1060, 360)
    bx1, by1 = P(1230, 180)
    c.ink(rect(bx0 - 12, by0 - 12, bx1 + 12, by1 + 12), (130, 80, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(bx0, by0, bx1, by1), (196, 146, 96), lw=2.0, shade=0.2, tex=0.4)
    poster(c, bx0 + 70, by0 + 80, 100, 130, (40, 30, 70),
           lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.18, "STACKS", 15, (255, 220, 120)),
                              p.text(w_ / 2, h_ * 0.36, "SLAM", 20, (255, 120, 170)),
                              p.ink(ell(w_ / 2, h_ * 0.62, 10, 14), (200, 200, 210), lw=1.6),
                              p.stroke([(w_ / 2, h_ * 0.7), (w_ / 2, h_ * 0.82)], 2, (200, 200, 210)),
                              p.text(w_ / 2, h_ * 0.92, "TONIGHT. SHH.", 7, (200, 220, 255), "Bold")),
           angle=-3, seed=72, tape=(220, 40, 60))
    for k, (dx, dy, col, txt) in enumerate(((140, 30, (255, 240, 140), "TUTOR"), (140, 100, (160, 230, 255), "RIDE?"),
                                             (50, 160, (255, 170, 200), "LOST"))):
        x_, y_ = bx0 + dx, by0 + dy
        c.ink(Sh([rot_pts([(x_ - 22, y_ - 18), (x_ + 22, y_ - 18), (x_ + 22, y_ + 18), (x_ - 22, y_ + 18)], k * 6 - 6, x_, y_)]), col,
              lw=1.6, shade=0.2)
        c.text(x_, y_, txt, 8, (60, 40, 60), "Bold")
        c.ink(ell(x_, y_ - 15, 3, 3), (220, 40, 60), lw=1)
    # trash can overflowing + tray rack
    R.contact(980, 1030, 10, 60, 0.5)
    R.ink_box(980, 1030, 0, 90, 10, 60, (60, 70, 90), seed=73)
    for k in range(4):
        x_, y_ = P(990 + k * 12, 94 + (k % 2) * 8, 30 + k * 6)
        c.ink(ell(x_, y_, 11, 8), rng.choice([(246, 244, 236), (220, 60, 70), (250, 220, 80)]), lw=2.0, shade=0.4)
    # dining tables + stools in the room
    for X0, Z0 in ((660, 150), (1060, 150)):
        R.contact(X0, X0 + 150, Z0, Z0 + 80, 0.5)
        c.stroke([P(X0 + 75, 0, Z0 + 40), P(X0 + 75, 70, Z0 + 40)], 10, INK, taper=(0, 0))
        R.ink_box(X0, X0 + 150, 70, 78, Z0, Z0 + 80, (240, 200, 70), top=(255, 220, 100), seed=X0)
        for sx in (X0 - 20, X0 + 170):
            R.ink_box(sx - 16, sx + 16, 40, 48, Z0 + 24, Z0 + 56, (220, 60, 80), seed=sx)
            c.stroke([P(sx, 0, Z0 + 40), P(sx, 40, Z0 + 40)], 6, INK, taper=(0, 0))
        x_, y_ = P(X0 + 50, 78, Z0 + 40)
        c.ink(Sh([[(x_ - 30, y_ - 4), (x_ + 30, y_ - 4), (x_ + 24, y_ + 4), (x_ - 24, y_ + 4)]]), (220, 60, 80), lw=1.8)
        c.ink(ell(x_ + 4, y_ - 8, 14, 5), (240, 200, 90), lw=1.6)
    # ceiling: panel lights, ducts, a hanging "ORDER HERE" sign
    lamps = []
    for X0 in (150, 600, 1000):
        panel_light(c, R, X0, X0 + 180, 120, 210, cone=0.2, flicker=(X0 == 1000))
        lamps.append(R.pt(X0 + 90, Hb - 14, 165))
    pipe(c, [P(0, Hb - 30, 300), P(Wb, Hb - 30, 300)], w=34, col=(170, 170, 190), brackets=[P(400, Hb - 30, 300), P(900, Hb - 30, 300)])
    cobweb(c, *P(0, Hb, 0), 100, "tl")
    cobweb(c, *P(Wb, Hb, 0), 110, "tr")
    stain(c, *P(700, 420), 50, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(500, 620, 520, 0.4), (980, 600, 520, 0.4), (1400, 600, 400, 0.25),
                          (P(300, 120, 40)[0], 560, 300, 0.3, (255, 170, 90))],
               ambient=0.94, vign=0.6, top_dark=0.42, bottom_dark=0.35)
    for k, (x, y) in enumerate(lamps):
        c.glow2(x, y, 260, (255, 246, 210), 0.5 if k < 2 else 0.25, sy=0.4)
        c.glow2(x, y, 120, (255, 255, 240), 0.6 if k < 2 else 0.3, sy=0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_chair_back(sub, 80, 900, 340, 320)
        fg_bottles(sub, 1600, 1050, 4, 1.0, seed=33)
        fg_table_edge(sub, 1500, 2000, 1015, 120)
        fg_plant(sub, 1900, 1080, 260, seed=12, flip=True)
        fg_cable(sub, [(400, 1100), (800, 1070), (1200, 1095)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_student_union.png")


LAYOUT["student_union"] = dict(
        walk_px=[(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)],
        hotspots={
            ("Quad", 0): dict(box=(70, 360, 270, 790), stand=(250, 850)),
            ("Menu board", 0): dict(box=(440, 240, 900, 410), stand=(670, 790)),
            ("Grill counter", 0): dict(box=(310, 470, 970, 715), stand=(640, 790)),
            ("Doreen", 0): dict(npc="hs_doreen", feet=(880, 945), stand=(1070, 935)),
            ("Soda fountain", 0): dict(box=(1110, 450, 1290, 715), stand=(1200, 790)),
            ("Kyle", 0): dict(npc="hs_kyle", feet=(1520, 945), stand=(1340, 935)),
            ("Bulletin board", 0): dict(box=(1380, 320, 1570, 520), stand=(1475, 790)),
        },
        entries={"from_campus": (280, 900)})


# =========================================================================== 7. Library stacks (attic, poetry slam)
def beanbag(c, x, y, s, col):
    c.soft(ell(x, y + 4 * s, 90 * s, 18 * s), (24, 6, 34), 0.45, 10)
    c.ink(blob([(x - 86 * s, y), (x - 92 * s, y - 46 * s), (x - 46 * s, y - 92 * s), (x + 28 * s, y - 90 * s), (x + 84 * s, y - 44 * s),
                (x + 82 * s, y)], 2), col, lw=3.2, shade=0.55, sw=30 * s, hi=0.35, rim=0.2)
    c.stroke([(x - 40 * s, y - 50 * s), (x + 10 * s, y - 40 * s), (x + 40 * s, y - 56 * s)], 2.2, shade_col(col, 0.5), opacity=0.7)


def paint_library_stacks():
    c, R, rng = std_room(700, back=(330, 220, 1590, 690), light=(0.2, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 60, 140)
    WOOD = (110, 66, 60)

    def ceil(sub):
        planks(sub, (90, 56, 70), 0, 0, sub.w, sub.h, pw=36 * sub.density, seed=71, vertical=True)
        for _ in range(8):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 110), (30, 10, 30), 0.3, 0, rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (100, 40, 110), 0.3), (90, 56, 60), 72, low_kind="wood", chips=6)
        poster(sub, sub.ax(200), sub.by(320), 130, 160, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.16, "RULES OF", 12, (60, 40, 120)),
                                  p.text(w_ / 2, h_ * 0.3, "THE SLAM", 15, (200, 40, 90)),
                                  p.text(w_ / 2, h_ * 0.5, "1. snap, don't clap", 7.5, (60, 40, 60), "Bold"),
                                  p.text(w_ / 2, h_ * 0.62, "2. no rhyming 'orange'", 7.5, (60, 40, 60), "Bold"),
                                  p.text(w_ / 2, h_ * 0.74, "3. do NOT wake", 7.5, (60, 40, 60), "Bold"),
                                  p.text(w_ / 2, h_ * 0.84, "Ms. Hush", 7.5, (60, 40, 60), "Bold")),
               angle=-3, seed=73, peel="br")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.03), (90, 56, 60), 74, low_kind="wood", chips=6)
        for k in range(3):
            hanging_web(sub, sub.ax(80 + k * 120), 4, 40 + k * 20, opacity=0.4)

    def floor(sub):
        planks(sub, (120, 74, 70), 0, 0, sub.w, sub.h, pw=44 * sub.density, seed=75, vertical=True)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=700)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, (90, 56, 60), 76, chips=8, stains=5, low_kind="wood")
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=76)
    R.ao(0.55)
    R.edges(w=4.0)

    # round moonlit window (back wall)
    wx, wy = P(830, 360)
    r = 74
    c.ink(ell(wx, wy, r + 18, r + 18), (200, 170, 140), lw=3.2, shade=0.45, sw=10, hi=0.3)
    clip = ell(wx, wy, r, r)
    c.ink(clip, ("vy", wy - r, wy + r, (30, 30, 90), (90, 60, 150)), lw=2.6, shade=0, hi=0, ao=0)
    c.glow2(wx + 18, wy - 14, 90, (220, 230, 255), 0.5)
    c.ink(ell(wx + 18, wy - 14, 26, 26), (250, 248, 230), lw=0, shade=0.2, sw=8, hi=0, clip=clip)
    for _ in range(14):
        sx, sy = wx + rng.uniform(-r, r), wy + rng.uniform(-r, r)
        if (sx - wx) ** 2 + (sy - wy) ** 2 < (r - 8) ** 2:
            c.ink(ell(sx, sy, 1.4, 1.4), (255, 255, 230), lw=0, shade=0, hi=0, ao=0)
    for a in (0, 90):
        rr = math.radians(a)
        c.stroke([(wx - math.cos(rr) * r, wy - math.sin(rr) * r), (wx + math.cos(rr) * r, wy + math.sin(rr) * r)], 8, (200, 170, 140))
    c.ink(ell(wx, wy, r, r), (0, 0, 0, 0), lw=3.0, line_only=True)
    moon_floor = P(760, 0, 260)
    c.light_cone((wx, wy), (moon_floor[0] - 260, moon_floor[1] + 40), (moon_floor[0] + 200, moon_floor[1] + 40), (170, 190, 255),
                 0.22, 40)
    # dusty shelves (hotspot "Dusty shelves")
    bookcase(c, R, 60, 240, 360, 0, 54, rng, WOOD, shelves=6, gaps=0.15, dust=True)
    bookcase(c, R, 250, 420, 300, 0, 54, rng, WOOD, shelves=5, gaps=0.15, dust=True)
    # boxes stacked beside the shelves
    for k, (X0, Y0, w, h) in enumerate(((430, 0, 90, 70), (440, 70, 70, 56), (425, 126, 60, 44))):
        R.ink_box(X0, X0 + w, Y0, Y0 + h, 4, 4 + w * 0.8, (200, 150, 90), seed=k + 70)
    x_, y_ = P(475, 36, 76)
    c.text(x_, y_, "OVERDUE", 10, (120, 50, 40))
    # slam chalkboard on the back wall (hotspot "Slam chalkboard")
    bx0, by0 = P(480, 330)
    bx1, by1 = P(700, 170)
    c.ink(rect(bx0 - 14, by0 - 14, bx1 + 14, by1 + 14), (150, 96, 60), lw=3.2, shade=0.4, hi=0.3)
    c.ink(rect(bx0, by0, bx1, by1), (40, 60, 56), lw=2.4, shade=0.2, tex=0.35)
    c.text((bx0 + bx1) / 2, by0 + 22, "TONIGHT'S SLAM", 15, (250, 250, 240))
    for k, nm in enumerate(("1. PERCIVAL T.", "2. ~~percival~~", "3. ________", "4. ________")):
        c.text(bx0 + 24, by0 + 52 + k * 22, nm.replace("~~", ""), 11, (230, 236, 230), "Bold", anchor="lm")
    c.stroke([(bx0 + 24, by0 + 74), (bx0 + 130, by0 + 74)], 2.0, (250, 250, 240))
    c.ink(rect(bx0 + 20, by1 - 4, bx0 + 60, by1 + 4), (240, 240, 230), lw=1.4)
    c.soft(rect(bx0 + 120, by0 + 110, bx1 - 20, by1 - 10), (250, 250, 250), 0.12, 10)
    # stage pallet + open mic + amp + clip spotlight (hotspot "Open mic")
    R.contact(960, 1200, 0, 120, 0.5)
    R.ink_box(960, 1200, 0, 24, 0, 120, (150, 100, 70), top=(180, 130, 90), seed=77)
    for k in range(5):
        c.stroke([P(970 + k * 48, 24, 2), P(970 + k * 48, 24, 118)], 2.0, (110, 70, 50), opacity=0.8)
    # small rug on the stage
    c.ink(blob([P(990, 25, 20), P(1170, 25, 20), P(1180, 25, 110), P(980, 25, 110)], 1), (200, 60, 100), lw=2.4, shade=0.15, tex=0.3)
    mx_, my_ = P(1080, 24, 50)
    mt = P(1080, 160, 50)
    c.ink(ell(mx_, my_, 24, 6), (40, 40, 50), lw=2.2)
    c.stroke([(mx_, my_), mt], 6, INK, taper=(0, 0))
    c.stroke([(mx_, my_), mt], 3, (170, 170, 180), taper=(0, 0))
    c.stroke([mt, (mt[0] - 20, mt[1] - 16)], 4, INK)
    c.ink(rrect(mt[0] - 32, mt[1] - 30, mt[0] - 14, mt[1] - 12, 7), (70, 70, 80), lw=2.4, shade=0.4, hi=0.5, hw=2)
    cable(c, (mx_, my_ - 4), P(1180, 24, 90), sag=-8, w=3, col=(30, 30, 40))
    R.ink_box(1130, 1190, 24, 90, 20, 60, (50, 46, 56), seed=78)
    ax, ay = P(1160, 60, 60)
    c.ink(ell(ax, ay, 16, 16), (30, 26, 34), lw=2.2, shade=0.2, hi=0.3)
    spot = P(1000, 300, 0)
    c.stroke([spot, (spot[0], spot[1] + 30)], 4, INK)
    c.ink(Sh([rot_pts([(spot[0] - 20, spot[1] + 20), (spot[0] + 16, spot[1] + 20), (spot[0] + 22, spot[1] + 54),
                       (spot[0] - 26, spot[1] + 54)], -30, spot[0], spot[1] + 30)]), (60, 60, 70), lw=2.6, shade=0.4, hi=0.4)
    c.light_cone((spot[0] + 18, spot[1] + 50), (mx_ - 60, my_ + 20), (mx_ + 160, my_ + 20), (255, 220, 160), 0.35, 20)
    # snapping-fingers sign on the stage front
    sx_, sy_ = P(1080, 12, 121)
    c.ink(rrect(sx_ - 50, sy_ - 11, sx_ + 50, sy_ + 11, 3), (250, 240, 200), lw=1.8, shade=0.2)
    c.text(sx_, sy_, "SNAP ONLY", 9, (150, 40, 60))
    # Plumworth bust on a pedestal in the corner (hotspot "Plumworth bust")
    R.contact(1170, 1240, 140, 200, 0.55)
    R.ink_box(1170, 1240, 0, 130, 140, 200, (220, 210, 200), top=(240, 236, 226), seed=79)
    q = P(1205, 0, 201)
    c.text(q[0], q[1] - 50 * R.k(200), "PLUMWORTH", 9, (90, 70, 60))
    bx_, by_ = P(1205, 130, 170)
    s = R.k(170)
    BR = (176, 132, 84)        # bronze with a green patina
    c.ink(blob([(bx_ - 50 * s, by_), (bx_ - 54 * s, by_ - 22 * s), (bx_ - 30 * s, by_ - 42 * s), (bx_ + 30 * s, by_ - 42 * s),
                (bx_ + 54 * s, by_ - 22 * s), (bx_ + 50 * s, by_)], 2), BR, lw=2.8, shade=0.55, sw=16, hi=0.5, hw=6, rim=0.25)
    c.stroke([(bx_ - 30 * s, by_ - 38 * s), (bx_, by_ - 10 * s), (bx_ + 30 * s, by_ - 38 * s)], 2.4, shade_col(BR, 0.5))  # lapels
    c.ink(rect(bx_ - 12 * s, by_ - 52 * s, bx_ + 12 * s, by_ - 36 * s), shade_col(BR, 0.8), lw=2.4)
    head = blob([(bx_ - 26 * s, by_ - 60 * s), (bx_ - 30 * s, by_ - 96 * s), (bx_ - 12 * s, by_ - 118 * s), (bx_ + 14 * s, by_ - 118 * s),
                 (bx_ + 30 * s, by_ - 96 * s), (bx_ + 24 * s, by_ - 60 * s), (bx_, by_ - 48 * s)], 2)
    c.ink(head, BR, lw=2.8, shade=0.55, sw=12, hi=0.5, hw=5, rim=0.25)
    c.ink(blob([(bx_ - 30 * s, by_ - 96 * s), (bx_ - 34 * s, by_ - 116 * s), (bx_ - 10 * s, by_ - 128 * s), (bx_ + 20 * s, by_ - 126 * s),
                (bx_ + 34 * s, by_ - 108 * s), (bx_ + 30 * s, by_ - 94 * s), (bx_ + 4 * s, by_ - 110 * s)], 2), shade_col(BR, 0.75),
          lw=2.4, shade=0.4, hi=0.4)                                   # swept hair
    c.ink(blob([(bx_ + 2 * s, by_ - 90 * s), (bx_ + 14 * s, by_ - 74 * s), (bx_ + 2 * s, by_ - 70 * s)], 1), hi_col(BR, 0.1), lw=2.0)
    c.stroke([(bx_ - 14 * s, by_ - 92 * s), (bx_ - 4 * s, by_ - 94 * s)], 2.4)
    c.stroke([(bx_ + 10 * s, by_ - 94 * s), (bx_ + 20 * s, by_ - 92 * s)], 2.4)
    c.ink(blob([(bx_ - 22 * s, by_ - 62 * s), (bx_ - 4 * s, by_ - 68 * s), (bx_ + 6 * s, by_ - 68 * s), (bx_ + 24 * s, by_ - 62 * s),
                (bx_ + 4 * s, by_ - 64 * s)], 1), shade_col(BR, 0.7), lw=2.0)        # grand moustache
    for _ in range(5):
        c.ink(ell(bx_ + rng.uniform(-40, 40) * s, by_ - rng.uniform(10, 110) * s, rng.uniform(4, 9), rng.uniform(3, 6)),
              (90, 160, 130), lw=0, shade=0, hi=0, ao=0, opacity=0.6, atop=True)
    c.ink(Sh([[(bx_ - 16 * s, by_ - 122 * s), (bx_ + 20 * s, by_ - 124 * s), (bx_ + 8 * s, by_ - 160 * s)]]), (250, 210, 60), lw=2.0,
          shade=0.3)                                                   # someone gave him a party hat
    c.ink(ell(bx_ + 8 * s, by_ - 162 * s, 5, 5), (255, 90, 150), lw=1.4)
    # beanbags, candles, crates of zines
    beanbag(c, *P(320, 0, 200), 0.95, (200, 70, 110))
    beanbag(c, *P(560, 0, 170), 0.85, (60, 150, 160))
    beanbag(c, *P(880, 0, 210), 0.9, (230, 170, 60))
    cand = []
    for X, Z, h in ((470, 140, 30), (490, 150, 20), (1220, 60, 26), (720, 120, 24)):
        x_, y_ = P(X, 0, Z)
        c.ink(rect(x_ - 5, y_ - h, x_ + 5, y_), (250, 240, 220), lw=1.8, shade=0.3)
        c.ink(ell(x_, y_ - h - 6, 3, 6), (255, 200, 80), lw=0)
        cand.append((x_, y_ - h - 6))
    # ceiling rafters + string lights + paper lanterns
    for X in (0, 300, 600, 900, 1230):
        R.ink_box(X, X + 30, Hb - 34, Hb + 1, 0, 600, (90, 54, 50), side=(64, 36, 40), seed=X)
    string_lights2(c, [P(0, Hb - 30, 80), P(400, Hb - 50, 160), P(800, Hb - 40, 120), P(Wb, Hb - 30, 160)], sag=50, seed=9,
                   colors=((255, 220, 120), (255, 180, 100), (255, 240, 180)))
    lanterns = []
    for X, Z, col in ((420, 260, (255, 120, 160)), (1000, 300, (255, 210, 90))):
        x_, y_ = P(X, Hb - 110, Z)
        c.stroke([P(X, Hb, Z), (x_, y_ - 30)], 2.4, INK)
        c.ink(ell(x_, y_, 32, 30), col, lw=2.6, shade=0.3, sw=10, hi=0.3)
        for k in (-1, 0, 1):
            c.stroke([(x_ + k * 14, y_ - 28), (x_ + k * 18, y_ + 28)], 1.4, shade_col(col, 0.6), opacity=0.6)
        c.glow2(x_, y_, 160, col, 0.45)
        lanterns.append((x_, y_))
    cobweb(c, *P(0, Hb, 0), 140, "tl", opacity=0.6)
    cobweb(c, *P(Wb, Hb, 0), 130, "tr", opacity=0.6)
    cobweb(c, *P(Wb, 0, 0), 70, "tr", opacity=0.35)
    hanging_web(c, *P(200, Hb, 30), 70)
    hanging_web(c, *P(1150, Hb, 40), 60)
    # floor hatch with the ladder down (hotspot "Ladder down")
    hatch = [P(40, 0, 300), P(200, 0, 300), P(200, 0, 420), P(40, 0, 420)]
    c.ink(Sh([[P(30, 0, 290), P(210, 0, 290), P(210, 0, 430), P(30, 0, 430)]]), (90, 56, 50), lw=3.0, shade=0.2)
    c.ink(Sh([hatch]), (20, 10, 24), lw=2.6, shade=0, hi=0, ao=0)
    c.glow2(*P(120, 0, 370), 160, GLOW, 0.3)
    lid = [P(200, 0, 300), P(200, 0, 420), P(200, 150, 420), P(200, 150, 300)]
    c.ink(Sh([[P(40, 0, 300), P(200, 0, 300), P(212, 150, 290), P(52, 150, 290)]]), (120, 76, 60), lw=3.0, shade=0.4, sw=16, hi=0.3)
    for X in (85, 155):
        c.stroke([P(X, -30, 330), P(X, 130, 322)], 12, INK, taper=(0, 0))
        c.stroke([P(X, -30, 330), P(X, 130, 322)], 7, (180, 120, 70), taper=(0, 0))
    for Y in (10, 60, 110):
        c.stroke([P(85, Y, 328 - Y * 0.05), P(155, Y, 328 - Y * 0.05)], 7, INK, taper=(0, 0))
        c.stroke([P(85, Y, 328 - Y * 0.05), P(155, Y, 328 - Y * 0.05)], 3.4, (200, 140, 80), taper=(0, 0))

    room_grade(c, lights=[(lanterns[0][0], lanterns[0][1] + 160, 480, 0.35, (255, 150, 170)),
                          (lanterns[1][0], lanterns[1][1] + 160, 480, 0.35),
                          (mx_, my_ - 60, 300, 0.4), (wx, wy, 240, 0.3, (170, 190, 255)),
                          (P(120, 0, 370)[0], P(120, 0, 370)[1], 200, 0.3)],
               ambient=0.88, vign=0.66, top_dark=0.45, bottom_dark=0.4)
    for x_, y_ in cand:
        c.glow2(x_, y_, 70, GLOW, 0.5)
    for x_, y_ in lanterns:
        c.glow2(x_, y_, 80, (255, 240, 200), 0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1580, 1040, 5, 1.05, seed=41)
        fg_chair_back(sub, 1880, 880, 300, 320)
        fg_plant(sub, 760, 1110, 220, seed=42)
        fg_cable(sub, [(900, 1100), (1200, 1070), (1500, 1100)], 16)
        sub.ink(blob([(-40, 1080), (-30, 960), (60, 930), (180, 960), (240, 1080)], 2), FG, lw=0, shade=0.2, hi=0.2)   # stacked books
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_library_stacks.png")


LAYOUT["library_stacks"] = dict(
        walk_px=[(390, Y_TOP), (1760, Y_TOP), (1860, 880), (1820, Y_BOT), (330, Y_BOT), (390, 900)],
        hotspots={
            ("Ladder down", 0): dict(box=(60, 600, 360, 870), stand=(440, 880)),
            ("Dusty shelves", 0): dict(box=(390, 320, 750, 700), stand=(570, 790)),
            ("Slam chalkboard", 0): dict(box=(800, 350, 1040, 530), stand=(920, 790)),
            ("Percival Thorne", 0): dict(npc="hs_percival_thorne", feet=(1180, 945), stand=(1000, 935)),
            ("Open mic", 0): dict(box=(1380, 500, 1490, 690), stand=(1435, 790)),
            ("Plumworth bust", 0): dict(box=(1630, 380, 1770, 755), stand=(1640, 800)),
        },
        entries={"from_library": (450, 900)})


# =========================================================================== 8. Campus quad (outdoors, dusk)
def facade_windows(c, x0, x1, y0, y1, rows, cols, rng, lit=0.6, col_lit=(255, 206, 110), col_dark=(60, 40, 90), frame=(230, 210, 200),
                   ww=None, wh=None):
    cw = (x1 - x0) / cols
    rh = (y1 - y0) / rows
    ww = ww or cw * 0.5
    wh = wh or rh * 0.55
    out = []
    for r_ in range(rows):
        for k in range(cols):
            cx_, cy_ = x0 + cw * (k + 0.5), y0 + rh * (r_ + 0.5)
            on = rng.random() < lit
            c.ink(rect(cx_ - ww / 2 - 5, cy_ - wh / 2 - 5, cx_ + ww / 2 + 5, cy_ + wh / 2 + 7), frame, lw=2.2, shade=0.3)
            c.ink(rect(cx_ - ww / 2, cy_ - wh / 2, cx_ + ww / 2, cy_ + wh / 2), col_lit if on else col_dark, lw=2.0, shade=0.25 if on else 0.4,
                  hi=0.2)
            c.stroke([(cx_, cy_ - wh / 2), (cx_, cy_ + wh / 2)], 2.0, frame, taper=(0, 0))
            if on:
                out.append((cx_, cy_))
                if rng.random() < 0.3:      # a silhouette in the window
                    c.ink(ell(cx_ + rng.uniform(-6, 6), cy_ + wh * 0.1, ww * 0.16, wh * 0.22), (90, 50, 80), lw=0, shade=0, hi=0, ao=0)
    return out


def lamppost(c, x, y, h=300, col=(50, 40, 70), glow=True):
    c.soft(ell(x, y + 4, 40, 8), (24, 6, 34), 0.5, 8)
    c.ink(rect(x - 14, y - 26, x + 14, y), col, lw=2.6, shade=0.4, hi=0.3)
    c.stroke([(x, y - 20), (x, y - h)], 11, INK, taper=(0, 0))
    c.stroke([(x, y - 20), (x, y - h)], 6, hi_col(col, 0.15), taper=(0, 0))
    c.ink(Sh([[(x - 26, y - h - 6), (x + 26, y - h - 6), (x + 16, y - h - 60), (x - 16, y - h - 60)]]), (255, 226, 150), lw=2.6, shade=0.2,
          hi=0.3)
    c.ink(Sh([[(x - 32, y - h - 56), (x + 32, y - h - 56), (x, y - h - 84)]]), col, lw=2.6, shade=0.3)
    c.ink(rect(x - 30, y - h - 10, x + 30, y - h), col, lw=2.4)
    if glow:
        c.light_cone((x, y - h - 20), (x - 220, y + 60), (x + 220, y + 60), strength=0.25, blur_px=30)
    return (x, y - h - 34)


def tree_round(c, x, y, h, col=(40, 110, 100), seed=0):
    rng = random.Random(seed)
    c.stroke([(x, y), (x + 4, y - h * 0.5)], h * 0.07, INK, taper=(0, 0))
    c.stroke([(x, y), (x + 4, y - h * 0.5)], h * 0.045, (90, 56, 60), taper=(0, 0))
    for k in range(5):
        a = rng.uniform(0, 2 * math.pi)
        r = h * rng.uniform(0.18, 0.28)
        cx_, cy_ = x + math.cos(a) * h * 0.14, y - h * 0.68 + math.sin(a) * h * 0.1
        c.ink(ell(cx_, cy_, r, r * 0.92), col, lw=2.8, shade=0.55, sw=r * 0.4, hi=0.35, hw=r * 0.15, rim=0.2, tex=0.2)


def founder_statue(c, x, y, s=1.0):
    """Bronze founder (the same moustached gentleman as the Plumworth bust) striding forward with a book,
    a pigeon on his raised hand, and somebody's sunglasses pushed up on his head."""
    BR = (120, 150, 120)          # weathered verdigris bronze
    BRD = shade_col(BR, 0.6)
    u = s
    # striding legs + shoes
    for (xa, xb, lean) in ((-26, -4, -10), (6, 28, 12)):
        c.ink(Sh([[(x + xa * u, y - 100 * u), (x + xb * u, y - 100 * u), (x + (xb + lean) * u, y - 6 * u), (x + (xa + lean) * u, y - 6 * u)]]),
              BRD, lw=2.6, shade=0.45, sw=8, hi=0.35)
        c.ink(rrect(x + (xa + lean - 6) * u, y - 14 * u, x + (xb + lean + 8) * u, y + 2 * u, 6), shade_col(BR, 0.5), lw=2.4, shade=0.3, hi=0.4)
    # frock coat: shoulders -> flared tails, split at the back
    coat = Sh([[(x - 38 * u, y - 206 * u), (x + 38 * u, y - 206 * u), (x + 44 * u, y - 150 * u), (x + 58 * u, y - 70 * u),
                (x + 10 * u, y - 82 * u), (x + 2 * u, y - 110 * u), (x - 6 * u, y - 82 * u), (x - 52 * u, y - 72 * u),
                (x - 44 * u, y - 150 * u)]])
    c.ink(coat, BR, lw=3.0, shade=0.55, sw=18, hi=0.5, hw=6, rim=0.25, tex=0.18)
    c.stroke([(x - 2 * u, y - 204 * u), (x + 2 * u, y - 112 * u)], 2.4, BRD)
    c.stroke([(x - 18 * u, y - 206 * u), (x - 2 * u, y - 170 * u), (x + 18 * u, y - 206 * u)], 2.6, BRD)     # lapels
    for k in range(3):
        c.ink(ell(x + 6 * u, y - 168 * u + k * 22 * u, 3.5 * u, 3.5 * u), hi_col(BR, 0.25), lw=1.4)
    # book arm (near, down) holding a big book
    c.ink(limb([(x - 34 * u, y - 200 * u), (x - 50 * u, y - 160 * u), (x - 44 * u, y - 122 * u)], [15 * u, 13 * u, 11 * u]), BR, lw=2.8,
          shade=0.5, sw=8, hi=0.4)
    c.ink(Sh([rot_pts([(x - 74 * u, y - 150 * u), (x - 26 * u, y - 150 * u), (x - 26 * u, y - 100 * u), (x - 74 * u, y - 100 * u)], -10,
                      x - 50 * u, y - 125 * u)]), BRD, lw=2.8, shade=0.4, hi=0.3)
    c.ink(ell(x - 40 * u, y - 122 * u, 8 * u, 8 * u), BR, lw=2.2, shade=0.3)
    # raised arm (far) pointing to the sky
    c.ink(limb([(x + 32 * u, y - 200 * u), (x + 60 * u, y - 240 * u), (x + 74 * u, y - 292 * u)], [15 * u, 13 * u, 11 * u]), BR, lw=2.8,
          shade=0.5, sw=8, hi=0.4)
    c.ink(ell(x + 76 * u, y - 298 * u, 10 * u, 9 * u), BR, lw=2.4, shade=0.4)
    c.stroke([(x + 78 * u, y - 304 * u), (x + 84 * u, y - 326 * u)], 6 * u, BR)
    # pigeon on the finger
    px_, py_ = x + 86 * u, y - 330 * u
    c.ink(blob([(px_ - 16, py_), (px_ - 12, py_ - 14), (px_ + 4, py_ - 16), (px_ + 12, py_ - 26), (px_ + 20, py_ - 22), (px_ + 16, py_ - 10),
                (px_ + 14, py_)], 2), (170, 170, 190), lw=2.2, shade=0.4, hi=0.4)
    c.ink(ell(px_ + 16, py_ - 22, 1.6, 1.6), INK, lw=0)
    c.ink(Sh([[(px_ + 20, py_ - 22), (px_ + 27, py_ - 20), (px_ + 20, py_ - 18)]]), (240, 170, 60), lw=1.2)
    # head with swept hair and a grand moustache, sunglasses pushed up
    u = s * 1.25
    hx, hy = x + 2 * s, y - 238 * s
    c.ink(rect(hx - 9 * u, hy + 14 * u, hx + 9 * u, hy + 28 * u), BRD, lw=2.4)
    c.ink(blob([(hx - 24 * u, hy + 12 * u), (hx - 28 * u, hy - 18 * u), (hx - 12 * u, hy - 38 * u), (hx + 14 * u, hy - 38 * u),
                (hx + 28 * u, hy - 16 * u), (hx + 22 * u, hy + 12 * u), (hx, hy + 22 * u)], 2), BR, lw=2.8, shade=0.55, sw=10, hi=0.5,
          hw=5, rim=0.25)
    c.ink(blob([(hx - 28 * u, hy - 16 * u), (hx - 30 * u, hy - 36 * u), (hx - 6 * u, hy - 50 * u), (hx + 22 * u, hy - 46 * u),
                (hx + 32 * u, hy - 28 * u), (hx + 26 * u, hy - 18 * u), (hx + 2 * u, hy - 34 * u)], 2), BRD, lw=2.4, shade=0.4, hi=0.4)
    c.ink(blob([(hx - 20 * u, hy + 6 * u), (hx - 2 * u, hy), (hx + 6 * u, hy), (hx + 24 * u, hy + 6 * u), (hx + 4 * u, hy + 3 * u)], 1),
          BRD, lw=2.0)
    c.stroke([(hx - 14 * u, hy - 12 * u), (hx - 4 * u, hy - 14 * u)], 2.4)
    c.stroke([(hx + 8 * u, hy - 14 * u), (hx + 18 * u, hy - 12 * u)], 2.4)
    # the sunglasses (real, not bronze) - pink frames, dark lenses
    gy = hy - 34 * u
    for gx in (hx - 12 * u, hx + 12 * u):
        c.ink(rrect(gx - 11 * u, gy - 7 * u, gx + 11 * u, gy + 7 * u, 5), (30, 20, 50), lw=2.4, oc=(255, 90, 170), shade=0.1, hi=0.6, hw=3)
    c.stroke([(hx - 2 * u, gy), (hx + 2 * u, gy)], 3, (255, 90, 170))
    c.stroke([(hx - 24 * u, gy), (hx - 30 * u, gy + 8 * u)], 3, (255, 90, 170))


def paint_campus():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(0.35, -0.94), lw=3.4, seed=800)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), (-400, 100, 2320, 700), fc=1000)
    rng = random.Random(800)
    P = R.pt
    HOR = 700          # where the plaza meets the buildings

    # ---------------- sky: dusk gradient, stars, moon, clouds
    c.ink(rect(-10, -10, W_BG + 10, HOR + 10), ("vy", -10, HOR, (40, 22, 90), (240, 110, 120)), lw=0, shade=0, hi=0, ao=0, tex=0.06, wob=0)
    c.soft(rect(-10, 380, W_BG + 10, HOR), (255, 170, 110), 0.45, 60)
    for _ in range(160):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, 330)
        r = rng.choice([0.9, 1.2, 1.8, 2.4])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.5, 1))
    mx, my = 1460, 150
    c.glow2(mx, my, 260, (255, 220, 255), 0.4)
    c.ink(ell(mx, my, 52, 52), (255, 246, 220), lw=0, shade=0.3, sw=14, scol=(230, 200, 210), hi=0, tex=0.1)
    for (cx_, cy_, w) in ((300, 180, 340), (1000, 120, 420), (1750, 260, 300)):
        cl = blob([(cx_ - w / 2, cy_), (cx_ - w * 0.3, cy_ - 30), (cx_ - w * 0.05, cy_ - 44), (cx_ + w * 0.2, cy_ - 32), (cx_ + w / 2, cy_ - 6),
                   (cx_ + w * 0.3, cy_ + 12), (cx_ - w * 0.3, cy_ + 12)], 2)
        c.ink(cl, (150, 80, 150), lw=0, shade=0.3, sw=10, scol=(110, 60, 130), hi=0.4, hw=6, hcol=(255, 170, 160), opacity=0.8, tex=0.1)
    # distant tree line
    for k in range(40):
        tx = k * 52 + rng.uniform(-20, 20)
        r = rng.uniform(40, 80)
        c.ink(ell(tx, HOR - 150 - rng.uniform(0, 60), r, r * 0.9), (60, 40, 100), lw=0, shade=0, hi=0, ao=0, tex=0.1)

    # ---------------- floor: paving with a ring around the statue
    def floor(sub):
        tiles(sub, (170, 120, 150), (150, 104, 140), 0, 0, sub.w, sub.h, size=74 * sub.density, seed=81, chipped=0.12,
              grout=(100, 66, 100))
    R.paint_plane("floor", -400, 2700, 0, R.z_front(160), floor, density=0.9, seed=81)
    ring = [P(1380 + 380 * math.cos(a), 0, 120 + 90 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    c.ink(Sh([ring]), (190, 150, 170), lw=3.0, shade=0.1, hi=0.1, tex=0.25)
    ring2 = [P(1380 + 300 * math.cos(a), 0, 120 + 64 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    c.ink(Sh([ring2]), (160, 110, 150), lw=2.4, shade=0.1, hi=0, tex=0.25)
    for _ in range(14):
        x_, y_ = rng.uniform(0, W_BG), rng.uniform(720, 1060)
        c.soft(ell(x_, y_, rng.uniform(30, 90), rng.uniform(8, 20)), (60, 20, 60), 0.15, 10)

    # ---------------- buildings along the back (screen space; base at y = HOR)
    # Dorm (left): brick block, door = hotspot "Dorm"
    c.ink(rect(-30, 300, 330, HOR), (170, 70, 90), lw=3.2, shade=0.35, sw=60, hi=0.2, tex=0.2)
    for yy in np.arange(310, HOR, 16):
        c.stroke([(-30, yy), (330, yy)], 1.2, (120, 40, 70), opacity=0.35, taper=(0, 0))
    c.ink(rect(-40, 286, 340, 306), (200, 180, 190), lw=2.8, shade=0.3, hi=0.3)
    facade_windows(c, 0, 320, 320, 440, 2, 4, rng, lit=0.6)
    c.ink(rect(60, 450, 260, 470), (60, 120, 150), lw=2.6, shade=0.3)
    c.text(160, 460, "MAPLE HALL", 13, (255, 236, 160))
    flat_door(c, 100, 490, 220, HOR, (60, 90, 190), frame=(220, 200, 210), window=True, seed=82)
    c.ink(Sh([[(70, HOR), (250, HOR), (262, HOR + 14), (58, HOR + 14)]]), (190, 180, 190), lw=2.6, shade=0.3)
    bulb(c, 160, 476, 7, strength=0.4)
    # Library (classical facade)
    lx0, lx1 = 360, 760
    c.ink(rect(lx0, 330, lx1, HOR), (220, 196, 170), lw=3.2, shade=0.35, sw=50, hi=0.25, tex=0.2)
    c.ink(Sh([[(lx0 - 20, 336), (lx1 + 20, 336), ((lx0 + lx1) / 2, 250)]]), (230, 206, 180), lw=3.2, shade=0.35, hi=0.3)
    c.ink(Sh([[(lx0 + 40, 326), (lx1 - 40, 326), ((lx0 + lx1) / 2, 270)]]), (200, 176, 150), lw=2.2, shade=0.2)
    c.ink(ell((lx0 + lx1) / 2, 304, 18, 18), (236, 196, 90), lw=2.2, shade=0.3, hi=0.5)
    c.ink(rect(lx0 - 10, 336, lx1 + 10, 360), (236, 216, 190), lw=2.6, shade=0.3, hi=0.3)
    c.text((lx0 + lx1) / 2, 348, "L I B R A R Y", 14, (110, 70, 60))
    for k in range(6):
        cx_ = lx0 + 34 + k * (lx1 - lx0 - 68) / 5
        c.ink(rect(cx_ - 15, 362, cx_ + 15, HOR - 30), (240, 226, 206), lw=2.6, shade=0.5, sw=12, hi=0.4, hw=4)
        c.ink(rect(cx_ - 20, 362, cx_ + 20, 374), (230, 216, 196), lw=2.0)
    c.ink(rect(500, 470, 620, HOR - 30), (120, 60, 50), lw=2.6, shade=0.3)
    c.glow2(560, 560, 120, GLOW, 0.4)
    c.ink(rect(510, 480, 610, HOR - 34), (255, 210, 130), lw=2.0, shade=0.2, hi=0, opacity=0.85)
    c.stroke([(560, 480), (560, HOR - 34)], 3, (120, 60, 50))
    for k in range(3):
        y_ = HOR - 30 + k * 10
        c.ink(rect(lx0 - 20 - k * 12, y_, lx1 + 20 + k * 12, y_ + 12), (210, 190, 176), lw=2.2, shade=0.3, hi=0.3)
    # Student Union block behind the signpost / statue (right of the library)
    ux0, ux1 = 840, 1290
    c.ink(rect(ux0, 380, ux1, HOR), (90, 150, 160), lw=3.2, shade=0.35, sw=50, hi=0.2, tex=0.2)
    facade_windows(c, ux0 + 10, ux1 - 10, 400, 560, 2, 6, rng, lit=0.75, frame=(220, 230, 230))
    c.ink(rect(ux0 + 60, 590, ux1 - 60, HOR), (60, 50, 70), lw=2.6, shade=0.3)
    c.ink(rect(ux0 + 70, 600, ux1 - 70, HOR), (255, 200, 120), lw=2.0, shade=0.15, opacity=0.8)
    c.glow2((ux0 + ux1) / 2, 650, 300, GLOW, 0.3)
    c.ink(Sh([[(ux0 - 20, 586), (ux1 + 20, 586), (ux1 + 6, 560), (ux0 - 6, 560)]]), (220, 60, 90), lw=2.6, shade=0.4, hi=0.3)
    for k in range(10):
        c.ink(Sh([[(ux0 - 20 + k * 50, 586), (ux0 + 5 + k * 50, 586), (ux0 + 5 + k * 50, 598), (ux0 - 20 + k * 50, 598)]]),
              (250, 240, 230) if k % 2 else (220, 60, 90), lw=1.6, shade=0.2)
    c.ink(rrect(ux1 - 230, 340, ux1 - 20, 384, 8), (40, 30, 60), lw=2.8, shade=0.3)
    c.text(ux1 - 125, 362, "STUDENT UNION", 18, (255, 120, 190))
    c.glow2(ux1 - 125, 362, 240, (255, 90, 190), 0.3)
    # stage (right): scaffolding truss + banner; hotspot "Stage"
    sx0, sx1 = 1480, 1960
    c.ink(rect(1300, 420, 1960, HOR), (120, 80, 140), lw=3.0, shade=0.4, sw=40, hi=0.2, tex=0.2)    # back building
    facade_windows(c, 1310, 1470, 440, 640, 3, 2, rng, lit=0.5)
    for X in (sx0 + 20, sx1 - 40):
        c.stroke([(X, 740), (X, 430)], 16, INK, taper=(0, 0))
        c.stroke([(X, 740), (X, 430)], 9, (190, 190, 200), taper=(0, 0))
        for yy in np.arange(450, 730, 36):
            c.stroke([(X - 6, yy), (X + 6, yy + 30)], 2.2, (110, 110, 120))
    c.stroke([(sx0 + 10, 440), (sx1, 440)], 18, INK, taper=(0, 0))
    c.stroke([(sx0 + 10, 440), (sx1, 440)], 10, (190, 190, 200), taper=(0, 0))
    ban = blob([(sx0 + 60, 456), (sx1 - 60, 456), (sx1 - 70, 530), (sx0 + 70, 536)], 1)
    c.ink(ban, (250, 210, 70), lw=3.0, shade=0.4, sw=14, hi=0.3)
    c.text((sx0 + sx1) / 2 - 10, 496, "WELCOME WEEK!", 30, (170, 30, 80), angle=-1)
    spots = []
    for X in (sx0 + 120, sx0 + 240, sx0 + 360):
        c.ink(Sh([rot_pts([(X - 14, 446), (X + 14, 446), (X + 18, 476), (X - 18, 476)], 20, X, 446)]), (60, 60, 70), lw=2.4, shade=0.3)
        spots.append((X - 6, 476))
    # stage deck
    deck_top, deck_front = 646, 742
    c.ink(Sh([[(sx0, deck_top), (sx1, deck_top), (sx1, deck_front), (sx0 - 10, deck_front)]]), (90, 50, 70), lw=3.2, shade=0.3, hi=0.2,
          tex=0.2)
    c.ink(Sh([[(sx0 + 10, deck_top - 20), (sx1, deck_top - 20), (sx1, deck_top), (sx0, deck_top)]]), (170, 110, 90), lw=2.8, shade=0.2,
          hi=0.3)
    for k in range(9):
        c.ink(Sh([[(sx0 + k * 52, deck_top), (sx0 + 26 + k * 52, deck_top), (sx0 + 26 + k * 52, deck_front - 10),
                   (sx0 + 13 + k * 52, deck_front), (sx0 + k * 52, deck_front - 10)]]), (220, 60, 100), lw=1.6, shade=0.2)
    for X in (sx0 + 60, sx1 - 120):       # speaker stacks
        c.ink(rect(X, deck_top - 120, X + 70, deck_top - 20), (40, 36, 50), lw=2.8, shade=0.3, hi=0.2)
        for yy in (deck_top - 90, deck_top - 46):
            c.ink(ell(X + 35, yy, 22, 22), (24, 20, 30), lw=2.2, shade=0.2, hi=0.3)
    c.ink(ell(sx0 + 260, deck_top - 20, 18, 5), (40, 40, 50), lw=2.0)
    c.stroke([(sx0 + 260, deck_top - 20), (sx0 + 260, deck_top - 120)], 4, INK)
    c.ink(rrect(sx0 + 252, deck_top - 140, sx0 + 268, deck_top - 118, 6), (90, 90, 100), lw=2.2, shade=0.4, hi=0.5)
    for (x_, y_) in spots:
        c.light_cone((x_, y_), (x_ - 40, deck_top + 10), (x_ + 160, deck_top + 10), (255, 200, 240), 0.3, 20)
    # hedges along the building base
    for k in range(26):
        hx = k * 78 + rng.uniform(-10, 10)
        if 440 < hx < 680 or 60 < hx < 260 or 1460 < hx:
            continue
        c.ink(ell(hx, HOR - 6, 52, 30), (50, 110, 90), lw=2.6, shade=0.55, sw=14, hi=0.35, rim=0.2)

    # ---------------- plaza props
    # info kiosk (hotspot "Info kiosk")
    kx, ky = 1355, 718
    c.soft(ell(kx, ky + 4, 80, 12), (24, 6, 34), 0.5, 8)
    c.ink(rect(kx - 52, ky - 220, kx + 52, ky), (60, 140, 150), lw=3.0, shade=0.45, sw=26, hi=0.35, rim=0.2)
    c.ink(Sh([[(kx - 70, ky - 220), (kx + 70, ky - 220), (kx + 52, ky - 270), (kx - 52, ky - 270)]]), (220, 60, 90), lw=3.0, shade=0.4,
          hi=0.4)
    c.text(kx, ky - 244, "INFO", 18, (255, 236, 160))
    c.ink(rect(kx - 40, ky - 200, kx + 40, ky - 110), (250, 246, 230), lw=2.2, shade=0.2)
    c.ink(blob([(kx - 32, ky - 186), (kx + 10, ky - 192), (kx + 32, ky - 160), (kx + 6, ky - 120), (kx - 30, ky - 130)], 1), (120, 200, 120),
          lw=1.6, shade=0.2)
    c.ink(ell(kx - 6, ky - 160, 5, 5), (220, 40, 60), lw=1.2)
    c.text(kx + 2, ky - 146, "YOU", 7, (150, 30, 50), "Bold")
    for k in range(4):
        c.ink(Sh([rot_pts([(kx - 44 + k * 22, ky - 100), (kx - 26 + k * 22, ky - 100), (kx - 26 + k * 22, ky - 70), (kx - 44 + k * 22, ky - 70)],
                          k * 7 - 10, kx, ky - 85)]), rng.choice([(255, 240, 140), (160, 230, 255), (255, 170, 200)]), lw=1.4)
    # founder statue on a plinth (hotspot "Founder statue")
    fx, fy = 980, 720
    c.soft(ell(fx, fy + 4, 120, 16), (24, 6, 34), 0.55, 10)
    c.ink(rect(fx - 90, fy - 30, fx + 90, fy), (200, 190, 200), lw=3.0, shade=0.4, sw=30, hi=0.3)
    c.ink(rect(fx - 70, fy - 160, fx + 70, fy - 30), (220, 210, 220), lw=3.0, shade=0.45, sw=30, hi=0.35, rim=0.15)
    c.ink(rect(fx - 84, fy - 176, fx + 84, fy - 156), (200, 190, 200), lw=2.8, shade=0.3, hi=0.3)
    c.ink(rect(fx - 50, fy - 120, fx + 50, fy - 70), (180, 150, 90), lw=2.2, shade=0.3, hi=0.4)
    c.text(fx, fy - 104, "E. PLUMWORTH", 10, (80, 50, 30))
    c.text(fx, fy - 86, "FOUNDER", 9, (80, 50, 30))
    founder_statue(c, fx, fy - 176, 1.0)
    c.soft(ell(fx - 30, fy - 140, 20, 50), (255, 255, 255), 0.1, 10)
    # lamp posts
    lamps = [lamppost(c, 300, 724, 290), lamppost(c, 1230, 726, 220)]
    # string lights from lamp to stage
    string_lights2(c, [(lamps[1][0], lamps[1][1] + 30), (sx0 + 40, 446)], sag=60, seed=11)
    string_lights2(c, [(lamps[0][0], lamps[0][1] + 30), (lx0 + 30, 380)], sag=40, seed=12)
    # bench, bin, flyers on the ground
    bx = 700
    c.soft(ell(bx, 728, 90, 10), (24, 6, 34), 0.5, 8)
    c.ink(rect(bx - 80, 690, bx + 80, 702), (190, 110, 70), lw=2.6, shade=0.3, hi=0.3)
    c.ink(rect(bx - 80, 662, bx + 80, 676), (190, 110, 70), lw=2.6, shade=0.3, hi=0.3)
    for X in (bx - 66, bx + 66):
        c.stroke([(X, 676), (X, 726)], 6, INK, taper=(0, 0))
    for (x_, y_, a) in ((420, 780, 20), (1500, 800, -30), (860, 830, 10), (1150, 760, 40)):
        c.ink(Sh([rot_pts([(x_ - 18, y_ - 6), (x_ + 18, y_ - 6), (x_ + 18, y_ + 6), (x_ - 18, y_ + 6)], a, x_, y_)]),
              rng.choice([(250, 246, 230), (255, 230, 120), (160, 230, 255)]), lw=1.6, shade=0.2)
    # trees framing the scene at the back corners
    tree_round(c, 1270, HOR + 6, 300, seed=4)
    tree_round(c, 330, HOR + 4, 260, seed=5)

    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 200, 420, 0.4), (lamps[1][0], lamps[1][1] + 200, 420, 0.4),
                          ((ux0 + ux1) / 2, 650, 380, 0.3), (1700, 640, 420, 0.3, (255, 170, 230)),
                          (560, 600, 200, 0.3)],
               ambient=0.94, vign=0.55, top_dark=0.2, bottom_dark=0.4, shadow_tint=(80, 40, 130))
    for x_, y_ in lamps:
        c.glow2(x_, y_, 140, GLOW, 0.5)
    c.painterly(0.05)

    def fg(sub):
        for x0, flip in ((-40, False), (1960, True)):
            for k in range(7):
                a = rng.uniform(0, math.pi)
                r = rng.uniform(70, 130)
                xx = x0 + (1 if not flip else -1) * rng.uniform(0, 260)
                r = r * 0.8
                sub.ink(ell(xx, 1100 - rng.uniform(0, 100), r, r * 0.9), FG, lw=0, shade=0.2, hi=0.15, ao=0)
        fg_plant(sub, 300, 1100, 240, seed=51)
        fg_plant(sub, 1650, 1100, 220, seed=52, flip=True)
        # bench back silhouette at the bottom centre
        sub.ink(rect(700, 1030, 1220, 1052), FG, lw=0, shade=0.2, hi=0.2)
        sub.ink(rect(700, 1066, 1220, 1088), FG, lw=0, shade=0.2, hi=0.2)
        for X in (740, 1180):
            sub.ink(rect(X - 10, 1020, X + 10, 1100), FG, lw=0)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_campus.png")


LAYOUT["campus"] = dict(
        walk_px=[(40, Y_TOP), (1880, Y_TOP), (1890, 900), (1840, Y_BOT), (80, Y_BOT), (30, 900)],
        hotspots={
            ("Dorm", 0): dict(box=(80, 440, 240, 710), stand=(180, 800)),
            ("Library", 0): dict(box=(450, 330, 670, 720), stand=(560, 790)),
            ("Founder statue", 0): dict(box=(880, 190, 1090, 720), stand=(985, 790)),
            ("Frisbee", 0): dict(sprite="hs_frisbee", feet=(1180, 905), stand=(1090, 905)),
            ("Info kiosk", 0): dict(box=(1295, 440, 1420, 720), stand=(1355, 790)),
            ("Stage", 0): dict(box=(1490, 560, 1910, 745), stand=(1620, 800)),
            ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1720, 945), stand=(1540, 935)),
            ("Student Union", 0): dict(sprite="hs_student_union", feet=(790, 752), stand=(800, 800)),
        },
        entries={"from_dorm": (200, 880), "from_library": (560, 820), "from_map": (1100, 900), "from_union": (800, 850)})


ASSETS = {
    "player_dex": paint_player_dex,
    **{n: (lambda n=n: paint_npc(n)) for n in NPC_FN},
    "hs_room_216": paint_room_216, "hs_student_union": paint_union_sign, "hs_alarm_clock": paint_alarm_clock_prop,
    "hs_air_freshener": paint_air_freshener_prop, "hs_frisbee": paint_frisbee,
    "bg_dex_room": paint_dex_room, "bg_campus": paint_campus, "bg_library_stacks": paint_library_stacks, "bg_student_union": paint_student_union, "bg_library": paint_library, "bg_gil_room": paint_gil_room, "bg_lounge": paint_lounge, "bg_dorm_hallway": paint_dorm_hallway,
}


def main(argv):
    args = [a.lower() for a in argv[1:]]
    if "--layout" in args:
        write_layout()
        return
    if "--composite" in args:
        rooms = [a for a in args if not a.startswith("--")] or list(LAYOUT)
        for r in rooms:
            composite(r)
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
