#!/usr/bin/env python3
"""
Big Night Out -- the finale (Speed Daters Live TV studio) repainted in "style 2" (see Docs/ART_STYLE.md).

Paints the three finale backgrounds (studio floor, green room, control booth), the finale-only
characters (Chet Studwell, Gloria Puff, Norma Fade) and the finale-only prop sprites (reserved sign,
playback deck, empty deck) with tools/art/style2.py, matching Act 1 (tools/art/act1_style2.py):
perspective rooms, grungy magenta / teal palette, warm lamp light, dark out-of-focus foreground framing
and tall (6.5-head) characters. Roxy Vale and Dex come from act1_style2.py and are not repainted here.

This supersedes the finale painters in finale.py for these files (finale.py still paints the finale
item icons; a plain run of finale.py would overwrite the files below with the old style).

Usage:  python3 tools/art/finale_style2.py              # paint everything
        python3 tools/art/finale_style2.py chet studio  # paint assets whose name contains these words
        python3 tools/art/finale_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into finale.json
        BNO_COMPOSITES=/some/dir python3 tools/art/finale_style2.py --composite [room ids]
"""
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style2 import *  # noqa: F401,F403,E402
import act1_style2 as A  # noqa: E402
from act1_style2 import (DEX_H, BRICK, MORTAR, grunge_wall, skirting, two_tone_wall, legs, glasses, skirt,  # noqa: E402
                         hair_strands, folds, soft_shade, clip_draw, couch, exit_sign, panel_light, sprite_grade,
                         window_flat)

WORLD = os.path.join(ROOT, "Assets", "_Project", "World", "finale.json")
Y_TOP, Y_BOT = 762, 975          # walkable band (px), same as Act 1
NPC_FEET_Y = 945                 # every NPC stands here (world y -4.05), like Act 1
LAYOUT = {}

STUDIO_BACK = (260, 210, 1660, 690)
GREEN_BACK = (300, 240, 1620, 690)
BOOTH_BACK = (300, 220, 1620, 690)


def new_room(seed, back, vp_x=960, light=(-0.3, -0.95), fc=1000):
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=light, lw=3.4, seed=seed)
    R = Room(c, (vp_x, vp_for_walk(Y_TOP, Y_BOT)), back, fc=fc)
    return c, R, random.Random(seed)


# =========================================================================== shared studio props
def star_pts(cx, cy, r, r2=None, n=5, rot=-90):
    r2 = r2 or r * 0.45
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r2
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


