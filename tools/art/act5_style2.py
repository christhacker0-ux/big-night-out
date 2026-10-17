#!/usr/bin/env python3
"""
Big Night Out -- Act 5 (Uptown, the Finals) repainted in "style 2" (see Docs/ART_STYLE.md).

Paints the five Act 5 backgrounds (uptown street, Gallery Pierre, Club Velour, Cafe Snoot terrace,
Velour backstage), the Act 5 characters and the Act 5 prop sprites with tools/art/style2.py, in the
same look as tools/art/act1_style2.py: perspective rooms with grungy, lived-in surfaces, magenta /
teal palette, warm lamp light plus one or two coloured sources per room, dark out-of-focus
foreground framing, and tall (6.5-head) characters standing near the front (feet y ~ 945 px).

Characters from earlier acts (Dex, Roxy Vale) are not repainted here; they are placed at feet y ~ 945
px like in Act 1 so their painted size is right.

This supersedes the Act 5 painters in act5.py (a plain run of act5.py would overwrite these files;
run act5.py only for the Act 5 item icons, e.g. `python3 tools/art/act5.py icon_`).

Usage:  python3 tools/art/act5_style2.py              # paint everything
        python3 tools/art/act5_style2.py mimi uptown  # paint assets whose name contains these words
        python3 tools/art/act5_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into act5.json
        BNO_COMPOSITES=/some/dir python3 tools/art/act5_style2.py --composite [room ids]
                                                      # check images: room + sprites + Dex + hotspot boxes
        BNO_COMPOSITES=/some/dir python3 tools/art/act5_style2.py --sheet
                                                      # contact sheets of the backgrounds and sprites
"""
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style2 import *  # noqa: F401,F403,E402
import act1_style2 as A1  # noqa: E402  (shared room / outfit helpers; importing it paints nothing)
from act1_style2 import (BRICK, MORTAR, clip_draw, exit_sign, facade_windows, flat_door, folds, glasses,  # noqa: E402,F401
                         grunge_wall, hair_strands, lamppost, legs, skirt, skirting, soft_shade, spiky_hair,
                         sprite_grade, two_tone_wall, window_flat, ImageChops_multiply)

DEX_H = 440
Y_TOP, Y_BOT = 762, 975          # walkable area span (px) in every Act 5 room
FEET_Y = 945                      # NPCs stand near the front (world y -4.05)
LAYOUT = {}
JSON_PATH = os.path.join(ROOT, "Assets", "_Project", "World", "act5.json")


def C2(w, h, seed, lw=3.0, light=(0.42, -0.9)):
    return Canvas2(w, h, light=light, lw=lw, seed=seed)


# =========================================================================== character helpers
def stripes_in(c, sh, cols, step, w, angle=0.0, opacity=1.0):
    """Horizontal (or tilted) stripes clipped to shape sh."""
    bx0, by0, bx1, by1 = sh.bbox()
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    L = max(bx1 - bx0, by1 - by0) + 40

    def fn(t):
        y = cy - L
        k = 0
        while y < cy + L:
            t.stroke(rot_pts([(cx - L, y), (cx + L, y)], angle, cx, cy), w, cols[k % len(cols)], taper=(0, 0), wob=0.6,
                     smooth=0, opacity=opacity)
            y += step
            k += 1
    clip_draw(c, sh, fn)


def outline(c, sh, lw=3.0):
    c.ink(sh, (0, 0, 0, 0), lw=lw, line_only=True)


def face_base(b, skin, jaw=1.0, chin=1.0, cheek=1.0, chin_drop=1.0, lw=3.0, rim_col=(255, 170, 160)):
    head = Sh([b.head_pts(jaw=jaw, chin=chin, cheek=cheek, chin_drop=chin_drop)])
    b.c.ink(head, skin, lw=lw, shade=0.5, sw=b.r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=rim_col)
    return head


# =========================================================================== Mimi (the mime)
def paint_mimi(height=372, name="hs_mimi.png"):
    W, Hc = 380, 560
    skin = (250, 236, 226)
    paint_w = (252, 252, 250)
    c = C2(W, Hc, 501)
    b = Body(c, 150, Hc - 14, height, skin=paint_w,
             build=dict(shoulders=0.8, waist=0.72, hips=0.92, limbs=0.8, head=1.08, legs=1.04, neck=1.0, chest=0.9,
                        hand=1.05, foot=0.9),
             pose=dict(arm_n=58, fore_n=52, arm_f=70, fore_f=54, leg_n=-8, shin_n=4, leg_f=12, shin_f=-6, lean=4,
                       head_dx=0.4), seed=5)
    navy, navy_sh = (40, 44, 96), (24, 24, 64)
    stripe_w = (246, 244, 240)
    black, black_sh = (40, 34, 52), (22, 18, 32)
    red = (222, 44, 64)
    glove = (250, 250, 252)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm: raised forward, palm flat on the invisible wall
    c.ink(b.sleeve(False, to_wrist=True, w0=6.6, w1=5.8, cuff=5.0), shade_col(stripe_w, 0.86), lw=2.8, shade=0.3)
    sl = b.sleeve(False, to_wrist=True, w0=6.6, w1=5.8, cuff=5.0)
    stripes_in(c, sl, [shade_col(navy, 0.85)], 9, 4.2)
    outline(c, sl, 2.8)
    b.hand(False, "flat", col=(214, 212, 228), d=(0.15, -1.0), thumb=-1, size=1.05)
    # legs: black trousers, little black slippers
    def shoes(bb, near):
        bb.shoe(near, black if near else black_sh, kind="slipper", length=0.95)
    legs(b, black, w=(7.6, 5.2, 4.6), scol=black_sh, shoe=shoes, folds_col=(80, 70, 100))
    # high-waisted trousers top + red braces
    hips = Sh([b.Ps([(-5.0, b.hip_y + 9), (4.6, b.hip_y + 9), (5.0, b.hip_y - 3), (-5.2, b.hip_y - 3)])])
    c.ink(hips, black, lw=3.0, shade=0.45, scol=black_sh)
    # torso: navy / white striped boat-neck top
    torso = Sh([b.torso_pts(slack=0.3, hem=b.hip_y + 7, flare=-0.4, neck_open=1.0)])
    c.ink(torso, stripe_w, lw=0, shade=0, hi=0, ao=0)
    stripes_in(c, torso, [navy], 10, 4.6, angle=-3)
    soft_shade(c, torso, o=0.3)
    outline(c, torso)
    sy, sx = b.shoulder_y, b.lean_dx
    for x0_, x1_ in ((-3.4, -1.8), (2.4, 3.8)):
        c.stroke(b.Ps([(sx + x0_, sy + 0.4), (x0_ * 0.6 + 0.6, b.hip_y + 9.2)]), 3.6, red, taper=(0, 0))
        c.ink(rrect(*b.P(x0_ * 0.6 + 0.0, b.hip_y + 10.5), *b.P(x0_ * 0.6 + 1.3, b.hip_y + 8.6), 2), (230, 200, 90), lw=1.4)
    # neck (painted white) and head
    c.ink(b.neck_shape(0.85), paint_w, lw=2.6, shade=0.5, sw=6, scol=(210, 206, 226))
    # bob hair behind the head
    back = blob([(hx - r * 1.12, hy + ry * 0.75), (hx - r * 1.2, hy - ry * 0.2), (hx - r * 0.8, hy - ry * 0.95), (hx, hy - ry * 1.05),
                 (hx + r * 0.8, hy - ry * 0.8), (hx + r * 0.2, hy + ry * 0.2), (hx - r * 0.4, hy + ry * 0.95)], 2)
    c.ink(back, (34, 24, 40), lw=3.0, shade=0.4, sw=r * 0.3, hi=0.4, hw=r * 0.15, hcol=(110, 80, 140))
    face_base(b, paint_w, jaw=0.9, chin=0.92, cheek=0.96, rim_col=(220, 210, 255))
    fa = b.face_anchor()
    ex, ey = fa["eye_n"]
    b.cheeks(ex + r * 0.14, ey + ry * 0.44, r * 0.26, (255, 120, 140), 0.45)
    # black mime marks: tear drop under the near eye, sharp brows
    b.eyes(iris=(70, 110, 190), look=(0.4, -0.05), lid=0.05, size=1.08, lashes=1)
    b.brows(col=INK, lift_n=0.22, lift_f=0.2, tilt_n=1.0, tilt_f=0.8, w=r * 0.1, arch=0.12)
    c.ink(blob([(ex - r * 0.02, ey + ry * 0.3), (ex + r * 0.06, ey + ry * 0.5), (ex, ey + ry * 0.62), (ex - r * 0.08, ey + ry * 0.5)], 2),
          (30, 20, 40), lw=1.2, shade=0, hi=0.4, hw=1.5)
    b.nose("button", 0.95)
    b.mouth("o", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.42, r * 0.32, open_col=(170, 20, 50))
    mx, my = fa["mouth"]
    c.ink(ell(mx + r * 0.0, my + ry * 0.02, r * 0.16, r * 0.14), (0, 0, 0, 0), lw=3.2, oc=red, line_only=True)
    b.ear(0.85, col=paint_w)
    # fringe
    fringe = blob([(hx - r * 1.0, hy - ry * 0.1), (hx - r * 0.75, hy - ry * 0.85), (hx + r * 0.1, hy - ry * 1.05), (hx + r * 0.95, hy - ry * 0.7),
                   (hx + r * 1.1, hy - ry * 0.3), (hx + r * 0.6, hy - ry * 0.42), (hx + r * 0.1, hy - ry * 0.36), (hx - r * 0.45, hy - ry * 0.25),
                   (hx - r * 0.6, hy + ry * 0.25)], 2)
    c.ink(fringe, (34, 24, 40), lw=3.0, shade=0.4, sw=r * 0.3, hi=0.45, hw=r * 0.15, hcol=(110, 80, 140))
    # red beret, tilted, with a stalk
    bx, by = hx - r * 0.05, hy - ry * 0.82
    beret = blob([(bx - r * 1.25, by + ry * 0.12), (bx - r * 1.1, by - ry * 0.32), (bx - r * 0.3, by - ry * 0.62), (bx + r * 0.7, by - ry * 0.55),
                  (bx + r * 1.25, by - ry * 0.12), (bx + r * 0.95, by + ry * 0.1), (bx - r * 0.2, by + ry * 0.2)], 2)
    c.ink(beret, red, lw=3.0, shade=0.55, sw=r * 0.3, hi=0.45, hw=r * 0.15, rim=0.2)
    c.stroke([(bx - r * 0.1, by - ry * 0.58), (bx + r * 0.05, by - ry * 0.85)], 4.0, INK, taper=(0, 0.3))
    # near arm: raised, palm flat against nothing
    sl = b.sleeve(True, to_wrist=True, w0=7.0, w1=6.2, cuff=5.4)
    c.ink(sl, stripe_w, lw=0, shade=0, hi=0)
    stripes_in(c, sl, [navy], 9, 4.2)
    soft_shade(c, sl, o=0.25, hi=0.1)
    outline(c, sl)
    b.hand(True, "flat", col=glove, d=(0.1, -1.0), thumb=-1, size=1.1)
    wx, wy = b.P(*b.wrist_n)
    c.ink(rrect(wx - 9, wy - 6, wx + 9, wy + 8, 4), glove, lw=2.4, shade=0.3)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Brutus (bouncer)
def paint_brutus(height=470, name="hs_brutus.png"):
    W, Hc = 480, 660
    skin = (128, 82, 62)
    c = C2(W, Hc, 502, lw=3.2)
    b = Body(c, 220, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.62, waist=1.3, hips=1.25, limbs=1.32, head=0.9, legs=0.98, neck=1.7, chest=2.6, belly=1.2,
                        hand=1.25, foot=1.15),
             pose=dict(arm_n=4, fore_n=96, arm_f=-6, fore_f=8, leg_n=-6, shin_n=2, leg_f=7, shin_f=-3, lean=1,
                       head_dx=1.2, head_dy=-1.0), seed=12)
    tee, tee_sh = (38, 34, 48), (20, 16, 30)
    pants, pants_sh = (52, 50, 66), (28, 26, 40)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (behind the clipboard)
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=3.0, shade=0.4)
    c.ink(b.sleeve(False, 0.5, 8.4, 7.8), shade_col(tee, 0.9), lw=3.0, shade=0.3)
    b.hand(False, "fist", col=shade_col(skin, 0.86), size=1.15)
    # legs: black cargo trousers, boots
    def boots(bb, near):
        bb.shoe(near, (34, 30, 40) if near else (26, 22, 32), (70, 60, 70), "boot", length=1.0)
    legs(b, pants, w=(10.6, 7.8, 7.2), scol=pants_sh, shoe=boots, folds_col=(90, 86, 110))
    for near in (True,):
        kn = b.knee_n
        c.ink(rrect(*b.P(kn[0] - 3.4, kn[1] + 9), *b.P(kn[0] + 2.2, kn[1] + 3), 3), shade_col(pants, 0.8), lw=2.4, shade=0.3)
    # torso: big black SECURITY tee
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=12)
    torso = Sh([b.torso_pts(slack=1.0, hem=b.hip_y - 2.5, flare=0.4, neck_open=1.3)])
    c.ink(torso, tee, lw=3.2, shade=0.5, sw=30, scol=tee_sh, hi=0.25, hcol=(90, 80, 110), rim=0.25, rcol=(150, 110, 220))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 2.4, sy + 1.6), (sx + 3.8, sy + 1.2), (sx + 1.0, sy - 2.6)])]), skin, lw=2.4, shade=0.5)
    c.stroke(b.Ps([(sx - 3.0, sy + 1.4), (sx + 0.6, sy - 3.0), (sx + 4.4, sy + 1.0)]), 3.4, (70, 64, 90), taper=(0, 0))
    tx, ty = b.P(sx * 0.5 + 0.2, sy - 5.2)
    c.label(tx, ty, "SECURITY", 10, (250, 248, 236), mirror=True)
    # belt
    c.ink(Sh([b.Ps([(-6.4, b.hip_y - 1.0), (6.0, b.hip_y - 1.0), (6.0, b.hip_y - 3.6), (-6.4, b.hip_y - 3.6)])]), (24, 20, 30), lw=2.4)
    c.ink(rrect(*b.P(1.0, b.hip_y - 0.8), *b.P(4.0, b.hip_y - 3.8), 2), (190, 190, 200), lw=1.8, shade=0.3, hi=0.6)
    # head: bald, sunglasses at night, earpiece
    face_base(b, skin, jaw=1.3, chin=1.15, cheek=1.08, chin_drop=1.04)
    fa = b.face_anchor()
    c.soft(ell(hx - r * 0.1, hy - ry * 0.55, r * 0.5, ry * 0.2, -15), (255, 230, 210), 0.35, 4)    # scalp shine
    b.brows(col=(30, 18, 20), lift_n=-0.12, lift_f=-0.12, tilt_n=-0.6, tilt_f=-0.6, w=r * 0.16)
    (ex, ey), (fx_, fy_) = fa["eye_n"], fa["eye_f"]
    lens = (26, 22, 40)
    for (x_, y_, w_) in ((ex, ey, r * 0.42), (fx_, fy_, r * 0.27)):
        sh = rrect(x_ - w_, y_ - r * 0.24, x_ + w_, y_ + r * 0.26, 5)
        c.ink(sh, lens, lw=2.6, shade=0.1, hi=0.0)
        c.stroke([(x_ - w_ * 0.6, y_ + r * 0.12), (x_ - w_ * 0.1, y_ - r * 0.16)], 3.0, (160, 140, 255), opacity=0.7)
    c.stroke([(ex + r * 0.42, ey - r * 0.05), (fx_ - r * 0.27, fy_ - r * 0.05)], 3.0, lens)
    c.stroke([(ex - r * 0.42, ey - r * 0.08), (fa["ear"][0], fa["ear"][1] - r * 0.1)], 3.0, lens)
    b.nose("round", 1.15)
    b.mouth("flat", fa["mouth"][0], fa["mouth"][1] + ry * 0.06, r * 0.5, r * 0.25)
    b.ear(1.0)
    exx, eyy = fa["ear"]
    c.ink(ell(exx - r * 0.18, eyy, r * 0.12, r * 0.14), (40, 40, 50), lw=1.8)
    c.stroke([(exx - r * 0.18, eyy + r * 0.12), (exx - r * 0.3, eyy + r * 0.6), (exx - r * 0.2, eyy + r * 1.1),
              (exx - r * 0.36, eyy + r * 1.7)], 1.8, (220, 220, 230), taper=(0, 0), opacity=0.9)
    # near arm: holding the clipboard against the chest like a shield
    c.ink(b.arm_shape(True), skin, lw=3.2, shade=0.5)
    c.ink(b.sleeve(True, 0.52, 8.8, 8.2), tee, lw=3.2, shade=0.4, sw=10, hi=0.2, hcol=(90, 80, 110))
    wx, wy = b.P(*b.wrist_n)
    wy += 30
    cb = Sh([rot_pts([(wx - 30, wy - 80), (wx + 46, wy - 80), (wx + 46, wy + 30), (wx - 30, wy + 30)], 8, wx, wy)])
    c.ink(cb, (190, 140, 80), lw=3.0, shade=0.4, sw=10, hi=0.3)
    paper = Sh([rot_pts([(wx - 22, wy - 70), (wx + 38, wy - 70), (wx + 38, wy + 22), (wx - 22, wy + 22)], 8, wx, wy)])
    c.ink(paper, (250, 248, 236), lw=2.0, shade=0.2)
    for k in range(6):
        p0, p1 = rot_pts([(wx - 14, wy - 54 + k * 12), (wx + 30 - (k % 3) * 8, wy - 54 + k * 12)], 8, wx, wy)
        c.stroke([p0, p1], 1.6, (90, 90, 130), taper=(0, 0), opacity=0.8)
    c.ink(Sh([rot_pts([(wx - 2, wy - 88), (wx + 20, wy - 88), (wx + 20, wy - 74), (wx - 2, wy - 74)], 8, wx, wy)]), (200, 200, 210), lw=2.0,
          shade=0.3, hi=0.5)
    b.hand(True, "hold", size=1.2, d=(0.9, -0.3), thumb=1)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Pierre (curator)
