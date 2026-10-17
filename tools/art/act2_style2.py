#!/usr/bin/env python3
"""
Big Night Out -- Act 2 (Greek Week) repainted in "style 2" (see Docs/ART_STYLE.md).

Paints the Act 2 backgrounds (Greek Row, the frat house, the Fuse Box bar, the sorority parlor, the frat
basement), the Act 2 cast (Tess Calloway, Chad Thunderclap, Dolly Spark, Mother Whitlock, Moose, Dunk),
Fernanda the inflatable flamingo, sleeping Moose, the bedsheet and the confiscated record with the
style-2 kit (tools/art/style2.py) and the shared Act 1 helpers (tools/art/act1_style2.py, imported,
not modified). Item icons are unchanged and still come from tools/art/act2.py.

NOTE: a plain run of tools/art/act2.py repaints the old versions of these files. Run this script after
it (or run act2.py only with explicit icon names) until act2.py learns to skip them.

Usage:  python3 tools/art/act2_style2.py              # paint everything
        python3 tools/art/act2_style2.py tess greek   # paint assets whose name contains these words
        python3 tools/art/act2_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into act2.json
        BNO_COMPOSITES=/some/dir python3 tools/art/act2_style2.py --composite [room ids]
"""
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style2 import *  # noqa: F401,F403,E402
import act1_style2 as A1  # noqa: E402
from act1_style2 import (DEX_H, BRICK, MORTAR, legs, soft_shade, glasses, hair_strands, clip_draw, skirt, folds,  # noqa: E402,F401
                         grunge_wall, two_tone_wall, skirting, window_flat, doorway_flat, exit_sign, bunting2, corkboard,
                         facade_windows, lamppost, tree_round, sprite_grade, crt_tv, couch, bookcase, panel_light, balloon)

Y_TOP, Y_BOT = 762, 975          # walkable band (px), same as Act 1
NPC_FEET_Y = 945                 # NPCs stand near the front, like Act 1
WORLD = os.path.join(ROOT, "Assets", "_Project", "World", "act2.json")
LAYOUT = {}


# =========================================================================== shared character bits
def toga_shape(b, hem, flare=2.0, slack=1.0, bare_far=True):
    """A bedsheet toga: over the near shoulder, under the far arm (bare far shoulder), to the knees."""
    bb = b.b
    sx, sy = b.lean_dx, b.shoulder_y
    bl = bb["belly"]
    top_far = [(sx + 3.4, sy - 2.6), (b.sh_f[0] + 1.0 + slack + bb["chest"] * 0.8, sy - 10.0)] if bare_far else \
        [(sx + 2.6, sy + 1.2), (b.sh_f[0] + 0.4 + slack, sy - 0.6), (b.sh_f[0] + 1.5 + slack + bb["chest"], sy - 5.0)]
    pts = [(b.sh_n[0] - 0.8 - slack, sy + 0.4), (sx - 1.0, sy + 1.8), (sx + 1.4, sy + 1.2)] + top_far + [
        (sx * 0.62 + 4.6 * bb["waist"] + slack + bl * 0.8, b.hip_y + 13),
        (sx * 0.45 + 4.8 * bb["waist"] + slack + bl, b.hip_y + 5),
        (5.4 * bb["hips"] + slack + flare + bl * 0.4, hem + 1.0),
        (2.0, hem - 1.2), (-1.5, hem + 0.6),
        (-5.8 * bb["hips"] - slack - flare, hem - 0.4),
        (sx * 0.4 - 5.4 * bb["hips"] - slack, b.hip_y + 5),
        (sx * 0.6 - 5.0 * bb["waist"] - slack - bl * 0.2, b.hip_y + 12),
        (b.sh_n[0] + 0.4 - slack, sy - 9.0), (b.sh_n[0] - 1.2 - slack, sy - 3.0)]
    return Sh([chaikin(b.Ps(pts), 1)])


def toga_folds(b, col, hem, n=4):
    """Diagonal drape folds from the near shoulder toward the far hip and down to the hem."""
    c = b.c
    sx, sy = b.lean_dx, b.shoulder_y
    fc = shade_col(col, 0.6)
    for k in range(n):
        t = k / max(1, n - 1)
        a = (b.sh_n[0] + 1.5 + t * 3.5, sy - 1 - t * 3)
        m = (sx + 1 + t * 3, b.hip_y + 14 - t * 6)
        e = (4.0 - t * 7.5, hem + 2 + t * 1.5)
        c.stroke(b.Ps([a, m, e]), 2.0, fc, taper=(0.3, 0.5), opacity=0.65, smooth=2)


def sandal(bb, near, col=(150, 96, 52)):
    """Bare foot in a strappy sandal."""
    c = bb.c
    an = bb.ankle_n if near else bb.ankle_f
    x, y = an
    L = 10.0 * bb.b["foot"]
    skin = bb.skin if near else shade_col(bb.skin, 0.86)
    foot = blob(bb.Ps([(x - 2.8, y + 2.0), (x + 2.0, y + 2.2), (x + L * 0.6, y - 0.4), (x + L * 1.02, y - 2.2), (x + L * 1.0, y - 4.0),
                       (x - 2.8, y - 4.0), (x - 3.2, y - 1.8)]), 1)
    c.ink(foot, skin, lw=c.lw * 0.85, shade=0.45, hi=0.3)
    c.ink(Sh([bb.Ps([(x - 3.4, y - 3.6), (x + L * 1.08, y - 3.6), (x + L * 1.08, y - 4.9), (x - 3.4, y - 4.9)])]), col, lw=c.lw * 0.7, shade=0.3)
    for (p, q) in (((x - 2.6, y + 0.5), (x + 2.4, y + 1.0)), ((x + L * 0.3, y - 0.2), (x + L * 0.62, y - 2.6))):
        c.stroke(bb.Ps([p, q]), max(2.0, bb.u * 1.1), col, taper=(0, 0))


def laurel(c, cx, cy, rx, ry, col=(90, 170, 70), n=7, wilt=0.0, seed=0):
    """Laurel wreath around a head (ellipse centre cx, cy); leaves along the back half."""
    rng = random.Random(seed)
    for side in (-1, 1):
        for k in range(n):
            t = k / (n - 1)
            a = math.radians(180 + side * (10 + t * 150)) if side < 0 else math.radians(-10 - t * 150)
            px, py = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            ang = math.degrees(a) + 90 * side + wilt * 40 * t + rng.uniform(-8, 8)
            L = rx * 0.2
            c.ink(ell(px, py + wilt * t * ry * 0.2, L, L * 0.42, ang), col if k % 2 else hi_col(col, 0.15), lw=1.8, oc=dk(col, 0.45),
                  shade=0.35, hi=0.3, ao=0, tex=0, wob=0.2)


def neck_beads(c, pts, r, col, n=None):
    P = resample(pts, r * 1.9)
    for x, y in P:
        c.ink(ell(x, y, r, r), col, lw=1.4, shade=0.4, sw=r * 0.6, hi=0.7, hw=r * 0.4, ao=0, tex=0, wob=0)


def pledge_beanie(c, b, col=(60, 110, 220)):
    """Blue pledge beanie with a small brim and a button on top (sits on the crown)."""
    hx, hy, r, ry = b.hx, b.hy, b.r, b.ry
    cap = blob([(hx - r * 1.04, hy - ry * 0.18), (hx - r * 0.98, hy - ry * 0.7), (hx - r * 0.5, hy - ry * 1.08), (hx + r * 0.2, hy - ry * 1.12),
                (hx + r * 0.82, hy - ry * 0.86), (hx + r * 1.02, hy - ry * 0.42), (hx + r * 0.2, hy - ry * 0.5), (hx - r * 0.6, hy - ry * 0.32)], 2)
    c.ink(cap, col, lw=3.0, shade=0.5, sw=r * 0.4, hi=0.45, hw=r * 0.18, rim=0.2)
    for k in range(4):
        a = -150 + k * 32
        ar = math.radians(a)
        c.stroke([(hx + math.cos(ar) * r * 0.2, hy - ry * 1.08), (hx + math.cos(ar) * r * 0.95, hy + math.sin(ar) * ry * 0.4 - ry * 0.55)],
                 1.6, shade_col(col, 0.55), opacity=0.6, smooth=1)
    c.ink(Sh([chaikin([(hx + r * 0.1, hy - ry * 0.52), (hx + r * 1.02, hy - ry * 0.44), (hx + r * 1.5, hy - ry * 0.3),
                       (hx + r * 1.42, hy - ry * 0.18), (hx + r * 0.9, hy - ry * 0.26), (hx + r * 0.1, hy - ry * 0.34)], 1)]),
          shade_col(col, 0.8), lw=2.6, shade=0.3, hi=0.3)
    c.ink(ell(hx - r * 0.1, hy - ry * 1.12, r * 0.14, r * 0.1), (250, 220, 80), lw=1.8, shade=0.3, hi=0.5)
    c.label(hx - r * 0.05, hy - ry * 0.78, "P", r * 0.42, (250, 220, 80), mirror=False)
    return cap


def clip_tie(c, b, col=(40, 52, 120), dots=(240, 200, 80)):
    sx, sy = b.lean_dx, b.shoulder_y
    x0, y0 = b.P(sx + 1.4, sy + 0.4)
    L = b.u * 18
    w = b.u * 2.6
    knot = blob([(x0 - w * 0.6, y0 - w * 0.2), (x0 + w * 0.6, y0 - w * 0.2), (x0 + w * 0.45, y0 + w * 0.9), (x0 - w * 0.45, y0 + w * 0.9)], 1)
    blade = blob([(x0 - w * 0.4, y0 + w * 0.8), (x0 + w * 0.4, y0 + w * 0.8), (x0 + w * 1.15, y0 + L * 0.8), (x0 + w * 0.2, y0 + L),
                  (x0 - w * 0.75, y0 + L * 0.82)], 1)
    c.ink(blade, col, lw=2.6, shade=0.5, hi=0.35)
    for k in range(5):
        c.ink(ell(x0 + w * (0.1 + (k % 2) * 0.5 - 0.25) + k * w * 0.08, y0 + w * 2 + k * L * 0.15, w * 0.18, w * 0.15), dots, lw=0,
              shade=0, hi=0, ao=0, tex=0, wob=0, clip=blade)
    c.ink(knot, shade_col(col, 0.85), lw=2.4, shade=0.3, hi=0.3)
    c.stroke([(x0 - w * 0.9, y0 - w * 0.4), (x0 + w * 0.9, y0 - w * 0.4)], 2.4, (200, 204, 216), taper=(0, 0))


# =========================================================================== Tess Calloway (sorority president)
def paint_tess_calloway(height=382, name="hs_tess_calloway.png"):
    W, Hc = 360, 600
    skin = (250, 212, 184)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=201)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.86, waist=0.72, hips=1.0, limbs=0.84, head=1.05, legs=1.04, neck=1.0, chest=1.0, hand=0.9, foot=0.9),
             pose=dict(arm_n=10, fore_n=92, arm_f=-8, fore_f=26, leg_n=2, shin_n=-1, leg_f=-5, shin_f=4, lean=-2, head_dx=0.4,
                       head_dy=0.3), seed=21)
    card, card_hi = (246, 130, 176), (255, 196, 220)
    navy = (44, 50, 110)
    hair, hair_sh, hair_hi = (140, 74, 44), (90, 44, 30), (200, 124, 72)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # bob behind the head
    c.ink(blob([(hx - r * 1.25, hy + ry * 0.75), (hx - r * 1.3, hy - ry * 0.2), (hx - r * 0.7, hy - ry * 1.0), (hx + r * 0.4, hy - ry * 1.05),
                (hx + r * 0.6, hy + ry * 0.9), (hx - r * 0.3, hy + ry * 1.0)], 2), shade_col(hair, 0.8), lw=3.0, shade=0.4)
    # far arm
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.86))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.0, w1=7.0, cuff=6.4), shade_col(card, 0.8), lw=2.8, shade=0.4)

    def loafer(bb, near):
        bb.shoe(near, (130, 36, 60) if near else (104, 30, 50), (60, 30, 30), kind="shoe", length=0.95)
        an = bb.ankle_n if near else bb.ankle_f
        c.ink(ell(*bb.P(an[0] + 6.5, an[1] - 1.2), bb.u * 1.0, bb.u * 0.7), (250, 220, 90), lw=1.2)
    for near in (False, True):
        sh = b.leg_shape(near, w=(7.2, 4.9, 3.6))
        c.ink(sh, skin if near else shade_col(skin, 0.88), lw=3.0, shade=0.5, hi=0.35)
        an = b.ankle_n if near else b.ankle_f
        kn = b.knee_n if near else b.knee_f
        sock = Sh([b.Ps([(an[0] - 2.4, an[1] - 2), (an[0] + 2.4, an[1] - 2), (kn[0] + 2.4, kn[1] - 3), (kn[0] - 2.6, kn[1] - 3)])])
        c.ink(sock, (250, 250, 246) if near else (214, 212, 226), lw=0, shade=0.4, hi=0.2, clip=sh)
        c.ink(sh, (0, 0, 0, 0), lw=3.0, line_only=True)
        c.stroke(b.Ps([(kn[0] - 2.6, kn[1] - 3), (kn[0] + 2.4, kn[1] - 3)]), 2.4, (240, 120, 170), taper=(0, 0))
        loafer(b, near)
    # pleated navy skirt with a pink stripe
    sk = skirt(b, navy, b.hip_y - 16, flare=2.4, waist=b.hip_y + 7, pleats=4)
    clip_draw(c, sk, lambda t: t.stroke(b.Ps([(-9, b.hip_y - 13.5), (9, b.hip_y - 13.5)]), b.u * 1.0, (246, 130, 176), taper=(0, 0)))
    c.ink(sk, (0, 0, 0, 0), lw=3.0, line_only=True)
    # torso: white blouse under a pink cardigan
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.8, hem=b.hip_y + 4, flare=0.6, neck_open=1.0)])
    c.ink(torso, card, lw=3.0, shade=0.55, sw=18, hi=0.4, hcol=card_hi, rim=0.2, rcol=(255, 200, 230))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 1.6, sy + 1.4), (sx + 3.0, sy + 1.0), (sx + 3.6, b.hip_y + 6), (sx + 1.0, b.hip_y + 5)])]), (250, 248, 244),
          lw=2.2, shade=0.35)
    for k in range(4):
        c.ink(ell(*b.P(sx + 3.0, sy - 5 - k * 6), 3.2, 3.2), (250, 240, 250), lw=1.4, hi=0.5)
    for pts in ([(sx - 2.4, sy + 2.2), (sx - 0.2, sy - 2.2), (sx + 1.0, sy + 0.8)], [(sx + 2.0, sy + 0.6), (sx + 3.4, sy - 2.6), (sx + 5.0, sy + 1.6)]):
        c.ink(Sh([b.Ps(pts)]), (252, 252, 250), lw=2.2, shade=0.3)
    neck_beads(c, bez(b.P(sx - 1.6, sy + 0.4), b.P(sx + 0.6, sy - 5.5), b.P(sx + 3.4, sy + 0.2), 12), b.u * 0.75, (252, 248, 240))
    # head
    head = Sh([b.head_pts(jaw=0.94, chin=0.95, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.44, r * 0.3, (255, 110, 140), 0.45)
    b.eyes(iris=(60, 140, 110), look=(0.4, 0.0), lid=0.2, size=1.04, lashes=1)
    b.brows(col=hair_sh, lift_n=0.05, lift_f=0.32, tilt_n=-0.05, tilt_f=-0.3, w=r * 0.1, arch=0.12)
    b.nose("button", 0.95)
    b.mouth("smile", fa["mouth"][0], fa["mouth"][1] + ry * 0.0, r * 0.56, r * 0.34, lip=(236, 90, 130))
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.05, ey_ + r * 0.52, r * 0.1, r * 0.1), (252, 248, 240), lw=1.6, hi=0.6)
    # glossy chestnut bob + side-swept bangs
    bob = blob([(hx - r * 1.22, hy + ry * 0.72), (hx - r * 1.28, hy - ry * 0.3), (hx - r * 0.86, hy - ry * 0.98), (hx - r * 0.05, hy - ry * 1.12),
                (hx + r * 0.75, hy - ry * 0.92), (hx + r * 1.12, hy - ry * 0.4), (hx + r * 1.1, hy + ry * 0.05), (hx + r * 0.85, hy - ry * 0.4),
                (hx + r * 0.3, hy - ry * 0.62), (hx - r * 0.1, hy - ry * 0.45), (hx - r * 0.3, hy + ry * 0.2), (hx - r * 0.42, hy + ry * 0.75),
                (hx - r * 0.85, hy + ry * 0.95)], 2)
    c.ink(bob, hair, lw=3.0, shade=0.5, sw=r * 0.45, scol=hair_sh, hi=0.55, hw=r * 0.25, hcol=hair_hi, rim=0.2, rcol=(255, 170, 140))
    hair_strands(c, [[(hx - r * 0.7, hy - ry * 0.9), (hx + r * 0.2, hy - ry * 0.85), (hx + r * 0.95, hy - ry * 0.3)],
                     [(hx - r * 1.05, hy - ry * 0.4), (hx - r * 1.0, hy + ry * 0.3), (hx - r * 0.8, hy + ry * 0.8)]], hair_hi, w=2.0, o=0.6)
    # big pink headband with a bow
    hb = Sh([chaikin([(hx - r * 0.95, hy - ry * 0.55), (hx - r * 0.4, hy - ry * 0.98), (hx + r * 0.3, hy - ry * 1.02), (hx + r * 0.8, hy - ry * 0.75),
                      (hx + r * 0.72, hy - ry * 0.6), (hx + r * 0.25, hy - ry * 0.84), (hx - r * 0.4, hy - ry * 0.8), (hx - r * 0.86, hy - ry * 0.4)], 2)])
    c.ink(hb, (240, 80, 150), lw=2.6, shade=0.4, hi=0.5)
    bx_, by_ = hx - r * 0.55, hy - ry * 0.98
    for s_ in (-1, 1):
        c.ink(blob([(bx_, by_), (bx_ + s_ * r * 0.55, by_ - r * 0.38), (bx_ + s_ * r * 0.62, by_ + r * 0.12), (bx_ + s_ * r * 0.1, by_ + r * 0.05)], 2),
              (250, 96, 164), lw=2.6, shade=0.45, sw=r * 0.15, hi=0.5)
    c.ink(ell(bx_, by_, r * 0.14, r * 0.14), (220, 60, 130), lw=2.2, shade=0.3, hi=0.4)
    # near arm hugging a clipboard to the chest
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    wx, wy = b.P(*b.wrist_n)
    ex, ey = b.P(*b.elbow_n)
    cb = Sh([rot_pts([(wx - 30, wy - 70), (wx + 34, wy - 70), (wx + 34, wy + 28), (wx - 30, wy + 28)], 10, wx, wy)])
    c.ink(cb, (190, 140, 90), lw=2.8, shade=0.4, sw=10, hi=0.35)
    pg = Sh([rot_pts([(wx - 24, wy - 60), (wx + 28, wy - 60), (wx + 28, wy + 22), (wx - 24, wy + 22)], 10, wx, wy)])
    c.ink(pg, (252, 252, 246), lw=1.8, shade=0.2)
    for k in range(6):
        p0, p1 = rot_pts([(wx - 18, wy - 44 + k * 11), (wx + 18 - (k % 3) * 6, wy - 44 + k * 11)], 10, wx, wy)
        c.stroke([p0, p1], 1.4, (120, 120, 170) if k else (230, 80, 140), taper=(0, 0), opacity=0.8)
    cl = rot_pts([(wx - 8, wy - 76), (wx + 12, wy - 76), (wx + 12, wy - 64), (wx - 8, wy - 64)], 10, wx, wy)
    c.ink(Sh([cl]), (200, 200, 214), lw=2.0, shade=0.3, hi=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.4, w1=7.6, cuff=6.8), card, lw=3.0, shade=0.5, sw=10, hi=0.4, hcol=card_hi)
    b.hand(True, "flat", size=0.95, d=(0.3, -1.0))
    return finish_sprite(c, name, flip=False)