def heart_pts(cx, cy, w, n=48):
    """Heart outline, centred (cx, cy), about w wide."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * w / 34, cy + y * w / 34))
    return pts


def lightbox(c, x0, y0, x1, y1, text, col=(230, 40, 60), lit=True, size=None, txt=(255, 240, 230)):
    """Studio light-up sign (APPLAUSE / ON AIR) in screen space."""
    c.ink(rrect(x0 - 8, y0 - 8, x1 + 8, y1 + 8, 8), (40, 26, 50), lw=3.0, shade=0.3, hi=0.3)
    face = col if lit else shade_col(col, 0.45)
    c.ink(rrect(x0, y0, x1, y1, 6), ("v", hi_col(face, 0.2), face), lw=2.4, shade=0.2, hi=0.4, ao=0)
    c.text((x0 + x1) / 2, (y0 + y1) / 2 + 1, text, size or int((y1 - y0) * 0.5), txt if lit else (150, 110, 120))
    if lit:
        c.glow2((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.9, col, 0.5)
        c.glow2((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.35, (255, 220, 200), 0.3)
    for x in (x0 + (x1 - x0) * 0.3, x1 - (x1 - x0) * 0.3):
        c.stroke([(x, y0 - 8), (x, y0 - 70)], 2.2, (60, 50, 70), taper=(0, 0))


def spot_can(c, x, y, s=1.0, aim=(0.3, 1.0), col=(50, 44, 60), lit=True, cone_to=None, cone_w=200, strength=0.22,
             cone_col=GLOW):
    """Hanging theatre spotlight: yoke + can + lens, optional light cone down to y=cone_to."""
    ax_, ay_ = aim
    L = math.hypot(ax_, ay_)
    ax_, ay_ = ax_ / L, ay_ / L
    nx_, ny_ = -ay_, ax_
    w, ln = 26 * s, 54 * s
    p0 = (x, y + 10 * s)
    p1 = (p0[0] + ax_ * ln, p0[1] + ay_ * ln)
    if lit and cone_to:
        c.light_cone(p1, (p1[0] + (cone_to[0] - p1[0]) - cone_w, cone_to[1]),
                     (p1[0] + (cone_to[0] - p1[0]) + cone_w, cone_to[1]), cone_col, strength, 30)
    c.stroke([(x, y - 14 * s), (x, y + 6 * s)], 4 * s, INK, taper=(0, 0))
    c.ink(Sh([[(p0[0] + nx_ * w * 0.7, p0[1] + ny_ * w * 0.7), (p1[0] + nx_ * w, p1[1] + ny_ * w),
               (p1[0] - nx_ * w, p1[1] - ny_ * w), (p0[0] - nx_ * w * 0.7, p0[1] - ny_ * w * 0.7)]]), col, lw=2.6,
          shade=0.4, hi=0.35, sw=6 * s)
    c.ink(ell(p1[0], p1[1], w * 0.9, w * 0.5, math.degrees(math.atan2(ay_, ax_)) + 90),
          (255, 244, 200) if lit else (90, 86, 100), lw=2.2, shade=0, hi=0, ao=0)
    c.stroke([(x - w * 0.9, y), (x, y + 14 * s), (x + w * 0.9, y)], 3.0 * s, (70, 64, 80), taper=(0, 0))
    if lit:
        c.glow2(p1[0], p1[1], 70 * s, (255, 236, 180), 0.5)


def truss(c, a, b, h=22, col=(150, 150, 170)):
    """Lighting truss (two rails with zig-zag bracing) between screen points a and b."""
    ax_, ay_ = a
    bx_, by_ = b
    c.stroke([(ax_, ay_), (bx_, by_)], 6, INK, taper=(0, 0), smooth=0)
    c.stroke([(ax_, ay_ + h), (bx_, by_ + h)], 6, INK, taper=(0, 0), smooth=0)
    c.stroke([(ax_, ay_), (bx_, by_)], 3, col, taper=(0, 0), smooth=0)
    c.stroke([(ax_, ay_ + h), (bx_, by_ + h)], 3, col, taper=(0, 0), smooth=0)
    n = max(2, int(math.dist(a, b) / (h * 1.4)))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        p = (ax_ + (bx_ - ax_) * t0, ay_ + (by_ - ay_) * t0)
        q = (ax_ + (bx_ - ax_) * t1, ay_ + (by_ - ay_) * t1 + h)
        c.stroke([p, q], 2.0, shade_col(col, 0.7), taper=(0, 0), smooth=0, opacity=0.9)


def tape_x(c, x, y, s, col=(250, 214, 60), text=None, tcol=(40, 30, 50), ky=0.35):
    """Gaffer-tape X on the floor (flattened by perspective)."""
    for ang in (28, -28):
        a = math.radians(ang)
        dx, dy = math.cos(a) * s, math.sin(a) * s * ky
        nx_, ny_ = -math.sin(a) * 9 * ky * 1.6, math.cos(a) * 9 * ky * 1.6
        c.ink(Sh([[(x - dx + nx_ * 0.5, y - dy - ny_), (x + dx + nx_ * 0.5, y + dy - ny_), (x + dx - nx_ * 0.5, y + dy + ny_),
                   (x - dx - nx_ * 0.5, y - dy + ny_)]]), col, lw=2.0, shade=0.2, hi=0.3, tex=0.3, wob=0.6)
    if text:
        c.text(x, y + s * ky + 16, text, 15, col, angle=0)


def floor_cable(c, pts, w=7, col=(30, 24, 40)):
    c.stroke(pts, w + 3, INK, taper=(0, 0), smooth=2)
    c.stroke(pts, w, col, taper=(0, 0), smooth=2)
    c.stroke([(x, y - w * 0.25) for x, y in pts], max(1.2, w * 0.25), (110, 100, 140), taper=(0.1, 0.1), smooth=2,
             opacity=0.5)


# --------------------------------------------------------------------------- audience busts
SKINS = [(255, 214, 178), (240, 186, 140), (206, 142, 100), (160, 104, 72), (120, 76, 56), (250, 200, 170)]
HAIRS = [(60, 34, 30), (250, 204, 96), (30, 20, 26), (150, 70, 40), (210, 60, 120), (90, 50, 140), (230, 230, 236)]
TOPS = [(40, 190, 196), (230, 70, 140), (250, 196, 60), (120, 70, 180), (70, 120, 210), (236, 110, 70), (60, 170, 110),
        (240, 236, 230)]


def bust(c, x, yb, s, skin, top, hair, style, look=1.0, mouth="smile", glasses_=None, arm_up=False, rng=None):
    """A seated audience member, head + shoulders, base centre (x, yb), head radius 17*s px."""
    r = 17 * s
    lw = max(1.6, 2.6 * s)
    hx, hy = x + 1 * s, yb - 2.75 * r
    hs = shade_col(hair, 0.7)
    if style in ("long", "braid"):
        c.ink(blob([(hx - r * 1.1, hy - r * 0.2), (hx + r * 1.1, hy - r * 0.2), (hx + r * 1.2, hy + r * 1.7),
                    (hx - r * 1.2, hy + r * 1.7)], 2), hair, lw=lw, shade=0.5, sw=r * 0.4, scol=hs)
    # shoulders / top
    body = blob([(x - 1.55 * r, yb + 2), (x - 1.5 * r, yb - 1.1 * r), (x - 1.0 * r, yb - 1.75 * r), (x + 1.0 * r, yb - 1.75 * r),
                 (x + 1.5 * r, yb - 1.1 * r), (x + 1.55 * r, yb + 2)], 2)
    c.ink(body, top, lw=lw, shade=0.5, sw=r * 0.5, hi=0.3, tex=0.1)
    c.ink(rect(hx - r * 0.32, hy + r * 0.6, hx + r * 0.32, yb - 1.6 * r), shade_col(skin, 0.8), lw=lw * 0.8, shade=0.3)
    if arm_up:
        for sx in (-1, 1):
            c.ink(limb([(x + sx * 1.25 * r, yb - 1.2 * r), (x + sx * 1.9 * r, yb - 2.6 * r), (x + sx * 1.6 * r, yb - 4.0 * r)],
                       [r * 0.42, r * 0.36, r * 0.32], smooth=1), top, lw=lw, shade=0.4)
            c.ink(ell(x + sx * 1.6 * r, yb - 4.2 * r, r * 0.34, r * 0.34), skin, lw=lw * 0.8, shade=0.4)
    head = ell(hx, hy, r, r * 1.12)
    c.ink(head, skin, lw=lw, shade=0.45, sw=r * 0.35, hi=0.3, rim=0.15, rcol=(255, 170, 160))
    # hair
    if style == "short":
        c.ink(blob([(hx - r * 1.04, hy + r * 0.1), (hx - r * 0.9, hy - r * 0.9), (hx, hy - r * 1.25), (hx + r * 0.9, hy - r * 0.9),
                    (hx + r * 1.02, hy - r * 0.1), (hx + r * 0.5, hy - r * 0.55), (hx - r * 0.4, hy - r * 0.6)], 2), hair, lw=lw,
              shade=0.45, sw=r * 0.3, scol=hs, hi=0.4)
    elif style in ("long", "braid", "bob"):
        c.ink(blob([(hx - r * 1.12, hy + r * (0.9 if style == "bob" else 0.6)), (hx - r * 1.1, hy - r * 0.8), (hx, hy - r * 1.3),
                    (hx + r * 1.1, hy - r * 0.8), (hx + r * 1.12, hy + r * 0.6), (hx + r * 0.7, hy - r * 0.4),
                    (hx - r * 0.2, hy - r * 0.55), (hx - r * 0.7, hy - r * 0.2)], 2), hair, lw=lw, shade=0.45, sw=r * 0.3,
              scol=hs, hi=0.45)
        if style == "braid":
            for k in range(4):
                c.ink(ell(hx + r * 1.0, hy + r * (0.7 + k * 0.42), r * 0.26, r * 0.24), hair, lw=lw * 0.8, shade=0.4, scol=hs)
    elif style == "curly":
        for k in range(9):
            a = math.radians(180 + k * 22.5)
            c.ink(ell(hx + math.cos(a) * r * 0.95, hy + math.sin(a) * r * 1.02, r * 0.42, r * 0.42), hair, lw=lw * 0.8,
                  shade=0.4, scol=hs, hi=0.3)
    elif style == "bun":
        c.ink(ell(hx - r * 0.1, hy - r * 1.35, r * 0.5, r * 0.45), hair, lw=lw, shade=0.45, scol=hs, hi=0.4)
        c.ink(blob([(hx - r * 1.04, hy + r * 0.1), (hx - r * 0.9, hy - r * 0.9), (hx, hy - r * 1.2), (hx + r * 0.9, hy - r * 0.9),
                    (hx + r * 1.02, hy - r * 0.1), (hx + r * 0.4, hy - r * 0.6)], 2), hair, lw=lw, shade=0.45, scol=hs, hi=0.4)
        c.stroke([(hx - r * 0.6, hy - r * 1.75), (hx + r * 0.4, hy - r * 1.1)], max(1.6, 2.6 * s), (250, 200, 50))
    elif style == "spiky":
        pts = []
        for k in range(9):
            a = math.radians(190 + k * 20)
            rr = r * (1.55 if k % 2 == 0 else 1.0)
            pts.append((hx + math.cos(a) * rr, hy - r * 0.1 + math.sin(a) * rr))
        pts += [(hx + r * 0.9, hy - r * 0.2), (hx - r * 0.9, hy - r * 0.2)]
        c.ink(blob(pts, 1), hair, lw=lw, shade=0.45, scol=hs, hi=0.4)
    elif style == "cap":
        c.ink(blob([(hx - r * 1.05, hy - r * 0.2), (hx - r * 0.9, hy - r * 1.0), (hx + r * 0.9, hy - r * 1.0),
                    (hx + r * 1.05, hy - r * 0.2)], 2), hair, lw=lw, shade=0.45, hi=0.4)
        c.ink(Sh([[(hx + r * 0.3, hy - r * 0.35), (hx + r * 1.9, hy - r * 0.2), (hx + r * 1.0, hy - r * 0.05)]]), shade_col(hair, 0.8),
              lw=lw, shade=0.3)
    elif style == "cowboy":
        A.cowboy_hat2(c, hx, hy - r * 0.55, r * 3.0, tilt=-6)
    elif style == "phones":
        c.ink(blob([(hx - r * 1.04, hy + r * 0.1), (hx - r * 0.9, hy - r * 0.9), (hx, hy - r * 1.25), (hx + r * 0.9, hy - r * 0.9),
                    (hx + r * 1.02, hy - r * 0.1)], 2), hair, lw=lw, shade=0.45, scol=hs, hi=0.4)
        c.stroke([(hx - r * 1.05, hy), (hx - r * 0.7, hy - r * 1.25), (hx + r * 0.7, hy - r * 1.25), (hx + r * 1.05, hy)],
                 max(2, r * 0.22), (40, 200, 210), smooth=2)
        for sx in (-1, 1):
            c.ink(rrect(hx + sx * r * 1.05 - r * 0.25, hy - r * 0.3, hx + sx * r * 1.05 + r * 0.25, hy + r * 0.35, 3),
                  (40, 200, 210), lw=lw * 0.8, shade=0.4)
    elif style == "bald":
        c.stroke([(hx - r * 0.3, hy - r * 0.8), (hx + r * 0.2, hy - r * 0.9)], max(1.4, 2 * s), (255, 255, 255), opacity=0.5)
    # face: eyes look toward the stage (right)
    for ex, rx_ in ((hx - r * 0.36, r * 0.24), (hx + r * 0.36, r * 0.24)):
        ey = hy + r * 0.05
        c.ink(ell(ex, ey, rx_, rx_ * 1.25), (252, 250, 246), lw=max(1.2, lw * 0.6), shade=0.2, hi=0, ao=0, tex=0)
        c.ink(ell(ex + rx_ * 0.4 * look, ey + rx_ * 0.1, rx_ * 0.55, rx_ * 0.65), (20, 12, 26), lw=0, shade=0, hi=0, ao=0, tex=0)
        c.ink(ell(ex + rx_ * 0.25 * look, ey - rx_ * 0.2, rx_ * 0.2, rx_ * 0.2), (255, 255, 255), lw=0, shade=0, hi=0, ao=0, tex=0)
    if glasses_:
        for ex in (hx - r * 0.36, hx + r * 0.36):
            c.ink(ell(ex, hy + r * 0.05, r * 0.34, r * 0.34), (0, 0, 0, 0), lw=max(1.4, r * 0.1), oc=glasses_, line_only=True)
    my = hy + r * 0.62
    if mouth == "open":
        c.ink(ell(hx + r * 0.05, my, r * 0.28, r * 0.22), (110, 26, 48), lw=max(1.2, lw * 0.6), shade=0, hi=0, ao=0, tex=0)
    elif mouth == "flat":
        c.stroke([(hx - r * 0.2, my), (hx + r * 0.28, my)], max(1.2, lw * 0.6), INK)
    else:
        c.stroke(bez((hx - r * 0.32, my - r * 0.05), (hx, my + r * 0.25), (hx + r * 0.34, my - r * 0.08), 8), max(1.2, lw * 0.6),
                 INK)
    c.soft(ell(hx - r * 0.55, hy + r * 0.4, r * 0.22, r * 0.14), (255, 110, 130), 0.35, 2)
    c.soft(ell(hx + r * 0.6, hy + r * 0.4, r * 0.22, r * 0.14), (255, 110, 130), 0.35, 2)
    return hx, hy, r


def held_sign(c, x, y, w, h, text, bg=(252, 246, 220), col=(220, 40, 90), angle=0, size=None):
    """Hand-lettered cardboard sign held above the crowd (on a stick)."""
    c.stroke([(x, y + h / 2), (x + 2, y + h / 2 + 50)], 5, INK, taper=(0, 0))
    c.stroke([(x, y + h / 2), (x + 2, y + h / 2 + 50)], 2.6, (190, 150, 100), taper=(0, 0))
    pts = rot_pts([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], angle, x, y)
    c.ink(Sh([pts]), bg, lw=2.6, shade=0.25, hi=0.2, tex=0.2)
    c.text(x, y, text, size or int(h * 0.42), col, angle=-angle)


def bleachers(c, R, X0, X1, rng, tiers=((150, 0, 50), (100, 50, 95), (50, 95, 140)), panel=(200, 50, 130)):
    """Tiered audience seating against the back wall with seated fans. tiers: (seat Y, Z0, Z1), back to front."""
    P = R.pt
    who = [  # (skin, top, hair, style, extras) - a few nods to people Dex met, the rest generic fans
        (SKINS[0], (230, 70, 140), (250, 204, 96), "cowboy", {}),            # Lacey Rae
        (SKINS[5], (120, 70, 180), (150, 70, 40), "braid", {"glasses_": (200, 60, 90)}),   # Ivy
        (SKINS[3], (40, 190, 196), (30, 20, 26), "phones", {}),              # Dolly
        (SKINS[1], (250, 196, 60), (90, 50, 30), "bun", {}),                 # Bree, pencil in her bun
        (SKINS[2], (236, 110, 70), (30, 20, 26), "curly", {}),
        (SKINS[4], (70, 120, 210), (20, 14, 20), "short", {}),
        (SKINS[0], (60, 170, 110), (210, 60, 120), "spiky", {}),
        (SKINS[1], (240, 236, 230), (60, 34, 30), "bob", {}),
        (SKINS[3], (230, 70, 140), (40, 30, 30), "cap", {}),
        (SKINS[5], (40, 190, 196), (230, 230, 236), "bun", {}),
        (SKINS[2], (120, 70, 180), (30, 20, 26), "long", {}),
        (SKINS[4], (250, 196, 60), (30, 20, 26), "bald", {}),
    ]
    seats = []
    for ti, (sy, z0, z1) in enumerate(tiers):
        R.contact(X0, X1, z0, z1, 0.3)
        R.ink_box(X0, X1, 0, sy, z0, z1, (120, 64, 130) if ti % 2 == 0 else (104, 54, 118), top=(150, 90, 160), seed=ti)
        # seat cushions (teal) along the step
        f = R.box(X0 + 6, X1 - 6, sy, sy + 8, z0 + 6, z1 - 4)
        c.ink(Sh([f["front"]]), (40, 170, 170), lw=2.2, shade=0.3, hi=0.3)
        if "top" in f:
            c.ink(Sh([f["top"]]), (70, 200, 196), lw=2.0, shade=0.1, hi=0.3)
        n = 8
        zz = z1 - 24
        k = R.k(zz)
        row = []
        for i in range(n):
            X = X0 + (X1 - X0) * (i + 0.5) / n + rng.uniform(-6, 6)
            sk, top, hair, style, ex = who[(i * 5 + ti * 3) % len(who)]
            x, yb = P(X, sy + 6, zz)
            # knees / legs over the step front
            lx, ly = P(X, sy, z1)
            pants = rng.choice([(50, 60, 110), (70, 40, 80), (40, 40, 60), (150, 110, 70)])
            for sx in (-1, 1):
                c.ink(rrect(lx + sx * 9 * k - 8 * k, ly - 4, lx + sx * 9 * k + 8 * k, ly + 30 * k, 6 * k), pants, lw=2.0,
                      shade=0.4)
            row.append((x, yb, k, sk, top, hair, style, ex))
        for (x, yb, k, sk, top, hair, style, ex) in row:
            bust(c, x, yb, k, sk, top, hair, style, look=rng.choice([0.8, 1.0, 0.6]),
                 mouth=rng.choice(["smile", "smile", "open", "flat"]), rng=rng, **ex)
            seats.append((x, yb, k))
        # front rail of the step
        c.stroke([P(X0, sy, z1), P(X1, sy, z1)], 3.0, INK, taper=(0, 0), smooth=0)
    # front panel with marquee bulbs and a label
    sy, z0, z1 = tiers[-1]
    q = [P(X0, sy - 4, z1 + 1), P(X1, sy - 4, z1 + 1), P(X1, 0, z1 + 1), P(X0, 0, z1 + 1)]
    c.ink(Sh([q]), panel, lw=3.0, shade=0.35, hi=0.3, tex=0.12)
    for i in range(22):
        bx, by = P(X0 + 14 + (X1 - X0 - 28) * i / 21, sy - 12, z1 + 1)
        c.ink(ell(bx, by, 4.5, 4.5), (255, 236, 150), lw=1.6, shade=0, hi=0.5)
        c.glow2(bx, by, 16, GLOW, 0.4)
    tx, ty = P((X0 + X1) / 2, 18, z1 + 1)
    c.text(tx, ty, "STUDIO AUDIENCE", 18, (255, 236, 200))
    return seats


def studio_camera(c, R, X, Z, s=1.0):
    """Big pedestal TV camera on a wheeled base, lens toward the stage (right)."""
    P = R.pt
    k = R.k(Z)
    bx, by = P(X, 0, Z)
    R.contact(X - 60, X + 60, Z - 30, Z + 30, 0.5)
    # wheeled tripod base
    for dx, dz in ((-62, 26), (62, 26), (0, -34)):
        fx, fy = P(X + dx, 6, Z + dz)
        c.stroke([(bx, by - 30 * k), (fx, fy)], 9 * k, INK, taper=(0, 0))
        c.stroke([(bx, by - 30 * k), (fx, fy)], 5 * k, (70, 70, 90), taper=(0, 0))
        c.ink(ell(fx, fy + 3, 9 * k, 7 * k), (40, 36, 50), lw=2.0, shade=0.3)
    # column + steering ring
    top = P(X, 168, Z)
    c.ink(rect(bx - 11 * k, top[1], bx + 11 * k, by - 26 * k), (150, 150, 170), lw=2.8, shade=0.5, sw=8, hi=0.4)
    c.ink(ell(bx, P(X, 120, Z)[1], 52 * k, 12 * k), (0, 0, 0, 0), lw=5 * k, oc=(60, 60, 80), line_only=True)
    # camera body
    f = R.ink_box(X - 70, X + 54, 168, 248, Z - 22, Z + 22, (70, 66, 86), top=(110, 104, 130), side=(50, 46, 64), seed=3)
    fr = f["front"]
    # lens hood toward the stage
    lx, ly = P(X + 54, 208, Z)
    c.ink(Sh([[(lx - 4, ly - 30 * k), (lx + 52 * k, ly - 40 * k), (lx + 52 * k, ly + 40 * k), (lx - 4, ly + 30 * k)]]),
          (40, 36, 52), lw=2.8, shade=0.4, hi=0.3)
    c.ink(ell(lx + 52 * k, ly, 12 * k, 40 * k), (60, 140, 200), lw=2.6, shade=0.3, hi=0.6, hw=4)
    c.stroke([(lx + 50 * k, ly - 24 * k), (lx + 54 * k, ly - 6 * k)], 3, (255, 255, 255), opacity=0.7)
    # viewfinder + tally light + label
    vx, vy = P(X - 70, 236, Z + 22)
    c.ink(rrect(vx - 34 * k, vy - 30 * k, vx + 6 * k, vy + 4 * k, 4), (50, 46, 64), lw=2.4, shade=0.3)
    c.ink(rect(vx - 28 * k, vy - 24 * k, vx, vy - 2 * k), (90, 200, 220), lw=1.6, shade=0.2, hi=0.3)
    tx, ty = P(X + 20, 258, Z)
    c.ink(ell(tx, ty, 7 * k, 6 * k), (255, 40, 60), lw=2.0, hi=0.6)
    c.glow2(tx, ty, 50 * k, (255, 40, 60), 0.6)
    cx_, cy_ = (fr[0][0] + fr[1][0]) / 2, (fr[0][1] + fr[2][1]) / 2
    c.ink(rrect(cx_ - 28 * k, cy_ - 11 * k, cx_ + 28 * k, cy_ + 11 * k, 4), (250, 240, 220), lw=1.8)
    c.text(cx_, cy_, "CAM 1", int(13 * k), (40, 30, 50))
    # pan bars
    hx, hy = P(X - 70, 190, Z + 22)
    c.stroke([(hx, hy), (hx - 70 * k, hy + 40 * k)], 8 * k, INK, taper=(0, 0))
    c.stroke([(hx, hy), (hx - 70 * k, hy + 40 * k)], 4 * k, (120, 120, 140), taper=(0, 0))
    return f


def sound_board(c, R, X0, X1, Z0, Z1):
    """Mixing desk on legs with faders, knobs and two labelled tape decks."""
    P = R.pt
    R.contact(X0, X1, Z0, Z1, 0.55)
    for X, Z in ((X0 + 10, Z1 - 8), (X1 - 10, Z1 - 8), (X0 + 10, Z0 + 8), (X1 - 10, Z0 + 8)):
        a, b_ = P(X, 0, Z), P(X, 80, Z)
        c.stroke([a, b_], 9, INK, taper=(0, 0), smooth=0)
        c.stroke([a, b_], 5, (90, 90, 110), taper=(0, 0), smooth=0)
    f = R.ink_box(X0, X1, 80, 112, Z0, Z1, (60, 56, 80), top=(86, 82, 110), side=(44, 40, 60), seed=11)
    t = f["top"]
    rng = random.Random(4)
    # faders + knobs on the top face
    for i in range(14):
        u = (i + 0.5) / 14
        for j, v in enumerate((0.2, 0.42)):
            X = X0 + (X1 - X0) * u
            Z = Z0 + (Z1 - Z0) * v
            x, y = P(X, 112, Z)
            c.ink(ell(x, y, 3.6, 2.6), rng.choice([(255, 90, 120), (90, 220, 220), (255, 220, 90), (230, 230, 240)]), lw=1.2,
                  shade=0, hi=0.4)
        a, b_ = P(X0 + (X1 - X0) * u, 112, Z0 + (Z1 - Z0) * 0.58), P(X0 + (X1 - X0) * u, 112, Z0 + (Z1 - Z0) * 0.9)
        c.stroke([a, b_], 2.0, (20, 16, 30), taper=(0, 0), smooth=0)
        m = rng.uniform(0.2, 0.8)
        fx, fy = a[0] + (b_[0] - a[0]) * m, a[1] + (b_[1] - a[1]) * m
        c.ink(rect(fx - 4, fy - 2.5, fx + 4, fy + 2.5), (230, 230, 240), lw=1.0, shade=0)
    # two tape decks on a riser at the back
    for i, (xa, xb) in enumerate(((X0 + 8, X0 + (X1 - X0) * 0.48), (X0 + (X1 - X0) * 0.52, X1 - 8))):
        g = R.ink_box(xa, xb, 112, 150, Z0 + 2, Z0 + 30, (40, 36, 56), top=(70, 66, 90), seed=12 + i)
        fr = g["front"]
        (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
        c.ink(rrect(x0 + 8, y0 + 6, x0 + (x1 - x0) * 0.6, y1 - 6, 3), (24, 20, 30), lw=1.6)
        for kk in (0.25, 0.45):
            c.ink(ell(x0 + (x1 - x0) * kk + 6, (y0 + y1) / 2, 5, 5), (200, 200, 210), lw=1.2)
        c.ink(ell(x1 - 12, (y0 + y1) / 2, 4, 4), (255, 60, 80) if i == 0 else (90, 255, 140), lw=1.2)
        c.glow2(x1 - 12, (y0 + y1) / 2, 18, (255, 60, 80) if i == 0 else (90, 255, 140), 0.5)
        lx, ly = (x0 + x1) / 2, y0 - 12
        c.ink(rect(lx - 34, ly - 8, lx + 34, ly + 8), (255, 236, 120), lw=1.6, shade=0.1)
        c.text(lx, ly, "CONTESTANT %d" % (i + 1), 8, (120, 30, 60), "Bold")
    # level meter glow + a rolled cable on top
    mx, my = P((X0 + X1) / 2, 113, Z0 + (Z1 - Z0) * 0.3)
    c.glow2(mx, my, 90, (90, 220, 220), 0.25)
    return f


def marquee_heart(c, cx, cy, w, rng):
    """SPEED DATERS LIVE! heart sign ringed with bulbs (the show's own logo)."""
    pts = heart_pts(cx, cy, w)
    c.ink(Sh([heart_pts(cx, cy + 6, w * 1.08)]), (120, 20, 70), lw=3.4, shade=0.4, hi=0.2)
    c.ink(Sh([pts]), ("v", (255, 110, 170), (210, 30, 110)), lw=3.4, shade=0.4, sw=w * 0.08, hi=0.5, hw=w * 0.04,
          rim=0.2, rcol=(255, 200, 230))
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        x = cx + (x - cx) * 0.9
        y = cy + (y - cy) * 0.9
        c.ink(ell(x, y, 5, 5), (255, 240, 170), lw=1.4, shade=0, hi=0.6)
        c.glow2(x, y, 18, GLOW, 0.45)
    c.text(cx, cy - w * 0.12, "SPEED", int(w * 0.17), (255, 236, 120), stroke=3, sc=(120, 20, 70))
    c.text(cx, cy + w * 0.06, "DATERS", int(w * 0.17), (255, 236, 120), stroke=3, sc=(120, 20, 70))
    c.ink(rrect(cx - w * 0.2, cy + w * 0.17, cx + w * 0.2, cy + w * 0.3, 8), (40, 200, 196), lw=2.6, shade=0.3, hi=0.4)
    c.text(cx, cy + w * 0.235, "LIVE!", int(w * 0.09), (255, 255, 255))
    c.glow2(cx, cy, w * 1.1, (255, 80, 160), 0.45)


# =========================================================================== 1. TV studio floor
def paint_tv_studio():
    c, R, rng = new_room(900, STUDIO_BACK)
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 56, 150)

    def ceil(sub):
        plaster_wall(sub, (60, 34, 80), (44, 24, 62), seed=3, w=sub.w, h=sub.h)
        step = 120 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 3, (30, 16, 40), taper=(0, 0), opacity=0.6)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 100), (20, 8, 30), 0.3, 0,
                  rng.randint(0, 99))

    def left(sub):
        grunge_wall(sub, sub.w, sub.h, mix(WALL, (110, 40, 120), 0.3), seed=901, chips=6, stains=4, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(70, 30, 70))
        x0, x1 = sub.ax(265), sub.ax(150)
        y0, y1 = sub.by(290), sub.by(0)

        def sign(cc, cx, cy):
            cc.ink(ell(cx, cy - 10, 26, 26), (230, 230, 240), lw=2.6, shade=0.3, hi=0.4)
            cc.ink(ell(cx, cy - 10, 18, 18), (90, 150, 200), lw=1.8, shade=0.2, hi=0.5)
            cc.ink(rect(cx - 46, cy + 40, cx + 46, cy + 72), (240, 230, 210), lw=2.0, shade=0.1)
            cc.text(cx, cy + 56, "STAGE DOOR", 13, (120, 30, 40))
        flat_door(sub, x0, y0, x1, y1, (190, 50, 60), frame=(70, 40, 60), knob="L", sign=sign, seed=902)
        sub.ink(rect(x0 - 26, (y0 + y1) / 2 + 10, x1 + 26, (y0 + y1) / 2 + 26), (220, 220, 230), lw=2.4, shade=0.4,
                hi=0.4)   # push bar
        exit_sign(sub, (x0 + x1) / 2, y0 - 60, 120, "EXIT", (255, 70, 70))
        poster(sub, sub.ax(80), sub.by(300), 120, 160, (40, 30, 70),
               lambda p, w_, h_: (p.ink(Sh([heart_pts(w_ / 2, h_ * 0.42, w_ * 0.6)]), (255, 80, 150), lw=2.4),
                                  p.text(w_ / 2, h_ * 0.12, "SEASON 9", 12, (255, 236, 120)),
                                  p.text(w_ / 2, h_ * 0.8, "SPEED DATERS", 11, (255, 255, 255)),
                                  p.text(w_ / 2, h_ * 0.92, "tuesdays 9pm", 8, (200, 220, 255), "Bold")),
               angle=-3, seed=903, peel="br")
        poster(sub, sub.ax(340), sub.by(320), 90, 120, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.25, "QUIET", 15, (200, 40, 60)),
                                  p.text(w_ / 2, h_ * 0.48, "ON SET", 13, (60, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.75, "(yes YOU)", 9, (60, 40, 80), "Bold")),
               angle=4, seed=904, peel="tl")
        sub.ink(rrect(sub.ax(110) - 16, sub.by(70) - 60, sub.ax(110) + 16, sub.by(70), 8), (220, 40, 50), lw=2.4,
                shade=0.5, hi=0.4)   # fire extinguisher

    def right(sub):
        grunge_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), seed=905, chips=4, stains=3, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(70, 30, 70))
        poster(sub, sub.ax(250), sub.by(330), 110, 140, (40, 190, 196),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.3, "SMILE", 16, (255, 255, 255)),
                                  p.text(w_ / 2, h_ * 0.55, "YOU'RE", 12, (40, 30, 60)),
                                  p.text(w_ / 2, h_ * 0.75, "ON TV", 16, (255, 236, 120))), angle=3, seed=906, peel="tr")

    def floor(sub):
        planks(sub, (78, 54, 96), 0, 0, sub.w, sub.h, pw=70 * sub.density, seed=907, vertical=True,
               gap_col=(40, 24, 50))

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=900)

    def back(sub):
        grunge_wall(sub, sub.w, sub.h, WALL, seed=908, chips=9, stains=5, cracks=3, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(70, 30, 70))
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=908)

    # ---------------- stage backdrop: glitter curtain on the right of the back wall
    SX0, SX1 = 970, Wb

    def curtain(sub):
        w, h = sub.w, sub.h
        n = 26
        for i in range(n):
            x0_, x1_ = w * i / n, w * (i + 1) / n
            col = (226, 50, 150) if i % 2 == 0 else (196, 34, 126)
            sub.ink(rect(x0_ - 1, 0, x1_ + 1, h), ("h", hi_col(col, 0.15), shade_col(col, 0.8)), lw=0, shade=0, hi=0, ao=0,
                    tex=0.12, wob=0)
            sub.stroke([(x1_, 0), (x1_ + rng.uniform(-3, 3), h)], 2.0, (110, 10, 70), opacity=0.6)
        for _ in range(420):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            sub.ink(ell(x, y, 1.6, 1.6), (255, 220, 240), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.4, 0.9))
        # scalloped gold valance
        for i in range(12):
            cx = w * (i + 0.5) / 12
            sub.ink(ell(cx, 30, w / 24 + 2, 34), (240, 190, 70), lw=2.4, shade=0.4, hi=0.4)
        sub.ink(rect(-4, 0, w + 4, 30), (250, 206, 90), lw=2.6, shade=0.3, hi=0.4)
    R.paint_plane("back", SX0, SX1, 40, Hb - 6, curtain, density=1.0, seed=909)
    R.ao(0.5)
    R.edges(w=4.0)

    # ---------------- stage platform + podiums
    R.contact(SX0 - 10, Wb, 0, 160, 0.5)
    f = R.ink_box(SX0 - 10, Wb + 2, 0, 44, 0, 150, (60, 30, 80), top=(150, 70, 150), side=(40, 20, 56), seed=910)
    fr = f["front"]
    for i in range(30):
        bx, by = P(SX0 + (Wb - SX0) * (i + 0.5) / 30, 26, 151)
        c.ink(ell(bx, by, 5, 5), (255, 236, 150), lw=1.6, shade=0, hi=0.5)
        c.glow2(bx, by, 18, GLOW, 0.45)
    c.ink(Sh([[P(SX0 - 10, 44, 150), P(Wb + 2, 44, 150), P(Wb + 2, 38, 150), P(SX0 - 10, 38, 150)]]), (250, 200, 80), lw=2.0,
          shade=0.2, hi=0.4)
    for i, X in enumerate((1040, 1190)):
        R.contact(X - 50, X + 50, 50, 100, 0.45)
        g = R.ink_box(X - 46, X + 46, 44, 180, 54, 96, (40, 190, 196), top=(255, 236, 140), side=(30, 120, 130), seed=911 + i)
        gx, gy = P(X, 120, 96)
        c.ink(Sh([heart_pts(gx, gy, 54)]), (255, 90, 150), lw=2.4, shade=0.3, hi=0.5)
        c.text(gx, gy - 2, str(i + 1), 20, (255, 255, 255))
    marquee_heart(c, *P((SX0 + Wb) / 2 + 20, 300), 300, rng)

    # ---------------- back wall left: applause sign, ON AIR, booth window, green room door
    lightbox(c, *P(150, 400), *P(390, 335), "APPLAUSE", (230, 40, 60), size=30)
    lightbox(c, *P(620, 395), *P(740, 350), "ON AIR", (255, 60, 60), size=18)
    # control booth window (dark, a figure in a headset)
    wx0, wy0 = P(790, 450)
    wx1, wy1 = P(950, 320)
    c.ink(rect(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 18), (80, 70, 100), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(wx0, wy0, wx1, wy1), ("v", (40, 60, 110), (20, 24, 50)), lw=2.4, shade=0.2, hi=0)
    for k in range(3):
        mx = wx0 + 20 + k * 44
        c.ink(rect(mx, wy1 - 52, mx + 36, wy1 - 26), (60, 200, 220), lw=1.4, shade=0, hi=0, ao=0, opacity=0.6)
    nx_, ny_ = wx0 + 100, wy1 - 30
    c.ink(ell(nx_, ny_ - 34, 10, 12), (16, 14, 30), lw=0)
    c.ink(blob([(nx_ - 20, ny_ + 6), (nx_ - 16, ny_ - 18), (nx_ + 16, ny_ - 18), (nx_ + 20, ny_ + 6)], 2), (16, 14, 30), lw=0)
    c.stroke([(nx_ - 11, ny_ - 36), (nx_, ny_ - 48), (nx_ + 11, ny_ - 36)], 2.4, (60, 60, 80), smooth=2)
    for k in range(6):   # venetian blind, half down and crooked
        yy = wy0 + 6 + k * 9
        c.stroke([(wx0 + 2, yy), (wx1 - 2, yy + (k * 1.5 if k > 2 else 0))], 4, (190, 180, 210), taper=(0, 0), smooth=0)
    c.stroke([(wx0 + 40, wy0), (wx0 + 40, wy0 + 60)], 1.2, (220, 220, 230), taper=(0, 0))
    c.ink(rect(wx0, wy1 - 18, wx1, wy1), (50, 44, 70), lw=1.6, shade=0)   # desk edge inside
    c.stroke([(wx0 + (wx1 - wx0) / 2, wy0), (wx0 + (wx1 - wx0) / 2, wy1)], 6, (80, 70, 100), taper=(0, 0), smooth=0)
    c.stroke([(wx0 + 10, wy1 - 10), (wx0 + 60, wy0 + 10)], 12, (255, 255, 255), opacity=0.12)
    c.glow2((wx0 + wx1) / 2, (wy0 + wy1) / 2, 160, (70, 140, 255), 0.35)
    c.ink(rect((wx0 + wx1) / 2 - 40, wy1 + 22, (wx0 + wx1) / 2 + 40, wy1 + 40), (40, 30, 50), lw=1.8)
    c.text((wx0 + wx1) / 2, wy1 + 31, "CONTROL", 10, (200, 200, 220))
    # green room door
    dx0, dy0 = P(812, 268)
    dx1, dy1 = P(928, 0)

    def gsign(cc, cx, cy):
        cc.ink(Sh([star_pts(cx, cy - 16, 34)]), (255, 220, 80), lw=2.6, shade=0.3, hi=0.5)
        cc.ink(rect(cx - 44, cy + 38, cx + 44, cy + 60), (250, 246, 230), lw=1.8, shade=0.1)
        cc.text(cx, cy + 49, "GREEN ROOM", 10, (60, 120, 80))
    flat_door(c, dx0, dy0, dx1, dy1, (40, 150, 150), frame=(90, 50, 90), knob="L", sign=gsign, seed=912)

    # ---------------- bleachers with the audience (the whole night came to watch)
    seats = bleachers(c, R, 30, 560, rng)
    # signs held up over the crowd
    x, yb, k = seats[3]
    held_sign(c, x + 10, yb - 112 * k, 120, 46, "GO DEX!", angle=-5)
    x, yb, k = seats[13]
    held_sign(c, x, yb - 108 * k, 150, 44, "WHO IS DEX?", bg=(255, 250, 240), col=(60, 40, 120), angle=4, size=17)

    # ---------------- floor: camera, sound board, tape marks, cables
    floor_cable(c, [P(640, 0, 120), P(560, 0, 200), P(380, 0, 230), P(200, 0, 190), P(40, 0, 230)], 7)
    floor_cable(c, [P(1300, 0, 200), P(1340, 0, 300), P(Wb - 4, 0, 320)], 6, (40, 30, 60))
    studio_camera(c, R, 660, 112)
    sound_board(c, R, 1236, 1394, 135, 205)
    floor_pool(c, 1330, 790, 520, 70, (255, 90, 170), 0.3)
    mx, my = 960, 905
    tape_x(c, mx, my, 54, text="DEC")
    for (X, Z) in ((300, 330), (1080, 260), (1460, 380)):
        x_, y_ = P(X, 0, Z)
        c.ink(rect(x_ - 22, y_ - 4, x_ + 22, y_ + 4), (250, 214, 60), lw=1.4, shade=0.1, tex=0.3, opacity=0.8)
    # crumpled cue cards + confetti on the floor
    for _ in range(40):
        X, Z = rng.uniform(40, Wb - 40), rng.uniform(170, 520)
        x_, y_ = P(X, 0, Z)
        col = rng.choice([(255, 90, 150), (255, 220, 90), (60, 220, 210), (250, 250, 240)])
        c.ink(Sh([rot_pts([(x_ - 4, y_ - 2), (x_ + 4, y_ - 2), (x_ + 4, y_ + 2), (x_ - 4, y_ + 2)], rng.uniform(0, 180), x_, y_)]),
              col, lw=0, shade=0, hi=0, ao=0, tex=0, opacity=0.8)
    for X, Z in ((420, 260), (1500, 300)):
        x_, y_ = P(X, 6, Z)
        c.ink(ell(x_, y_, 12, 8), (246, 244, 236), lw=2.0, shade=0.4)

    # ---------------- ceiling: lighting trusses + spotlights aimed at the stage
    for Z in (200, 400):
        truss(c, P(-300, Hb - 12, Z), P(Wb + 300, Hb - 12, Z), h=int(18 * R.k(Z)))
    cone_y = P(0, 0, 160)[1]
    for X, Z, tx in ((960, 200, 1300), (1180, 200, 1420), (1380, 200, 1560), (100, 400, 1180), (560, 400, 1260),
                     (1000, 400, 1460), (1500, 400, 1600)):
        x_, y_ = P(X, Hb - 12, Z)
        aim = (tx - x_, cone_y - y_)
        spot_can(c, x_, y_ + 6, (0.9 if Z < 300 else 0.6) * R.k(Z), aim=aim, lit=True, cone_to=(tx, cone_y + 80), cone_w=150, strength=0.13)
    hanging_cable(c, P(420, Hb, 120), 160, sway=20, w=6, col=(40, 30, 60), seed=2)
    hanging_cable(c, P(1100, Hb, 200), 120, sway=-16, w=5, col=(60, 40, 90), seed=5)
    cobweb(c, *P(0, Hb, 0), 110, "tl", opacity=0.45)
    cobweb(c, *P(SX0 - 12, Hb, 0), 70, "tr", opacity=0.3)

    # ---------------- lighting
    room_grade(c, lights=[(1290, 560, 700, 0.55, (255, 120, 190)), (1300, 860, 600, 0.35), (530, 255, 260, 0.4, (255, 60, 70)),
                          (1130, 310, 200, 0.3, (100, 150, 255)), (520, 560, 420, 0.25), (960, 900, 300, 0.25)],
               ambient=0.95, vign=0.55, top_dark=0.35, bottom_dark=0.3)
    c.painterly(0.05)

    # ---------------- foreground: floor monitor wedges, cable, boom mic (outside the walkable band)
    def fg(sub):
        fg_cable(sub, [(-20, 1050), (500, 1030), (900, 1060), (1400, 1040), (1960, 1070)], 20)
        for x0_ in (560, 1300):
            sub.ink(poly([(x0_, 1080), (x0_ + 30, 1000), (x0_ + 270, 990), (x0_ + 300, 1080)]), FG, lw=0, shade=0.2, hi=0.2, hw=6)
            sub.ink(poly([(x0_ + 50, 1012), (x0_ + 250, 1004), (x0_ + 262, 1060), (x0_ + 40, 1066)]), (36, 20, 56), lw=0,
                    shade=0, hi=0)
        sub.stroke([(1990, 150), (1560, 70)], 14, FG, taper=(0, 0))
        sub.ink(rrect(1470, 40, 1580, 100, 30), FG, lw=0, shade=0.2, hi=0.2)
        fg_chair_back(sub, 80, 990, 340, 220)
        fg_chair_back(sub, 1850, 995, 320, 220)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_tv_studio.png")