def paint_pierre(height=400, name="hs_pierre.png"):
    W, Hc = 380, 600
    skin = (246, 214, 192)
    c = C2(W, Hc, 503)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.82, waist=0.78, hips=0.82, limbs=0.78, head=1.02, legs=1.1, neck=1.15, chest=0.4,
                        hand=0.9, foot=1.1),
             pose=dict(arm_n=12, fore_n=104, arm_f=2, fore_f=8, leg_n=-3, shin_n=1, leg_f=6, shin_f=-2, lean=-6,
                       head_dx=-0.6, head_dy=0.8), seed=13)
    black, black_sh = (36, 32, 46), (20, 16, 28)
    grey, grey_sh = (120, 118, 136), (76, 72, 96)
    hair, hair_sh, hair_hi = (220, 222, 232), (150, 150, 176), (255, 255, 255)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm folded behind the back (hidden), legs: slim grey trousers, pointy black shoes
    c.ink(b.arm_shape(False), shade_col(black, 0.9), lw=2.8, shade=0.3)

    def shoes(bb, near):
        an = bb.ankle_n if near else bb.ankle_f
        x, y = an
        L = 13.0
        sh = blob(bb.Ps([(x - 2.8, y + 2.0), (x + 2.0, y + 2.4), (x + L * 0.6, y + 0.2), (x + L * 1.12, y - 3.0), (x + L * 0.9, y - 4.3),
                         (x - 2.6, y - 4.3), (x - 3.2, y - 2.0)]), 1)
        c.ink(sh, (30, 26, 36) if near else (24, 20, 30), lw=2.8, shade=0.4, hi=0.6, hw=3)
    legs(b, grey, w=(7.2, 5.0, 4.2), scol=grey_sh, shoe=shoes, folds_col=(80, 78, 100))
    # torso: black turtleneck, slim
    torso = Sh([b.torso_pts(slack=0.3, hem=b.hip_y - 1.0, flare=-0.6, neck_open=0.8)])
    c.ink(torso, black, lw=3.0, shade=0.5, sw=20, scol=black_sh, hi=0.3, hcol=(110, 96, 140), rim=0.25, rcol=(160, 120, 230))
    folds(c, [b.Ps([(-2, b.hip_y + 10), (0.5, b.hip_y + 4)]), b.Ps([(3, b.hip_y + 14), (2.2, b.hip_y + 8)])], (80, 70, 110), 1.6, 0.7)
    # tall turtleneck collar
    nb = b.P(*b.neck_base)
    neck = b.neck_shape(1.0)
    c.ink(neck, skin, lw=2.6, shade=0.6, sw=6)
    col_ = limb([nb, (nb[0] + b.u * 1.6, nb[1] - b.u * 3.6)], [b.u * 7.2, b.u * 6.0], smooth=0, ends=True)
    c.ink(col_, black, lw=2.8, shade=0.4, hi=0.3, hcol=(110, 96, 140))
    for k in range(3):
        c.stroke([(nb[0] - b.u * 2.6, nb[1] - b.u * (0.6 + k * 1.1)), (nb[0] + b.u * 3.6, nb[1] - b.u * (1.2 + k * 1.1))], 1.4,
                 (80, 70, 110), opacity=0.7)
    # head: nose up, tiny glasses, silver quiff
    face_base(b, skin, jaw=0.86, chin=1.15, cheek=0.92, chin_drop=1.06)
    fa = b.face_anchor()
    b.eyes(iris=(90, 110, 140), look=(0.3, -0.35), lid=0.45, size=0.92)
    b.brows(col=hair_sh, lift_n=0.28, lift_f=0.24, tilt_n=-0.4, tilt_f=-0.5, w=r * 0.1, arch=0.14)
    nx, ny = fa["nose"]
    c.ink(blob([(nx - r * 0.24, ny - r * 0.5), (nx + r * 0.2, ny - r * 0.3), (nx + r * 0.58, ny - r * 0.22), (nx + r * 0.2, ny + r * 0.12),
                (nx - r * 0.2, ny + r * 0.12)], 2), skin, lw=c.lw * 0.8, shade=0.45, sw=r * 0.12, hi=0.35, hw=r * 0.06, ao=0)
    c.stroke([(nx - r * 0.02, ny + r * 0.06), (nx + r * 0.12, ny + r * 0.02)], 1.6, INK, taper=(0.2, 0.2), smooth=0)
    b.mouth("smirk", fa["mouth"][0] - r * 0.04, fa["mouth"][1] + ry * 0.02, r * 0.4, r * 0.18)
    glasses(b, col=(30, 26, 40), size=0.7, lw=2.2)
    b.ear(0.92)
    quiff = blob([(hx - r * 1.02, hy + ry * 0.35), (hx - r * 1.12, hy - ry * 0.45), (hx - r * 0.7, hy - ry * 1.05), (hx + r * 0.1, hy - ry * 1.45),
                  (hx + r * 1.15, hy - ry * 1.62), (hx + r * 0.95, hy - ry * 1.12), (hx + r * 0.85, hy - ry * 0.7), (hx + r * 0.4, hy - ry * 0.55),
                  (hx - r * 0.1, hy - ry * 0.45), (hx - r * 0.45, hy + ry * 0.0), (hx - r * 0.6, hy + ry * 0.4)], 2)
    c.ink(quiff, hair, lw=3.0, shade=0.5, sw=r * 0.4, scol=hair_sh, hi=0.4, hw=r * 0.2, hcol=hair_hi, rim=0.2, rcol=(200, 190, 255))
    hair_strands(c, [[(hx - r * 0.7, hy - ry * 0.5), (hx, hy - ry * 1.1), (hx + r * 0.9, hy - ry * 1.45)],
                     [(hx - r * 0.9, hy + ry * 0.1), (hx - r * 0.6, hy - ry * 0.8), (hx + r * 0.3, hy - ry * 1.3)]], hair_sh, 1.8)
    # near arm: wine glass raised, pinky out
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=7.4, w1=6.4, cuff=5.6), black, lw=3.0, shade=0.45, sw=10, hi=0.3, hcol=(110, 96, 140))
    wx, wy = b.P(*b.wrist_n)
    gx, gy = wx + 16, wy - 18
    c.stroke([(gx, gy + 6), (gx, gy + 34)], 2.6, (230, 236, 255), taper=(0, 0))
    c.ink(ell(gx, gy + 36, 11, 3.5), (220, 230, 250, 200), lw=1.8, shade=0, hi=0)
    bowl = blob([(gx - 15, gy - 30), (gx + 15, gy - 30), (gx + 13, gy - 8), (gx, gy + 6), (gx - 13, gy - 8)], 2)
    c.ink(bowl, (220, 236, 255, 120), lw=2.2, oc=(60, 50, 90), shade=0, hi=0.5, hw=3)
    c.ink(blob([(gx - 12, gy - 14), (gx + 12, gy - 14), (gx + 8, gy - 4), (gx, gy + 2), (gx - 8, gy - 4)], 2), (150, 30, 70), lw=0, shade=0.3,
          hi=0.3, clip=bowl)
    c.stroke([(gx - 8, gy - 24), (gx - 10, gy - 12)], 2.4, (255, 255, 255), opacity=0.8)
    b.hand(True, "hold", size=1.0, d=(0.4, -1.0), thumb=1)
    c.stroke([(wx + 4, wy + 6), (wx + 16, wy + 14), (wx + 24, wy + 12)], 3.2, skin, taper=(0, 0.4))
    c.stroke([(wx + 4, wy + 6), (wx + 16, wy + 14), (wx + 24, wy + 12)], 1.2, INK, taper=(0, 0.4), opacity=0.6)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Jett Vex (bored punk star)
def paint_jett_vex(height=380, name="hs_jett_vex.png"):
    W, Hc = 400, 620
    skin = (238, 196, 176)
    c = C2(W, Hc, 504)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.88, waist=0.72, hips=0.98, limbs=0.84, head=1.04, legs=1.06, neck=1.0, chest=1.0,
                        hand=0.92, foot=1.05),
             pose=dict(arm_n=16, fore_n=82, arm_f=-6, fore_f=14, leg_n=-12, shin_n=6, leg_f=12, shin_f=-2, lean=-6,
                       head_dx=0.6, head_dy=-0.8), seed=14)
    leather, leather_sh, leather_hi = (44, 38, 56), (22, 18, 32), (130, 120, 170)
    pink = (255, 70, 160)
    green, green_sh, green_hi = (90, 236, 110), (30, 150, 80), (200, 255, 190)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm hanging, thumb in the skirt pocket
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.88), size=0.95)
    c.ink(b.sleeve(False, to_wrist=True, w0=8.4, w1=7.6, cuff=7.0), shade_col(leather, 0.9), lw=2.8, shade=0.3)
    # legs: ripped black tights + chunky boots
    tights = (64, 50, 70)

    def boots(bb, near):
        sh = bb.shoe(near, (30, 26, 36) if near else (24, 20, 30), (230, 230, 220), "boot", length=1.1)
        an = bb.ankle_n if near else bb.ankle_f
        for k in range(3):
            c.stroke(bb.Ps([(an[0] - 1.8, an[1] + 9 - k * 2.6), (an[0] + 2.2, an[1] + 9.6 - k * 2.6)]), 1.6, (220, 220, 230), taper=(0, 0))
        c.ink(Sh([bb.Ps([(an[0] - 3.4, an[1] - 4.3), (an[0] + 13, an[1] - 4.3), (an[0] + 13, an[1] - 6.2), (an[0] - 3.4, an[1] - 6.2)])]),
              (230, 230, 220), lw=2.2, shade=0.2)
    legs(b, tights, w=(7.4, 5.0, 4.4), scol=(36, 26, 44), shoe=boots, skin=True)
    for near in (True, False):
        kn = b.knee_n if near else b.knee_f
        x_, y_ = b.P(kn[0] + 0.4, kn[1] + 1.5)
        c.ink(ell(x_, y_, b.u * 1.8, b.u * 1.2, 20), skin, lw=1.8, oc=(30, 20, 30), shade=0.3)
    # pink tartan mini skirt
    sk = skirt(b, pink, b.hip_y - 13, flare=2.6, waist=b.hip_y + 5)

    def tartan(t):
        bx0, by0, bx1, by1 = sk.bbox()
        for x in np.arange(bx0 - 20, bx1 + 20, 18):
            t.stroke([(x, by0 - 10), (x + 10, by1 + 10)], 3.0, (40, 20, 40), taper=(0, 0), opacity=0.8)
        for y in np.arange(by0, by1 + 20, 16):
            t.stroke([(bx0 - 10, y), (bx1 + 10, y)], 2.4, (255, 190, 220), taper=(0, 0), opacity=0.6)
    clip_draw(c, sk, tartan)
    outline(c, sk)
    c.ink(Sh([b.Ps([(-5.6, b.hip_y + 5.6), (5.2, b.hip_y + 5.6), (5.4, b.hip_y + 2.8), (-5.8, b.hip_y + 2.8)])]), (24, 20, 30), lw=2.2)
    for k in range(5):
        c.ink(ell(*b.P(-4.6 + k * 2.3, b.hip_y + 4.2), 2.2, 2.2), (220, 220, 230), lw=1.0, hi=0.6)
    chain = [b.P(-4, b.hip_y + 2), b.P(-2, b.hip_y - 6), b.P(3, b.hip_y - 3)]
    c.stroke(chain, 2.0, (210, 210, 220), taper=(0, 0))
    # torso: pink tee under a cropped leather jacket
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.4, hem=b.hip_y + 4.5, flare=-0.3, neck_open=1.1)])
    c.ink(torso, pink, lw=3.0, shade=0.5, sw=16, hi=0.3)
    sy, sx = b.shoulder_y, b.lean_dx
    bolt = Sh([b.Ps([(sx + 2.2, sy - 6), (sx - 0.4, sy - 12), (sx + 1.6, sy - 12), (sx - 0.6, sy - 18), (sx + 3.6, sy - 10.5),
                     (sx + 1.6, sy - 10.5), (sx + 3.8, sy - 6)])])
    c.ink(bolt, (255, 236, 80), lw=1.8, shade=0.2)
    jk = Sh([b.torso_pts(slack=1.3, hem=b.hip_y + 9, flare=0.6, neck_open=1.6)])
    open_front = Sh([b.Ps([(sx - 0.4, sy + 2), (sx + 4.6, sy + 2), (sx + 5.6 + b.b["chest"], b.hip_y + 7), (sx * 0.4 - 0.8, b.hip_y + 7)])])
    # jacket = torso shape minus the open front strip: paint left and right panels
    for pts in ([(sx - 3.6, sy + 2.2), (sx - 0.2, sy + 1.6), (sx * 0.4 - 0.4, b.hip_y + 8.6), (-5.6, b.hip_y + 8.6), (-5.8, b.hip_y + 15),
                 (b.sh_n[0] + 0.6, sy - 9), (b.sh_n[0] - 1.2, sy - 3), (b.sh_n[0] + 1.0, sy + 0.6)],
                [(sx + 4.6, sy + 1.6), (b.sh_f[0] + 0.8, sy - 0.4), (b.sh_f[0] + 2.4 + b.b["chest"], sy - 6), (5.2, b.hip_y + 15),
                 (5.6, b.hip_y + 8.6), (sx + 5.4, b.hip_y + 8.6)]):
        sh = Sh([chaikin(b.Ps(pts), 1)])
        c.ink(sh, leather, lw=3.0, shade=0.5, sw=14, scol=leather_sh, hi=0.45, hw=5, hcol=leather_hi, rim=0.25, rcol=(170, 130, 255))
    for k in range(4):     # studs on the lapel + safety pins
        c.ink(ell(*b.P(sx - 1.6 - k * 0.3, sy - 2 - k * 3.4), 2.0, 2.0), (230, 230, 240), lw=1.0, hi=0.7)
    for (px_, py_) in ((sx + 6.0, sy - 9), (sx + 6.4, sy - 14)):
        x_, y_ = b.P(px_, py_)
        c.stroke([(x_ - 6, y_ - 2), (x_ + 6, y_ + 2)], 1.8, (230, 230, 240), taper=(0, 0))
        c.ink(ell(x_ - 7, y_ - 2, 2.2, 2.2), (230, 230, 240), lw=0.8)
    c.stroke(b.Ps([(sx + 0.6, sy + 1), (sx * 0.4 + 0.4, b.hip_y + 8)]), 1.4, (200, 200, 210), taper=(0, 0), opacity=0.8)   # zip
    # head
    face_base(b, skin, jaw=0.92, chin=0.95, cheek=0.96)
    fa = b.face_anchor()
    (ex, ey), (fx_, fy_) = fa["eye_n"], fa["eye_f"]
    for (x_, y_), k in (((ex, ey), 1.0), ((fx_, fy_), 0.65)):
        c.soft(ell(x_ + r * 0.06 * k, y_ - ry * 0.04, r * 0.4 * k, ry * 0.22), (60, 20, 70), 0.55, 3)
    b.eyes(iris=(90, 220, 120), look=(0.45, 0.45), lid=0.55, lower=0.08, size=1.04, lashes=1, tilt=-0.05)
    b.brows(col=(40, 30, 40), lift_n=0.0, lift_f=-0.04, tilt_n=-0.1, tilt_f=-0.2, w=r * 0.1)
    b.nose("button", 0.95)
    c.ink(ell(fa["nose"][0] - r * 0.04, fa["nose"][1] + r * 0.04, 2.4, 2.4), (0, 0, 0, 0), lw=1.6, oc=(220, 220, 230), line_only=True)
    mx, my = fa["mouth"]
    b.mouth("o", mx - r * 0.02, my + ry * 0.02, r * 0.34, r * 0.26, open_col=(120, 20, 60))
    c.ink(ell(mx + r * 0.32, my - ry * 0.02, r * 0.44, r * 0.42), (255, 150, 210), lw=2.6, oc=(150, 30, 100), shade=0.3, sw=6, hi=0.6, hw=5,
          opacity=0.95)
    c.stroke([(mx + r * 0.14, my - ry * 0.2), (mx + r * 0.3, my - ry * 0.3)], 2.6, (255, 255, 255), opacity=0.8)
    b.ear(0.92)
    ex_, ey_ = fa["ear"]
    for k in range(3):
        c.ink(ell(ex_ - r * 0.28 + k * r * 0.02, ey_ - r * 0.2 + k * r * 0.22, 2.4, 2.4), (0, 0, 0, 0), lw=1.8, oc=(230, 230, 240), line_only=True)
    # shaved sides + a tall green mohawk
    c.ink(Sh([b.head_pts(jaw=0.92, chin=0.95, cheek=0.96)]), (60, 46, 60, 120), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0,
          clip=Sh([[(hx - r * 1.2, hy - ry * 1.2), (hx + r * 0.5, hy - ry * 1.2), (hx + r * 0.2, hy - ry * 0.35), (hx - r * 0.25, hy + ry * 0.2),
                    (hx - r * 1.2, hy + ry * 0.5)]]))
    pts = []
    n = 6
    for i in range(n * 2 + 1):
        t = i / (n * 2)
        a = math.radians(196 + t * 128)
        base = (hx + math.cos(a) * r * 0.98, hy + math.sin(a) * ry * 0.96)
        if i % 2 == 0:
            pts.append(base)
        else:
            L = r * (0.75 + 0.55 * math.sin(t * math.pi))
            aa = a - 0.28
            pts.append((base[0] + math.cos(aa) * L, base[1] + math.sin(aa) * L))
    pts += [(hx + r * 0.55, hy - ry * 0.62), (hx - r * 0.1, hy - ry * 0.72), (hx - r * 0.7, hy - ry * 0.5)]
    hawk = Sh([pts])
    c.ink(hawk, green, lw=3.0, shade=0.55, sw=r * 0.4, scol=green_sh, hi=0.5, hw=r * 0.2, hcol=green_hi, rim=0.3, rcol=(220, 255, 120))
    # near arm: phone in hand, she checks it
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.8, w1=8.0, cuff=7.4), leather, lw=3.0, shade=0.5, sw=10, scol=leather_sh, hi=0.45, hw=4,
          hcol=leather_hi, rim=0.25, rcol=(170, 130, 255))
    wx, wy = b.P(*b.wrist_n)
    ph = Sh([rot_pts([(wx + 2, wy - 44), (wx + 26, wy - 44), (wx + 26, wy + 0), (wx + 2, wy + 0)], -18, wx + 14, wy - 22)])
    c.ink(ph, (30, 30, 40), lw=2.4, shade=0.2, hi=0.3)
    scr = Sh([rot_pts([(wx + 5, wy - 40), (wx + 23, wy - 40), (wx + 23, wy - 4), (wx + 5, wy - 4)], -18, wx + 14, wy - 22)])
    c.ink(scr, (120, 230, 255), lw=0, shade=0.2, hi=0)
    c.glow2(wx + 14, wy - 22, 50, (120, 230, 255), 0.25)
    b.hand(True, "hold", size=0.95, d=(0.3, -1.0), thumb=1)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Anton (head waiter)
def paint_anton(height=400, name="hs_anton.png"):
    W, Hc = 400, 600
    skin = (236, 200, 170)
    c = C2(W, Hc, 505)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=0.82, hips=0.86, limbs=0.84, head=1.0, legs=1.06, neck=1.1, chest=1.2,
                        hand=0.95, foot=1.0),
             pose=dict(arm_n=20, fore_n=70, arm_f=-10, fore_f=6, leg_n=-2, shin_n=0, leg_f=4, shin_f=-1, lean=-5,
                       head_dx=-0.4, head_dy=0.6), seed=15)
    white, white_sh = (248, 246, 240), (196, 190, 222)
    black, black_sh = (34, 30, 42), (18, 14, 26)
    hair, hair_sh, hair_hi = (30, 24, 36), (14, 10, 20), (120, 110, 170)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm straight at the side (stiff)
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.88), size=0.95)
    c.ink(b.sleeve(False, to_wrist=True, w0=8.0, w1=7.0, cuff=6.4), shade_col(white, 0.86), lw=2.8, shade=0.3, scol=white_sh)

    def shoes(bb, near):
        bb.shoe(near, (24, 20, 30) if near else (20, 16, 26), (40, 36, 46), "shoe", length=1.05)
        an = bb.ankle_n if near else bb.ankle_f
        c.stroke(bb.Ps([(an[0] + 2, an[1] - 0.8), (an[0] + 7, an[1] - 1.8)]), 2.2, (255, 255, 255), opacity=0.6)
    legs(b, black, w=(7.6, 5.4, 4.8), scol=black_sh, shoe=shoes, folds_col=(90, 80, 110))
    for near in (True, False):     # satin stripe
        hp, an = (b.hip_n, b.ankle_n) if near else (b.hip_f, b.ankle_f)
        c.stroke(b.Ps([(hp[0] - 2.4, hp[1] - 2), (b.knee_n[0] - 2.2 if near else b.knee_f[0] - 2.2, b.knee_n[1] if near else b.knee_f[1]),
                       (an[0] - 1.8, an[1] + 5)]), 1.6, (90, 84, 110), taper=(0, 0), opacity=0.8)
    # torso: white waiter's jacket, brass buttons, black bow tie
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.5, hem=b.hip_y - 3.0, flare=0.0, neck_open=1.0)])
    c.ink(torso, white, lw=3.0, shade=0.5, sw=20, scol=white_sh, hi=0.2, rim=0.2, rcol=(200, 220, 255))
    sy, sx = b.shoulder_y, b.lean_dx
    c.stroke(b.Ps([(sx + 1.0, sy + 1.0), (sx * 0.5 + 2.4, b.hip_y + 2), (2.0, b.hip_y - 3)]), 1.8, (150, 140, 180), taper=(0.1, 0.1))
    for k in range(3):
        f = k / 3.0
        for dx in (0.0, 3.4):
            c.ink(ell(*b.P(sx * (1 - f * 0.8) + 2.6 + dx * (1 - f * 0.2), sy - 8 - k * 7.4), 2.6, 2.6), (236, 190, 80), lw=1.3, shade=0.3,
                  hi=0.6)
    c.ink(Sh([b.Ps([(sx - 1.8, sy + 1.6), (sx + 3.2, sy + 1.2), (sx + 1.4, sy - 3.0)])]), (250, 250, 250), lw=2.0, shade=0.2)
    bt = b.P(sx + 0.9, sy - 0.6)
    for d in (-1, 1):
        c.ink(Sh([[bt, (bt[0] + d * 14, bt[1] - 7), (bt[0] + d * 14, bt[1] + 7)]]), black, lw=2.0, shade=0.2, hi=0.4)
    c.ink(ell(bt[0], bt[1], 4, 4), black, lw=1.6)
    c.stroke([b.P(1.6, b.hip_y + 15), b.P(4.6, b.hip_y + 14)], 2.0, (150, 140, 180), opacity=0.6)   # breast pocket
    # head: slick side-parted hair, pencil moustache, chin up, glaring
    face_base(b, skin, jaw=0.95, chin=1.1, cheek=0.92, chin_drop=1.02)
    fa = b.face_anchor()
    b.eyes(iris=(80, 60, 50), look=(0.4, -0.45), lid=0.42, size=0.96)
    b.brows(col=hair, lift_n=0.05, lift_f=0.02, tilt_n=-0.9, tilt_f=-0.9, w=r * 0.13)
    b.nose("long", 1.0)
    mx, my = fa["mouth"]
    b.mouth("flat", mx, my + ry * 0.06, r * 0.36, r * 0.2)
    c.stroke([(mx - r * 0.24, my - ry * 0.06), (mx + r * 0.0, my - ry * 0.1), (mx + r * 0.28, my - ry * 0.12)], 2.6, hair, taper=(0.4, 0.4))
    b.ear(0.92)
    slick = blob([(hx - r * 1.04, hy + ry * 0.3), (hx - r * 1.1, hy - ry * 0.45), (hx - r * 0.6, hy - ry * 1.0), (hx + r * 0.3, hy - ry * 1.06),
                  (hx + r * 0.98, hy - ry * 0.6), (hx + r * 0.9, hy - ry * 0.45), (hx + r * 0.2, hy - ry * 0.55), (hx - r * 0.3, hy - ry * 0.35),
                  (hx - r * 0.5, hy + ry * 0.2)], 2)
    c.ink(slick, hair, lw=3.0, shade=0.4, sw=r * 0.3, scol=hair_sh, hi=0.55, hw=r * 0.18, hcol=hair_hi)
    for k in range(4):
        c.stroke([(hx - r * (0.8 - k * 0.1), hy - ry * (0.3 + k * 0.14)), (hx + r * (0.2 + k * 0.18), hy - ry * (0.8 + k * 0.04))], 1.6, hair_hi,
                 opacity=0.6)
    c.stroke([(hx - r * 0.1, hy - ry * 1.0), (hx + r * 0.2, hy - ry * 0.6)], 1.8, skin, opacity=0.8)    # parting
    # near arm: forearm held level with a napkin draped over it
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.4, w1=7.4, cuff=6.8), white, lw=3.0, shade=0.45, sw=10, scol=white_sh, hi=0.2)
    b.hand(True, "flat", size=0.95, d=(1.0, -0.2), thumb=-1)
    el, wr = b.P(*b.elbow_n), b.P(*b.wrist_n)
    mxp = ((el[0] + wr[0]) / 2 + 4, (el[1] + wr[1]) / 2)
    nap = blob([(mxp[0] - 24, mxp[1] - 10), (mxp[0] + 22, mxp[1] - 12), (mxp[0] + 26, mxp[1] + 52), (mxp[0] + 6, mxp[1] + 64),
                (mxp[0] - 8, mxp[1] + 50), (mxp[0] - 26, mxp[1] + 30)], 1)
    c.ink(nap, (252, 252, 250), lw=2.6, shade=0.45, sw=10, scol=white_sh, hi=0.2)
    folds(c, [[(mxp[0] - 6, mxp[1] + 2), (mxp[0] - 2, mxp[1] + 48)], [(mxp[0] + 10, mxp[1]), (mxp[0] + 14, mxp[1] + 50)]], white_sh, 1.6, 0.8)
    return finish_sprite(c, name, flip=False)