# =========================================================================== Chad Thunderclap (frat president)
def paint_chad_thunderclap(height=424, name="hs_chad_thunderclap.png"):
    W, Hc = 480, 660
    skin = (240, 176, 132)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.2, seed=202)
    b = Body(c, 210, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.55, waist=1.08, hips=1.1, limbs=1.45, head=0.94, legs=1.0, neck=1.8, chest=2.8, hand=1.15, foot=1.1),
             pose=dict(arm_n=-26, fore_n=74, arm_f=84, fore_f=96, leg_n=-6, shin_n=2, leg_f=8, shin_f=-3, lean=-3, head_dx=0.8,
                       head_dy=-0.4), seed=22)
    toga_c = (250, 248, 240)
    toga_sh = (186, 180, 214)
    sash = (130, 40, 140)
    gold = (246, 200, 70)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm, flexing (behind the torso; the bicep and fist show above the far shoulder)
    c.ink(b.arm_shape(False, w=1.7), shade_col(skin, 0.88), lw=3.2, shade=0.45, rim=0.15)
    ex, ey = b.P(*b.elbow_f)
    sx_, sy_ = b.P(*b.sh_f)
    c.ink(ell((ex + sx_) / 2, (ey + sy_) / 2 - b.u * 2.2, b.u * 4.6, b.u * 3.4, -10), shade_col(skin, 0.9), lw=3.0, shade=0.45, hi=0.35)
    b.hand(False, "fist", col=shade_col(skin, 0.88), size=1.1)
    wx, wy = b.P(*b.wrist_f)
    c.ink(rrect(wx - b.u * 3.0, wy + b.u * 0.6, wx + b.u * 3.0, wy + b.u * 3.2, 3), gold, lw=2.2, shade=0.3, hi=0.6)
    # legs: bare calves + sandals
    for near in (False, True):
        sh = b.leg_shape(near, w=(8.2, 5.8, 4.2))
        c.ink(sh, skin if near else shade_col(skin, 0.86), lw=3.2, shade=0.5, hi=0.35)
        kn = b.knee_n if near else b.knee_f
        c.stroke(b.Ps([(kn[0] + 0.6, kn[1] - 4), (kn[0] + 2.6, kn[1] - 9), (kn[0] + 1.0, kn[1] - 13)]), 1.6, shade_col(skin, 0.6), opacity=0.6)
        sandal(b, near)
    # toga
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=12)
    body_sh = Sh([b.torso_pts(slack=0.6, hem=b.hip_y + 4, flare=0.4, neck_open=1.2)])
    c.ink(body_sh, skin, lw=3.0, shade=0.5, sw=20, hi=0.35)
    sy, sx = b.shoulder_y, b.lean_dx
    c.stroke(b.Ps([(sx + 3.5, sy - 1.5), (sx + 6.5, sy - 4), (sx + 8.5, sy - 3)]), 1.8, shade_col(skin, 0.6), opacity=0.7)   # pec line
    hem = 25
    tg = toga_shape(b, hem, flare=2.4, slack=1.0)
    c.ink(tg, toga_c, lw=3.2, shade=0.55, sw=22, scol=toga_sh, hi=0.3, rim=0.15)
    toga_folds(b, toga_c, hem, 4)
    band = Sh([chaikin(b.Ps([(b.sh_n[0] - 0.6, sy + 0.2), (b.sh_n[0] + 3.0, sy + 1.4), (5.6, b.hip_y + 4), (4.2, b.hip_y + 0.5)]), 1)])
    c.ink(band, sash, lw=2.6, shade=0.45, hi=0.35, clip=tg)
    c.ink(tg, (0, 0, 0, 0), lw=3.2, line_only=True)
    c.ink(ell(*b.P(b.sh_n[0] + 1.6, sy - 1.0), b.u * 2.0, b.u * 2.0), gold, lw=2.0, shade=0.3, hi=0.6)          # shoulder brooch
    c.stroke(b.Ps([(-6.4, hem + 2.6), (6.8, hem + 3.6)]), b.u * 0.9, gold, taper=(0.1, 0.1), opacity=0.9)      # gold hem trim
    # head: square jaw, big grin
    head = Sh([b.head_pts(jaw=1.32, chin=1.28, cheek=1.06, chin_drop=1.04)])
    c.ink(head, skin, lw=3.2, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.4, rim=0.15, rcol=(255, 170, 150))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.1, fa["eye_n"][1] + ry * 0.42, r * 0.32, (240, 90, 80), 0.4)
    b.eyes(iris=(60, 120, 210), look=(0.45, 0.05), lid=0.3, size=0.92)
    b.brows(col=(170, 120, 40), lift_n=0.08, lift_f=0.16, tilt_n=-0.25, tilt_f=-0.35, w=r * 0.15)
    b.nose("long", 1.0)
    b.mouth("teeth", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.08, r * 0.78, r * 0.4)
    cx_, cy_ = fa["chin"]
    c.stroke([(cx_ - r * 0.05, cy_ - ry * 0.06), (cx_ + r * 0.08, cy_ - ry * 0.02)], 1.8, shade_col(skin, 0.6), opacity=0.7)   # chin dimple
    b.ear(1.0)
    # blond swoop
    hair, hair_sh, hair_hi = (250, 210, 90), (196, 140, 50), (255, 246, 190)
    swoop = blob([(hx - r * 1.08, hy + ry * 0.05), (hx - r * 1.12, hy - ry * 0.6), (hx - r * 0.6, hy - ry * 1.08), (hx + r * 0.3, hy - ry * 1.3),
                  (hx + r * 1.1, hy - ry * 1.24), (hx + r * 1.42, hy - ry * 0.9), (hx + r * 1.0, hy - ry * 0.72), (hx + r * 0.5, hy - ry * 0.55),
                  (hx - r * 0.2, hy - ry * 0.5), (hx - r * 0.5, hy - ry * 0.1)], 2)
    c.ink(swoop, hair, lw=3.0, shade=0.5, sw=r * 0.35, scol=hair_sh, hi=0.55, hw=r * 0.2, hcol=hair_hi, rim=0.2)
    hair_strands(c, [[(hx - r * 0.6, hy - ry * 0.9), (hx + r * 0.4, hy - ry * 1.15), (hx + r * 1.25, hy - ry * 0.95)],
                     [(hx - r * 0.9, hy - ry * 0.5), (hx - r * 0.2, hy - ry * 0.95), (hx + r * 0.7, hy - ry * 0.98)]], hair_sh, w=2.0, o=0.6)
    laurel(c, hx - r * 0.1, hy - ry * 0.5, r * 1.1, ry * 0.42, seed=3)
    # near arm: hand on the hip, gold cuff
    c.ink(b.arm_shape(True, w=1.7), skin, lw=3.2, shade=0.5, hi=0.35)
    b.hand(True, "fist", size=1.1)
    wx, wy = b.P(*b.wrist_n)
    ex, ey = b.P(*b.elbow_n)
    d = (wx - ex, wy - ey)
    L = math.hypot(*d)
    nx, ny = -d[1] / L, d[0] / L
    ccx, ccy = wx - d[0] / L * b.u * 2.4, wy - d[1] / L * b.u * 2.4
    c.ink(Sh([[(ccx + nx * b.u * 3.2, ccy + ny * b.u * 3.2), (ccx - nx * b.u * 3.2, ccy - ny * b.u * 3.2),
               (ccx - nx * b.u * 3.2 - d[0] / L * b.u * 2.6, ccy - ny * b.u * 3.2 - d[1] / L * b.u * 2.6),
               (ccx + nx * b.u * 3.2 - d[0] / L * b.u * 2.6, ccy + ny * b.u * 3.2 - d[1] / L * b.u * 2.6)]]), gold, lw=2.2, shade=0.3, hi=0.6)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Dolly Spark (DJ)
def paint_dolly_spark(height=374, name="hs_dolly_spark.png"):
    W, Hc = 380, 640
    skin = (236, 190, 160)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=203)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.88, waist=0.74, hips=0.98, limbs=0.86, head=1.08, legs=1.04, neck=0.95, chest=1.0, hand=0.92, foot=1.0),
             pose=dict(arm_n=168, fore_n=-14, arm_f=-16, fore_f=34, leg_n=-8, shin_n=6, leg_f=10, shin_f=-2, lean=-4, head_dx=0.6,
                       head_dy=-0.2), seed=23)
    denim, denim_hi = (70, 120, 200), (140, 190, 240)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    hair, hair_sh, hair_hi = (250, 70, 170), (170, 30, 120), (255, 170, 220)
    teal = (40, 230, 210)
    # far arm, hand on hip, glow bracelets
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.86))
    wx, wy = b.P(*b.wrist_f)
    for k, col in enumerate(((90, 255, 120), (255, 90, 200))):
        c.ink(ell(wx, wy - k * 6 + 2, b.u * 2.6, b.u * 1.1), (0, 0, 0, 0), lw=3.0, oc=col, line_only=True)
        c.glow2(wx, wy - k * 6, 18, col, 0.4)
    c.ink(b.sleeve(False, 0.62, 8.6, 8.0), shade_col(denim, 0.8), lw=2.8, shade=0.4)
    # legs: striped tights + chunky platform sneakers

    def platform(bb, near):
        an = bb.ankle_n if near else bb.ankle_f
        x, y = an
        bb.shoe(near, (250, 250, 246) if near else (210, 210, 226), (240, 80, 170), kind="sneaker", length=1.05)
        c.ink(Sh([bb.Ps([(x - 3.6, y - 1.6), (x + 11.4, y - 2.0), (x + 11.6, y - 4.3), (x - 3.6, y - 4.3)])]), (240, 80, 170) if near else
              (190, 60, 140), lw=2.4, shade=0.3, hi=0.4)
        c.stroke(bb.Ps([(x + 1.5, y + 0.8), (x + 4.5, y - 0.6)]), 1.6, INK, opacity=0.7)
    for near in (False, True):
        sh = b.leg_shape(near, w=(7.2, 5.0, 3.8))
        base = (40, 30, 50) if near else (30, 22, 40)
        c.ink(sh, base, lw=3.0, shade=0.4, hi=0.2)
        bx0, by0, bx1, by1 = sh.bbox()
        stripe = (120, 230, 220) if near else (80, 170, 170)
        clip_draw(c, sh, lambda t, by0=by0, by1=by1, bx0=bx0, bx1=bx1, stripe=stripe: [
            t.ink(rect(bx0 - 4, y, bx1 + 4, y + 7), stripe, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
            for y in np.arange(by0, by1, 16)])
        c.ink(sh, (0, 0, 0, 0), lw=3.0, line_only=True)
        platform(b, near)
    # black mini skirt
    sk = skirt(b, (34, 26, 44), b.hip_y - 10, flare=1.6, waist=b.hip_y + 6)
    c.ink(sk, (0, 0, 0, 0), lw=0, shade=0, hi=0)
    for k in range(3):
        c.ink(ell(*b.P(-3 + k * 3.2, b.hip_y + 5), b.u * 0.6, b.u * 0.6), (210, 210, 220), lw=1.0)
    # torso: black tank + cropped denim jacket
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    tank = Sh([b.torso_pts(slack=0.4, hem=b.hip_y + 5, flare=0.2, neck_open=1.3)])
    c.ink(tank, (30, 24, 40), lw=3.0, shade=0.4, hi=0.25)
    sy, sx = b.shoulder_y, b.lean_dx
    bx_, by_ = b.P(sx + 3.4, sy - 14)
    u_ = b.u
    c.ink(Sh([[(bx_ + u_ * 0.8, by_ - u_ * 3.2), (bx_ - u_ * 1.4, by_ + u_ * 0.4), (bx_ + u_ * 0.1, by_ + u_ * 0.4), (bx_ - u_ * 0.8, by_ + u_ * 3.4),
               (bx_ + u_ * 1.6, by_ - u_ * 0.6), (bx_ + u_ * 0.1, by_ - u_ * 0.6)]]), (255, 230, 60), lw=1.4, shade=0.2, hi=0.3)
    jacket = Sh([chaikin(b.Ps([(sx - 2.8, sy + 1.8), (sx - 0.6, sy + 1.0), (sx + 0.6, sy - 6), (sx + 1.4, sy - 15), (sx + 0.6, b.hip_y + 14),
                               (sx * 0.6 - 5.4, b.hip_y + 13), (b.sh_n[0] - 0.4, sy - 6), (b.sh_n[0] + 0.6, sy + 0.6)]), 1)]) + \
        Sh([chaikin(b.Ps([(sx + 3.6, sy + 1.4), (sx + 6.8, sy + 0.4), (b.sh_f[0] + 1.6, sy - 5), (sx + 6.4, b.hip_y + 14), (sx + 4.4, b.hip_y + 15),
                          (sx + 4.8, sy - 8)]), 1)])
    c.ink(jacket, denim, lw=3.0, shade=0.55, sw=14, hi=0.4, hcol=denim_hi, rim=0.15)
    rng = random.Random(4)
    bx0, by0, bx1, by1 = jacket.bbox()
    for _ in range(14):        # safety pins
        x_, y_ = rng.uniform(bx0 + 6, bx1 - 6), rng.uniform(by0 + 10, by1 - 8)
        a = rng.uniform(-60, 60)
        p0, p1 = rot_pts([(x_ - 7, y_), (x_ + 7, y_)], a, x_, y_)
        c.stroke([p0, p1], 2.4, (226, 230, 240), taper=(0, 0))
        c.ink(ell(p0[0], p0[1], 2.0, 2.0), (250, 210, 80), lw=0.8)
    for (px_, py_, col, txt) in ((-3.0, b.hip_y + 22, (250, 220, 60), "★"), (sx - 2.0, b.hip_y + 11, (240, 80, 170), "")):
        c.ink(ell(*b.P(px_, py_), b.u * 2.0, b.u * 2.0), col, lw=1.8, shade=0.3, clip=jacket)
    c.stroke(b.Ps([(sx + 0.6, sy - 6), (sx + 0.4, b.hip_y + 14)]), 1.6, shade_col(denim, 0.5), opacity=0.7)
    # head
    head = Sh([b.head_pts(jaw=0.92, chin=0.94, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.2, rcol=(255, 130, 220))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.44, r * 0.3, (255, 90, 160), 0.5)
    b.eyes(iris=(100, 60, 200), look=(0.35, -0.1), lid=0.05, size=1.08, lashes=1)
    for (ex_, ey_), k in ((fa["eye_n"], 1.0), (fa["eye_f"], 0.65)):      # neon liner flick
        c.stroke([(ex_ + r * 0.28 * k, ey_ - ry * 0.18), (ex_ + r * 0.5 * k, ey_ - ry * 0.32)], 2.4, teal, taper=(0.1, 0.6))
    b.brows(col=hair_sh, lift_n=0.22, lift_f=0.2, tilt_n=0.0, tilt_f=-0.1, w=r * 0.1)
    b.nose("button", 0.9)
    b.mouth("grin", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.7, r * 0.46, open_col=(150, 20, 70))
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    for k in range(3):
        c.ink(ell(ex_ - r * 0.32 + k * r * 0.1, ey_ - r * 0.25 + k * r * 0.24, r * 0.05, r * 0.05), (220, 226, 240), lw=1.0)
    # big headphones round the neck
    nx_, ny_ = b.P(sx + 0.6, sy + 0.2)
    c.stroke(bez((nx_ - r * 0.9, ny_ - r * 0.1), (nx_, ny_ + r * 0.8), (nx_ + r * 0.9, ny_ - r * 0.2), 14), r * 0.16, (40, 36, 50), taper=(0, 0))
    for dx_ in (-0.9, 0.7):
        c.ink(ell(nx_ + r * dx_, ny_ - r * 0.1, r * 0.26, r * 0.32), (40, 36, 50), lw=2.6, shade=0.4, hi=0.4)
        c.ink(ell(nx_ + r * dx_ + r * 0.05, ny_ - r * 0.1, r * 0.12, r * 0.15), (255, 90, 200), lw=1.6, shade=0.2, hi=0.5)
    # asymmetric neon bob with long bangs, teal tips
    bob = blob([(hx - r * 1.18, hy + ry * 0.62), (hx - r * 1.3, hy - ry * 0.2), (hx - r * 0.95, hy - ry * 1.0), (hx - r * 0.1, hy - ry * 1.25),
                (hx + r * 0.85, hy - ry * 1.05), (hx + r * 1.3, hy - ry * 0.5), (hx + r * 1.3, hy + ry * 0.45), (hx + r * 1.05, hy + ry * 0.2),
                (hx + r * 0.95, hy - ry * 0.25), (hx + r * 0.45, hy - ry * 0.5), (hx + r * 0.1, hy - ry * 0.35), (hx - r * 0.3, hy + ry * 0.15),
                (hx - r * 0.5, hy + ry * 0.55)], 2)
    c.ink(bob, hair, lw=3.0, shade=0.5, sw=r * 0.45, scol=hair_sh, hi=0.55, hw=r * 0.25, hcol=hair_hi, rim=0.3, rcol=(120, 255, 240))
    clip_draw(c, bob, lambda t: t.ink(rect(hx - r * 2, hy + ry * 0.1, hx + r * 2, hy + ry * 1.2), teal, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0,
                                      opacity=0.9))
    c.ink(bob, (0, 0, 0, 0), lw=3.0, line_only=True)
    hair_strands(c, [[(hx - r * 0.6, hy - ry * 1.0), (hx + r * 0.4, hy - ry * 0.95), (hx + r * 1.1, hy - ry * 0.4)],
                     [(hx + r * 0.6, hy - ry * 0.6), (hx + r * 1.0, hy - ry * 0.1), (hx + r * 1.15, hy + ry * 0.35)]], hair_hi, w=2.2, o=0.6)
    c.glow2(hx, hy - ry * 0.3, r * 2.2, (255, 90, 200), 0.25)
    # near arm raised: rock-on hand
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, 0.62, 8.8, 8.2), denim, lw=3.0, shade=0.5, sw=10, hi=0.4, hcol=denim_hi)
    b.hand(True, "point", size=1.0, d=(0.15, -1.0))
    wx, wy = b.P(*b.wrist_n)
    c.ink(ell(wx, wy + 4, b.u * 2.4, b.u * 1.0), (0, 0, 0, 0), lw=3.0, oc=(255, 230, 60), line_only=True)
    c.glow2(wx, wy + 4, 18, (255, 230, 60), 0.4)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Mother Whitlock (housemother)
def paint_mother_whitlock(height=350, name="hs_mother_whitlock.png"):
    W, Hc = 380, 560
    skin = (246, 216, 196)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=204)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.98, waist=1.08, hips=1.2, limbs=1.0, head=1.04, legs=0.9, neck=0.85, chest=1.8, belly=0.8, hand=0.92,
                        foot=0.9),
             pose=dict(arm_n=8, fore_n=104, arm_f=-10, fore_f=18, leg_n=-2, shin_n=1, leg_f=3, shin_f=-1, lean=-4, head_dx=-0.2,
                       head_dy=0.6), seed=24)
    lilac, lilac_hi = (176, 140, 220), (222, 200, 250)
    tweed = (110, 86, 110)
    glove = (252, 252, 248)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm, gloved hand at the side
    c.ink(b.arm_shape(False), shade_col(lilac, 0.8), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(glove, 0.86))
    c.ink(b.sleeve(False, to_wrist=True, w0=8.6, w1=7.6, cuff=7.0), shade_col(lilac, 0.8), lw=2.8, shade=0.4)

    def pumps(bb, near):
        bb.shoe(near, (70, 46, 60) if near else (56, 36, 50), (40, 26, 36), kind="shoe", length=0.9)
    legs(b, (232, 200, 184), w=(7.0, 5.0, 3.8), shoe=pumps, skin=True)
    # long tweed skirt (mid-calf)
    sk = skirt(b, tweed, 16, flare=3.0, waist=b.hip_y + 8, pleats=3)
    rng = random.Random(7)
    bx0, by0, bx1, by1 = sk.bbox()
    clip_draw(c, sk, lambda t: [t.stroke([(x, by0), (x + 8, by1)], 1.0, (150, 126, 150), taper=(0, 0), opacity=0.35)
                                for x in np.arange(bx0 - 20, bx1 + 20, 7)])
    c.ink(sk, (0, 0, 0, 0), lw=3.0, line_only=True)
    # cardigan (buttoned) + lace collar + sorority pin
    c.ink(b.neck_shape(0.85), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y + 2, flare=1.2, neck_open=0.8)])
    c.ink(torso, lilac, lw=3.0, shade=0.55, sw=18, hi=0.4, hcol=lilac_hi, rim=0.2)
    sy, sx = b.shoulder_y, b.lean_dx
    for k in range(5):
        c.ink(ell(*b.P(sx + 3.0 + k * 0.25, sy - 4 - k * 6), 3.2, 3.2), (250, 246, 240), lw=1.4, hi=0.5)
    c.stroke(b.Ps([(sx + 2.6, sy - 1), (sx + 3.6, b.hip_y + 3)]), 1.6, shade_col(lilac, 0.55), opacity=0.7)
    for s_ in (-1, 1):
        cx_, cy_ = b.P(sx + 0.6 + s_ * 1.8, sy + 0.4)
        c.ink(blob([(cx_ - 12, cy_ - 4), (cx_ + 12, cy_ - 4), (cx_ + s_ * 14, cy_ + 14), (cx_ - s_ * 4, cy_ + 10)], 2), (252, 252, 248), lw=2.0,
              shade=0.3)
    px_, py_ = b.P(sx - 1.4, sy - 8)
    c.ink(Sh([[(px_, py_ - 9), (px_ + 8, py_), (px_, py_ + 9), (px_ - 8, py_)]]), (250, 210, 80), lw=1.8, shade=0.3, hi=0.6)
    c.ink(ell(px_, py_, 2.6, 2.6), (220, 50, 90), lw=0.8)
    # head
    head = Sh([b.head_pts(jaw=1.05, chin=1.0, cheek=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 170))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.46, r * 0.3, (240, 120, 150), 0.4)
    b.eyes(iris=(110, 110, 150), look=(0.45, 0.1), lid=0.42, size=0.94, lashes=1)
    b.brows(col=(150, 150, 170), lift_n=0.0, lift_f=0.4, tilt_n=-0.3, tilt_f=-0.5, w=r * 0.12, arch=0.15)
    b.nose("hook", 0.95)
    b.mouth("flat", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.42, r * 0.2, lip=(190, 80, 120))
    for (ex_, ey_) in (fa["eye_n"],):     # crow's feet + smile lines
        c.stroke([(ex_ - r * 0.42, ey_ + ry * 0.05), (ex_ - r * 0.55, ey_ + ry * 0.12)], 1.2, shade_col(skin, 0.6), opacity=0.6)
    mx, my = fa["mouth"]
    c.stroke([(mx - r * 0.32, my - ry * 0.18), (mx - r * 0.38, my + ry * 0.1)], 1.4, shade_col(skin, 0.6), opacity=0.6)
    b.ear(0.95)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.05, ey_ + r * 0.52, r * 0.11, r * 0.11), (252, 248, 240), lw=1.6, hi=0.6)
    # silver hair swept up into a tall bun
    hair, hair_sh, hair_hi = (220, 222, 236), (160, 160, 190), (255, 255, 255)
    bun = ell(hx - r * 0.35, hy - ry * 1.2, r * 0.62, r * 0.55)
    hs = blob([(hx - r * 1.08, hy + ry * 0.3), (hx - r * 1.16, hy - ry * 0.5), (hx - r * 0.7, hy - ry * 1.05), (hx + r * 0.2, hy - ry * 1.12),
               (hx + r * 0.95, hy - ry * 0.72), (hx + r * 1.04, hy - ry * 0.32), (hx + r * 0.55, hy - ry * 0.55), (hx - r * 0.15, hy - ry * 0.42),
               (hx - r * 0.45, hy + ry * 0.25)], 2)
    c.ink(bun, hair, lw=3.0, shade=0.5, sw=r * 0.3, scol=hair_sh, hi=0.5, hw=r * 0.2, hcol=hair_hi)
    c.stroke(ell_pts(hx - r * 0.35, hy - ry * 1.2, r * 0.38, r * 0.3, 0, 30, 0, 300), 1.6, hair_sh, opacity=0.7)
    c.ink(hs, hair, lw=3.0, shade=0.5, sw=r * 0.4, scol=hair_sh, hi=0.55, hw=r * 0.25, hcol=hair_hi, rim=0.2)
    hair_strands(c, [[(hx - r * 0.9, hy - ry * 0.2), (hx - r * 0.6, hy - ry * 0.8), (hx + r * 0.1, hy - ry * 1.0)],
                     [(hx - r * 0.3, hy - ry * 0.5), (hx + r * 0.4, hy - ry * 0.85), (hx + r * 0.9, hy - ry * 0.55)]], hair_sh, w=1.8, o=0.6)
    c.stroke([(hx - r * 0.7, hy - ry * 1.5), (hx + r * 0.05, hy - ry * 1.0)], 2.2, (240, 200, 90))     # hairpin
    # cat-eye glasses (lilac)
    fa = b.face_anchor()
    for (x_, y_, rx_, ry_) in ((fa["eye_n"][0], fa["eye_n"][1], r * 0.44, r * 0.34), (fa["eye_f"][0], fa["eye_f"][1], r * 0.24, r * 0.32)):
        sh_ = blob([(x_ - rx_, y_ - ry_ * 0.6), (x_ + rx_ * 1.15, y_ - ry_ * 1.15), (x_ + rx_, y_ + ry_ * 0.6), (x_ - rx_ * 0.6, y_ + ry_ * 0.8)], 2)
        c.ink(sh_, (0, 0, 0, 0), lw=max(2.6, r * 0.1), oc=(150, 80, 170), line_only=True, wob=0.2, inner=0.5)
        c.stroke([(x_ - rx_ * 0.4, y_ + ry_ * 0.3), (x_, y_ - ry_ * 0.4)], 2.0, (255, 255, 255), opacity=0.5)
    c.stroke([(fa["eye_n"][0] + r * 0.44, fa["eye_n"][1] - r * 0.1), (fa["eye_f"][0] - r * 0.24, fa["eye_f"][1] - r * 0.1)], 2.4, (150, 80, 170))
    c.stroke([(fa["eye_n"][0] - r * 0.44, fa["eye_n"][1] - r * 0.12), (ex_, ey_ - r * 0.1)], 2.2, (150, 80, 170))
    # chain for the glasses
    c.stroke(bez((ex_, ey_ - r * 0.05), (ex_ + r * 0.1, ey_ + r * 1.4), b.P(sx + 0.4, sy + 0.5), 10), 1.0, (250, 210, 90), opacity=0.8)
    # near arm: teacup + saucer held at the chest
    c.ink(b.arm_shape(True), lilac, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.8, w1=8.0, cuff=7.4), lilac, lw=3.0, shade=0.5, sw=10, hi=0.4, hcol=lilac_hi)
    g = b.hand(True, "hold", col=glove, size=0.95, d=(1.0, -0.15))
    wx, wy = b.P(*b.wrist_n)
    sx2, sy2 = wx + b.u * 6.5, wy - b.u * 1.6
    c.ink(ell(sx2, sy2, b.u * 6.0, b.u * 1.5), (250, 248, 252), lw=2.4, shade=0.4, hi=0.4)
    cup = blob([(sx2 - b.u * 3.4, sy2 - b.u * 5.4), (sx2 + b.u * 3.4, sy2 - b.u * 5.4), (sx2 + b.u * 2.4, sy2 - b.u * 0.6), (sx2 - b.u * 2.4, sy2 - b.u * 0.6)], 1)
    c.ink(cup, (250, 248, 252), lw=2.4, shade=0.45, sw=6, hi=0.5)
    c.stroke([(sx2 - b.u * 3.0, sy2 - b.u * 3.6), (sx2 + b.u * 3.0, sy2 - b.u * 3.6)], 1.6, (180, 120, 200), taper=(0, 0))
    c.ink(ell(sx2, sy2 - b.u * 5.4, b.u * 3.4, b.u * 0.7), (170, 110, 70), lw=1.6, shade=0.2)
    c.stroke(ell_pts(sx2 + b.u * 3.6, sy2 - b.u * 3.2, b.u * 1.3, b.u * 1.4, 0, 16, -100, 110), 2.0, INK)
    for k in range(2):
        x_ = sx2 - b.u * 1 + k * b.u * 2
        c.stroke([(x_, sy2 - b.u * 7), (x_ + 4, sy2 - b.u * 9), (x_ - 2, sy2 - b.u * 11.5)], 2.0, (255, 255, 255), opacity=0.45, smooth=2)
    return finish_sprite(c, name, flip=False)