# =========================================================================== 2. Green room
def wardrobe_rack(c, R, X0, X1, Z, rng):
    P = R.pt
    k = R.k(Z)
    R.contact(X0, X1, Z - 20, Z + 20, 0.45)
    H = 220
    for X in (X0, X1):
        c.stroke([P(X, 6, Z), P(X, H, Z)], 7, INK, taper=(0, 0), smooth=0)
        c.stroke([P(X, 6, Z), P(X, H, Z)], 3.6, (200, 200, 214), taper=(0, 0), smooth=0)
        for dz in (-22, 22):
            c.stroke([P(X, 6, Z), P(X + 20 * (1 if X == X0 else -1) * 0, 2, Z + dz)], 6, INK, taper=(0, 0), smooth=0)
            wx, wy = P(X, 0, Z + dz)
            c.ink(ell(wx, wy, 7 * k, 6 * k), (40, 36, 50), lw=1.8)
    c.stroke([P(X0 - 8, H, Z), P(X1 + 8, H, Z)], 8, INK, taper=(0, 0), smooth=0)
    c.stroke([P(X0 - 8, H, Z), P(X1 + 8, H, Z)], 4, (220, 220, 230), taper=(0, 0), smooth=0)
    # clothes on hangers: sequin jackets, the tuxedo T-shirt
    clothes = [((250, 200, 70), "sequin"), ((40, 190, 196), "sequin"), ((250, 250, 246), "tux"), ((230, 70, 140), "sequin"),
               ((120, 70, 180), "plain")]
    n = len(clothes)
    for i, (col, kind) in enumerate(clothes):
        X = X0 + 14 + (X1 - X0 - 28) * i / (n - 1)
        hx, hy = P(X, H, Z)
        c.stroke([(hx, hy), (hx, hy + 10 * k)], 2.0, (200, 200, 210), taper=(0, 0))
        w, L = 30 * k, 120 * k
        sh = blob([(hx - w * 0.5, hy + 12 * k), (hx + w * 0.5, hy + 12 * k), (hx + w * 0.62, hy + L), (hx - w * 0.62, hy + L)], 1)
        c.ink(sh, col, lw=2.4, shade=0.5, sw=8, hi=0.4, rim=0.15)
        bx0, by0, bx1, by1 = sh.bbox()
        if kind == "sequin":
            for _ in range(28):
                x_, y_ = rng.uniform(bx0, bx1), rng.uniform(by0, by1)
                c.ink(ell(x_, y_, 1.6, 1.6), hi_col(col, 0.6), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=sh)
        elif kind == "tux":
            c.ink(Sh([[(hx - 3, hy + 14 * k), (hx + 3, hy + 14 * k), (hx + 6, hy + L * 0.8), (hx - 6, hy + L * 0.8)]]),
                  (30, 26, 40), lw=0, shade=0, hi=0, clip=sh)
            c.ink(Sh([[(hx - 10, hy + 18 * k), (hx, hy + 22 * k), (hx + 10, hy + 18 * k), (hx + 10, hy + 28 * k), (hx, hy + 24 * k),
                       (hx - 10, hy + 28 * k)]]), (30, 26, 40), lw=1.2, shade=0)
    # feather boa draped over the bar
    pts = [P(X0 + 4, H - 4, Z)] + [P(X0 + (X1 - X0) * t, H - 4 - 40 * math.sin(math.pi * t), Z + 2) for t in (0.25, 0.5, 0.75)] + \
        [P(X1 - 4, H - 70, Z + 2)]
    c.stroke(pts, 16 * k, INK, taper=(0.2, 0.4), smooth=2)
    c.stroke(pts, 12 * k, (255, 110, 180), taper=(0.2, 0.4), smooth=2)
    for t in range(18):
        q = pts[min(len(pts) - 1, int(t / 18 * len(pts)))]
        c.ink(ell(q[0] + rng.uniform(-8, 8), q[1] + rng.uniform(-6, 6), 4, 3), (255, 170, 210), lw=0, shade=0, hi=0)
    # box of mic packs on the bottom shelf
    f = R.ink_box(X0 + 10, X1 - 10, 8, 50, Z - 18, Z + 18, (200, 160, 110), top=(220, 190, 140), seed=21)
    fr = f["front"]
    cx_, cy_ = (fr[0][0] + fr[1][0]) / 2, (fr[0][1] + fr[2][1]) / 2
    c.text(cx_, cy_, "MIC PACKS", int(11 * k), (90, 50, 30))
    for i in range(4):
        x_, y_ = P(X0 + 26 + i * 26, 54, Z)
        c.ink(rrect(x_ - 8, y_ - 10, x_ + 8, y_, 2), (40, 40, 50), lw=1.6, shade=0.2)
        c.stroke([(x_, y_ - 10), (x_ + 6, y_ - 22)], 1.4, INK)


def makeup_station(c, R, X0, X1, rng):
    """Mirror ringed with bulbs on the back wall, a counter of brushes and sprays."""
    P = R.pt
    mx0, my0 = P(X0 + 20, 400)
    mx1, my1 = P(X1 - 20, 140)
    c.ink(rrect(mx0 - 26, my0 - 26, mx1 + 26, my1 + 26, 14), (236, 206, 140), lw=3.2, shade=0.4, sw=10, hi=0.4)
    c.ink(rect(mx0, my0, mx1, my1), ("v", (200, 220, 236), (130, 150, 190)), lw=2.4, shade=0.2, hi=0)
    c.stroke([(mx0 + 30, my1 - 20), (mx0 + 110, my0 + 30)], 16, (255, 255, 255), opacity=0.3)
    c.stroke([(mx0 + 70, my1 - 30), (mx0 + 140, my0 + 70)], 6, (255, 255, 255), opacity=0.25)
    # a lipstick note on the glass
    c.text(mx1 - 60, my0 + 40, "U R A STAR", 13, (220, 30, 80), angle=6)
    bulbs = []
    for i in range(7):
        bulbs.append((mx0 - 13 + (mx1 - mx0 + 26) * i / 6, my0 - 13))
    for i in range(1, 6):
        bulbs.append((mx0 - 13, my0 + (my1 - my0) * i / 6))
        bulbs.append((mx1 + 13, my0 + (my1 - my0) * i / 6))
    for i, (x, y) in enumerate(bulbs):
        dead = i == 9
        c.ink(ell(x, y, 9, 9), (255, 246, 210) if not dead else (150, 140, 130), lw=2.0, shade=0.1, hi=0.5)
        if not dead:
            c.glow2(x, y, 40, GLOW, 0.45)
    c.glow2((mx0 + mx1) / 2, (my0 + my1) / 2, 300, GLOW, 0.3)
    # counter
    R.contact(X0 - 20, X1 + 20, 0, 60, 0.5)
    R.ink_box(X0 - 20, X1 + 20, 0, 110, 0, 56, (60, 150, 150), top=(240, 230, 220), side=(40, 110, 116), seed=31)
    for i in range(3):
        q = R.box(X0 - 10 + i * (X1 - X0 + 20) / 3 + 6, X0 - 10 + (i + 1) * (X1 - X0 + 20) / 3 - 6, 14, 96, 56, 56)["front"]
        c.ink(Sh([q]), (70, 166, 166), lw=2.2, shade=0.3, hi=0.3)
        hx_, hy_ = (q[0][0] + q[1][0]) / 2, q[0][1] + 16
        c.ink(rrect(hx_ - 14, hy_ - 4, hx_ + 14, hy_ + 4, 3), (236, 196, 90), lw=1.8)
    # stuff on the counter: brushes in a cup, sprays, a wig on a head stand, powder tins
    x_, y_ = P(X0 + 30, 110, 24)
    c.ink(rrect(x_ - 12, y_ - 28, x_ + 12, y_, 4), (230, 80, 140), lw=2.2, shade=0.4)
    for j, col in enumerate([(250, 200, 70), (40, 40, 50), (240, 240, 240), (200, 60, 90)]):
        c.stroke([(x_ - 6 + j * 4, y_ - 26), (x_ - 14 + j * 9, y_ - 60)], 3, col)
    for j, col in enumerate([(200, 60, 120), (60, 170, 200), (240, 200, 80)]):
        x_, y_ = P(X0 + 80 + j * 26, 110, 30)
        c.ink(rrect(x_ - 9, y_ - 56, x_ + 9, y_, 4), col, lw=2.2, shade=0.45, hi=0.4)
        c.ink(rect(x_ - 5, y_ - 64, x_ + 5, y_ - 56), (220, 220, 230), lw=1.6)
    x_, y_ = P(X1 - 40, 110, 26)
    c.ink(rrect(x_ - 6, y_ - 50, x_ + 6, y_, 2), (90, 80, 100), lw=2.0)
    c.ink(ell(x_, y_ - 70, 22, 26), (236, 220, 210), lw=2.4, shade=0.4)
    c.ink(blob([(x_ - 30, y_ - 66), (x_ - 26, y_ - 110), (x_, y_ - 124), (x_ + 26, y_ - 110), (x_ + 30, y_ - 66),
                (x_ + 18, y_ - 84), (x_ - 18, y_ - 84)], 2), (250, 120, 40), lw=2.6, shade=0.5, hi=0.4)
    for j in range(2):
        x_, y_ = P(X1 - 110 + j * 30, 110, 40)
        c.ink(ell(x_, y_ - 6, 14, 6), (250, 190, 200), lw=2.0, shade=0.3)