# =========================================================================== Vivian Quill (critic) at her tall table
def paint_vivian_quill(height=376, name="hs_vivian_quill.png"):
    W, Hc = 520, 620
    skin = (240, 210, 190)
    c = C2(W, Hc, 506)
    b = Body(c, 190, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.86, waist=0.86, hips=1.0, limbs=0.8, head=1.0, legs=1.0, neck=1.05, chest=1.2,
                        hand=0.9, foot=0.95),
             pose=dict(arm_n=30, fore_n=12, arm_f=24, fore_f=22, leg_n=-2, shin_n=0, leg_f=4, shin_f=-1, lean=8,
                       head_dx=1.0, head_dy=-0.4), seed=16)
    black, black_sh, black_hi = (40, 34, 50), (20, 16, 30), (120, 100, 160)
    hair, hair_sh, hair_hi = (226, 224, 236), (160, 156, 186), (255, 255, 255)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # tall bistro table in front of her (drawn first so her far hand rests on it)
    tx, ttop = b.P(19, 0)[0], b.P(0, 52)[1]
    c.soft(ell(tx, b.fy - 2, 50, 7), (30, 8, 40), 0.4, 5)
    c.ink(ell(tx, b.fy - 4, 34, 7), (60, 56, 70), lw=2.6, shade=0.3, hi=0.3)
    c.stroke([(tx, b.fy - 6), (tx, ttop + 6)], 9, INK, taper=(0, 0))
    c.stroke([(tx, b.fy - 6), (tx, ttop + 6)], 5, (150, 140, 160), taper=(0, 0))
    # far arm (behind) leaning on the table top
    c.ink(b.arm_shape(False), shade_col(black, 0.9), lw=2.8, shade=0.3)
    b.hand(False, "flat", col=shade_col(skin, 0.88), d=(1.0, 0.1), thumb=-1, size=0.9)
    c.ink(ell(tx, ttop, 62, 13), (70, 64, 80), lw=2.8, shade=0.3, sw=6, hi=0.5, hw=3)
    c.ink(ell(tx, ttop - 2, 58, 11), (90, 84, 100), lw=0, shade=0.2, hi=0.4)
    # espresso cup + notepad on the table
    c.ink(rrect(tx + 14, ttop - 18, tx + 30, ttop - 4, 4), (250, 248, 240), lw=1.8, shade=0.3)
    c.ink(ell(tx + 22, ttop - 3, 13, 3.4), (240, 236, 226), lw=1.6)
    c.ink(Sh([[(tx - 44, ttop - 4), (tx - 4, ttop - 8), (tx + 4, ttop + 0), (tx - 36, ttop + 4)]]), (252, 250, 236), lw=1.8, shade=0.2)
    # long black dress / coat down to the boots
    def boots(bb, near):
        bb.shoe(near, (30, 26, 36) if near else (24, 20, 30), (50, 46, 56), "boot", length=0.95)
    legs(b, (60, 50, 70), w=(6.8, 4.6, 4.0), scol=(36, 26, 44), shoe=boots, skin=True)
    coat = skirt(b, black, 14, flare=4.6, waist=b.hip_y + 8, scol=black_sh, pleats=3)
    # torso
    c.ink(b.neck_shape(0.85), skin, lw=2.6, shade=0.6, sw=6)
    torso = Sh([b.torso_pts(slack=0.6, hem=b.hip_y - 2, flare=0.6, neck_open=0.9)])
    c.ink(torso, black, lw=3.0, shade=0.5, sw=18, scol=black_sh, hi=0.35, hcol=black_hi, rim=0.25, rcol=(170, 130, 240))
    sy, sx = b.shoulder_y, b.lean_dx
    c.ink(Sh([b.Ps([(sx - 2.8, sy + 2.0), (sx + 4.0, sy + 1.4), (sx + 3.6, sy - 1.2), (sx - 2.4, sy - 0.8)])]), (60, 54, 70), lw=2.2)   # collar
    c.ink(ell(*b.P(sx + 1.0, sy - 3.4), 4.6, 4.6), (200, 40, 60), lw=1.8, shade=0.3, hi=0.6)   # brooch
    # head: severe silver bun, glasses on a chain made of tiny glasses, a pen behind the ear
    bun = ell(hx - r * 0.55, hy - ry * 1.05, r * 0.62, r * 0.55, -20)
    c.ink(bun, hair, lw=3.0, shade=0.5, sw=r * 0.3, scol=hair_sh, hi=0.4, hcol=hair_hi)
    c.stroke([(hx - r * 0.95, hy - ry * 1.2), (hx - r * 0.2, hy - ry * 0.95)], 2.0, hair_sh, opacity=0.8)
    face_base(b, skin, jaw=0.95, chin=1.1, cheek=0.94, chin_drop=1.04)
    fa = b.face_anchor()
    b.eyes(iris=(70, 90, 120), look=(0.35, 0.25), lid=0.5, size=0.9)
    b.brows(col=hair_sh, lift_n=0.18, lift_f=0.0, tilt_n=-0.4, tilt_f=-0.9, w=r * 0.1, arch=0.1)
    b.nose("hook", 1.1)
    mx, my = fa["mouth"]
    b.mouth("frown", mx, my + ry * 0.06, r * 0.36, r * 0.18, lip=(150, 30, 60))
    for (dx, dy, L) in ((0.35, 0.55, 0.25), (0.82, 0.62, 0.18)):        # laugh lines (she does not laugh)
        c.stroke([(fa["c"][0] + r * dx, fa["c"][1] + ry * dy), (fa["c"][0] + r * (dx + 0.06), fa["c"][1] + ry * (dy + L))], 1.4,
                 shade_col(skin, 0.6), opacity=0.7)
    glasses(b, col=(30, 26, 36), round_=False, size=0.85, lw=2.4)
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    # glasses chain of tiny glasses: little loops from the temple down behind the ear and back up
    pts = bez((ex_ + r * 0.02, ey_ - r * 0.12), (ex_ - r * 0.2, ey_ + r * 1.8), (ex_ + r * 0.9, ey_ + r * 0.4), 14)
    for i, (px_, py_) in enumerate(pts[1::2]):
        c.ink(ell(px_, py_, 2.6, 2.0), (0, 0, 0, 0), lw=1.4, oc=(240, 200, 90), line_only=True)
    hairline = blob([(hx - r * 1.05, hy + ry * 0.35), (hx - r * 1.1, hy - ry * 0.45), (hx - r * 0.55, hy - ry * 1.0), (hx + r * 0.4, hy - ry * 1.02),
                     (hx + r * 1.0, hy - ry * 0.55), (hx + r * 0.85, hy - ry * 0.42), (hx + r * 0.2, hy - ry * 0.62), (hx - r * 0.35, hy - ry * 0.3),
                     (hx - r * 0.55, hy + ry * 0.25)], 2)
    c.ink(hairline, hair, lw=3.0, shade=0.5, sw=r * 0.3, scol=hair_sh, hi=0.4, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 0.9, hy + ry * 0.1), (hx - r * 0.7, hy - ry * 0.7), (hx, hy - ry * 0.95)],
                     [(hx - r * 0.3, hy - ry * 0.4), (hx + r * 0.3, hy - ry * 0.8), (hx + r * 0.9, hy - ry * 0.55)]], hair_sh, 1.6)
    for k, col in enumerate(((220, 40, 60), (40, 120, 220))):         # a pen behind each ear (the far one just shows)
        a0 = (ex_ - r * 0.5 + k * r * 0.9, ey_ - r * 0.55 - k * r * 0.1)
        a1 = (a0[0] + r * 0.75, a0[1] - r * 0.45)
        c.stroke([a0, a1], 5.0, INK, taper=(0, 0))
        c.stroke([a0, a1], 3.0, col, taper=(0, 0))
    # near arm: pen poised over the notepad, about to be unkind
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=8.0, w1=7.0, cuff=6.6), black, lw=3.0, shade=0.45, sw=10, scol=black_sh, hi=0.35, hcol=black_hi)
    wx, wy = b.P(*b.wrist_n)
    c.stroke([(wx + 6, wy + 4), (wx + 30, wy + 18)], 5.0, INK, taper=(0, 0))
    c.stroke([(wx + 6, wy + 4), (wx + 30, wy + 18)], 3.0, (30, 30, 40), taper=(0, 0.2))
    b.hand(True, "hold", size=0.9, d=(0.8, 0.6), thumb=1)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Grizz (roadie, knitting)
def paint_grizz(height=440, name="hs_grizz.png"):
    W, Hc = 460, 640
    skin = (230, 172, 134)
    c = C2(W, Hc, 507, lw=3.2)
    b = Body(c, 200, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.4, waist=1.35, hips=1.3, limbs=1.3, head=0.96, legs=0.94, neck=1.4, chest=1.6, belly=3.0,
                        hand=1.2, foot=1.15),
             pose=dict(arm_n=2, fore_n=50, arm_f=8, fore_f=46, leg_n=-6, shin_n=2, leg_f=7, shin_f=-3, lean=0,
                       head_dx=0.8, head_dy=-1.2), seed=17)
    tee, tee_sh = (44, 40, 52), (24, 20, 32)
    denim, denim_sh = (64, 96, 170), (36, 54, 120)
    beard, beard_sh, beard_hi = (150, 86, 46), (96, 50, 30), (220, 150, 90)
    pink = (255, 120, 180)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=3.0, shade=0.4)
    c.ink(b.sleeve(False, 0.5, 8.4, 7.8), shade_col(tee, 0.9), lw=3.0, shade=0.3)

    def boots(bb, near):
        bb.shoe(near, (120, 80, 50) if near else (96, 64, 40), (60, 40, 30), "boot", length=1.0)
        an = bb.ankle_n if near else bb.ankle_f
        c.stroke(bb.Ps([(an[0] - 2, an[1] + 8), (an[0] + 2.4, an[1] + 8.4)]), 1.8, (230, 200, 120), taper=(0, 0))
    legs(b, denim, w=(10.4, 8.4, 7.8), scol=denim_sh, shoe=boots, cuffs=(90, 120, 190))
    # tool belt: gaffer tape roll, multitool
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=10)
    torso = Sh([b.torso_pts(slack=1.2, hem=b.hip_y - 2.5, flare=0.8, neck_open=1.2)])
    c.ink(torso, tee, lw=3.2, shade=0.5, sw=28, scol=tee_sh, hi=0.25, hcol=(100, 90, 120), rim=0.25, rcol=(150, 110, 220))
    sy, sx = b.shoulder_y, b.lean_dx
    tx, ty = b.P(sx * 0.5 + 2.6, sy - 10)
    c.label(tx, ty, "CREW", 17, (120, 240, 140), mirror=True)
    c.label(tx, ty + 18, "SINCE FOREVER", 7, (200, 200, 210), "Bold", mirror=True)
    c.ink(Sh([b.Ps([(-6.6, b.hip_y - 0.6), (6.4, b.hip_y - 0.6), (6.4, b.hip_y - 3.6), (-6.6, b.hip_y - 3.6)])]), (110, 70, 40), lw=2.4, shade=0.3)
    gx, gy = b.P(-5.0, b.hip_y - 5)
    c.ink(ell(gx, gy, 18, 18), (70, 70, 80), lw=2.6, shade=0.4, hi=0.5)
    c.ink(ell(gx, gy, 8, 8), (30, 24, 34), lw=2.0)
    # head: beanie, hedge of a beard
    face_base(b, skin, jaw=1.15, chin=1.05, cheek=1.05)
    fa = b.face_anchor()
    b.eyes(iris=(70, 110, 80), look=(0.4, 0.5), lid=0.36, size=0.94)
    b.brows(col=beard_sh, lift_n=0.06, lift_f=0.04, tilt_n=0.5, tilt_f=0.3, w=r * 0.16)
    b.nose("round", 1.2)
    bd = blob([(hx - r * 0.55, hy + ry * 0.1), (hx + r * 0.1, hy + ry * 0.52), (hx + r * 0.9, hy + ry * 0.45), (hx + r * 1.22, hy + ry * 0.3),
               (hx + r * 1.35, hy + ry * 0.9), (hx + r * 1.2, hy + ry * 1.7), (hx + r * 0.7, hy + ry * 2.2), (hx - r * 0.1, hy + ry * 2.1),
               (hx - r * 0.7, hy + ry * 1.5), (hx - r * 0.85, hy + ry * 0.7)], 2)
    c.ink(bd, beard, lw=3.0, shade=0.55, sw=r * 0.5, scol=beard_sh, hi=0.4, hw=r * 0.2, hcol=beard_hi, rim=0.2)
    rng = random.Random(3)
    for _ in range(26):
        x_, y_ = hx + r * rng.uniform(-0.6, 1.1), hy + ry * rng.uniform(0.6, 1.9)
        c.stroke([(x_, y_), (x_ + rng.uniform(-4, 4), y_ + rng.uniform(8, 16))], 1.6, beard_sh, opacity=0.6, taper=(0.3, 0.6))
    mx, my = fa["mouth"]
    c.ink(blob([(mx - r * 0.5, my - ry * 0.12), (mx + r * 0.1, my - ry * 0.22), (mx + r * 0.6, my - ry * 0.1), (mx + r * 0.3, my + ry * 0.05),
                (mx - r * 0.3, my + ry * 0.05)], 2), hi_col(beard, 0.1), lw=2.4, shade=0.4, hi=0.3)       # moustache
    b.ear(1.0)
    beanie = blob([(hx - r * 1.12, hy - ry * 0.05), (hx - r * 1.1, hy - ry * 0.7), (hx - r * 0.5, hy - ry * 1.18), (hx + r * 0.4, hy - ry * 1.18),
                   (hx + r * 1.08, hy - ry * 0.7), (hx + r * 1.1, hy - ry * 0.3)], 2)
    c.ink(beanie, (236, 110, 40), lw=3.0, shade=0.5, sw=r * 0.3, hi=0.4)
    clip_draw(c, beanie, lambda t: [t.stroke([(x, hy - ry * 1.3), (x + r * 0.05, hy)], 1.8, (180, 70, 20), taper=(0, 0), opacity=0.6)
                                    for x in np.arange(hx - r * 1.2, hx + r * 1.2, r * 0.18)])
    c.ink(Sh([[(hx - r * 1.16, hy - ry * 0.02), (hx + r * 1.14, hy - ry * 0.28), (hx + r * 1.1, hy - ry * 0.55), (hx - r * 1.14, hy - ry * 0.35)]]),
          (210, 90, 30), lw=2.8, shade=0.4, hi=0.3)
    # near arm + hands working the little pink scarf (finger knitting)
    c.ink(b.arm_shape(True), skin, lw=3.2, shade=0.5)
    c.ink(b.sleeve(True, 0.52, 8.8, 8.2), tee, lw=3.2, shade=0.4, sw=10, hi=0.2, hcol=(100, 90, 120))
    for k in range(5):           # forearm hair
        e, w = b.P(*b.elbow_n), b.P(*b.wrist_n)
        t = 0.25 + k * 0.13
        x_, y_ = e[0] + (w[0] - e[0]) * t, e[1] + (w[1] - e[1]) * t
        c.stroke([(x_, y_ - 6), (x_ + 4, y_ - 10)], 1.4, beard_sh, opacity=0.6)
    wn, wf = b.P(*b.wrist_n), b.P(*b.wrist_f)
    scarf = limb([((wn[0] + wf[0]) / 2 + 6, (wn[1] + wf[1]) / 2 + 6), (wn[0] - 4, wn[1] + 60), (wn[0] + 10, wn[1] + 120)],
                 [26, 24, 22], smooth=2)
    c.ink(scarf, pink, lw=2.8, shade=0.45, sw=8, hi=0.4)
    clip_draw(c, scarf, lambda t: [t.stroke([(wn[0] - 40, y), (wn[0] + 60, y + 6)], 1.6, (200, 70, 130), taper=(0, 0), opacity=0.7)
                                   for y in np.arange(wn[1] - 10, wn[1] + 140, 8)])
    outline(c, scarf, 2.8)
    for k in range(4):
        x_ = wn[0] + 2 + k * 6
        c.stroke([(x_, wn[1] + 128), (x_ + 2, wn[1] + 146)], 2.4, pink, taper=(0, 0.6))
    b.hand(False, "hold", col=shade_col(skin, 0.92), size=1.15, d=(0.7, -0.6), thumb=1)
    b.hand(True, "hold", size=1.2, d=(0.6, -0.8), thumb=1)
    c.stroke([wn, ((wn[0] + wf[0]) / 2 + 4, (wn[1] + wf[1]) / 2 - 4), wf], 2.4, pink, taper=(0, 0))
    return finish_sprite(c, name, flip=True)


# =========================================================================== shared room bits
def neon(c, x, y, s, size, col, kind="Black", angle=0, glow=1.0):
    """Neon tube lettering: coloured glow, a dark tube outline and a hot white core."""
    c.glow2(x, y, size * len(s) * 0.45 + size, col, 0.45 * glow, sy=0.55)
    c.text(x, y, s, size, col + (255,), kind, stroke=3.0, sc=INK, angle=angle)
    c.text(x, y, s, size * 0.98, mix(col, (255, 255, 255), 0.55) + (255,), kind, angle=angle)
    c.glow2(x, y, size * len(s) * 0.3 + size * 0.5, mix(col, (255, 255, 255), 0.4), 0.3 * glow, sy=0.4)


def brick_block(c, x0, y0, x1, y1, col, seed=0, mortar=None, bh=16, opacity=0.35):
    """A flat brick wall face in screen space (fill + mortar lines + a few odd bricks)."""
    rng = random.Random(seed)
    c.ink(rect(x0, y0, x1, y1), col, lw=3.2, shade=0.35, sw=60, hi=0.2, tex=0.22)
    mortar = mortar or shade_col(col, 0.6)
    row = 0
    for yy in np.arange(y0 + bh, y1, bh):
        c.stroke([(x0, yy), (x1, yy)], 1.2, mortar, opacity=opacity, taper=(0, 0), wob=0.3)
        off = (row % 2) * 20
        for xx in np.arange(x0 + off, x1, 40):
            c.stroke([(xx, yy - bh), (xx, yy)], 1.1, mortar, opacity=opacity * 0.8, taper=(0, 0), wob=0.2)
            if rng.random() < 0.05:
                c.ink(rect(xx + 1, yy - bh + 1, xx + 39, yy - 1), mix(col, (255, 180, 160) if rng.random() < 0.5 else (60, 20, 50), 0.25),
                      lw=0, shade=0, hi=0, ao=0, tex=0.2)
        row += 1


def awning(c, x0, x1, y, h, cols, n=None, drop=26):
    """Striped scalloped shop awning, seen from below-front (screen space)."""
    n = n or max(4, int((x1 - x0) / 46))
    w = (x1 - x0) / n
    top = [(x0 - 16, y), (x1 + 16, y), (x1 + 4, y + h), (x0 - 4, y + h)]
    c.ink(Sh([top]), cols[0], lw=3.0, shade=0.45, sw=20, hi=0.3)
    clip_draw(c, Sh([top]), lambda t: [t.ink(Sh([[(x0 - 16 + k * w * (x1 - x0 + 32) / (x1 - x0), y), (x0 - 16 + (k + 0.5) * w * (x1 - x0 + 32) / (x1 - x0), y),
                                                 (x0 - 4 + (k + 0.5) * w * (x1 - x0 + 8) / (x1 - x0), y + h), (x0 - 4 + k * w * (x1 - x0 + 8) / (x1 - x0), y + h)]]),
                                             cols[1], lw=0, shade=0, hi=0, ao=0) for k in range(n)])
    c.ink(Sh([top]), (0, 0, 0, 0), lw=3.0, line_only=True)
    for k in range(n):
        xa = x0 - 4 + k * (x1 - x0 + 8) / n
        xb = xa + (x1 - x0 + 8) / n
        sc = blob([(xa, y + h - 2), (xb, y + h - 2), (xb - 2, y + h + 6), ((xa + xb) / 2, y + h + drop), (xa + 2, y + h + 6)], 1)
        c.ink(sc, cols[k % 2], lw=2.6, shade=0.4, sw=8, hi=0.2)


def stanchion(c, x, y, h=86, col=(230, 190, 80)):
    c.soft(ell(x, y + 2, 22, 5), (24, 6, 34), 0.5, 4)
    c.ink(ell(x, y - 2, 18, 6), col, lw=2.4, shade=0.4, hi=0.6, hw=2)
    c.stroke([(x, y - 4), (x, y - h)], 8, INK, taper=(0, 0))
    c.stroke([(x, y - 4), (x, y - h)], 4.4, col, taper=(0, 0))
    c.ink(ell(x, y - h - 4, 8, 8), col, lw=2.2, shade=0.3, hi=0.6, hw=2)
    return (x, y - h + 6)


def velvet_rope(c, a, b, sag=34, col=(200, 30, 80)):
    cable(c, a, b, sag=sag, w=9, col=col)


def hydrant(c, x, y, s=1.0, col=(220, 50, 60)):
    c.soft(ell(x, y + 2, 34 * s, 7 * s), (24, 6, 34), 0.5, 4)
    c.ink(rrect(x - 18 * s, y - 70 * s, x + 18 * s, y, 6), col, lw=2.8, shade=0.5, sw=10, hi=0.4, rim=0.2)
    c.ink(ell(x, y - 74 * s, 20 * s, 12 * s), col, lw=2.6, shade=0.4, hi=0.5)
    c.ink(rect(x - 28 * s, y - 52 * s, x + 28 * s, y - 38 * s), dk(col, 0.85), lw=2.4, shade=0.3)
    c.ink(rect(x - 24 * s, y - 6 * s, x + 24 * s, y + 2), dk(col, 0.8), lw=2.4)