# =========================================================================== Moose (the last pledge)
def _moose_body(c, fx, fy, height, sleeping=False):
    skin = (222, 168, 128)
    b = Body(c, fx, fy, height, skin=skin,
             build=dict(shoulders=1.35, waist=1.5, hips=1.3, limbs=1.5, head=1.1, legs=0.84, neck=1.4, chest=1.6, belly=9.0, hand=1.2,
                        foot=1.2),
             pose=(dict(arm_n=12, fore_n=72, arm_f=-4, fore_f=8, leg_n=-6, shin_n=4, leg_f=6, shin_f=-2, lean=2, head_dx=1.2, head_dy=-1.8)
                   if not sleeping else
                   dict(arm_n=64, fore_n=70, arm_f=10, fore_f=20, leg_n=30, shin_n=-40, leg_f=40, shin_f=-50, lean=4, head_dx=1.4,
                        head_dy=-1.6)), seed=26)
    return b


def _moose_draw(c, b, sleeping=False):
    toga_c, toga_sh = (248, 246, 236), (184, 178, 212)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    skin = b.skin
    # far arm
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=3.2, shade=0.45)
    b.hand(False, "relaxed", col=shade_col(skin, 0.86), size=1.1)
    # legs + sandals
    for near in (False, True):
        sh = b.leg_shape(near, w=(8.8, 6.6, 5.0))
        c.ink(sh, skin if near else shade_col(skin, 0.86), lw=3.2, shade=0.5, hi=0.3)
        sandal(b, near, col=(110, 76, 50))
    # toga over a big belly
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=12)
    body_sh = Sh([b.torso_pts(slack=1.2, hem=b.hip_y + 2, flare=1.0, neck_open=1.2)])
    c.ink(body_sh, skin, lw=3.2, shade=0.5, sw=24, hi=0.3)
    hem = 26
    tg = toga_shape(b, hem, flare=-1.5, slack=1.0)
    c.ink(tg, toga_c, lw=3.2, shade=0.55, sw=26, scol=toga_sh, hi=0.3, rim=0.15)
    toga_folds(b, toga_c, hem, 5)
    sy, sx = b.shoulder_y, b.lean_dx
    if not sleeping:
        clip_tie(c, b)
        # tummy rumble lines
        bx, by = b.P(sx + 9 + b.b["belly"], b.hip_y + 10)
        for k in range(3):
            c.stroke(ell_pts(bx, by, 14 + k * 9, 16 + k * 10, 0, 10, -40, 40), 2.2, (255, 250, 230), opacity=0.8)
    # head
    head = Sh([b.head_pts(jaw=1.25, chin=1.1, cheek=1.12, chin_drop=1.02)])
    c.ink(head, skin, lw=3.2, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.4, rim=0.15, rcol=(255, 170, 150))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.45, r * 0.34, (240, 100, 100), 0.45)
    if sleeping:
        b.eyes(closed=True, size=0.95)
        b.brows(col=(90, 56, 36), lift_n=0.0, lift_f=0.0, tilt_n=0.2, tilt_f=0.2, w=r * 0.15)
        b.nose("round", 1.1)
        b.mouth("smile", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.5, r * 0.3)
    else:
        b.eyes(iris=(90, 60, 40), look=(0.3, 0.05), lid=0.0, lower=0.1, size=1.04)
        b.brows(col=(90, 56, 36), lift_n=0.35, lift_f=0.35, tilt_n=0.7, tilt_f=0.7, w=r * 0.16)
        b.nose("round", 1.15)
        b.mouth("worried", fa["mouth"][0], fa["mouth"][1] + ry * 0.04, r * 0.56, r * 0.4)
    b.ear(1.05, jug=0.4)
    # stubble shadow
    c.soft(blob([(hx - r * 0.3, hy + ry * 0.75), (hx + r * 0.9, hy + ry * 0.6), (hx + r * 0.8, hy + ry * 1.1), (hx, hy + ry * 1.0)], 2),
           (90, 60, 80), 0.18, 4, clip=head)
    # buzz-cut hairline under the beanie
    c.ink(blob([(hx - r * 1.02, hy + ry * 0.05), (hx - r * 0.98, hy - ry * 0.4), (hx - r * 0.5, hy - ry * 0.45), (hx - r * 0.55, hy + ry * 0.1)], 2),
          (90, 60, 40), lw=2.2, shade=0.3)
    pledge_beanie(c, b)
    # near arm (resting on the belly)
    c.ink(b.arm_shape(True), skin, lw=3.2, shade=0.5, hi=0.3)
    if sleeping:
        return b
    b.hand(True, "flat", size=1.1)
    return b


def paint_moose(height=465, name="hs_moose.png"):
    W, Hc = 560, 700
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.2, seed=206)
    b = _moose_body(c, 240, Hc - 14, height)
    _moose_draw(c, b)
    return finish_sprite(c, name, flip=True)


def paint_sleeping_moose(height=330, name="hs_sleeping_moose.png"):
    """Moose asleep on his side on the cot, hugging a pink pillow (lying with his head to the left)."""
    W, Hc = 520, 620
    c = Canvas2(W, Hc, light=(0.95, -0.3), lw=3.2, seed=207)
    b = _moose_body(c, 240, Hc - 14, height, sleeping=True)
    _moose_draw(c, b, sleeping=True)
    # pink pillow hugged to the chest
    sy, sx = b.shoulder_y, b.lean_dx
    px_, py_ = b.P(*b.wrist_n)
    px_ += b.u * 4
    u_ = b.u
    pil = blob([(px_ - 6 * u_, py_ - 9 * u_), (px_ + 4 * u_, py_ - 10 * u_), (px_ + 7 * u_, py_ - 1 * u_), (px_ + 5 * u_, py_ + 9 * u_), (px_ - 4 * u_, py_ + 9.5 * u_), (px_ - 6 * u_, py_ + 0.5 * u_)], 2)
    c.ink(pil, (250, 140, 190), lw=3.0, shade=0.5, sw=20, hi=0.45, rim=0.2)
    c.ink(blob([(px_ - 10, py_ - 14), (px_ + 4, py_ - 26), (px_ + 18, py_ - 14), (px_ + 4, py_ + 8)], 1), (255, 200, 225), lw=1.6, shade=0.2)
    b.hand(True, "flat", size=1.1, d=(0.6, -0.8))
    # turn him on his side (head to the left)
    c.img = c.img.rotate(90, resample=Image.BICUBIC, expand=True)
    c.w, c.h = c.h, c.w
    hx, hy = None, None
    a = np.asarray(c.img.getchannel("A"))
    ys, xs = np.nonzero(a > 8)
    x0, y0 = xs.min() / S, ys.min() / S
    for k, (dx, dy, sz) in enumerate(((60, 20, 18), (90, -4, 24), (126, -32, 30))):
        c.text(x0 + dx, y0 + dy - 10, "Z", sz, (240, 240, 255), stroke=1.6, sc=INK)
    return finish_sprite(c, name, flip=False)


# =========================================================================== Dunk (seventh-year senior)
def paint_dunk(height=403, name="hs_dunk.png"):
    W, Hc = 440, 640
    skin = (200, 146, 110)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=208)
    b = Body(c, 200, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.05, waist=1.25, hips=1.15, limbs=1.05, head=1.0, legs=0.98, neck=1.0, chest=1.0, belly=2.6, hand=1.0, foot=1.05),
             pose=dict(arm_n=12, fore_n=96, arm_f=-6, fore_f=16, leg_n=-10, shin_n=4, leg_f=12, shin_f=-6, lean=-6, head_dx=0.6, head_dy=-0.8),
             seed=28)
    toga_c, toga_sh = (232, 220, 186), (170, 150, 150)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    hair, hair_sh, hair_hi = (70, 50, 46), (40, 26, 30), (130, 100, 90)
    # long hair at the back (behind)
    c.ink(blob([(hx - r * 1.1, hy - ry * 0.4), (hx - r * 1.5, hy + ry * 0.6), (hx - r * 1.3, hy + ry * 1.5), (hx - r * 0.6, hy + ry * 1.3),
                (hx - r * 0.3, hy + ry * 0.4)], 2), shade_col(hair, 0.85), lw=3.0, shade=0.4)
    # far arm
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.86))
    # legs: hairy shins, tube socks, flip-flops

    def flops(bb, near):
        an = bb.ankle_n if near else bb.ankle_f
        x, y = an
        c.ink(Sh([bb.Ps([(an[0] - 2.4, an[1] + 7), (an[0] + 2.4, an[1] + 7), (an[0] + 2.6, an[1] - 1), (an[0] - 2.6, an[1] - 1)])]),
              (250, 250, 246) if near else (210, 210, 224), lw=2.4, shade=0.4)
        for k in (5.6, 4.2):
            c.stroke(bb.Ps([(an[0] - 2.4, an[1] + k), (an[0] + 2.4, an[1] + k)]), 1.8, (220, 60, 60), taper=(0, 0))
        sandal(bb, near, col=(60, 160, 200))
    for near in (False, True):
        sh = b.leg_shape(near, w=(8.4, 5.8, 4.4))
        c.ink(sh, skin if near else shade_col(skin, 0.86), lw=3.0, shade=0.5, hi=0.3)
        kn = b.knee_n if near else b.knee_f
        an = b.ankle_n if near else b.ankle_f
        for k in range(5):
            y_ = an[1] + 8 + k * 2.6
            c.stroke(b.Ps([(kn[0] - 1.4 + k * 0.2, y_), (kn[0] - 0.8 + k * 0.2, y_ + 1.2)]), 1.0, (60, 40, 30), opacity=0.6)
        flops(b, near)
    # faded toga over a vintage tee, mug in hand
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=8)
    tee = Sh([b.torso_pts(slack=1.0, hem=b.hip_y + 2, flare=0.8, neck_open=1.0)])
    c.ink(tee, (230, 110, 70), lw=3.0, shade=0.5, sw=18, hi=0.3)
    sy, sx = b.shoulder_y, b.lean_dx
    hem = 24
    tg = toga_shape(b, hem, flare=2.6, slack=1.4)
    c.ink(tg, toga_c, lw=3.0, shade=0.55, sw=22, scol=toga_sh, hi=0.25, tex=0.2)
    toga_folds(b, toga_c, hem, 4)
    rng = random.Random(3)
    bx0, by0, bx1, by1 = tg.bbox()
    for _ in range(5):        # stains, a patch, a cigarette... no: a pizza stain
        c.soft(ell(rng.uniform(bx0, bx1), rng.uniform(by0, by1), rng.uniform(8, 18), rng.uniform(6, 12)), (150, 110, 60), 0.3, 3, clip=tg)
    pt = b.P(-2, hem + 10)
    c.ink(Sh([rot_pts([(pt[0] - 16, pt[1] - 12), (pt[0] + 16, pt[1] - 12), (pt[0] + 16, pt[1] + 12), (pt[0] - 16, pt[1] + 12)], 8, *pt)]),
          (90, 150, 200), lw=2.0, shade=0.3, clip=tg)
    for k in range(4):
        c.stroke([(pt[0] - 18 + k * 11, pt[1] - 14), (pt[0] - 16 + k * 11, pt[1] - 8)], 1.2, INK, opacity=0.6)
    # head: stubble, wilted laurel, sunglasses at night
    head = Sh([b.head_pts(jaw=1.1, chin=1.0, cheek=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.35, rim=0.15, rcol=(255, 160, 130))
    fa = b.face_anchor()
    c.soft(blob([(hx - r * 0.3, hy + ry * 0.6), (hx + r * 0.95, hy + ry * 0.45), (hx + r * 0.85, hy + ry * 1.12), (hx - r * 0.1, hy + ry * 1.0)], 2),
           (60, 40, 50), 0.3, 3, clip=head)
    b.nose("long", 1.05)
    b.mouth("smirk", fa["mouth"][0] + r * 0.02, fa["mouth"][1] + ry * 0.02, r * 0.5, r * 0.3)
    b.brows(col=hair_sh, lift_n=0.38, lift_f=0.36, tilt_n=-0.1, tilt_f=-0.1, w=r * 0.13)
    b.ear(1.0)
    # wraparound shades (dark, with a neon glint)
    (ex_, ey_), (fx_, fy_) = fa["eye_n"], fa["eye_f"]
    shades = blob([(ex_ - r * 0.5, ey_ - r * 0.25), (fx_ + r * 0.3, fy_ - r * 0.3), (fx_ + r * 0.26, fy_ + r * 0.2), (fx_ - r * 0.1, fy_ + r * 0.28),
                   ((ex_ + fx_) / 2, ey_ + r * 0.05), (ex_ + r * 0.1, ey_ + r * 0.36), (ex_ - r * 0.45, ey_ + r * 0.2)], 1)
    c.ink(shades, (30, 24, 50), lw=2.6, shade=0.2, hi=0.5, hw=4, hcol=(160, 120, 255))
    c.stroke([(ex_ - r * 0.25, ey_ + r * 0.1), (ex_ + r * 0.05, ey_ - r * 0.15)], 2.4, (255, 140, 230), opacity=0.7)
    c.stroke([(ex_ - r * 0.5, ey_ - r * 0.15), (fa["ear"][0], fa["ear"][1] - r * 0.1)], 2.6, (30, 24, 50))
    # shaggy hair + wilted laurel
    hs = blob([(hx - r * 1.12, hy + ry * 0.4), (hx - r * 1.2, hy - ry * 0.5), (hx - r * 0.7, hy - ry * 1.08), (hx + r * 0.2, hy - ry * 1.15),
               (hx + r * 0.95, hy - ry * 0.75), (hx + r * 1.08, hy - ry * 0.25), (hx + r * 0.7, hy - ry * 0.45), (hx + r * 0.3, hy - ry * 0.2),
               (hx - 0.05 * r, hy - ry * 0.5), (hx - r * 0.35, hy + ry * 0.1), (hx - r * 0.55, hy + ry * 0.55)], 2)
    c.ink(hs, hair, lw=3.0, shade=0.5, sw=r * 0.4, scol=hair_sh, hi=0.45, hw=r * 0.2, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 0.6, hy - ry * 0.9), (hx + r * 0.3, hy - ry * 0.9), (hx + r * 0.9, hy - ry * 0.4)]], hair_hi, w=1.8, o=0.6)
    laurel(c, hx - r * 0.1, hy - ry * 0.55, r * 1.1, ry * 0.42, col=(150, 150, 70), wilt=1.0, seed=8)
    # near arm: mug "WORLD'S OLDEST UNDERGRAD"
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, 0.5, 8.4, 7.8), (230, 110, 70), lw=3.0, shade=0.5)
    wx, wy = b.P(*b.wrist_n)
    mx0, my0 = wx + b.u * 2.0, wy - b.u * 10.5
    mug = rrect(mx0, my0, mx0 + b.u * 8.4, my0 + b.u * 10.0, 4)
    c.stroke(ell_pts(mx0 + b.u * 8.4, my0 + b.u * 5.0, b.u * 2.4, b.u * 3.0, 0, 16, -90, 90), 3.2, INK)
    c.ink(mug, (250, 246, 236), lw=2.6, shade=0.45, sw=8, hi=0.4)
    c.ink(ell(mx0 + b.u * 4.2, my0 + 1, b.u * 4.0, b.u * 0.9), (110, 66, 40), lw=1.6)
    for k, t in enumerate(("WORLD'S", "OLDEST", "UNDERGRAD")):
        c.text(mx0 + b.u * 4.2, my0 + b.u * (2.8 + k * 2.6), t, b.u * 1.5, (190, 40, 60), "Bold")
    b.hand(True, "hold", size=1.0, d=(1.0, -0.1))
    return finish_sprite(c, name, flip=False)


# =========================================================================== Fernanda (inflatable flamingo) + props
def paint_fernanda(height=290, name="hs_fernanda.png"):
    """Fernanda: a seven-foot inflatable flamingo with a smug face. Feet at the bottom centre."""
    W, Hc = 300, 420
    c = Canvas2(W, Hc, light=(-0.4, -0.92), lw=3.0, seed=209)
    k = height / 330.0
    pink, pink_sh, pink_hi = (255, 120, 170), (210, 60, 130), (255, 200, 225)
    fx, fy = 150, Hc - 12

    def P(x, y):
        return (fx + x * k, fy - y * k)
    # legs (one tucked), base ring
    c.ink(ell(*P(0, 4), 40 * k, 9 * k), (240, 80, 150), lw=2.6, shade=0.4, hi=0.3)
    c.ink(limb([P(-6, 6), P(-4, 70), P(-2, 128)], [7 * k, 6 * k, 7 * k], smooth=1), (255, 110, 160), lw=2.6, shade=0.4, hi=0.3)
    c.ink(limb([P(10, 128), P(26, 96), P(4, 82)], [7 * k, 7 * k, 6 * k], smooth=1), (240, 96, 150), lw=2.6, shade=0.4)
    c.ink(ell(*P(-4, 72), 7 * k, 6 * k), (255, 130, 176), lw=2.2, shade=0.3)
    # tail feathers
    c.ink(blob([P(-70, 168), P(-110, 150), P(-120, 168), P(-96, 190), P(-60, 196)], 2), pink_sh, lw=3.0, shade=0.4, hi=0.3)
    # plump body with a seam
    body = blob([P(-84, 176), P(-60, 214), P(0, 232), P(56, 224), P(78, 190), P(66, 150), P(20, 128), P(-40, 132), P(-80, 150)], 2)
    c.ink(body, pink, lw=3.2, shade=0.55, sw=30, scol=pink_sh, hi=0.55, hw=16, hcol=pink_hi, rim=0.25, rcol=(255, 210, 250))
    c.stroke([P(-70, 190), P(-10, 168), P(60, 176)], 1.8, pink_sh, opacity=0.7, smooth=2)
    c.ink(ell(*P(10, 156), 14 * k, 6 * k, -10), (255, 255, 255), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.45)   # vinyl shine
    # wing
    c.ink(blob([P(-46, 198), P(10, 210), P(34, 190), P(10, 168), P(-40, 166), P(-64, 180)], 2), (255, 150, 190), lw=2.8, shade=0.45, hi=0.4)
    for j in range(3):
        c.stroke([P(-30 + j * 18, 196), P(-20 + j * 18, 172)], 1.6, pink_sh, opacity=0.6)
    # inflation valve
    c.ink(ell(*P(-56, 160), 6 * k, 6 * k), (250, 250, 250), lw=2.0, shade=0.3, hi=0.5)
    # S-neck
    neck = limb([P(46, 218), P(64, 262), P(44, 300), P(26, 330), P(40, 362)], [26 * k, 20 * k, 18 * k, 18 * k, 20 * k], smooth=2)
    c.ink(neck, pink, lw=3.0, shade=0.5, sw=12, scol=pink_sh, hi=0.5, hw=6, hcol=pink_hi, rim=0.2)
    # head + beak
    head = ell(*P(48, 372), 26 * k, 22 * k, -10)
    c.ink(head, pink, lw=3.0, shade=0.5, sw=10, scol=pink_sh, hi=0.5, hw=6, hcol=pink_hi)
    beak = blob([P(66, 380), P(104, 372), P(110, 346), P(98, 336), P(84, 354), P(64, 360)], 1)
    c.ink(beak, (252, 240, 220), lw=2.8, shade=0.4, hi=0.4)
    c.ink(blob([P(100, 360), P(110, 346), P(98, 336), P(90, 348)], 1), (40, 30, 40), lw=2.4, shade=0.2, hi=0.3)
    # smug half-lidded eye with lashes
    ex_, ey_ = P(50, 378)
    c.ink(ell(ex_, ey_, 8 * k, 8 * k), (252, 250, 246), lw=2.0, shade=0.2)
    c.ink(ell(ex_ + 2 * k, ey_ + 1 * k, 4.4 * k, 4.4 * k), (40, 20, 40), lw=0, shade=0, hi=0)
    c.ink(Sh([[(ex_ - 10 * k, ey_ - 10 * k), (ex_ + 10 * k, ey_ - 10 * k), (ex_ + 10 * k, ey_ - 1 * k), (ex_ - 10 * k, ey_ + 1 * k)]]), pink,
          lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=ell(ex_, ey_, 8 * k, 8 * k))
    c.stroke([(ex_ - 9 * k, ey_), (ex_ + 9 * k, ey_ - 2 * k)], 2.4, INK)
    for j in range(3):
        c.stroke([(ex_ + (2 + j * 3.5) * k, ey_ - 1 * k), (ex_ + (5 + j * 5) * k, ey_ - (9 - j) * k)], 1.8, INK, taper=(0, 0.7))
    c.soft(ell(ex_ + 4 * k, ey_ + 12 * k, 8 * k, 4 * k), (255, 60, 120), 0.4, 3)
    return finish_sprite(c, name, flip=False)


def paint_bedsheet(name="hs_bedsheet.png"):
    """A plain white bedsheet pegged to the clothesline, billowing a little. Top edge = the line."""
    W, Hc = 240, 280
    c = Canvas2(W, Hc, light=(-0.4, -0.92), lw=3.0, seed=210)
    x0, x1, y0, y1 = 22, 218, 20, 250
    sheet = blob([(x0, y0), (x0 + 60, y0 + 6), (x1 - 60, y0 + 6), (x1, y0), (x1 + 6, y0 + 90), (x1 - 4, y1 - 30), (x1 - 30, y1),
                  (x0 + 110, y1 - 14), (x0 + 50, y1 + 4), (x0 + 6, y1 - 20), (x0 - 6, y0 + 120)], 1)
    c.ink(sheet, (250, 250, 246), lw=3.0, shade=0.45, sw=40, scol=(190, 186, 226), hi=0.3, rim=0.15, tex=0.12)
    for xa, xb in ((60, 50), (110, 120), (160, 150), (196, 200)):
        c.stroke([(xa, y0 + 14), (xa + 8, y0 + 120), (xb, y1 - 20)], 2.0, (176, 170, 214), opacity=0.6, taper=(0.3, 0.6), smooth=2)
    c.stroke([(x0 + 4, y1 - 34), (x0 + 60, y1 - 18), (x0 + 110, y1 - 32), (x1 - 30, y1 - 16)], 2.4, (200, 190, 236), opacity=0.7, smooth=2)
    c.label(x1 - 34, y1 - 46, "TC", 13, (170, 120, 210), "Bold")       # lavender monogram
    c.ink(rect(x0 - 8, y0 - 4, x1 + 8, y0 + 2), (0, 0, 0, 0), lw=0)
    for px_ in (x0 + 10, (x0 + x1) / 2, x1 - 10):                      # clothes pegs
        c.ink(rrect(px_ - 5, y0 - 14, px_ + 5, y0 + 18, 3), (220, 170, 110), lw=2.0, shade=0.4, hi=0.4)
        c.stroke([(px_, y0 - 10), (px_, y0 + 14)], 1.0, INK, opacity=0.6)
    sprite_grade(c, 0.96, (0.97, 0.94, 1.0))
    return finish_sprite(c, name, margin=2)