def makeup_chair(c, R, X0, X1, Z0, Z1, col=(200, 40, 60)):
    """Big leather salon chair on a chrome pedestal, seen from behind at an angle."""
    P = R.pt
    Xm, Zm = (X0 + X1) / 2, (Z0 + Z1) / 2
    R.contact(X0, X1, Z0, Z1, 0.5)
    k = R.k(Zm)
    bx, by = P(Xm, 0, Zm)
    c.ink(ell(bx, by - 4, 70 * k, 16 * k), (200, 200, 214), lw=2.8, shade=0.5, hi=0.6, hw=4)
    c.ink(rect(bx - 12 * k, P(Xm, 56, Zm)[1], bx + 12 * k, by - 8), (210, 210, 224), lw=2.6, shade=0.5, sw=6, hi=0.6)
    c.ink(rect(bx - 30 * k, by - 22 * k, bx + 60 * k, by - 12 * k), (190, 190, 204), lw=2.0, shade=0.4)   # foot rest
    R.ink_box(X0 + 6, X1 - 6, 56, 84, Z0 + 10, Z1, col, top=hi_col(col, 0.2), side=shade_col(col, 0.6), seed=41)
    for X in (X0, X1 - 16):
        R.ink_box(X, X + 16, 80, 112, Z0 + 20, Z1, shade_col(col, 0.85), top=hi_col(col, 0.25), seed=42)
        R.ink_box(X - 2, X + 18, 112, 120, Z0 + 16, Z1 + 4, (220, 220, 230), seed=43)
    back = R.box(X0 + 4, X1 - 4, 80, 182, Z0 - 4, Z0 + 26)
    sh = blob(back["front"], 3)
    c.ink(sh, col, lw=3.2, shade=0.55, sw=26, hi=0.4, rim=0.2, rcol=(255, 160, 170), tex=0.15)
    bx0, by0, bx1, by1 = sh.bbox()
    for j in range(1, 4):
        xx = bx0 + (bx1 - bx0) * j / 4
        c.stroke([(xx, by0 + 30), (xx, by1 - 20)], 2.0, shade_col(col, 0.6), opacity=0.7)
    for j in range(3):
        for i in range(3):
            c.ink(ell(bx0 + (bx1 - bx0) * (i + 1) / 4 + ((j % 2) - 0.5) * 18, by0 + 30 + j * 30, 3, 3), shade_col(col, 0.5),
                  lw=0, shade=0, hi=0)
    hr = R.box(Xm - 34, Xm + 34, 182, 208, Z0 - 2, Z0 + 20)
    c.ink(blob(hr["front"], 2), col, lw=3.0, shade=0.5, sw=10, hi=0.4)
    c.stroke([((bx0 + bx1) / 2 - 20, by1 - 40), ((bx0 + bx1) / 2 + 30, by0 + 60)], 3, hi_col(col, 0.5), opacity=0.5)


def intercom(c, x, y, s=1.0):
    c.ink(rrect(x - 26 * s, y - 50 * s, x + 26 * s, y + 50 * s, 6), (220, 220, 226), lw=2.6, shade=0.4, hi=0.4)
    for k in range(5):
        c.stroke([(x - 14 * s, y - 36 * s + k * 7 * s), (x + 14 * s, y - 36 * s + k * 7 * s)], 2, (90, 90, 110), taper=(0, 0))
    c.ink(ell(x, y + 18 * s, 15 * s, 15 * s), (230, 30, 40), lw=2.4, shade=0.4, hi=0.6, hw=3)
    c.text(x, y + 40 * s, "TALK", int(10 * s), (60, 40, 50))
    c.glow2(x, y + 18 * s, 40 * s, (255, 40, 60), 0.35)