def city_sky(c, y1, seed, top=(30, 16, 70), bot=(170, 60, 130), stars=150, towers=True):
    rng = random.Random(seed)
    c.ink(rect(-10, -10, W_BG + 10, y1 + 10), ("vy", -10, y1, top, bot), lw=0, shade=0, hi=0, ao=0, tex=0.06, wob=0)
    for _ in range(stars):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, y1 * 0.55)
        r = rng.choice([0.9, 1.2, 1.8, 2.2])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.4, 1))
    if towers:
        x = -20
        while x < W_BG:
            w = rng.uniform(70, 160)
            t = rng.uniform(y1 * 0.25, y1 * 0.6)
            col = mix((50, 26, 90), bot, rng.uniform(0.05, 0.25))
            c.ink(rect(x, t, x + w, y1 + 5), col, lw=0, shade=0, hi=0, ao=0, tex=0.06)
            if rng.random() < 0.3:
                c.stroke([(x + w / 2, t), (x + w / 2, t - 40)], 3, col)
                c.ink(ell(x + w / 2, t - 42, 3, 3), (255, 60, 80), lw=0)
                c.glow2(x + w / 2, t - 42, 14, (255, 60, 80), 0.5)
            for wy in np.arange(t + 10, y1, 18):
                for wx in np.arange(x + 8, x + w - 8, 14):
                    if rng.random() < 0.25:
                        c.ink(rect(wx, wy, wx + 6, wy + 8), mix((255, 206, 110), bot, 0.4), lw=0, shade=0, hi=0, ao=0, tex=0, opacity=0.8)
            x += w + rng.uniform(-10, 10)


def outdoor_room(seed, light=(0.35, -0.94), hor=700):
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=light, lw=3.4, seed=seed)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), (-400, 100, 2320, hor), fc=1000)
    return c, R, random.Random(seed)


def sidewalk(c, R, seed, c1=(150, 112, 150), c2=(136, 100, 140), grout=(92, 62, 100), size=90):
    def floor(sub):
        tiles(sub, c1, c2, 0, 0, sub.w, sub.h, size=size * sub.density, seed=seed, chipped=0.12, grout=grout)
    R.paint_plane("floor", -400, 2700, 0, R.z_front(160), floor, density=0.9, seed=seed)


def chalk_square(c, R, cx, cy, w=150, d=70, col=(250, 250, 255)):
    X, Z = R.floor_at(cx, cy)
    pts = [R.pt(X - w / 2, 0, Z - d / 2), R.pt(X + w / 2, 0, Z - d / 2), R.pt(X + w / 2, 0, Z + d / 2), R.pt(X - w / 2, 0, Z + d / 2)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        c.stroke([a, b], 3.4, col, opacity=0.75, wob=1.2, taper=(0.1, 0.1))
    return pts


# =========================================================================== 1. Uptown street (night)
HOR_UP = 700


def paint_uptown():
    c, R, rng = outdoor_room(5100)
    P = R.pt
    HOR = HOR_UP
    city_sky(c, HOR, 5101)
    # ---------------- floor: sidewalk, curb and the road edge at the very bottom
    sidewalk(c, R, 5102)
    c.ink(Sh([[(-20, 1012), (1940, 1012), (1940, 1030), (-20, 1030)]]), (180, 160, 190), lw=3.0, shade=0.3, hi=0.4, tex=0.2)
    c.ink(rect(-20, 1030, 1940, 1100), (40, 34, 56), lw=0, shade=0, hi=0, ao=0, tex=0.3)
    for x in range(-40, 1960, 220):
        c.ink(Sh([[(x, 1060), (x + 120, 1060), (x + 126, 1080), (x - 6, 1080)]]), (240, 210, 100), lw=0, opacity=0.6)
    for _ in range(16):
        x_, y_ = rng.uniform(0, W_BG), rng.uniform(720, 1000)
        c.soft(ell(x_, y_, rng.uniform(30, 90), rng.uniform(8, 20)), (60, 20, 60), 0.15, 10)
    for (x_, y_, a) in ((420, 790, 20), (1120, 830, -30), (1640, 780, 10), (300, 930, 40)):       # litter: flyers, a cup
        c.ink(Sh([rot_pts([(x_ - 16, y_ - 6), (x_ + 16, y_ - 6), (x_ + 16, y_ + 6), (x_ - 16, y_ + 6)], a, x_, y_)]),
              rng.choice([(250, 246, 230), (255, 120, 190), (160, 230, 255)]), lw=1.6, shade=0.2)
    chalk_square(c, R, 812, 940, 170, 80)
    c.text(760, 988, "THE BOX", 12, (250, 250, 255, 170), "Bold", angle=2)

    # ---------------- far left: brick block with the campus shuttle stop
    brick_block(c, -30, 250, 250, HOR, (120, 60, 90), seed=1)
    facade_windows(c, -10, 240, 270, 420, 2, 2, rng, lit=0.5)
    sx0, sx1 = 30, 230
    c.soft(ell((sx0 + sx1) / 2, HOR + 10, 130, 14), (24, 6, 34), 0.5, 8)
    for X in (sx0, sx1):
        c.stroke([(X, HOR + 6), (X, 470)], 9, INK, taper=(0, 0))
        c.stroke([(X, HOR + 6), (X, 470)], 5, (150, 160, 180), taper=(0, 0))
    c.ink(Sh([[(sx0 - 20, 470), (sx1 + 20, 470), (sx1 + 6, 446), (sx0 - 6, 446)]]), (60, 150, 160), lw=3.0, shade=0.4, hi=0.4)
    c.ink(rect(sx0 + 8, 480, sx1 - 8, 640), (150, 210, 230, 70), lw=2.4, oc=(60, 80, 110), shade=0, hi=0.4)
    c.stroke([(sx0 + 30, 620), (sx0 + 90, 500)], 6, (255, 255, 255), opacity=0.25)
    c.ink(rrect(sx0 + 24, 500, sx1 - 24, 560, 6), (40, 120, 200), lw=2.6, shade=0.3, hi=0.3)
    c.text((sx0 + sx1) / 2, 518, "CAMPUS", 15, (255, 255, 240))
    c.text((sx0 + sx1) / 2, 540, "SHUTTLE", 13, (255, 236, 140))
    c.ink(rect(sx0 + 10, 640, sx1 - 10, 654), (190, 110, 70), lw=2.6, shade=0.3, hi=0.3)
    for X in (sx0 + 26, sx1 - 26):
        c.stroke([(X, 654), (X, HOR)], 5, INK, taper=(0, 0))
    c.ink(rrect(sx0 + 40, 580, sx0 + 120, 630, 4), (250, 246, 230), lw=2.0, shade=0.2)
    c.text(sx0 + 80, 594, "12 MIN.", 9, (60, 60, 120), "Bold")
    c.text(sx0 + 80, 612, "OR 40", 9, (190, 40, 60), "Bold")

    # ---------------- Gallery Pierre: pale plaster facade, big window with one white canvas
    gx0, gx1 = 250, 770
    c.ink(rect(gx0, 180, gx1, HOR), (226, 196, 214), lw=3.2, shade=0.35, sw=60, hi=0.25, tex=0.2)
    for _ in range(3):
        chip(c, rng.uniform(gx0 + 30, gx1 - 30), rng.uniform(220, 420), rng.uniform(20, 36), BRICK, MORTAR, (226, 196, 214),
             seed=rng.randint(0, 99))
    stain(c, gx0 + 120, 230, 50, (90, 40, 80), 0.18, 3, 7)
    facade_windows(c, gx0 + 10, gx1 - 10, 190, 330, 1, 4, rng, lit=0.6, frame=(250, 236, 244))
    c.ink(rect(gx0 - 12, 340, gx1 + 12, 362), (250, 236, 244), lw=2.8, shade=0.3, hi=0.4)
    c.ink(rrect(gx0 + 70, 372, gx1 - 70, 420, 6), (36, 30, 46), lw=3.0, shade=0.3, hi=0.2)
    c.text((gx0 + gx1) / 2, 396, "GALLERY  PIERRE", 26, (250, 246, 236), "Black")
    c.text((gx0 + gx1) / 2, 432, "fine art  ·  finer silence", 11, (80, 50, 70), "Italic")
    # shop window (left)
    wx0, wx1, wy0, wy1 = gx0 + 30, gx0 + 270, 455, HOR - 30
    c.ink(rect(wx0 - 12, wy0 - 12, wx1 + 12, wy1 + 12), (250, 236, 244), lw=3.0, shade=0.4)
    c.ink(rect(wx0, wy0, wx1, wy1), ("v", (250, 246, 240), (220, 210, 220)), lw=2.6, shade=0.2, hi=0)
    c.ink(rect(wx0 + 70, wy0 + 40, wx1 - 70, wy1 - 70), (255, 255, 252), lw=2.4, shade=0.3, sw=10)
    c.ink(rrect(wx0 + 100, wy1 - 54, wx1 - 100, wy1 - 38, 2), (250, 250, 250), lw=1.4)
    c.glow2((wx0 + wx1) / 2, (wy0 + wy1) / 2, 200, (220, 240, 255), 0.4)
    c.stroke([(wx0 + 20, wy1 - 20), (wx0 + 100, wy0 + 20)], 12, (255, 255, 255), opacity=0.25)
    c.ink(rect(wx0 - 12, wy1 + 12, wx1 + 12, HOR), (110, 70, 100), lw=2.6, shade=0.3)
    # door (hotspot "Gallery Pierre")
    dx0, dx1, dy0 = gx0 + 310, gx0 + 450, 460
    c.ink(rect(dx0 - 16, dy0 - 16, dx1 + 16, HOR), (36, 30, 46), lw=3.0, shade=0.3)
    for (a, b_) in ((dx0, (dx0 + dx1) / 2 - 2), ((dx0 + dx1) / 2 + 2, dx1)):
        c.ink(rect(a, dy0, b_, HOR), (60, 70, 90), lw=2.4, shade=0.2)
        c.ink(rect(a + 8, dy0 + 10, b_ - 8, HOR - 30), (200, 230, 240, 200), lw=2.0, shade=0.1, hi=0.3)
    c.glow2((dx0 + dx1) / 2, 560, 120, (220, 240, 255), 0.35)
    c.stroke([((dx0 + dx1) / 2 - 10, 560), ((dx0 + dx1) / 2 - 10, 620)], 5, (230, 200, 90), taper=(0, 0))
    c.stroke([((dx0 + dx1) / 2 + 10, 560), ((dx0 + dx1) / 2 + 10, 620)], 5, (230, 200, 90), taper=(0, 0))
    c.ink(rrect(dx0 + 14, dy0 + 40, dx0 + 60, dy0 + 74, 3), (250, 246, 230), lw=1.6)
    c.text(dx0 + 37, dy0 + 51, "OPEN", 7, (190, 40, 60), "Bold")
    c.text(dx0 + 37, dy0 + 63, "TONIGHT", 6, (60, 60, 120), "Bold")
    c.ink(Sh([[(dx0 - 30, HOR), (dx1 + 30, HOR), (dx1 + 40, HOR + 14), (dx0 - 40, HOR + 14)]]), (200, 190, 200), lw=2.6, shade=0.3)
    # topiary in a pot by the door
    tx = gx1 - 30
    c.ink(rrect(tx - 24, HOR - 50, tx + 24, HOR, 4), (60, 150, 160), lw=2.6, shade=0.4, hi=0.3)
    c.stroke([(tx, HOR - 50), (tx, HOR - 90)], 5, (90, 56, 60))
    c.ink(ell(tx, HOR - 120, 34, 36), (50, 120, 90), lw=2.8, shade=0.55, sw=12, hi=0.35, rim=0.2)

    # ---------------- the brick wall between: posters (Jett Vex poster = hotspot), lamppost
    bx0, bx1 = gx1, 1100
    brick_block(c, bx0, 120, bx1, HOR, (150, 60, 100), seed=2)
    for k, (x_, y_, w_, h_, col, a) in enumerate(((800, 600, 70, 90, (255, 230, 120), -4), (1060, 610, 60, 80, (160, 230, 255), 6),
                                                   (860, 300, 80, 100, (200, 255, 170), 3))):
        poster(c, x_, y_, w_, h_, col, angle=a, seed=40 + k, peel="br" if k == 1 else None,
               draw=lambda t, w, h, k=k: [t.stroke([(10, 20 + j * 14), (w - 10, 20 + j * 14)], 4, (60, 40, 80), opacity=0.6) for j in range(4)])

    def jett_poster(t, w, h):
        t.ink(rect(0, 0, w, h), (30, 20, 40), lw=0, shade=0, hi=0)
        t.ink(rect(0, h * 0.62, w, h), (255, 60, 160), lw=0, shade=0, hi=0)
        hx_, hy_ = w * 0.5, h * 0.36
        for k in range(7):            # green spikes
            a = math.radians(200 + k * 24)
            t.ink(Sh([[(hx_ + math.cos(a) * 20, hy_ + math.sin(a) * 20), (hx_ + math.cos(a + 0.2) * 52, hy_ + math.sin(a + 0.2) * 52),
                       (hx_ + math.cos(a + 0.35) * 20, hy_ + math.sin(a + 0.35) * 20)]]), (90, 236, 110), lw=1.6, shade=0.3)
        t.ink(ell(hx_, hy_, 26, 30), (238, 196, 176), lw=2.0, shade=0.3)
        t.ink(ell(hx_ + 2, hy_ + 14, 9, 11), (110, 20, 50), lw=1.6)            # the yawn
        for ex in (-10, 10):
            t.stroke([(hx_ + ex - 6, hy_ - 4), (hx_ + ex + 6, hy_ - 4)], 2.4, INK)
        t.stroke([(hx_ - 12, hy_ + 3), (hx_ - 2, hy_ + 1), (hx_ + 2, hy_ + 1), (hx_ + 12, hy_ + 3)], 2.6, INK)   # drawn-on moustache
        t.text(w / 2, h * 0.72, "JETT VEX", 17, (255, 255, 240))
        t.text(w / 2, h * 0.84, "LIVE @ CLUB VELOUR", 7, (30, 20, 40), "Bold")
        t.text(w / 2, h * 0.93, "bored out of my skull tour", 6, (255, 236, 120), "Bold")
    poster(c, 1010, 455, 120, 168, (30, 20, 40), draw=jett_poster, angle=-2, seed=48, peel="tr")
    lamps = [lamppost(c, 880, HOR + 22, 300)]

    # ---------------- Club Velour: purple velvet facade, pink neon, padded door, velvet rope
    cx0, cx1 = 1100, 1620
    c.ink(rect(cx0, 140, cx1, HOR), (70, 30, 96), lw=3.2, shade=0.35, sw=60, hi=0.2, tex=0.25)
    for x in np.arange(cx0 + 20, cx1, 40):         # velvet pleats
        c.stroke([(x, 150), (x + 4, HOR)], 6, (50, 20, 70), opacity=0.5, taper=(0, 0), wob=1.0)
        c.stroke([(x + 14, 150), (x + 16, HOR)], 3, (130, 70, 160), opacity=0.3, taper=(0, 0), wob=1.0)
    c.ink(rect(cx0 - 10, 130, cx1 + 10, 152), (230, 190, 80), lw=2.8, shade=0.3, hi=0.5)
    neon(c, 1270, 250, "Club", 46, (255, 80, 190), "Italic", angle=8)
    neon(c, 1380, 320, "VELOUR", 74, (110, 220, 255))
    c.stroke([(1180, 375), (1560, 362)], 4, (255, 80, 190))
    c.glow2(1370, 368, 220, (255, 80, 190), 0.3, sy=0.2)
    ddx0, ddx1, ddy0 = 1215, 1385, 420
    c.ink(rect(ddx0 - 34, ddy0 - 34, ddx1 + 34, HOR), (230, 190, 80), lw=3.0, shade=0.4, hi=0.5)
    for k in range(22):
        t_ = k / 21
        for (x_, y_) in ((ddx0 - 18, ddy0 - 18 + t_ * (HOR - ddy0)), (ddx1 + 18, ddy0 - 18 + t_ * (HOR - ddy0))):
            c.ink(ell(x_, y_, 5, 5), (255, 240, 200), lw=1.4, shade=0, hi=0)
            c.glow2(x_, y_, 16, GLOW, 0.4)
    for (a, b_) in ((ddx0, (ddx0 + ddx1) / 2 - 2), ((ddx0 + ddx1) / 2 + 2, ddx1)):
        c.ink(rect(a, ddy0, b_, HOR), (170, 30, 90), lw=2.8, shade=0.45, sw=24, hi=0.3)
        for yy in np.arange(ddy0 + 30, HOR - 10, 44):
            for xx in np.arange(a + 20, b_ - 10, 34):
                c.ink(ell(xx, yy, 3.4, 3.4), (240, 200, 90), lw=1.0, hi=0.6)
    c.stroke([((ddx0 + ddx1) / 2 - 12, 560), ((ddx0 + ddx1) / 2 - 12, 610)], 6, (240, 200, 90), taper=(0, 0))
    c.stroke([((ddx0 + ddx1) / 2 + 12, 560), ((ddx0 + ddx1) / 2 + 12, 610)], 6, (240, 200, 90), taper=(0, 0))
    c.ink(Sh([[(ddx0 - 60, HOR), (ddx1 + 60, HOR), (ddx1 + 80, HOR + 16), (ddx0 - 80, HOR + 16)]]), (150, 30, 70), lw=2.6, shade=0.3,
          tex=0.3)    # red carpet
    c.ink(Sh([[(ddx0 - 10, HOR + 16), (ddx1 + 10, HOR + 16), (ddx1 + 90, 760), (ddx0 - 90, 760)]]), (170, 36, 80), lw=2.6, shade=0.25, tex=0.3)
    a2 = stanchion(c, 1470, 752)
    a3 = stanchion(c, 1580, 748)
    velvet_rope(c, a2, a3, 22)
    # ---------------- Cafe Snoot archway (right)
    ax0, ax1 = 1620, 1960
    brick_block(c, ax0, 200, ax1, HOR, (176, 80, 76), seed=3)
    facade_windows(c, ax0 + 20, ax1, 220, 360, 1, 3, rng, lit=0.7, frame=(240, 220, 210))
    def arch_pts(r_, cx=1780, cy=500):
        return [(cx - r_, HOR), (cx - r_, cy)] + [(cx + r_ * math.cos(math.radians(a)), cy - r_ * math.sin(math.radians(a)))
                                                  for a in range(180, -1, -10)] + [(cx + r_, HOR)]
    ring = Sh([arch_pts(118)])
    c.ink(ring, (214, 180, 160), lw=3.2, shade=0.45, sw=20, hi=0.35, tex=0.25)
    arch = Sh([arch_pts(90)])
    c.ink(arch, ("v", (70, 30, 60), (140, 70, 80)), lw=3.2, shade=0.2, hi=0)
    c.ink(Sh([[(1690, HOR - 70), (1870, HOR - 70), (1870, HOR), (1690, HOR)]]), (190, 130, 120), lw=0, shade=0, hi=0, clip=arch)
    clip_draw(c, arch, lambda t: [t.stroke([(1680, HOR - 70 + k * 18), (1880, HOR - 70 + k * 18)], 1.6, (120, 70, 80), taper=(0, 0))
                                  for k in range(4)])
    for k in range(5):                  # glimpse of the terrace: string lights, a table, a warm window
        x_ = 1706 + k * 37
        y_ = 470 + 14 * math.sin(k * 1.3)
        c.ink(ell(x_, y_, 5, 7), (255, 230, 140), lw=1.4, clip=arch)
        c.glow2(x_, y_, 30, GLOW, 0.4)
    c.ink(rect(1720, 520, 1840, 600), (255, 200, 120), lw=2.4, shade=0.2, clip=arch)
    c.stroke([(1780, 520), (1780, 600)], 3, (110, 40, 50))
    c.ink(ell(1752, 638, 34, 7), (240, 236, 230), lw=2.0, clip=arch)
    c.stroke([(1752, 640), (1752, HOR - 6)], 4, INK)
    c.ink(arch, (0, 0, 0, 0), lw=3.2, line_only=True)
    for a in range(180, -1, -20):     # arch stones
        p0 = (1780 + 90 * math.cos(math.radians(a)), 500 - 90 * math.sin(math.radians(a)))
        p1 = (1780 + 118 * math.cos(math.radians(a)), 500 - 118 * math.sin(math.radians(a)))
        c.stroke([p0, p1], 2.2, shade_col((214, 180, 160), 0.5), taper=(0, 0))
    c.ink(rrect(1700, 330, 1860, 370, 6), (110, 30, 40), lw=2.8, shade=0.3, hi=0.3)
    c.text(1780, 350, "CAFE SNOOT", 19, (255, 236, 200), "Black")
    c.text(1780, 382, "espresso · opinions", 9, (255, 220, 160), "Italic")
    c.glow2(1780, 600, 200, GLOW, 0.4)

    # ---------------- overhead: cables across the street, a pigeon on the wire
    cable(c, (-20, 120), (980, 160), sag=50, w=5, col=(30, 20, 50))
    cable(c, (980, 160), (1940, 110), sag=60, w=5, col=(30, 20, 50))
    string_lights2(c, [(780, 200), (1100, 170)], sag=40, seed=13)
    for x_ in (420, 1520):
        y_ = 182 if x_ < 980 else 210
        c.ink(blob([(x_ - 14, y_), (x_ - 10, y_ - 14), (x_ + 6, y_ - 16), (x_ + 14, y_ - 26), (x_ + 22, y_ - 22), (x_ + 18, y_ - 8), (x_ + 14, y_)], 2),
              (150, 150, 176), lw=2.2, shade=0.4, hi=0.3)
    cobweb(c, 252, 182, 60, "tl", opacity=0.35)
    # trash can, bollards at the back edge of the sidewalk
    tcx, tcy = 1060, 740
    c.soft(ell(tcx, tcy + 2, 36, 8), (24, 6, 34), 0.5, 5)
    c.ink(Sh([[(tcx - 28, tcy - 80), (tcx + 28, tcy - 80), (tcx + 22, tcy), (tcx - 22, tcy)]]), (60, 130, 140), lw=2.8, shade=0.45, hi=0.3)
    c.ink(ell(tcx, tcy - 82, 32, 8), (50, 110, 120), lw=2.6, shade=0.2, hi=0.3)
    c.ink(blob([(tcx - 10, tcy - 96), (tcx + 14, tcy - 100), (tcx + 18, tcy - 84), (tcx - 14, tcy - 84)], 1), (250, 240, 200), lw=1.8)
    # a few warm window pools from the gallery and club
    floor_pool(c, 1300, 790, 380, 60, (255, 80, 190), 0.35)
    floor_pool(c, 630, 760, 220, 40, (200, 230, 255), 0.25)
    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 260, 420, 0.45), ((dx0 + dx1) / 2, 640, 280, 0.35, (210, 230, 255)),
                          (1300, 600, 420, 0.4, (255, 90, 190)), (1780, 620, 260, 0.4), (130, 600, 200, 0.25, (120, 200, 255))],
               ambient=0.92, vign=0.55, top_dark=0.25, bottom_dark=0.4, shadow_tint=(80, 40, 130))
    for x_, y_ in lamps:
        c.glow2(x_, y_, 140, GLOW, 0.5)
    c.painterly(0.05)

    def fg(sub):
        hydrant(sub, 70, 1086, 1.5, FG)
        sub.ink(rrect(1700, 960, 1840, 1100, 10), FG, lw=0, shade=0.2, hi=0.2)       # newspaper box
        sub.ink(rect(1712, 980, 1828, 1030), mix(FG, (60, 40, 90), 0.5), lw=0)
        for X in (1880, 1940):
            sub.ink(rrect(X - 16, 990, X + 16, 1100, 12), FG, lw=0, shade=0.2, hi=0.2)
        fg_plant(sub, 420, 1110, 200, seed=55)
        fg_cable(sub, [(700, 1100), (1000, 1070), (1300, 1100)], 14)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_uptown.png")