def draw_record_sleeve(c, x, y, s):
    """Square record sleeve 's' px wide at top-left (x, y): a volcano erupting disco balls."""
    c.ink(rrect(x + s * 0.36, y - s * 0.06, x + s * 1.06, y + s * 0.64, s * 0.35), (24, 20, 30), lw=2.4, shade=0.2, hi=0.4)  # vinyl
    c.ink(ell(x + s * 0.72, y + s * 0.29, s * 0.12, s * 0.12), (255, 90, 120), lw=1.4)
    sl = rect(x, y, x + s, y + s)
    c.ink(sl, ("v", (120, 40, 160), (250, 110, 70)), lw=2.6, shade=0.3, hi=0.3)
    c.ink(Sh([[(x + s * 0.12, y + s * 0.92), (x + s * 0.4, y + s * 0.5), (x + s * 0.6, y + s * 0.5), (x + s * 0.88, y + s * 0.92)]]),
          (70, 40, 60), lw=1.8, shade=0.3, clip=sl)
    c.ink(Sh([[(x + s * 0.4, y + s * 0.52), (x + s * 0.5, y + s * 0.62), (x + s * 0.6, y + s * 0.52)]]), (255, 140, 40), lw=1.2, clip=sl)
    for k, (dx, dy, rr) in enumerate(((0.5, 0.36, 0.08), (0.3, 0.24, 0.06), (0.7, 0.22, 0.07), (0.5, 0.14, 0.05))):
        c.ink(ell(x + s * dx, y + s * dy, s * rr, s * rr), (220, 226, 240), lw=1.2, shade=0.4, hi=0.6, clip=sl)
        c.glow2(x + s * dx, y + s * dy, s * 0.14, (255, 240, 200), 0.4)
    c.text(x + s * 0.5, y + s * 0.84, "DISCO", s * 0.13, (255, 236, 120))
    c.text(x + s * 0.5, y + s * 0.95, "VOLCANO", s * 0.1, (255, 236, 120))


def paint_disco_volcano_record(name="hs_disco_volcano_record.png"):
    W, Hc = 140, 140
    c = Canvas2(W, Hc, light=(-0.4, -0.92), lw=2.6, seed=211)
    draw_record_sleeve(c, 26, 26, 76)
    c.ink(Sh([rot_pts([(70, 104), (92, 104), (92, 116), (70, 116)], -8, 80, 110)]), (250, 246, 230), lw=1.6, shade=0.2)   # tag
    c.stroke([(80, 104), (74, 96)], 1.0, INK)
    sprite_grade(c, 0.92, (0.96, 0.9, 1.0))
    return finish_sprite(c, name, margin=2)



# =========================================================================== scenery helpers
def clapboard(c, x0, y0, x1, y1, col, step=20, seed=0):
    """Painted wooden siding: horizontal boards with a lit lower lip and a dark gap."""
    rng = random.Random(seed)
    c.ink(rect(x0, y0, x1, y1), col, lw=3.0, shade=0.3, sw=40, hi=0.2, tex=0.18)
    y = y0 + step
    while y < y1:
        c.stroke([(x0 + 2, y), (x1 - 2, y)], 2.0, shade_col(col, 0.55), taper=(0, 0), wob=0.4, opacity=0.8)
        c.stroke([(x0 + 2, y + 3), (x1 - 2, y + 3)], 1.4, hi_col(col, 0.3), taper=(0, 0), wob=0.4, opacity=0.5)
        y += step
    for _ in range(int((x1 - x0) * (y1 - y0) / 9000)):
        x_, y_ = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.stroke([(x_, y_), (x_ + rng.uniform(8, 30), y_ + rng.uniform(-1, 1))], 1.4, hi_col(col, 0.5), opacity=0.35)   # peeling paint


def brick_face(c, x0, y0, x1, y1, col=(170, 64, 74), mortar=(110, 44, 64), bw=34, bh=15, seed=0):
    rng = random.Random(seed)
    c.ink(rect(x0, y0, x1, y1), mortar, lw=3.0, shade=0.3, sw=40, hi=0.1, tex=0.2)
    row = 0
    y = y0
    while y < y1:
        x = x0 - (bw / 2 if row % 2 else 0)
        while x < x1:
            cc = mix(col, (60, 20, 50) if rng.random() < 0.5 else (230, 120, 110), rng.uniform(0, 0.2))
            c.ink(rect(max(x0, x + 1.5), y + 1.5, min(x1, x + bw - 1.5), min(y1, y + bh - 1.5)), cc, lw=0, shade=0.2, sw=4, hi=0.25, hw=2,
                  ao=0, tex=0.15, wob=0.2)
            x += bw
        y += bh
        row += 1
    c.ink(rect(x0, y0, x1, y1), (0, 0, 0, 0), lw=3.0, line_only=True)


def lit_window(c, x0, y0, x1, y1, glass=(255, 206, 120), frame=(250, 240, 236), shutters=None, curtain=None, sill=True, panes=(2, 2),
               silhouette=None, seed=0):
    rng = random.Random(seed)
    if shutters:
        sw_ = (x1 - x0) * 0.42
        for xa, xb in ((x0 - sw_ - 8, x0 - 8), (x1 + 8, x1 + sw_ + 8)):
            c.ink(rect(xa, y0 - 4, xb, y1 + 4), shutters, lw=2.6, shade=0.4, hi=0.3)
            for yy in np.arange(y0 + 6, y1, 9):
                c.stroke([(xa + 4, yy), (xb - 4, yy)], 1.4, shade_col(shutters, 0.55), taper=(0, 0), opacity=0.8)
    c.ink(rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), frame, lw=2.8, shade=0.35, hi=0.3)
    c.ink(rect(x0, y0, x1, y1), ("v", hi_col(glass, 0.25), shade_col(glass, 0.85)), lw=2.2, shade=0.2, hi=0)
    if silhouette:
        silhouette(c, x0, y0, x1, y1)
    if curtain:
        for side in (0, 1):
            xa = x0 if side == 0 else x1 - (x1 - x0) * 0.28
            xb = x0 + (x1 - x0) * 0.28 if side == 0 else x1
            c.ink(Sh([[(xa, y0), (xb, y0), (xb - (8 if side == 0 else -8), y1), (xa, y1)]]), curtain, lw=2.0, shade=0.45, hi=0.3,
                  clip=rect(x0, y0, x1, y1))
    nx, ny = panes
    for k in range(1, nx):
        xx = x0 + (x1 - x0) * k / nx
        c.stroke([(xx, y0), (xx, y1)], 4.0, frame, taper=(0, 0))
    for k in range(1, ny):
        yy = y0 + (y1 - y0) * k / ny
        c.stroke([(x0, yy), (x1, yy)], 4.0, frame, taper=(0, 0))
    c.stroke([(x0 + 8, y1 - 10), (x0 + (x1 - x0) * 0.4, y0 + 8)], 6, (255, 255, 255), opacity=0.18)
    if sill:
        c.ink(rect(x0 - 16, y1 + 6, x1 + 16, y1 + 16), frame, lw=2.4, shade=0.4, hi=0.3)
    c.glow2((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 1.1, glass, 0.3)


def column(c, x, y0, y1, w=26, col=(250, 244, 236)):
    c.ink(rect(x - w / 2, y0 + 12, x + w / 2, y1 - 10), col, lw=2.8, shade=0.55, sw=w * 0.4, hi=0.45, hw=w * 0.15, tex=0.12)
    for k in range(1, 3):
        xx = x - w / 2 + w * k / 3
        c.stroke([(xx, y0 + 16), (xx, y1 - 14)], 1.2, shade_col(col, 0.7), taper=(0, 0), opacity=0.6)
    c.ink(rect(x - w / 2 - 6, y0, x + w / 2 + 6, y0 + 14), col, lw=2.4, shade=0.3, hi=0.3)
    c.ink(rect(x - w / 2 - 6, y1 - 12, x + w / 2 + 6, y1), col, lw=2.4, shade=0.3, hi=0.3)


def hedge(c, x0, x1, y, h=50, col=(46, 110, 90), seed=0):
    rng = random.Random(seed)
    x = x0
    while x < x1:
        r = rng.uniform(h * 0.6, h * 0.9)
        c.ink(ell(x + r * 0.6, y - r * 0.55, r, r * 0.75), mix(col, (30, 70, 70), rng.uniform(0, 0.3)), lw=2.6, shade=0.55, sw=r * 0.4, hi=0.35,
              hw=r * 0.2, rim=0.2, tex=0.2)
        x += r * 1.1


def grass_tufts(c, x0, x1, y0, y1, n, col=(70, 150, 100), seed=0):
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        for k in range(3):
            c.stroke([(x + k * 3, y), (x + k * 3 + rng.uniform(-6, 6), y - rng.uniform(6, 14))], 1.6, mix(col, (30, 60, 60), rng.uniform(0, 0.5)),
                     taper=(0, 0.8), opacity=0.8)


def red_cup(c, x, y, s=1.0, lying=False, ang=0):
    if lying:
        pts = rot_pts([(x - 12 * s, y - 7 * s), (x + 12 * s, y - 9 * s), (x + 12 * s, y + 2 * s), (x - 12 * s, y + 1 * s)], ang, x, y)
        c.ink(Sh([pts]), (220, 40, 60), lw=2.0, shade=0.4, hi=0.4)
        c.ink(ell(*rot_pts([(x + 12 * s, y - 3.5 * s)], ang, x, y)[0], 3 * s, 6 * s), (250, 240, 240), lw=1.4)
        return
    c.ink(Sh([[(x - 9 * s, y - 24 * s), (x + 9 * s, y - 24 * s), (x + 6.5 * s, y), (x - 6.5 * s, y)]]), (220, 40, 60), lw=2.0, shade=0.45, hi=0.45)
    c.ink(rect(x - 9 * s, y - 25 * s, x + 9 * s, y - 21 * s), (250, 240, 240), lw=1.2)


def neon_text(c, x, y, s, size, col, on=False, angle=0):
    """Neon tubing lettering: lit (glowing) or dark (unlit glass)."""
    if on:
        c.glow2(x, y, size * len(s) * 0.45, col, 0.45)
        c.text(x, y, s, size, hi_col(col, 0.5), "Italic", stroke=size * 0.08, sc=col, angle=angle)
    else:
        c.text(x, y, s, size, shade_col(col, 0.45), "Italic", stroke=size * 0.06, sc=(30, 20, 40), angle=angle)
        c.text(x - 2, y - 2, s, size, (0, 0, 0, 0), "Italic", stroke=0, angle=angle)


def plaque(c, x, y, w, h, text_lines, size=9, col=(220, 180, 80), ink_col=(80, 50, 30)):
    c.ink(rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 4), col, lw=2.2, shade=0.35, hi=0.5, hw=3)
    for k, t in enumerate(text_lines):
        c.text(x, y - h / 2 + (k + 0.75) * h / (len(text_lines) + 0.5), t, size, ink_col, "Bold")