def paint_tv_green_room():
    c, R, rng = new_room(920, GREEN_BACK)
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (224, 104, 160)
    LOW = (40, 140, 150)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (130, 90, 130), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 90 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 2.6, (100, 70, 110), taper=(0, 0))
        for y in np.arange(0, sub.h, step * 0.8):
            sub.stroke([(0, y), (sub.w, y)], 2.6, (100, 70, 110), taper=(0, 0))
        for _ in range(8):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (120, 80, 40), 0.25, 0,
                  rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (170, 60, 140), 0.25), LOW, 921, low_kind="wood")
        x0, x1 = sub.ax(220), sub.ax(45)
        y0, y1 = sub.by(300), sub.by(0)

        def sign(cc, cx, cy):
            cc.ink(rrect(cx - 50, cy - 24, cx + 50, cy + 10, 5), (40, 30, 40), lw=2.2)
            cc.text(cx, cy - 7, "ON AIR", 15, (255, 80, 80))
            cc.glow2(cx, cy - 7, 70, (255, 60, 60), 0.4)
        flat_door(sub, x0, y0, x1, y1, (180, 50, 70), frame=(90, 40, 70), knob="L", sign=sign, seed=922)
        sub.ink(rrect((x0 + x1) / 2 - 64, y0 - 70, (x0 + x1) / 2 + 64, y0 - 32, 4), (40, 30, 40), lw=2.4)
        sub.text((x0 + x1) / 2, y0 - 51, "STUDIO", 18, (250, 240, 230))
        poster(sub, sub.ax(320), sub.by(330), 100, 130, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.2, "BE NICE", 13, (200, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.45, "TO THE", 11, (60, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.68, "MAKEUP", 13, (200, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.86, "LADY", 13, (200, 40, 80))), angle=-4, seed=923, peel="tr")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 924, low_kind="wood")
        x0, x1 = sub.ax(45), sub.ax(220)
        y0, y1 = sub.by(305), sub.by(0)

        def sign(cc, cx, cy):
            cc.ink(rect(cx - 52, cy + 40, cx + 52, cy + 84), (255, 236, 120), lw=2.2, shade=0.1)
            cc.text(cx, cy + 54, "CREW ONLY", 12, (180, 30, 50))
            cc.text(cx, cy + 72, "CONTROL BOOTH", 8, (60, 40, 60), "Bold")
        flat_door(sub, x0, y0, x1, y1, (90, 90, 120), frame=(60, 50, 80), knob="L", window=True, sign=sign, seed=925,
                  panels=False)
        # stairs through the little window
        wx0, wy0 = x0 + (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.08
        wx1, wy1 = x1 - (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.38
        for k in range(5):
            yy = wy1 - k * (wy1 - wy0) / 5
            sub.stroke([(wx0 + 4, yy - 6), (wx1 - 4 - k * 6, yy - 18)], 4, (40, 60, 70), opacity=0.8)
        intercom(sub, sub.ax(275), sub.by(150), 1.2)

    def floor(sub):
        tiles(sub, (226, 70, 120), (246, 226, 214), 0, 0, sub.w, sub.h, size=64 * sub.density, seed=926, chipped=0.1)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=920)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 927, chips=6, stains=4, low_kind="wood")
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=927)
    R.ao(0.45)
    R.edges(w=4.0)

    # ---------------- wall decor
    for i, (X, season, bg) in enumerate(((120, "SEASON 1", (60, 30, 90)), (330, "SEASON 2", (30, 40, 90)))):
        poster(c, *P(X, 330), 120, 150, bg,
               lambda p, w_, h_, season=season: (p.ink(Sh([heart_pts(w_ / 2, h_ * 0.4, w_ * 0.6)]), (255, 90, 150), lw=2.4),
                                                  p.text(w_ / 2, h_ * 0.38, "SDL", 18, (255, 255, 255)),
                                                  p.ink(rect(w_ * 0.12, h_ * 0.72, w_ * 0.88, h_ * 0.86), (255, 220, 80), lw=1.6),
                                                  p.text(w_ / 2, h_ * 0.79, season, 10, (60, 30, 60))),
               angle=(-4 if i == 0 else 3), seed=930 + i, peel=("br" if i == 0 else None))
    # signed photo of Roxy (framed)
    fx0, fy0 = P(930, 400)
    fx1, fy1 = P(1050, 250)
    c.ink(rect(fx0 - 12, fy0 - 12, fx1 + 12, fy1 + 12), (236, 196, 90), lw=3.0, shade=0.4, hi=0.5)
    c.ink(rect(fx0, fy0, fx1, fy1), (255, 160, 200), lw=2.0, shade=0.2)
    cx_, cy_ = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    c.ink(blob([(cx_ - 34, cy_ + 20), (cx_ - 40, cy_ - 30), (cx_, cy_ - 52), (cx_ + 38, cy_ - 30), (cx_ + 34, cy_ + 20)], 2),
          (96, 30, 80), lw=2.2)
    c.ink(ell(cx_ + 2, cy_ - 8, 22, 26), (240, 196, 160), lw=2.2, shade=0.3)
    c.ink(blob([(cx_ - 46, fy1), (cx_ - 36, cy_ + 34), (cx_ + 36, cy_ + 34), (cx_ + 46, fy1)], 2), (236, 46, 140), lw=2.2)
    c.stroke(bez((cx_ - 10, cy_ + 4), (cx_ + 2, cy_ + 12), (cx_ + 12, cy_ + 4), 8), 2, INK)
    c.text(cx_, fy1 + 30, "xoxo Roxy", 12, (120, 30, 80), "Bold", angle=-4)
    # clock + TV feed
    cx_, cy_ = P(620, 420)
    c.ink(ell(cx_, cy_, 26, 26), (250, 240, 220), lw=3.0, shade=0.4, hi=0.3)
    c.stroke([(cx_, cy_), (cx_, cy_ - 18)], 3)
    c.stroke([(cx_, cy_), (cx_ + 12, cy_ + 6)], 3)
    A.crt_tv(c, *P(1110, 400), *P(1250, 300), screen=(90, 230, 220), seed=5, text="ON AIR")
    c.ink(rect(*P(1160, 300), *P(1200, 280)), (80, 70, 90), lw=2.2)
    # string of bare bulbs along the top of the walls
    string_lights2(c, [P(0, Hb - 20, 200), P(0, Hb - 20, 0), P(440, Hb - 30), P(880, Hb - 20), P(Wb, Hb - 30), P(Wb, Hb - 20, 200)],
                   colors=((255, 236, 170),), sag=24, spacing=60, seed=7)
    lightbox(c, *P(1130, 245), *P(1250, 205), "QUIET PLEASE", (255, 60, 90), size=12)

    # ---------------- furniture, back to front
    # craft services table
    TX0, TX1, TZ0, TZ1 = 30, 300, 40, 120
    R.contact(TX0, TX1, TZ0, TZ1, 0.5)
    for X, Z in ((TX0 + 10, TZ0 + 8), (TX1 - 10, TZ0 + 8), (TX0 + 10, TZ1 - 8), (TX1 - 10, TZ1 - 8)):
        c.stroke([P(X, 0, Z), P(X, 72, Z)], 7, INK, taper=(0, 0), smooth=0)
        c.stroke([P(X, 0, Z), P(X, 72, Z)], 3.4, (150, 100, 70), taper=(0, 0), smooth=0)
    f = R.box(TX0, TX1, 66, 76, TZ0, TZ1)
    c.ink(Sh([f["top"]]), (250, 246, 240), lw=2.6, shade=0.1, hi=0.2)
    cloth = blob([f["front"][0], f["front"][1], P(TX1 + 2, 30, TZ1 + 2), P((TX0 + TX1) / 2, 26, TZ1 + 4), P(TX0 - 2, 30, TZ1 + 2)], 1)
    c.ink(cloth, (250, 246, 240), lw=2.6, shade=0.4, sw=10, hi=0.2)
    bx0, by0, bx1, by1 = cloth.bbox()
    for x in np.arange(bx0 + 8, bx1, 22):
        c.ink(rect(x, by0, x + 11, by1 + 4), (220, 50, 70), lw=0, shade=0, hi=0, clip=cloth, opacity=0.9)
    c.ink(cloth, (0, 0, 0, 0), lw=2.6, line_only=True)
    # bowl of cheese puffs
    x_, y_ = P(90, 76, 80)
    c.ink(Sh([[(x_ - 46, y_ - 22), (x_ + 46, y_ - 22), (x_ + 30, y_), (x_ - 30, y_)]]), (40, 170, 190), lw=2.6, shade=0.4, hi=0.3)
    for j in range(16):
        c.ink(ell(x_ + rng.uniform(-36, 36), y_ - 24 - rng.uniform(0, 14), 8, 5, rng.uniform(0, 180)), (255, 150, 30), lw=1.6,
              shade=0.4, hi=0.4)
    c.text(x_, y_ - 9, "PUFFS", 9, (255, 255, 255))
    # cup of bendy straws
    x_, y_ = P(180, 76, 70)
    c.ink(rrect(x_ - 14, y_ - 36, x_ + 14, y_, 4), (250, 250, 240), lw=2.4, shade=0.4)
    for j, col in enumerate([(255, 90, 150), (60, 220, 210), (255, 220, 90), (180, 120, 255)]):
        c.stroke([(x_ - 8 + j * 5, y_ - 34), (x_ - 10 + j * 7, y_ - 70), (x_ - 2 + j * 9, y_ - 80)], 3.4, col, smooth=1)
    # eclair on a plate with a sticky note
    x_, y_ = P(250, 76, 95)
    c.ink(ell(x_, y_ - 4, 34, 9), (250, 250, 246), lw=2.2, shade=0.3)
    c.ink(rrect(x_ - 24, y_ - 18, x_ + 24, y_ - 4, 7), (230, 180, 110), lw=2.2, shade=0.4)
    c.ink(rrect(x_ - 22, y_ - 20, x_ + 14, y_ - 12, 4), (90, 50, 30), lw=1.6)
    c.ink(ell(x_ + 18, y_ - 15, 7, 6), (180, 120, 200, 0), lw=0)
    nx_, ny_ = P(250, 120, 60)
    c.ink(Sh([rot_pts([(nx_ - 22, ny_ - 18), (nx_ + 22, ny_ - 18), (nx_ + 22, ny_ + 18), (nx_ - 22, ny_ + 18)], 6, nx_, ny_)]),
          (255, 236, 120), lw=1.8, shade=0.1)
    c.text(nx_, ny_ - 5, "CHET'S", 8, (200, 30, 50))
    c.text(nx_, ny_ + 7, "NO TOUCH", 6, (60, 40, 60), "Bold")
    c.stroke([(nx_, ny_ + 18), (x_, y_ - 18)], 1.2, (120, 110, 100))

    wardrobe_rack(c, R, 390, 540, 60, rng)
    makeup_station(c, R, 600, 860, rng)
    couch(c, R, 1000, 1290, 10, 110, col=(50, 160, 160), seed=4)
    # a cushion with a heart on the couch
    x_, y_ = P(1080, 90, 70)
    c.ink(blob([(x_ - 30, y_ + 16), (x_ - 34, y_ - 24), (x_ + 30, y_ - 30), (x_ + 34, y_ + 12)], 2), (255, 120, 170), lw=2.6,
          shade=0.4, hi=0.3)
    c.ink(Sh([heart_pts(x_, y_ - 6, 22)]), (250, 240, 200), lw=1.6)
    makeup_chair(c, R, 660, 800, 100, 175)
    # floor rug + a dropped sequin trail
    rug = [P(1150 + 200 * math.cos(a), 0, 300 + 70 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    c.ink(Sh([rug]), (110, 60, 160), lw=3.0, shade=0.2, hi=0.1, tex=0.25)
    rr = [P(1150 + 160 * math.cos(a), 0, 300 + 55 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    c.ink(Sh([rr]), (140, 90, 190), lw=2.0, shade=0.1, hi=0.0, tex=0.25)
    for _ in range(30):
        x_, y_ = P(rng.uniform(400, 900), 0, rng.uniform(150, 420))
        c.ink(ell(x_, y_, 2.2, 1.6), (255, 236, 150), lw=0, shade=0, hi=0, opacity=0.8)

    # ---------------- ceiling: two bare-bulb pendants + a panel light, cables, cobwebs
    panel_light(c, R, 560, 820, 200, 300, cone=0.12, floor_y=980)
    for X, Z in ((260, 400), (1080, 400)):
        top = P(X, Hb, Z)
        pendant_lamp(c, top[0], top[1], P(X, Hb - 46, Z)[1], w=120, col=(40, 170, 170), cone_to=980, cone_w=300,
                     cone_strength=0.16)
    cable(c, P(0, Hb, 300), P(600, Hb, 360), sag=50, w=6, col=(60, 40, 80))
    hanging_cable(c, P(980, Hb, 80), 90, sway=14, w=5, col=(60, 40, 90), seed=6)
    cobweb(c, *P(0, Hb, 0), 100, "tl", opacity=0.45)
    cobweb(c, *P(Wb, Hb, 0), 90, "tr", opacity=0.4)

    room_grade(c, lights=[(R.pt(730, 270)[0], R.pt(730, 270)[1], 420, 0.45), (P(260, 300, 400)[0], 760, 420, 0.3),
                          (P(1080, 300, 400)[0], 780, 440, 0.3), (P(1180, 350)[0], P(1180, 350)[1], 220, 0.3, (90, 230, 220)),
                          (1800, 560, 180, 0.25, (255, 60, 80))],
               ambient=0.98, vign=0.5, top_dark=0.3, bottom_dark=0.3)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 160, 1110, 280, seed=9)
        fg_bottles(sub, 1600, 1060, 5, 0.9, seed=4)
        fg_table_edge(sub, 1500, 2000, 1020, 120)
        fg_cable(sub, [(-20, 1050), (500, 1066), (1000, 1060), (1500, 1074)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_tv_green_room.png")


# =========================================================================== 3. Control booth
def foam_panel(sub, x0, y0, x1, y1, col=(96, 50, 120), cell=34):
    """Acoustic foam (egg-crate pyramids) in flat space."""
    sub.ink(rect(x0, y0, x1, y1), shade_col(col, 0.8), lw=2.4, shade=0.2, hi=0, tex=0.1)
    for yy in np.arange(y0, y1 - 1, cell):
        for xx in np.arange(x0, x1 - 1, cell):
            a, b_ = (xx, yy), (min(x1, xx + cell), min(y1, yy + cell))
            cx, cy = (a[0] + b_[0]) / 2, (a[1] + b_[1]) / 2
            sub.ink(Sh([[a, (b_[0], a[1]), (cx, cy)]]), hi_col(col, 0.18), lw=0, shade=0, hi=0, ao=0, tex=0.05, wob=0)
            sub.ink(Sh([[(b_[0], a[1]), b_, (cx, cy)]]), col, lw=0, shade=0, hi=0, ao=0, tex=0.05, wob=0)
            sub.ink(Sh([[b_, (a[0], b_[1]), (cx, cy)]]), shade_col(col, 0.7), lw=0, shade=0, hi=0, ao=0, tex=0.05, wob=0)
            sub.ink(Sh([[(a[0], b_[1]), a, (cx, cy)]]), shade_col(col, 0.86), lw=0, shade=0, hi=0, ao=0, tex=0.05, wob=0)


def monitor_screen(c, x0, y0, x1, y1, kind, rng):
    """One little monitor picture."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "stage":
        c.ink(rect(x0, y0, x1, y1), (200, 40, 130), lw=0, shade=0, hi=0)
        c.ink(Sh([heart_pts(cx, cy - h * 0.05, w * 0.42)]), (255, 120, 180), lw=1.4)
        c.ink(rect(x0, y1 - h * 0.18, x1, y1), (90, 40, 110), lw=0, shade=0, hi=0)
    elif kind == "audience":
        c.ink(rect(x0, y0, x1, y1), (90, 50, 120), lw=0, shade=0, hi=0)
        for r_ in range(3):
            for i in range(6):
                c.ink(ell(x0 + w * (i + 0.5 + (r_ % 2) * 0.3) / 6.3, y0 + h * (0.3 + r_ * 0.25), w * 0.05, w * 0.06),
                      rng.choice(SKINS), lw=0.8, shade=0)
    elif kind == "parking":
        c.ink(rect(x0, y0, x1, y1), (30, 40, 70), lw=0, shade=0, hi=0)
        c.ink(rect(x0, y0 + h * 0.6, x1, y1), (60, 60, 80), lw=0, shade=0, hi=0)
        c.ink(rrect(cx - w * 0.25, cy, cx + w * 0.25, cy + h * 0.25, 4), (220, 60, 70), lw=1.2)
        c.ink(ell(x0 + w * 0.8, y0 + h * 0.2, 4, 4), (255, 240, 180), lw=0)
    elif kind == "teeth":
        c.ink(rect(x0, y0, x1, y1), (236, 178, 130), lw=0, shade=0, hi=0)
        c.ink(Sh([[(x0 + w * 0.1, cy - h * 0.15), (x1 - w * 0.1, cy - h * 0.2), (cx + w * 0.1, cy + h * 0.32), (cx - w * 0.2, cy + h * 0.3)]]),
              (150, 30, 50), lw=1.4, shade=0)
        c.ink(rect(x0 + w * 0.14, cy - h * 0.16, x1 - w * 0.14, cy + h * 0.02), (255, 255, 250), lw=1.0, shade=0)
        for i in range(1, 6):
            xx = x0 + w * 0.14 + (w * 0.72) * i / 6
            c.stroke([(xx, cy - h * 0.16), (xx, cy + h * 0.02)], 1.0, (180, 170, 170), taper=(0, 0))
        c.stroke([(x0 + w * 0.3, cy - h * 0.12), (x0 + w * 0.36, cy - h * 0.3)], 2, (255, 255, 255))
    elif kind == "count":
        c.ink(rect(x0, y0, x1, y1), (20, 14, 26), lw=0, shade=0, hi=0)
        c.text(cx, cy, "4:00", int(h * 0.42), (255, 60, 60))
    elif kind == "bars":
        cols = [(240, 240, 240), (240, 230, 60), (60, 220, 220), (60, 220, 80), (220, 60, 220), (230, 50, 50), (50, 60, 220)]
        for i, col in enumerate(cols):
            c.ink(rect(x0 + w * i / 7, y0, x0 + w * (i + 1) / 7 + 1, y1), col, lw=0, shade=0, hi=0)
    elif kind == "roxy":
        c.ink(rect(x0, y0, x1, y1), (255, 160, 200), lw=0, shade=0, hi=0)
        c.ink(ell(cx, cy - h * 0.08, w * 0.2, h * 0.3), (96, 30, 80), lw=1.2)
        c.ink(ell(cx + w * 0.02, cy - h * 0.02, w * 0.13, h * 0.22), (240, 196, 160), lw=1.0)
        c.ink(blob([(cx - w * 0.3, y1), (cx - w * 0.2, cy + h * 0.25), (cx + w * 0.2, cy + h * 0.25), (cx + w * 0.3, y1)], 1),
              (236, 46, 140), lw=1.0)
    elif kind == "heart":
        c.ink(rect(x0, y0, x1, y1), (50, 20, 70), lw=0, shade=0, hi=0)
        c.ink(Sh([heart_pts(cx, cy, w * 0.5)]), (255, 70, 150), lw=1.4)
    elif kind == "dex":
        c.ink(rect(x0, y0, x1, y1), (60, 100, 150), lw=0, shade=0, hi=0)
        c.ink(ell(cx, cy - h * 0.06, w * 0.13, h * 0.22), (255, 206, 168), lw=1.0)
        c.ink(blob([(cx - w * 0.16, cy - h * 0.2), (cx, cy - h * 0.42), (cx + w * 0.16, cy - h * 0.2)], 1), (250, 120, 40), lw=1.0)
        c.ink(blob([(cx - w * 0.3, y1), (cx - w * 0.2, cy + h * 0.2), (cx + w * 0.2, cy + h * 0.2), (cx + w * 0.3, y1)], 1),
              (28, 196, 200), lw=1.0)
        c.text(cx, y0 + h * 0.15, "WHO?", int(h * 0.16), (255, 255, 255))
    else:  # static
        c.ink(rect(x0, y0, x1, y1), (120, 120, 130), lw=0, shade=0, hi=0)
        for _ in range(60):
            x_, y_ = rng.uniform(x0, x1 - 3), rng.uniform(y0, y1 - 2)
            c.ink(rect(x_, y_, x_ + 3, y_ + 2), rng.choice([(240, 240, 240), (40, 40, 50)]), lw=0, shade=0, hi=0)
    for yy in np.arange(y0 + 2, y1 - 1, 4):
        c.stroke([(x0 + 1, yy), (x1 - 1, yy)], 0.8, (0, 0, 0), opacity=0.12, taper=(0, 0), smooth=0)
    c.stroke([(x0 + w * 0.1, y1 - h * 0.15), (x0 + w * 0.35, y0 + h * 0.1)], 4, (255, 255, 255), opacity=0.15)


def studio_view(c, x0, y0, x1, y1, rng):
    """What the booth window looks down on: the studio floor and the pink stage."""
    w, h = x1 - x0, y1 - y0
    c.ink(rect(x0, y0, x1, y1), ("v", (40, 20, 60), (80, 40, 100)), lw=0, shade=0, hi=0)
    for i in range(18):
        xx0, xx1 = x0 + w * 0.25 + w * 0.7 * i / 18, x0 + w * 0.25 + w * 0.7 * (i + 1) / 18
        c.ink(rect(xx0, y0 + h * 0.08, xx1 + 1, y0 + h * 0.62), (226, 50, 150) if i % 2 == 0 else (190, 34, 120), lw=0, shade=0,
              hi=0)
    c.ink(rect(x0 + w * 0.25, y0 + h * 0.08, x1 - w * 0.05, y0 + h * 0.14), (250, 206, 90), lw=0, shade=0, hi=0)
    c.ink(Sh([heart_pts(x0 + w * 0.6, y0 + h * 0.3, w * 0.18)]), (255, 110, 170), lw=1.8, shade=0.2)
    c.ink(rect(x0 + w * 0.22, y0 + h * 0.62, x1, y0 + h * 0.7), (80, 30, 100), lw=0, shade=0, hi=0)
    c.ink(rect(x0, y0 + h * 0.7, x1, y1), (70, 50, 90), lw=0, shade=0, hi=0)
    # bleachers with tiny heads on the left
    for r_ in range(3):
        yy = y0 + h * (0.34 + r_ * 0.12)
        c.ink(rect(x0, yy + 6, x0 + w * 0.2, yy + h * 0.12), (120, 64, 130), lw=0, shade=0, hi=0)
        for i in range(6):
            c.ink(ell(x0 + w * (0.018 + i * 0.032), yy, 5, 6), rng.choice(SKINS), lw=1.0, shade=0)
    # tiny Roxy + Chet on the floor
    for (px, col) in ((0.5, (236, 46, 140)), (0.72, (250, 250, 246))):
        bx, by = x0 + w * px, y0 + h * 0.86
        c.ink(rect(bx - 6, by - 30, bx + 6, by), col, lw=1.0, shade=0)
        c.ink(ell(bx, by - 37, 6, 7), (240, 196, 160), lw=1.0)
    for i in range(4):
        sx = x0 + w * (0.3 + i * 0.18)
        c.light_cone((sx, y0), (sx - 60, y1), (sx + 60, y1), (255, 230, 200), 0.12, 10)
    c.glow2(x0 + w * 0.6, y0 + h * 0.35, w * 0.5, (255, 80, 170), 0.35)


def paint_tv_control_booth():
    c, R, rng = new_room(940, BOOTH_BACK)
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (110, 54, 130)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (70, 50, 90), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 100 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 2.6, (50, 34, 66), taper=(0, 0))
        for y in np.arange(0, sub.h, step * 0.8):
            sub.stroke([(0, y), (sub.w, y)], 2.6, (50, 34, 66), taper=(0, 0))
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (40, 20, 30), 0.25, 0, rng.randint(0, 99))

    def left(sub):
        grunge_wall(sub, sub.w, sub.h, mix(WALL, (140, 50, 140), 0.2), seed=941, chips=4, stains=3, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(60, 30, 70))
        x0, x1 = sub.ax(250), sub.ax(60)
        y0, y1 = sub.by(300), sub.by(0)
        # stairwell opening: dark, steps going down, handrail
        sub.ink(rect(x0 - 20, y0 - 20, x1 + 20, y1), (150, 140, 160), lw=3.0, shade=0.4, sw=10, hi=0.3)
        sub.ink(rect(x0, y0, x1, y1), ("v", (40, 40, 60), (16, 12, 24)), lw=2.6, shade=0.2, hi=0)
        for k in range(7):
            yy = y0 + (y1 - y0) * (0.35 + k * 0.09)
            sub.ink(rect(x0 + 6, yy, x1 - 6 - k * 4, yy + 12), (90, 90, 110), lw=1.8, shade=0.2, hi=0.3)
        sub.stroke([(x0 + 10, y0 + (y1 - y0) * 0.35), (x1 - 10, y1 - 20)], 6, (220, 220, 230))
        sub.stroke([(x0 + 10, y0 + (y1 - y0) * 0.35), (x0 + 10, y1 - 10)], 5, (200, 200, 210))
        sub.ink(rrect((x0 + x1) / 2 - 60, y0 - 74, (x0 + x1) / 2 + 60, y0 - 36, 5), (40, 140, 80), lw=2.4, shade=0.3)
        sub.text((x0 + x1) / 2, y0 - 55, "STAIRS", 17, (240, 255, 240))
        poster(sub, sub.ax(330), sub.by(330), 110, 140, (250, 240, 220),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.18, "RULE 1", 13, (200, 40, 60)),
                                  p.text(w_ / 2, h_ * 0.34, "don't touch", 9, (60, 40, 80), "Bold"),
                                  p.text(w_ / 2, h_ * 0.52, "RULE 2", 13, (200, 40, 60)),
                                  p.text(w_ / 2, h_ * 0.68, "DON'T TOUCH", 9, (60, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.86, "RULE 3: coffee", 9, (60, 40, 80), "Bold")),
               angle=-3, seed=942, peel="br")

    def right(sub):
        grunge_wall(sub, sub.w, sub.h, hi_col(WALL, 0.05), seed=943, chips=3, stains=3, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(60, 30, 70))
        foam_panel(sub, sub.ax(60), sub.by(420), sub.ax(330), sub.by(200), (120, 60, 140), 30)

    def floor(sub):
        carpet(sub, (64, 50, 86), 0, 0, sub.w, sub.h, seed=944)
        step = 110 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 1.6, (40, 30, 56), taper=(0, 0), opacity=0.5)
        for y in np.arange(0, sub.h, step):
            sub.stroke([(0, y), (sub.w, y)], 1.6, (40, 30, 56), taper=(0, 0), opacity=0.5)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=940)

    def back(sub):
        grunge_wall(sub, sub.w, sub.h, WALL, seed=945, chips=5, stains=4, cracks=2, floor_y=sub.h)
        skirting(sub, sub.w, sub.h, col=(60, 30, 70))
        foam_panel(sub, sub.ax(520), sub.by(350), sub.ax(745), sub.by(130), (120, 60, 140), 32)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=945)
    R.ao(0.5)
    R.edges(w=4.0)

    # ---------------- monitor wall (12 screens) over the vision-mixer console
    mx0, my0 = P(20, 445)
    mx1, my1 = P(475, 125)
    c.ink(rect(mx0 - 10, my0 - 10, mx1 + 10, my1 + 10), (36, 30, 46), lw=3.2, shade=0.3, hi=0.3)
    kinds = ["stage", "audience", "parking", "teeth", "bars", "roxy", "count", "static", "heart", "dex", "stage", "audience"]
    cw, ch = (mx1 - mx0) / 4, (my1 - my0) / 3
    for j in range(3):
        for i in range(4):
            x0, y0 = mx0 + i * cw + 6, my0 + j * ch + 6
            c.ink(rrect(x0, y0, x0 + cw - 12, y0 + ch - 12, 4), (20, 18, 28), lw=2.4, shade=0.2)
            monitor_screen(c, x0 + 6, y0 + 6, x0 + cw - 18, y0 + ch - 24, kinds[j * 4 + i], rng)
            c.ink(ell(x0 + cw - 22, y0 + ch - 17, 2.4, 2.4), (90, 255, 140) if (i + j) % 3 else (255, 70, 70), lw=0)
    c.glow2((mx0 + mx1) / 2, (my0 + my1) / 2, 420, (90, 200, 255), 0.35)
    # console
    R.contact(-10, 500, 10, 120, 0.5)
    f = R.ink_box(-10, 500, 0, 96, 10, 116, (60, 56, 84), top=(90, 86, 116), side=(40, 36, 56), seed=946)
    for i in range(22):
        for jz in range(2):
            x_, y_ = P(10 + i * 21.5, 96, 40 + jz * 40)
            col = [(255, 80, 100), (255, 220, 80), (80, 220, 230), (120, 230, 120), (240, 240, 250)][(i + jz * 2) % 5]
            c.ink(rrect(x_ - 6, y_ - 3, x_ + 6, y_ + 3, 2), col, lw=1.2, shade=0, hi=0.4)
    fr = f["front"]
    for i in range(4):
        q = R.box(10 + i * 120, 120 + i * 120, 10, 80, 116, 116)["front"]
        c.ink(Sh([q]), (70, 66, 96), lw=2.0, shade=0.3, hi=0.3)
    x_, y_ = P(260, 96, 60)
    c.ink(ell(x_, y_, 18, 6), (240, 240, 240), lw=1.8)   # a styrofoam cup
    # ---------------- coffee cabinet + Norma's coffee maker
    R.contact(530, 650, 8, 84, 0.5)
    R.ink_box(530, 650, 0, 110, 8, 84, (150, 96, 70), top=(190, 140, 100), seed=947)
    for X in (560, 620):
        x_, y_ = P(X, 60, 84)
        c.ink(ell(x_, y_, 4, 4), (236, 196, 90), lw=1.4)
    g = R.ink_box(556, 624, 110, 196, 24, 70, (40, 36, 50), top=(70, 66, 80), seed=948)
    fr = g["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    c.ink(rect(x0 + 8, y0 + (y1 - y0) * 0.45, x1 - 8, y1 - 6), (60, 40, 30), lw=1.8)
    c.ink(rrect(x0 + 14, y0 + (y1 - y0) * 0.55, x1 - 14, y1 - 8, 4), (170, 210, 230, 200), lw=1.8, shade=0.2)
    c.ink(rect(x0 + 16, y0 + (y1 - y0) * 0.75, x1 - 16, y1 - 10), (90, 50, 30), lw=0)
    c.ink(rect(x0 + 6, y0 + 6, x1 - 6, y0 + 30), (250, 246, 236), lw=1.6, shade=0.1)
    c.text((x0 + x1) / 2, y0 + 13, "NORMA'S", 9, (200, 30, 50))
    c.text((x0 + x1) / 2, y0 + 24, "touch it + die", 6, (60, 40, 60), "Bold")
    c.ink(ell(x1 - 10, y0 + 40, 3, 3), (255, 60, 60), lw=0)
    c.glow2(x1 - 10, y0 + 40, 14, (255, 60, 60), 0.5)
    for k in range(3):
        sx = (x0 + x1) / 2 - 12 + k * 12
        c.stroke([(sx, y0 - 6), (sx - 6, y0 - 24), (sx + 4, y0 - 40), (sx - 2, y0 - 54)], 2.2, (240, 240, 250), opacity=0.5,
                 smooth=2)
    # countdown clock
    cx0, cy0 = P(540, 445)
    cx1, cy1 = P(745, 370)
    c.ink(rrect(cx0, cy0, cx1, cy1, 8), (24, 16, 28), lw=3.0, shade=0.2, hi=0.3)
    c.text((cx0 + cx1) / 2, (cy0 + cy1) / 2, "00:04:00", 30, (255, 50, 60))
    c.glow2((cx0 + cx1) / 2, (cy0 + cy1) / 2, 160, (255, 40, 60), 0.5)
    c.text((cx0 + cx1) / 2, cy1 + 16, "TO AIR", 12, (255, 120, 130))
    # ---------------- the big window down onto the studio
    wx0, wy0 = P(770, 430)
    wx1, wy1 = P(1300, 150)
    c.ink(rect(wx0 - 18, wy0 - 18, wx1 + 18, wy1 + 18), (150, 140, 170), lw=3.0, shade=0.4, sw=10, hi=0.3)
    studio_view(c, wx0, wy0, wx1, wy1, rng)
    for xx in (wx0 + (wx1 - wx0) / 3, wx0 + 2 * (wx1 - wx0) / 3):
        c.ink(rect(xx - 7, wy0, xx + 7, wy1), (150, 140, 170), lw=2.4, shade=0.3)
    c.stroke([(wx0 + 30, wy1 - 20), (wx0 + 120, wy0 + 20)], 14, (255, 255, 255), opacity=0.12)
    c.stroke([(wx1 - 140, wy1 - 20), (wx1 - 60, wy0 + 20)], 8, (255, 255, 255), opacity=0.1)
    c.ink(rect(wx0 - 30, wy1 + 18, wx1 + 30, wy1 + 34), (170, 160, 190), lw=2.6, shade=0.4, sw=6, hi=0.3)
    # a heart-shaped sticky note on the glass
    c.ink(Sh([rot_pts([(wx0 + 30, wy0 + 30), (wx0 + 80, wy0 + 30), (wx0 + 80, wy0 + 76), (wx0 + 30, wy0 + 76)], 8, wx0 + 55, wy0 + 53)]),
          (255, 236, 120), lw=1.8, shade=0.1)
    c.text(wx0 + 55, wy0 + 52, "4 MIN!!", 10, (200, 30, 50), angle=-8)
    # ---------------- director's chair (rolling)
    X, Z = 720, 190
    cx_, cy_ = P(X, 0, Z)
    k = R.k(Z)
    R.contact(X - 40, X + 40, Z - 30, Z + 30, 0.4)
    for dx in (-40, -14, 14, 40):
        c.stroke([(cx_, cy_ - 30 * k), (cx_ + dx * k, cy_ - 4)], 5 * k, INK)
        c.ink(ell(cx_ + dx * k, cy_ - 2, 6, 5), (30, 26, 40), lw=0)
    c.stroke([(cx_, cy_ - 30 * k), (cx_, cy_ - 80 * k)], 8 * k, INK)
    R.ink_box(X - 40, X + 40, 80, 96, Z - 30, Z + 30, (90, 60, 150), seed=949)
    R.ink_box(X - 36, X + 36, 96, 200, Z - 32, Z - 20, (90, 60, 150), seed=950)
    tx, ty = P(X, 160, Z - 20)
    c.text(tx, ty, "DIRECTOR", int(10 * k), (255, 236, 120))
    # ---------------- director's desk on the right: talkback mic, papers, lamp
    DX0, DX1, DZ0, DZ1 = 1110, Wb, 110, 228
    R.contact(DX0, DX1, DZ0, DZ1, 0.5)
    f = R.ink_box(DX0, DX1 + 4, 0, 100, DZ0, DZ1, (70, 66, 96), top=(110, 106, 136), side=(46, 42, 66), seed=951)
    for i in range(3):
        q = R.box(DX0 + 10 + i * 66, DX0 + 66 + i * 66, 12, 88, DZ1, DZ1)["front"]
        c.ink(Sh([q]), (80, 76, 108), lw=2.0, shade=0.3, hi=0.3)
    # gooseneck talkback mic + button
    bx_, by_ = P(1200, 100, 170)
    c.ink(ell(bx_, by_, 26, 9), (40, 36, 50), lw=2.4, shade=0.3, hi=0.3)
    neck = [(bx_, by_ - 4), (bx_ + 6, by_ - 60), (bx_ - 18, by_ - 110), (bx_ - 54, by_ - 120)]
    c.stroke(neck, 9, INK, smooth=2)
    c.stroke(neck, 5, (150, 150, 170), smooth=2)
    c.ink(rrect(bx_ - 80, by_ - 132, bx_ - 46, by_ - 110, 9), (40, 36, 50), lw=2.4, shade=0.3, hi=0.4)
    tb_x, tb_y = P(1250, 100, 200)
    c.ink(rrect(tb_x - 40, tb_y - 12, tb_x + 40, tb_y + 6, 4), (40, 36, 50), lw=2.0)
    c.ink(ell(tb_x - 20, tb_y - 4, 9, 5), (255, 40, 50), lw=1.6, hi=0.6)
    c.glow2(tb_x - 20, tb_y - 4, 28, (255, 40, 60), 0.5)
    c.text(tb_x + 12, tb_y - 4, "TALK", 9, (255, 236, 200))
    # papers, a stopwatch, a donut
    for kk in range(3):
        px_, py_ = P(1160 + kk * 12, 101, 150 + kk * 8)
        c.ink(Sh([rot_pts([(px_ - 30, py_ - 7), (px_ + 30, py_ - 7), (px_ + 30, py_ + 7), (px_ - 30, py_ + 7)], kk * 7 - 7, px_, py_)]),
              (248, 246, 236), lw=1.8)
    px_, py_ = P(1290, 101, 140)
    c.ink(ell(px_, py_ - 4, 16, 7), (240, 170, 90), lw=2.0, shade=0.3)
    c.ink(ell(px_, py_ - 6, 5, 2), (60, 40, 30), lw=0)
    # desk lamp
    lx_, ly_ = P(1300, 100, 130)
    c.ink(ell(lx_, ly_, 18, 6), (40, 170, 170), lw=2.2)
    c.stroke([(lx_, ly_), (lx_ - 6, ly_ - 60), (lx_ - 40, ly_ - 84)], 5, INK)
    c.stroke([(lx_, ly_), (lx_ - 6, ly_ - 60), (lx_ - 40, ly_ - 84)], 2.4, (40, 170, 170))
    c.ink(Sh([[(lx_ - 72, ly_ - 84), (lx_ - 30, ly_ - 104), (lx_ - 20, ly_ - 78), (lx_ - 56, ly_ - 64)]]), (40, 170, 170), lw=2.6,
          shade=0.4, hi=0.4)
    c.light_cone((lx_ - 44, ly_ - 72), (lx_ - 170, ly_ + 20), (lx_ + 10, ly_ + 26), strength=0.4, blur_px=12)
    # ---------------- cables on the floor, a cable tray on the ceiling, downlights
    floor_cable(c, [P(480, 0, 116), P(620, 0, 260), P(900, 0, 240), P(1100, 0, 280), P(DX0, 0, DZ1)], 6)
    floor_cable(c, [P(300, 0, 116), P(240, 0, 300), P(60, 0, 340)], 5, (50, 30, 60))
    for X, Z in ((250, 150), (660, 150), (1060, 150), (450, 380), (900, 380)):
        x_, y_ = P(X, Hb, Z)
        c.ink(ell(x_, y_ + 2, 34 * R.k(Z), 8 * R.k(Z)), (255, 246, 220), lw=2.2, shade=0, hi=0, ao=0)
        c.glow2(x_, y_ + 6, 90, GLOW, 0.4)
        c.light_cone((x_, y_ + 6), (x_ - 160, 1000), (x_ + 160, 1000), (255, 240, 200), 0.07, 30)
    pipe(c, [P(-200, Hb - 20, 300), P(Wb + 200, Hb - 20, 300)], w=22, col=(90, 80, 120))
    hanging_cable(c, P(560, Hb, 300), 110, sway=16, w=5, col=(40, 30, 60), seed=4)
    cobweb(c, *P(0, Hb, 0), 100, "tl", opacity=0.4)
    cobweb(c, *P(Wb, Hb, 0), 80, "tr", opacity=0.35)

    room_grade(c, lights=[((mx0 + mx1) / 2, (my0 + my1) / 2, 520, 0.4, (90, 200, 255)), ((wx0 + wx1) / 2, 450, 560, 0.45, (255, 90, 180)),
                          ((cx0 + cx1) / 2, (cy0 + cy1) / 2, 200, 0.35, (255, 60, 60)), (lx_ - 80, ly_ + 10, 260, 0.4),
                          (900, 840, 600, 0.25)],
               ambient=0.9, vign=0.58, top_dark=0.35, bottom_dark=0.3)
    c.painterly(0.05)

    def fg(sub):
        sub.ink(poly([(-40, 1080), (-40, 1000), (700, 990), (760, 1080)]), FG, lw=0, shade=0.2, hi=0.25, hw=6)
        for i in range(10):
            sub.ink(ell(40 + i * 64, 1010, 14, 7), (50, 30, 76), lw=0, shade=0, hi=0)
        fg_cable(sub, [(700, 1060), (1200, 1050), (1960, 1070)], 16)
        sub.ink(rrect(1700, 960, 1800, 1100, 14), FG, lw=0, shade=0.2, hi=0.2)       # a mug in the corner
        sub.stroke([(1800, 990), (1840, 1010), (1840, 1050), (1800, 1060)], 14, FG)
        # headphones hanging into the top-left corner
        sub.stroke([(120, -20), (126, 140)], 6, FG)
        sub.stroke([(60, 230), (70, 150), (126, 130), (182, 150), (192, 230)], 14, FG, smooth=2)
        sub.ink(rrect(36, 210, 92, 290, 20), FG, lw=0, shade=0.2, hi=0.2)
        sub.ink(rrect(160, 210, 216, 290, 20), FG, lw=0, shade=0.2, hi=0.2)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_tv_control_booth.png")


# =========================================================================== characters (finale only)
def sparkle4(c, x, y, s, col=(255, 255, 240)):
    c.ink(Sh([star_pts(x, y, s, s * 0.22, n=4, rot=-90)]), col, lw=1.4, shade=0, hi=0, ao=0)


def paint_chet_studwell(height=415, name="hs_chet_studwell.png"):
    """Chet Studwell: the rival contestant. Blond pompadour, white disco suit, grape soda, hidden earpiece."""
    W, Hc = 420, 640
    skin = (238, 180, 132)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=81)
    b = Body(c, 190, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.14, waist=0.9, hips=0.98, limbs=1.0, head=1.0, legs=1.04, neck=1.1, chest=0.8,
                        hand=1.0, foot=1.0),
             pose=dict(arm_n=8, fore_n=84, arm_f=-16, fore_f=34, leg_n=7, shin_n=-2, leg_f=-9, shin_f=4, lean=-4,
                       head_dx=0.8), seed=8)
    suit, suit_sh, suit_hi = (248, 244, 236), (176, 160, 214), (255, 255, 255)
    shirt = (140, 50, 180)
    hair, hair_sh, hair_hi = (255, 220, 100), (214, 156, 52), (255, 248, 200)
    gold = (250, 206, 70)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm: fist on the hip
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.6, w1=7.8, cuff=7.0), mix(suit, suit_sh, 0.35), lw=2.8, shade=0.4, scol=suit_sh)
    # legs: white flares + white loafers with gold buckles
    def loafers(bb, near):
        bb.shoe(near, (246, 240, 230) if near else (214, 206, 220), (120, 100, 90), "shoe", length=1.05)
        an = bb.ankle_n if near else bb.ankle_f
        c.ink(rect(*bb.P(an[0] + 3.0, an[1] - 0.6), *bb.P(an[0] + 5.0, an[1] - 2.0)), gold, lw=1.4)
    legs(b, suit, w=(9.4, 6.6, 7.6), scol=suit_sh, shoe=loafers)
    hips = Sh([b.Ps([(-5.6, b.hip_y + 5), (5.2, b.hip_y + 5), (5.6, b.hip_y - 3), (-5.8, b.hip_y - 3)])])
    c.ink(hips, suit, lw=3.0, shade=0.45, scol=suit_sh)
    c.ink(Sh([b.Ps([(-5.7, b.hip_y + 5.4), (5.3, b.hip_y + 5.4), (5.3, b.hip_y + 3.2), (-5.7, b.hip_y + 3.2)])]), (70, 40, 60), lw=2.0)
    c.ink(rrect(*b.P(1.6, b.hip_y + 5.8), *b.P(4.0, b.hip_y + 2.8), 2), gold, lw=1.6, hi=0.6)
    # neck + torso: purple shirt open at the collar, white jacket with huge lapels
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y + 1.0, flare=0.6, neck_open=1.3)])
    c.ink(torso, suit, lw=3.0, shade=0.55, sw=20, scol=suit_sh, hi=0.4, hcol=suit_hi, rim=0.2, rcol=(255, 230, 250))
    sy, sx = b.shoulder_y, b.lean_dx
    vee = Sh([b.Ps([(sx - 2.2, sy + 1.8), (sx + 3.6, sy + 1.2), (sx + 2.2, b.hip_y + 9), (sx + 0.8, b.hip_y + 9)])])
    c.ink(vee, shirt, lw=2.4, shade=0.4, hi=0.3)
    c.ink(Sh([b.Ps([(sx - 1.4, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 1.2, sy - 7.5)])]), skin, lw=2.2, shade=0.45, sw=6)
    for pts in ([(sx - 3.8, sy + 2.2), (sx - 1.0, sy + 0.8), (sx + 1.0, sy - 8), (sx + 1.4, b.hip_y + 8), (sx - 2.0, sy - 9)],
                [(sx + 3.0, sy + 1.4), (sx + 6.6, sy + 0.4), (sx + 4.6, sy - 9), (sx + 2.6, b.hip_y + 8)]):
        c.ink(Sh([b.Ps(pts)]), suit, lw=2.6, shade=0.4, sw=8, scol=suit_sh, hi=0.45)
    for pts in ([(sx - 2.6, sy + 1.0), (sx - 6.0, sy + 0.8), (sx - 3.4, sy - 4.8)], [(sx + 3.4, sy + 0.8), (sx + 7.6, sy + 0.2), (sx + 4.6, sy - 4.2)]):
        c.ink(Sh([b.Ps(pts)]), shirt, lw=2.2, shade=0.35)   # big shirt collar over the lapels
    c.ink(ell(*b.P(sx * 0.7 + 4.4, sy - 6), 4.6, 4.6), (230, 40, 90), lw=1.8, hi=0.5)    # carnation
    # gold chain + medallion
    c.stroke([b.P(sx - 1.2, sy + 1.2), b.P(sx + 0.6, sy - 4.0), b.P(sx + 2.8, sy + 0.8)], 2.2, gold, smooth=1)
    mx_, my_ = b.P(sx + 0.7, sy - 4.6)
    c.ink(ell(mx_, my_, 8, 8), gold, lw=2.0, shade=0.4, hi=0.7, hw=3)
    c.label(mx_, my_ + 1, "C", 8, (150, 100, 20), mirror=True)
    folds(c, [b.Ps([(-3, b.hip_y + 14), (-1, b.hip_y + 9)]), b.Ps([(4, b.hip_y + 15), (3, b.hip_y + 10)])], suit_sh, 1.6, 0.6)
    # head: square jaw, big chin, sparkly grin
    head = Sh([b.head_pts(jaw=1.16, chin=1.16, cheek=1.02, chin_drop=1.05)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    cx_, cy_ = fa["chin"]
    c.stroke([(cx_ + r * 0.05, cy_ - ry * 0.05), (cx_ + r * 0.1, cy_ - ry * 0.16)], 1.6, shade_col(skin, 0.6))   # chin dimple
    b.cheeks(fa["eye_n"][0] + r * 0.1, fa["eye_n"][1] + ry * 0.42, r * 0.24, (240, 120, 100), 0.3)
    b.eyes(iris=(60, 150, 230), look=(0.45, 0.05), lid=0.36, size=0.98, tilt=-0.05)
    b.brows(col=hair_sh, lift_n=0.22, lift_f=0.04, tilt_n=-0.1, tilt_f=-0.45, w=r * 0.13)
    b.nose("long", 1.0)
    b.mouth("teeth", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.82, r * 0.42)
    mx, my = fa["mouth"]
    sparkle4(c, mx + r * 0.42, my - ry * 0.14, r * 0.22)
    b.ear(0.95)
    # the earpiece + coiled wire down into the collar
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.08, ey_ + r * 0.05, r * 0.13, r * 0.15), (250, 220, 190), lw=1.8, shade=0.3, hi=0.4)
    coil = [(ex_ - r * 0.1 + math.sin(t * 2.2) * r * 0.08, ey_ + r * 0.2 + t * r * 0.12) for t in range(18)]
    c.stroke(coil, 1.4, (200, 170, 150), taper=(0, 0), smooth=1, opacity=0.9)
    # pompadour
    pomp = blob([(hx - r * 1.08, hy + ry * 0.35), (hx - r * 1.16, hy - ry * 0.5), (hx - r * 0.8, hy - ry * 1.15),
                 (hx - r * 0.1, hy - ry * 1.5), (hx + r * 0.7, hy - ry * 1.62), (hx + r * 1.32, hy - ry * 1.42),
                 (hx + r * 1.42, hy - ry * 1.06), (hx + r * 1.12, hy - ry * 0.86), (hx + r * 0.9, hy - ry * 0.55),
                 (hx + r * 0.4, hy - ry * 0.55), (hx - r * 0.25, hy - ry * 0.4), (hx - r * 0.45, hy + ry * 0.0),
                 (hx - r * 0.62, hy + ry * 0.42)], 2)
    c.ink(pomp, hair, lw=3.0, shade=0.5, sw=r * 0.45, scol=hair_sh, hi=0.55, hw=r * 0.25, hcol=hair_hi, rim=0.2,
          rcol=(255, 250, 220))
    hair_strands(c, [[(hx - r * 0.7, hy - ry * 0.9), (hx + r * 0.2, hy - ry * 1.3), (hx + r * 1.1, hy - ry * 1.3)],
                     [(hx - r * 0.5, hy - ry * 0.5), (hx + r * 0.3, hy - ry * 0.9), (hx + r * 1.0, hy - ry * 0.95)],
                     [(hx + r * 1.3, hy - ry * 1.1), (hx + r * 1.15, hy - ry * 0.95)]], hair_sh, w=2.0)
    c.ink(blob([(hx - r * 0.42, hy + ry * 0.1), (hx - r * 0.25, hy + ry * 0.1), (hx - r * 0.25, hy + ry * 0.55),
                (hx - r * 0.42, hy + ry * 0.6)], 1), hair_sh, lw=2.0, shade=0.2)   # sideburn
    curl = blob([(hx + r * 1.0, hy - ry * 1.0), (hx + r * 1.42, hy - ry * 1.08), (hx + r * 1.5, hy - ry * 0.78),
                 (hx + r * 1.24, hy - ry * 0.62), (hx + r * 1.08, hy - ry * 0.8)], 2)
    c.ink(curl, hair, lw=2.6, shade=0.45, sw=r * 0.15, scol=hair_sh, hi=0.5, hcol=hair_hi)
    sparkle4(c, hx + r * 0.9, hy - ry * 1.5, r * 0.18)
    # near arm: the giant grape soda
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=9.0, w1=8.2, cuff=7.2), suit, lw=3.0, shade=0.5, sw=10, scol=suit_sh, hi=0.4)
    wx, wy = b.P(*b.wrist_n)
    cup = Sh([[(wx - 8, wy - 52), (wx + 38, wy - 52), (wx + 32, wy + 30), (wx - 2, wy + 30)]])
    c.ink(cup, (130, 50, 170), lw=2.8, shade=0.5, sw=10, hi=0.4)
    c.ink(rect(wx - 2, wy - 30, wx + 34, wy - 4), (250, 236, 120), lw=1.8, shade=0.2, clip=cup)
    c.label(wx + 16, wy - 17, "XXL", 10, (130, 40, 140), mirror=True)
    c.ink(ell(wx + 15, wy - 53, 26, 6), (240, 236, 246), lw=2.2, shade=0.3)
    c.stroke([(wx + 20, wy - 54), (wx + 26, wy - 96), (wx + 38, wy - 102)], 4.2, INK)
    c.stroke([(wx + 20, wy - 54), (wx + 26, wy - 96), (wx + 38, wy - 102)], 2.4, (255, 90, 150))
    c.ink(ell(wx + 4, wy + 34, 4, 6), (160, 70, 200), lw=1.2)   # drip
    b.hand(True, "hold", size=1.0, d=(1.0, -0.2))
    return finish_sprite(c, name, flip=True)


def paint_gloria_puff(height=374, name="hs_gloria_puff.png"):
    """Gloria Puff: hair, makeup, wardrobe. Platinum beehive, lavender smock full of brushes, giant powder puff."""
    W, Hc = 420, 700
    skin = (255, 214, 190)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=91)
    b = Body(c, 190, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=1.04, hips=1.22, limbs=0.92, head=1.06, legs=0.94, neck=0.9, chest=1.6,
                        belly=0.8, hand=0.95, foot=0.9),
             pose=dict(arm_n=48, fore_n=52, arm_f=-22, fore_f=44, leg_n=3, shin_n=0, leg_f=-6, shin_f=3, lean=2,
                       head_dx=0.6, head_dy=-0.5), seed=9)
    smock, smock_sh = (190, 150, 236), (120, 80, 180)
    hair, hair_sh, hair_hi = (252, 238, 186), (206, 180, 150), (255, 252, 230)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm: hand on the hip
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, 0.55, 8.4, 7.6), shade_col(smock, 0.82), lw=2.8, shade=0.4)
    # legs: striped tights + pink heels
    def heels(bb, near):
        bb.shoe(near, (255, 80, 160) if near else (210, 60, 130), kind="heel", heel_col=(200, 30, 100), length=0.92)
    legs(b, (60, 36, 80), w=(7.6, 5.0, 3.8), shoe=heels, skin=True)
    for near in (True, False):
        an = b.ankle_n if near else b.ankle_f
        kn = b.knee_n if near else b.knee_f
        for t in np.linspace(0.15, 0.9, 6):
            x_, y_ = an[0] + (kn[0] - an[0]) * t, an[1] + (kn[1] - an[1]) * t
            c.stroke(b.Ps([(x_ - 2.2, y_), (x_ + 2.2, y_ + 0.4)]), 2.6, (230, 90, 170), taper=(0, 0), opacity=0.8)
    # smock: knee-length A-line over a big chest
    sk = skirt(b, smock, b.hip_y - 20, flare=3.0, waist=b.hip_y + 8, scol=smock_sh)
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.4, hem=b.hip_y - 1, flare=1.6, neck_open=1.1)])
    c.ink(torso, smock, lw=3.0, shade=0.55, sw=18, scol=smock_sh, hi=0.35, rim=0.2, rcol=(230, 210, 255))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.4, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 1.0, sy - 4.0)])]), skin, lw=2.0, shade=0.4)
    # front pocket stuffed with brushes and combs
    pk = Sh([b.Ps([(-3.5, b.hip_y + 4), (5.8, b.hip_y + 4), (6.2, b.hip_y - 9), (-3.0, b.hip_y - 9)])])
    rng = random.Random(3)
    for i in range(6):
        x0_ = -2.6 + i * 1.5
        col = [(250, 200, 70), (40, 40, 50), (240, 90, 140), (60, 200, 200), (250, 250, 240), (200, 60, 90)][i]
        top = b.P(x0_ + rng.uniform(-0.4, 0.4), b.hip_y + 9 + rng.uniform(0, 3))
        bot = b.P(x0_, b.hip_y)
        c.stroke([bot, top], 3.2, INK)
        c.stroke([bot, top], 1.8, col)
        c.ink(ell(top[0], top[1] - 4, 4, 6), rng.choice([(250, 230, 200), (60, 40, 40), (255, 160, 200)]), lw=1.4, shade=0.3)
    c.ink(pk, shade_col(smock, 0.88), lw=2.6, shade=0.3, hi=0.3)
    c.stroke(b.Ps([(-3.3, b.hip_y + 2.6), (6.0, b.hip_y + 2.6)]), 1.4, (255, 255, 255), taper=(0, 0), opacity=0.5)
    # tape measure round the neck
    c.stroke([b.P(sx - 2.2, sy + 1.4), b.P(sx - 1.6, sy - 14), b.P(sx - 1.8, sy - 22)], 4.4, INK, smooth=1)
    c.stroke([b.P(sx - 2.2, sy + 1.4), b.P(sx - 1.6, sy - 14), b.P(sx - 1.8, sy - 22)], 2.8, (250, 220, 80), smooth=1)
    c.stroke([b.P(sx + 3.6, sy + 1.0), b.P(sx + 4.6, sy - 12), b.P(sx + 4.4, sy - 18)], 4.4, INK, smooth=1)
    c.stroke([b.P(sx + 3.6, sy + 1.0), b.P(sx + 4.6, sy - 12), b.P(sx + 4.4, sy - 18)], 2.8, (250, 220, 80), smooth=1)
    folds(c, [b.Ps([(-4, b.hip_y - 6), (-5, b.hip_y - 16)]), b.Ps([(4, b.hip_y - 10), (5.6, b.hip_y - 18)])], smock_sh, 1.6, 0.6)
    # head
    head = Sh([b.head_pts(jaw=1.0, chin=0.92, cheek=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.44, r * 0.32, (255, 90, 140), 0.55)
    for (ex, ey), k in ((fa["eye_n"], 1.0), (fa["eye_f"], 0.65)):
        c.soft(ell(ex, ey - ry * 0.24, r * 0.38 * k, ry * 0.22), (40, 190, 196), 0.6, 3)
    b.eyes(iris=(60, 170, 120), look=(0.4, 0.05), lid=0.3, size=1.0, lashes=1, tilt=0.06)
    b.brows(col=(160, 120, 90), lift_n=0.3, lift_f=0.26, tilt_n=-0.05, tilt_f=-0.1, w=r * 0.09, arch=0.12)
    b.nose("button", 0.95)
    b.mouth("smile", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.6, r * 0.36, lip=(230, 30, 70))
    mx, my = fa["mouth"]
    c.ink(ell(mx + r * 0.5, my - ry * 0.22, 1.8, 1.8), INK, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)   # beauty mark
    glasses(b, (255, 90, 170), False, 1.0, lw=b.r * 0.1)
    for (ex, ey) in (fa["eye_n"],):   # cat-eye flick on the frames
        c.stroke([(ex + r * 0.4, ey - r * 0.3), (ex + r * 0.62, ey - r * 0.52)], r * 0.1, (255, 90, 170))
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.1, ey_ + r * 0.66, r * 0.26, r * 0.3), (0, 0, 0, 0), lw=3.6, oc=(60, 210, 210), line_only=True)
    # the beehive: tall, platinum, with a pink bow
    hive = blob([(hx - r * 1.1, hy + ry * 0.45), (hx - r * 1.2, hy - ry * 0.3), (hx - r * 1.25, hy - ry * 1.2),
                 (hx - r * 1.0, hy - ry * 2.1), (hx - r * 0.3, hy - ry * 2.6), (hx + r * 0.5, hy - ry * 2.55),
                 (hx + r * 1.05, hy - ry * 2.0), (hx + r * 1.2, hy - ry * 1.1), (hx + r * 1.12, hy - ry * 0.4),
                 (hx + r * 0.7, hy - ry * 0.62), (hx + r * 0.1, hy - ry * 0.58), (hx - r * 0.35, hy - ry * 0.3),
                 (hx - r * 0.5, hy + ry * 0.2)], 2)
    c.ink(hive, hair, lw=3.0, shade=0.5, sw=r * 0.5, scol=hair_sh, hi=0.55, hw=r * 0.3, hcol=hair_hi, rim=0.2,
          rcol=(255, 220, 250))
    hair_strands(c, [[(hx - r * 0.9, hy - ry * 0.6), (hx - r * 0.95, hy - ry * 1.6), (hx - r * 0.4, hy - ry * 2.3)],
                     [(hx - r * 0.4, hy - ry * 0.7), (hx - r * 0.2, hy - ry * 1.7), (hx + r * 0.4, hy - ry * 2.2)],
                     [(hx + r * 0.3, hy - ry * 0.75), (hx + r * 0.7, hy - ry * 1.4), (hx + r * 0.8, hy - ry * 2.0)]],
                 hair_sh, w=2.2)
    bx_, by_ = hx - r * 0.2, hy - ry * 0.95
    for sgn in (-1, 1):
        c.ink(Sh([[(bx_, by_), (bx_ + sgn * r * 0.6, by_ - r * 0.32), (bx_ + sgn * r * 0.6, by_ + r * 0.32)]]), (255, 80, 150), lw=2.4,
              shade=0.4, hi=0.4)
    c.ink(ell(bx_, by_, r * 0.14, r * 0.14), (255, 120, 180), lw=2.0)
    c.stroke([(hx + r * 0.9, hy - ry * 1.6), (hx + r * 1.3, hy - ry * 2.0)], 2.6, (200, 60, 90))   # a pencil stuck in it
    # near arm: the powder puff, raised
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, 0.6, 8.8, 8.0), smock, lw=3.0, shade=0.5, sw=10, scol=smock_sh, hi=0.35)
    wx, wy = b.P(*b.wrist_n)
    px_, py_ = wx + 22, wy - 36
    for k in range(10):
        a = math.radians(k * 36)
        c.ink(ell(px_ + math.cos(a) * 26, py_ + math.sin(a) * 22, 14, 12), (255, 190, 214), lw=0, shade=0, hi=0)
    c.ink(ell(px_, py_, 36, 31), (255, 190, 214), lw=2.8, shade=0.45, sw=10, hi=0.5, hw=6, tex=0.25)
    c.ink(rrect(px_ - 14, py_ - 4, px_ + 14, py_ + 6, 4), (255, 120, 170), lw=2.0)
    for k in range(4):
        c.soft(ell(px_ + 26 + k * 7, py_ - 28 - k * 7, 8 + k * 2, 7 + k * 2), (255, 250, 245), 0.35, 4)
    b.hand(True, "hold", size=0.95, d=(0.6, -1.0))
    return finish_sprite(c, name, flip=True)


def paint_norma_fade(height=365, name="hs_norma_fade.png"):
    """Norma Fade: the director. Headset, chunky glasses, mustard cardigan with a pencil in every pocket,
    stopwatch on a lanyard, clipboard."""
    W, Hc = 380, 620
    skin = (152, 98, 68)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=101)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.96, waist=1.02, hips=1.08, limbs=0.96, head=1.02, legs=0.98, neck=0.95, chest=0.7,
                        hand=0.95, foot=0.95),
             pose=dict(arm_n=8, fore_n=104, arm_f=-6, fore_f=12, leg_n=-3, shin_n=1, leg_f=5, shin_f=-1, lean=5,
                       head_dx=1.0, head_dy=-0.6), seed=10)
    cardi, cardi_sh = (226, 168, 48), (160, 100, 40)
    tee = (246, 244, 236)
    hair, hair_sh = (40, 26, 30), (20, 12, 16)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (cardigan sleeve to the wrist)
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.6, w1=7.8, cuff=7.0), shade_col(cardi, 0.82), lw=2.8, shade=0.4)
    # legs: dark jeans + chunky sneakers
    def sneaks(bb, near):
        bb.shoe(near, (90, 200, 200) if near else (60, 160, 170), (246, 240, 230), "sneaker", length=1.0)
    legs(b, (52, 64, 112), w=(8.8, 6.0, 5.6), scol=(30, 34, 80), shoe=sneaks, cuffs=(70, 86, 140))
    hips = Sh([b.Ps([(-5.4, b.hip_y + 4.5), (5.0, b.hip_y + 4.5), (5.4, b.hip_y - 3), (-5.6, b.hip_y - 3)])])
    c.ink(hips, (52, 64, 112), lw=3.0, shade=0.45, scol=(30, 34, 80))
    # neck + white tee + long open cardigan
    c.ink(b.neck_shape(0.95), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.4, hem=b.hip_y - 6, flare=1.4, neck_open=1.1)])
    c.ink(torso, cardi, lw=3.0, shade=0.55, sw=18, scol=cardi_sh, hi=0.35, tex=0.18)
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.6, sy + 1.6), (sx + 3.4, sy + 1.2), (sx + 4.4, b.hip_y + 3), (sx + 0.2, b.hip_y + 3)])]), tee,
          lw=2.2, shade=0.35)
    c.ink(Sh([b.Ps([(sx - 1.2, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 1.0, sy - 2.6)])]), skin, lw=2.0, shade=0.4)
    for xx in np.linspace(-4, 5, 7):   # knit ribs
        c.stroke(b.Ps([(xx, b.hip_y - 2), (xx + 0.2, b.hip_y - 5.5)]), 1.2, cardi_sh, opacity=0.6, taper=(0, 0))
    # pockets with a pencil in every one
    for (px, py) in ((-2.6, b.hip_y + 2), (3.8, b.hip_y + 2), (4.2, sy - 9)):
        pk = Sh([b.Ps([(px - 2.2, py + 1.0), (px + 2.2, py + 1.0), (px + 2.0, py - 3.6), (px - 2.0, py - 3.6)])])
        for j, col in enumerate([(250, 210, 60), (220, 60, 80)]):
            a_ = b.P(px - 0.8 + j * 1.3, py)
            t_ = b.P(px - 1.2 + j * 1.8, py + 4.6 - j * 0.8)
            c.stroke([a_, t_], 3.8, INK)
            c.stroke([a_, t_], 2.2, col)
            c.ink(ell(t_[0], t_[1], 2, 2), (250, 170, 170), lw=1.0)
        c.ink(pk, hi_col(cardi, 0.08), lw=2.2, shade=0.3, hi=0.3)
    # lanyard + stopwatch
    c.stroke([b.P(sx - 1.4, sy + 1.4), b.P(sx - 0.4, sy - 10), b.P(sx + 1.2, sy - 13)], 2.2, (230, 50, 80), smooth=1)
    c.stroke([b.P(sx + 3.2, sy + 1.0), b.P(sx + 2.6, sy - 10), b.P(sx + 1.2, sy - 13)], 2.2, (230, 50, 80), smooth=1)
    wx_, wy_ = b.P(sx + 1.2, sy - 15.5)
    c.ink(ell(wx_, wy_, 11, 11), (210, 214, 226), lw=2.4, shade=0.4, hi=0.6, hw=3)
    c.ink(ell(wx_, wy_, 7, 7), (250, 250, 246), lw=1.4)
    c.stroke([(wx_, wy_), (wx_ + 4, wy_ - 4)], 1.6, (220, 40, 60))
    c.ink(rect(wx_ - 3, wy_ - 15, wx_ + 3, wy_ - 10), (210, 214, 226), lw=1.4)
    # head
    head = Sh([b.head_pts(jaw=1.0, chin=0.96, cheek=1.0)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.35, rim=0.15, rcol=(255, 160, 130))
    fa = b.face_anchor()
    b.eyes(iris=(70, 40, 30), look=(0.5, 0.05), lid=0.38, size=0.95, tilt=-0.1)
    b.brows(col=hair_sh, lift_n=0.1, lift_f=0.06, tilt_n=-0.7, tilt_f=-0.6, w=r * 0.14)
    b.nose("round", 1.0)
    b.mouth("flat", fa["mouth"][0] + r * 0.02, fa["mouth"][1] + ry * 0.02, r * 0.46, r * 0.24)
    glasses(b, (40, 180, 176), False, 1.06, lw=b.r * 0.11)
    b.ear(0.95)
    # short curls
    curls = [(hx - r * 1.05, hy + ry * 0.2), (hx - r * 1.1, hy - ry * 0.4), (hx - r * 0.8, hy - ry * 0.9),
             (hx - r * 0.2, hy - ry * 1.1), (hx + r * 0.45, hy - ry * 1.05), (hx + r * 0.95, hy - ry * 0.7)]
    c.ink(blob([(hx - r * 1.12, hy + ry * 0.4), (hx - r * 1.2, hy - ry * 0.6), (hx - r * 0.3, hy - ry * 1.15), (hx + r * 0.6, hy - ry * 1.1),
                (hx + r * 1.08, hy - ry * 0.55), (hx + r * 0.6, hy - ry * 0.55), (hx - r * 0.2, hy - ry * 0.5),
                (hx - r * 0.45, hy + ry * 0.05), (hx - r * 0.7, hy + ry * 0.45)], 2), hair, lw=3.0, shade=0.4, scol=hair_sh, hi=0.3,
          hcol=(110, 80, 90))
    for (x_, y_) in curls:
        c.ink(ell(x_, y_, r * 0.32, r * 0.3), hair, lw=2.2, shade=0.4, scol=hair_sh, hi=0.4, hcol=(120, 90, 100))
    # headset: band over the top, ear cup, boom mic to the mouth
    ex_, ey_ = fa["ear"]
    c.stroke([(ex_ - r * 0.05, ey_ - r * 0.2), (hx - r * 0.5, hy - ry * 1.1), (hx + r * 0.4, hy - ry * 1.18), (hx + r * 0.95, hy - ry * 0.6)],
             r * 0.16, INK, smooth=2)
    c.stroke([(ex_ - r * 0.05, ey_ - r * 0.2), (hx - r * 0.5, hy - ry * 1.1), (hx + r * 0.4, hy - ry * 1.18), (hx + r * 0.95, hy - ry * 0.6)],
             r * 0.09, (80, 80, 96), smooth=2)
    c.ink(rrect(ex_ - r * 0.36, ey_ - r * 0.36, ex_ + r * 0.24, ey_ + r * 0.4, 8), (50, 50, 64), lw=2.6, shade=0.4, hi=0.4)
    mx, my = fa["mouth"]
    c.stroke([(ex_ + r * 0.1, ey_ + r * 0.25), (mx - r * 0.4, my + ry * 0.12), (mx - r * 0.02, my + ry * 0.05)], r * 0.1, INK, smooth=2)
    c.stroke([(ex_ + r * 0.1, ey_ + r * 0.25), (mx - r * 0.4, my + ry * 0.12), (mx - r * 0.02, my + ry * 0.05)], r * 0.05, (90, 90, 106),
             smooth=2)
    c.ink(ell(mx - r * 0.02, my + ry * 0.05, r * 0.1, r * 0.08), (30, 30, 40), lw=1.6)
    # near arm: clipboard against the chest
    wx, wy = b.P(*b.wrist_n)
    cb = Sh([rot_pts([(wx - 10, wy - 70), (wx + 54, wy - 70), (wx + 54, wy + 14), (wx - 10, wy + 14)], 8, wx, wy)])
    c.ink(cb, (170, 116, 70), lw=2.8, shade=0.4, hi=0.3)
    pp = Sh([rot_pts([(wx - 4, wy - 62), (wx + 48, wy - 62), (wx + 48, wy + 8), (wx - 4, wy + 8)], 8, wx, wy)])
    c.ink(pp, (250, 248, 240), lw=1.8, shade=0.2)
    for k in range(5):
        c.stroke(rot_pts([(wx + 4, wy - 48 + k * 11), (wx + 40, wy - 48 + k * 11)], 8, wx, wy), 1.4, (120, 120, 160), taper=(0, 0))
    c.ink(Sh([rot_pts([(wx + 10, wy - 76), (wx + 34, wy - 76), (wx + 34, wy - 64), (wx + 10, wy - 64)], 8, wx, wy)]),
          (200, 200, 214), lw=2.0, shade=0.3, hi=0.5)
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=9.0, w1=8.2, cuff=7.4), cardi, lw=3.0, shade=0.5, sw=10, scol=cardi_sh, hi=0.35, tex=0.18)
    b.hand(True, "hold", size=0.95, d=(1.0, -0.4))
    return finish_sprite(c, name, flip=True)


# =========================================================================== prop sprites (finale only)
PROP_FEET = {}   # sprite -> feet (screen px) where it was painted; LAYOUT uses the same numbers


def prop_canvas(back, seed):
    """Full-screen canvas + the room's projection, so a prop sprite is painted in true perspective at the
    spot where it stands (finish_sprite then crops it, keeping the bottom centre as the feet)."""
    c = Canvas2(W_BG, H_BG, light=(0.42, -0.9), lw=3.0, seed=seed)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), back, fc=1000)
    return c, R


def finish_prop(c, name):
    a = np.asarray(c.result().getchannel("A"))
    ys, xs = np.nonzero(a > 8)
    y1 = ys.max() + 1
    band = ys > y1 - max(3, (y1 - ys.min()) * 0.03)
    PROP_FEET[name] = (round((xs[band].min() + xs[band].max()) / 2), int(y1))
    sprite_grade(c, 0.92)
    out = finish_sprite(c, name + ".png")
    print("   feet", PROP_FEET[name])
    return out


def paint_reserved_sign(name="hs_reserved_sign"):
    """Little brass stand with a card: RESERVED: C. STUDWELL. ALL NIGHT."""
    c, R = prop_canvas(GREEN_BACK, 111)
    X, Z = 870, 176
    P = R.pt
    k = R.k(Z)
    bx, by = P(X, 0, Z)
    c.soft(ell(bx, by - 2, 30 * k, 7 * k), (30, 8, 40), 0.4, 3)
    c.ink(ell(bx, by - 4, 24 * k, 7 * k), (220, 170, 60), lw=2.6, shade=0.5, hi=0.6, hw=3)
    top = P(X, 78, Z)
    c.ink(rect(bx - 3.5 * k, top[1], bx + 3.5 * k, by - 6), (230, 186, 70), lw=2.4, shade=0.5, sw=3, hi=0.6, hw=2)
    cx, cy = P(X, 104, Z)
    w, h = 64 * k, 44 * k
    c.ink(rrect(cx - w / 2 - 4, cy - h / 2 - 4, cx + w / 2 + 4, cy + h / 2 + 4, 4), (230, 186, 70), lw=2.6, shade=0.5, hi=0.6)
    c.ink(rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), (252, 248, 236), lw=1.8, shade=0.15)
    c.text(cx, cy - h * 0.24, "RESERVED", int(12 * k), (200, 30, 50))
    c.text(cx, cy + h * 0.06, "C. STUDWELL", int(8 * k), (40, 30, 50))
    c.text(cx, cy + h * 0.3, "ALL NIGHT", int(7 * k), (40, 30, 50), "Bold")
    return finish_prop(c, name)


def _deck(name, loaded):
    """The playback deck on its rolling cart: a tape deck wired to a transmitter with a bendy antenna."""
    c, R = prop_canvas(BOOTH_BACK, 121)
    P = R.pt
    X0, X1, Z0, Z1 = 906, 1042, 140, 194
    R.contact(X0, X1, Z0, Z1, 0.45, grow=6, blur_px=6)
    # cart: legs, lower shelf, top
    for X, Z in ((X0 + 6, Z1 - 4), (X1 - 6, Z1 - 4), (X0 + 6, Z0 + 4), (X1 - 6, Z0 + 4)):
        a, b_ = P(X, 10, Z), P(X, 80, Z)
        c.stroke([a, b_], 7, INK, taper=(0, 0), smooth=0)
        c.stroke([a, b_], 3.6, (170, 170, 186), taper=(0, 0), smooth=0)
        wx, wy = P(X, 5, Z)
        c.ink(ell(wx, wy, 7, 6), (36, 30, 44), lw=1.8, shade=0.3)
    R.ink_box(X0, X1, 22, 30, Z0, Z1, (70, 66, 96), top=(100, 96, 126), seed=1)
    for i in range(3):   # spare tapes on the bottom shelf
        g = R.box(X0 + 12 + i * 38, X0 + 44 + i * 38, 30, 42, Z0 + 10, Z1 - 12)
        c.ink(Sh([g["front"]]), [(240, 80, 150), (60, 200, 210), (250, 210, 70)][i], lw=1.8, shade=0.3)
        if "top" in g:
            c.ink(Sh([g["top"]]), (60, 56, 70), lw=1.6, shade=0.1)
    R.ink_box(X0 - 4, X1 + 4, 80, 90, Z0 - 2, Z1 + 2, (90, 86, 116), top=(130, 126, 156), seed=2)
    # tape deck (left) and transmitter (right)
    d = R.ink_box(X0 + 4, X0 + 84, 90, 134, Z0 + 6, Z1 - 6, (40, 36, 54), top=(70, 66, 86), seed=3)
    fr = d["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    win = rect(x0 + 6, y0 + 6, x0 + (x1 - x0) * 0.66, y1 - 10)
    c.ink(win, (20, 16, 28), lw=2.0, shade=0.1, hi=0)
    if loaded:
        tx0, ty0, tx1, ty1 = x0 + 10, y0 + 10, x0 + (x1 - x0) * 0.66 - 4, y1 - 14
        c.ink(rrect(tx0, ty0, tx1, ty1, 3), (250, 120, 190), lw=1.8, shade=0.2, hi=0.4)
        for kk in (0.32, 0.68):
            c.ink(ell(tx0 + (tx1 - tx0) * kk, (ty0 + ty1) / 2, 5, 5), (250, 250, 246), lw=1.4)
        rng = random.Random(5)
        for _ in range(14):
            c.ink(ell(rng.uniform(tx0 + 2, tx1 - 2), rng.uniform(ty0 + 2, ty1 - 2), 1.3, 1.3), (255, 250, 200), lw=0, shade=0, hi=0)
        c.stroke([(tx0 + 3, ty1 - 3), (tx1 - 6, ty0 + 4)], 1.4, (255, 255, 255), opacity=0.7)
    for i in range(3):
        bx_ = x0 + (x1 - x0) * (0.74 + (i % 2) * 0.12)
        by_ = y0 + 10 + (i // 2) * 14
        c.ink(rect(bx_ - 4, by_ - 4, bx_ + 4, by_ + 4), (200, 200, 214), lw=1.2)
    t = R.ink_box(X0 + 90, X1 - 4, 90, 128, Z0 + 6, Z1 - 6, (40, 36, 54), top=(70, 66, 86), seed=4)
    fr = t["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    for kk in range(5):
        c.stroke([(x0 + 8, y0 + 8 + kk * 5), (x1 - 22, y0 + 8 + kk * 5)], 1.4, (90, 86, 110), taper=(0, 0))
    lit = loaded
    c.ink(ell(x1 - 12, (y0 + y1) / 2, 6, 6), (255, 50, 60) if lit else (90, 50, 60), lw=1.6, hi=0.5)
    if lit:
        c.glow2(x1 - 12, (y0 + y1) / 2, 30, (255, 40, 60), 0.7)
    cable_pts = [P(X0 + 84, 104, Z1 - 8), P(X0 + 88, 96, Z1), P(X0 + 92, 104, Z1 - 8)]
    c.stroke(cable_pts, 2.4, INK, smooth=2)
    # bendy antenna
    ax_, ay_ = P(X1 - 20, 128, Z0 + 20)
    ant = [(ax_, ay_), (ax_ + 4, ay_ - 30), (ax_ - 8, ay_ - 56), (ax_ + 6, ay_ - 82)]
    c.stroke(ant, 4.4, INK, smooth=2)
    c.stroke(ant, 2.2, (200, 200, 214), smooth=2)
    c.ink(ell(ax_ + 6, ay_ - 84, 5, 5), (230, 230, 240), lw=1.6, hi=0.5)
    # the sticky label on top: CH. CHET / DO NOT TOUCH
    lx, ly = P((X0 + X1) / 2, 134, Z0 + 4)
    c.ink(Sh([rot_pts([(lx - 50, ly - 26), (lx + 50, ly - 26), (lx + 50, ly), (lx - 50, ly)], -3, lx, ly)]), (255, 236, 110), lw=1.8,
          shade=0.15)
    c.text(lx, ly - 17, "CH. CHET", 11, (200, 30, 50), angle=3)
    c.text(lx, ly - 6, "DO NOT TOUCH", 7, (60, 40, 60), "Bold", angle=3)
    return finish_prop(c, name)


def paint_playback_deck(name="hs_playback_deck"):
    return _deck(name, True)


def paint_empty_deck(name="hs_empty_deck"):
    return _deck(name, False)


# =========================================================================== layouts (px) -> finale.json
LAYOUT["tv_studio"] = dict(
        walk_px=[(70, Y_TOP), (1850, Y_TOP), (1900, 880), (1860, Y_BOT), (60, Y_BOT), (20, 880)],
        hotspots={
            ("Stage door", 0): dict(box=(8, 380, 140, 780), stand=(200, 880)),
            ("Studio audience", 0): dict(box=(270, 400, 828, 735), stand=(560, 800)),
            ("Applause sign", 0): dict(box=(400, 282, 660, 362), stand=(530, 800)),
            ("Studio camera", 0): dict(box=(830, 405, 1050, 735), stand=(940, 800)),
            ("Control booth window", 0): dict(box=(1040, 228, 1220, 410), stand=(1130, 800)),
            ("Green room door", 0): dict(box=(1060, 412, 1200, 692), stand=(1130, 790)),
            ("Contestant mark", 0): dict(box=(865, 875, 995, 950), stand=(930, 912)),
            ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1210, NPC_FEET_Y), stand=(1060, 935)),
            ("Chet Studwell", 0): dict(npc="hs_chet_studwell", feet=(1500, NPC_FEET_Y), stand=(1360, 935)),
            ("Sound board", 0): dict(box=(1630, 540, 1840, 758), stand=(1740, 800)),
        },
        entries={"from_campus": (250, 900), "from_green_room": (1130, 810)})

LAYOUT["tv_green_room"] = dict(
        walk_px=[(120, Y_TOP), (1800, Y_TOP), (1880, 880), (1850, Y_BOT), (70, Y_BOT), (30, 880)],
        hotspots={
            ("Studio door", 0): dict(box=(105, 300, 280, 762), stand=(300, 870)),
            ("Craft services", 0): dict(box=(240, 535, 560, 735), stand=(400, 800)),
            ("Wardrobe rack", 0): dict(box=(655, 460, 850, 720), stand=(750, 800)),
            ("Makeup chair", 0): dict(box=(890, 270, 1160, 740), stand=(1030, 800)),
            ("Reserved sign", 0): dict(sprite="hs_reserved_sign", feet=None, stand=(1215, 800)),
            ("Gloria Puff", 0): dict(npc="hs_gloria_puff", feet=(1450, NPC_FEET_Y), stand=(1290, 935)),
            ("Booth stairs", 0): dict(box=(1640, 300, 1915, 762), stand=(1690, 850)),
        },
        entries={"from_studio": (320, 890), "from_booth": (1660, 870)})

LAYOUT["tv_control_booth"] = dict(
        walk_px=[(110, Y_TOP), (1800, Y_TOP), (1880, 880), (1850, Y_BOT), (70, Y_BOT), (30, 880)],
        hotspots={
            ("Stairs down", 0): dict(box=(75, 300, 270, 772), stand=(290, 870)),
            ("Monitor wall", 0): dict(box=(310, 240, 785, 580), stand=(550, 800)),
            ("Coffee maker", 0): dict(box=(835, 440, 935, 595), stand=(885, 800)),
            ("Norma Fade", 0): dict(npc="hs_norma_fade", feet=(1110, NPC_FEET_Y), stand=(950, 935)),
            ("Playback deck", 0): dict(sprite="hs_playback_deck", feet=None, stand=(1347, 800)),
            ("Empty deck", 0): dict(sprite="hs_empty_deck", feet=None, stand=(1347, 800)),
            ("Talkback mic", 0): dict(box=(1500, 470, 1830, 768), stand=(1660, 810)),
        },
        entries={"from_green_room": (320, 890)})

# where the prop sprites were painted (see finish_prop); must match the painters above
PROP_AT = {"hs_reserved_sign": (1214, 754), "hs_playback_deck": (1347, 761), "hs_empty_deck": (1347, 761)}
for _L in LAYOUT.values():
    for _h in _L["hotspots"].values():
        if _h.get("sprite") in PROP_AT:
            _h["feet"] = PROP_AT[_h["sprite"]]

NPC_REL = {"hs_chet_studwell": 1.0, "hs_gloria_puff": 0.9, "hs_norma_fade": 0.88}
NPC_FN = {"hs_chet_studwell": paint_chet_studwell, "hs_gloria_puff": paint_gloria_puff, "hs_norma_fade": paint_norma_fade}


def npc_height(npc):
    for L in LAYOUT.values():
        for h in L["hotspots"].values():
            if h.get("npc") == npc:
                return round(DEX_H * depth_scale(h["feet"][1], Y_TOP, Y_BOT) * NPC_REL[npc])
    raise KeyError(npc)


def _sprite_size(name):
    return Image.open(os.path.join(OUT_DIR, name + ".png")).size


def write_layout(path=WORLD):
    """Write walkable, hotspot feet / size / standAt and entry positions into finale.json (nothing else)."""
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
                bw = spec.get("w", 1.9) if "npc" in spec else round(w / 100, 2)
                h["feet"] = list(px_to_world(*spec["feet"]))
                h["size"] = [bw, round(hh / 100, 2)]
            else:
                x0, y0, x1, y1 = spec["box"]
                h["feet"] = list(px_to_world((x0 + x1) / 2, y1))
                h["size"] = [round((x1 - x0) / 100, 2), round((y1 - y0) / 100, 2)]
            h["standAt"] = list(px_to_world(*spec["stand"]))
    # keep the file's one-line-per-item style: rewrite only the rooms block's changed fields in place
    text = open(path).read()
    for room in data["rooms"]:
        text = _patch_room(text, room)
    with open(path, "w") as f:
        f.write(text)
    print("updated", os.path.relpath(path, ROOT))


def _fmt(v):
    return json.dumps(v, separators=(", ", ": "))


def _patch_room(text, room):
    """Patch one room's layout fields into the hand-formatted JSON text."""
    start = text.index('"id": "%s"' % room["id"])
    end = text.find('"id": "', start + 10)
    end = len(text) if end < 0 else end
    seg = text[start:end]
    # walkable: insert after "floor" if missing, else replace
    wl = '"walkable": %s' % _fmt(room["walkable"])
    if '"walkable"' in seg:
        seg = re.sub(r'"walkable": \[[^\]]*\]', wl, seg, count=1)
    else:
        seg = re.sub(r'("floor": \[[^\]]*\],)', r'\1\n      ' + wl.replace('\\', '\\\\') + ',', seg, count=1)
    for e in room.get("entries", []):
        seg = re.sub(r'(\{"name": "%s", "pos": )\[[^\]]*\]' % re.escape(e["name"]), r'\g<1>' + _fmt(e["pos"]), seg, count=1)
    pos = 0
    for h in room["hotspots"]:
        i = seg.index('{"name": "%s"' % h["name"], pos)
        j = seg.index('"look"', i)
        head = seg[i:j]
        for key in ("feet", "size", "standAt"):
            head = re.sub(r'("%s": )\[[^\]]*\]' % key, r'\g<1>' + _fmt(h[key]), head, count=1)
        seg = seg[:i] + head + seg[j:]
        pos = i + len(head)
    return text[:start] + seg + text[end:]


# =========================================================================== composites
COMPOSITE_DIR = os.environ.get("BNO_COMPOSITES", os.path.join(ROOT, "..", "composites"))


def composite(room_id, out_dir=None, boxes=True, flags=()):
    """Background + sprites at their feet (unscaled, like the game) + Dex (depth-scaled) at the front stand
    points and at the back of the walkable area, with hotspot boxes, stand points and entries."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    room = [r for r in json.load(open(WORLD))["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))

    def shown(h):
        if h.get("showWhenFlag") and h["showWhenFlag"] not in flags:
            return False
        if h.get("hideWhenFlag") and h["hideWhenFlag"] in flags:
            return False
        return True
    items = []
    for h in room["hotspots"]:
        if not shown(h):
            continue
        slug = re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx))
    if boxes:
        stands = [world_to_px(*h["standAt"]) for h in room["hotspots"] if shown(h)]
        stands = sorted(stands, key=lambda p: -p[1])[:2] + [((wp[0][0] + wp[1][0]) / 2, yt)]
        for (sx, sy) in stands:
            k = 1.0 - 0.4 * (yb - sy) / max(1, yb - yt)
            items.append((sy, dex.resize((int(dex.width * k), int(dex.height * k)), Image.LANCZOS), sx))
    for fy, im, fx in sorted(items, key=lambda t: t[0]):
        bg.alpha_composite(im, (int(fx - im.width / 2), int(fy - im.height)))
    if boxes:
        ov = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.line(wp + [wp[0]], fill=(80, 255, 120, 220), width=3)
        for h in room["hotspots"]:
            fx, fy = world_to_px(*h["feet"])
            w, hh = h["size"][0] * 100, h["size"][1] * 100
            col = (255, 230, 60, 255) if shown(h) else (120, 200, 255, 255)
            d.rectangle([fx - w / 2, fy - hh, fx + w / 2, fy], outline=col, width=3)
            sx, sy = world_to_px(*h["standAt"])
            d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 80, 80, 255))
            d.text((fx - w / 2 + 4, fy - hh + 4), h["name"], fill=col)
        for e in room.get("entries", []):
            ex, ey = world_to_px(*e["pos"])
            d.rectangle([ex - 6, ey - 6, ex + 6, ey + 6], fill=(80, 160, 255, 255))
        bg.alpha_composite(ov)
    tag = ("_" + "_".join(flags) if flags else "") + ("" if boxes else "_clean")
    out = os.path.join(out_dir, "composite_%s%s.png" % (room_id, tag))
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


def contact_sheets(out_dir=None):
    out_dir = out_dir or COMPOSITE_DIR
    rooms = list(LAYOUT)
    for name, ims in (("final_bgs.jpg", [Image.open(os.path.join(OUT_DIR, "bg_%s.png" % r)).convert("RGB") for r in rooms]),
                      ("final_scenes.jpg", [Image.open(composite(r, out_dir, boxes=False)) for r in rooms])):
        w, h = 960, 540
        sheet = Image.new("RGB", (w, h * len(ims) + 8 * (len(ims) - 1)), (20, 10, 30))
        for i, im in enumerate(ims):
            sheet.paste(im.resize((w, h), Image.LANCZOS), (0, i * (h + 8)))
        sheet.save(os.path.join(out_dir, name), quality=88)
        print("wrote", os.path.join(out_dir, name))


ASSETS = {
    **{n: (lambda n=n: NPC_FN[n](height=npc_height(n))) for n in NPC_FN},
    "hs_reserved_sign": paint_reserved_sign, "hs_playback_deck": paint_playback_deck, "hs_empty_deck": paint_empty_deck,
    "bg_tv_studio": paint_tv_studio, "bg_tv_green_room": paint_tv_green_room, "bg_tv_control_booth": paint_tv_control_booth,
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
        composite("tv_control_booth", flags=("f_tape_swapped",)) if not [a for a in args if not a.startswith("--")] else None
        contact_sheets()
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