LAYOUT["uptown"] = dict(
    walk_px=[(30, Y_TOP), (1890, Y_TOP), (1900, 900), (1860, Y_BOT), (110, Y_BOT), (30, 900)],
    hotspots={
        ("Campus shuttle", 0): dict(box=(20, 440, 240, 710), stand=(170, 800)),
        ("Gallery Pierre", 0): dict(box=(545, 440, 715, 705), stand=(630, 795)),
        ("Mimi", 0): dict(npc="hs_mimi", feet=(820, FEET_Y), stand=(650, 935)),
        ("Jett Vex poster", 0): dict(box=(945, 365, 1075, 545), stand=(1010, 790)),
        ("Club Velour", 0): dict(box=(1180, 390, 1420, 705), stand=(1300, 800)),
        ("Brutus", 0): dict(npc="hs_brutus", feet=(1530, FEET_Y), w=2.2, stand=(1360, 935)),
        ("Cafe Snoot", 0): dict(box=(1685, 400, 1875, 705), stand=(1780, 800)),
    },
    entries={"from_campus": (180, 880), "from_gallery": (630, 830), "from_club": (1300, 830), "from_cafe": (1760, 870)})


# =========================================================================== layout -> act5.json, composites
NPC_REL = {"hs_mimi": 0.9, "hs_brutus": 1.13, "hs_pierre": 0.96, "hs_jett_vex": 0.92, "hs_anton": 0.97,
           "hs_vivian_quill": 0.91, "hs_grizz": 1.06}
NPC_FN = {"hs_mimi": paint_mimi, "hs_brutus": paint_brutus, "hs_pierre": paint_pierre, "hs_jett_vex": paint_jett_vex,
          "hs_anton": paint_anton, "hs_vivian_quill": paint_vivian_quill, "hs_grizz": paint_grizz}


def npc_height(npc):
    """Crown height (px) for an NPC sprite, from the depth scale at its feet."""
    for rid, L in LAYOUT.items():
        for key, h in L["hotspots"].items():
            if h.get("npc") == npc:
                return round(DEX_H * depth_scale(h["feet"][1], Y_TOP, Y_BOT) * NPC_REL[npc])
    return round(DEX_H * 0.94 * NPC_REL.get(npc, 1.0))


def paint_npc(npc):
    return NPC_FN[npc](height=npc_height(npc))


def _sprite_size(name):
    return Image.open(os.path.join(OUT_DIR, name + ".png")).size