# =========================================================================== 1. Greek Row (outdoor street)
def paint_greek_row():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(0.35, -0.94), lw=3.4, seed=2001)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), (-400, 100, 2320, 700), fc=1000)
    rng = random.Random(2001)
    P = R.pt
    HOR = 700

    # ---------------- sky
    c.ink(rect(-10, -10, W_BG + 10, HOR + 10), ("vy", -10, HOR, (30, 18, 76), (200, 70, 150)), lw=0, shade=0, hi=0, ao=0, tex=0.06, wob=0)
    c.soft(rect(-10, 420, W_BG + 10, HOR), (255, 120, 150), 0.35, 60)
    for _ in range(170):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, 360)
        r = rng.choice([0.9, 1.2, 1.8, 2.4])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.5, 1))
    mx, my = 360, 120
    c.ink(ell(mx, my, 44, 44), (255, 246, 220), lw=0, shade=0.3, sw=12, scol=(230, 200, 210), hi=0, tex=0.1)
    c.ink(ell(mx + 18, my - 10, 38, 38), (59, 27, 89), lw=0, shade=0, hi=0, ao=0, tex=0)       # crescent
    c.glow2(mx, my, 230, (255, 220, 255), 0.4)
    for (cx_, cy_, w) in ((780, 150, 380), (1500, 90, 300), (1840, 230, 260)):
        cl = blob([(cx_ - w / 2, cy_), (cx_ - w * 0.3, cy_ - 30), (cx_ - w * 0.05, cy_ - 44), (cx_ + w * 0.2, cy_ - 32), (cx_ + w / 2, cy_ - 6),
                   (cx_ + w * 0.3, cy_ + 12), (cx_ - w * 0.3, cy_ + 12)], 2)
        c.ink(cl, (140, 70, 150), lw=0, shade=0.3, sw=10, scol=(100, 50, 130), hi=0.4, hw=6, hcol=(255, 160, 190), opacity=0.75, tex=0.1)
    for k in range(44):          # distant trees + rooftops
        tx = k * 46 + rng.uniform(-20, 20)
        r = rng.uniform(40, 80)
        c.ink(ell(tx, HOR - 190 - rng.uniform(0, 60), r, r * 0.9), (64, 36, 100), lw=0, shade=0, hi=0, ao=0, tex=0.1)
    # water tower on the skyline
    c.ink(rect(1210, 300, 1290, 360), (70, 44, 104), lw=0, shade=0, hi=0, ao=0)
    c.ink(Sh([[(1200, 300), (1300, 300), (1250, 270)]]), (70, 44, 104), lw=0, shade=0, hi=0, ao=0)
    for X in (1216, 1284):
        c.stroke([(X, 360), (X - 6, 440)], 5, (70, 44, 104), taper=(0, 0))

    # ---------------- ground: lawn strip + brick sidewalk
    def floor(sub):
        tiles(sub, (166, 92, 110), (150, 80, 104), 0, 0, sub.w, sub.h, size=60 * sub.density, seed=21, chipped=0.1, grout=(96, 50, 84))
    R.paint_plane("floor", -400, 2700, 0, R.z_front(160), floor, density=0.9, seed=21)
    c.ink(rect(-10, HOR - 4, W_BG + 10, 748), ("vy", HOR, 748, (50, 110, 90), (40, 90, 80)), lw=2.4, shade=0, hi=0, ao=0, tex=0.25, wob=0.4)
    grass_tufts(c, 0, W_BG, 706, 748, 260, seed=3)
    c.ink(rect(-10, 748, W_BG + 10, 760), (190, 170, 180), lw=2.4, shade=0.3, hi=0.3)            # kerb
    for _ in range(14):
        x_, y_ = rng.uniform(0, W_BG), rng.uniform(780, 1060)
        c.soft(ell(x_, y_, rng.uniform(30, 90), rng.uniform(8, 20)), (60, 20, 60), 0.15, 10)

    # ---------------- left: path back to campus + signpost
    lamps = []
    lamps.append(lamppost(c, 120, 744, 300))
    c.ink(rect(30, 470, 44, 744), (110, 70, 60), lw=2.4, shade=0.4)
    for k, (t, ang) in enumerate((("CAMPUS", -4), ("QUAD", 3))):
        y_ = 500 + k * 54
        c.ink(Sh([rot_pts([(-10, y_ - 18), (90, y_ - 18), (112, y_), (90, y_ + 18), (-10, y_ + 18)], ang, 40, y_)]), (240, 200, 80), lw=2.6, shade=0.4,
              hi=0.3)
        c.text(48, y_, "← " + t, 14, (90, 40, 30), angle=-ang)
    hedge(c, -30, 60, 744, 46, seed=1)

    # ---------------- clothesline (the bedsheet itself is a sprite hung on this line)
    for X in (170, 470):
        c.stroke([(X, 744), (X, 410)], 12, INK, taper=(0, 0))
        c.stroke([(X, 744), (X, 410)], 7, (150, 110, 90), taper=(0, 0))
        c.ink(rect(X - 36, 404, X + 36, 418), (150, 110, 90), lw=2.4, shade=0.3, hi=0.3)
    line = cable(c, (140, 412), (500, 412), sag=26, w=2.4, col=(230, 226, 236), outline=True)
    LINE_Y[0] = min(line, key=lambda p: abs(p[0] - BEDSHEET_X))[1]
    for (x_, w_, h_, col) in ((392, 46, 70, (100, 200, 200)), (446, 30, 52, (250, 140, 180))):
        y_ = min(line, key=lambda p: abs(p[0] - x_))[1]
        c.ink(blob([(x_ - w_ / 2, y_), (x_ + w_ / 2, y_ + 2), (x_ + w_ / 2 - 3, y_ + h_), (x_ - w_ / 2 + 2, y_ + h_ - 4)], 1), col, lw=2.4, shade=0.45,
              hi=0.3)
        c.ink(rrect(x_ - 4, y_ - 10, x_ + 4, y_ + 10, 2), (220, 170, 110), lw=1.6)
    c.text(392, min(line, key=lambda p: abs(p[0] - 392))[1] + 40, "ΦΛΑ", 12, (250, 250, 240))

    # ---------------- Phi Lambda Alpha sorority house (pink, white trim)
    sx0, sx1 = 500, 960
    PINK = (240, 150, 190)
    # roof + gable
    c.ink(Sh([[(sx0 - 40, 330), (sx1 + 40, 330), (sx1 - 10, 270), (sx0 + 10, 270)]]), (110, 60, 110), lw=3.2, shade=0.4, hi=0.2, tex=0.2)
    clapboard(c, sx0, 300, sx1, HOR - 6, PINK, step=20, seed=4)
    c.ink(Sh([[(sx0 + 70, 330), (sx1 - 70, 330), ((sx0 + sx1) / 2, 190)]]), PINK, lw=3.2, shade=0.35, hi=0.3)
    c.ink(Sh([[(sx0 + 40, 336), (sx1 - 40, 336), ((sx0 + sx1) / 2, 176)]]), (0, 0, 0, 0), lw=10, oc=(252, 246, 240), line_only=True)
    c.ink(ell((sx0 + sx1) / 2, 278, 30, 30), (252, 246, 240), lw=2.6, shade=0.3, hi=0.3)
    c.text((sx0 + sx1) / 2, 280, "ΦΛΑ", 20, (200, 60, 120))
    c.ink(rect(sx0 - 10, 330, sx1 + 10, 346), (252, 246, 240), lw=2.6, shade=0.3, hi=0.3)
    # upstairs windows with shutters, one with a sister peeking
    def peek(cc, x0, y0, x1, y1):
        cc.ink(ell((x0 + x1) / 2 + 6, y0 + (y1 - y0) * 0.55, (x1 - x0) * 0.18, (y1 - y0) * 0.24), (120, 60, 90), lw=0, shade=0, hi=0, ao=0)
    for k, X in enumerate((580, 880)):
        lit_window(c, X - 34, 374, X + 34, 452, shutters=(200, 60, 120), curtain=(255, 220, 230), silhouette=peek if k else None, seed=k)
    # porch: roof, columns, railing; front door (hotspot "Sorority door")
    c.ink(rect(sx0 + 20, 486, sx1 - 20, 506), (252, 246, 240), lw=2.8, shade=0.35, hi=0.3)
    dx0, dx1, dy0 = 620, 720, 540
    c.ink(rect(dx0 - 22, dy0 - 22, dx1 + 22, HOR - 26), (252, 246, 240), lw=2.8, shade=0.4, hi=0.3)
    c.ink(Sh([ell_pts((dx0 + dx1) / 2, dy0 - 20, (dx1 - dx0) / 2 + 22, 40, 0, 24, 180, 360)]), (255, 214, 140), lw=2.6, shade=0.2, hi=0.3)  # fanlight
    flat_door(c, dx0, dy0, dx1, HOR - 26, (230, 70, 130), frame=(252, 246, 240), knob="R", seed=5)
    wx_, wy_ = (dx0 + dx1) / 2, dy0 + 50
    for k in range(14):        # wreath
        a = k / 14 * 2 * math.pi
        c.ink(ell(wx_ + math.cos(a) * 22, wy_ + math.sin(a) * 22, 9, 6, math.degrees(a) + 90), (60, 140, 90), lw=1.6, shade=0.3, hi=0.3)
    for k in range(3):
        c.ink(ell(wx_ - 14 + k * 14, wy_ + 20 - (k % 2) * 6, 4, 4), (230, 50, 80), lw=1.2)
    plaque(c, wx_, dy0 + 112, 70, 34, ["GENTLEMEN", "NECKTIES ONLY"], 6.5)
    lit_window(c, 520, 552, 586, 626, shutters=(200, 60, 120), curtain=(255, 220, 230), seed=7)
    lit_window(c, 760, 552, 826, 626, shutters=(200, 60, 120), curtain=(255, 220, 230), seed=8)
    lit_window(c, 874, 552, 934, 626, shutters=(200, 60, 120), seed=9)
    for X in (sx0 + 40, 600, 740, sx1 - 40):
        column(c, X, 506, HOR - 20, 24)
    c.ink(rect(sx0 + 20, HOR - 26, sx1 - 20, HOR - 8), (252, 246, 240), lw=2.6, shade=0.35, hi=0.3)
    for (xa, xb) in ((sx0 + 52, 588), (752, sx1 - 52)):          # porch railings
        c.ink(rect(xa, 640, xb, 648), (252, 246, 240), lw=2.2, shade=0.3)
        for X in np.arange(xa + 6, xb, 13):
            c.stroke([(X, 648), (X, HOR - 26)], 3.0, (240, 232, 236), taper=(0, 0))
    for k in range(3):                                            # steps
        c.ink(rect(dx0 - 20 - k * 10, HOR - 8 + k * 14, dx1 + 20 + k * 10, HOR + 6 + k * 14), (220, 210, 220), lw=2.4, shade=0.3, hi=0.3)
    bulb(c, (dx0 + dx1) / 2, 520, 8, strength=0.45)
    hedge(c, sx0 - 10, 590, HOR + 8, 44, seed=2)
    hedge(c, 760, 800, HOR + 8, 40, seed=3)
    # Fernanda's plinth on the lawn (she stands here once she is home)
    px_, py_ = FERN_X, 748
    c.soft(ell(px_, py_ + 2, 80, 12), (24, 6, 34), 0.5, 8)
    c.ink(rect(px_ - 56, py_ - 46, px_ + 56, py_), (236, 226, 236), lw=3.0, shade=0.45, sw=20, hi=0.3)
    c.ink(rect(px_ - 64, py_ - 56, px_ + 64, py_ - 44), (250, 244, 250), lw=2.6, shade=0.3, hi=0.4)
    plaque(c, px_, py_ - 22, 84, 26, ["FERNANDA", "OUR QUEEN · 1987"], 6.5)
    for dx in (-14, 12):
        c.ink(Sh([[(px_ + dx - 6, py_ - 52), (px_ + dx + 6, py_ - 52), (px_ + dx, py_ - 58)]]), (200, 120, 150), lw=1.0, shade=0, hi=0)

    # ---------------- Theta Eta Kappa frat house (brick, vibrating)
    fx0, fx1 = 1130, 1660
    c.ink(Sh([[(fx0 - 30, 300), (fx1 + 30, 300), (fx1 - 20, 250), (fx0 + 20, 250)]]), (60, 40, 70), lw=3.2, shade=0.4, hi=0.2, tex=0.2)
    brick_face(c, fx0, 290, fx1, HOR - 6, seed=6)
    c.ink(Sh([[(fx0 + 80, 300), (fx1 - 80, 300), ((fx0 + fx1) / 2, 170)]]), (240, 236, 226), lw=3.2, shade=0.35, hi=0.3)
    c.ink(Sh([[(fx0 + 120, 290), (fx1 - 120, 290), ((fx0 + fx1) / 2, 196)]]), (170, 64, 74), lw=2.4, shade=0.3)
    c.text((fx0 + fx1) / 2, 256, "ΘΗΚ", 30, (250, 236, 200), stroke=1.5, sc=INK)
    c.ink(rect(fx0 - 10, 296, fx1 + 10, 312), (240, 236, 226), lw=2.6, shade=0.3, hi=0.3)
    party = (190, 90, 255)

    def dancers(cc, x0, y0, x1, y1):
        for k in range(3):
            xx = x0 + (x1 - x0) * (0.2 + k * 0.3)
            cc.ink(ell(xx, y0 + (y1 - y0) * 0.5, (x1 - x0) * 0.08, (y1 - y0) * 0.12), (70, 30, 90), lw=0, shade=0, hi=0, ao=0)
            cc.stroke([(xx, y0 + (y1 - y0) * 0.6), (xx + (k - 1) * 8, y0 + (y1 - y0) * 0.2)], 4, (70, 30, 90), taper=(0, 0.5))
    for k, X in enumerate((1210, 1300, 1490, 1580)):
        lit_window(c, X - 30, 350, X + 30, 430, glass=party if k % 2 else (255, 120, 200), frame=(240, 236, 226), silhouette=dancers, seed=10 + k)
    # bedsheet banner
    ban = blob([(1230, 450), (1560, 446), (1556, 520), (1400, 512), (1236, 524)], 1)
    c.ink(ban, (250, 248, 240), lw=3.0, shade=0.4, sw=14, hi=0.3)
    c.text(1396, 472, "TOGA PARTY", 26, (200, 40, 60), "Italic", angle=1)
    c.text(1396, 500, "TONITE!!", 18, (60, 60, 140), "Italic", angle=1)
    for X in (1236, 1556):
        c.ink(ell(X, 452, 5, 5), (90, 90, 100), lw=1.4)
    # porch + double door (hotspot "Frat house door")
    for X in (fx0 + 40, 1310, 1490, fx1 - 40):
        column(c, X, 540, HOR - 20, 28, (240, 236, 226))
    c.ink(rect(fx0 + 10, 526, fx1 - 10, 546), (240, 236, 226), lw=2.8, shade=0.35, hi=0.3)
    ddx0, ddx1 = 1340, 1460
    c.ink(rect(ddx0 - 16, 560, ddx1 + 16, HOR - 26), (240, 236, 226), lw=2.8, shade=0.4)
    for k in range(2):
        flat_door(c, ddx0 + k * 60, 574, ddx0 + 60 + k * 60, HOR - 26, (90, 50, 40), frame=(110, 60, 50), knob="R" if k == 0 else "L", seed=11 + k)
    c.soft(rect(ddx0, HOR - 34, ddx1, HOR - 26), party, 0.6, 4)
    plaque(c, (ddx0 + ddx1) / 2, 594, 92, 22, ["NO TOGA NO ENTRY"], 7, col=(250, 220, 90))
    bulb(c, (ddx0 + ddx1) / 2, 552, 8, strength=0.45)
    lit_window(c, 1180, 580, 1250, 650, glass=party, frame=(240, 236, 226), seed=14, silhouette=dancers)
    lit_window(c, 1550, 580, 1620, 650, glass=(255, 120, 200), frame=(240, 236, 226), seed=15, silhouette=dancers)
    for k in range(3):
        c.ink(rect(ddx0 - 26 - k * 10, HOR - 8 + k * 14, ddx1 + 26 + k * 10, HOR + 6 + k * 14), (200, 196, 204), lw=2.4, shade=0.3, hi=0.3)
    for k in range(4):                        # "thump" lines
        c.stroke(ell_pts((fx0 + fx1) / 2, 420, (fx1 - fx0) * 0.56 + k * 14, 180 + k * 10, 0, 12, -20, 20), 2.4, (255, 170, 255), opacity=0.45)
        c.stroke(ell_pts((fx0 + fx1) / 2, 420, (fx1 - fx0) * 0.56 + k * 14, 180 + k * 10, 0, 12, 160, 200), 2.4, (255, 170, 255), opacity=0.45)
    hedge(c, fx0 - 10, 1300, HOR + 8, 40, seed=5)
    hedge(c, 1500, 1640, HOR + 8, 40, seed=6)
    for (x_, y_, lie, a) in ((1180, 734, False, 0), (1262, 742, True, 20), (1530, 738, True, -30), (1618, 730, False, 0), (1080, 790, True, 60)):
        red_cup(c, x_, y_, 1.0, lie, a)

    # ---------------- quiz podium between the houses + Speed Daters Live sign
    qx = QUIZ_X
    for X in (qx - 70, qx + 70):
        c.stroke([(X, 748), (X, 480)], 9, INK, taper=(0, 0))
        c.stroke([(X, 748), (X, 480)], 4, (200, 190, 210), taper=(0, 0))
    sign = rrect(qx - 92, 452, qx + 92, 538, 12)
    c.ink(sign, (60, 30, 110), lw=3.0, shade=0.35, hi=0.3)
    for k in range(14):
        a = (k + 0.5) / 14
        bx_ = qx - 88 + a * 176
        c.ink(ell(bx_, 458, 4, 4), (255, 236, 140), lw=1.2)
        c.ink(ell(bx_, 532, 4, 4), (255, 236, 140), lw=1.2)
    c.text(qx, 482, "SPEED DATERS", 17, (255, 236, 120))
    c.text(qx, 512, "LIVE!", 22, (255, 110, 190), "Italic")
    c.glow2(qx, 495, 200, (255, 150, 220), 0.3)
    c.soft(ell(qx, 750, 70, 10), (24, 6, 34), 0.5, 8)
    pod = Sh([[(qx - 56, 620), (qx + 56, 620), (qx + 44, 748), (qx - 44, 748)]])
    c.ink(pod, ("v", (180, 60, 200), (110, 40, 150)), lw=3.0, shade=0.4, hi=0.4, rim=0.2)
    for _ in range(40):
        x_, y_ = rng.uniform(qx - 50, qx + 50), rng.uniform(626, 744)
        c.ink(ell(x_, y_, 1.6, 1.6), (255, 240, 200), lw=0, shade=0, hi=0, ao=0, clip=pod, opacity=0.8)
    c.ink(rect(qx - 66, 606, qx + 66, 624), (240, 200, 80), lw=2.6, shade=0.3, hi=0.5)
    c.ink(ell(qx, 598, 24, 10), (60, 40, 50), lw=2.4)
    c.ink(Sh([ell_pts(qx, 598, 20, 22, 0, 20, 180, 360)]), (230, 40, 50), lw=2.6, shade=0.4, hi=0.6, hw=4)
    c.glow2(qx, 590, 50, (255, 80, 80), 0.3)
    c.ink(ell(qx, 680, 22, 22), (255, 220, 90), lw=2.4, shade=0.3, hi=0.4)
    c.text(qx, 681, "?", 26, (120, 40, 140))
    c.text(qx, 718, "QUIZ", 12, (255, 236, 140))
    bunting2(c, (900, 236), (1190, 236), list("GREEK WEEK"), [(240, 70, 130), (60, 200, 200), (250, 200, 70), (150, 90, 210)], sag=46,
             size=31)

    # ---------------- Fuse Box bar (right edge, dark)
    bx0 = 1690
    c.ink(rect(bx0, 380, W_BG + 20, HOR - 6), (66, 52, 84), lw=3.2, shade=0.3, sw=40, hi=0.15, tex=0.25)
    for yy in np.arange(392, HOR, 15):
        c.stroke([(bx0, yy), (W_BG, yy)], 1.4, (40, 30, 56), opacity=0.5, taper=(0, 0))
    c.ink(rect(bx0 - 10, 370, W_BG + 20, 390), (40, 34, 56), lw=2.8, shade=0.3)
    c.ink(rrect(1716, 410, 1904, 470, 10), (30, 24, 44), lw=3.0, shade=0.2)
    neon_text(c, 1800, 440, "FUSE BOX", 30, (255, 90, 160), on=False)
    c.stroke([(1880, 418), (1866, 444), (1882, 444), (1868, 466)], 3.0, (90, 70, 40))
    flat_door(c, 1750, 500, 1860, HOR - 6, (60, 40, 110), frame=(40, 30, 50), knob="L", seed=16)
    c.ink(ell(1805, 548, 20, 20), (255, 210, 120), lw=3.0, oc=(200, 200, 210), shade=0.2)
    c.glow2(1805, 548, 50, GLOW, 0.4)
    c.ink(rrect(1772, 600, 1838, 624, 4), (250, 246, 230), lw=1.8)
    c.text(1805, 612, "OPEN*", 10, (200, 40, 60))
    c.text(1805, 634, "*WHEN POWERED", 6, (200, 200, 220), "Bold")
    c.ink(rect(1736, HOR - 6, 1874, HOR + 6), (130, 120, 140), lw=2.4, shade=0.3)

    # ---------------- grime, power lines, litter
    for (x_, y_, r_) in ((560, 420, 40), (900, 600, 34), (1200, 330, 50), (1620, 420, 44), (1300, 640, 36), (1760, 640, 40)):
        stain(c, x_, y_, r_, (60, 20, 50), 0.22, drips=2, seed=int(x_))
    crack(c, 940, 320, 120, 100, (150, 70, 110), 2.0, seed=4, branches=2)
    cobweb(c, sx1 - 24, 508, 60, "tr", opacity=0.45)
    cobweb(c, fx0 + 14, 548, 60, "tl", opacity=0.45)
    poster(c, 1700, 580, 60, 80, (255, 230, 120),
           lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.25, "DJ", 14, (200, 40, 90)), p.text(w_ / 2, h_ * 0.5, "DOLLY", 10, (60, 40, 120)),
                              p.text(w_ / 2, h_ * 0.75, "TONIGHT", 7, (60, 40, 120), "Bold")), angle=-6, seed=31, peel="br")
    cable(c, (-20, 236), (1000, 196), sag=70, w=4, col=(30, 20, 46))
    cable(c, (1000, 196), (1940, 250), sag=60, w=4, col=(30, 20, 46))
    cable(c, (-20, 260), (1940, 230), sag=120, w=3, col=(30, 20, 46))
    hanging_cable(c, (1690, 378), 60, sway=10, w=4, col=(40, 30, 60), seed=3)
    for (x_, y_, a) in ((300, 820, 20), (700, 960, -40), (1240, 880, 60), (1500, 1000, 10)):          # leaves + flyers
        c.ink(ell(x_, y_, 10, 5, a), (200, 110, 70), lw=1.6, shade=0.3)
    for (x_, y_, a) in ((560, 860, 15), (1680, 900, -20)):
        c.ink(Sh([rot_pts([(x_ - 18, y_ - 6), (x_ + 18, y_ - 6), (x_ + 18, y_ + 6), (x_ - 18, y_ + 6)], a, x_, y_)]), (250, 240, 200), lw=1.6, shade=0.2)
    for k in range(4):                       # chalk hearts on the sidewalk
        x_, y_ = 860 + k * 44, 800 + (k % 2) * 10
        c.stroke([(x_, y_ + 8), (x_ - 12, y_ - 2), (x_ - 6, y_ - 10), (x_, y_ - 4), (x_ + 6, y_ - 10), (x_ + 12, y_ - 2), (x_, y_ + 8)], 2.2,
                 (255, 200, 230), opacity=0.55, taper=(0, 0))
    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 200, 420, 0.4),
                          ((sx0 + sx1) / 2, 600, 420, 0.35), ((fx0 + fx1) / 2, 480, 520, 0.35, (200, 120, 255)),
                          (QUIZ_X, 500, 220, 0.3, (255, 150, 220)), (1400, 640, 200, 0.3, (200, 120, 255))],
               ambient=0.94, vign=0.55, top_dark=0.2, bottom_dark=0.4, shadow_tint=(80, 40, 130))
    for x_, y_ in lamps:
        c.glow2(x_, y_, 140, GLOW, 0.5)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 60, 1100, 300, seed=61)
        fg_plant(sub, 1880, 1100, 280, seed=62, flip=True)
        fg_bottles(sub, 1620, 1090, 3, 0.8, seed=6)
        # picket fence along the bottom edge (out of focus)
        for X in np.arange(400, 1500, 46):
            sub.ink(Sh([[(X, 1100), (X, 1018), (X + 14, 1004), (X + 28, 1018), (X + 28, 1100)]]), FG, lw=0, shade=0.2, hi=0.2)
        sub.ink(rect(380, 1040, 1520, 1054), FG, lw=0)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_greek_row.png")


LINE_Y = [430]
BEDSHEET_X = 290
FERN_X = 860
QUIZ_X = 1030


# =========================================================================== room props
def keg_tub(c, R, X, Z, s=1.0):
    """A keg standing in a tin tub of ice; returns the label centre."""
    P = R.pt
    R.contact(X - 70, X + 70, Z - 40, Z + 40, 0.5)
    kx, ky = P(X, 0, Z)
    k = R.k(Z) * s
    c.ink(rrect(kx - 44 * k, ky - 150 * k, kx + 44 * k, ky - 30 * k, 18 * k), (200, 204, 216), lw=3.0, shade=0.55, sw=24, hi=0.6, hw=8, rim=0.2)
    for yy in (-130, -90, -50):
        c.stroke([(kx - 44 * k, ky + yy * k), (kx + 44 * k, ky + yy * k)], 3.0, (150, 150, 170), taper=(0, 0))
    c.ink(rect(kx - 8 * k, ky - 170 * k, kx + 8 * k, ky - 148 * k), (90, 90, 100), lw=2.2)
    c.stroke([(kx, ky - 166 * k), (kx + 36 * k, ky - 180 * k), (kx + 54 * k, ky - 150 * k)], 4, (40, 40, 50))
    c.ink(ell(kx + 56 * k, ky - 146 * k, 7 * k, 5 * k), (40, 40, 50), lw=1.6)
    tub = Sh([[(kx - 70 * k, ky - 64 * k), (kx + 70 * k, ky - 64 * k), (kx + 60 * k, ky), (kx - 60 * k, ky)]])
    c.ink(tub, (110, 150, 190), lw=3.0, shade=0.5, sw=18, hi=0.45)
    for j in range(9):
        c.ink(rrect(kx - 64 * k + j * 15 * k, ky - 76 * k + (j % 3) * 4, kx - 48 * k + j * 15 * k, ky - 62 * k + (j % 3) * 4, 4), (220, 240, 255), lw=1.6,
              shade=0.3, hi=0.6)
    c.ink(rrect(kx - 32 * k, ky - 120 * k, kx + 32 * k, ky - 84 * k, 4), (250, 240, 200), lw=2.0, shade=0.2)
    c.text(kx, ky - 108 * k, "THE HARD", 8 * k, (150, 40, 40))
    c.text(kx, ky - 94 * k, "STUFF", 9 * k, (150, 40, 40))
    for j in range(3):
        red_cup(c, kx + 80 * k + j * 22 * k, ky - (2 if j % 2 else 6), 0.9 * k)
    return kx, ky


def speaker_stack(c, x, y_floor, w, h, col=(40, 34, 52)):
    c.soft(ell(x + w / 2, y_floor, w * 0.7, 10), (20, 6, 30), 0.5, 8)
    c.ink(rrect(x, y_floor - h, x + w, y_floor, 6), col, lw=3.0, shade=0.35, hi=0.25, rim=0.15)
    for k, (fy, r) in enumerate(((0.28, 0.3), (0.68, 0.38))):
        cx, cy = x + w / 2, y_floor - h + h * fy
        c.ink(ell(cx, cy, w * r, w * r), (24, 20, 30), lw=2.4, shade=0.3, hi=0.3)
        c.ink(ell(cx, cy, w * r * 0.35, w * r * 0.35), (60, 56, 70), lw=1.8, hi=0.5)


def dancer_silhouette(c, x, y_floor, h, col, arm=1, seed=0):
    """A toga-wearing partier in silhouette (arms up)."""
    rng = random.Random(seed)
    hd = h * 0.13
    c.ink(ell(x, y_floor - h + hd, hd * 0.8, hd), col, lw=0, shade=0, hi=0.2, hw=3, ao=0)
    c.ink(blob([(x - h * 0.14, y_floor - h * 0.76), (x + h * 0.14, y_floor - h * 0.76), (x + h * 0.15, y_floor - h * 0.4), (x + h * 0.1, y_floor - h * 0.36),
                (x + h * 0.09, y_floor), (x + h * 0.02, y_floor), (x, y_floor - h * 0.3), (x - h * 0.02, y_floor), (x - h * 0.09, y_floor),
                (x - h * 0.1, y_floor - h * 0.36), (x - h * 0.15, y_floor - h * 0.4)], 1), col, lw=0, shade=0, hi=0.2, hw=3, ao=0)
    for sgn in (-1, 1):
        ex, ey = x + sgn * h * 0.2, y_floor - h * (0.92 if arm else 0.55) + rng.uniform(-10, 10)
        c.stroke([(x + sgn * h * 0.11, y_floor - h * 0.72), (x + sgn * h * 0.2, y_floor - h * 0.86), (ex + sgn * h * 0.04, ey - h * 0.06)], h * 0.075, col,
                 taper=(0, 0.2))
        c.ink(ell(ex + sgn * h * 0.04, ey - h * 0.08, h * 0.04, h * 0.04), col, lw=0, shade=0, hi=0, ao=0)
    c.ink(blob([(x - h * 0.15, y_floor - h * 0.6), (x + h * 0.15, y_floor - h * 0.74), (x + h * 0.17, y_floor - h * 0.36),
                (x - h * 0.15, y_floor - h * 0.34)], 1), mix(col, (240, 230, 250), 0.45), lw=0, shade=0, hi=0, ao=0, opacity=0.95)


def disco_ball(c, x, y, r, rope_top=0):
    c.stroke([(x, rope_top), (x, y - r)], 2.4, (60, 60, 70), taper=(0, 0))
    ball = ell(x, y, r, r)
    c.ink(ball, (200, 200, 220), lw=2.6, shade=0.5, sw=r * 0.5, hi=0.5, rim=0.2)
    rng = random.Random(int(x))
    def tiles_(t):
        for yy in np.arange(y - r, y + r, r * 0.2):
            for xx in np.arange(x - r, x + r, r * 0.2):
                col = rng.choice([(255, 255, 255), (170, 170, 200), (255, 150, 230), (140, 230, 255), (120, 120, 150)])
                t.ink(rect(xx + 1, yy + 1, xx + r * 0.2 - 1, yy + r * 0.2 - 1), col, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.85)
    clip_draw(c, ball, tiles_)
    c.ink(ball, (0, 0, 0, 0), lw=2.6, line_only=True)


def sparkles(c, x0, y0, x1, y1, n, seed=0, cols=((255, 160, 240), (150, 230, 255), (255, 255, 220))):
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        col = rng.choice(cols)
        r = rng.uniform(2, 5)
        c.glow2(x, y, r * 7, col, 0.3)
        c.ink(ell(x, y, r, r), hi_col(col, 0.5), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.9)


def side_door(sub, x0, y0, x1, y1, col, sign_lines=None, sign_col=(250, 240, 200), knob="R", seed=0, window=False):
    def sign(cc, cx, cy):
        if not sign_lines:
            return
        w = (x1 - x0) * 0.86
        cc.ink(Sh([rot_pts([(cx - w / 2, cy - 28), (cx + w / 2, cy - 28), (cx + w / 2, cy + 18 + 12 * len(sign_lines)), (cx - w / 2, cy + 18 + 12 * len(sign_lines))],
                           -3, cx, cy)]), sign_col, lw=2.2, shade=0.2)
        for k, t in enumerate(sign_lines):
            cc.text(cx, cy - 10 + k * 18, t, 11 if k == 0 else 9, (170, 30, 60) if k == 0 else (60, 50, 90), angle=-3)
    flat_door(sub, x0, y0, x1, y1, col, frame=(236, 220, 230), knob=knob, sign=sign, seed=seed, window=window)


# =========================================================================== 2. Frat house (party floor)
def paint_frat_house():
    c, R, rng = A1.std_room(2002, back=(330, 250, 1590, 690), light=(0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (176, 50, 110)           # deep raspberry
    LOW = (90, 46, 60)              # dark wood dado

    def ceil(sub):
        plaster_wall(sub, (90, 50, 90), (60, 30, 70), seed=51, w=sub.w, h=sub.h)
        for _ in range(8):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 110), (60, 30, 30), 0.3, 0, rng.randint(0, 99))
        for _ in range(10):     # ping-pong balls stuck in the plaster
            sub.ink(ell(rng.uniform(0, sub.w), rng.uniform(0, sub.h), 7, 7), (250, 250, 240), lw=1.6, shade=0.3)

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (120, 30, 100), 0.25), LOW, 52, low_kind="wood", rail=(230, 180, 80))
        x0, x1 = sub.ax(290), sub.ax(100)
        side_door(sub, x0, sub.by(300), x1, sub.by(0), (40, 140, 150), knob="R", seed=53)
        exit_sign(sub, (x0 + x1) / 2, sub.by(300) - 50, 170, "GREEK ROW")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 54, low_kind="wood", rail=(230, 180, 80))
        x0, x1 = sub.ax(100), sub.ax(290)
        side_door(sub, x0, sub.by(300), x1, sub.by(0), (60, 70, 120), ["BASEMENT", "PLEDGES +", "DUNK ONLY"], knob="L", seed=55)

    def floor(sub):
        planks(sub, (120, 70, 66), 0, 0, sub.w, sub.h, pw=40 * sub.density, seed=57, vertical=True)
        for _ in range(18):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(20, 60), (60, 20, 40), 0.22, 0, rng.randint(0, 99))
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=2002)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 58, chips=6, stains=5, low_kind="wood", rail=(230, 180, 80))
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=58)
    R.ao(0.55)
    R.edges(w=4.0)

    # TOGA banner (a bedsheet nailed to the back wall)
    ban = blob([P(260, 410), P(1000, 414), P(990, 330), P(640, 344), P(270, 326)], 1)
    c.ink(ban, (250, 248, 240), lw=3.0, shade=0.4, sw=16, hi=0.3)
    c.text(*P(630, 372), "TOGA! TOGA! TOGA!", 40, (200, 30, 60), "Italic", angle=-1)
    for X in (270, 990):
        c.ink(ell(*P(X, 404), 5, 5), (90, 90, 100), lw=1.4)
    # frat composite photos (hotspot "Frat photos": back wall, left)
    for r_ in range(2):
        for k in range(3):
            x0, y0 = P(240 + k * 82, 300 - r_ * 74)
            fr = rect(x0, y0, x0 + 66, y0 + 58)
            c.ink(fr, (110, 70, 40), lw=2.6, shade=0.35, hi=0.35)
            c.ink(rect(x0 + 7, y0 + 7, x0 + 59, y0 + 51), (230, 220, 190), lw=1.6, shade=0.2)
            for j in range(3):
                for i in range(4):
                    fx_, fy_ = x0 + 13 + i * 13, y0 + 15 + j * 12
                    c.ink(ell(fx_, fy_, 3.6, 4.2), (150, 110, 90), lw=0.8, shade=0, hi=0)
            c.text(x0 + 33, y0 + 54, str(1912 + (r_ * 3 + k) * 15), 6, (60, 40, 30), "Bold")
    poster(c, *P(70, 330), 100, 130, (40, 40, 70),
           lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.22, "RUSH", 20, (255, 220, 90)), p.text(w_ / 2, h_ * 0.45, "\u0398\u0397\u039a", 16, (255, 120, 180)),
                              p.text(w_ / 2, h_ * 0.7, "FREE ROOT", 9, (200, 230, 255)), p.text(w_ / 2, h_ * 0.84, "BEER!!", 11, (200, 230, 255))),
           angle=3, seed=56, peel="tl")
    # keg in a tub (hotspot "Root beer keg")
    kx, ky = keg_tub(c, R, 140, 90)
    # Fernanda's spot: velvet ropes and a pink rug in a spotlight (her sprite stands here)
    fx_ = FERN_X_FRAT
    fz = R.z_at_y(FERN_FEET_Y)
    fXc = R.x_at(fx_, FERN_FEET_Y)
    rug = [P(fXc + 90 * math.cos(a), 0, fz + 50 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    c.ink(Sh([rug]), (240, 110, 170), lw=2.6, shade=0.2, hi=0.2, tex=0.3)
    for dX in (-120, 120):
        post_b = P(fXc + dX, 0, fz + 30)
        post_t = P(fXc + dX, 90, fz + 30)
        c.stroke([post_b, post_t], 8, INK, taper=(0, 0))
        c.stroke([post_b, post_t], 4, (240, 200, 80), taper=(0, 0))
        c.ink(ell(*post_t, 7, 7), (250, 220, 90), lw=1.8, hi=0.6)
        c.ink(ell(post_b[0], post_b[1], 18, 5), (200, 160, 60), lw=1.8)
    c.stroke([P(fXc - 120, 84, fz + 30), P(fXc, 60, fz + 30), P(fXc + 120, 84, fz + 30)], 6, (190, 30, 60), smooth=2)
    lamp_top = P(fXc, Hb, fz)
    c.ink(Sh([[(lamp_top[0] - 20, lamp_top[1]), (lamp_top[0] + 20, lamp_top[1]), (lamp_top[0] + 26, lamp_top[1] + 34), (lamp_top[0] - 26, lamp_top[1] + 34)]]),
          (50, 46, 60), lw=2.6, shade=0.3)
    c.light_cone((lamp_top[0], lamp_top[1] + 34), (fx_ - 120, FERN_FEET_Y + 20), (fx_ + 120, FERN_FEET_Y + 20), (255, 220, 200), 0.32, 22)
    floor_pool(c, fx_, FERN_FEET_Y + 4, 120, 26, (255, 220, 200), 0.35)
    rug = [P(200 + 380 + 420 * math.cos(a), 0, 380 + 120 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    c.ink(Sh([rug]), (40, 130, 140), lw=3.0, shade=0.15, hi=0.05, tex=0.3)
    rug2 = [P(580 + 370 * math.cos(a), 0, 380 + 100 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    c.ink(Sh([rug2]), (0, 0, 0, 0), lw=5, oc=(230, 180, 80), line_only=True)
    for _ in range(5):
        x_, y_ = P(rng.uniform(300, 860), 0, rng.uniform(300, 460))
        stain(c, x_, y_, rng.uniform(20, 40), (40, 30, 30), 0.25, 0, rng.randint(0, 99))
    # dance floor: light-up tiles on the floor (hotspot "Dance floor")
    cols = [(255, 70, 170), (60, 220, 220), (250, 220, 70), (150, 90, 255)]
    for i in range(6):
        for j in range(4):
            X0, Z0 = 840 + i * 60, 20 + j * 46
            q = [P(X0 + 2, 0, Z0 + 2), P(X0 + 58, 0, Z0 + 2), P(X0 + 58, 0, Z0 + 44), P(X0 + 2, 0, Z0 + 44)]
            col = cols[(i * 3 + j * 5) % 4]
            on = (i + j) % 3 != 0
            c.ink(Sh([q]), col if on else shade_col(col, 0.5), lw=2.0, shade=0.1, hi=0.3, tex=0.1)
            if on:
                c.glow2(sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4, 50, col, 0.18)
    # dancers in togas against the back wall
    for k, X in enumerate((880, 950, 1020, 1090, 1160)):
        x_, y_ = P(X, 0, 4)
        dancer_silhouette(c, x_ + rng.uniform(-10, 10), y_, rng.uniform(190, 245), (46, 20, 70), arm=k % 2 == 0, seed=k)
    speaker_stack(c, *P(790, 0, 10), 70, 170)
    speaker_stack(c, P(1215, 0, 10)[0], P(1215, 0, 10)[1], 70, 170)
    # breaker box (back wall, right corner)
    bx0, by0 = P(1170, 300)
    bx1, by1 = P(1240, 200)
    c.ink(rect(bx0, by0, bx1, by1), (150, 156, 170), lw=3.0, shade=0.45, sw=14, hi=0.4)
    c.ink(rect(bx0 + 6, by0 + 18, bx1 - 6, by1 - 6), (110, 116, 130), lw=2.0, shade=0.2)
    for k in range(4):
        cx_, cy_ = bx0 + 20 + (k % 2) * 30, by0 + 40 + (k // 2) * 30
        c.ink(ell(cx_, cy_, 9, 9), (230, 200, 120) if k else (250, 220, 90), lw=1.8, shade=0.3, hi=0.5)
    c.text((bx0 + bx1) / 2, by0 + 10, "MAIN", 8, (40, 30, 30))
    cable(c, ((bx0 + bx1) / 2, by0), P(1240, Hb, 0), sag=10, w=5, col=(40, 30, 50))
    # ceiling: disco ball, spot rig, string lights, cables
    db_x, db_y = P(1020, Hb - 120, 160)
    disco_ball(c, db_x, db_y, 34, rope_top=P(1020, Hb, 160)[1])
    for (dx, dy, col) in ((-300, 300, (255, 120, 220)), (260, 340, (120, 220, 255)), (-120, 420, (255, 240, 160))):
        c.light_cone((db_x, db_y), (db_x + dx - 60, db_y + dy), (db_x + dx + 60, db_y + dy), col, 0.16, 18)
    string_lights2(c, [P(0, 420, 0), P(420, 400, 0), P(840, 418, 0), P(Wb, 400, 0)], sag=30, seed=9)
    pipe(c, [P(0, Hb - 26, 0), P(Wb, Hb - 26, 0)], w=18, col=(150, 120, 160), brackets=[P(300, Hb - 26), P(900, Hb - 26)])
    cable(c, P(0, Hb, 200), P(800, Hb, 300), sag=70, w=7, col=(40, 30, 70))
    hanging_cable(c, P(350, Hb, 220), 150, sway=-18, w=6, col=(40, 120, 130), seed=6)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    sparkles(c, 1100, 250, 1700, 560, 22, seed=3)
    for (x_, y_, lie, a) in ((560, 780, True, 30), (1300, 830, True, -20), (760, 900, True, 70), (1560, 760, False, 0)):
        red_cup(c, x_, y_, 1.2, lie, a)
    room_grade(c, lights=[(fx_, FERN_FEET_Y - 120, 300, 0.4, (255, 220, 200)), (db_x, db_y + 300, 600, 0.35, (230, 140, 255)),
                          (P(1000, 0, 100)[0], 720, 420, 0.3, (255, 100, 200)), (kx, ky - 80, 200, 0.2)],
               ambient=0.9, vign=0.6, top_dark=0.4, bottom_dark=0.35)
    c.glow2(db_x, db_y, 90, (255, 230, 255), 0.4)
    c.painterly(0.05)

    def fg(sub):
        fg_chair_back(sub, 1820, 900, 360, 300)
        fg_bottles(sub, 60, 1080, 4, 1.0, seed=7)
        fg_cable(sub, [(400, 1100), (700, 1060), (1000, 1090)], 16)
        fg_lamp_top(sub, 300, 60, 360)
        sub.ink(rect(1300, 1030, 1560, 1100), FG, lw=0, shade=0.2, hi=0.2)       # a cooler
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_frat_house.png")


FERN_FEET_Y = 705          # Fernanda stands at the same depth in both rooms (her sprite is painted for it)
FERN_X_FRAT = 900


# =========================================================================== 3. The Fuse Box (bar with the power out)
def candle(c, x, y, h=26, lit=True):
    c.ink(rrect(x - 6, y - h, x + 6, y, 3), (250, 240, 220), lw=2.0, shade=0.4, hi=0.4)
    c.ink(blob([(x - 5, y - h + 4), (x, y - h - 2), (x + 5, y - h + 4), (x + 3, y - h + 14), (x - 3, y - h + 14)], 1), (240, 236, 214), lw=0, shade=0, hi=0)
    if lit:
        c.ink(blob([(x, y - h - 22), (x + 5, y - h - 8), (x, y - h - 2), (x - 5, y - h - 8)], 1), (255, 220, 110), lw=1.4, oc=(220, 120, 40), shade=0, hi=0)
        c.glow2(x, y - h - 10, 70, GLOW, 0.5)


def paint_fuse_box():
    c, R, rng = A1.std_room(2003, back=(330, 250, 1590, 690), light=(-0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (126, 60, 150)          # purple-painted brick
    LOW = (70, 40, 90)

    def brick_wall(sub, seed, chips=3):
        rng2 = random.Random(seed)
        w, h = sub.w, sub.h
        grunge_wall(sub, w, h, WALL, seed=seed, chips=0, stains=5, floor_y=h)
        bw, bh = 60 * sub.density, 26 * sub.density
        for r_ in range(int(h / bh) + 1):
            y = r_ * bh
            sub.stroke([(0, y), (w, y)], 1.6, shade_col(WALL, 0.6), taper=(0, 0), opacity=0.55)
            off = (r_ % 2) * bw / 2
            for x in np.arange(-off, w, bw):
                sub.stroke([(x, y), (x, y + bh)], 1.4, shade_col(WALL, 0.6), taper=(0, 0), opacity=0.5)
        for _ in range(chips):
            chip(sub, rng2.uniform(0, w), rng2.uniform(0.1, 0.8) * h, rng2.uniform(20, 36), BRICK, MORTAR, WALL, seed=rng2.randint(0, 999))
        sub.ink(rect(-4, h * 0.74, w + 4, h), LOW, lw=0, shade=0, hi=0, ao=0, tex=0.15, wob=0)
        sub.ink(rect(-4, h * 0.74 - 10, w + 4, h * 0.74 + 6), (40, 170, 170), lw=2.4, shade=0.4, hi=0.4)
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)
        skirting(sub, w, h, col=(40, 30, 50))

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (60, 46, 70), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        for k in range(1, 10):
            y = sub.by(k * 90)
            sub.stroke([(0, y), (sub.w, y)], 4, (36, 26, 46), opacity=0.6, taper=(0, 0))

    def left(sub):
        brick_wall(sub, 61)
        x0, x1 = sub.ax(290), sub.ax(100)
        side_door(sub, x0, sub.by(300), x1, sub.by(0), (60, 40, 110), knob="R", seed=62, window=True)
        exit_sign(sub, (x0 + x1) / 2, sub.by(300) - 50, 170, "GREEK ROW")

    def right(sub):
        brick_wall(sub, 63)
        x0, x1 = sub.ax(80), sub.ax(300)
        poster(sub, (x0 + x1) / 2, sub.by(250), 150, 190, (30, 30, 50),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.16, "TONIGHT", 12, (120, 230, 220)), p.text(w_ / 2, h_ * 0.34, "DJ DOLLY", 18, (255, 90, 190)),
                                  p.text(w_ / 2, h_ * 0.5, "SPARK", 22, (255, 230, 90)),
                                  p.ink(ell(w_ / 2, h_ * 0.72, w_ * 0.2, w_ * 0.2), (24, 20, 30), lw=1.6),
                                  p.ink(ell(w_ / 2, h_ * 0.72, w_ * 0.06, w_ * 0.06), (255, 90, 190), lw=1.0)), angle=-3, seed=64, peel="br")

    def floor(sub):
        tiles(sub, (70, 56, 80), (110, 70, 110), 0, 0, sub.w, sub.h, size=70 * sub.density, seed=65, chipped=0.12)
        for _ in range(16):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(20, 60), (40, 20, 40), 0.25, 0, rng.randint(0, 99))
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=2003)

    def back(sub):
        brick_wall(sub, 66, chips=4)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=66)
    R.ao(0.55)
    R.edges(w=4.0)

    # unlit neon signs on the back wall
    neon_text(c, *P(260, 362), "BAR", 46, (80, 230, 230), on=False)
    neon_text(c, *P(985, 362), "DANCE", 44, (255, 90, 190), on=False, angle=-3)
    c.stroke([P(1080, 392), P(1062, 360), P(1084, 360), P(1066, 328)], 5, shade_col((255, 220, 90), 0.5))
    # back-bar shelves with bottles behind the counter
    for k, Y in enumerate((300, 230)):
        y_ = P(60, Y)[1]
        x0_, x1_ = P(40, Y)[0], P(460, Y)[0]
        shelf(c, x0_, x1_, y_, 16, (110, 70, 60))
        x = x0_ + 14
        while x < x1_ - 20:
            h_ = rng.uniform(34, 56)
            w_ = rng.uniform(12, 18)
            col = rng.choice([(80, 170, 90), (200, 120, 50), (90, 120, 220), (220, 200, 120), (160, 60, 120)])
            c.ink(blob([(x, y_), (x, y_ - h_ * 0.6), (x + w_ * 0.35, y_ - h_ * 0.75), (x + w_ * 0.35, y_ - h_), (x + w_ * 0.65, y_ - h_),
                        (x + w_ * 0.65, y_ - h_ * 0.75), (x + w_, y_ - h_ * 0.6), (x + w_, y_)], 1), col, lw=1.8, shade=0.4, hi=0.5, hw=2)
            x += w_ + rng.uniform(3, 8)
    # bar counter (hotspot "Bar counter")
    R.contact(20, 470, 40, 150, 0.6)
    R.ink_box(20, 470, 0, 110, 40, 150, (130, 70, 50), top=(170, 100, 70), side=(90, 50, 40), seed=67)
    for X in np.arange(60, 470, 70):
        c.stroke([P(X, 100, 150), P(X, 8, 150)], 2.0, (90, 46, 36), taper=(0, 0), opacity=0.7)
    c.ink(Sh([[P(20, 110, 150), P(470, 110, 150), P(470, 118, 156), P(20, 118, 156)]]), (190, 120, 80), lw=2.4, shade=0.3, hi=0.4)
    cands = []
    for X, Z in ((80, 110), (230, 100), (400, 116)):
        x_, y_ = P(X, 110, Z)
        candle(c, x_, y_, 24)
        cands.append((x_, y_ - 34))
    tx, ty = P(320, 110, 120)                     # tip jar
    c.ink(rrect(tx - 18, ty - 46, tx + 18, ty, 6), (190, 220, 230, 170), lw=2.2, shade=0.2, hi=0.6)
    c.ink(rect(tx - 14, ty - 22, tx + 14, ty - 6), (250, 240, 200), lw=1.2)
    c.text(tx, ty - 14, "TIPS 4 FUSES", 4.5, (150, 40, 40), "Bold")
    bx_, by_ = P(150, 110, 110)                   # blender (dead)
    c.ink(rect(bx_ - 16, by_ - 18, bx_ + 16, by_), (60, 60, 70), lw=2.2, shade=0.3)
    c.ink(Sh([[(bx_ - 16, by_ - 18), (bx_ + 16, by_ - 18), (bx_ + 20, by_ - 66), (bx_ - 20, by_ - 66)]]), (200, 230, 240, 160), lw=2.2, shade=0.2, hi=0.5)
    c.ink(rect(bx_ - 22, by_ - 74, bx_ + 22, by_ - 64), (60, 60, 70), lw=2.0)
    for k in range(3):                            # bar stools
        X = 90 + k * 140
        x_, y_ = P(X, 0, 210)
        top_ = P(X, 80, 210)
        c.stroke([(x_, y_), top_], 8, INK, taper=(0, 0))
        c.stroke([(x_, y_), top_], 4, (150, 150, 170), taper=(0, 0))
        c.ink(ell(x_, y_, 26, 7), (60, 60, 70), lw=2.0)
        c.ink(ell(top_[0], top_[1], 34, 11), (220, 50, 90), lw=2.6, shade=0.4, hi=0.4)
    # fuse panel (hotspot "Fuse panel"): grey box, door open, dead fuse
    fx0, fy0 = P(500, 290)
    fx1, fy1 = P(590, 170)
    c.ink(rect(fx0, fy0, fx1, fy1), (150, 156, 170), lw=3.0, shade=0.45, sw=14, hi=0.4)
    c.ink(rect(fx0 + 8, fy0 + 10, fx1 - 8, fy1 - 10), (70, 76, 90), lw=2.0, shade=0.2)
    c.ink(ell((fx0 + fx1) / 2, (fy0 + fy1) / 2, 14, 14), (40, 30, 30), lw=2.0, shade=0.2)
    c.ink(ell((fx0 + fx1) / 2, (fy0 + fy1) / 2, 8, 8), (20, 16, 16), lw=1.0)
    c.soft(ell((fx0 + fx1) / 2 + 6, (fy0 + fy1) / 2 - 14, 18, 12), (20, 10, 10), 0.4, 4)
    c.ink(Sh([[(fx0, fy0), (fx0 - 34, fy0 + 10), (fx0 - 34, fy1 + 6), (fx0, fy1)]]), (170, 176, 190), lw=2.6, shade=0.4, hi=0.3)
    c.text(fx0 - 17, (fy0 + fy1) / 2, "30A", 9, (60, 40, 40), angle=80)
    cable(c, ((fx0 + fx1) / 2, fy0), P(545, Hb, 0), sag=6, w=6, col=(40, 30, 50))
    # request chalkboard (hotspot "Request board")
    bx0, by0 = P(650, 340)
    bx1, by1 = P(810, 150)
    c.ink(rect(bx0 - 12, by0 - 12, bx1 + 12, by1 + 12), (130, 80, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(bx0, by0, bx1, by1), (40, 56, 50), lw=2.0, shade=0.2, tex=0.3)
    for k, (t, sz, col) in enumerate((("DJ DOLLY", 15, (255, 140, 200)), ("SPARK", 17, (255, 140, 200)), ("TONIGHT!", 11, (250, 250, 240)),
                                       ("requests welcome", 8, (230, 230, 220)), ("Dolly's #1 fave:", 8, (230, 230, 220)),
                                       ("DISCO VOLCANO", 11, (255, 220, 90)))):
        c.text((bx0 + bx1) / 2, by0 + 20 + k * 27, t, sz, col, "Bold" if sz < 10 else "Black")
    c.stroke([(bx0 + 20, by1 - 20), (bx1 - 20, by1 - 22)], 1.6, (240, 240, 230), opacity=0.6)
    c.ink(rect(bx0 + 10, by1 + 4, bx0 + 40, by1 + 10), (250, 250, 240), lw=1.2)
    # DJ booth (hotspot "DJ booth"): table with a skirt, two turntables, a sticker laptop
    R.contact(840, 1100, 40, 140, 0.6)
    f = R.ink_box(840, 1100, 0, 100, 40, 140, (50, 40, 70), top=(70, 60, 90), seed=68)
    fr = f["front"]
    cx_, cy_ = sum(p[0] for p in fr) / 4, sum(p[1] for p in fr) / 4
    c.text(cx_, cy_, "DJ DOLLY", 26, (110, 80, 140), "Italic")
    for X in (880, 1000):
        tt = R.box(X, X + 80, 100, 110, 70, 130)
        c.ink(Sh([tt["top"]]), (40, 40, 50), lw=2.4, shade=0.2, hi=0.3)
        c.ink(Sh([tt["front"]]), (30, 30, 40), lw=2.0)
        x_, y_ = P(X + 40, 110, 100)
        c.ink(ell(x_, y_, 30, 9), (20, 20, 26), lw=2.0, hi=0.4)
        c.ink(ell(x_, y_, 6, 2), (255, 90, 160), lw=0.8)
    lx_, ly_ = P(970, 112, 80)
    c.ink(Sh([[(lx_ - 34, ly_), (lx_ + 34, ly_), (lx_ + 30, ly_ - 46), (lx_ - 30, ly_ - 46)]]), (190, 190, 210), lw=2.4, shade=0.3, hi=0.4)
    for k, col in enumerate(((255, 90, 160), (90, 220, 220), (255, 220, 80), (150, 90, 255))):
        c.ink(ell(lx_ - 18 + k * 12, ly_ - 32 + (k % 2) * 12, 5, 4), col, lw=1.0)
    cable(c, P(1060, 60, 140), P(1170, 0, 160), sag=-10, w=4, col=(30, 30, 40))
    # Big Bertha (hotspot): an amp the size of a fridge, right-hand back corner
    R.contact(1110, 1250, 30, 130, 0.6)
    f = R.ink_box(1110, 1250, 0, 330, 30, 130, (40, 36, 52), side=(30, 26, 40), seed=69)
    fr = f["front"]
    (ax0, ay0), (ax1, _), (_, ay1) = fr[0], fr[1], fr[2]
    for k, (fy, rr) in enumerate(((0.62, 0.36), (0.32, 0.26))):
        cx_, cy_ = (ax0 + ax1) / 2, ay0 + (ay1 - ay0) * fy
        c.ink(ell(cx_, cy_, (ax1 - ax0) * rr, (ax1 - ax0) * rr), (22, 20, 28), lw=2.6, shade=0.3, hi=0.3)
        c.ink(ell(cx_, cy_, (ax1 - ax0) * rr * 0.36, (ax1 - ax0) * rr * 0.36), (60, 56, 70), lw=2.0, hi=0.5)
    c.ink(rect(ax0 + 10, ay0 + 10, ax1 - 10, ay0 + 44), (60, 54, 70), lw=2.0)
    for k in range(6):
        c.ink(ell(ax0 + 24 + k * (ax1 - ax0 - 48) / 5, ay0 + 27, 5, 5), (200, 200, 210), lw=1.2, hi=0.5)
    c.text((ax0 + ax1) / 2, ay0 + 60, "BIG BERTHA", 16, (255, 120, 120), "Italic")
    cable(c, ((ax0 + ax1) / 2, ay1 - 10), P(980, 0, 200), sag=-6, w=6, col=(30, 30, 40))
    # unlit string lights + mirror ball, pipes
    string_lights2(c, [P(0, Hb - 10, 120), P(420, Hb - 30, 160), P(840, Hb - 20, 160), P(Wb, Hb - 10, 120)], sag=40, glow=False,
                   colors=((120, 90, 110), (110, 100, 90), (80, 110, 110), (100, 90, 130)), seed=5)
    disco_ball(c, *P(720, 420, 300), 30, rope_top=P(720, Hb, 300)[1])
    pipe(c, [P(0, Hb - 30, 0), P(Wb, Hb - 30, 0)], w=22, col=(120, 110, 140), brackets=[P(300, Hb - 30), P(900, Hb - 30)])
    pipe(c, [P(200, Hb, 160), P(200, Hb - 40, 160), P(Wb, Hb - 40, 160)], w=30, col=(150, 150, 170))
    hanging_cable(c, P(980, Hb, 240), 160, sway=14, w=6, col=(40, 30, 60), seed=4)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 110, "tr")
    # a tea light trail on the floor + a flashlight
    for k in range(4):
        x_, y_ = P(560 + k * 80, 0, 260 + (k % 2) * 30)
        candle(c, x_, y_, 14)
        cands.append((x_, y_ - 20))
    x_, y_ = P(760, 0, 340)
    c.ink(rrect(x_ - 30, y_ - 14, x_ + 20, y_, 5), (240, 200, 60), lw=2.2, shade=0.4, hi=0.4)
    c.light_cone((x_ + 20, y_ - 7), (x_ + 220, y_ - 70), (x_ + 220, y_ + 60), (255, 240, 200), 0.18, 16)
    lights = [(x_, y_ - 60, 200, 0.6) for (x_, y_) in cands]
    room_grade(c, lights=lights + [(P(Wb, 300, 200)[0], 520, 300, 0.2, (120, 140, 255)), (960, 300, 500, 0.1, (180, 120, 255))],
               ambient=0.86, vign=0.66, top_dark=0.45, bottom_dark=0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1700, 1090, 4, 1.0, seed=8)
        fg_chair_back(sub, 120, 930, 340, 280)
        fg_table_edge(sub, 700, 1200, 1030, 120)
        fg_cable(sub, [(1250, 1100), (1450, 1050), (1650, 1100)], 14)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_fuse_box.png")


# =========================================================================== 4. Sorority parlor
def wallpaper(sub, w, h, base, seed=0):
    """Faded rose-stripe wallpaper with a few stains and one peeling seam."""
    rng = random.Random(seed)
    grunge_wall(sub, w, h, base, seed=seed, chips=3, stains=3, floor_y=h)
    step = 70 * getattr(sub, "density", 1.0)
    for x in np.arange(step / 2, w, step):
        sub.stroke([(x, 0), (x, h)], 6, hi_col(base, 0.25), taper=(0, 0), opacity=0.5)
        for y in np.arange((x / step % 2) * step * 0.5, h, step):
            sub.ink(ell(x + step * 0.5, y, 7, 7), (230, 80, 130), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.6)
            sub.ink(ell(x + step * 0.5 - 8, y + 8, 6, 3, 30), (70, 160, 120), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.6)
    x = rng.uniform(w * 0.3, w * 0.7)
    sub.ink(Sh([[(x, 0), (x + 40, 0), (x + 10, 60)]]), shade_col(base, 0.8), lw=1.6, shade=0.3, hi=0.3)


def paint_sorority_parlor():
    c, R, rng = A1.std_room(2004, back=(330, 250, 1590, 690), light=(-0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (230, 130, 180)          # rose pink
    TRIM = (240, 236, 236)
    LOW = (60, 150, 140)            # teal dado

    def ceil(sub):
        plaster_wall(sub, (200, 150, 190), (150, 100, 150), seed=71, w=sub.w, h=sub.h)
        cx_, cy_ = sub.ax(630), sub.by(250)
        for k in range(3):
            sub.stroke(ell_pts(cx_, cy_, 150 + k * 40, 90 + k * 24, 0, 40, 0, 360), 3, (240, 220, 236), opacity=0.6)   # ceiling rose
        for _ in range(4):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 90), (120, 60, 50), 0.2, 0, rng.randint(0, 99))

    def lower(sub):
        y0 = sub.h * 0.6
        wainscot(sub, -6, sub.w + 6, y0, sub.h, LOW, seed=72, panel_w=150 * sub.density)
        sub.ink(rect(-4, y0 - 14, sub.w + 4, y0 + 4), TRIM, lw=2.4, shade=0.4, hi=0.4)
        scuffs(sub, 0, sub.w, sub.h - 10, int(sub.w / 30), seed=73, opacity=0.3, spread=90)
        skirting(sub, sub.w, sub.h, col=TRIM)

    def left(sub):
        wallpaper(sub, sub.w, sub.h, mix(WALL, (170, 80, 140), 0.25), seed=74)
        lower(sub)
        x0, x1 = sub.ax(290), sub.ax(100)
        side_door(sub, x0, sub.by(300), x1, sub.by(0), (230, 80, 140), knob="R", seed=75)
        exit_sign(sub, (x0 + x1) / 2, sub.by(300) - 50, 140, "PORCH")

    def right(sub):
        wallpaper(sub, sub.w, sub.h, hi_col(WALL, 0.04), seed=76)
        lower(sub)
        # a framed photo of Fernanda in her prime + a wall sconce
        x_, y_ = sub.ax(200), sub.by(300)
        sub.ink(rect(x_ - 70, y_ - 90, x_ + 70, y_ + 90), (220, 180, 80), lw=3.0, shade=0.4, hi=0.5)
        sub.ink(rect(x_ - 54, y_ - 74, x_ + 54, y_ + 74), (250, 220, 230), lw=2.0, shade=0.2)
        sub.ink(ell(x_ - 4, y_ + 20, 30, 22), (255, 120, 170), lw=2.0, shade=0.3)
        sub.stroke([(x_ + 16, y_ + 10), (x_ + 24, y_ - 30), (x_ + 10, y_ - 50)], 9, (255, 120, 170))
        sub.text(x_, y_ + 62, "FERNANDA '87", 10, (120, 50, 80))

    def floor(sub):
        planks(sub, (150, 90, 80), 0, 0, sub.w, sub.h, pw=34 * sub.density, seed=77, vertical=False)
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=2004)

    def back(sub):
        wallpaper(sub, sub.w, sub.h, WALL, seed=78)
        lower(sub)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=78)
    R.ao(0.45)
    R.edges(w=4.0)

    # round rug
    rug = [P(630 + 520 * math.cos(a), 0, 260 + 150 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 60, endpoint=False)]
    c.ink(Sh([rug]), (170, 40, 90), lw=3.0, shade=0.15, hi=0.05, tex=0.3)
    rug2 = [P(630 + 470 * math.cos(a), 0, 260 + 128 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 60, endpoint=False)]
    c.ink(Sh([rug2]), (0, 0, 0, 0), lw=5, oc=(240, 200, 90), line_only=True)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        c.ink(ell(*P(630 + 380 * math.cos(a), 0, 260 + 100 * math.sin(a)), 14, 6), (250, 160, 200), lw=1.4, shade=0.1)
    # founder portrait (hotspot "Founder portrait"): oval gilt frame
    px_, py_ = P(170, 300)
    c.ink(ell(px_, py_, 78, 100), (220, 176, 70), lw=3.2, shade=0.45, sw=20, hi=0.6, hw=6)
    c.ink(ell(px_, py_, 62, 84), ("v", (90, 70, 110), (50, 40, 70)), lw=2.4, shade=0.2)
    pc = ell(px_, py_, 62, 84)

    def prudence(t):
        t.ink(blob([(px_ - 44, py_ + 90), (px_ - 36, py_ + 30), (px_, py_ + 18), (px_ + 36, py_ + 30), (px_ + 44, py_ + 90)], 2), (110, 60, 120), lw=2.2,
              shade=0.4)
        t.ink(ell(px_, py_ - 10, 24, 30), (240, 210, 190), lw=2.2, shade=0.4, hi=0.3)
        t.ink(ell(px_, py_ - 50, 20, 16), (200, 200, 216), lw=2.2, shade=0.4, hi=0.4)
        t.ink(blob([(px_ - 26, py_ - 22), (px_ - 22, py_ - 42), (px_, py_ - 44), (px_ + 22, py_ - 42), (px_ + 26, py_ - 22), (px_, py_ - 32)], 1), (200, 200, 216),
              lw=2.0, shade=0.3)
        for s_ in (-1, 1):                                                      # THE eyebrows
            t.stroke([(px_ + s_ * 4, py_ - 16), (px_ + s_ * 14, py_ - 24), (px_ + s_ * 22, py_ - 18)], 4.2, (60, 50, 60), taper=(0.2, 0.4))
            t.ink(ell(px_ + s_ * 10, py_ - 8, 3, 3), INK, lw=0)
        t.stroke([(px_ - 8, py_ + 8), (px_ + 8, py_ + 8)], 2.0, INK)
        neck_beads(t, bez((px_ - 20, py_ + 24), (px_, py_ + 40), (px_ + 20, py_ + 24), 10), 3, (250, 246, 240))
    clip_draw(c, pc, prudence)
    c.ink(pc, (0, 0, 0, 0), lw=2.4, line_only=True)
    plaque(c, px_, py_ + 118, 120, 22, ["PRUDENCE LAMBERT · 1921"], 7)
    # window with heavy drapes (back wall, centre)
    wx0, wy0 = P(520, 380)
    wx1, wy1 = P(760, 150)
    c.ink(rect(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14), TRIM, lw=3.0, shade=0.4, hi=0.3)
    night_sky(c, wx0, wy0, wx1, wy1, seed=7)
    c.stroke([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], 8, TRIM, taper=(0, 0))
    c.stroke([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], 8, TRIM, taper=(0, 0))
    c.ink(rect(wx0 - 30, wy1 + 10, wx1 + 30, wy1 + 26), TRIM, lw=2.6, shade=0.4, hi=0.3)
    for side in (0, 1):
        xa = wx0 - 70 if side == 0 else wx1 - 30
        xb = wx0 + 40 if side == 0 else wx1 + 70
        dr = blob([(xa, wy0 - 40), (xb, wy0 - 40), (xb - (30 if side == 0 else -30), (wy0 + wy1) / 2), (xb - (10 if side == 0 else -10), wy1 + 60),
                   (xa, wy1 + 70)], 1)
        c.ink(dr, (50, 150, 140), lw=3.0, shade=0.55, sw=30, hi=0.4, rim=0.2)
        for k in range(1, 4):
            fx_ = xa + (xb - xa) * k / 4
            c.stroke([(fx_, wy0 - 30), (fx_ + rng.uniform(-8, 8), wy1 + 60)], 2.2, shade_col((50, 150, 140), 0.5), opacity=0.7)
        c.ink(ell((xa + xb) / 2, (wy0 + wy1) / 2 + 10, 20, 8), (240, 200, 90), lw=2.0)
    c.ink(rect(wx0 - 90, wy0 - 60, wx1 + 90, wy0 - 30), (40, 130, 120), lw=3.0, shade=0.4, hi=0.4)       # pelmet
    for k in range(9):
        x_ = wx0 - 80 + k * (wx1 - wx0 + 160) / 8
        c.ink(ell(x_, wy0 - 28, 8, 10), (240, 200, 90), lw=1.6)
    # armchair under the window (Whitlock's throne)
    couch(c, R, 500, 780, 20, 120, col=(130, 70, 170), seed=79, seat_y=52, back_y=140, arm_y=84)
    # tea cart (hotspot "Tea cart")
    R.contact(260, 420, 120, 200, 0.5)
    for Y in (20, 80):
        R.ink_box(260, 420, Y, Y + 8, 120, 200, (210, 214, 226), top=(236, 238, 246), seed=82)
    for X, Z in ((262, 122), (418, 122), (262, 198), (418, 198)):
        c.stroke([P(X, 88, Z), P(X, 6, Z)], 4, (150, 150, 170), taper=(0, 0))
        c.ink(ell(*P(X, 4, Z), 6, 6), (40, 40, 50), lw=1.4)
    tp = P(300, 88, 160)
    c.ink(blob([(tp[0] - 18, tp[1]), (tp[0] - 22, tp[1] - 24), (tp[0], tp[1] - 34), (tp[0] + 22, tp[1] - 24), (tp[0] + 18, tp[1])], 2), (250, 248, 252),
          lw=2.4, shade=0.4, hi=0.5)
    c.stroke([(tp[0] + 20, tp[1] - 18), (tp[0] + 36, tp[1] - 30)], 4, INK)
    c.ink(ell(tp[0], tp[1] - 36, 5, 4), (240, 200, 90), lw=1.2)
    sp = P(370, 88, 160)                                                        # finger sandwiches on a stand
    c.ink(ell(sp[0], sp[1], 30, 7), (250, 248, 252), lw=2.0, shade=0.3)
    for k in range(4):
        x_ = sp[0] - 20 + k * 13
        c.ink(Sh([[(x_ - 6, sp[1] - 4), (x_ + 6, sp[1] - 4), (x_, sp[1] - 18)]]), (250, 230, 190), lw=1.4, shade=0.3)
    c.ink(ell(sp[0], sp[1] - 24, 20, 5), (250, 248, 252), lw=1.8)
    # manners sampler (hotspot "Manners sampler")
    sx0, sy0 = P(800, 330)
    sx1, sy1 = P(900, 220)
    c.ink(rect(sx0 - 12, sy0 - 12, sx1 + 12, sy1 + 12), (220, 176, 70), lw=3.0, shade=0.4, hi=0.5)
    c.ink(rect(sx0, sy0, sx1, sy1), (250, 244, 226), lw=1.6, shade=0.2, tex=0.4)
    c.text((sx0 + sx1) / 2, sy0 + 14, "RULES OF", 8, (190, 60, 110))
    c.text((sx0 + sx1) / 2, sy0 + 26, "THE PARLOR", 8, (190, 60, 110))
    for k in range(4):
        y_ = sy0 + 40 + k * 12
        for x_ in np.arange(sx0 + 12, sx1 - 12, 6):
            c.stroke([(x_, y_), (x_ + 3, y_ - 3)], 1.2, (90, 120, 150), taper=(0, 0), opacity=0.8)
    for k in range(5):
        c.ink(ell(sx0 + 14 + k * 18, sy1 - 10, 4, 4), (230, 80, 130), lw=0.8)
    # grandfather clock
    R.contact(940, 1010, 10, 60, 0.5)
    f = R.ink_box(940, 1010, 0, 280, 10, 60, (110, 60, 50), seed=83)
    fr = f["front"]
    (cx0, cy0), (cx1, _), (_, cy1) = fr[0], fr[1], fr[2]
    c.ink(ell((cx0 + cx1) / 2, cy0 + 40, 26, 26), (250, 244, 226), lw=2.4, shade=0.3, hi=0.4)
    c.stroke([((cx0 + cx1) / 2, cy0 + 40), ((cx0 + cx1) / 2 + 12, cy0 + 28)], 2.4, INK)
    c.stroke([((cx0 + cx1) / 2, cy0 + 40), ((cx0 + cx1) / 2 - 4, cy0 + 22)], 2.0, INK)
    c.ink(rect(cx0 + 14, cy0 + 90, cx1 - 14, cy1 - 40), (60, 30, 30), lw=2.0, shade=0.2)
    c.ink(ell((cx0 + cx1) / 2, cy1 - 70, 12, 12), (240, 200, 90), lw=1.8, hi=0.6)
    # confiscation cabinet (hotspot) with a little display stand on top (the record sprite sits on it)
    R.contact(1040, 1240, 10, 90, 0.6)
    f = R.ink_box(1040, 1240, 0, 330, 10, 90, (120, 70, 60), top=(150, 90, 80), seed=84)
    fr = f["front"]
    (gx0, gy0), (gx1, _), (_, gy1) = fr[0], fr[1], fr[2]
    glass = rect(gx0 + 14, gy0 + 16, gx1 - 14, gy1 - 50)
    c.ink(glass, (70, 60, 90), lw=2.4, shade=0.2)
    for k, yy in enumerate(np.linspace(gy0 + 16, gy1 - 50, 4)[1:-1]):
        c.stroke([(gx0 + 14, yy), (gx1 - 14, yy)], 3.0, (150, 90, 80), taper=(0, 0))
    sh1 = gy0 + 16 + (gy1 - 66 - gy0) / 3
    sh2 = gy0 + 16 + (gy1 - 66 - gy0) * 2 / 3
    sh3 = gy1 - 50
    # top shelf: airhorn + cassette
    c.ink(rrect(gx0 + 24, sh1 - 40, gx0 + 50, sh1 - 2, 4), (230, 40, 50), lw=2.0, shade=0.4, hi=0.4)
    c.ink(Sh([[(gx0 + 50, sh1 - 34), (gx0 + 90, sh1 - 46), (gx0 + 90, sh1 - 4), (gx0 + 50, sh1 - 10)]]), (250, 220, 80), lw=2.0, shade=0.3)
    c.ink(rrect(gx0 + 110, sh1 - 26, gx0 + 164, sh1 - 2, 3), (40, 40, 50), lw=1.8)
    c.ink(rect(gx0 + 116, sh1 - 22, gx0 + 158, sh1 - 12), (250, 240, 200), lw=1.0)
    c.text(gx0 + 137, sh1 - 17, "TOGA x3", 5, (200, 40, 60), "Bold")
    # middle shelf: water-balloon catapult
    c.stroke([(gx0 + 30, sh2 - 4), (gx0 + 80, sh2 - 40), (gx0 + 130, sh2 - 4)], 4, (140, 90, 50))
    c.ink(ell(gx0 + 80, sh2 - 44, 14, 10), (90, 180, 255), lw=1.8, shade=0.3, hi=0.6)
    # bottom shelf: forty-one red cups
    for k in range(11):
        for j in range(2):
            red_cup(c, gx0 + 26 + k * 13 + j * 6, sh3 - 2 - j * 18, 0.7)
    for (x_, y_) in ((gx0 + 60, sh1 - 2), (gx0 + 150, sh2 - 4)):
        c.ink(Sh([rot_pts([(x_ - 10, y_ - 6), (x_ + 10, y_ - 6), (x_ + 10, y_ + 4), (x_ - 10, y_ + 4)], 10, x_, y_)]), (250, 246, 230), lw=1.2)
    c.stroke([(gx0 + 30, gy1 - 60), ((gx0 + gx1) / 2, gy0 + 30)], 10, (255, 255, 255), opacity=0.15)
    c.ink(glass, (0, 0, 0, 0), lw=2.4, line_only=True)
    plaque(c, (gx0 + gx1) / 2, gy1 - 26, 120, 22, ["CONFISCATED"], 9)
    top_ = P(1140, 330, 50)
    c.ink(Sh([[(top_[0] - 30, top_[1]), (top_[0] + 30, top_[1]), (top_[0] + 22, top_[1] - 8), (top_[0] - 22, top_[1] - 8)]]), (220, 176, 70), lw=2.0,
          shade=0.3, hi=0.5)
    c.stroke([(top_[0] + 4, top_[1] - 8), (top_[0] + 18, top_[1] - 60)], 3, (220, 176, 70))
    RECORD_FEET[0] = (top_[0], top_[1] - 4)
    # chandelier + wall sconces
    chx, chy = P(630, Hb - 110, 250)
    c.stroke([P(630, Hb, 250), (chx, chy - 30)], 3, (200, 170, 80))
    c.ink(ell(chx, chy, 90, 18), (220, 180, 80), lw=2.6, shade=0.4, hi=0.5)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        x_, y_ = chx + math.cos(a) * 80, chy + math.sin(a) * 14
        candle(c, x_, y_ - 2, 18)
        c.ink(ell(x_, y_ + 14, 4, 8), (220, 240, 255), lw=1.0, hi=0.6)
    for X in (40,):
        x_, y_ = P(X, 300)
        c.ink(Sh([[(x_ - 12, y_), (x_ + 12, y_), (x_ + 20, y_ - 30), (x_ - 20, y_ - 30)]]), (255, 220, 160), lw=2.0, shade=0.2)
        c.glow2(x_, y_ - 16, 90, GLOW, 0.4)
    pipe(c, [P(0, Hb - 20, 0), P(Wb, Hb - 20, 0)], w=14, col=(240, 220, 236))
    cobweb(c, *P(0, Hb, 0), 90, "tl", opacity=0.4)
    cobweb(c, *P(Wb, Hb, 0), 80, "tr", opacity=0.4)
    room_grade(c, lights=[(chx, chy + 200, 640, 0.45), (P(40, 300)[0], 400, 220, 0.3), (1500, 420, 260, 0.25),
                          ((wx0 + wx1) / 2, (wy0 + wy1) / 2, 260, 0.25, (140, 160, 255))],
               ambient=0.95, vign=0.55, top_dark=0.35, bottom_dark=0.32)
    c.glow2(chx, chy, 160, GLOW, 0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 80, 1100, 320, seed=91)
        fg_chair_back(sub, 1800, 900, 340, 300)
        fg_table_edge(sub, 1100, 1500, 1020, 120)
        # a teapot silhouette on the table edge
        sub.ink(blob([(1240, 1024), (1232, 990), (1260, 970), (1290, 990), (1284, 1024)], 2), FG, lw=0)
        fg_lamp_top(sub, 1500, 50, 300)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_sorority_parlor.png")


RECORD_FEET = [(1440, 372)]


# =========================================================================== 5. Frat basement
def paint_frat_basement():
    c, R, rng = A1.std_room(2005, back=(330, 250, 1590, 690), light=(0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (140, 80, 150)           # painted cinder block
    LOW = (80, 60, 100)

    def blocks(sub, seed):
        w, h = sub.w, sub.h
        grunge_wall(sub, w, h, WALL, seed=seed, chips=2, stains=6, floor_y=h)
        bw, bh = 110 * sub.density, 50 * sub.density
        for r_ in range(int(h / bh) + 1):
            y = r_ * bh
            sub.stroke([(0, y), (w, y)], 2.2, shade_col(WALL, 0.6), taper=(0, 0), opacity=0.6)
            off = (r_ % 2) * bw / 2
            for x in np.arange(-off, w, bw):
                sub.stroke([(x, y), (x, y + bh)], 2.0, shade_col(WALL, 0.6), taper=(0, 0), opacity=0.55)
        sub.ink(rect(-4, h * 0.8, w + 4, h), LOW, lw=0, shade=0, hi=0, ao=0, tex=0.2, wob=0)
        sub.ink(rect(-4, h * 0.8 - 8, w + 4, h * 0.8 + 6), (40, 170, 170), lw=2.4, shade=0.4, hi=0.4)
        rng2 = random.Random(seed)
        for _ in range(4):           # damp patches
            stain(sub, rng2.uniform(0, w), rng2.uniform(h * 0.5, h), rng2.uniform(40, 90), (40, 60, 60), 0.25, drips=0, seed=rng2.randint(0, 99))
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (70, 50, 70), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)

    def left(sub):
        blocks(sub, 81)
        # high basement window (night, a street lamp beyond)
        x0, x1 = sub.ax(300), sub.ax(120)
        y0, y1 = sub.by(420), sub.by(330)
        sub.ink(rect(x0 - 14, y0 - 14, x1 + 14, y1 + 14), (200, 196, 210), lw=3.0, shade=0.4)
        night_sky(sub, x0, y0, x1, y1, seed=4, skyline=False)
        sub.stroke([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 6, (200, 196, 210), taper=(0, 0))
        poster(sub, sub.ax(210), sub.by(230), 170, 90, (250, 250, 240),
               lambda p, w_, h_: (p.ink(rect(0, 0, w_, h_ * 0.3), (60, 100, 200), lw=0), p.text(w_ / 2, h_ * 0.55, "BEER PONG", 16, (40, 40, 80)),
                                  p.text(w_ / 2, h_ * 0.8, "CHAMPS 2019", 11, (200, 40, 60))), angle=-3, seed=82)

    def right(sub):
        blocks(sub, 83)

    def floor(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (110, 104, 120), lw=0, shade=0, hi=0, ao=0, tex=0.35, wob=0)
        for _ in range(40):
            crack(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 120), rng.uniform(0, 180), (70, 60, 80), 1.6, seed=rng.randint(0, 999),
                  branches=1, opacity=0.5)
        for _ in range(24):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 90), (50, 40, 60), 0.25, 0, rng.randint(0, 99))
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=2005)

    def back(sub):
        blocks(sub, 84)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=84)
    R.ao(0.6)
    R.edges(w=4.0)

    # joists across the ceiling + pipes
    for z0 in np.arange(0, 700, 90):
        R.ink_box(0, Wb, Hb - 26, Hb + 1, z0, z0 + 30, (120, 80, 70), side=(80, 50, 50), seed=int(z0))
    pipe(c, [P(0, Hb - 40, 20), P(Wb, Hb - 40, 20)], w=24, col=(190, 120, 80), brackets=[P(300, Hb - 40, 20), P(900, Hb - 40, 20)])
    pipe(c, [P(160, Hb - 70, 0), P(160, 0, 0)], w=18, col=(150, 150, 170))
    # Dunk's couch against the left of the back wall + lava lamp on a crate
    couch(c, R, 20, 360, 10, 110, col=(170, 110, 60), seed=85)
    R.ink_box(380, 450, 0, 70, 10, 70, (170, 120, 70), top=(200, 150, 90), seed=86)
    lx, ly = P(415, 70, 40)
    c.ink(Sh([[(lx - 10, ly), (lx + 10, ly), (lx + 6, ly - 30), (lx + 12, ly - 70), (lx - 12, ly - 70), (lx - 6, ly - 30)]]), (240, 90, 200), lw=2.2, shade=0.3,
          hi=0.6)
    for k in range(3):
        c.ink(ell(lx + rng.uniform(-4, 4), ly - 20 - k * 16, 5, 7), (255, 200, 90), lw=0, shade=0, hi=0, ao=0)
    c.glow2(lx, ly - 40, 120, (240, 90, 220), 0.45)
    # mascot shelf (hotspot): gnome in a grad cap, plaster goat, giant foam finger, empty "RESERVED: FLAMINGO"
    sx0, sy_ = P(60, 300)
    sx1 = P(330, 300)[0]
    shelf(c, sx0, sx1, sy_, 18, (130, 80, 60))
    gx = sx0 + 40
    c.ink(blob([(gx - 18, sy_), (gx - 14, sy_ - 40), (gx, sy_ - 50), (gx + 14, sy_ - 40), (gx + 18, sy_)], 2), (60, 110, 200), lw=2.2, shade=0.4)
    c.ink(ell(gx, sy_ - 56, 10, 10), (250, 200, 170), lw=2.0, shade=0.3)
    c.ink(blob([(gx - 8, sy_ - 50), (gx, sy_ - 36), (gx + 8, sy_ - 50)], 1), (250, 250, 250), lw=1.6)
    c.ink(Sh([[(gx - 16, sy_ - 66), (gx + 16, sy_ - 66), (gx + 10, sy_ - 72), (gx - 10, sy_ - 72)]]), (30, 30, 40), lw=1.8)
    c.ink(Sh([[(gx - 18, sy_ - 72), (gx, sy_ - 78), (gx + 18, sy_ - 72), (gx, sy_ - 66)]]), (30, 30, 40), lw=1.8)
    c.stroke([(gx + 14, sy_ - 72), (gx + 20, sy_ - 60)], 1.6, (250, 210, 80))
    gx2 = sx0 + 110
    c.ink(blob([(gx2 - 26, sy_ - 22), (gx2 + 20, sy_ - 24), (gx2 + 22, sy_ - 40), (gx2 - 20, sy_ - 40)], 2), (236, 230, 220), lw=2.2, shade=0.4)
    for X in (gx2 - 20, gx2 - 8, gx2 + 8, gx2 + 18):
        c.stroke([(X, sy_ - 24), (X, sy_)], 4, (236, 230, 220))
    c.ink(ell(gx2 + 26, sy_ - 46, 12, 10), (236, 230, 220), lw=2.0, shade=0.3)
    c.stroke([(gx2 + 22, sy_ - 54), (gx2 + 14, sy_ - 66)], 3, (200, 190, 170))
    c.stroke([(gx2 + 30, sy_ - 54), (gx2 + 36, sy_ - 66)], 3, (200, 190, 170))
    fx_ = sx0 + 180
    c.ink(blob([(fx_ - 16, sy_), (fx_ - 18, sy_ - 50), (fx_ - 6, sy_ - 58), (fx_ - 4, sy_ - 120), (fx_ + 8, sy_ - 122), (fx_ + 10, sy_ - 60),
                (fx_ + 22, sy_ - 52), (fx_ + 20, sy_)], 1), (250, 200, 50), lw=2.4, shade=0.45, hi=0.4)
    c.text(fx_ + 2, sy_ - 24, "#1", 10, (60, 60, 140))
    tx_ = sx1 - 30
    c.ink(Sh([rot_pts([(tx_ - 22, sy_ - 22), (tx_ + 22, sy_ - 22), (tx_ + 22, sy_ - 4), (tx_ - 22, sy_ - 4)], -6, tx_, sy_ - 12)]), (250, 246, 230), lw=1.4)
    c.text(tx_, sy_ - 16, "RESERVED:", 4.5, (180, 40, 60), "Bold", angle=6)
    c.text(tx_, sy_ - 9, "FLAMINGO", 4.5, (180, 40, 60), "Bold", angle=6)
    # ping-pong table (hotspot) with a net of knotted socks + scoreboard
    R.contact(460, 760, 90, 230, 0.55)
    R.ink_box(460, 760, 76, 86, 90, 230, (40, 140, 90), top=(50, 170, 110), seed=87)
    for X, Z in ((476, 100), (744, 100), (476, 220), (744, 220)):
        c.stroke([P(X, 76, Z), P(X, 0, Z)], 5, INK, taper=(0, 0))
    c.stroke([P(610, 86, 90), P(610, 86, 230)], 3, (250, 250, 240), taper=(0, 0))
    net = [P(610, 86 + 14 * (k % 2), 90 + k * 14) for k in range(11)]
    c.stroke(net, 4, (250, 250, 240), taper=(0, 0))
    for k in range(5):
        x_, y_ = P(610, 100, 100 + k * 28)
        c.ink(ell(x_, y_, 6, 4), rng.choice([(220, 60, 60), (60, 120, 220), (250, 220, 80)]), lw=1.2)
    c.ink(ell(*P(560, 90, 160), 5, 5), (250, 250, 240), lw=1.4)
    for X, col in ((510, (220, 50, 50)), (710, (40, 40, 50))):
        c.ink(ell(*P(X, 90, 200), 14, 9), col, lw=2.0, shade=0.3)
    bx0, by0 = P(470, 330)
    bx1, by1 = P(640, 250)
    c.ink(rect(bx0, by0, bx1, by1), (30, 30, 36), lw=2.6, shade=0.3, hi=0.3)
    c.text((bx0 + bx1) / 2, by0 + 16, "DUNK 4,011", 13, (255, 200, 90))
    c.text((bx0 + bx1) / 2, by0 + 40, "EVERYONE ELSE 3", 9, (120, 230, 220))
    # pledge rules whiteboard (hotspot)
    wx0, wy0 = P(800, 330)
    wx1, wy1 = P(960, 220)
    c.ink(rect(wx0 - 8, wy0 - 8, wx1 + 8, wy1 + 8), (200, 200, 210), lw=2.6, shade=0.4, hi=0.3)
    c.ink(rect(wx0, wy0, wx1, wy1), (250, 250, 250), lw=1.6, shade=0.15)
    c.text((wx0 + wx1) / 2, wy0 + 14, "PLEDGE RULES", 11, (40, 60, 180))
    for k in range(4):
        y_ = wy0 + 32 + k * 15
        c.text(wx0 + 12, y_, "%d." % (k + 1), 8, (40, 60, 180), "Bold")
        c.stroke([(wx0 + 22, y_), (wx1 - 14 - (k * 13) % 30, y_ + 1)], 1.6, (40, 60, 180), opacity=0.8)
    c.text((wx0 + wx1) / 2, wy1 - 10, "RULE 2, MOOSE!", 9, (210, 40, 60), angle=-3)
    # Moose's cot (the sleeping-Moose sprite lies on it)
    R.contact(780, 1000, 140, 230, 0.55)
    R.ink_box(790, 1000, 30, 40, 150, 230, (90, 110, 70), top=(120, 140, 90), seed=88)
    for X, Z in ((796, 156), (994, 156), (796, 224), (994, 224)):
        c.stroke([P(X, 30, Z), P(X - 14, 0, Z)], 4, (60, 60, 70), taper=(0, 0))
        c.stroke([P(X, 30, Z), P(X + 14, 0, Z)], 4, (60, 60, 70), taper=(0, 0))
    COT_TOP[0] = P(895, 40, 195)
    c.ink(blob([P(950, 40, 160), P(996, 40, 162), P(996, 54, 196), P(954, 54, 194)], 1), (240, 236, 220), lw=2.2, shade=0.3)    # thin pillow
    # washer + dryer (hotspot "Dryer"), dryer door open with blue beanies spilling out
    for k, X in enumerate((4,)):        # against the left wall, clear of Moose's cot
        k = 1
        R.contact(X, X + 84, 170, 250, 0.5)
        f = R.ink_box(X, X + 84, 0, 110, 170, 250, (236, 236, 240), side=(180, 180, 196), seed=89 + k)
        fr = f["front"]
        (ax0, ay0), (ax1, _), (_, ay1) = fr[0], fr[1], fr[2]
        cx_, cy_ = (ax0 + ax1) / 2, (ay0 + ay1) / 2 + 8
        c.ink(rect(ax0 + 6, ay0 + 6, ax1 - 6, ay0 + 20), (200, 200, 214), lw=1.6)
        c.ink(ell(ax1 - 16, ay0 + 13, 4, 4), (60, 200, 120) if k == 0 else (40, 40, 50), lw=1.0)
        c.ink(ell(cx_, cy_, 30, 30), (90, 100, 130), lw=2.6, shade=0.3, hi=0.4)
        if k == 1:
            c.ink(ell(cx_, cy_, 22, 22), (20, 20, 30), lw=1.6)
            c.ink(Sh([[(cx_ - 30, cy_ - 30), (cx_ - 72, cy_ - 22), (cx_ - 72, cy_ + 26), (cx_ - 30, cy_ + 30)]]), (200, 210, 230), lw=2.6, shade=0.3, hi=0.4)
            for j in range(5):
                bx_, by_ = cx_ - 10 + j * 14 - 30, ay1 + 6 + (j % 2) * 6
                c.ink(blob([(bx_ - 14, by_), (bx_ - 12, by_ - 14), (bx_, by_ - 18), (bx_ + 12, by_ - 14), (bx_ + 14, by_)], 2), (60, 110, 220), lw=2.0, shade=0.4,
                      hi=0.4)
            for j in range(3):
                bx_, by_ = cx_ - 8 + j * 9, cy_ + 6 - j * 4
                c.ink(ell(bx_, by_, 9, 6), (60, 110, 220), lw=1.4, shade=0.3)
        c.text(cx_, ay0 + 13, "WASH" if k == 0 else "DRY", 6, (60, 60, 80), "Bold")
    # stairs up along the right wall
    for k in range(11):
        Y = 40 + k * 38
        Z0 = 340 - k * 30
        R.ink_box(Wb - 140, Wb, Y - 38, Y, Z0, Z0 + 36, (140, 90, 70), top=(170, 110, 80), seed=90 + k, shade=0.3)
    rail = [P(Wb - 146, 130, 360), P(Wb - 146, Hb + 30, 60)]
    c.stroke(rail, 8, INK, taper=(0, 0))
    c.stroke(rail, 4, (200, 190, 200), taper=(0, 0))
    for k in range(5):
        Z = 360 - k * 70
        Y = 130 + k * 88.6
        c.stroke([P(Wb - 146, Y - 90, Z), P(Wb - 146, Y, Z)], 4, (200, 190, 200), taper=(0, 0))
    sg = P(Wb - 70, 380, 220)
    c.ink(Sh([rot_pts([(sg[0] - 50, sg[1] - 16), (sg[0] + 50, sg[1] - 16), (sg[0] + 50, sg[1] + 16), (sg[0] - 50, sg[1] + 16)], 4, *sg)]), (250, 240, 200), lw=2.0)
    c.text(sg[0], sg[1], "PARTY ↑", 12, (190, 40, 60), angle=-4)
    c.glow2(*P(Wb - 100, Hb, 30), 200, (255, 140, 220), 0.35)     # light from the party upstairs
    # bare bulb, cables, cobwebs, a puddle
    bx_, by_ = P(700, Hb - 150, 300)
    bulb(c, bx_, by_, 11, strength=0.6, cord_from=P(700, Hb - 26, 300))
    c.light_cone((bx_, by_ + 6), (bx_ - 420, 900), (bx_ + 420, 900), strength=0.22, blur_px=34)
    hanging_cable(c, P(300, Hb - 26, 300), 160, sway=-14, w=6, col=(40, 30, 60), seed=8)
    cable(c, P(0, Hb - 26, 300), P(700, Hb - 26, 300), sag=40, w=5, col=(40, 30, 60))
    cobweb(c, *P(0, Hb, 0), 130, "tl")
    cobweb(c, *P(Wb, Hb, 0), 120, "tr")
    hanging_web(c, *P(400, Hb - 26, 100), 90)
    pud = [P(300 + 140 * math.cos(a), 0, 420 + 40 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30, endpoint=False)]
    c.ink(Sh([pud]), (80, 150, 170), lw=2.0, shade=0.1, hi=0.5, hw=6, tex=0.1, opacity=0.7)
    for (x_, y_, lie, a) in ((600, 820, True, 40), (1150, 880, True, -30), (420, 760, False, 0)):
        red_cup(c, x_, y_, 1.1, lie, a)
    room_grade(c, lights=[(bx_, by_ + 200, 700, 0.5), (lx, ly - 40, 260, 0.3, (240, 90, 220)), (P(Wb - 100, Hb, 30)[0], 300, 360, 0.3, (255, 140, 220))],
               ambient=0.9, vign=0.62, top_dark=0.4, bottom_dark=0.35)
    c.glow2(bx_, by_, 120, GLOW, 0.5)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 60, 1090, 5, 1.0, seed=9)
        fg_cable(sub, [(500, 1100), (800, 1050), (1100, 1095)], 16)
        sub.ink(rrect(1500, 1000, 1760, 1120, 10), FG, lw=0, shade=0.2, hi=0.2)          # a laundry basket
        for X in np.arange(1520, 1750, 26):
            sub.stroke([(X, 1010), (X, 1100)], 4, mix(FG, (90, 60, 120), 0.4), opacity=0.6)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_frat_basement.png")