def write_layout(path=JSON_PATH):
    """Write walkable / feet / size / standAt / entry pos from LAYOUT. Nothing else in the file changes."""
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
                bw = spec.get("w", 1.9) if "npc" in spec else spec.get("w", round(w / 100, 2))
                h["feet"] = list(px_to_world(fx, fy))
                h["size"] = [bw, round(spec.get("h", hh) / 100, 2)]
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
    """Background + hotspot sprites at their feet (unscaled, like the game) + Dex (depth-scaled) at the two
    front-most stand points and at the back of the walkable area, with hotspot boxes and the walkable outline.
    flags: show the showWhenFlag sprites for these flags instead of the hideWhenFlag ones."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(JSON_PATH))
    room = [r for r in data["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))
    items = []

    def visible(h):
        if h.get("showWhenFlag"):
            return h["showWhenFlag"] in flags
        if h.get("hideWhenFlag"):
            return h["hideWhenFlag"] not in flags
        return True
    for h in room["hotspots"]:
        if not visible(h):
            continue
        slug = re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx))
    stands = [world_to_px(*h["standAt"]) for h in room["hotspots"] if not h.get("showWhenFlag")]
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
            col = (255, 230, 60, 255) if not h.get("showWhenFlag") else (120, 200, 255, 255)
            d.rectangle([fx - w / 2, fy - hh, fx + w / 2, fy], outline=col, width=3)
            sx, sy = world_to_px(*h["standAt"])
            d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 80, 80, 255))
            d.text((fx - w / 2 + 4, fy - hh + 4), h["name"], fill=col)
        for e in room.get("entries", []):
            ex, ey = world_to_px(*e["pos"])
            d.rectangle([ex - 6, ey - 6, ex + 6, ey + 6], fill=(80, 160, 255, 255))
        bg.alpha_composite(ov)
    out = os.path.join(out_dir, "composite_%s%s.png" % (room_id, "_" + "_".join(flags) if flags else ""))
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


ROOM_IDS = ["uptown", "art_gallery", "nightclub", "cafe_snoot", "velour_backstage"]


def contact_sheets(out_dir=None):
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    ims = [Image.open(os.path.join(OUT_DIR, "bg_%s.png" % r)).convert("RGB").resize((960, 540), Image.LANCZOS) for r in ROOM_IDS]
    sheet = Image.new("RGB", (1920, 540 * 3), (20, 10, 30))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sp = [n for n in SPRITES] + ["player_dex", "hs_roxy_vale"]
    sims = [Image.open(os.path.join(OUT_DIR, n + ".png")) for n in sp]
    H = max(i.height for i in sims) + 20
    strip = Image.new("RGBA", (sum(i.width for i in sims) + 16 * len(sims) + 16, H), (110, 90, 130, 255))
    x = 16
    for im in sims:
        strip.alpha_composite(im, (x, H - 10 - im.height))
        x += im.width + 16
    k = min(1.0, 960 / strip.width) if False else 960 / strip.width
    strip = strip.convert("RGB").resize((960, int(H * k)), Image.LANCZOS)
    sheet.paste(strip, (960, 1080 + (540 - strip.height) // 2))
    out = os.path.join(out_dir, "final_bgs.jpg")
    sheet.save(out, quality=90)
    print("wrote", out)


# =========================================================================== 2. Gallery Pierre
GAL_CANVAS = (820, 615, 300, 262)       # centre x, bottom y, w, h of the hung canvas (sprites hs_blank_canvas / hs_something_no_1)


def bronze_man(c, fx, fy, h):
    """'Man Waiting For Text Back': a bronze figure hunched over his phone (original statue)."""
    BR = (150, 120, 80)
    b = Body(c, fx, fy, h, skin=BR,
             build=dict(shoulders=1.0, waist=1.0, hips=0.95, limbs=1.0, head=1.0, legs=1.0, neck=0.9, belly=1.0),
             pose=dict(arm_n=10, fore_n=110, arm_f=14, fore_f=100, leg_n=-4, shin_n=2, leg_f=6, shin_f=-2, lean=10,
                       head_dx=1.4, head_dy=-3.0), seed=21)
    k = dict(lw=2.6, shade=0.55, scol=(70, 50, 40), hi=0.55, hcol=(255, 220, 150), rim=0.25, rcol=(120, 200, 180), tex=0.18)
    c.ink(b.arm_shape(False), shade_col(BR, 0.85), **{**k, "hi": 0.3})
    legs(b, BR, w=(8.0, 5.6, 5.0), scol=(70, 50, 40), shoe=lambda bb, near: bb.shoe(near, shade_col(BR, 0.8), shade_col(BR, 0.7), "shoe"))
    c.ink(b.neck_shape(), BR, **k)
    c.ink(Sh([b.torso_pts(slack=0.8, hem=b.hip_y - 3)]), BR, **k)
    c.ink(Sh([b.head_pts()]), BR, **k)
    fa = b.face_anchor()
    b.eyes(closed=True)
    c.stroke([(fa["mouth"][0] - b.r * 0.2, fa["mouth"][1]), (fa["mouth"][0] + b.r * 0.2, fa["mouth"][1] + 2)], 2.0, INK)
    c.ink(b.arm_shape(True), BR, **k)
    wx, wy = b.P(*b.wrist_n)
    c.ink(Sh([rot_pts([(wx - 2, wy - 22), (wx + 12, wy - 22), (wx + 12, wy + 2), (wx - 2, wy + 2)], -30, wx, wy)]), shade_col(BR, 0.7), lw=2.0)
    b.hand(True, "hold", col=BR, size=1.0, d=(0.4, -1.0))
    # verdigris drips
    for dx in (-6, 4, 10):
        c.stroke([(fx + dx, fy - h * 0.6), (fx + dx + 1, fy - h * 0.45)], 2.6, (110, 190, 170), opacity=0.6, taper=(0.2, 0.8))


def paint_art_gallery():
    c, R, rng = A1.std_room(5200, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (232, 182, 214)
    DADO = (60, 150, 160)

    def wall_paint(sub, w, h, seed):
        two_tone_wall(sub, w, h, WALL, DADO, seed, rail=(250, 220, 120), split=0.8, chips=2, stains=2)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (96, 66, 120), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        for y in np.arange(0, sub.h, 70 * sub.density):
            sub.stroke([(0, y), (sub.w, y)], 2.6, (80, 54, 104), taper=(0, 0))
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (60, 30, 50), 0.22, 0, rng.randint(0, 99))

    def floor(sub):
        planks(sub, (156, 96, 82), 0, 0, sub.w, sub.h, pw=64 * sub.density, seed=52, vertical=True)

    def left(sub):
        wall_paint(sub, sub.w, sub.h, 61)
        x0, x1 = sub.ax(330), sub.ax(150)
        y0, y1 = sub.by(300), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (60, 150, 160), frame=(250, 236, 244), knob="R", window=True, seed=5)
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 110, "EXIT")

    def right(sub):
        wall_paint(sub, sub.w, sub.h, 62)
        x0, x1 = sub.ax(40), sub.ax(190)
        y0, y1 = sub.by(400), sub.by(250)
        sub.ink(rect(x0 - 18, y0 - 18, x1 + 18, y1 + 18), (40, 30, 50), lw=3.0, shade=0.3, hi=0.3)
        sub.ink(rect(x0, y0, x1, y1), (250, 246, 236), lw=2.4, shade=0.2)
        sub.ink(ell((x0 + x1) / 2, (y0 + y1) / 2, 24, 24), (220, 40, 60), lw=2.0, shade=0.3, hi=0.3)
        sub.ink(rrect((x0 + x1) / 2 - 50, y1 + 40, (x0 + x1) / 2 + 50, y1 + 64, 3), (250, 250, 250), lw=1.6)
        sub.text((x0 + x1) / 2, y1 + 52, "DOT (SAD)", 9, (60, 60, 90), "Bold")
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=5200)
    R.paint_plane("back", 0, Wb, 0, Hb, lambda sub: wall_paint(sub, sub.w, sub.h, 63), density=1.0, seed=63)
    R.ao(0.45)
    R.edges(w=4.0)

    # banner across the back wall
    ban = blob([P(300, 420), P(960, 420), P(940, 372), P(320, 372)], 1)
    c.ink(ban, (200, 40, 90), lw=3.0, shade=0.4, sw=14, hi=0.3)
    c.text(P(630, 396)[0], P(630, 396)[1], "OPENING NIGHT  ·  NOTHING: A RETROSPECTIVE", 17, (255, 240, 230))
    for X in (300, 960):
        c.stroke([P(X, 420), P(X, Hb)], 2.0, INK)
    # the canvas spot: picture hook, spotlit, a little card that says PRICELESS
    cx, by, cw, ch = GAL_CANVAS
    c.stroke([(cx, 250), (cx, by - ch - 6)], 1.6, (200, 200, 210), opacity=0.8)
    c.soft(rect(cx - cw / 2 - 10, by - ch - 10, cx + cw / 2 + 20, by + 14), (60, 20, 60), 0.12, 12)
    c.ink(rrect(cx + cw / 2 + 26, by - 76, cx + cw / 2 + 100, by - 30, 3), (252, 252, 250), lw=1.8, shade=0.2)
    c.text(cx + cw / 2 + 63, by - 62, "PRICELESS", 8, (190, 40, 60), "Bold")
    for k in range(2):
        c.stroke([(cx + cw / 2 + 36, by - 48 + k * 8), (cx + cw / 2 + 90 - k * 16, by - 48 + k * 8)], 1.4, (120, 120, 150), taper=(0, 0))
    # velvet rope in front of the canvas spot
    a1 = stanchion(c, *P(330, 0, 70), h=70)
    a2 = stanchion(c, *P(650, 0, 70), h=70)
    velvet_rope(c, a1, a2, 24)
    # sculpture on its pedestal (back left)
    R.contact(40, 150, 30, 120, 0.5)
    R.ink_box(40, 150, 0, 96, 30, 120, (246, 240, 244), seed=4)
    fx, fy = P(95, 96, 75)
    bronze_man(c, fx, fy, 236)
    c.ink(rrect(*P(60, 60, 120), *P(130, 34, 120), 3), (200, 170, 90), lw=1.6, shade=0.3, hi=0.4)
    # plinth with the "invisible key" (empty) and its card
    R.contact(720, 820, 40, 110, 0.5)
    pf = R.ink_box(720, 820, 0, 150, 40, 110, (250, 248, 250), seed=6)
    kx, ky = P(770, 150, 75)
    c.ink(ell(kx, ky, 22, 6), (255, 255, 255), lw=0, opacity=0.5)
    c.ink(rrect(*P(735, 112, 110), *P(805, 82, 110), 2), (250, 250, 236), lw=1.4)
    c.text(P(770, 97, 110)[0], P(770, 97, 110)[1], "UNTITLED (KEY)", 6, (60, 60, 90), "Bold")
    # art supplies cart (back right): FREE PAINT
    R.contact(1060, 1230, 40, 120, 0.5)
    cart = R.ink_box(1060, 1230, 40, 120, 40, 120, (60, 150, 160), seed=7)
    R.ink_box(1060, 1230, 46, 54, 40, 120, (50, 120, 130), seed=8)
    for X, Z in ((1075, 40), (1215, 40), (1075, 120), (1215, 120)):
        c.ink(ell(*P(X, 12, Z), 11, 11), (40, 36, 50), lw=2.2, hi=0.3)
        c.stroke([P(X, 24, Z), P(X, 40, Z)], 3, INK)
    for k, col in enumerate(((255, 70, 160), (90, 236, 110), (30, 26, 36), (255, 200, 60), (60, 140, 255))):
        x_, y_ = P(1080 + k * 30, 120, 70)
        c.ink(rrect(x_ - 8, y_ - 34, x_ + 8, y_, 3), col, lw=2.0, shade=0.4, hi=0.4)
        c.ink(rect(x_ - 4, y_ - 42, x_ + 4, y_ - 34), (210, 210, 220), lw=1.4)
    jx, jy = P(1215, 120, 60)
    c.ink(rrect(jx - 14, jy - 40, jx + 14, jy, 4), (200, 230, 240, 200), lw=2.0)
    for k in range(4):
        c.stroke([(jx - 6 + k * 4, jy - 20), (jx - 12 + k * 7, jy - 70)], 3, (150, 100, 60))
        c.ink(ell(jx - 12 + k * 7, jy - 74, 4, 6), [(255, 70, 160), (90, 236, 110), (60, 140, 255), (255, 200, 60)][k], lw=1.2)
    for k in range(3):                 # black smocks on the lower shelf
        x_, y_ = P(1090 + k * 44, 54, 100)
        c.ink(blob([(x_ - 18, y_ - 26), (x_ + 18, y_ - 26), (x_ + 20, y_), (x_ - 20, y_)], 1), (36, 32, 44), lw=2.0, shade=0.3, hi=0.3)
    sx_, sy_ = P(1150, 260, 40)
    c.stroke([P(1150, 120, 40), (sx_, sy_ + 50)], 4, INK)
    c.ink(Sh([rot_pts([(sx_ - 70, sy_ - 30), (sx_ + 70, sy_ - 30), (sx_ + 70, sy_ + 50), (sx_ - 70, sy_ + 50)], 4, sx_, sy_)]), (255, 236, 90),
          lw=2.6, shade=0.3, hi=0.3)
    c.text(sx_, sy_ - 8, "FREE PAINT!", 15, (200, 30, 80), angle=4)
    c.text(sx_, sy_ + 14, "take some.", 9, (60, 50, 90), "Bold", angle=4)
    c.text(sx_, sy_ + 32, "MAKE SOMETHING.", 9, (60, 50, 90), "Bold", angle=4)
    # cheese + wine table (clutter at the back right corner)
    R.contact(1200, 1255, 160, 220, 0.4)
    # ceiling: track rail with spotlights + cones on the art
    rail_y = Hb - 10
    c.stroke([P(80, rail_y, 140), P(1180, rail_y, 140)], 10, INK, taper=(0, 0))
    c.stroke([P(80, rail_y, 140), P(1180, rail_y, 140)], 5, (190, 190, 200), taper=(0, 0))
    spots = []
    for X, tgt in ((95, P(95, 160, 75)), (490, (cx, by - ch / 2)), (770, P(770, 150, 75)), (1150, P(1150, 200, 60))):
        x_, y_ = P(X, rail_y, 140)
        c.ink(Sh([rot_pts([(x_ - 12, y_), (x_ + 12, y_), (x_ + 16, y_ + 34), (x_ - 16, y_ + 34)], -14, x_, y_)]), (40, 36, 50), lw=2.4, shade=0.3, hi=0.4)
        c.light_cone((x_, y_ + 30), (tgt[0] - 150, tgt[1] + 120), (tgt[0] + 150, tgt[1] + 120), (255, 240, 210), 0.22, 30)
        spots.append((x_, y_ + 30))
    pipe(c, [P(0, Hb - 30, 300), P(Wb, Hb - 30, 300)], w=20, col=(170, 120, 190), brackets=[P(300, Hb - 30, 300), P(900, Hb - 30, 300)])
    hanging_cable(c, P(1000, Hb, 220), 90, sway=10, w=5, col=(40, 30, 70), seed=6)
    cobweb(c, *P(0, Hb, 0), 90, "tl")
    cobweb(c, *P(Wb, Hb, 0), 80, "tr", opacity=0.4)
    scuffs(c, 400, 1500, 690, 18, seed=3, opacity=0.2)
    # neon on the right wall
    nx, ny = P(Wb, 300, 190)
    neon(c, nx + 10, ny, "ART?", 40, (255, 80, 190), angle=-14)
    for (X, Z) in ((95, 200), (490, 160), (770, 190), (1150, 200)):
        x_, y_ = P(X, 0, Z)
        floor_pool(c, x_, y_, 180 * R.k(Z), 40 * R.k(Z), (255, 236, 200), 0.3)
    for (X, Z, col) in ((600, 360, (255, 220, 90)), (980, 420, (250, 250, 240)), (300, 520, (200, 40, 90))):    # cheese cube, napkin, ticket
        x_, y_ = P(X, 0, Z)
        k_ = R.k(Z)
        c.ink(Sh([[(x_ - 8 * k_, y_ - 4 * k_), (x_ + 9 * k_, y_ - 6 * k_), (x_ + 10 * k_, y_ + 3 * k_), (x_ - 7 * k_, y_ + 5 * k_)]]), col, lw=2.0,
              shade=0.3)
    room_grade(c, lights=[(cx, by - 120, 420, 0.4), (P(95, 160, 75)[0], 560, 260, 0.35), (P(770, 150, 75)[0], 620, 240, 0.3),
                          (130, 470, 220, 0.25, (90, 255, 160)), (1720, 420, 300, 0.3, (255, 90, 190))],
               ambient=0.94, vign=0.55, top_dark=0.4, bottom_dark=0.35)
    for x_, y_ in spots:
        c.glow2(x_, y_, 60, (255, 250, 220), 0.6)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 60, 1100, 330, seed=17)
        # cocktail table edge with wine glasses (bottom right)
        sub.ink(ell(1760, 1070, 220, 40), FG, lw=0, shade=0.2, hi=0.2)
        for X in (1690, 1760, 1830):
            sub.ink(blob([(X - 16, 1030), (X + 16, 1030), (X + 12, 1000), (X, 990), (X - 12, 1000)], 1), FG, lw=0, hi=0.4, hw=4)
            sub.stroke([(X, 1030), (X, 1050)], 4, FG)
        fg_cable(sub, [(500, 1100), (900, 1076), (1300, 1100)], 14)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_art_gallery.png")


def _canvas_base(c, cx, by, w, h):
    d = 14
    side = Sh([[(cx + w / 2, by - h), (cx + w / 2 + d, by - h + 5), (cx + w / 2 + d, by + 3), (cx + w / 2, by)]])
    c.soft(rect(cx - w / 2 + 8, by - h + 10, cx + w / 2 + 14, by + 8), (40, 10, 50), 0.35, 6)
    c.ink(side, (200, 196, 206), lw=2.8, shade=0.4, hi=0.2)
    face = rect(cx - w / 2, by - h, cx + w / 2, by)
    c.ink(face, (253, 252, 250), lw=3.0, shade=0.06, sw=40, hi=0.1, tex=0.03, ao=0.08)
    return face


def paint_blank_canvas(name="hs_blank_canvas.png"):
    cx, by, w, h = GAL_CANVAS
    c = C2(w + 80, h + 60, 521, lw=3.0, light=(-0.3, -0.95))
    x0, y1 = 30, h + 30
    face = _canvas_base(c, x0 + w / 2, y1, w, h)
    # canvas weave + the tiny upside-down signature in the top corner
    clip_draw(c, face, lambda t: [t.stroke([(x0, y), (x0 + w, y)], 1.0, (226, 222, 230), opacity=0.18, taper=(0, 0)) for y in range(int(y1 - h), int(y1), 6)])
    c.text(x0 + 30, y1 - h + 16, "Pierre?", 8, (90, 80, 110), "Italic", angle=180)
    sprite_grade(c, 0.93, (0.98, 0.92, 1.0))
    return finish_sprite(c, name, margin=2)


def paint_something_no_1(name="hs_something_no_1.png"):
    cx, by, w, h = GAL_CANVAS
    nw = 92
    c = C2(w + 80 + 2 * (nw + 30), h + 60, 522, lw=3.0, light=(-0.3, -0.95))
    x0, y1 = 30 + nw + 30, h + 30
    face = _canvas_base(c, x0 + w / 2, y1, w, h)
    rng = random.Random(7)
    pink, green, black = (255, 70, 160), (90, 236, 110), (30, 26, 36)

    def art(t):
        for _ in range(26):              # splatters
            x_, y_ = rng.uniform(x0, x0 + w), rng.uniform(y1 - h, y1)
            r_ = rng.uniform(3, 14)
            t.ink(ell(x_, y_, r_, r_ * rng.uniform(0.7, 1.1)), rng.choice([pink, green, black]), lw=0, shade=0.2, hi=0.3)
        for k in range(5):               # big loud strokes
            ya = y1 - h + rng.uniform(20, h - 20)
            t.stroke([(x0 - 10, ya), (x0 + w * 0.5, ya + rng.uniform(-40, 40)), (x0 + w + 10, ya + rng.uniform(-30, 30))], rng.uniform(10, 18),
                     [pink, green, pink, black, green][k], taper=(0.1, 0.4), opacity=0.9)
        bx, byy = x0 + w * 0.36, y1 - h * 0.5        # lightning bolt
        t.ink(Sh([[(bx + 30, byy - 110), (bx - 30, byy + 4), (bx + 4, byy + 4), (bx - 22, byy + 110), (bx + 50, byy - 20), (bx + 14, byy - 20),
                   (bx + 56, byy - 110)]]), (255, 236, 60), lw=3.0, shade=0.2, hi=0.3)
        hx_, hy_ = x0 + w * 0.76, y1 - h * 0.66      # heart
        t.ink(blob([(hx_, hy_ + 34), (hx_ - 38, hy_ - 4), (hx_ - 30, hy_ - 30), (hx_ - 6, hy_ - 30), (hx_, hy_ - 14), (hx_ + 6, hy_ - 30),
                    (hx_ + 30, hy_ - 30), (hx_ + 38, hy_ - 4)], 2), (230, 30, 70), lw=3.0, shade=0.3, hi=0.4)
        dx_, dy_ = x0 + w * 0.76, y1 - h * 0.26      # a doodle of Brutus: bald, shades, flat mouth
        t.ink(ell(dx_, dy_, 30, 34), (150, 100, 80), lw=2.6, shade=0.2)
        t.ink(rrect(dx_ - 24, dy_ - 10, dx_ + 24, dy_ + 4, 4), black, lw=1.6)
        t.stroke([(dx_ - 10, dy_ + 18), (dx_ + 10, dy_ + 18)], 2.6, black)
        t.text(x0 + 40, y1 - 18, "J.V.", 14, black, "Italic")
    clip_draw(c, face, art)
    outline(c, face)
    # Vivian's napkin, framed, beside it
    nx0, ny0 = x0 + w + 40, y1 - h + 30
    c.ink(rect(nx0, ny0, nx0 + nw, ny0 + nw * 1.1), (40, 30, 50), lw=2.8, shade=0.3, hi=0.4)
    c.ink(Sh([rot_pts([(nx0 + 12, ny0 + 12), (nx0 + nw - 12, ny0 + 12), (nx0 + nw - 12, ny0 + nw * 1.1 - 12), (nx0 + 12, ny0 + nw * 1.1 - 12)], 4,
                      nx0 + nw / 2, ny0 + nw * 0.55)]), (252, 250, 236), lw=1.8, shade=0.2)
    c.text(nx0 + nw / 2, ny0 + 34, "SOMETHING,", 9, (30, 26, 36), "Black", angle=4)
    c.text(nx0 + nw / 2, ny0 + 50, "FINALLY.", 10, (30, 26, 36), "Black", angle=4)
    c.text(nx0 + nw / 2, ny0 + 72, "* * * * *", 10, (200, 30, 70), "Black", angle=4)
    sprite_grade(c, 0.93, (0.98, 0.92, 1.0))
    return finish_sprite(c, name, margin=2)


LAYOUT["art_gallery"] = dict(
    walk_px=[(300, Y_TOP), (1620, Y_TOP), (1760, 900), (1700, Y_BOT), (240, Y_BOT), (170, 900)],
    hotspots={
        ("Exit", 0): dict(box=(20, 330, 200, 820), stand=(260, 880)),
        ("Sculpture", 0): dict(box=(350, 400, 500, 742), stand=(430, 800)),
        ("Blank canvas", 0): dict(sprite="hs_blank_canvas", feet=(GAL_CANVAS[0], GAL_CANVAS[1] + 4), stand=(820, 800)),
        ("Something No. 1", 0): dict(sprite="hs_something_no_1", feet=(GAL_CANVAS[0], GAL_CANVAS[1] + 4), w=3.3, stand=(820, 800)),
        ("Plinth", 0): dict(box=(1040, 520, 1150, 752), stand=(1080, 800)),
        ("Pierre", 0): dict(npc="hs_pierre", feet=(1290, FEET_Y), stand=(1120, 935)),
        ("Art supplies", 0): dict(box=(1390, 470, 1600, 752), stand=(1480, 800)),
    },
    entries={"from_street": (280, 880)})


# =========================================================================== 3. Club Velour (nightclub)
CLUB_BALL = (430, 360, 200)          # disco ball (X, Y, Z) in room space


def disco_ball(c, x, y, r, rng):
    c.glow2(x, y, r * 3.2, (200, 220, 255), 0.35)
    ball = ell(x, y, r, r)
    c.ink(ball, (170, 176, 210), lw=3.0, shade=0.55, sw=r * 0.6, scol=(80, 70, 140), hi=0.5, hw=r * 0.3, rim=0.3)

    def tiles_(t):
        for yy in np.arange(y - r, y + r, r * 0.16):
            for xx in np.arange(x - r, x + r, r * 0.16):
                v = rng.random()
                col = (255, 255, 255) if v < 0.12 else (255, 120, 220) if v < 0.2 else (120, 230, 255) if v < 0.28 else (60, 56, 100)
                t.ink(rect(xx + 1, yy + 1, xx + r * 0.16 - 1, yy + r * 0.16 - 1), col, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0,
                      opacity=0.55 if v > 0.28 else 0.9)
    clip_draw(c, ball, tiles_)
    c.ink(ball, (0, 0, 0, 0), lw=3.0, line_only=True)
    c.stroke([(x, y - r), (x, 0)], 3, INK, taper=(0, 0))
    for k in range(10):
        a = rng.uniform(0, 2 * math.pi)
        L = rng.uniform(r * 1.2, r * 2.4)
        sx, sy = x + math.cos(a) * L, y + math.sin(a) * L
        c.stroke([(sx - 7, sy), (sx + 7, sy)], 2, (255, 255, 255), opacity=0.9)
        c.stroke([(sx, sy - 7), (sx, sy + 7)], 2, (255, 255, 255), opacity=0.9)


def paint_nightclub():
    c, R, rng = A1.std_room(5300, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (120, 40, 120)
    LOW = (60, 24, 80)

    def wall_paint(sub, w, h, seed):
        two_tone_wall(sub, w, h, WALL, LOW, seed, rail=(255, 90, 190), split=0.7, chips=4, stains=3)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (40, 22, 60), lw=0, shade=0, hi=0, ao=0, tex=0.3, wob=0)
        for x in np.arange(0, sub.w, 120 * sub.density):
            sub.stroke([(x, 0), (x, sub.h)], 6, (26, 14, 40), taper=(0, 0))

    def floor(sub):
        sz = 56 * sub.density
        cols = [(220, 60, 150), (50, 180, 200), (130, 70, 200), (220, 170, 60)] + [(44, 32, 70), (36, 26, 58), (50, 36, 80)] * 3
        sub.ink(rect(0, 0, sub.w, sub.h), (20, 14, 30), lw=0, shade=0, hi=0, ao=0)
        rr = random.Random(9)
        for y in np.arange(0, sub.h, sz):
            for x in np.arange(0, sub.w, sz):
                col = rr.choice(cols)
                sub.ink(rrect(x + 3, y + 3, x + sz - 3, y + sz - 3, 4), col, lw=0, shade=0.3, sw=sz * 0.2, hi=0.4, hw=sz * 0.1, ao=0, tex=0.15,
                        wob=0.3)
                if col[0] > 60 or col[1] > 60:
                    sub.glow2(x + sz / 2, y + sz / 2, sz * 0.9, col, 0.18)
        for _ in range(12):
            stain(sub, rr.uniform(0, sub.w), rr.uniform(0, sub.h), rr.uniform(20, 50), (20, 10, 20), 0.18, 0, rr.randint(0, 99))

    def left(sub):
        wall_paint(sub, sub.w, sub.h, 71)
        x0, x1 = sub.ax(330), sub.ax(150)
        y0, y1 = sub.by(300), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (40, 120, 130), frame=(30, 20, 40), knob="R", seed=7)
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 110, "EXIT")
        for k in range(3):
            poster(sub, sub.ax(420 + k * 120), sub.by(330 - (k % 2) * 30), 80, 110, [(255, 220, 90), (90, 220, 255), (255, 120, 200)][k],
                   angle=rng.uniform(-6, 6), seed=70 + k, peel="br" if k == 1 else None,
                   draw=lambda t, w, h: [t.stroke([(10, 20 + j * 16), (w - 10, 20 + j * 16)], 5, (40, 30, 60), opacity=0.6) for j in range(5)])

    def right(sub):
        wall_paint(sub, sub.w, sub.h, 72)
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=5300)
    R.paint_plane("back", 0, Wb, 0, Hb, lambda sub: wall_paint(sub, sub.w, sub.h, 73), density=1.0, seed=73)
    R.ao(0.55)
    R.edges(w=4.0)

    # ---- bar (back left): shelves of glowing bottles, counter, stools
    for k, Y in enumerate((300, 230)):
        x0_, y0_ = P(20, Y)
        x1_, _ = P(330, Y)
        shelf(c, x0_, x1_, y0_, 16, (90, 50, 90))
        xx = x0_ + 14
        while xx < x1_ - 20:
            col = rng.choice([(255, 80, 180), (90, 236, 110), (90, 200, 255), (255, 210, 80), (190, 120, 255)])
            hh = rng.uniform(34, 56)
            c.ink(blob([(xx - 8, y0_), (xx - 8, y0_ - hh * 0.6), (xx - 3, y0_ - hh * 0.75), (xx - 3, y0_ - hh), (xx + 3, y0_ - hh), (xx + 3, y0_ - hh * 0.75),
                        (xx + 8, y0_ - hh * 0.6), (xx + 8, y0_)], 1), col, lw=2.0, shade=0.4, hi=0.5, hw=2)
            c.glow2(xx, y0_ - hh * 0.4, 24, col, 0.3)
            xx += rng.uniform(20, 28)
    nx, ny = P(175, 380)
    neon(c, nx, ny, "COCKTAILS", 30, (255, 80, 190), "Italic", angle=-3)
    R.contact(0, 350, 30, 110, 0.6)
    bar = R.ink_box(0, 350, 0, 110, 30, 110, (110, 40, 70), seed=9)
    R.ink_box(-6, 356, 110, 120, 24, 116, (60, 160, 170), seed=10)
    fr = bar["front"]
    c.light_cone(((fr[0][0] + fr[1][0]) / 2, fr[0][1] + 14), (fr[0][0], fr[3][1]), (fr[1][0], fr[2][1]), (255, 80, 190), 0.15, 10)
    c.stroke([(fr[0][0] + 6, fr[0][1] + 16), (fr[1][0] - 6, fr[1][1] + 16)], 4, (255, 120, 210), taper=(0, 0))
    c.glow2((fr[0][0] + fr[1][0]) / 2, fr[0][1] + 16, 220, (255, 80, 190), 0.3, sy=0.2)
    for X in (60, 170, 280):
        x_, y_ = P(X, 0, 140)
        c.stroke([(x_, y_), (x_, y_ - 66)], 5, INK, taper=(0, 0))
        c.ink(ell(x_, y_ - 70, 26, 9), (220, 50, 110), lw=2.6, shade=0.3, hi=0.4)
        c.ink(ell(x_, y_ - 26, 14, 4), (0, 0, 0, 0), lw=2.4, line_only=True)
    for k, col in enumerate(((90, 236, 110), (255, 200, 60))):
        x_, y_ = P(110 + k * 140, 120, 70)
        c.ink(Sh([[(x_ - 12, y_ - 26), (x_ + 12, y_ - 26), (x_, y_ - 10)]]), col, lw=1.8, shade=0.2, hi=0.4)
        c.stroke([(x_, y_ - 10), (x_, y_)], 2, (220, 220, 230))

    # ---- backstage door (black, propped open with a guitar case)
    dx0, dy0 = P(380, 300)
    dx1, dy1 = P(480, 0)
    c.ink(rect(dx0 - 12, dy0 - 12, dx1 + 12, dy1), (30, 20, 40), lw=3.0, shade=0.3)
    c.ink(rect(dx0, dy0, dx1, dy1), ("v", (255, 210, 140), (150, 90, 80)), lw=2.4, shade=0.2)
    c.ink(Sh([[(dx0, dy0), (dx0 + 34, dy0 + 14), (dx0 + 34, dy1 + 8), (dx0, dy1)]]), (36, 32, 44), lw=2.6, shade=0.3, hi=0.3)
    c.ink(rrect(dx0 + 40, dy0 + 40, dx1 - 6, dy0 + 90, 4), (40, 36, 50), lw=2.0)
    c.text((dx0 + dx1) / 2 + 18, dy0 + 56, "BACKSTAGE", 8, (255, 236, 140), "Bold")
    c.text((dx0 + dx1) / 2 + 18, dy0 + 74, "CREW ONLY", 7, (220, 220, 230), "Bold")
    gc = blob([(dx0 + 24, dy1 + 6), (dx0 + 12, dy1 - 70), (dx0 + 20, dy1 - 120), (dx0 + 44, dy1 - 130), (dx0 + 56, dy1 - 100), (dx0 + 50, dy1 - 60),
               (dx0 + 58, dy1 + 6)], 2)
    c.ink(gc, (40, 34, 30), lw=2.6, shade=0.4, hi=0.4)
    c.ink(rrect(dx0 + 26, dy1 - 40, dx0 + 52, dy1 - 30, 2), (200, 180, 100), lw=1.4)
    c.ink(ell(dx0 + 36, dy1 - 90, 9, 7), (255, 120, 200), lw=1.4)
    c.glow2((dx0 + dx1) / 2, dy1 - 60, 120, GLOW, 0.3)

    # ---- the stage (back centre): curtains, THE FINALS sign, footlights
    sX0, sX1 = 520, 1020
    q = R.quad("back", sX0, sX1, 60, 420)
    for k in range(9):
        t0, t1 = k / 9, (k + 1) / 9
        xa = q[0][0] + (q[1][0] - q[0][0]) * t0
        xb = q[0][0] + (q[1][0] - q[0][0]) * t1
        top_, bot_ = q[3][1], q[0][1]
        c.ink(Sh([[(xa, top_), (xb, top_), (xb + 3, bot_), (xa - 3, bot_)]]), (170, 20, 60) if k % 2 else (140, 14, 50), lw=2.4,
              shade=0.5, sw=18, hi=0.35, hw=6, tex=0.15, wob=0.6)
        c.stroke([((xa + xb) / 2, top_ + 10), ((xa + xb) / 2 + 2, bot_ - 4)], 2.4, (90, 6, 36), opacity=0.7)
    top_ = q[3][1]
    c.ink(blob([(q[0][0] - 20, top_ - 10), (q[1][0] + 20, top_ - 10), (q[1][0] + 10, top_ + 50), ((q[0][0] + q[1][0]) / 2, top_ + 30),
                (q[0][0] - 10, top_ + 50)], 2), (200, 30, 70), lw=3.0, shade=0.5, sw=14, hi=0.4)
    q = [(x_, top_ if i < 2 else y_) for i, (x_, y_) in enumerate([q[3], q[2], q[1], q[0]])]
    sg = rrect(q[0][0] + 70, q[0][1] + 60, q[1][0] - 70, q[0][1] + 180, 10)
    c.ink(sg, (30, 20, 44), lw=3.0, shade=0.2, hi=0.2)
    for k in range(18):
        t_ = k / 17
        for yy in (q[0][1] + 66, q[0][1] + 174):
            x_ = q[0][0] + 80 + t_ * (q[1][0] - q[0][0] - 160)
            c.ink(ell(x_, yy, 4, 4), (255, 240, 200), lw=1.2)
            c.glow2(x_, yy, 14, GLOW, 0.4)
    neon(c, (q[0][0] + q[1][0]) / 2, q[0][1] + 96, "SPEED DATERS LIVE", 24, (110, 220, 255))
    neon(c, (q[0][0] + q[1][0]) / 2, q[0][1] + 142, "THE FINALS", 44, (255, 220, 80))
    R.contact(sX0 - 20, sX1 + 20, 0, 130, 0.6)
    R.ink_box(sX0 - 20, sX1 + 20, 0, 52, 0, 130, (70, 40, 90), top=(110, 70, 120), seed=11)
    for k in range(10):
        x_, y_ = P(sX0 + k * (sX1 - sX0) / 9, 36, 130)
        c.ink(ell(x_, y_, 6, 5), (255, 236, 160), lw=1.4)
        c.glow2(x_, y_, 22, GLOW, 0.45)
    mx_, my_ = P(770, 52, 60)
    c.stroke([(mx_, my_), (mx_, my_ - 120)], 4, INK, taper=(0, 0))
    c.ink(ell(mx_, my_, 18, 5), (40, 40, 50), lw=2.0)
    c.ink(rrect(mx_ - 8, my_ - 140, mx_ + 8, my_ - 116, 6), (180, 180, 200), lw=2.0, shade=0.4, hi=0.5)
    for X in (sX0 + 40, sX1 - 40):           # speaker stacks on stage
        R.ink_box(X - 40, X + 40, 52, 190, 20, 80, (40, 36, 50), seed=12)
        for Yc in (90, 150):
            c.ink(ell(*P(X, Yc, 80), 22, 22), (24, 20, 30), lw=2.2, hi=0.3)

    # ---- VIP booth (back right + right wall): curved red couch, little table, VIP neon
    R.contact(1060, Wb, 20, 260, 0.6)
    R.ink_box(1060, Wb, 0, 150, 0, 40, (170, 30, 70), seed=13)
    R.ink_box(Wb - 50, Wb, 0, 150, 40, 260, (150, 24, 60), seed=14)
    R.ink_box(1060, Wb - 50, 30, 60, 40, 110, (200, 40, 90), top=(230, 70, 120), seed=15)
    for k in range(5):
        c.ink(ell(*P(1080 + k * 36, 110, 10), 4, 4), (240, 200, 90), lw=1.0)
    tx_, ty_ = P(1130, 70, 170)
    c.stroke([(tx_, ty_), P(1130, 0, 170)], 5, INK, taper=(0, 0))
    c.ink(ell(tx_, ty_, 44, 10), (230, 190, 80), lw=2.6, shade=0.3, hi=0.5)
    c.ink(rrect(tx_ - 6, ty_ - 30, tx_ + 6, ty_ - 8, 3), (60, 200, 220, 220), lw=1.6)
    c.ink(ell(tx_ + 20, ty_ - 6, 10, 4), (90, 236, 110), lw=1.4)          # bowl of green gummies
    vx, vy = P(1160, 330)
    neon(c, vx, vy, "VIP", 50, (255, 210, 80))
    c.stroke([P(1060, 270), P(Wb - 10, 270)], 4, (255, 210, 80))
    # ---- ceiling: lighting truss, coloured spots, the disco ball
    c.stroke([P(0, Hb - 20, 160), P(Wb, Hb - 20, 160)], 16, INK, taper=(0, 0))
    c.stroke([P(0, Hb - 20, 160), P(Wb, Hb - 20, 160)], 9, (150, 150, 170), taper=(0, 0))
    spots = []
    for X, col, tgt in ((160, (255, 80, 190), P(200, 0, 300)), (640, (110, 220, 255), P(770, 0, 300)), (900, (255, 210, 80), P(770, 40, 120)),
                        (1200, (190, 120, 255), P(1100, 0, 320))):
        x_, y_ = P(X, Hb - 20, 160)
        c.ink(Sh([[(x_ - 14, y_), (x_ + 14, y_), (x_ + 18, y_ + 34), (x_ - 18, y_ + 34)]]), (40, 36, 50), lw=2.4, shade=0.3, hi=0.4)
        c.light_cone((x_, y_ + 30), (tgt[0] - 200, tgt[1]), (tgt[0] + 200, tgt[1]), col, 0.22, 30)
        spots.append((x_, y_ + 32, col))
    bx_, by_ = P(*CLUB_BALL)
    disco_ball(c, bx_, by_, 56, random.Random(3))
    cobweb(c, *P(0, Hb, 0), 90, "tl", opacity=0.4)
    cobweb(c, *P(Wb, Hb, 0), 100, "tr", opacity=0.4)
    cable(c, P(0, Hb, 300), P(600, Hb, 360), sag=70, w=7, col=(30, 20, 50))
    hanging_cable(c, P(1100, Hb, 240), 120, sway=12, w=6, col=(30, 20, 50), seed=3)
    room_grade(c, lights=[(bx_, by_, 420, 0.3, (200, 220, 255)), (P(770, 100)[0], 560, 460, 0.35, (255, 120, 160)),
                          (P(175, 200)[0], 560, 320, 0.4, (255, 80, 190)), (1500, 560, 320, 0.35, (255, 210, 80)), (130, 480, 200, 0.25, (90, 255, 160))],
               ambient=0.86, vign=0.62, top_dark=0.45, bottom_dark=0.3, sat=1.15)
    for x_, y_, col in spots:
        c.glow2(x_, y_, 70, col, 0.6)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1620, 1090, 6, 1.1, seed=31)
        fg_chair_back(sub, 60, 900, 280, 300)
        fg_cable(sub, [(300, 1100), (700, 1060), (1100, 1080), (1500, 1110)], 18)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_nightclub.png")


def _club_ball_box():
    R = Room(None, (960, vp_for_walk(Y_TOP, Y_BOT)), (330, 250, 1590, 690), fc=1000)
    x, y = R.pt(*CLUB_BALL)
    return (round(x - 62), round(y - 62), round(x + 62), round(y + 62))


LAYOUT["nightclub"] = dict(
    walk_px=[(300, Y_TOP), (1620, Y_TOP), (1760, 900), (1700, Y_BOT), (240, Y_BOT), (170, 900)],
    hotspots={
        ("Exit", 0): dict(box=(20, 330, 200, 820), stand=(260, 880)),
        ("Bar", 0): dict(box=(330, 470, 720, 760), stand=(540, 800)),
        ("Disco ball", 0): dict(box=_club_ball_box(), stand=(720, 830)),
        ("Stage", 0): dict(box=(840, 500, 1380, 762), stand=(1110, 800)),
        ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1090, FEET_Y), w=1.6, stand=(930, 935)),
        ("Jett Vex", 0): dict(npc="hs_jett_vex", feet=(1620, FEET_Y), stand=(1450, 935)),
        ("Backstage door", 0): dict(box=(720, 400, 820, 694), stand=(770, 790)),
    },
    entries={"from_street": (280, 880), "from_backstage": (770, 815)})


# =========================================================================== 4. Cafe Snoot terrace
CAFE_PERCH = (975, 548)            # Mr. Pemberton's feet on the rim of the tall urn planter (px)


def bistro_table(c, x, y, s=1.0, top=(240, 236, 230), card=True, chairs=True):
    if chairs:
        for dx in (-1, 1):
            cx_ = x + dx * 62 * s
            c.stroke([(cx_, y), (cx_ + dx * 4 * s, y - 50 * s)], 4 * s, INK, taper=(0, 0))
            c.stroke([(cx_ - dx * 22 * s, y), (cx_ - dx * 18 * s, y - 46 * s)], 4 * s, INK, taper=(0, 0))
            c.ink(ell(cx_ - dx * 9 * s, y - 48 * s, 24 * s, 7 * s), (60, 150, 160), lw=2.2, shade=0.3, hi=0.4)
            c.ink(Sh([[(cx_ + dx * 2 * s, y - 50 * s), (cx_ + dx * 8 * s, y - 50 * s), (cx_ + dx * 14 * s, y - 110 * s), (cx_ + dx * 6 * s, y - 110 * s)]]),
                  (50, 130, 140), lw=2.2, shade=0.3)
            c.ink(ell(cx_ + dx * 10 * s, y - 108 * s, 14 * s, 6 * s), (60, 150, 160), lw=2.0)
    c.soft(ell(x, y + 2, 50 * s, 8 * s), (24, 6, 34), 0.45, 5)
    c.stroke([(x, y), (x, y - 70 * s)], 6 * s, INK, taper=(0, 0))
    c.stroke([(x, y), (x, y - 70 * s)], 3 * s, (150, 140, 160), taper=(0, 0))
    c.ink(ell(x, y - 2, 22 * s, 5 * s), (60, 56, 70), lw=2.0)
    c.ink(ell(x, y - 72 * s, 46 * s, 11 * s), top, lw=2.6, shade=0.3, hi=0.4)
    if card:
        c.ink(Sh([[(x - 12 * s, y - 76 * s), (x + 12 * s, y - 76 * s), (x + 8 * s, y - 96 * s), (x - 8 * s, y - 96 * s)]]), (252, 250, 240), lw=1.6, shade=0.2)
        c.text(x, y - 86 * s, "RSVD", max(4, 6 * s), (190, 40, 60), "Bold")


def paint_cafe_snoot():
    c, R, rng = outdoor_room(5400)
    P = R.pt
    HOR = 700
    city_sky(c, HOR, 5401, top=(26, 14, 64), bot=(120, 50, 120))
    sidewalk(c, R, 5402, c1=(176, 150, 160), c2=(150, 120, 140), grout=(100, 70, 96), size=70)
    # terrace floor: checker of warm/cool slabs in a band in front of the cafe
    for _ in range(18):
        x_, y_ = rng.uniform(0, W_BG), rng.uniform(720, 1000)
        c.soft(ell(x_, y_, rng.uniform(30, 90), rng.uniform(8, 20)), (60, 20, 60), 0.14, 10)

    # ---- left: stone wall with the archway back to the street
    brick_block(c, -30, 160, 250, HOR, (150, 70, 96), seed=11)
    ring = Sh([[(30, HOR), (30, 520)] + [(125 + 95 * math.cos(math.radians(a)), 520 - 95 * math.sin(math.radians(a))) for a in range(180, -1, -10)] + [(220, HOR)]])
    c.ink(ring, (214, 180, 170), lw=3.2, shade=0.45, sw=20, hi=0.35, tex=0.25)
    arch = Sh([[(52, HOR), (52, 520)] + [(125 + 73 * math.cos(math.radians(a)), 520 - 73 * math.sin(math.radians(a))) for a in range(180, -1, -10)] + [(198, HOR)]])
    c.ink(arch, ("v", (40, 24, 70), (110, 60, 120)), lw=3.2, shade=0.2, hi=0)
    clip_draw(c, arch, lambda t: (night_sky(t, 40, 440, 210, 640, seed=3, skyline=True, moon=False),
                                  t.ink(rect(40, 640, 210, HOR), (120, 90, 120), lw=0, shade=0, hi=0)))
    c.ink(arch, (0, 0, 0, 0), lw=3.2, line_only=True)
    c.ink(rrect(50, 380, 200, 410, 5), (40, 110, 160), lw=2.6, shade=0.3, hi=0.3)
    c.text(125, 395, "UPTOWN  ->", 12, (255, 255, 240), "Black")

    # ---- the cafe facade
    fx0, fx1 = 250, 1960
    c.ink(rect(fx0, 150, fx1, HOR), (214, 120, 150), lw=3.2, shade=0.35, sw=60, hi=0.25, tex=0.22)
    for _ in range(5):
        chip(c, rng.uniform(fx0 + 40, fx1 - 40), rng.uniform(170, 330), rng.uniform(22, 40), BRICK, MORTAR, (214, 120, 150), seed=rng.randint(0, 99))
    for _ in range(3):
        stain(c, rng.uniform(fx0, fx1), rng.uniform(180, 300), rng.uniform(40, 70), (90, 30, 70), 0.18, 2, rng.randint(0, 99))
    for k in range(5):                                         # upper windows with shutters + flower boxes
        wx = fx0 + 130 + k * 340
        c.ink(rect(wx - 50, 190, wx + 50, 300), (255, 206, 120) if k % 2 == 0 else (70, 40, 90), lw=2.6, shade=0.3, hi=0.2)
        c.stroke([(wx, 190), (wx, 300)], 2.4, (240, 230, 220))
        for sx_ in (-1, 1):
            c.ink(rect(wx + sx_ * 52, 186, wx + sx_ * 86, 304), (50, 130, 130), lw=2.4, shade=0.4, hi=0.3)
            for yy in range(196, 300, 12):
                c.stroke([(wx + sx_ * 56, yy), (wx + sx_ * 82, yy + 4)], 1.4, (30, 90, 90), opacity=0.7)
        c.ink(rect(wx - 60, 300, wx + 60, 322), (110, 50, 60), lw=2.4, shade=0.3)
        for j in range(6):
            c.ink(ell(wx - 50 + j * 20, 296, 9, 8), rng.choice([(255, 90, 150), (255, 220, 90), (90, 200, 120)]), lw=1.6)
    c.ink(rect(fx0 - 10, 340, fx1 + 10, 362), (110, 30, 50), lw=2.8, shade=0.3, hi=0.3)
    c.ink(rrect(720, 366, 1200, 412, 6), (110, 30, 50), lw=3.0, shade=0.3, hi=0.3)
    c.text(960, 389, "CAFE  SNOOT", 30, (255, 236, 200), "Black")
    c.text(960, 426, "est. whenever  ·  no florals", 10, (255, 236, 220), "Italic")
    awning(c, 280, 1900, 436, 60, [(170, 30, 60), (250, 240, 230)], drop=22)
    # ground floor: windows into the warm interior + the door
    for (x0_, x1_) in ((300, 640), (1220, 1560)):
        c.ink(rect(x0_ - 12, 520, x1_ + 12, HOR), (110, 30, 50), lw=3.0, shade=0.3)
        c.ink(rect(x0_, 534, x1_, HOR - 40), ("v", (255, 214, 140), (220, 140, 100)), lw=2.4, shade=0.2, hi=0)
        for k in range(3):                                      # silhouettes of snooty customers
            px_ = x0_ + 60 + k * 110
            c.ink(ell(px_, 600, 16, 18), (150, 80, 80), lw=0, opacity=0.6)
            c.ink(Sh([[(px_ - 26, HOR - 40), (px_ - 18, 620), (px_ + 18, 620), (px_ + 26, HOR - 40)]]), (150, 80, 80), lw=0, opacity=0.6)
        c.stroke([(x0_ + 20, HOR - 60), (x0_ + 120, 550)], 10, (255, 255, 255), opacity=0.25)
        c.ink(rect(x0_ - 12, HOR - 40, x1_ + 12, HOR), (90, 26, 44), lw=2.6, shade=0.3)
        c.glow2((x0_ + x1_) / 2, 610, 240, GLOW, 0.35)
    neon(c, 1390, 572, "Snoot", 34, (255, 90, 190), "Italic", angle=-4)
    dx0, dx1 = 720, 860
    c.ink(rect(dx0 - 14, 510, dx1 + 14, HOR), (110, 30, 50), lw=3.0, shade=0.3)
    c.ink(rect(dx0, 522, dx1, HOR), (60, 130, 130), lw=2.6, shade=0.4, sw=20, hi=0.3)
    c.ink(rect(dx0 + 18, 536, dx1 - 18, 630), (255, 214, 140), lw=2.0, shade=0.2)
    c.stroke([(dx1 - 22, 640), (dx1 - 22, 680)], 5, (230, 200, 90), taper=(0, 0))
    c.text((dx0 + dx1) / 2, 650, "PUSH", 9, (255, 236, 200), "Bold")
    c.text((dx0 + dx1) / 2, 664, "(gently)", 7, (255, 236, 200), "Italic")
    c.glow2((dx0 + dx1) / 2, 580, 140, GLOW, 0.35)
    # espresso machine glimpsed through the right window
    c.ink(rrect(1440, 600, 1520, HOR - 46, 6), (200, 200, 214), lw=2.4, shade=0.4, hi=0.5)
    c.ink(ell(1480, 600, 14, 6), (230, 190, 80), lw=1.6)

    # ---- specials board (A-frame chalkboard)
    bx, by_ = 345, 742
    c.soft(ell(bx, by_ + 2, 60, 8), (24, 6, 34), 0.5, 5)
    for dx in (-42, 42):
        c.stroke([(bx + dx * 0.6, 520), (bx + dx, by_)], 7, (120, 70, 50), taper=(0, 0))
    c.ink(Sh([[(bx - 50, 530), (bx + 50, 530), (bx + 56, 700), (bx - 56, 700)]]), (130, 80, 56), lw=3.0, shade=0.3, hi=0.3)
    c.ink(Sh([[(bx - 42, 540), (bx + 42, 540), (bx + 47, 690), (bx - 47, 690)]]), (36, 56, 50), lw=2.4, shade=0.2, hi=0.2, tex=0.3)
    for k, (t, col) in enumerate((("TONIGHT", (255, 255, 240)), ("espresso 9", (255, 255, 240)), ("dbl. 30", (255, 255, 240)),
                                  ("croissant:", (255, 236, 140)), ("SOLD OUT", (255, 130, 160)), ("opinions FREE", (160, 230, 255)))):
        c.text(bx, 556 + k * 22, t, 10 if k else 12, col, "Bold")
    # ---- the tall urn planter where Mr. Pemberton sits (brass plaque)
    ux = CAFE_PERCH[0]
    c.soft(ell(ux, 742, 70, 10), (24, 6, 34), 0.55, 6)
    c.ink(rect(ux - 40, 620, ux + 40, 742), (220, 206, 214), lw=3.0, shade=0.5, sw=24, hi=0.4, rim=0.15, tex=0.2)
    c.ink(rect(ux - 50, 606, ux + 50, 624), (236, 222, 230), lw=2.8, shade=0.3, hi=0.4)
    c.ink(rect(ux - 50, 726, ux + 50, 744), (200, 186, 196), lw=2.8, shade=0.3, hi=0.3)
    urn = blob([(ux - 30, 606), (ux - 56, 580), (ux - 64, CAFE_PERCH[1] + 4), (ux + 64, CAFE_PERCH[1] + 4), (ux + 56, 580), (ux + 30, 606)], 2)
    c.ink(urn, (60, 150, 160), lw=3.0, shade=0.5, sw=18, hi=0.4, rim=0.2)
    c.ink(ell(ux, CAFE_PERCH[1] + 2, 66, 10), (40, 110, 120), lw=2.8, shade=0.2, hi=0.4)
    for k in range(7):                                          # clipped little box hedge (behind the pigeon)
        c.ink(ell(ux - 46 + k * 15, CAFE_PERCH[1] - 14 - (k % 2) * 6, 16, 14), (50, 120, 90), lw=2.4, shade=0.5, hi=0.3)
    c.ink(rrect(ux - 30, 650, ux + 30, 690, 3), (210, 170, 80), lw=2.0, shade=0.3, hi=0.6)
    c.text(ux, 662, "MR. PEMBERTON", 6, (80, 50, 20), "Bold")
    c.text(ux, 678, "DO NOT FEED", 6, (80, 50, 20), "Bold")
    for k in range(4):                                          # droppings, naturally
        c.ink(ell(ux - 30 + k * 18, 612 + (k % 2) * 4, 3, 2), (250, 250, 240), lw=0, opacity=0.8)
    # ---- terrace tables at the back (all reserved), the empty one on the right
    for x_ in (1140, 1310):
        bistro_table(c, x_, 742, 0.95)
    bistro_table(c, 1790, 760, 1.15)
    # ---- newspaper stand (wire rack)
    nx = 1560
    c.soft(ell(nx, 746, 70, 8), (24, 6, 34), 0.5, 5)
    c.ink(rect(nx - 60, 540, nx + 60, 744), (40, 40, 60), lw=2.8, shade=0.3, hi=0.3)
    c.ink(rrect(nx - 66, 520, nx + 66, 552, 4), (40, 100, 170), lw=2.6, shade=0.3, hi=0.4)
    c.text(nx, 536, "THE UPTOWN SNEER", 10, (255, 255, 240), "Black")
    for k in range(3):
        y_ = 566 + k * 58
        c.ink(Sh([[(nx - 52, y_), (nx + 52, y_), (nx + 50, y_ + 48), (nx - 50, y_ + 48)]]), (240, 236, 220), lw=2.0, shade=0.2, hi=0.2)
        c.stroke([(nx - 42, y_ + 10), (nx + 42, y_ + 10)], 4, (40, 30, 50), taper=(0, 0))
        for j in range(3):
            c.stroke([(nx - 42, y_ + 22 + j * 8), (nx + 30 - j * 10, y_ + 22 + j * 8)], 1.4, (120, 120, 140), taper=(0, 0))
    # ---- overhead string lights, lamp, potted trees at the edges
    bulbs = string_lights2(c, [(260, 470), (700, 490), (1150, 470), (1600, 490), (1960, 470)], sag=50, seed=21,
                           colors=((255, 220, 120), (255, 200, 110), (255, 140, 180)))
    lamps = [lamppost(c, 1960, HOR + 30, 300)]
    for x_ in (1680,):
        c.ink(rrect(x_ - 30, 680, x_ + 30, 742, 5), (120, 60, 50), lw=2.6, shade=0.4, hi=0.3)
        A1.tree_round(c, x_, 690, 180, seed=x_)
    cobweb(c, 252, 156, 70, "tl", opacity=0.35)
    room_grade(c, lights=[(470, 640, 380, 0.4), (1390, 640, 420, 0.4), (790, 600, 260, 0.35), (ux, 560, 240, 0.25, (120, 220, 255)),
                          (1390, 572, 220, 0.3, (255, 90, 190)), (125, 560, 200, 0.25, (140, 160, 255))],
               ambient=0.92, vign=0.55, top_dark=0.2, bottom_dark=0.4, shadow_tint=(80, 40, 130))
    c.painterly(0.05)

    def fg(sub):
        fg_chair_back(sub, 80, 880, 300, 300)
        fg_plant(sub, 1840, 1100, 300, seed=61, flip=True)
        sub.ink(ell(960, 1110, 260, 50), FG, lw=0, shade=0.2, hi=0.2)            # out-of-focus table top + cup
        sub.ink(rrect(1040, 1020, 1090, 1066, 8), FG, lw=0, hi=0.4, hw=4)
        fg_cable(sub, [(300, 1100), (520, 1070), (700, 1100)], 12)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_cafe_snoot.png")


def paint_mr_pemberton(name="hs_mr_pemberton.png"):
    """A fat grey uptown pigeon with a puffed 'cravat' of neck feathers (sits on the urn rim)."""
    c = C2(160, 120, 541, lw=2.8)
    x, y = 70, 112
    grey, grey_sh, grey_hi = (156, 154, 180), (96, 92, 124), (210, 210, 230)
    tail = Sh([[(x - 30, y - 30), (x - 70, y - 16), (x - 66, y - 6), (x - 26, y - 14)]])
    c.ink(tail, shade_col(grey, 0.8), lw=2.6, shade=0.3)
    body = blob([(x - 36, y - 18), (x - 34, y - 46), (x - 10, y - 62), (x + 22, y - 58), (x + 36, y - 36), (x + 30, y - 12), (x, y - 6)], 2)
    c.ink(body, grey, lw=2.8, shade=0.5, sw=14, scol=grey_sh, hi=0.4, hcol=grey_hi, rim=0.2)
    c.ink(blob([(x - 26, y - 44), (x + 6, y - 50), (x + 14, y - 30), (x - 10, y - 20), (x - 30, y - 26)], 2), shade_col(grey, 0.86), lw=2.2, shade=0.3, hi=0.3)
    for k in range(2):
        c.stroke([(x - 18 + k * 10, y - 34), (x - 4 + k * 10, y - 26)], 2.0, (60, 56, 80))
    cravat = blob([(x + 10, y - 66), (x + 40, y - 70), (x + 48, y - 50), (x + 36, y - 34), (x + 14, y - 40)], 2)
    c.ink(cravat, (110, 160, 150), lw=2.6, shade=0.4, hi=0.6, hw=4, hcol=(200, 140, 220), rim=0.3, rcol=(220, 120, 220))
    hx, hy = x + 34, y - 84
    c.ink(ell(hx, hy, 15, 14), grey, lw=2.6, shade=0.45, hi=0.4, hcol=grey_hi)
    c.ink(ell(hx + 6, hy - 2, 4.6, 4.6), (250, 150, 60), lw=1.4)
    c.ink(ell(hx + 7, hy - 2, 2.2, 2.2), INK, lw=0)
    c.stroke([(hx + 1, hy - 8), (hx + 11, hy - 6)], 2.2, INK)                          # a judgemental brow
    c.ink(Sh([[(hx + 13, hy - 2), (hx + 26, hy + 2), (hx + 13, hy + 5)]]), (90, 70, 70), lw=1.6, shade=0.3)
    c.ink(ell(hx + 15, hy - 3, 2.6, 2.0), (240, 240, 240), lw=0.8)
    for dx in (-6, 10):
        c.stroke([(x + dx, y - 8), (x + dx, y - 1), (x + dx + 8, y - 1)], 2.6, (220, 100, 110), taper=(0, 0))
    sprite_grade(c, 0.93)
    return finish_sprite(c, name, margin=2)


LAYOUT["cafe_snoot"] = dict(
    walk_px=[(30, Y_TOP), (1890, Y_TOP), (1900, 900), (1860, Y_BOT), (110, Y_BOT), (30, 900)],
    hotspots={
        ("Uptown street", 0): dict(box=(30, 410, 220, 712), stand=(190, 820)),
        ("Specials board", 0): dict(box=(285, 515, 405, 744), stand=(350, 800)),
        ("Anton", 0): dict(npc="hs_anton", feet=(560, FEET_Y), stand=(730, 935)),
        ("Mr. Pemberton", 0): dict(sprite="hs_mr_pemberton", feet=(CAFE_PERCH[0] + 8, CAFE_PERCH[1]), w=1.0, h=90, stand=(975, 800)),
        ("Vivian Quill", 0): dict(npc="hs_vivian_quill", feet=(1300, FEET_Y), w=2.1, stand=(1110, 935)),
        ("Newspaper stand", 0): dict(box=(1490, 515, 1630, 748), stand=(1560, 800)),
        ("Empty table", 0): dict(box=(1700, 640, 1880, 765), stand=(1760, 815)),
    },
    entries={"from_street": (200, 870)})


# =========================================================================== 5. Velour backstage
BS_STOOL = (1020, 92, 70)            # stool top (X, Y, Z): the rider croissant sits here


def paint_velour_backstage():
    c, R, rng = A1.std_room(5500, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 70, 150)
    LOW = (70, 50, 90)

    def block_wall(sub, w, h, seed):
        two_tone_wall(sub, w, h, WALL, LOW, seed, rail=(255, 200, 80), split=0.66, chips=5, stains=4)
        for y in np.arange(0, h * 0.66, 34 * getattr(sub, "density", 1)):        # painted cinder blocks
            sub.stroke([(0, y), (w, y)], 1.6, shade_col(WALL, 0.7), opacity=0.35, taper=(0, 0))
        rr = random.Random(seed)
        for _ in range(int(w / 140)):                           # band stickers
            x_, y_ = rr.uniform(20, w - 60), rr.uniform(h * 0.3, h * 0.6)
            col = rr.choice([(255, 220, 90), (90, 220, 255), (255, 120, 200), (120, 255, 140)])
            sub.ink(Sh([rot_pts([(x_, y_), (x_ + 46, y_), (x_ + 46, y_ + 22), (x_, y_ + 22)], rr.uniform(-20, 20), x_, y_)]), col, lw=1.6, shade=0.2)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (60, 46, 70), lw=0, shade=0, hi=0, ao=0, tex=0.3, wob=0)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (40, 20, 30), 0.25, 0, rng.randint(0, 99))

    def floor(sub):
        tiles(sub, (96, 84, 104), (88, 76, 98), 0, 0, sub.w, sub.h, size=120 * sub.density, seed=55, chipped=0.15, grout=(60, 50, 70))
        rr = random.Random(5)
        for _ in range(7):                                      # gaffer-tape X marks
            x_, y_ = rr.uniform(0, sub.w), rr.uniform(0, sub.h)
            L = 30 * sub.density
            for d in (-1, 1):
                sub.stroke([(x_ - L, y_ - d * L * 0.6), (x_ + L, y_ + d * L * 0.6)], 8 * sub.density, (250, 220, 80), taper=(0, 0), opacity=0.85)

    def left(sub):
        block_wall(sub, sub.w, sub.h, 81)
        x0, x1 = sub.ax(330), sub.ax(150)
        y0, y1 = sub.by(300), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (40, 36, 50), frame=(30, 20, 40), knob="R", seed=8)
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 130, "TO CLUB", (255, 120, 200))

    def right(sub):
        block_wall(sub, sub.w, sub.h, 82)
        x0, x1 = sub.ax(150), sub.ax(220)
        y0, y1 = sub.by(300), sub.by(180)
        sub.ink(Sh([rot_pts([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 3, (x0 + x1) / 2, (y0 + y1) / 2)]), (250, 248, 236), lw=2.2, shade=0.2)
        for k in range(6):
            yy = y0 + 18 + k * (y1 - y0 - 30) / 6
            sub.stroke([(x0 + 8, yy), (x1 - 12 - (k % 2) * 10, yy + 2)], 2.0, (60, 60, 90), taper=(0, 0))
            if k < 4:
                sub.stroke([(x0 + 4, yy - 2), (x1 - 4, yy + 4)], 1.6, (30, 30, 40), taper=(0, 0))
        sub.text((x0 + x1) / 2, y1 - 10, "Something?", 9, (255, 60, 160), "Italic")
        for (tx_, ty_) in ((x0 + 4, y0 + 4), (x1 - 4, y0 + 4)):
            sub.ink(rect(tx_ - 10, ty_ - 4, tx_ + 10, ty_ + 6), (230, 220, 180, 210), lw=0)
    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=5500)
    R.paint_plane("back", 0, Wb, 0, Hb, lambda sub: block_wall(sub, sub.w, sub.h, 83), density=1.0, seed=83)
    R.ao(0.55)
    R.edges(w=4.0)

    # ---- dressing mirror with bulbs (half of them out) over a dresser
    R.contact(20, 260, 0, 60, 0.5)
    R.ink_box(20, 260, 0, 96, 0, 60, (120, 70, 60), seed=1)
    for k in range(2):
        x_, y_ = P(140, 70 - k * 34, 60)
        c.ink(ell(x_, y_, 5, 5), (230, 200, 90), lw=1.4)
        c.stroke([P(30, 82 - k * 34, 60), P(250, 82 - k * 34, 60)], 1.8, INK, opacity=0.7)
    mx0, my0 = P(40, 330)
    mx1, my1 = P(240, 120)
    c.ink(rect(mx0 - 24, my0 - 24, mx1 + 24, my1 + 24), (60, 40, 60), lw=3.0, shade=0.3, hi=0.3)
    c.ink(rect(mx0, my0, mx1, my1), ("v", (170, 190, 220), (110, 120, 160)), lw=2.6, shade=0.2, hi=0.4)
    c.stroke([(mx0 + 20, my1 - 20), (mx0 + 90, my0 + 20)], 12, (255, 255, 255), opacity=0.3)
    c.text((mx0 + mx1) / 2, (my0 + my1) / 2 - 16, "YOU ARE NOT", 15, (230, 40, 90, 200), "Italic", angle=-4)
    c.text((mx0 + mx1) / 2 + 4, (my0 + my1) / 2 + 8, "BORING. - J", 15, (230, 40, 90, 140), "Italic", angle=-4)
    c.soft(ell((mx0 + mx1) / 2 + 40, (my0 + my1) / 2 + 6, 60, 18), (150, 160, 200), 0.5, 6)   # half wiped off
    lit = []
    for k in range(16):
        t_ = k / 15
        for (x_, y_) in ((mx0 - 12 + t_ * (mx1 - mx0 + 24), my0 - 12),):
            on = rng.random() < 0.5
            c.ink(ell(x_, y_, 7, 7), (255, 246, 200) if on else (120, 110, 120), lw=1.6)
            if on:
                c.glow2(x_, y_, 30, GLOW, 0.5)
                lit.append((x_, y_))
    for k in range(10):
        t_ = k / 9
        for x_ in (mx0 - 12, mx1 + 12):
            y_ = my0 + t_ * (my1 - my0)
            on = rng.random() < 0.5
            c.ink(ell(x_, y_, 7, 7), (255, 246, 200) if on else (120, 110, 120), lw=1.6)
            if on:
                c.glow2(x_, y_, 30, GLOW, 0.5)
    for k, col in enumerate(((220, 40, 90), (60, 200, 220), (250, 250, 240))):      # makeup clutter
        x_, y_ = P(60 + k * 50, 96, 30)
        c.ink(rrect(x_ - 6, y_ - 24, x_ + 6, y_, 3), col, lw=1.8, shade=0.3, hi=0.4)
    # ---- costume rack: safety-pin jacket, forty-zip trousers, the NO cape
    rX0, rX1 = 300, 520
    for X in (rX0, rX1):
        c.stroke([P(X, 0, 60), P(X, 250, 60)], 7, INK, taper=(0, 0))
        c.stroke([P(X, 0, 60), P(X, 250, 60)], 3.6, (190, 190, 200), taper=(0, 0))
        c.ink(ell(*P(X, 0, 60), 16, 5), (40, 40, 50), lw=2.0)
    c.stroke([P(rX0, 250, 60), P(rX1, 250, 60)], 7, INK, taper=(0, 0))
    c.stroke([P(rX0, 250, 60), P(rX1, 250, 60)], 3.6, (190, 190, 200), taper=(0, 0))
    gar = [((330, 380), (40, 36, 50), "jacket"), ((390, 440), (60, 60, 80), "zips"), ((450, 510), (30, 26, 36), "cape")]
    for (Xa, Xb), col, kind in gar:
        (xa, ya), (xb, _) = P(Xa, 245, 60), P(Xb, 245, 60)
        _, yb = P(Xa, 80 if kind != "cape" else 30, 60)
        c.stroke([((xa + xb) / 2, ya - 6), ((xa + xb) / 2, ya + 10)], 2.0, (200, 200, 210))
        sh = blob([(xa + 4, ya + 8), (xb - 4, ya + 8), (xb + 12, ya + 26), (xb + 8, yb), (xa - 8, yb), (xa - 12, ya + 26)], 1) if kind != "zips" else \
            Sh([[(xa, ya + 10), (xb, ya + 10), (xb + 4, yb), ((xa + xb) / 2 + 3, yb), ((xa + xb) / 2, ya + 60), ((xa + xb) / 2 - 3, yb), (xa - 4, yb)]])
        c.ink(sh, col, lw=2.8, shade=0.5, sw=12, hi=0.35, hcol=(140, 130, 180))
        if kind == "jacket":
            for k in range(12):
                x_, y_ = xa + rng.uniform(0, xb - xa), ya + 20 + rng.uniform(0, yb - ya - 30)
                c.stroke([(x_ - 5, y_), (x_ + 5, y_ + 2)], 1.6, (230, 230, 240))
        elif kind == "zips":
            for k in range(8):
                y_ = ya + 20 + k * (yb - ya - 30) / 8
                c.stroke([(xa + 6, y_), (xb - 6, y_ + 3)], 1.6, (220, 210, 140))
        else:
            c.text((xa + xb) / 2, (ya + yb) / 2, "NO", 22, (255, 60, 160))
    # ---- rider table + stool with the glass dome
    tX0, tX1 = 760, 960
    R.contact(tX0, tX1, 20, 90, 0.55)
    R.ink_box(tX0, tX1, 96, 104, 20, 90, (120, 76, 60), top=(160, 110, 80), seed=3)
    for X in (tX0 + 10, tX1 - 10):
        for Z in (26, 84):
            c.stroke([P(X, 96, Z), P(X, 0, Z)], 5, INK, taper=(0, 0))
    gx, gy = P(800, 104, 55)
    c.ink(ell(gx, gy - 8, 30, 10), (240, 240, 240), lw=2.2, shade=0.3, hi=0.4)
    for k in range(9):
        c.ink(ell(gx - 18 + (k % 5) * 9, gy - 12 - (k // 5) * 6, 4.4, 4.4), (90, 236, 110), lw=1.2, hi=0.5)
    R.ink_box(850, 930, 104, 160, 40, 80, (200, 170, 120), top=(230, 200, 150), seed=4)
    ex_, ey_ = P(890, 135, 80)
    c.text(ex_, ey_, "ESPRESSO", 8, (90, 50, 30), "Bold")
    cx_, cy_ = P(900, 104, 92)
    c.ink(Sh([[(cx_ - 26, cy_ - 2), (cx_ + 26, cy_ - 2), (cx_ + 18, cy_ - 24), (cx_ - 18, cy_ - 24)]]), (252, 250, 240), lw=1.6, shade=0.2)
    c.text(cx_, cy_ - 13, "RIDER", 7, (190, 40, 60), "Bold")
    sX, sY, sZ = BS_STOOL
    R.contact(sX - 22, sX + 22, sZ - 22, sZ + 22, 0.5)
    for (dx, dz) in ((-18, -18), (18, -18), (18, 18), (-18, 18)):
        c.stroke([P(sX + dx * 0.6, sY, sZ + dz * 0.6), P(sX + dx, 0, sZ + dz)], 5, INK, taper=(0, 0))
        c.stroke([P(sX + dx * 0.6, sY, sZ + dz * 0.6), P(sX + dx, 0, sZ + dz)], 2.4, (190, 190, 200), taper=(0, 0))
    st = P(sX, sY, sZ)
    c.ink(ell(st[0], st[1], 30, 9), (200, 40, 80), lw=2.6, shade=0.3, hi=0.4)
    # empty glass dome (the croissant sprite sits inside it)
    dome = blob([(st[0] - 28, st[1] - 4), (st[0] - 27, st[1] - 34), (st[0] - 14, st[1] - 52), (st[0], st[1] - 56), (st[0] + 14, st[1] - 52),
                 (st[0] + 27, st[1] - 34), (st[0] + 28, st[1] - 4)], 2)
    c.ink(dome, (210, 230, 255, 50), lw=2.2, oc=(90, 90, 140), shade=0, hi=0.6, hw=4, ao=0)
    c.ink(ell(st[0], st[1] - 60, 5, 4), (200, 200, 220), lw=1.6)
    # ---- amp stack (LOUD / LOUDER / SORRY)
    aX0, aX1 = 1080, 1240
    R.contact(aX0, aX1, 10, 90, 0.6)
    for k, (Y0, Y1) in enumerate(((0, 120), (120, 240), (240, 320))):
        f = R.ink_box(aX0 + k * 6, aX1 - k * 6, Y0, Y1, 10, 90 - k * 6, (40, 36, 46), seed=10 + k)
        fr = f["front"]
        x0_, y0_ = fr[0]
        x1_, y1_ = fr[2]
        if k < 2:
            c.ink(rect(x0_ + 10, y0_ + 10, x1_ - 10, y1_ - 10), (60, 56, 66), lw=2.0, shade=0.2, tex=0.4)
            for j in range(2):
                for i in range(2):
                    c.ink(ell(x0_ + (x1_ - x0_) * (0.28 + i * 0.44), y0_ + (y1_ - y0_) * (0.3 + j * 0.42), 24, 24), (26, 22, 30), lw=2.0, hi=0.3)
        else:
            c.ink(rect(x0_ + 6, y0_ + 6, x1_ - 6, y0_ + 24), (220, 200, 140), lw=1.6, shade=0.2)
            for i, t in enumerate(("LOUD", "LOUDER", "SORRY")):
                kx_ = x0_ + 30 + i * (x1_ - x0_ - 60) / 2
                c.ink(ell(kx_, y0_ + 50, 9, 9), (30, 26, 36), lw=1.8, hi=0.5)
                c.text(kx_, y0_ + 68, t, 6, (220, 220, 230), "Bold")
            c.text((x0_ + x1_) / 2, y0_ + 15, "VEX", 11, (40, 30, 40), "Black")
    # ---- ceiling: pipes, a bare bulb, cables
    pipe(c, [P(0, Hb - 30, 60), P(Wb, Hb - 30, 60)], w=24, col=(150, 110, 170), brackets=[P(300, Hb - 30, 60), P(900, Hb - 30, 60)])
    pipe(c, [P(Wb - 120, Hb, 30), P(Wb - 120, Hb - 26, 30), P(Wb - 120, Hb - 26, 300)], w=18, col=(90, 150, 160))
    bulbs = []
    for X, Z in ((640, 200), (300, 360)):
        x_, y_ = P(X, Hb, Z)
        bulb(c, x_, y_ + 110, 10, strength=0.6, cord_from=(x_, y_))
        bulbs.append((x_, y_ + 110))
        c.light_cone((x_, y_ + 118), (x_ - 320, 1000), (x_ + 320, 1000), (255, 236, 190), 0.18, 40)
    cable(c, P(0, Hb, 300), P(700, Hb, 330), sag=60, w=7, col=(30, 20, 50))
    cable(c, P(700, Hb, 330), P(Wb, Hb, 220), sag=40, w=6, col=(40, 130, 130))
    string_lights2(c, [P(0, 380, 0), P(Wb, 380, 0)], sag=50, seed=23, spacing=60)
    cobweb(c, *P(0, Hb, 0), 100, "tl")
    cobweb(c, *P(Wb, Hb, 0), 110, "tr")
    # clutter: flight case, cable coils, a guitar on a stand
    R.contact(560, 700, 10, 80, 0.5)
    fc_ = R.ink_box(560, 700, 0, 70, 10, 80, (30, 30, 36), seed=20)
    x_, y_ = fc_["front"][0]
    c.text(x_ + 50, y_ + 24, "VEX / FRAGILE", 8, (230, 230, 240), "Bold")
    for (X, Z) in ((620, 200), (980, 220)):
        x_, y_ = P(X, 0, Z)
        for r_ in (30, 22, 14):
            c.ink(ell(x_, y_ - 6, r_ * 1.3, r_ * 0.45), (0, 0, 0, 0), lw=3.6, oc=(30, 26, 40), line_only=True)
    room_grade(c, lights=[((mx0 + mx1) / 2, my1, 380, 0.45), (bulbs[0][0], 760, 420, 0.35), (bulbs[1][0], 820, 360, 0.3),
                          (130, 480, 220, 0.3, (255, 120, 200)), (1500, 450, 260, 0.25, (110, 220, 255))],
               ambient=0.9, vign=0.6, top_dark=0.45, bottom_dark=0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1660, 1090, 5, 1.1, seed=41)
        sub.ink(rect(-20, 950, 260, 1100), FG, lw=0, shade=0.2, hi=0.2)            # flight case corner
        sub.ink(rect(230, 970, 260, 1100), mix(FG, (90, 90, 110), 0.4), lw=0)
        fg_cable(sub, [(300, 1100), (700, 1060), (1100, 1080), (1500, 1110)], 18)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_velour_backstage.png")


def _bs_stool_px():
    R = Room(None, (960, vp_for_walk(Y_TOP, Y_BOT)), (330, 250, 1590, 690), fc=1000)
    x, y = R.pt(*BS_STOOL)
    return (round(x), round(y))


def paint_rider_croissant(name="hs_rider_croissant.png"):
    """One perfect croissant on a little plate, with the dome's glass glint over it (sits on the stool)."""
    c = C2(90, 70, 551, lw=2.6)
    x, y = 45, 62
    c.ink(ell(x, y - 4, 24, 6), (250, 248, 240), lw=2.0, shade=0.3, hi=0.3)
    cr = blob([(x - 24, y - 6), (x - 18, y - 18), (x - 6, y - 26), (x + 6, y - 26), (x + 18, y - 18), (x + 24, y - 6), (x + 10, y - 12),
               (x, y - 10), (x - 10, y - 12)], 2)
    c.ink(cr, (230, 160, 70), lw=2.4, shade=0.5, sw=7, scol=(160, 90, 40), hi=0.6, hw=3, hcol=(255, 220, 140))
    for dx in (-10, 0, 10):
        c.stroke([(x + dx - 2, y - 24 + abs(dx) * 0.4), (x + dx + 2, y - 11)], 1.6, (150, 80, 40), opacity=0.8)
    c.stroke([(x - 18, y - 40), (x - 16, y - 16)], 3.0, (255, 255, 255), opacity=0.35)
    c.glow2(x, y - 16, 30, GLOW, 0.3)
    sprite_grade(c, 0.95)
    return finish_sprite(c, name, margin=2)