COT_TOP = [(1350, 690)]



# =========================================================================== layout (screen px), written into act2.json by --layout
NPC_REL = {"hs_tess_calloway": 0.92, "hs_chad_thunderclap": 1.02, "hs_dolly_spark": 0.9, "hs_mother_whitlock": 0.84, "hs_moose": 1.12,
           "hs_dunk": 0.97}
BEDSHEET_FEET = (BEDSHEET_X, 680)          # top of the sheet hangs on the clothesline (LINE_Y ~ 431)
SLEEP_MOOSE_FEET = (1289, 704)             # lying on the cot (COT_TOP)
RECORD_XY = (1497, 352)                    # on the little display stand on top of the cabinet

LAYOUT["greek_row"] = dict(
    walk_px=[(30, Y_TOP), (1890, Y_TOP), (1905, 900), (1850, Y_BOT), (70, Y_BOT), (15, 900)],
    hotspots={
        ("To campus", 0): dict(box=(0, 440, 150, 760), stand=(110, 830)),
        ("Bedsheet", 0): dict(sprite="hs_bedsheet", feet=BEDSHEET_FEET, stand=(300, 800)),
        ("Sorority door", 0): dict(box=(596, 500, 744, 705), stand=(670, 800)),
        ("Tess Calloway", 0): dict(npc="hs_tess_calloway", feet=(495, NPC_FEET_Y), stand=(660, 935)),
        ("Flamingo stand", 0): dict(box=(FERN_X - 66, 650, FERN_X + 66, 752), stand=(FERN_X, 800)),
        ("Fernanda", 0): dict(npc="hs_fernanda", feet=(FERN_X, FERN_FEET_Y), w=1.6, stand=(FERN_X, 800)),
        ("Quiz podium", 0): dict(box=(QUIZ_X - 70, 570, QUIZ_X + 40, 752), stand=(QUIZ_X, 800)),
        ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1170, NPC_FEET_Y), stand=(1000, 935)),
        ("Chad Thunderclap", 0): dict(npc="hs_chad_thunderclap", feet=(1590, NPC_FEET_Y), stand=(1430, 935)),
        ("Frat house door", 0): dict(box=(1330, 560, 1470, 705), stand=(1400, 800)),
        ("Fuse Box bar", 0): dict(box=(1720, 400, 1910, 720), stand=(1790, 820)),
    },
    entries={"from_campus": (130, 880), "from_frat": (1400, 840), "from_bar": (1780, 880), "from_parlor": (670, 840)})

LAYOUT["frat_house"] = dict(
    walk_px=[(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)],
    hotspots={
        ("Front door", 0): dict(box=(50, 340, 275, 790), stand=(250, 830)),
        ("Root beer keg", 0): dict(box=(340, 535, 555, 715), stand=(460, 800)),
        ("Frat photos", 0): dict(box=(560, 380, 810, 530), stand=(690, 790)),
        ("Fernanda", 0): dict(npc="hs_fernanda", feet=(FERN_X_FRAT, FERN_FEET_Y), w=1.6, stand=(FERN_X_FRAT, 800)),
        ("Moose", 0): dict(npc="hs_moose", feet=(1090, NPC_FEET_Y), stand=(900, 935)),
        ("Dance floor", 0): dict(box=(1190, 505, 1560, 760), stand=(1360, 800)),
        ("Breaker box", 0): dict(box=(1490, 380, 1580, 500), stand=(1530, 800)),
        ("Basement door", 0): dict(box=(1640, 340, 1885, 790), stand=(1680, 830)),
    },
    entries={"from_row": (290, 880), "from_basement": (1650, 880)})

LAYOUT["fuse_box"] = dict(
    walk_px=[(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)],
    hotspots={
        ("Door", 0): dict(box=(50, 340, 275, 790), stand=(250, 830)),
        ("Bar counter", 0): dict(box=(280, 540, 800, 745), stand=(560, 800)),
        ("Fuse panel", 0): dict(box=(785, 390, 925, 530), stand=(860, 790)),
        ("Request board", 0): dict(box=(960, 330, 1160, 560), stand=(1060, 790)),
        ("DJ booth", 0): dict(box=(1175, 540, 1455, 735), stand=(1300, 800)),
        ("Dolly Spark", 0): dict(npc="hs_dolly_spark", feet=(1560, NPC_FEET_Y), stand=(1390, 935)),
        ("Big Bertha", 0): dict(box=(1455, 340, 1680, 498), stand=(1640, 800)),
    },
    entries={"from_row": (290, 880)})

LAYOUT["sorority_parlor"] = dict(
    walk_px=[(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)],
    hotspots={
        ("Front door", 0): dict(box=(50, 340, 275, 790), stand=(250, 830)),
        ("Founder portrait", 0): dict(box=(420, 285, 580, 520), stand=(500, 790)),
        ("Tea cart", 0): dict(box=(490, 580, 730, 752), stand=(610, 800)),
        ("Mother Whitlock", 0): dict(npc="hs_mother_whitlock", feet=(900, NPC_FEET_Y), stand=(1080, 935)),
        ("Manners sampler", 0): dict(box=(1110, 340, 1250, 490), stand=(1180, 790)),
        ("Confiscation cabinet", 0): dict(box=(1370, 360, 1635, 715), stand=(1500, 800)),
        ("Disco Volcano record", 0): dict(sprite="hs_disco_volcano_record", feet=RECORD_XY, stand=(1500, 800)),
    },
    entries={"from_row": (290, 880)})

LAYOUT["frat_basement"] = dict(
    walk_px=[(200, Y_TOP), (1520, Y_TOP), (1690, 850), (1700, Y_BOT), (220, Y_BOT), (120, 860)],
    hotspots={
        ("Mascot shelf", 0): dict(box=(380, 255, 670, 410), stand=(520, 790)),
        ("Dunk", 0): dict(npc="hs_dunk", feet=(520, NPC_FEET_Y), stand=(700, 935)),
        ("Ping-pong table", 0): dict(box=(735, 590, 1095, 765), stand=(930, 800)),
        ("Pledge rules", 0): dict(box=(1115, 345, 1305, 485), stand=(1210, 790)),
        ("Sleeping Moose", 0): dict(sprite="hs_sleeping_moose", feet=SLEEP_MOOSE_FEET, stand=(1250, 800)),
        ("Dryer", 0): dict(box=(110, 600, 305, 785), stand=(260, 850)),
        ("Stairs up", 0): dict(box=(1485, 250, 1915, 840), stand=(1620, 880)),
    },
    entries={"from_frat": (1640, 900)})


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


def _sprite_size(name):
    return Image.open(os.path.join(OUT_DIR, name + ".png")).size


def write_layout(path=WORLD):
    """Write walkable polygons, hotspot feet / size / standAt and entry positions into act2.json.
    Touches nothing else (ids, names, nodes, items, flags stay as they are)."""
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
                bw = spec.get("w", 1.9) if "npc" in spec else round(w / 100, 2)
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


def composite(room_id, out_dir=None, boxes=True, flags=()):
    """Background + sprites at their feet (unscaled, like the game) + Dex (depth-scaled) at the two front-most
    stand points and the back of the walkable area, with hotspot boxes, stand points and entries.
    flags: show hotspots that need these flags (showWhenFlag) and hide those hidden by them (hideWhenFlag)."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(WORLD))
    room = [r for r in data["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))

    def visible(h):
        if h.get("showWhenFlag") and h["showWhenFlag"] not in flags:
            return False
        if h.get("hideWhenFlag") and h["hideWhenFlag"] in flags:
            return False
        return True
    items = []
    for h in room["hotspots"]:
        if not visible(h):
            continue
        slug = re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx))
    stands = [world_to_px(*h["standAt"]) for h in room["hotspots"] if visible(h)]
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
            if not visible(h):
                continue
            fx, fy = world_to_px(*h["feet"])
            w, hh = h["size"][0] * 100, h["size"][1] * 100
            col = (255, 230, 60, 255) if not (h.get("showWhenFlag") or h.get("hideWhenFlag")) else (120, 200, 255, 255)
            d.rectangle([fx - w / 2, fy - hh, fx + w / 2, fy], outline=col, width=3)
            sx, sy = world_to_px(*h["standAt"])
            d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 80, 80, 255))
            d.text((fx - w / 2 + 4, fy - hh + 4), h["name"], fill=col)
        for e in room.get("entries", []):
            ex, ey = world_to_px(*e["pos"])
            d.rectangle([ex - 6, ey - 6, ex + 6, ey + 6], fill=(80, 160, 255, 255))
        bg.alpha_composite(ov)
    tag = ("_" + "_".join(flags)) if flags else ""
    out = os.path.join(out_dir, "composite_%s%s.png" % (room_id, tag))
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


# flag sets that show the alternative hotspots (Fernanda home, sheet taken, Moose asleep, record taken)
COMPOSITE_FLAGS = {"greek_row": [(), ("fernanda_home", "took_sheet")], "frat_house": [()], "fuse_box": [()], "sorority_parlor": [()],
                   "frat_basement": [(), ("a2_moose_relieved",)]}


def paint_npc(npc):
    return CHAR_FN[npc](height=npc_height(npc))


CHAR_FN = {"hs_tess_calloway": paint_tess_calloway, "hs_chad_thunderclap": paint_chad_thunderclap, "hs_dolly_spark": paint_dolly_spark,
           "hs_mother_whitlock": paint_mother_whitlock, "hs_moose": paint_moose, "hs_dunk": paint_dunk}

ASSETS = {
    **{n: (lambda n=n: paint_npc(n)) for n in CHAR_FN},
    "hs_sleeping_moose": paint_sleeping_moose, "hs_fernanda": paint_fernanda, "hs_bedsheet": paint_bedsheet,
    "hs_disco_volcano_record": paint_disco_volcano_record,
    "bg_greek_row": paint_greek_row, "bg_frat_house": paint_frat_house, "bg_fuse_box": paint_fuse_box,
    "bg_sorority_parlor": paint_sorority_parlor, "bg_frat_basement": paint_frat_basement,
}


def main(argv):
    args = [a.lower() for a in argv[1:]]
    if "--layout" in args:
        write_layout()
        return
    if "--composite" in args:
        rooms = [a for a in args if not a.startswith("--")] or list(LAYOUT)
        for r in rooms:
            for fl in COMPOSITE_FLAGS.get(r, [()]):
                composite(r, flags=fl)
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