LAYOUT["velour_backstage"] = dict(
    walk_px=[(300, Y_TOP), (1620, Y_TOP), (1760, 900), (1700, Y_BOT), (240, Y_BOT), (170, 900)],
    hotspots={
        ("Club floor", 0): dict(box=(20, 330, 200, 820), stand=(260, 880)),
        ("Dressing mirror", 0): dict(box=(330, 310, 600, 715), stand=(470, 800)),
        ("Costume rack", 0): dict(box=(600, 420, 860, 715), stand=(745, 800)),
        ("Grizz", 0): dict(npc="hs_grizz", feet=(1010, FEET_Y), w=2.1, stand=(840, 935)),
        ("Rider croissant", 0): dict(sprite="hs_rider_croissant", feet=_bs_stool_px(), w=0.8, h=70, stand=(1340, 800)),
        ("Rider table", 0): dict(box=(1080, 570, 1320, 722), stand=(1190, 800)),
        ("Amp stack", 0): dict(box=(1405, 345, 1640, 722), stand=(1500, 800)),
        ("Set list", 0): dict(box=(1690, 360, 1800, 545), stand=(1690, 810)),
    },
    entries={"from_club": (280, 880)})


# =========================================================================== entry point
SPRITES = ["hs_mimi", "hs_brutus", "hs_pierre", "hs_jett_vex", "hs_anton", "hs_vivian_quill", "hs_grizz", "hs_mr_pemberton",
           "hs_rider_croissant", "hs_blank_canvas", "hs_something_no_1"]
ASSETS = {
    **{n: (lambda n=n: paint_npc(n)) for n in NPC_FN},
    "hs_mr_pemberton": paint_mr_pemberton, "hs_rider_croissant": paint_rider_croissant,
    "hs_blank_canvas": paint_blank_canvas, "hs_something_no_1": paint_something_no_1,
    "bg_uptown": paint_uptown, "bg_art_gallery": paint_art_gallery, "bg_nightclub": paint_nightclub,
    "bg_cafe_snoot": paint_cafe_snoot, "bg_velour_backstage": paint_velour_backstage,
}
SHOW_FLAGS = {"art_gallery": ("a5_took_canvas", "a5_canvas_hung"), "cafe_snoot": ("a5_anton_fled",),
              "velour_backstage": ("a5_got_croissant",)}


def main(argv):
    args = [a.lower() for a in argv[1:]]
    if "--layout" in args:
        write_layout()
        return
    if "--composite" in args:
        rooms = [a for a in args if not a.startswith("--")] or ROOM_IDS
        for r in rooms:
            composite(r)
            if r in SHOW_FLAGS:
                composite(r, flags=SHOW_FLAGS[r])
        return
    if "--sheet" in args:
        contact_sheets()
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
