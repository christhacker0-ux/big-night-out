#!/usr/bin/env python3
"""
Big Night Out -- Act 4 (Off Campus) repainted in "style 2" (see Docs/ART_STYLE.md).

Paints the Act 4 backgrounds (downtown, quickmart, rusty_anchor, starlite_diner, bijou_lobby) and the Act 4
character / prop sprites (Bree Marlowe, Lou, Captain Gus, Commodore Gus, Sal, Mortimer, the velvet rope) with
tools/art/style2.py, following act1_style2.py: perspective rooms, grungy surfaces, magenta / teal palette, warm
lamp light, dark foreground framing and tall characters. Roxy Vale and Dex come from act1_style2.py.

This supersedes the Act 4 painters in act4.py for these files (its item icons are unchanged). Running act4.py
without arguments would overwrite them with the old art.

Usage:  python3 tools/art/act4_style2.py              # paint everything
        python3 tools/art/act4_style2.py gus diner    # paint assets whose name contains these words
        python3 tools/art/act4_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into act4.json
        BNO_COMPOSITES=/some/dir python3 tools/art/act4_style2.py --composite [room ids]
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
from act1_style2 import (DEX_H, BRICK, MORTAR, Y_TOP, Y_BOT, legs, skirt, glasses, folds, hair_strands,  # noqa: E402
                         soft_shade, clip_draw, plaid, grunge_wall, two_tone_wall, skirting, window_flat,
                         doorway_flat, facade_windows, lamppost, exit_sign, sprite_grade, panel_light, std_room,
                         corkboard, bunting2, fire_extinguisher)

WORLD = os.path.join(ROOT, "Assets", "_Project", "World", "act4.json")
NPC_FEET_Y = 945          # every Act 4 NPC stands near the front, like Act 1 (world y -4.05)


def tattoo(c, sh, pts_list, col=(40, 70, 110), w=1.6, o=0.75):
    """Line-art tattoo strokes clipped to a limb."""
    def fn(t):
        for pts in pts_list:
            t.stroke(pts, w, col, taper=(0.1, 0.1), opacity=o, smooth=1)
    clip_draw(c, sh, fn)


# =========================================================================== Bree Marlowe (waitress, actress)
def paint_bree_marlowe(height=382, name="hs_bree_marlowe.png"):
    W, Hc = 380, 600
    skin = (252, 214, 188)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=401)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.82, waist=0.76, hips=1.0, limbs=0.84, head=1.08, legs=1.03, neck=0.98, chest=1.0,
                        hand=0.92, foot=0.92),
             pose=dict(arm_n=-34, fore_n=-20, arm_f=150, fore_f=48, leg_n=8, shin_n=-4, leg_f=-10, shin_f=6, lean=-6,
                       head_dx=-0.8, head_dy=0.4), seed=41)
    dress, dress_sh = (46, 176, 172), (24, 104, 120)
    hair, hair_sh, hair_hi = (236, 96, 48), (170, 46, 40), (255, 168, 100)
    white, white_sh = (250, 248, 242), (196, 190, 220)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # ponytail (behind the head), swinging back
    tail = limb([(hx - r * 0.7, hy - ry * 0.7), (hx - r * 1.6, hy - ry * 0.5), (hx - r * 2.0, hy + ry * 0.3),
                 (hx - r * 1.9, hy + ry * 1.1)], [r * 0.55, r * 0.62, r * 0.46, r * 0.12], smooth=2)
    c.ink(tail, hair, lw=3.0, shade=0.5, sw=r * 0.3, scol=hair_sh, hi=0.45, hw=r * 0.15, hcol=hair_hi)
    hair_strands(c, [[(hx - r * 1.1, hy - ry * 0.6), (hx - r * 1.7, hy - ry * 0.2), (hx - r * 1.85, hy + ry * 0.7)]], hair_sh)
    # far arm flung up to the forehead (dramatic)
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "flat", col=shade_col(skin, 0.88), size=0.95)
    c.ink(b.sleeve(False, 0.42, 7.4, 6.8), shade_col(dress, 0.82), lw=2.8, shade=0.4)
    # legs: bare + white socks + red-and-white sneakers
    def sneaks(bb, near):
        bb.shoe(near, (250, 250, 246) if near else (214, 210, 226), (226, 54, 70), "sneaker", length=0.95)
    legs(b, skin, w=(7.4, 5.0, 3.8), shoe=sneaks, skin=True)
    for near in (False, True):
        an = b.ankle_n if near else b.ankle_f
        c.ink(Sh([b.Ps([(an[0] - 2.4, an[1] + 6.0), (an[0] + 2.4, an[1] + 6.0), (an[0] + 2.6, an[1] + 1.0),
                        (an[0] - 2.6, an[1] + 0.6)])]), white if near else white_sh, lw=2.4, shade=0.3)
    # skirt of the diner dress + apron
    sk = skirt(b, dress, b.hip_y - 16, flare=2.6, waist=b.hip_y + 7, scol=dress_sh, pleats=2)
    # neck + bodice
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.4, hem=b.hip_y + 6, flare=-0.4, neck_open=1.0)])
    c.ink(torso, dress, lw=3.0, shade=0.55, sw=16, scol=dress_sh, hi=0.35, rim=0.2, rcol=(170, 255, 240))
    sy, sx = b.shoulder_y, b.lean_dx
    # white peter-pan collar
    for pts in ([(sx - 3.0, sy + 1.6), (sx + 0.8, sy + 0.6), (sx + 1.2, sy - 2.4), (sx - 2.0, sy - 2.6)],
                [(sx + 1.4, sy + 0.6), (sx + 5.4, sy + 0.8), (sx + 5.0, sy - 2.2), (sx + 1.8, sy - 2.6)]):
        c.ink(blob(b.Ps(pts), 2), white, lw=2.2, shade=0.35, sw=4)
    # apron: bib + skirt, ties, pocket with straws
    ap = Sh([chaikin(b.Ps([(sx - 0.6, sy - 5.5), (sx + 4.4, sy - 5.5), (sx + 4.8, b.hip_y + 8), (6.6, b.hip_y + 4),
                           (6.4, b.hip_y - 13), (-4.0, b.hip_y - 13.6), (-3.4, b.hip_y + 4), (sx - 1.4, b.hip_y + 8)]), 1)])
    c.ink(ap, white, lw=2.8, shade=0.5, sw=14, scol=white_sh, hi=0.3)
    c.stroke(b.Ps([(-4.4, b.hip_y + 6.4), (6.2, b.hip_y + 6.6)]), 3.0, white_sh)
    px_, py_ = b.P(2.6, b.hip_y - 4)
    c.ink(rrect(px_ - 16, py_ - 10, px_ + 16, py_ + 14, 4), white, lw=2.0, shade=0.3, scol=white_sh)
    for k, col in enumerate(((226, 54, 70), (60, 140, 220), (250, 210, 70))):
        c.stroke([(px_ - 8 + k * 7, py_ - 6), (px_ - 10 + k * 8, py_ - 26)], 2.6, col, taper=(0, 0))
    folds(c, [b.Ps([(-1.5, b.hip_y - 2), (-2.4, b.hip_y - 12)]), b.Ps([(4.6, b.hip_y), (5.2, b.hip_y - 12)])], white_sh, 1.6, 0.6)
    # name tag (red, the item Dex can borrow)
    tx_, ty_ = b.P(sx + 3.6, sy - 9)
    c.ink(rrect(tx_ - 18, ty_ - 7, tx_ + 18, ty_ + 7, 3), (230, 60, 76), lw=1.8, shade=0.2, hi=0.4, hw=2)
    c.label(tx_, ty_, "BREE", 7, (255, 246, 230), "Black")
    # head
    head = Sh([b.head_pts(jaw=0.95, chin=0.96, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.1, fa["eye_n"][1] + ry * 0.44, r * 0.3, (255, 110, 120), 0.45)
    rng = random.Random(41)
    for _ in range(8):   # freckles
        ex, ey = fa["eye_n"]
        c.ink(ell(ex + rng.uniform(-r * 0.2, r * 0.75), ey + ry * rng.uniform(0.3, 0.46), 1.1, 1.1), (210, 120, 80), lw=0,
              shade=0, hi=0, ao=0, tex=0, wob=0)
    b.eyes(iris=(70, 160, 120), look=(0.25, -0.25), lid=0.0, size=1.1, lashes=1, tilt=0.05)
    b.brows(col=hair_sh, lift_n=0.22, lift_f=0.18, tilt_n=0.6, tilt_f=0.5, w=r * 0.11)
    b.nose("button", 0.95)
    b.mouth("open", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.5, r * 0.42, lip=(220, 60, 90))
    b.ear(0.9)
    glasses(b, col=(236, 80, 140), round_=False, size=1.08)
    # bangs + top of the hair, pencil stuck in the ponytail band
    top = blob([(hx - r * 1.08, hy + ry * 0.25), (hx - r * 1.12, hy - ry * 0.5), (hx - r * 0.6, hy - ry * 1.05),
                (hx + r * 0.3, hy - ry * 1.05), (hx + r * 0.95, hy - ry * 0.65), (hx + r * 1.08, hy - ry * 0.25),
                (hx + r * 0.7, hy - ry * 0.4), (hx + r * 0.45, hy - ry * 0.28), (hx + r * 0.15, hy - ry * 0.42),
                (hx - r * 0.2, hy - ry * 0.3), (hx - r * 0.45, hy + ry * 0.15)], 2)
    c.ink(top, hair, lw=3.0, shade=0.45, sw=r * 0.4, scol=hair_sh, hi=0.5, hw=r * 0.25, hcol=hair_hi, rim=0.15)
    hair_strands(c, [[(hx - r * 0.6, hy - ry * 0.85), (hx + r * 0.2, hy - ry * 0.9), (hx + r * 0.85, hy - ry * 0.5)]], hair_sh)
    bx_, by_ = hx - r * 0.8, hy - ry * 0.72
    c.ink(ell(bx_, by_, r * 0.2, r * 0.22), (60, 200, 196), lw=2.2, shade=0.3)
    c.ink(limb([(bx_ - r * 0.6, by_ - r * 0.5), (bx_ + r * 0.5, by_ + r * 0.3)], [5, 5], smooth=0), (250, 210, 70), lw=2.0, shade=0.3)
    c.ink(Sh([[(bx_ + r * 0.5, by_ + r * 0.24), (bx_ + r * 0.66, by_ + r * 0.44), (bx_ + r * 0.42, by_ + r * 0.38)]]),
          (60, 40, 40), lw=1.4)
    # near arm thrown out to the side, holding an order pad like a script
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5, rim=0.15, rcol=(255, 170, 160))
    c.ink(b.sleeve(True, 0.46, 7.8, 7.0), dress, lw=3.0, shade=0.5, sw=8, scol=dress_sh, hi=0.3)
    wx, wy = b.P(*b.wrist_n)
    pad = Sh([rot_pts([(wx - 30, wy - 26), (wx + 4, wy - 26), (wx + 4, wy + 18), (wx - 30, wy + 18)], 18, wx, wy)])
    c.ink(pad, (255, 250, 220), lw=2.4, shade=0.3, hi=0.2)
    for k in range(4):
        a, b_ = rot_pts([(wx - 26, wy - 14 + k * 8), (wx - 2, wy - 14 + k * 8)], 18, wx, wy)
        c.stroke([a, b_], 1.2, (120, 120, 170), opacity=0.8)
    b.hand(True, "hold", size=0.95)
    for k in range(3):   # drama lines
        a = math.radians(-120 + k * 30)
        x0_, y0_ = hx + r * 0.4 + math.cos(a) * r * 1.6, hy + math.sin(a) * ry * 1.4
        c.stroke([(x0_, y0_), (x0_ + math.cos(a) * r * 0.5, y0_ + math.sin(a) * r * 0.5)], 2.2, (255, 250, 200))
    return finish_sprite(c, name, flip=False)


# =========================================================================== Lou (Quickmart clerk)
def paint_lou(height=390, name="hs_lou.png"):
    W, Hc = 380, 600
    skin = (126, 80, 58)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=402)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.9, waist=0.86, hips=1.0, limbs=0.92, head=1.04, legs=1.02, neck=1.0, chest=0.6,
                        hand=0.95, foot=1.0),
             pose=dict(arm_n=12, fore_n=88, arm_f=6, fore_f=96, leg_n=-6, shin_n=3, leg_f=7, shin_f=-4, lean=-3,
                       head_dx=0.2, head_dy=-0.4), seed=42)
    vest, vest_sh = (46, 160, 110), (24, 96, 80)
    tee = (40, 34, 52)
    jeans, jeans_sh = (64, 70, 120), (36, 38, 84)
    beanie, beanie_sh = (240, 130, 40), (180, 70, 40)
    braid, braid_hi = (34, 22, 26), (90, 60, 70)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # braids down the back
    for k, dx in enumerate((-0.95, -0.7, -0.45)):
        pts = [(hx + r * dx, hy + ry * 0.1), (hx + r * (dx - 0.2), hy + ry * 1.2), (hx + r * (dx - 0.1), hy + ry * 2.4 + k * 4)]
        c.ink(limb(pts, [r * 0.24, r * 0.22, r * 0.16], smooth=1), braid, lw=2.4, shade=0.4, hi=0.3, hcol=braid_hi)
        P_ = resample(chaikin(pts, 2, closed=False), r * 0.22)
        for p in P_[1:]:
            c.stroke([(p[0] - r * 0.1, p[1] - 2), (p[0] + r * 0.1, p[1] + 2)], 1.2, braid_hi, taper=(0.2, 0.2), opacity=0.7)
        ex_, ey_ = pts[-1]
        c.ink(ell(ex_, ey_ + 4, 4, 4), (250, 200, 70), lw=1.4)
    # far arm (behind) folded under the newspaper
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.86), d=(1.0, 0.1))
    c.ink(b.sleeve(False, 0.4, 7.8, 7.2), shade_col(tee, 0.9), lw=2.8, shade=0.3)
    # jeans + chunky boots
    def boots(bb, near):
        bb.shoe(near, (70, 50, 46) if near else (56, 40, 40), (40, 30, 30), "boot", length=1.0)
    legs(b, jeans, w=(8.6, 6.4, 6.6), scol=jeans_sh, shoe=boots)
    hips = Sh([b.Ps([(-5.4, b.hip_y + 4.5), (5.0, b.hip_y + 4.5), (5.4, b.hip_y - 3), (-5.6, b.hip_y - 3)])])
    c.ink(hips, jeans, lw=3.0, shade=0.45, scol=jeans_sh)
    # tee + vest
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=7)
    torso = Sh([b.torso_pts(slack=0.6, hem=b.hip_y + 1, flare=0.2, neck_open=1.0)])
    c.ink(torso, tee, lw=3.0, shade=0.4, hi=0.25)
    sy, sx = b.shoulder_y, b.lean_dx
    for pts in ([(sx - 2.4, sy + 1.4), (b.sh_n[0] + 1.6, sy - 0.2), (b.sh_n[0] + 1.6, sy - 9), (-5.6, b.hip_y + 1.4),
                 (-0.4, b.hip_y + 0.6), (sx - 0.6, sy - 6)],
                [(sx + 2.8, sy + 1.2), (b.sh_f[0], sy - 0.4), (b.sh_f[0] + 1.4, sy - 9), (5.6, b.hip_y + 1.4), (1.2, b.hip_y + 0.6),
                 (sx + 1.6, sy - 6)]):
        c.ink(Sh([chaikin(b.Ps(pts), 1)]), vest, lw=3.0, shade=0.5, sw=10, scol=vest_sh, hi=0.3)
    vx, vy = b.P(sx + 4.4, sy - 6)
    c.ink(rrect(vx - 20, vy - 7, vx + 20, vy + 7, 3), (250, 248, 236), lw=1.8, shade=0.2)
    c.label(vx, vy, "LOU", 7, (40, 90, 70), "Black", mirror=True)
    c.ink(ell(*b.P(sx - 3.2, sy - 10), 6, 6), (250, 210, 60), lw=1.6, shade=0.2)       # pin: a frowny face
    # head: deadpan
    head = Sh([b.head_pts(jaw=1.0, chin=1.0, cheek=1.0)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.7), hi=0.35, rim=0.15, rcol=(220, 150, 130))
    fa = b.face_anchor()
    b.eyes(iris=(70, 46, 30), look=(0.4, 0.35), lid=0.55, lower=0.08, size=1.0, lashes=1)
    b.brows(col=(30, 20, 20), lift_n=-0.04, lift_f=-0.02, tilt_n=-0.1, tilt_f=-0.1, w=r * 0.13, arch=0.02)
    b.nose("round", 1.0)
    b.mouth("flat", fa["mouth"][0], fa["mouth"][1] + ry * 0.04, r * 0.42, r * 0.2, lip=(110, 56, 56))
    b.ear(0.95)
    ex_, ey_ = fa["ear"]
    for k in range(3):
        c.ink(ell(ex_ - r * 0.32 + k * r * 0.04, ey_ - r * 0.3 + k * r * 0.22, 2.0, 2.0), (220, 220, 230), lw=1.0)
    # beanie with a pencil tucked in
    bx_, by_ = hx, hy - ry * 0.55
    bean = blob([(hx - r * 1.12, hy - ry * 0.2), (hx - r * 1.1, hy - ry * 0.8), (hx - r * 0.5, hy - ry * 1.28), (hx + r * 0.4, hy - ry * 1.3),
                 (hx + r * 1.0, hy - ry * 0.95), (hx + r * 1.12, hy - ry * 0.45), (hx + r * 0.2, hy - ry * 0.55)], 2)
    c.ink(bean, beanie, lw=3.0, shade=0.5, sw=r * 0.35, scol=beanie_sh, hi=0.4)
    clip_draw(c, bean, lambda t: [t.stroke([(x, hy - ry * 1.5), (x + r * 0.1, hy - ry * 0.4)], 1.6, beanie_sh, taper=(0, 0), opacity=0.6)
                                   for x in np.arange(hx - r * 1.2, hx + r * 1.3, r * 0.2)])
    cuff = Sh([[(hx - r * 1.16, hy - ry * 0.12), (hx - r * 1.12, hy - ry * 0.5), (hx + r * 1.14, hy - ry * 0.6), (hx + r * 1.16, hy - ry * 0.26)]])
    c.ink(cuff, hi_col(beanie, 0.1), lw=2.8, shade=0.4, scol=beanie_sh, hi=0.3)
    c.ink(bean, (0, 0, 0, 0), lw=3.0, line_only=True)
    c.ink(limb([(hx + r * 0.2, hy - ry * 1.0), (hx + r * 1.4, hy - ry * 1.55)], [6, 6], smooth=0), (250, 200, 60), lw=2.0, shade=0.3)
    c.ink(ell(hx + r * 0.22, hy - ry * 1.0, 4, 4), (240, 140, 150), lw=1.4)
    # near arm: holding the folded newspaper crossword up, tattoos on the forearm
    arm = b.arm_shape(True)
    c.ink(arm, skin, lw=3.0, shade=0.5, rim=0.15, rcol=(220, 150, 130))
    E, Wr = b.P(*b.elbow_n), b.P(*b.wrist_n)
    mx_, my_ = (E[0] + Wr[0]) / 2, (E[1] + Wr[1]) / 2
    tattoo(c, arm, [[(mx_ - 12, my_ - 4), (mx_ - 4, my_ - 8), (mx_ + 4, my_ - 4), (mx_ - 4, my_ + 4), (mx_ - 12, my_ - 4)],
                    [(mx_ + 10, my_ - 6), (mx_ + 14, my_ + 4)], [(E[0] - 2, E[1] - 18), (E[0] + 6, E[1] - 6)]])
    c.ink(b.sleeve(True, 0.44, 8.2, 7.4), tee, lw=3.0, shade=0.4, hi=0.25)
    paper = Sh([rot_pts([(Wr[0] - 6, Wr[1] - 62), (Wr[0] + 60, Wr[1] - 62), (Wr[0] + 60, Wr[1] + 10), (Wr[0] - 6, Wr[1] + 10)], -6, Wr[0], Wr[1])])
    c.ink(paper, (236, 232, 214), lw=2.6, shade=0.35, sw=10, hi=0.2)
    def grid(t):
        x0_, y0_ = Wr[0] + 8, Wr[1] - 52
        for i in range(6):
            for j in range(5):
                q = rot_pts([(x0_ + i * 8, y0_ + j * 8), (x0_ + i * 8 + 7, y0_ + j * 8), (x0_ + i * 8 + 7, y0_ + j * 8 + 7),
                             (x0_ + i * 8, y0_ + j * 8 + 7)], -6, Wr[0], Wr[1])
                t.ink(Sh([q]), (30, 30, 40) if (i * 3 + j) % 7 == 0 else (250, 250, 246), lw=0.8, shade=0, hi=0, ao=0, tex=0, wob=0)
        for k in range(3):
            a, b2 = rot_pts([(Wr[0] + 2, Wr[1] - 4 + k * 0), (Wr[0] + 52, Wr[1] - 4)], -6, Wr[0], Wr[1])
            t.stroke([a, b2], 1.2, (120, 120, 130), opacity=0.7)
    clip_draw(c, paper, grid)
    b.hand(True, "hold", d=(0.3, -1.0), size=1.0)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Captain Gus / Commodore Gus (bar stool)
def bar_stool(c, x, y_floor, seat_y, w=70, col=(200, 40, 56)):
    """Chrome bar stool (screen px): base at y_floor, seat top at seat_y."""
    chrome, chrome_sh = (200, 204, 220), (120, 120, 150)
    c.soft(ell(x, y_floor - 2, w * 0.75, w * 0.12), (30, 8, 40), 0.45, 4)
    c.ink(ell(x, y_floor - 6, w * 0.55, w * 0.13), chrome, lw=2.6, shade=0.5, scol=chrome_sh, hi=0.5)
    c.ink(rect(x - 6, seat_y + 10, x + 6, y_floor - 8), chrome, lw=2.6, shade=0.5, sw=5, scol=chrome_sh, hi=0.6, hw=2)
    ry_ = y_floor - (y_floor - seat_y) * 0.42
    c.ink(ell(x, ry_, w * 0.42, w * 0.1), (0, 0, 0, 0), lw=5.0, oc=chrome_sh, line_only=True)
    c.ink(ell(x, ry_, w * 0.42, w * 0.1), (0, 0, 0, 0), lw=2.0, oc=chrome, line_only=True, inner=-0.2)
    c.ink(rrect(x - w / 2, seat_y, x + w / 2, seat_y + 18, 8), col, lw=2.8, shade=0.5, sw=6, hi=0.5, hw=3)
    c.ink(ell(x, seat_y + 2, w / 2, 7), hi_col(col, 0.2), lw=2.2, shade=0.2, hi=0.4)
    return ry_


def paint_gus(height=392, name="hs_captain_gus.png", commodore=False):
    W, Hc = 420, 700 if commodore else 620
    skin = (246, 196, 168)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=403)
    yf = Hc - 14
    b = Body(c, 160, yf, height, skin=skin,
             build=dict(shoulders=1.12, waist=1.25, hips=1.15, limbs=1.12, head=1.06, legs=0.98, neck=0.8, chest=1.2, belly=2.6,
                        hand=1.08, foot=1.05),
             pose=dict(arm_n=24, fore_n=70, arm_f=20, fore_f=60, leg_n=84, shin_n=-76, leg_f=78, shin_f=-74, lean=-4,
                       head_dx=0.6, head_dy=-1.5), seed=43)
    navy, navy_sh = (44, 56, 120), (24, 28, 74)
    gold = (246, 200, 80)
    white, white_sh = (248, 248, 250), (190, 190, 214)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # the stool under him
    seat_y = b.P(0, b.hip_y - 3.2)[1]
    bar_stool(c, b.P(0.5, 0)[0], yf, seat_y, w=b.u * 22, col=(200, 40, 56))
    if commodore:   # towering white wig, back curls behind the head
        for k in range(6):
            cx_, cy_ = hx - r * 1.05 + (k % 2) * r * 0.25, hy - ry * 0.2 + k * ry * 0.32
            c.ink(ell(cx_, cy_, r * 0.36, r * 0.3), white, lw=2.6, shade=0.5, scol=white_sh, hi=0.3)
    # far arm (behind), resting on the knee
    c.ink(b.arm_shape(False), shade_col(navy, 0.85), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=shade_col(skin, 0.86))
    # legs (seated) + boots
    def boots(bb, near):
        bb.shoe(near, (60, 40, 36) if near else (46, 32, 30), (30, 20, 20), "boot", length=1.0)
    legs(b, navy, w=(10.0, 7.6, 7.0), scol=navy_sh, shoe=boots)
    # coat body (double-breasted), belly
    torso = Sh([b.torso_pts(slack=1.4, hem=b.hip_y - 4, flare=1.2, neck_open=0.9)])
    c.ink(torso, navy, lw=3.0, shade=0.55, sw=22, scol=navy_sh, hi=0.3, rim=0.2, rcol=(140, 160, 255))
    sy, sx = b.shoulder_y, b.lean_dx
    for k in range(4):
        for dx in (1.4, 5.2):
            x_, y_ = b.P(sx + dx + k * 0.5 + b.b["belly"] * 0.35 * (k / 3), sy - 7 - k * 6.2)
            c.ink(ell(x_, y_, 4.2, 4.2), gold, lw=1.6, shade=0.3, hi=0.6, hw=1.5)
    c.stroke(b.Ps([(sx + 0.8, sy - 2), (sx + 2.6, b.hip_y - 3)]), 2.0, navy_sh)
    # epaulette on the far shoulder (behind beard) + patches
    c.ink(ell(*b.P(b.sh_f[0], sy - 0.4), 14, 6, -10), gold, lw=2.2, shade=0.4, hi=0.5)
    pa = b.P(-3.2, sy - 26)
    c.ink(rrect(pa[0] - 12, pa[1] - 10, pa[0] + 12, pa[1] + 10, 3), (120, 90, 70), lw=2.0, shade=0.3, tex=0.3)
    folds(c, [b.Ps([(-3, b.hip_y + 2), (-2, b.hip_y + 10)]), b.Ps([(4, b.hip_y + 3), (6, b.hip_y + 12)])], navy_sh, 1.8, 0.7)
    # head
    head = Sh([b.head_pts(jaw=1.1, chin=1.05, cheek=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.15, fa["eye_n"][1] + ry * 0.4, r * 0.36, (240, 90, 100), 0.55)
    b.eyes(iris=(70, 120, 190), look=(0.35, 0.25), lid=0.42 if not commodore else 0.3, lower=0.1, size=0.95)
    b.brows(col=(240, 240, 246), lift_n=0.1 if commodore else 0.0, lift_f=0.05, tilt_n=0.3, tilt_f=0.2, w=r * 0.2, arch=0.1)
    # big beard
    beard = blob([(hx - r * 0.42, hy + ry * 0.05), (hx - r * 0.2, hy + ry * 0.55), (hx + r * 0.3, hy + ry * 0.48),
                  (hx + r * 0.75, hy + ry * 0.55), (hx + r * 1.12, hy + ry * 0.45), (hx + r * 1.2, hy + ry * 0.9),
                  (hx + r * 1.0, hy + ry * 1.5), (hx + r * 0.5, hy + ry * 1.95), (hx - r * 0.1, hy + ry * 1.85),
                  (hx - r * 0.55, hy + ry * 1.3), (hx - r * 0.65, hy + ry * 0.6)], 2)
    c.ink(beard, white, lw=3.0, shade=0.5, sw=r * 0.4, scol=white_sh, hi=0.4, rim=0.15)
    hair_strands(c, [[(hx + r * 0.2, hy + ry * 0.9), (hx + r * 0.3, hy + ry * 1.5)], [(hx + r * 0.7, hy + ry * 0.9), (hx + r * 0.65, hy + ry * 1.6)],
                     [(hx - r * 0.2, hy + ry * 0.9), (hx - r * 0.1, hy + ry * 1.5)]], white_sh, w=1.6)
    # moustache + red nose
    mx, my = fa["mouth"]
    c.ink(blob([(mx - r * 0.55, my - ry * 0.05), (mx - r * 0.1, my - ry * 0.22), (mx + r * 0.3, my - ry * 0.2),
                (mx + r * 0.62, my - ry * 0.02), (mx + r * 0.3, my + ry * 0.06), (mx - r * 0.2, my + ry * 0.06)], 2), white, lw=2.6,
          shade=0.45, scol=white_sh, hi=0.4)
    b.nose("round", 1.25, col=(244, 140, 130))
    b.ear(1.05)
    if commodore:
        # towering powdered wig with rows of curls
        crown = blob([(hx - r * 1.15, hy - ry * 0.1), (hx - r * 1.2, hy - ry * 1.2), (hx - r * 0.9, hy - ry * 2.4),
                      (hx - r * 0.2, hy - ry * 3.0), (hx + r * 0.6, hy - ry * 2.6), (hx + r * 1.05, hy - ry * 1.6),
                      (hx + r * 1.05, hy - ry * 0.55), (hx + r * 0.5, hy - ry * 0.6), (hx - r * 0.2, hy - ry * 0.5),
                      (hx - r * 0.5, hy - ry * 0.05)], 2)
        c.ink(crown, white, lw=3.0, shade=0.5, sw=r * 0.5, scol=white_sh, hi=0.4, rim=0.2, rcol=(200, 200, 255))
        rngw = random.Random(7)
        for row in range(5):
            yy = hy - ry * (0.75 + row * 0.48)
            for k in range(4):
                xx = hx - r * 1.0 + k * r * 0.62 + (row % 2) * r * 0.3
                c.stroke([(xx - r * 0.24, yy + r * 0.05), (xx - r * 0.1, yy + r * 0.2), (xx + r * 0.14, yy + r * 0.12),
                          (xx + r * 0.2, yy - r * 0.08)], 2.0, white_sh, taper=(0.3, 0.3), opacity=0.9)
                c.stroke([(xx - r * 0.12, yy - r * 0.1), (xx + r * 0.06, yy - r * 0.16)], 1.6, (255, 255, 255), opacity=0.9)
        c.ink(crown, (0, 0, 0, 0), lw=3.0, line_only=True)
        # a tiny anchor ribbon at the top
        c.ink(Sh([[(hx - r * 0.3, hy - ry * 2.9), (hx + r * 0.1, hy - ry * 3.1), (hx - r * 0.05, hy - ry * 2.7)]]), (60, 90, 200), lw=1.8)
        for k in range(2):   # side curls over the ear
            c.ink(ell(hx - r * 0.75, hy + ry * (0.05 + k * 0.35), r * 0.3, r * 0.22), white, lw=2.4, shade=0.45, scol=white_sh)
    else:
        # battered captain's hat
        cap_top = blob([(hx - r * 1.05, hy - ry * 0.7), (hx - r * 1.2, hy - ry * 1.15), (hx - r * 0.6, hy - ry * 1.45),
                        (hx + r * 0.6, hy - ry * 1.42), (hx + r * 1.25, hy - ry * 1.05), (hx + r * 1.05, hy - ry * 0.68)], 2)
        c.ink(cap_top, (238, 236, 230), lw=3.0, shade=0.5, sw=r * 0.3, scol=(170, 170, 190), hi=0.4)
        c.ink(Sh([[(hx - r * 1.02, hy - ry * 0.72), (hx + r * 1.04, hy - ry * 0.7), (hx + r * 1.0, hy - ry * 0.48), (hx - r * 1.0, hy - ry * 0.5)]]),
              (30, 30, 50), lw=2.6, shade=0.3, hi=0.3)
        c.ink(Sh([chaikin([(hx + r * 0.1, hy - ry * 0.5), (hx + r * 1.0, hy - ry * 0.52), (hx + r * 1.5, hy - ry * 0.32),
                           (hx + r * 0.9, hy - ry * 0.26), (hx + r * 0.1, hy - ry * 0.34)], 1)]), (24, 24, 36), lw=2.6, shade=0.2, hi=0.5,
              hw=3)
        c.ink(ell(hx + r * 0.25, hy - ry * 0.85, r * 0.24, r * 0.2), gold, lw=2.0, shade=0.3, hi=0.5)
        c.stroke([(hx + r * 0.25, hy - ry * 0.98), (hx + r * 0.25, hy - ry * 0.72)], 1.8, (150, 100, 30))
        c.stroke([(hx - r * 0.6, hy - ry * 1.3), (hx - r * 0.2, hy - ry * 1.12)], 1.6, (170, 170, 190), opacity=0.8)   # dent
        for k in range(3):   # white hair tufts under the cap
            c.ink(ell(hx - r * 0.95 + k * 0.1, hy - ry * 0.35 + k * ry * 0.22, r * 0.18, r * 0.14), white, lw=2.0, shade=0.4, scol=white_sh)
    # near arm: big mug of grog on the knee
    c.ink(b.arm_shape(True), navy, lw=3.0, shade=0.5, scol=navy_sh, rim=0.2, rcol=(140, 160, 255))
    wx, wy = b.P(*b.wrist_n)
    c.ink(ell(wx + 46, wy - 16, 10, 13), (0, 0, 0, 0), lw=5.0, oc=(200, 160, 90), line_only=True)
    mug = rrect(wx + 4, wy - 40, wx + 44, wy + 8, 6)
    c.ink(mug, (210, 170, 100), lw=3.0, shade=0.45, sw=12, hi=0.4)
    c.ink(ell(wx + 24, wy - 40, 20, 6), (255, 250, 236), lw=2.2, shade=0.2)
    for k in range(3):
        c.ink(ell(wx + 12 + k * 12, wy - 44 - (k % 2) * 4, 7, 6), (255, 250, 236), lw=1.6, shade=0.2)
    c.stroke([(wx + 6, wy - 24), (wx + 42, wy - 24)], 2.0, (150, 110, 60))
    c.stroke([(wx + 6, wy - 6), (wx + 42, wy - 6)], 2.0, (150, 110, 60))
    b.hand(True, "hold", d=(1.0, 0.0))
    c.ink(ell(*b.P(*b.wrist_n), 9 * b.u / 4, 6 * b.u / 4), gold, lw=1.8, shade=0.3) if False else None
    c.ink(b.segment(((b.elbow_n[0] + b.wrist_n[0] * 3) / 4, (b.elbow_n[1] + b.wrist_n[1] * 3) / 4), b.wrist_n, 8.0, 7.4), navy,
          lw=2.6, shade=0.4, scol=navy_sh)
    E = b.P(*b.wrist_n)
    c.stroke([(E[0] - 6, E[1] - 12), (E[0] - 2, E[1] + 12)], 3.0, gold)
    return finish_sprite(c, name, flip=True)


# =========================================================================== Sal (diner cook)
def paint_sal(height=415, name="hs_sal.png"):
    W, Hc = 480, 640
    skin = (210, 150, 110)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.2, seed=404)
    b = Body(c, 200, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.35, waist=1.35, hips=1.2, limbs=1.45, head=0.98, legs=0.94, neck=1.4, chest=1.6, belly=3.0,
                        hand=1.18, foot=1.1),
             pose=dict(arm_n=34, fore_n=92, arm_f=28, fore_f=110, leg_n=-6, shin_n=3, leg_f=8, shin_f=-4, lean=-2,
                       head_dx=0.8, head_dy=-1.2), seed=44)
    white, white_sh = (248, 246, 240), (190, 186, 210)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    hair = (40, 28, 30)

    def spatula(wx, wy, ang, s=1.0, col=(214, 216, 230)):
        dx_, dy_ = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
        top_ = (wx + dx_ * 70 * s, wy + dy_ * 70 * s)
        c.ink(limb([(wx - dx_ * 20, wy - dy_ * 20), top_], [9, 8], smooth=0), (70, 40, 30), lw=2.6, shade=0.4)
        blade = Sh([rot_pts([(top_[0] - 22 * s, top_[1] - 60 * s), (top_[0] + 22 * s, top_[1] - 60 * s), (top_[0] + 22 * s, top_[1] + 2),
                             (top_[0] - 22 * s, top_[1] + 2)], ang, top_[0], top_[1])])
        c.ink(blade, col, lw=3.0, shade=0.5, sw=10, hi=0.5)
        for k in range(3):
            c.ink(Sh([rot_pts([(top_[0] - 14 * s + k * 11 * s, top_[1] - 50 * s), (top_[0] - 9 * s + k * 11 * s, top_[1] - 50 * s),
                               (top_[0] - 9 * s + k * 11 * s, top_[1] - 12 * s), (top_[0] - 14 * s + k * 11 * s, top_[1] - 12 * s)],
                              ang, top_[0], top_[1])]), (120, 124, 140), lw=1.4)
    # far arm: raised spatula behind
    c.ink(b.arm_shape(False), shade_col(skin, 0.86), lw=3.0, shade=0.4)
    fw = b.P(*b.wrist_f)
    spatula(fw[0] + 6, fw[1] - 4, 25, 0.9, (180, 182, 200))
    b.hand(False, "fist", col=shade_col(skin, 0.86), d=(0.4, -1.0))
    c.ink(b.sleeve(False, 0.72, 5.6, 5.0), shade_col(white, 0.85), lw=3.0, shade=0.4)
    # checked trousers + clogs
    def clogs(bb, near):
        bb.shoe(near, (40, 36, 46) if near else (30, 28, 36), (20, 20, 24), "shoe", length=1.0)
    for near in (False, True):
        sh = b.leg_shape(near, w=(10.0, 8.2, 7.8))
        c.ink(sh, (240, 240, 236) if near else (200, 200, 210), lw=3.2, shade=0.5, scol=(150, 150, 170), hi=0.2)
        def checks(t, sh=sh):
            bx0, by0, bx1, by1 = sh.bbox()
            for i, x in enumerate(np.arange(bx0 - 10, bx1 + 10, 12)):
                for j, y in enumerate(np.arange(by0 - 10, by1 + 10, 12)):
                    if (i + j) % 2 == 0:
                        t.ink(rect(x, y, x + 12, y + 12), (40, 40, 56), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.85)
        clip_draw(c, sh, checks)
        c.ink(sh, (0, 0, 0, 0), lw=3.2, line_only=True)
        clogs(b, near)
    # torso: white tee + long apron, stained
    c.ink(b.neck_shape(1.0), skin, lw=3.0, shade=0.6, sw=10)
    torso = Sh([b.torso_pts(slack=1.2, hem=b.hip_y - 2, flare=1.0, neck_open=1.0)])
    c.ink(torso, white, lw=3.2, shade=0.55, sw=22, scol=white_sh, hi=0.3)
    sy, sx = b.shoulder_y, b.lean_dx
    ap = Sh([chaikin(b.Ps([(sx + 0.2, sy - 5), (sx + 5.6, sy - 5), (sx + 7.0 + b.b["belly"] * 0.8, b.hip_y + 12),
                           (6.8 * b.b["hips"] + 1.5, b.hip_y - 24), (-5.2 * b.b["hips"], b.hip_y - 24), (-4.4, b.hip_y + 8),
                           (sx - 1.0, sy - 12)]), 1)])
    c.ink(ap, (236, 234, 226), lw=3.0, shade=0.55, sw=18, scol=white_sh, hi=0.3)
    rng = random.Random(4)
    for _ in range(6):
        x_, y_ = b.P(rng.uniform(-3, 7), rng.uniform(b.hip_y - 20, b.hip_y + 14))
        col = rng.choice([(200, 60, 50), (190, 140, 60), (120, 80, 40)])
        c.soft(ell(x_, y_, rng.uniform(5, 10), rng.uniform(4, 8)), col, 0.4, 2, clip=ap)
    c.stroke(b.Ps([(-5.0, b.hip_y + 9), (sx + 7.6, b.hip_y + 11)]), 3.0, white_sh)
    c.stroke(b.Ps([(sx + 0.2, sy - 5), (sx - 2.2, sy + 1)]), 3.0, white_sh)
    tx_, ty_ = b.P(sx + 3.2, sy - 9)
    c.ink(rrect(tx_ - 18, ty_ - 7, tx_ + 18, ty_ + 7, 3), (60, 200, 196), lw=1.8, shade=0.2)
    c.label(tx_, ty_, "SAL", 8, (20, 50, 60), "Black")
    # head: paper hat, thick moustache, stubble, eyes on the tin (looking up)
    head = Sh([b.head_pts(jaw=1.2, chin=1.1, cheek=1.06)])
    c.ink(head, skin, lw=3.2, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.72), hi=0.35, rim=0.15, rcol=(240, 150, 120))
    fa = b.face_anchor()
    c.soft(Sh([[(hx - r * 0.2, hy + ry * 0.55), (hx + r * 1.0, hy + ry * 0.5), (hx + r * 0.9, hy + ry * 1.2), (hx - r * 0.3, hy + ry * 0.95)]]),
           shade_col(skin, 0.5), 0.35, 4, clip=head)
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.42, r * 0.3, (230, 90, 80), 0.4)
    b.eyes(iris=(60, 40, 30), look=(0.3, -0.45), lid=0.12, size=1.0)
    b.brows(col=hair, lift_n=0.22, lift_f=0.18, tilt_n=-0.2, tilt_f=-0.3, w=r * 0.2, arch=0.12)
    b.nose("round", 1.2)
    mx, my = fa["mouth"]
    b.mouth("grin", mx, my + ry * 0.1, r * 0.55, r * 0.34)
    c.ink(blob([(mx - r * 0.65, my + ry * 0.02), (mx - r * 0.2, my - ry * 0.26), (mx + r * 0.2, my - ry * 0.28), (mx + r * 0.68, my - ry * 0.04),
                (mx + r * 0.42, my + ry * 0.06), (mx, my - ry * 0.06), (mx - r * 0.4, my + ry * 0.1)], 2), hair, lw=2.6, shade=0.3, hi=0.3,
          hcol=(110, 90, 90))
    b.ear(1.0)
    c.ink(blob([(hx - r * 1.05, hy + ry * 0.3), (hx - r * 1.1, hy - ry * 0.3), (hx - r * 0.6, hy - ry * 0.6), (hx - r * 0.4, hy + ry * 0.1)], 2),
          hair, lw=2.6, shade=0.3)
    hat = Sh([[(hx - r * 1.12, hy - ry * 0.35), (hx + r * 1.08, hy - ry * 0.48), (hx + r * 1.12, hy - ry * 1.12), (hx + r * 0.7, hy - ry * 1.32),
               (hx - r * 0.6, hy - ry * 1.28), (hx - r * 1.16, hy - ry * 1.0)]])
    c.ink(hat, white, lw=3.0, shade=0.45, sw=r * 0.3, scol=white_sh, hi=0.4)
    c.stroke([(hx - r * 1.1, hy - ry * 0.55), (hx + r * 1.1, hy - ry * 0.68)], 2.0, white_sh)
    c.ink(rrect(hx - r * 0.1, hy - ry * 1.05, hx + r * 0.45, hy - ry * 0.78, 3), (220, 50, 60), lw=1.8, shade=0.2)
    # near arm: spatula forward, hairy forearm
    arm = b.arm_shape(True)
    c.ink(arm, skin, lw=3.2, shade=0.5, rim=0.15, rcol=(240, 150, 120))
    E, Wr = b.P(*b.elbow_n), b.P(*b.wrist_n)
    rngh = random.Random(9)
    def fur(t):
        for _ in range(26):
            k = rngh.uniform(0.1, 0.9)
            x_, y_ = E[0] + (Wr[0] - E[0]) * k + rngh.uniform(-8, 8), E[1] + (Wr[1] - E[1]) * k + rngh.uniform(-10, 6)
            t.stroke([(x_, y_), (x_ + 3, y_ - 5)], 1.2, shade_col(skin, 0.4), taper=(0.2, 0.6), opacity=0.7)
    clip_draw(c, arm, fur)
    c.ink(b.sleeve(True, 0.72, 5.8, 5.2), white, lw=3.2, shade=0.5, scol=white_sh)
    spatula(Wr[0] + 8, Wr[1] - 2, 40, 1.0)
    b.hand(True, "fist", size=1.0, d=(0.6, -0.8))
    return finish_sprite(c, name, flip=False)


# =========================================================================== Mortimer (ancient usher)
def paint_mortimer(height=372, name="hs_mortimer.png"):
    W, Hc = 420, 600
    skin = (240, 210, 190)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=405)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=0.82, hips=0.86, limbs=0.82, head=1.06, legs=1.0, neck=0.9, chest=0.8,
                        hand=0.92, foot=1.05),
             pose=dict(arm_n=58, fore_n=10, arm_f=-6, fore_f=60, leg_n=-4, shin_n=3, leg_f=5, shin_f=-3, lean=10,
                       head_dx=2.2, head_dy=-2.4), seed=45)
    red, red_sh = (196, 36, 56), (120, 20, 50)
    gold, gold_sh = (246, 200, 80), (180, 120, 40)
    black, black_sh = (40, 34, 50), (20, 16, 26)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (behind), hand at the small of the back
    c.ink(b.arm_shape(False), shade_col(red, 0.8), lw=2.8, shade=0.4)
    b.hand(False, "relaxed", col=(236, 236, 240), d=(1.0, 0.2))
    # black trousers with a gold stripe + shiny shoes
    def shoes(bb, near):
        bb.shoe(near, (30, 26, 34) if near else (24, 20, 28), (20, 16, 20), "shoe", length=1.1)
    legs(b, black, w=(7.6, 5.4, 4.8), scol=black_sh, shoe=shoes)
    for near in (False, True):
        hp, an = (b.hip_n, b.ankle_n) if near else (b.hip_f, b.ankle_f)
        if near:
            c.stroke(b.Ps([(hp[0] - 2.2, hp[1] - 2), ((hp[0] + b.knee_n[0]) / 2 - 2.4, (hp[1] + b.knee_n[1]) / 2),
                           (an[0] - 1.8, an[1] + 4)]), 2.4, gold, taper=(0, 0))
    # red jacket with tails, gold buttons, epaulettes, braid
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    jacket = Sh([b.torso_pts(slack=0.8, hem=b.hip_y - 5, flare=1.0, neck_open=0.8)])
    c.ink(jacket, red, lw=3.0, shade=0.55, sw=18, scol=red_sh, hi=0.35, rim=0.2, rcol=(255, 160, 180))
    sy, sx = b.shoulder_y, b.lean_dx
    tail = Sh([chaikin(b.Ps([(-5.4, b.hip_y + 2), (-1.0, b.hip_y + 1), (-2.0, b.hip_y - 14), (-6.6, b.hip_y - 12)]), 1)])
    c.ink(tail, shade_col(red, 0.86), lw=2.8, shade=0.4)
    for k in range(5):
        f = k / 4
        x_, y_ = b.P(sx * (1 - f * 0.6) + 3.4 + f * 0.6, sy - 5 - k * 5.6)
        c.ink(ell(x_, y_, 3.8, 3.8), gold, lw=1.5, shade=0.3, hi=0.6, hw=1.5)
    c.stroke(b.Ps([(sx + 1.2, sy - 1), (sx * 0.4 + 1.6, b.hip_y - 4)]), 2.0, red_sh)
    for X in (b.sh_f[0], b.sh_n[0] + 1.6):
        ex_, ey_ = b.P(X, sy - 0.2)
        c.ink(ell(ex_, ey_, 15, 6), gold, lw=2.2, shade=0.4, scol=gold_sh, hi=0.5)
        for k in range(4):
            c.stroke([(ex_ - 12 + k * 7, ey_ + 4), (ex_ - 13 + k * 7, ey_ + 14)], 2.0, gold)
    c.stroke(b.Ps([(b.sh_n[0] + 2, sy - 2), (sx - 0.6, sy - 9), (b.sh_n[0] + 3, sy - 14)]), 2.2, gold)
    # badge
    bx_, by_ = b.P(sx + 5.0, sy - 9)
    c.ink(rrect(bx_ - 22, by_ - 9, bx_ + 22, by_ + 9, 3), (250, 230, 150), lw=1.8, shade=0.3, hi=0.4)
    c.label(bx_, by_ - 2, "MORTIMER", 5, (110, 30, 30), "Black")
    c.label(bx_, by_ + 4.5, "UNDEFEATED", 4, (110, 30, 30), "Bold")
    # head: long nose, tufts of white hair, pillbox hat, monocle-free squint
    head = Sh([b.head_pts(jaw=0.92, chin=1.06, cheek=0.94, chin_drop=1.04)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 170, 160))
    fa = b.face_anchor()
    for (ex, ey), k in ((fa["eye_n"], 1.0), (fa["eye_f"], 0.6)):   # wrinkles
        c.stroke([(ex + r * 0.28 * k, ey + ry * 0.18), (ex + r * 0.4 * k, ey + ry * 0.05)], 1.3, shade_col(skin, 0.6), opacity=0.8)
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.45, r * 0.28, (240, 110, 120), 0.4)
    b.eyes(iris=(90, 110, 150), look=(0.45, 0.0), lid=0.45, lower=0.15, size=0.95)
    b.brows(col=(250, 250, 250), lift_n=0.12, lift_f=0.04, tilt_n=-0.6, tilt_f=-0.5, w=r * 0.18, arch=0.08)
    b.nose("hook", 1.35)
    b.mouth("frown", fa["mouth"][0] - r * 0.02, fa["mouth"][1] + ry * 0.06, r * 0.36, r * 0.18)
    b.ear(1.15, jug=0.4)
    for k, (dx, dy) in enumerate(((-0.9, -0.15), (-1.05, 0.2), (-0.75, -0.5))):
        x_, y_ = hx + r * dx, hy + ry * dy
        c.ink(blob([(x_ - r * 0.25, y_ + ry * 0.1), (x_ - r * 0.35, y_ - ry * 0.2), (x_, y_ - ry * 0.25), (x_ + r * 0.2, y_)], 2),
              (250, 250, 252), lw=2.2, shade=0.45, scol=(190, 190, 214))
    hb = (hx - r * 0.1, hy - ry * 0.7)
    hat = Sh([rot_pts([(hb[0] - r * 0.6, hb[1]), (hb[0] + r * 0.6, hb[1]), (hb[0] + r * 0.52, hb[1] - ry * 0.55), (hb[0] - r * 0.52, hb[1] - ry * 0.55)],
                      -8, hb[0], hb[1])])
    c.ink(hat, red, lw=3.0, shade=0.5, scol=red_sh, hi=0.4)
    c.ink(Sh([rot_pts([(hb[0] - r * 0.62, hb[1]), (hb[0] + r * 0.62, hb[1]), (hb[0] + r * 0.6, hb[1] - ry * 0.12), (hb[0] - r * 0.6, hb[1] - ry * 0.12)],
                      -8, hb[0], hb[1])]), gold, lw=2.2, shade=0.3)
    c.ink(Sh([rot_pts([(hb[0] - r * 0.52, hb[1] - ry * 0.55), (hb[0] + r * 0.52, hb[1] - ry * 0.55), (hb[0] + r * 0.5, hb[1] - ry * 0.47),
                       (hb[0] - r * 0.5, hb[1] - ry * 0.47)], -8, hb[0], hb[1])]), gold, lw=2.0, shade=0.3)
    c.stroke(rot_pts([(hb[0] + r * 0.4, hb[1]), (hb[0] + r * 0.9, hb[1] + ry * 0.6)], -8, hb[0], hb[1]), 1.6, gold)   # chin strap
    # near arm: flashlight held out like a sword, beam on
    c.ink(b.arm_shape(True), red, lw=3.0, shade=0.5, scol=red_sh, rim=0.2, rcol=(255, 160, 180))
    wx, wy = b.P(*b.wrist_n)
    ang = -30
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tip = (wx + ca * 80, wy + sa * 80)
    c.light_cone(tip, (tip[0] + ca * 140 - sa * 60, tip[1] + sa * 140 + ca * 60), (tip[0] + ca * 140 + sa * 60, tip[1] + sa * 140 - ca * 60),
                 (255, 246, 180), 0.55, 8)
    c.ink(limb([(wx - ca * 14, wy - sa * 14), tip], [12, 14], smooth=0), (60, 60, 76), lw=2.6, shade=0.4, hi=0.5)
    c.ink(ell(tip[0], tip[1], 6, 10, ang), (255, 250, 200), lw=2.2, shade=0, hi=0)
    c.glow2(tip[0], tip[1], 30, (255, 250, 200), 0.5)
    c.ink(ell(*b.P(*b.wrist_n), 7, 7), gold, lw=1.4) if False else None
    b.hand(True, "fist", col=(236, 236, 240), d=(ca, sa))
    cuff = b.P((b.elbow_n[0] + b.wrist_n[0] * 4) / 5, (b.elbow_n[1] + b.wrist_n[1] * 4) / 5)
    c.ink(ell(cuff[0], cuff[1], 8, 9, ang), gold, lw=2.0, shade=0.3)
    return finish_sprite(c, name, flip=False)


# =========================================================================== velvet rope (prop sprite)
ROPE_FEET = (1108, 776)      # in front of the auditorium doors in the Bijou lobby


def paint_velvet_rope(scale=None, name="hs_velvet_rope.png"):
    """Two brass posts and a sagging red rope, painted at the perspective scale of where it stands
    (prop sprites are not depth-scaled by the game)."""
    s = scale or geo().scale_at_y(ROPE_FEET[1])
    W, Hc = int(330 * s), int(200 * s)
    c = Canvas2(W, Hc, light=(-0.3, -0.95), lw=3.0, seed=406)
    gold, gold_sh = (240, 196, 80), (170, 110, 40)
    red, red_sh = (196, 30, 60), (110, 16, 50)
    y0 = Hc - 8
    xs = (40 * s, W - 40 * s)
    hpost = 130 * s
    c.soft(ell(W / 2, y0 - 2, W * 0.46, 10 * s), (30, 8, 40), 0.4, 5)
    for x in xs:
        c.ink(ell(x, y0 - 6 * s, 26 * s, 8 * s), gold, lw=2.8, shade=0.5, scol=gold_sh, hi=0.5)
        c.ink(rrect(x - 7 * s, y0 - hpost, x + 7 * s, y0 - 8 * s, 4), gold, lw=2.8, shade=0.5, sw=6, scol=gold_sh, hi=0.6, hw=2)
        c.ink(ell(x, y0 - hpost - 6 * s, 13 * s, 13 * s), gold, lw=2.8, shade=0.5, scol=gold_sh, hi=0.6, hw=3)
    a, b_ = (xs[0] + 8 * s, y0 - hpost + 6 * s), (xs[1] - 8 * s, y0 - hpost + 6 * s)
    pts = bez(a, ((a[0] + b_[0]) / 2, a[1] + 110 * s), b_, 40)
    c.stroke(pts, 15 * s + 3.2, INK, taper=(0, 0), smooth=0)
    c.stroke(pts, 15 * s, red, taper=(0, 0), smooth=0)
    c.stroke([(x, y + 5 * s) for x, y in pts], 5 * s, red_sh, taper=(0.05, 0.05), smooth=0, opacity=0.7)
    c.stroke([(x, y - 4 * s) for x, y in pts], 3 * s, (255, 140, 160), taper=(0.1, 0.1), smooth=0, opacity=0.7)
    for p in (a, b_):
        c.ink(ell(p[0], p[1], 9 * s, 7 * s), gold, lw=2.2, shade=0.4, hi=0.5)
    # little sign hanging from the middle of the rope
    mx, my = pts[len(pts) // 2]
    c.stroke([(mx - 14 * s, my + 4), (mx - 18 * s, my + 18 * s)], 1.6, (220, 200, 120))
    c.stroke([(mx + 14 * s, my + 4), (mx + 18 * s, my + 18 * s)], 1.6, (220, 200, 120))
    c.ink(rrect(mx - 44 * s, my + 16 * s, mx + 44 * s, my + 48 * s, 4), (250, 240, 214), lw=2.4, shade=0.3, hi=0.3)
    c.text(mx, my + 32 * s, "NOPE.", 15 * s, (170, 20, 50))
    sprite_grade(c, 0.9, (0.98, 0.88, 0.96))
    return finish_sprite(c, name, margin=2)


# =========================================================================== layout, sizes, composites
LAYOUT = {}
NPC_REL = {"hs_bree_marlowe": 0.92, "hs_lou": 0.94, "hs_captain_gus": 0.95, "hs_commodore_gus": 0.95, "hs_sal": 1.0,
           "hs_mortimer": 0.95}
NPC_FN = {"hs_bree_marlowe": paint_bree_marlowe, "hs_lou": paint_lou,
          "hs_captain_gus": lambda height: paint_gus(height, "hs_captain_gus.png", False),
          "hs_commodore_gus": lambda height: paint_gus(height, "hs_commodore_gus.png", True),
          "hs_sal": paint_sal, "hs_mortimer": paint_mortimer}


def npc_height(npc):
    """Crown height (px) for an NPC from the game's depth scale at its feet (first room it appears in)."""
    for rid, L in LAYOUT.items():
        for key, h in L["hotspots"].items():
            if h.get("npc") == npc:
                return round(DEX_H * depth_scale(h["feet"][1], Y_TOP, Y_BOT) * NPC_REL[npc])
    return round(DEX_H * depth_scale(NPC_FEET_Y, Y_TOP, Y_BOT) * NPC_REL.get(npc, 1.0))


def paint_npc(npc):
    return NPC_FN[npc](height=npc_height(npc))


# =========================================================================== room geometry helpers
STD_BACK = (330, 250, 1590, 690)
STD_WALK = [(200, Y_TOP), (1750, Y_TOP), (1820, 860), (1740, Y_BOT), (220, Y_BOT), (120, 860)]


def geo(back=STD_BACK, vp_x=960):
    """Room geometry only (no canvas) for computing hotspot boxes from room space."""
    return Room(None, (vp_x, vp_for_walk(Y_TOP, Y_BOT)), back, fc=1000)


def bbox_pts(pts, pad=0):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (int(min(xs) - pad), int(min(ys) - pad), int(max(xs) + pad), int(max(ys) + pad))


def box3(R, X0, X1, Y0, Y1, Z0, Z1, pad=0):
    return bbox_pts([R.pt(X, Y, Z) for X in (X0, X1) for Y in (Y0, Y1) for Z in (Z0, Z1)], pad)


def left_box(R, z0, z1, y0, y1, pad=0):
    return bbox_pts([R.pt(0, y, z) for y in (y0, y1) for z in (z0, z1)], pad)


def right_box(R, z0, z1, y0, y1, pad=0):
    return bbox_pts([R.pt(R.Wb, y, z) for y in (y0, y1) for z in (z0, z1)], pad)


def neon(c, x, y, s, size, col, kind="Black", angle=0, glow=0.45):
    """Glowing neon lettering: a coloured halo, the tube colour and a hot white-ish core."""
    w = len(s) * size * 0.62
    c.glow2(x, y, max(w * 0.7, size * 2.2), col, glow, sy=0.55)
    c.text(x, y, s, size, dk(col, 0.55), kind, stroke=3, sc=dk(col, 0.4), angle=angle)
    c.text(x, y, s, size, mix(col, (255, 255, 255), 0.55), kind, angle=angle)


def left_exit_door(sub, label="EXIT", door=(60, 170, 170), glass=True, sky=True, seed=1):
    """Exit door on a left-wall flat canvas at Z 100..280, Y 0..310 (the standard Act 1 / Act 4 spot)."""
    x0, x1 = sub.ax(280), sub.ax(100)
    y0, y1 = sub.by(310), sub.by(0)
    if glass:
        sub.ink(rect(x0 - 22, y0 - 22, x1 + 22, y1), (200, 196, 210), lw=3.0, shade=0.4)
        night_sky(sub, x0, y0, x1, y1, seed=seed, bot=(120, 60, 140)) if sky else \
            sub.ink(rect(x0, y0, x1, y1), ("v", (60, 40, 90), (30, 20, 50)), lw=2, shade=0.1)
        xm = (x0 + x1) / 2
        for xx in (x0, xm, x1):
            sub.ink(rect(xx - 8, y0, xx + 8, y1), door, lw=2.4, shade=0.3)
        sub.ink(rect(x0, y0 - 8, x1, y0 + 8), door, lw=2.4, shade=0.3)
        for xx in (xm - 30, xm + 30):
            sub.ink(rrect(xx - 5, y0 + (y1 - y0) * 0.45, xx + 5, y0 + (y1 - y0) * 0.6, 3), (230, 230, 240), lw=2.0)
        sub.stroke([(x0 + 20, y1 - 30), (xm - 20, y0 + 30)], 10, (255, 255, 255), opacity=0.14)
    else:
        flat_door(sub, x0, y0, x1, y1, door, frame=(236, 220, 230), knob="L", window=True, seed=seed)
    exit_sign(sub, (x0 + x1) / 2, y0 - 50, max(90, len(label) * 20 + 30), label)
    return x0, y0, x1, y1


def EXIT_BOX(R):
    return left_box(R, 78, 302, 0, 332)


def fg_hydrant(c, x, y, s=1.0, col=FG):
    c.ink(rrect(x - 30 * s, y - 150 * s, x + 30 * s, y + 40, 12), col, lw=0, shade=0.2, hi=0.2)
    c.ink(ell(x, y - 150 * s, 36 * s, 26 * s), col, lw=0, shade=0.2, hi=0.2)
    c.ink(rrect(x - 52 * s, y - 110 * s, x + 52 * s, y - 80 * s, 8), col, lw=0, shade=0.2, hi=0.2)


def fg_trash_can(c, x, y, s=1.0, col=FG):
    c.ink(Sh([[(x - 70 * s, y - 180 * s), (x + 70 * s, y - 180 * s), (x + 60 * s, y + 40), (x - 60 * s, y + 40)]]), col, lw=0, shade=0.2,
          hi=0.2)
    c.ink(ell(x, y - 182 * s, 80 * s, 22 * s), col, lw=0, shade=0.1, hi=0.2)
    for k in range(4):
        c.ink(ell(x - 40 * s + k * 26 * s, y - 196 * s - (k % 2) * 14 * s, 24 * s, 18 * s, k * 30), mix(col, (60, 40, 80), 0.3), lw=0)


# =========================================================================== 1. Downtown (street at night)
def storefront_window(c, x0, y0, x1, y1, inside=(255, 206, 120), frame=(220, 210, 220), seed=0, blinds=False):
    rng = random.Random(seed)
    c.ink(rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), frame, lw=2.8, shade=0.4, hi=0.3)
    c.ink(rect(x0, y0, x1, y1), ("v", hi_col(inside, 0.3), inside), lw=2.4, shade=0.2, hi=0)
    if blinds:
        for yy in np.arange(y0 + 6, y0 + (y1 - y0) * 0.4, 7):
            c.stroke([(x0 + 2, yy), (x1 - 2, yy)], 2.2, shade_col(inside, 0.8), taper=(0, 0), opacity=0.7)
    c.stroke([(x0 + 10, y1 - 10), (x0 + (x1 - x0) * 0.35, y0 + 10)], 9, (255, 255, 255), opacity=0.18)
    c.glow2((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.8, inside, 0.25)


def brick_facade(c, x0, y0, x1, y1, col, seed=0, mortar=None):
    rng = random.Random(seed)
    c.ink(rect(x0, y0, x1, y1), col, lw=3.0, shade=0.35, sw=50, hi=0.2, tex=0.2)
    mortar = mortar or shade_col(col, 0.65)
    for i, yy in enumerate(np.arange(y0 + 14, y1, 15)):
        c.stroke([(x0 + 2, yy), (x1 - 2, yy)], 1.2, mortar, opacity=0.4, taper=(0, 0))
        for xx in np.arange(x0 + (i % 2) * 18, x1, 36):
            c.stroke([(xx, yy - 14), (xx, yy)], 1.0, mortar, opacity=0.3, taper=(0, 0))
    for _ in range(int((x1 - x0) * (y1 - y0) / 30000)):
        stain(c, rng.uniform(x0, x1), rng.uniform(y0, y1 - 60), rng.uniform(20, 50), (40, 10, 40), 0.2, rng.randint(0, 2), rng.randint(0, 999))
    for _ in range(int((x1 - x0) / 160) + 1):
        chip(c, rng.uniform(x0 + 30, x1 - 30), rng.uniform(y0 + 40, y1 - 80), rng.uniform(14, 26), hi_col(col, 0.1), mortar, col,
             seed=rng.randint(0, 999), bw=30, bh=14)
    c.ink(rect(x0 - 8, y0 - 14, x1 + 8, y0 + 6), hi_col(col, 0.3), lw=2.8, shade=0.4, hi=0.3)       # cornice


def parking_meter(c, x, y, s=1.0):
    c.soft(ell(x, y + 2, 16 * s, 4 * s), (24, 6, 34), 0.5, 3)
    c.stroke([(x, y), (x, y - 70 * s)], 7 * s + 3, INK, taper=(0, 0))
    c.stroke([(x, y), (x, y - 70 * s)], 7 * s, (130, 130, 150), taper=(0, 0))
    c.ink(rrect(x - 14 * s, y - 108 * s, x + 14 * s, y - 68 * s, 7), (150, 160, 180), lw=2.4, shade=0.5, hi=0.5)
    c.ink(ell(x, y - 96 * s, 9 * s, 8 * s), (230, 240, 230), lw=1.8, shade=0.2)
    c.ink(rect(x - 4 * s, y - 84 * s, x + 4 * s, y - 78 * s), (255, 80, 80), lw=1.2)
    c.stroke([(x - 14 * s, y - 112 * s), (x - 22 * s, y - 120 * s)], 1.6, (255, 250, 200))   # "moved" sparkle
    c.stroke([(x + 14 * s, y - 112 * s), (x + 22 * s, y - 120 * s)], 1.6, (255, 250, 200))


def cafe_set(c, x, y, s=1.0):
    """Little café table with two chairs and a candle (the Date Round set)."""
    c.soft(ell(x, y + 2, 90 * s, 10 * s), (24, 6, 34), 0.5, 6)
    for dx, flip in ((-62, 1), (62, -1)):
        cx = x + dx * s
        c.stroke([(cx - 14 * s * flip, y), (cx - 14 * s * flip, y - 40 * s)], 4, INK, taper=(0, 0))
        c.stroke([(cx + 14 * s * flip, y), (cx + 14 * s * flip, y - 40 * s)], 4, INK, taper=(0, 0))
        c.ink(rrect(cx - 18 * s, y - 46 * s, cx + 18 * s, y - 38 * s, 3), (60, 200, 196), lw=2.0, shade=0.3)
        c.ink(Sh([[(cx + 16 * s * flip, y - 44 * s), (cx + 22 * s * flip, y - 44 * s), (cx + 26 * s * flip, y - 92 * s),
                   (cx + 18 * s * flip, y - 92 * s)]]), (60, 200, 196), lw=2.0, shade=0.3)
        c.ink(ell(cx + 22 * s * flip, y - 92 * s, 12 * s, 5 * s), (60, 200, 196), lw=2.0, shade=0.3)
    c.stroke([(x, y), (x, y - 56 * s)], 5, INK, taper=(0, 0))
    c.ink(ell(x, y - 2, 18 * s, 4 * s), (60, 50, 70), lw=1.6)
    c.ink(ell(x, y - 58 * s, 40 * s, 9 * s), (250, 246, 240), lw=2.4, shade=0.3, hi=0.3)
    c.ink(Sh([[(x - 40 * s, y - 58 * s), (x + 40 * s, y - 58 * s), (x + 34 * s, y - 42 * s), (x - 34 * s, y - 42 * s)]]), (236, 60, 110),
          lw=2.0, shade=0.3)
    c.ink(rect(x - 3 * s, y - 76 * s, x + 3 * s, y - 60 * s), (250, 240, 210), lw=1.4)
    c.ink(blob([(x, y - 88 * s), (x + 3 * s, y - 80 * s), (x, y - 76 * s), (x - 3 * s, y - 80 * s)], 1), (255, 200, 80), lw=0)
    c.glow2(x, y - 80 * s, 50 * s, GLOW, 0.6)
    c.glow2(x, y - 80 * s, 14 * s, (255, 250, 220), 0.8)


def camera_rig(c, x, y, s=1.0):
    """TV camera on a tripod + a softbox light stand (Speed Daters Live crew gear)."""
    c.soft(ell(x, y + 2, 70 * s, 8 * s), (24, 6, 34), 0.5, 6)
    for dx in (-40, 0, 40):
        c.stroke([(x, y - 90 * s), (x + dx * s, y)], 4.5, INK, taper=(0, 0))
        c.stroke([(x, y - 90 * s), (x + dx * s, y)], 2.4, (110, 110, 130), taper=(0, 0))
    cam = R_ = None
    c.ink(rrect(x - 46 * s, y - 136 * s, x + 30 * s, y - 92 * s, 6), (50, 46, 60), lw=2.6, shade=0.4, hi=0.3)
    c.ink(rrect(x - 74 * s, y - 128 * s, x - 44 * s, y - 100 * s, 4), (70, 66, 80), lw=2.4, shade=0.3)
    c.ink(ell(x - 76 * s, y - 114 * s, 8 * s, 13 * s), (120, 200, 255), lw=2.0, hi=0.6)
    c.ink(ell(x + 18 * s, y - 128 * s, 5 * s, 5 * s), (255, 40, 60), lw=1.2)
    c.glow2(x + 18 * s, y - 128 * s, 18 * s, (255, 60, 80), 0.6)
    c.ink(rrect(x - 30 * s, y - 132 * s, x + 4 * s, y - 120 * s, 3), (255, 70, 150), lw=1.4)
    lx = x + 100 * s
    c.stroke([(lx, y), (lx, y - 170 * s)], 4.5, INK, taper=(0, 0))
    for dx in (-26, 26):
        c.stroke([(lx, y - 40 * s), (lx + dx * s, y)], 3.5, INK, taper=(0, 0))
    soft = Sh([[(lx - 40 * s, y - 230 * s), (lx + 40 * s, y - 230 * s), (lx + 30 * s, y - 166 * s), (lx - 30 * s, y - 166 * s)]])
    c.ink(soft, (40, 36, 50), lw=2.6, shade=0.3)
    c.ink(Sh([[(lx - 34 * s, y - 222 * s), (lx + 34 * s, y - 222 * s), (lx + 26 * s, y - 172 * s), (lx - 26 * s, y - 172 * s)]]),
          (255, 246, 230), lw=1.6, shade=0, hi=0)
    c.glow2(lx, y - 196 * s, 120 * s, (255, 240, 220), 0.35)


def fountain(c, x, y, s=1.0, seed=0):
    """Tiered wishing fountain; (x, y) = front of the basin rim on the ground."""
    rng = random.Random(seed)
    stone, stone_sh = (190, 170, 200), (120, 100, 150)
    water = (90, 200, 220)
    c.soft(ell(x, y + 4, 170 * s, 22 * s), (24, 6, 34), 0.5, 8)
    c.ink(ell(x, y - 30 * s, 160 * s, 34 * s), stone, lw=3.0, shade=0.4, scol=stone_sh, hi=0.3, tex=0.2)
    c.ink(Sh([[(x - 160 * s, y - 30 * s), (x + 160 * s, y - 30 * s), (x + 156 * s, y - 2), (x - 156 * s, y - 2)]] ), stone, lw=3.0,
          shade=0.45, scol=stone_sh, hi=0.3, tex=0.2)
    c.ink(ell(x, y - 2, 156 * s, 22 * s), stone, lw=3.0, shade=0.45, scol=stone_sh, clip=Sh([[(x - 170 * s, y - 2), (x + 170 * s, y - 2),
                                                                                              (x + 170 * s, y + 40), (x - 170 * s, y + 40)]]))
    pool = ell(x, y - 32 * s, 140 * s, 26 * s)
    c.ink(pool, ("v", (40, 120, 160), water), lw=2.4, shade=0.2, hi=0.3)
    for _ in range(26):   # coins
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0, 0.8)
        cx_, cy_ = x + math.cos(a) * 130 * s * rr, y - 32 * s + math.sin(a) * 22 * s * rr
        c.ink(ell(cx_, cy_, 4 * s, 2.2 * s), rng.choice([(250, 210, 90), (220, 220, 230), (220, 150, 80)]), lw=0.8, clip=pool)
    c.ink(ell(x + 6 * s, y - 30 * s, 6 * s, 3.2 * s), (250, 250, 255), lw=1.2)
    c.glow2(x + 6 * s, y - 30 * s, 16 * s, (255, 255, 255), 0.6)
    c.ink(rect(x - 18 * s, y - 150 * s, x + 18 * s, y - 36 * s), stone, lw=2.8, shade=0.5, scol=stone_sh, hi=0.4)
    c.ink(ell(x, y - 150 * s, 74 * s, 16 * s), stone, lw=2.8, shade=0.4, scol=stone_sh, hi=0.3)
    c.ink(Sh([[(x - 74 * s, y - 150 * s), (x + 74 * s, y - 150 * s), (x + 40 * s, y - 128 * s), (x - 40 * s, y - 128 * s)]]), stone, lw=2.8,
          shade=0.5, scol=stone_sh)
    c.ink(ell(x, y - 152 * s, 64 * s, 11 * s), water, lw=2.0, shade=0.2, hi=0.4)
    c.ink(rect(x - 8 * s, y - 196 * s, x + 8 * s, y - 152 * s), stone, lw=2.4, shade=0.5, scol=stone_sh)
    c.ink(ell(x, y - 202 * s, 14 * s, 10 * s), (240, 200, 90), lw=2.2, shade=0.4, hi=0.5)    # gilded fish-ish finial
    for side in (-1, 1):
        for k in range(3):
            p0 = (x + side * (20 + k * 18) * s, y - 156 * s)
            p2 = (x + side * (90 + k * 26) * s, y - 40 * s)
            pts = bez(p0, (x + side * (70 + k * 22) * s, y - 200 * s + k * 14 * s), p2, 20)
            c.stroke(pts, 4.5 * s, (200, 245, 255), opacity=0.55, taper=(0.1, 0.3))
    c.stroke(bez((x, y - 204 * s), (x - 4 * s, y - 250 * s), (x, y - 206 * s), 10), 5 * s, (220, 250, 255), opacity=0.6)
    c.glow2(x, y - 90 * s, 170 * s, (90, 220, 255), 0.22)


def bus_shelter(c, x0, x1, y, seed=0):
    rng = random.Random(seed)
    top = y - 250
    c.soft(ell((x0 + x1) / 2, y + 4, (x1 - x0) * 0.6, 10), (24, 6, 34), 0.5, 8)
    c.ink(rect(x0 + 14, top + 30, x1 - 10, y - 50), (150, 200, 220, 110), lw=2.4, shade=0.1, hi=0.3)   # glass back panel
    # bench ad: a lawyer with a drawn-on moustache
    ax0, ay0, ax1, ay1 = x0 + 30, top + 60, x1 - 26, top + 160
    c.ink(rect(ax0, ay0, ax1, ay1), (250, 236, 180), lw=2.4, shade=0.2)
    c.ink(ell(ax0 + 34, ay0 + 44, 18, 22), (240, 200, 170), lw=1.8)
    c.ink(Sh([[(ax0 + 12, ay1), (ax0 + 56, ay1), (ax0 + 50, ay0 + 70), (ax0 + 18, ay0 + 70)]]), (60, 70, 120), lw=1.8)
    c.stroke([(ax0 + 22, ay0 + 52), (ax0 + 34, ay0 + 48), (ax0 + 46, ay0 + 52)], 3.2, INK)
    c.stroke([(ax0 + 22, ay0 + 52), (ax0 + 16, ay0 + 44)], 2.4, INK)
    c.stroke([(ax0 + 46, ay0 + 52), (ax0 + 52, ay0 + 44)], 2.4, INK)
    tx = (ax0 + 62 + ax1) / 2
    c.text(tx, ay0 + 24, "HURT?", 10, (200, 40, 60))
    c.text(tx, ay0 + 44, "SAD?", 9, (60, 60, 120))
    c.text(tx, ay0 + 66, "CALL", 8, (60, 60, 120))
    c.text(tx, ay0 + 82, "GARY", 10, (200, 40, 60))
    for X in (x0 + 10, x1 - 10):
        c.stroke([(X, y), (X, top)], 10, INK, taper=(0, 0))
        c.stroke([(X, y), (X, top)], 5, (120, 200, 200), taper=(0, 0))
    c.ink(Sh([[(x0 - 16, top), (x1 + 16, top - 8), (x1 + 20, top + 16), (x0 - 12, top + 22)]]), (60, 170, 170), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(x0 + 24, y - 64, x1 - 20, y - 50), (190, 110, 70), lw=2.4, shade=0.3, hi=0.3)
    for X in (x0 + 34, x1 - 30):
        c.stroke([(X, y - 50), (X, y - 4)], 5, INK, taper=(0, 0))
    # stop sign on a pole
    px = x1 + 10
    c.stroke([(px, y), (px, top - 80)], 8, INK, taper=(0, 0))
    c.stroke([(px, y), (px, top - 80)], 4, (150, 150, 170), taper=(0, 0))
    c.ink(rrect(px - 54, top - 124, px + 20, top - 74, 6), (60, 120, 210), lw=2.6, shade=0.3, hi=0.3)
    c.text(px - 17, top - 108, "CAMPUS", 10, (255, 255, 255))
    c.text(px - 17, top - 90, "SHUTTLE", 10, (255, 236, 120))


def paint_downtown():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(0.3, -0.95), lw=3.4, seed=4100)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), (-400, 100, 2320, 700), fc=1000)
    rng = random.Random(4100)
    HOR = 700
    # ---------------- sky + distant skyline
    c.ink(rect(-10, -10, W_BG + 10, HOR + 10), ("vy", -10, HOR, (26, 14, 66), (170, 60, 140)), lw=0, shade=0, hi=0, ao=0, tex=0.06, wob=0)
    for _ in range(140):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, 260)
        r = rng.choice([0.9, 1.2, 1.8])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.5, 1))
    mx, my = 820, 96
    c.glow2(mx, my, 220, (255, 220, 255), 0.4)
    c.ink(ell(mx, my, 40, 40), (255, 246, 220), lw=0, shade=0.3, sw=12, scol=(230, 200, 210), hi=0, tex=0.1)
    x = -20
    while x < W_BG:
        w = rng.uniform(60, 140)
        t = rng.uniform(140, 300)
        c.ink(rect(x, t, x + w, HOR), (56, 30, 96), lw=0, shade=0, hi=0, ao=0, tex=0.1)
        for wy in np.arange(t + 12, HOR - 300, 22):
            for wx in np.arange(x + 8, x + w - 10, 18):
                if rng.random() < 0.25:
                    c.ink(rect(wx, wy, wx + 7, wy + 9), (255, 200, 120), lw=0, shade=0, hi=0, ao=0, opacity=0.7)
        if rng.random() < 0.3:   # water tower / antenna
            c.stroke([(x + w / 2, t), (x + w / 2, t - 40)], 3, (56, 30, 96), taper=(0, 0))
            c.ink(ell(x + w / 2, t - 42, 3, 3), (255, 60, 80), lw=0)
        x += w + rng.uniform(-10, 10)
    # ---------------- sidewalk (floor plane) + curb + road at the very front
    def floor(sub):
        tiles(sub, (150, 104, 150), (136, 92, 140), 0, 0, sub.w, sub.h, size=80 * sub.density, seed=41, chipped=0.15, grout=(86, 56, 96))
    R.paint_plane("floor", -400, 2700, 0, R.z_front(160), floor, density=0.9, seed=41)
    for _ in range(18):
        x_, y_ = rng.uniform(0, W_BG), rng.uniform(720, 1000)
        c.soft(ell(x_, y_, rng.uniform(30, 90), rng.uniform(8, 20)), (50, 20, 60), 0.18, 10)
    for (x_, y_, rx) in ((520, 900, 90), (1440, 880, 70)):        # puddles reflecting neon
        c.ink(blob([(x_ - rx, y_), (x_ - rx * 0.4, y_ - 14), (x_ + rx * 0.6, y_ - 12), (x_ + rx, y_ + 2), (x_ + rx * 0.2, y_ + 14)], 2),
              ("v", (90, 60, 140), (60, 40, 110)), lw=1.6, oc=(60, 30, 80), shade=0, hi=0.4, hw=4)
    c.ink(rect(-10, 1000, W_BG + 10, 1020), (170, 150, 180), lw=3.0, shade=0.3, hi=0.4)
    c.ink(rect(-10, 1020, W_BG + 10, 1090), (40, 34, 56), lw=0, shade=0, hi=0, ao=0, tex=0.3)
    for k in range(6):
        c.ink(rect(80 + k * 340, 1056, 230 + k * 340, 1066), (230, 200, 80), lw=0, opacity=0.7)

    # ---------------- facades along the back (base y = HOR)
    # bus stop (left edge)
    bus_shelter(c, 20, 196, HOR + 12, seed=1)
    # Starlite Diner: pink chrome box, big windows, neon star sign
    dx0, dx1 = 238, 650
    c.ink(rect(dx0, 330, dx1, HOR), (226, 110, 170), lw=3.2, shade=0.35, sw=60, hi=0.25, tex=0.18)
    for yy in (380, 600):
        c.ink(rect(dx0 - 4, yy, dx1 + 4, yy + 14), (210, 214, 230), lw=2.4, shade=0.3, hi=0.6, hw=3)
    for (wx0, wx1) in ((dx0 + 24, dx0 + 150), (dx1 - 150, dx1 - 24)):
        storefront_window(c, wx0, 420, wx1, 586, (255, 200, 130), seed=wx0, blinds=True)
    # little silhouettes at the counter inside
    for wx in (dx0 + 70, dx1 - 90):
        c.ink(ell(wx, 540, 16, 18), (120, 60, 80), lw=0, opacity=0.7)
        c.ink(rrect(wx - 22, 556, wx + 22, 590, 8), (120, 60, 80), lw=0, opacity=0.7)
    flat_door(c, 394, 440, 494, HOR, (60, 190, 186), frame=(210, 214, 230), knob="R", window=True, seed=42)
    c.ink(rrect(384, 404, 504, 434, 5), (40, 30, 60), lw=2.2)
    neon(c, 444, 419, "OPEN 24 HRS", 10, (120, 255, 200), glow=0.35)
    c.ink(rrect(dx0 + 20, 250, dx1 - 20, 330, 14), (40, 30, 70), lw=3.0, shade=0.3, hi=0.2)
    neon(c, (dx0 + dx1) / 2 - 20, 290, "STARLITE", 40, (255, 90, 170), "Black")
    star = [(dx1 - 40 + (30 if k % 2 == 0 else 13) * math.cos(math.radians(-90 + k * 36)),
             252 + (30 if k % 2 == 0 else 13) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
    c.glow2(dx1 - 40, 252, 90, (255, 230, 90), 0.6)
    c.ink(Sh([star]), (255, 240, 140), lw=3.0, oc=(200, 120, 30), shade=0.2, hi=0.5)
    c.ink(rrect(dx0 + 110, 340, dx1 - 110, 372, 6), (250, 240, 214), lw=2.4, shade=0.2)
    c.text((dx0 + dx1) / 2, 356, "PIE 23 HOURS A DAY", 12, (190, 40, 80))
    c.ink(Sh([[(dx0 - 10, 600), (dx1 + 10, 600), (dx1 + 30, 640), (dx0 - 30, 640)]]), (60, 190, 186), lw=2.8, shade=0.3, hi=0.3) if False else None
    # bank-ish brick block with lit windows, behind the fountain
    brick_facade(c, 650, 300, 1090, HOR, (120, 70, 140), seed=43)
    facade_windows(c, 660, 1080, 330, 560, 2, 4, rng, lit=0.55, frame=(220, 200, 210))
    c.ink(rrect(720, 588, 1020, 622, 4), (60, 40, 70), lw=2.6, shade=0.3)
    c.text(870, 605, "SECOND BANK OF DOWNTOWN", 13, (240, 210, 140))
    c.ink(rect(760, 630, 980, HOR), (60, 40, 70), lw=2.6, shade=0.3)
    c.ink(rect(770, 640, 970, HOR), (255, 210, 140), lw=1.6, shade=0.15, opacity=0.5)
    for k in range(5):
        c.stroke([(780 + k * 46, 640), (780 + k * 46, HOR)], 5, (60, 40, 70), taper=(0, 0))
    poster(c, 690, 660, 54, 70, (255, 230, 120), lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.3, "LOST", 10, (190, 40, 60)),
                                                                   p.text(w_ / 2, h_ * 0.6, "CAT?", 10, (60, 60, 120))), angle=4, seed=44,
           peel="br")
    poster(c, 1048, 650, 60, 80, (60, 200, 196), lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.3, "SPEED", 9, (255, 255, 255)),
                                                                   p.text(w_ / 2, h_ * 0.52, "DATERS", 9, (255, 236, 120)),
                                                                   p.text(w_ / 2, h_ * 0.78, "LIVE!", 12, (200, 40, 110))), angle=-5, seed=45)
    # Quickmart: glassy fluorescent box
    qx0, qx1 = 1090, 1400
    c.ink(rect(qx0, 380, qx1, HOR), (70, 170, 160), lw=3.2, shade=0.35, sw=50, hi=0.2, tex=0.18)
    c.ink(rect(qx0 + 16, 470, qx1 - 16, HOR - 4), ("v", (230, 255, 240), (180, 230, 220)), lw=2.6, shade=0.15)
    for k in range(4):     # shelves glimpsed inside
        yy = 520 + k * 40
        c.stroke([(qx0 + 30, yy), (qx1 - 30, yy)], 3, (150, 170, 170), taper=(0, 0))
        for xx in np.arange(qx0 + 34, qx1 - 34, 14):
            if rng.random() < 0.7:
                c.ink(rect(xx, yy - 18, xx + 10, yy - 2), rng.choice(BOOK_COLS), lw=0, opacity=0.8)
    c.ink(rect(1180, 500, 1300, HOR), (200, 236, 230), lw=2.6, shade=0.15, opacity=0.95)
    c.stroke([(1240, 500), (1240, HOR)], 3, (120, 150, 150))
    for xx in (1226, 1254):
        c.ink(rrect(xx - 4, 590, xx + 4, 630, 3), (200, 200, 210), lw=1.6)
    c.ink(rect(1200, 540, 1236, 566), (250, 240, 120), lw=1.4)
    c.text(1218, 553, "OPEN", 7, (190, 30, 50), "Bold")
    c.glow2(1245, 590, 220, (200, 255, 230), 0.3)
    c.ink(rrect(qx0 + 20, 392, qx1 - 20, 452, 8), (40, 140, 90), lw=3.0, shade=0.3, hi=0.3)
    neon(c, (qx0 + qx1) / 2, 420, "QUICKMART", 30, (140, 255, 170))
    c.ink(rect(qx0 + 90, 456, qx1 - 90, 470), (250, 240, 214), lw=1.6)
    c.text((qx0 + qx1) / 2, 463, "WE HAVE EVERYTHING*", 8, (40, 90, 60), "Bold")
    # Bijou: tall art-deco facade with a vertical sign and marquee
    bx0, bx1 = 1400, 1780
    c.ink(rect(bx0, 150, bx1, HOR), (150, 40, 80), lw=3.2, shade=0.4, sw=60, hi=0.2, tex=0.18)
    for X in (bx0 + 20, bx1 - 40):
        c.ink(rect(X, 160, X + 20, HOR), (230, 180, 80), lw=2.4, shade=0.4, hi=0.4)
    c.ink(Sh([[(1560, 20), (1620, 20), (1630, 220), (1550, 220)]]), (40, 30, 60), lw=3.0, shade=0.3, hi=0.2)
    for k, ch in enumerate("BIJOU"):
        neon(c, 1590, 52 + k * 36, ch, 30, (255, 220, 90), glow=0.3)
    mq = Sh([[(1430, 250), (1750, 250), (1770, 300), (1760, 400), (1420, 400), (1410, 300)]])
    c.ink(mq, (250, 236, 200), lw=3.2, shade=0.3, hi=0.3)
    c.ink(rect(1450, 296, 1730, 380), (250, 250, 240), lw=2.2, shade=0.1)
    c.text(1590, 318, "MIDNIGHT CLASSICS", 21, (30, 30, 50))
    c.text(1590, 350, "OLD MOVIES  NEW POPCORN", 13, (180, 30, 60))
    c.text(1590, 372, "LOVE AMONG THE LIGHTHOUSES", 10, (60, 60, 110))
    for k in range(26):          # chaser bulbs, half of them out
        t = k / 25
        bx_, by_ = 1436 + t * 308, 262
        on = (k * 7) % 3 != 0
        c.ink(ell(bx_, by_, 5, 5), (255, 236, 150) if on else (120, 100, 90), lw=1.4, shade=0, hi=0.3)
        if on:
            c.glow2(bx_, by_, 16, GLOW, 0.5)
    c.ink(rect(1440, 400, 1740, 412), (60, 40, 60), lw=2.4)
    for (x0_, x1_) in ((1470, 1560), (1620, 1710)):
        c.ink(rect(x0_, 470, x1_, HOR), (110, 20, 50), lw=2.6, shade=0.3)
        c.ink(rect(x0_ + 12, 486, x1_ - 12, 560), (255, 200, 130), lw=1.8, opacity=0.8)
        c.stroke([((x0_ + x1_) / 2, 470), ((x0_ + x1_) / 2, HOR)], 3, (60, 10, 30))
    c.ink(rrect(1564, 520, 1616, 600, 6), (230, 180, 80), lw=2.4, shade=0.3)
    c.text(1590, 540, "TIX", 10, (90, 30, 30))
    c.ink(rect(1572, 552, 1608, 590), (255, 220, 160), lw=1.4, opacity=0.8)
    # Rusty Anchor: dark wood, porthole door, life ring, hanging sign
    ax0 = 1780
    clip_draw(c, rect(ax0, 260, W_BG + 10, HOR), lambda t: planks(t, (110, 66, 60), ax0, 260, W_BG + 10, HOR, pw=30, seed=46))
    c.ink(rect(ax0, 260, W_BG + 10, HOR), (0, 0, 0, 0), lw=3.2, line_only=True)
    flat_door(c, 1808, 450, 1900, HOR, (80, 50, 44), frame=(60, 36, 34), knob="L", seed=47)
    c.ink(ell(1854, 500, 22, 22), (220, 180, 90), lw=3.0, shade=0.4, hi=0.5)
    c.ink(ell(1854, 500, 15, 15), ("v", (255, 200, 120), (200, 120, 70)), lw=2.0)
    c.ink(ell(1810, 330, 30, 30), (250, 246, 240), lw=3.0, shade=0.4)
    c.ink(ell(1810, 330, 16, 16), (110, 66, 60), lw=2.4)
    for a in (45, 135, 225, 315):
        c.ink(Sh([rot_pts([(1786, 326), (1800, 326), (1800, 334), (1786, 334)], a, 1810, 330)]), (226, 60, 70), lw=1.2)
    c.stroke([(1860, 380), (1860, 404)], 2.4, INK)
    c.stroke([(1906, 380), (1906, 404)], 2.4, INK)
    c.ink(rrect(1838, 402, 1920, 440, 5), (60, 36, 34), lw=2.6, shade=0.3)
    c.text(1879, 414, "RUSTY", 10, (240, 200, 120))
    c.text(1879, 430, "ANCHOR", 9, (240, 200, 120))
    c.stroke([(1786, 380), (1950, 380)], 4, INK, taper=(0, 0))
    c.glow2(1854, 470, 90, GLOW, 0.4)
    # awnings / downpipes between the buildings, grime at the base
    for X in (650, 1090, 1400, 1780):
        pipe(c, [(X + 4, 320), (X + 4, HOR - 4)], w=12, col=(90, 80, 110), joints=False)
    c.soft(rect(200, HOR - 20, 1920, HOR + 6), (30, 10, 40), 0.3, 14)
    # ---------------- sidewalk props
    lamps = [lamppost(c, 222, 708, 300), lamppost(c, 1100, 708, 300)]
    string_lights2(c, [(lamps[0][0], lamps[0][1] + 28), (650, 330), (lamps[1][0], lamps[1][1] + 28)], sag=60, seed=4)
    fountain(c, 880, 758, 1.0, seed=48)
    parking_meter(c, 610, 760, 1.0)
    cafe_set(c, 1360, 762, 0.9)
    camera_rig(c, 1680, 760, 0.85)
    c.ink(Sh([[(1300, 770), (1440, 770), (1460, 790), (1290, 790)]]), (200, 40, 80, 0), lw=0) if False else None
    for (x_, y_, a) in ((340, 800, 20), (1500, 830, -30), (1020, 870, 10)):
        c.ink(Sh([rot_pts([(x_ - 16, y_ - 5), (x_ + 16, y_ - 5), (x_ + 16, y_ + 5), (x_ - 16, y_ + 5)], a, x_, y_)]),
              rng.choice([(250, 246, 230), (255, 230, 120), (160, 230, 255)]), lw=1.6, shade=0.2)
    # neon spill on the pavement
    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 220, 440, 0.4), (lamps[1][0], lamps[1][1] + 220, 440, 0.4),
                          (444, 520, 380, 0.35, (255, 120, 190)), (1245, 600, 360, 0.35, (150, 255, 210)),
                          (1590, 360, 420, 0.4, (255, 220, 140)), (880, 700, 260, 0.25, (90, 220, 255)), (1854, 500, 200, 0.3)],
               ambient=0.95, vign=0.5, top_dark=0.15, bottom_dark=0.45, shadow_tint=(80, 40, 130))
    for x_, y_ in lamps:
        c.glow2(x_, y_, 140, GLOW, 0.5)
    c.glow2(444, 290, 260, (255, 90, 170), 0.2)
    c.glow2(1360, 690, 80, GLOW, 0.4)
    c.painterly(0.05)

    def fg(sub):
        fg_hydrant(sub, 40, 1090, 0.9)
        fg_trash_can(sub, 1890, 1100, 0.9)
        fg_plant(sub, 1700, 1110, 160, seed=61, flip=True)
        fg_cable(sub, [(300, 1110), (700, 1068), (1100, 1100)], 14)
        sub.ink(rect(820, 1040, 1080, 1100), FG, lw=0)    # bench seat edge in the gutter
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_downtown.png")


_G_DT = geo((-400, 100, 2320, 700))
LAYOUT["downtown"] = dict(
        walk_px=[(30, Y_TOP), (1890, Y_TOP), (1900, 900), (1850, Y_BOT), (70, Y_BOT), (20, 900)],
        hotspots={
            ("Bus stop", 0): dict(box=(20, 420, 230, 712), stand=(200, 820)),
            ("Starlite Diner", 0): dict(box=(250, 250, 640, 702), stand=(444, 800)),
            ("Bree Marlowe", 0): dict(npc="hs_bree_marlowe", feet=(660, 945), stand=(860, 935)),
            ("Fountain", 0): dict(box=(720, 552, 1040, 762), stand=(880, 805)),
            ("Quickmart", 0): dict(box=(1150, 400, 1330, 702), stand=(1240, 800)),
            ("Bijou Theatre", 0): dict(box=(1410, 240, 1770, 412), stand=(1590, 800)),
            ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1500, 945), stand=(1320, 935)),
            ("Rusty Anchor", 0): dict(box=(1790, 300, 1915, 702), stand=(1790, 830)),
        },
        entries={"from_campus": (200, 880), "from_quickmart": (1240, 830), "from_anchor": (1770, 880),
                 "from_diner": (444, 830), "from_bijou": (1600, 840)})


# =========================================================================== 2. Quickmart
def snack_shelf(c, R, X0, X1, Z0, Z1, H, rng, wood=(70, 150, 150), rows=4, label=None, label_col=(240, 80, 140)):
    """Free-standing / wall shelf unit in room space packed with snacks; returns its front quad."""
    f = R.ink_box(X0, X1, 0, H, Z0, Z1, shade_col(wood, 0.6), side=shade_col(wood, 0.5), seed=int(X0))
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    c.ink(Sh([fr]), shade_col(wood, 0.45), lw=2.6, shade=0.2)
    rh = (y1 - y0) / rows
    for k in range(rows):
        yb = y0 + rh * (k + 1)
        xx = x0 + 6
        while xx < x1 - 14:
            w = rng.uniform(12, 24)
            h = rh * rng.uniform(0.45, 0.8)
            col = rng.choice(BOOK_COLS + [(255, 230, 90), (90, 220, 120), (250, 120, 200)])
            if rng.random() < 0.35:
                c.ink(ell(xx + w / 2, yb - h * 0.45, w * 0.55, h * 0.45), col, lw=1.6, shade=0.4, hi=0.4)
            else:
                c.ink(rrect(xx, yb - h, xx + w, yb - 2, 3), col, lw=1.6, shade=0.4, sw=4, hi=0.35, hw=2, ao=0)
                c.stroke([(xx + 3, yb - h * 0.6), (xx + w - 3, yb - h * 0.6)], 1.4, hi_col(col, 0.6), taper=(0, 0), opacity=0.8)
            xx += w + rng.uniform(1, 4)
        c.ink(rect(x0 - 2, yb - 4, x1 + 2, yb + 4), wood, lw=2.0, shade=0.3, hi=0.4)
        c.ink(rect(x0 + 10 + k * 30 % (x1 - x0 - 60), yb - 2, x0 + 44 + k * 30 % (x1 - x0 - 60), yb + 6), (255, 240, 140), lw=1.0)
    if label:
        lx, ly = (x0 + x1) / 2, y0 - 24
        c.ink(rrect(lx - len(label) * 6 - 14, ly - 15, lx + len(label) * 6 + 14, ly + 15, 6), label_col, lw=2.6, shade=0.3, hi=0.3)
        c.text(lx, ly, label, 13, (255, 255, 240))
    return fr


def paint_quickmart():
    c, R, rng = std_room(4200, back=STD_BACK)
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (200, 80, 160)
    LOW = (40, 150, 150)

    def ceil(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (150, 140, 170), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 90 * sub.density
        for x in np.arange(0, sub.w, step):
            sub.stroke([(x, 0), (x, sub.h)], 2.6, (110, 100, 130), taper=(0, 0))
        for y in np.arange(0, sub.h, step * 0.8):
            sub.stroke([(0, y), (sub.w, y)], 2.6, (110, 100, 130), taper=(0, 0))
        for _ in range(10):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (120, 80, 40), 0.25, 0, rng.randint(0, 99))

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (150, 50, 130), 0.25), LOW, 4201)
        x0, y0, x1, y1 = left_exit_door(sub, "EXIT", door=(60, 170, 170), seed=4202)
        # door chime
        sub.ink(ell((x0 + x1) / 2 + 40, y0 + 16, 10, 7), (250, 210, 80), lw=1.8, shade=0.3, hi=0.5)
        poster(sub, sub.ax(420), sub.by(300), 120, 150, (60, 140, 230),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.17, "BRAIN", 15, (255, 255, 255)),
                                  p.text(w_ / 2, h_ * 0.33, "FREEZE", 15, (255, 255, 255)),
                                  p.ink(Sh([[(w_ * 0.3, h_ * 0.45), (w_ * 0.7, h_ * 0.45), (w_ * 0.62, h_ * 0.85), (w_ * 0.38, h_ * 0.85)]]),
                                        (220, 240, 255), lw=1.6),
                                  p.ink(ell(w_ * 0.5, h_ * 0.45, w_ * 0.22, h_ * 0.06), (90, 160, 255), lw=1.4),
                                  p.text(w_ / 2, h_ * 0.94, "GUARANTEED", 8, (255, 236, 120), "Bold")),
               angle=-5, seed=4203, peel="br")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 4204)
        # ice chest (glass-front freezer) against the right wall
        x0, x1 = sub.ax(40), sub.ax(300)
        y0, y1 = sub.by(260), sub.by(0)
        sub.ink(rect(x0, y0, x1, y1), (220, 230, 240), lw=3.0, shade=0.4, hi=0.3)
        sub.ink(rect(x0 + 16, y0 + 40, x1 - 16, y1 - 40), ("v", (190, 230, 255), (120, 180, 230)), lw=2.4, shade=0.2)
        for k in range(3):
            yy = y0 + 60 + k * ((y1 - y0 - 120) / 3)
            sub.ink(rect(x0 + 26, yy, x1 - 26, yy + 50), (240, 250, 255), lw=1.6, shade=0.3)
            sub.text((x0 + x1) / 2, yy + 25, "ICE", 18, (60, 120, 200))
        sub.stroke([(x0 + 30, y1 - 50), (x0 + 120, y0 + 50)], 10, (255, 255, 255), opacity=0.25)
        sub.ink(rect(x0 + 10, y0 + 8, x1 - 10, y0 + 32), (60, 150, 220), lw=2, shade=0.2)
        sub.text((x0 + x1) / 2, y0 + 20, "ICE COLD (MOSTLY)", 11, (255, 255, 255))

    def floor(sub):
        tiles(sub, (70, 170, 170), (236, 226, 200), 0, 0, sub.w, sub.h, size=64 * sub.density, seed=4205, chipped=0.1)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=4200)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 4206, chips=5, stains=4)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=4206)
    R.ao(0.5)
    R.edges(w=4.0)

    # flower bucket (hotspot "Flower bucket"), on the floor by the door
    R.contact(40, 140, 50, 120, 0.5)
    f = R.ink_box(50, 130, 0, 70, 60, 110, (60, 70, 90), seed=4207)
    tx_, ty_ = P(90, 70, 85)
    for k in range(9):
        a = math.radians(-138 + k * 12 + rng.uniform(-4, 4))
        L = rng.uniform(60, 92) * (1.0 - 0.25 * abs(k - 4) / 4)
        base = (tx_ + (k - 4) * 4, ty_)
        tip = (base[0] + math.cos(a) * L, base[1] + math.sin(a) * L)
        c.stroke([base, ((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2 + 4), tip], 3, (50, 120, 60))
        c.ink(ell((base[0] + tip[0]) / 2 + 6, (base[1] + tip[1]) / 2, 8, 3.5, 30), (60, 140, 70), lw=1.2) if k % 2 else None
        c.ink(ell(tip[0], tip[1], 11, 10), (200, 40, 70) if k % 3 else (160, 30, 70), lw=2.2, shade=0.45, hi=0.3)
        c.stroke([(tip[0] - 5, tip[1] - 1), (tip[0], tip[1] - 5), (tip[0] + 5, tip[1])], 1.4, (120, 20, 50), opacity=0.8)
        c.ink(ell(tip[0] + 3, tip[1] + 8, 5, 3), (60, 130, 60), lw=0) if k % 3 == 0 else None
    fr = f["front"]
    cx_ = (fr[0][0] + fr[1][0]) / 2
    cy_ = (fr[0][1] + fr[2][1]) / 2
    c.ink(Sh([rot_pts([(cx_ - 30, cy_ - 16), (cx_ + 30, cy_ - 16), (cx_ + 30, cy_ + 16), (cx_ - 30, cy_ + 16)], -6, cx_, cy_)]),
          (255, 250, 220), lw=1.8, shade=0.2)
    c.text(cx_, cy_ - 5, "$5", 11, (200, 30, 50), angle=6)
    c.text(cx_, cy_ + 8, "NO REFUNDS", 6, (60, 60, 90), "Bold", angle=6)
    # slushie machine on a cabinet (hotspot "Slushie machine")
    R.contact(170, 340, 0, 70, 0.5)
    R.ink_box(170, 340, 0, 100, 0, 70, (60, 140, 150), seed=4208)
    f = R.ink_box(185, 325, 100, 160, 8, 62, (200, 200, 214), seed=4209)
    flav = [((70, 140, 255), "BLUE"), ((240, 40, 70), "RED"), ((130, 80, 40), "BROWN")]
    for k, (col, nm) in enumerate(flav):
        X = 195 + k * 44
        fq = R.box(X, X + 38, 160, 250, 14, 56)
        bowl = blob(fq["front"], 3)
        c.ink(bowl, (230, 240, 250), lw=2.6, shade=0.3, hi=0.5)
        x0_, y0_ = fq["front"][0]
        x1_, _ = fq["front"][1]
        _, y1_ = fq["front"][2]
        liq = Sh([[(x0_ + 3, y0_ + (y1_ - y0_) * 0.3), (x1_ - 3, y0_ + (y1_ - y0_) * 0.34), (x1_ - 3, y1_ - 3), (x0_ + 3, y1_ - 3)]])
        c.ink(liq, col, lw=0, shade=0.4, hi=0.3, clip=bowl)
        c.stroke([(x0_ + 8, y1_ - 10), (x0_ + 10, y0_ + 14)], 4, (255, 255, 255), opacity=0.5)
        lx, ly = P(X + 19, 130, 62)
        c.ink(rect(lx - 18, ly - 8, lx + 18, ly + 8), (250, 250, 240), lw=1.4)
        c.text(lx, ly, nm, 7 if nm != "BROWN" else 6, dk(col, 0.6), "Black")
    lx, ly = P(255, 270, 40)
    c.ink(rrect(lx - 80, ly - 18, lx + 80, ly + 14, 6), (40, 30, 70), lw=2.6, shade=0.2)
    neon(c, lx, ly - 2, "SLUSH-O-MATIC", 13, (120, 220, 255), glow=0.35)
    lx, ly = P(301, 115, 72)
    c.ink(Sh([rot_pts([(lx - 26, ly - 10), (lx + 26, ly - 10), (lx + 26, ly + 10), (lx - 26, ly + 10)], 5, lx, ly)]), (255, 236, 120), lw=1.4)
    c.text(lx, ly, "(DON'T)", 7, (130, 60, 30), "Bold", angle=-5)
    # snack shelves on the back wall
    snack_shelf(c, R, 380, 640, 0, 46, 270, rng, label="SNACKS & REGRETS")
    snack_shelf(c, R, 1000, 1240, 0, 46, 270, rng, label="BATTERIES · GUM · SOCKS", label_col=(60, 120, 220))
    # employee of the month frame
    ex_, ey_ = P(700, 300)
    c.ink(rect(ex_ - 40, ey_ - 50, ex_ + 40, ey_ + 44), (230, 190, 80), lw=2.6, shade=0.4, hi=0.4)
    c.ink(rect(ex_ - 30, ey_ - 40, ex_ + 30, ey_ + 20), (250, 240, 220), lw=1.6)
    c.ink(ell(ex_, ey_ - 14, 14, 16), (126, 80, 58), lw=1.6)
    c.ink(Sh([[(ex_ - 16, ey_ - 22), (ex_ + 16, ey_ - 24), (ex_ + 12, ey_ - 36), (ex_ - 12, ey_ - 36)]]), (240, 130, 40), lw=1.4)
    c.stroke([(ex_ - 6, ey_ - 6), (ex_ + 6, ey_ - 6)], 1.6, INK)
    c.ink(rect(ex_ - 24, ey_ + 2, ex_ + 24, ey_ + 20), (46, 160, 110), lw=1.2)
    c.text(ex_, ey_ + 32, "EMPLOYEE OF", 6, (90, 50, 30), "Bold")
    c.text(ex_, ey_ + 40, "EVERY MONTH", 6, (90, 50, 30), "Bold")
    # convex security mirror in the corner
    mx_, my_ = P(Wb - 30, 380)
    c.ink(ell(mx_, my_, 44, 40), (200, 210, 230), lw=3.0, shade=0.4, hi=0.6)
    c.ink(ell(mx_, my_, 36, 32), ("r", (230, 236, 250), (120, 140, 180)) if False else (150, 170, 210), lw=1.6, shade=0.5, hi=0.6, hw=8)
    # counter (hotspot "Counter") with till, bell, gum rack, newspaper
    R.contact(660, 960, 40, 150, 0.55)
    R.ink_box(660, 960, 0, 104, 40, 150, (60, 160, 150), top=(240, 236, 220), seed=4210)
    f = R.box(660, 960, 0, 104, 40, 150)
    fr = f["front"]
    c.ink(Sh([[fr[3], fr[2], (fr[2][0], fr[2][1] - 30), (fr[3][0], fr[3][1] - 30)]]), (240, 90, 140), lw=2.0, shade=0.3)
    for k in range(3):
        sx_ = fr[3][0] + 30 + k * 100
        poster(c, sx_ + 30, (fr[0][1] + fr[3][1]) / 2 - 10, 60, 40, rng.choice([(255, 236, 120), (160, 230, 255), (255, 170, 200)]),
               lambda p, w_, h_, k=k: p.text(w_ / 2, h_ / 2, ("LOTTO", "NO CHANGE", "CASH ONLY")[k], 8, (60, 40, 60), "Bold"),
               angle=rng.uniform(-6, 6), seed=4211 + k)
    tx_, ty_ = P(880, 104, 80)
    c.ink(Sh([[(tx_ - 40, ty_), (tx_ + 40, ty_), (tx_ + 30, ty_ - 40), (tx_ - 30, ty_ - 40)]]), (80, 80, 96), lw=2.6, shade=0.4, hi=0.3)
    c.ink(rect(tx_ - 22, ty_ - 70, tx_ + 22, ty_ - 40), (60, 60, 76), lw=2.4, shade=0.3)
    c.ink(rect(tx_ - 16, ty_ - 66, tx_ + 16, ty_ - 48), (120, 255, 170), lw=1.4)
    c.text(tx_, ty_ - 57, "0.00", 8, (20, 80, 40), "Bold")
    bx_, by_ = P(760, 104, 110)
    c.ink(ell(bx_, by_ - 4, 18, 5), (180, 150, 70), lw=2)
    c.ink(Sh([chaikin([(bx_ - 14, by_ - 4), (bx_ - 12, by_ - 20), (bx_, by_ - 26), (bx_ + 12, by_ - 20), (bx_ + 14, by_ - 4)], 1, False)]),
          (240, 200, 80), lw=2.2, shade=0.4, hi=0.6)
    np_ = [P(690, 105, 90), P(750, 105, 85), P(756, 105, 130), P(694, 105, 136)]
    c.ink(Sh([np_]), (236, 232, 214), lw=2.0, shade=0.2)
    for k in range(4):
        c.stroke([(np_[0][0] + 6, np_[0][1] + 3 + k * 5), (np_[1][0] - 6, np_[1][1] + 3 + k * 5)], 1.2, (120, 120, 130), opacity=0.7)
    gx_, gy_ = P(820, 104, 120)
    c.ink(rect(gx_ - 30, gy_ - 44, gx_ + 30, gy_), (240, 80, 140), lw=2.2, shade=0.3)
    for k in range(3):
        for j in range(4):
            c.ink(rect(gx_ - 26 + j * 13, gy_ - 40 + k * 13, gx_ - 16 + j * 13, gy_ - 30 + k * 13), BOOK_COLS[(j + k) % 8], lw=1)
    # 1-Hour Photo kiosk (hotspot "1-Hour Photo")
    R.contact(1080, 1220, 20, 100, 0.55)
    f = R.ink_box(1080, 1220, 0, 240, 20, 100, (250, 200, 50), seed=4212)
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    c.ink(rrect(x0 + 10, y0 + 10, x1 - 10, y0 + 44, 5), (40, 40, 70), lw=2.2)
    neon(c, (x0 + x1) / 2, y0 + 27, "1-HOUR PHOTO", 12, (255, 236, 120), glow=0.3)
    c.ink(rect(x0 + 24, y0 + 60, x1 - 24, y0 + 150), (30, 50, 70), lw=2.4, shade=0.2)
    c.ink(rect(x0 + 32, y0 + 68, x1 - 32, y0 + 142), (110, 200, 255), lw=1.6, shade=0.3, hi=0.3)
    c.text((x0 + x1) / 2, y0 + 104, "INSERT FILM", 9, (20, 60, 90), "Bold")
    c.ink(rect(x0 + 40, y0 + 170, x1 - 40, y0 + 182), (30, 30, 40), lw=2.0)
    c.ink(Sh([rot_pts([(x0 + 30, y0 + 196), (x1 - 30, y0 + 196), (x1 - 30, y0 + 236), (x0 + 30, y0 + 236)], 4, x0, y0)]), (255, 250, 230), lw=1.6,
          shade=0.2)
    c.text((x0 + x1) / 2, y0 + 210, "1 HR. OR 1 MIN", 6, (190, 30, 50), "Bold", angle=-4)
    c.text((x0 + x1) / 2, y0 + 224, "IF LOU LIKES YOU", 6, (190, 30, 50), "Bold", angle=-4)
    c.glow2((x0 + x1) / 2, y0 + 104, 120, (110, 200, 255), 0.3)
    # ceiling: fluorescent panels (one flickering), a hanging "OPEN 24/7" sign, cables
    lamps = []
    for X0 in (150, 560, 960):
        panel_light(c, R, X0, X0 + 200, 110, 200, cone=0.22, flicker=(X0 == 560))
        lamps.append(R.pt(X0 + 100, Hb - 14, 155))
    hanging_cable(c, P(820, Hb, 260), 120, sway=14, w=5, col=(40, 120, 130), seed=3)
    cobweb(c, *P(0, Hb, 0), 100, "tl")
    cobweb(c, *P(Wb, Hb, 0), 90, "tr")
    stain(c, *P(860, 400), 50, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(lamps[0][0], 620, 520, 0.4, (230, 255, 240)), (lamps[1][0], 620, 460, 0.2, (230, 255, 240)),
                          (lamps[2][0], 620, 520, 0.4, (230, 255, 240)), (P(1150, 160, 60)[0], 560, 260, 0.3, (110, 200, 255)),
                          (P(255, 200, 40)[0], 520, 240, 0.3, (150, 200, 255))],
               ambient=0.94, vign=0.58, top_dark=0.4, bottom_dark=0.35)
    for k, (x, y) in enumerate(lamps):
        c.glow2(x, y, 260, (240, 255, 240), 0.5 if k != 1 else 0.2, sy=0.4)
    c.painterly(0.05)

    def fg(sub):
        fg_table_edge(sub, 1540, 2000, 1000, 120)
        fg_bottles(sub, 1600, 1010, 4, 0.75, seed=72)
        fg_plant(sub, 60, 1100, 280, seed=71)
        fg_cable(sub, [(300, 1100), (700, 1070), (1200, 1095)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_quickmart.png")


_G = geo()
LAYOUT["quickmart"] = dict(
        walk_px=STD_WALK,
        hotspots={
            ("Exit", 0): dict(box=EXIT_BOX(_G), stand=(250, 850)),
            ("Flower bucket", 0): dict(box=box3(_G, 30, 150, 0, 170, 50, 120), stand=(400, 800)),
            ("Slushie machine", 0): dict(box=box3(_G, 170, 340, 0, 285, 0, 70), stand=(600, 790)),
            ("Counter", 0): dict(box=box3(_G, 660, 960, 0, 150, 40, 150), stand=(1170, 800)),
            ("Lou", 0): dict(npc="hs_lou", feet=(1290, 945), stand=(1100, 935)),
            ("1-Hour Photo", 0): dict(box=box3(_G, 1080, 1220, 0, 240, 20, 100), stand=(1520, 800)),
        },
        entries={"from_downtown": (290, 880)})


# =========================================================================== 3. Rusty Anchor (sailors' bar)
def barrel(c, R, X, Z, rad, H, col=(150, 90, 56), hoop=(90, 90, 104)):
    """Upright wooden barrel standing on the floor at (X, Z); returns the top ellipse centre (px)."""
    bx, by = R.pt(X, 0, Z)
    tx, ty = R.pt(X, H, Z)
    k = R.k(Z)
    w = rad * k
    ry = w * 0.22
    c.soft(ell(bx, by, w * 1.2, ry * 1.2), (24, 6, 34), 0.5, 6)
    body = blob([(bx - w, by - ry * 0.2), (bx - w * 1.1, (by + ty) / 2), (tx - w, ty), (tx + w, ty), (bx + w * 1.1, (by + ty) / 2),
                 (bx + w, by - ry * 0.2), (bx, by + ry * 0.8)], 2)
    c.ink(body, col, lw=3.0, shade=0.55, sw=w * 0.5, hi=0.35, rim=0.2, tex=0.2)
    for f in (-0.5, 0.0, 0.5):
        c.stroke([(bx + w * f * 1.0, by + ry * 0.5), (tx + w * f * 1.1, ty + 4)], 1.6, shade_col(col, 0.55), opacity=0.7)
    for t in (0.14, 0.86):
        yy = by + (ty - by) * t
        ww = w * (1.0 + 0.1 * math.sin(t * math.pi))
        c.stroke(bez((bx - ww, yy), (bx, yy + ry * 1.6), (bx + ww, yy), 16), 5, hoop, taper=(0, 0))
    c.ink(ell(tx, ty, w, ry), hi_col(col, 0.15), lw=2.6, shade=0.3, hi=0.2)
    c.ink(ell(tx, ty, w * 0.8, ry * 0.75), shade_col(col, 0.6), lw=1.6, shade=0, hi=0)
    return tx, ty


def jukebox(c, R, X0, X1, Z0, Z1, H=280, seed=0):
    rng = random.Random(seed)
    R.contact(X0, X1, Z0, Z1, 0.55)
    f = R.ink_box(X0, X1, 0, H * 0.72, Z0, Z1, (180, 50, 90), seed=seed)
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    w = x1 - x0
    arch = Sh([chaikin([(x0, y0 + 2), (x0, y0 - w * 0.3), (x0 + w * 0.14, y0 - w * 0.62), (x0 + w * 0.5, y0 - w * 0.78), (x1 - w * 0.14, y0 - w * 0.62),
                        (x1, y0 - w * 0.3), (x1, y0 + 2)], 2, False)])
    c.ink(arch, (220, 70, 110), lw=3.0, shade=0.5, sw=w * 0.15, hi=0.5, hw=6, rim=0.2)
    inner = Sh([chaikin([(x0 + w * 0.14, y0 + 2), (x0 + w * 0.14, y0 - w * 0.28), (x0 + w * 0.5, y0 - w * 0.56), (x1 - w * 0.14, y0 - w * 0.28),
                         (x1 - w * 0.14, y0 + 2)], 2, False)])
    c.ink(inner, ("v", (255, 230, 120), (255, 120, 60)), lw=2.4, shade=0.1, hi=0.3)
    for k, col in enumerate(((90, 220, 255), (255, 90, 170), (140, 255, 140))):   # bubble tubes
        xx = x0 + w * (0.07 if k == 0 else 0.93 if k == 1 else 0.5)
        if k == 2:
            continue
        c.ink(rrect(xx - 6, y0 - w * 0.25, xx + 6, y1 - 20, 6), col, lw=2.2, shade=0.3, hi=0.6, hw=2)
        for j in range(6):
            yy = rng.uniform(y0 - w * 0.2, y1 - 30)
            c.ink(ell(xx + rng.uniform(-2, 2), yy, 2.6, 2.6), (255, 255, 255), lw=0.8, opacity=0.8)
        c.glow2(xx, (y0 + y1) / 2, 80, col, 0.35)
    c.ink(rect(x0 + w * 0.2, y0 + 16, x1 - w * 0.2, y0 + 60), (250, 246, 230), lw=2.0, shade=0.2)
    for k in range(3):
        c.stroke([(x0 + w * 0.26, y0 + 26 + k * 12), (x1 - w * 0.26, y0 + 26 + k * 12)], 1.4, (140, 60, 90), opacity=0.8)
    c.ink(rect(x0 + w * 0.2, y0 + 74, x1 - w * 0.2, y1 - 30), (60, 30, 50), lw=2.2, shade=0.2)
    for k in range(5):
        c.stroke([(x0 + w * 0.24, y0 + 84 + k * 10), (x1 - w * 0.24, y0 + 84 + k * 10)], 2.2, (200, 160, 100), opacity=0.7)
    c.ink(rrect((x0 + x1) / 2 - 22, y1 - 26, (x0 + x1) / 2 + 22, y1 - 12, 3), (230, 200, 80), lw=1.6)
    c.text((x0 + x1) / 2, y1 - 19, "25¢", 7, (90, 40, 30), "Bold")
    c.glow2((x0 + x1) / 2, y0 - w * 0.2, w * 1.4, (255, 170, 80), 0.45)
    return ((x0 + x1) / 2, y0)


def ships_wheel(c, x, y, r, col=(150, 90, 50)):
    for k in range(8):
        a = math.radians(k * 45 + 10)
        c.stroke([(x, y), (x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3)], 7, INK, taper=(0, 0))
        c.stroke([(x, y), (x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3)], 4, col, taper=(0, 0))
        c.ink(ell(x + math.cos(a) * r * 1.32, y + math.sin(a) * r * 1.32, 6, 6), col, lw=2.0, shade=0.3)
    c.ink(ell(x, y, r, r), (0, 0, 0, 0), lw=9, oc=INK, line_only=True)
    c.ink(ell(x, y, r, r), (0, 0, 0, 0), lw=5, oc=col, line_only=True, inner=0.5)
    c.ink(ell(x, y, r * 0.22, r * 0.22), col, lw=2.4, shade=0.4, hi=0.4)


def porthole(c, x, y, r, seed=0):
    c.ink(ell(x, y, r + 10, r + 10), (220, 170, 80), lw=3.0, shade=0.45, hi=0.5, hw=4)
    clip = ell(x, y, r, r)
    c.ink(clip, ("v", (40, 30, 90), (60, 120, 170)), lw=2.4, shade=0.1)
    c.ink(rect(x - r, y + r * 0.2, x + r, y + r), (40, 80, 140), lw=0, clip=clip)
    for k in range(3):
        c.stroke([(x - r, y + r * (0.3 + k * 0.2)), (x - r * 0.3, y + r * (0.24 + k * 0.2)), (x + r, y + r * (0.32 + k * 0.2))], 1.4,
                 (150, 200, 255), opacity=0.5)
    c.ink(ell(x + r * 0.35, y - r * 0.35, r * 0.18, r * 0.18), (255, 246, 214), lw=0, clip=clip)
    c.stroke([(x - r * 0.6, y + r * 0.4), (x - r * 0.1, y - r * 0.6)], 5, (255, 255, 255), opacity=0.25)
    for k in range(6):
        a = math.radians(k * 60)
        c.ink(ell(x + math.cos(a) * (r + 5), y + math.sin(a) * (r + 5), 2.4, 2.4), (140, 100, 40), lw=0.8)
    c.glow2(x, y, r * 2.2, (120, 170, 255), 0.25)


def lantern(c, x, y_ceil, y, s=1.0):
    c.stroke([(x, y_ceil), (x, y - 26 * s)], 3, INK, taper=(0, 0))
    c.ink(Sh([[(x - 14 * s, y - 26 * s), (x + 14 * s, y - 26 * s), (x + 20 * s, y - 16 * s), (x - 20 * s, y - 16 * s)]]), (50, 40, 50), lw=2.2)
    c.ink(rrect(x - 17 * s, y - 16 * s, x + 17 * s, y + 24 * s, 5), (255, 220, 120), lw=2.6, shade=0.2, hi=0.3)
    for dx in (-17, 0, 17):
        c.stroke([(x + dx * s, y - 16 * s), (x + dx * s, y + 24 * s)], 2.6, (50, 40, 50), taper=(0, 0))
    c.ink(rect(x - 20 * s, y + 24 * s, x + 20 * s, y + 32 * s), (50, 40, 50), lw=2.0)
    c.glow2(x, y + 4 * s, 120 * s, GLOW, 0.55)
    c.glow2(x, y + 4 * s, 30 * s, (255, 250, 220), 0.7)


def paint_rusty_anchor():
    c, R, rng = std_room(4300, back=STD_BACK, light=(0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 56, 130)
    WOOD = (120, 70, 66)

    def ceil(sub):
        planks(sub, (90, 56, 70), 0, 0, sub.w, sub.h, pw=50 * sub.density, seed=4301, vertical=False)
        sub.ink(rect(0, 0, sub.w, sub.h), (30, 10, 40), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=0.25)

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (110, 40, 110), 0.25), WOOD, 4302, low_kind="wood", split=0.62)
        left_exit_door(sub, "DRY LAND", door=(110, 64, 50), glass=False, seed=4303)
        x0, x1 = sub.ax(280), sub.ax(100)
        porthole(sub, (x0 + x1) / 2, sub.by(240), 26)
        # anchor + oar on the wall
        ax_, ay_ = sub.ax(420), sub.by(300)
        sub.stroke([(ax_, ay_ - 70), (ax_, ay_ + 60)], 12, (90, 96, 110), taper=(0, 0))
        sub.ink(ell(ax_, ay_ - 82, 14, 14), (0, 0, 0, 0), lw=7, oc=(90, 96, 110), line_only=True)
        sub.stroke([(ax_ - 40, ay_ - 40), (ax_ + 40, ay_ - 40)], 10, (90, 96, 110), taper=(0.1, 0.1))
        sub.stroke(bez((ax_ - 70, ay_ + 10), (ax_, ay_ + 110), (ax_ + 70, ay_ + 10), 20), 12, (90, 96, 110), taper=(0.3, 0.3))

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.03), WOOD, 4304, low_kind="wood", split=0.62)
        porthole(sub, sub.ax(160), sub.by(300), 54, seed=2)
        # fishing net with floats + starfish
        nx0, nx1, ny0, ny1 = sub.ax(40), sub.ax(380), sub.by(470), sub.by(360)
        for k in range(12):
            t = k / 11
            sub.stroke([(nx0 + (nx1 - nx0) * t, ny0), (nx0 + (nx1 - nx0) * t + 30, ny1 + 60 * math.sin(t * math.pi))], 1.4, (230, 220, 190), opacity=0.7)
            sub.stroke([(nx0 + (nx1 - nx0) * t + 30, ny0), (nx0 + (nx1 - nx0) * t, ny1 + 60 * math.sin(t * math.pi))], 1.4, (230, 220, 190), opacity=0.7)
        for k in range(4):
            sub.ink(ell(nx0 + 40 + k * (nx1 - nx0 - 80) / 3, ny1 + 40 * math.sin((k + 0.5) / 4 * math.pi), 14, 14),
                    ((220, 60, 70), (250, 220, 90), (60, 200, 196), (250, 250, 240))[k], lw=2.4, shade=0.4, hi=0.5)

    def floor(sub):
        planks(sub, (130, 76, 64), 0, 0, sub.w, sub.h, pw=44 * sub.density, seed=4305, vertical=True)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=4300)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, WOOD, 4306, chips=6, stains=5, low_kind="wood", split=0.62)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=4306)
    R.ao(0.55)
    R.edges(w=4.0)

    # wall decor
    ships_wheel(c, *P(470, 330), 54)
    ring_x, ring_y = P(640, 340)
    c.ink(ell(ring_x, ring_y, 44, 44), (250, 246, 240), lw=3.0, shade=0.45, hi=0.3)
    c.ink(ell(ring_x, ring_y, 24, 24), WALL, lw=2.6)
    for a in (45, 135, 225, 315):
        c.ink(Sh([rot_pts([(ring_x - 46, ring_y - 6), (ring_x - 24, ring_y - 6), (ring_x - 24, ring_y + 6), (ring_x - 46, ring_y + 6)], a, ring_x, ring_y)]),
              (226, 60, 70), lw=1.6)
    c.text(ring_x, ring_y + 66, "S.S. SOGGY BISCUIT", 9, (250, 230, 180), "Bold")
    # mounted fish
    fx_, fy_ = P(1210, 400)
    c.ink(Sh([[(fx_ - 50, fy_ - 30), (fx_ + 50, fy_ - 30), (fx_ + 50, fy_ + 30), (fx_ - 50, fy_ + 30)]]), (130, 80, 50), lw=2.6, shade=0.3)
    c.ink(blob([(fx_ - 40, fy_), (fx_ - 10, fy_ - 16), (fx_ + 22, fy_ - 10), (fx_ + 30, fy_), (fx_ + 22, fy_ + 10), (fx_ - 10, fy_ + 14)], 2),
          (90, 170, 150), lw=2.4, shade=0.4, hi=0.5)
    c.ink(Sh([[(fx_ + 28, fy_), (fx_ + 46, fy_ - 16), (fx_ + 46, fy_ + 16)]]), (90, 170, 150), lw=2.2)
    c.ink(ell(fx_ - 28, fy_ - 4, 3, 3), INK, lw=0)
    # bottle shelves + sign behind the bar
    for k, Y in enumerate((270, 190)):
        sx0, sy0 = P(760, Y)
        sx1, _ = P(1200, Y)
        shelf(c, sx0, sx1, sy0, 18, (110, 64, 50))
        xx = sx0 + 14
        while xx < sx1 - 20:
            h = rng.uniform(40, 66)
            w = rng.uniform(14, 20)
            col = rng.choice([(60, 150, 90), (150, 70, 40), (230, 200, 120), (90, 60, 140), (200, 60, 70), (60, 120, 180)])
            c.ink(Sh([[(xx, sy0), (xx, sy0 - h * 0.62), (xx + w * 0.3, sy0 - h * 0.78), (xx + w * 0.3, sy0 - h), (xx + w * 0.7, sy0 - h),
                       (xx + w * 0.7, sy0 - h * 0.78), (xx + w, sy0 - h * 0.62), (xx + w, sy0)]]), col, lw=1.8, shade=0.4, hi=0.6, hw=3)
            if rng.random() < 0.5:
                c.ink(rect(xx + 2, sy0 - h * 0.45, xx + w - 2, sy0 - h * 0.2), (250, 240, 214), lw=0.8)
            xx += w + rng.uniform(3, 8)
    sgx, sgy = P(980, 372)
    c.ink(rrect(sgx - 120, sgy - 26, sgx + 120, sgy + 26, 6), (250, 236, 200), lw=2.8, shade=0.3, hi=0.3)
    c.text(sgx, sgy - 9, "SELF-SERVE", 16, (140, 40, 40))
    c.text(sgx, sgy + 12, "PAY THE PARROT", 11, (40, 80, 70))
    c.stroke([(sgx - 100, sgy - 26), (sgx - 90, P(980, Hb)[1])], 2, (200, 180, 140))
    c.stroke([(sgx + 100, sgy - 26), (sgx + 90, P(980, Hb)[1])], 2, (200, 180, 140))
    # jukebox (hotspot "Jukebox")
    jtop = jukebox(c, R, 210, 350, 4, 60, H=280, seed=4307)
    # junk barrel (hotspot "Junk barrel") with a net on a pole, a boot, rope
    tx_, ty_ = barrel(c, R, 80, 120, 48, 110)
    c.stroke([(tx_ + 10, ty_), (tx_ + 46, ty_ - 170)], 6, INK, taper=(0, 0))
    c.stroke([(tx_ + 10, ty_), (tx_ + 46, ty_ - 170)], 3, (200, 170, 110), taper=(0, 0))
    net = ell(tx_ + 52, ty_ - 190, 22, 26, 15)
    c.ink(net, (0, 0, 0, 0), lw=3.6, oc=(200, 170, 110), line_only=True)
    clip_draw(c, net, lambda t: [t.stroke([(tx_ + 20 + k * 8, ty_ - 230), (tx_ + 40 + k * 8, ty_ - 150)], 1.0, (240, 230, 200)) for k in range(8)] +
              [t.stroke([(tx_ + 20, ty_ - 220 + k * 8), (tx_ + 90, ty_ - 216 + k * 8)], 1.0, (240, 230, 200)) for k in range(10)])
    c.ink(blob([(tx_ - 30, ty_ + 4), (tx_ - 34, ty_ - 40), (tx_ - 14, ty_ - 44), (tx_ - 12, ty_ - 10), (tx_ + 8, ty_ - 6), (tx_ + 6, ty_ + 6)], 1),
          (240, 200, 60), lw=2.4, shade=0.4, hi=0.4)
    c.ink(ell(tx_ + 18, ty_ - 6, 22, 8), (0, 0, 0, 0), lw=4, oc=(210, 180, 120), line_only=True)
    # bar counter (hotspot "Bar") + two empty stools
    R.contact(740, 1240, 0, 120, 0.55)
    f = R.ink_box(740, 1240, 0, 112, 0, 120, (110, 60, 50), top=(170, 104, 70), seed=4308)
    fr = f["front"]
    for k in range(10):
        t = k / 10
        a = (fr[3][0] + (fr[2][0] - fr[3][0]) * t, fr[3][1])
        b_ = (fr[0][0] + (fr[1][0] - fr[0][0]) * t, fr[0][1])
        c.stroke([a, b_], 1.6, (70, 36, 34), opacity=0.7, taper=(0, 0))
    c.stroke([P(740, 30, 122), P(1240, 30, 122)], 6, (200, 170, 90), taper=(0, 0))       # brass foot rail
    for k in range(8):   # elbow dents + rings on the bar top
        x_, y_ = P(780 + k * 58, 112, 60 + (k % 3) * 18)
        c.ink(ell(x_, y_, 14, 4), (0, 0, 0, 0), lw=1.4, oc=(90, 50, 40), line_only=True, opacity=0.7)
    for X in (820, 1060):
        sx_, sy_ = P(X, 0, 170)
        st_ = P(X, 78, 170)
        c.soft(ell(sx_, sy_, 34, 7), (24, 6, 34), 0.45, 4)
        c.stroke([(sx_, sy_), st_], 7, INK, taper=(0, 0))
        c.stroke([(sx_, sy_), st_], 3.6, (190, 190, 210), taper=(0, 0))
        c.ink(ell(sx_, sy_ - 2, 22, 6), (170, 170, 190), lw=2.0)
        c.ink(rrect(st_[0] - 30, st_[1] - 6, st_[0] + 30, st_[1] + 10, 6), (200, 40, 56), lw=2.6, shade=0.4, hi=0.5)
    for X, col in ((900, (230, 190, 110)), (1150, (90, 160, 110))):
        x_, y_ = P(X, 112, 50)
        c.ink(rrect(x_ - 10, y_ - 28, x_ + 10, y_, 3), col, lw=2.0, shade=0.4, hi=0.5)
    # parrot on a hoop perch (hotspot "Parrot")
    hx_, hy_ = P(1200, 300, 90)
    c.stroke([P(1200, Hb, 90), (hx_, hy_ - 70)], 2.4, INK, taper=(0, 0))
    c.ink(ell(hx_, hy_ - 10, 48, 60), (0, 0, 0, 0), lw=6, oc=(220, 180, 80), line_only=True)
    c.stroke([(hx_ - 46, hy_ + 30), (hx_ + 46, hy_ + 30)], 6, (220, 180, 80), taper=(0, 0))
    g, g_sh = (60, 190, 90), (30, 110, 70)
    body = blob([(hx_ - 6, hy_ + 32), (hx_ - 22, hy_ + 6), (hx_ - 16, hy_ - 26), (hx_ + 2, hy_ - 40), (hx_ + 20, hy_ - 30), (hx_ + 18, hy_ - 4),
                 (hx_ + 10, hy_ + 24)], 2)
    c.ink(blob([(hx_ - 8, hy_ + 24), (hx_ - 30, hy_ + 76), (hx_ - 16, hy_ + 80), (hx_ + 4, hy_ + 28)], 1), (220, 60, 60), lw=2.2, shade=0.4)
    c.ink(body, g, lw=2.6, shade=0.5, scol=g_sh, hi=0.4)
    c.ink(blob([(hx_ - 18, hy_ - 6), (hx_ - 4, hy_ - 14), (hx_ + 12, hy_ + 2), (hx_ - 2, hy_ + 26), (hx_ - 18, hy_ + 16)], 2), (240, 200, 60), lw=2.0,
          shade=0.4)
    c.ink(blob([(hx_ + 16, hy_ - 32), (hx_ + 30, hy_ - 26), (hx_ + 26, hy_ - 14), (hx_ + 16, hy_ - 18)], 1), (240, 236, 220), lw=2.0, shade=0.3)
    c.ink(ell(hx_ + 8, hy_ - 28, 6, 6), (250, 250, 240), lw=1.6)
    c.ink(ell(hx_ + 9, hy_ - 28, 3, 3), INK, lw=0)
    c.ink(ell(hx_ + 2, hy_ - 30, 7, 6), (20, 16, 24), lw=1.2)          # eye patch
    c.stroke([(hx_ - 12, hy_ - 36), (hx_ + 14, hy_ - 24)], 1.6, INK)
    c.ink(rrect(hx_ - 18, hy_ + 36, hx_ + 22, hy_ + 50, 3), (250, 240, 214), lw=1.4)
    c.text(hx_ + 2, hy_ + 43, "ADMIRAL", 6, (120, 40, 40), "Bold")
    # ceiling: rafters, lanterns, a sagging net with floats, cables
    for z0 in (60, 280):
        R.ink_box(0, Wb, Hb - 34, Hb + 1, z0, z0 + 40, (100, 60, 60), side=(70, 40, 50), seed=z0)
    lamps = []
    for X, Z in ((300, 150), (700, 200), (1060, 150)):
        x_, y_ = P(X, Hb - 120, Z)
        lantern(c, x_, P(X, Hb, Z)[1], y_, 1.3)
        lamps.append((x_, y_))
    string_lights2(c, [P(0, Hb - 40, 40), P(420, Hb - 60, 40), P(840, Hb - 40, 40), P(Wb, Hb - 60, 40)], sag=40, seed=9,
                   colors=((255, 210, 120), (255, 160, 90)))
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    stain(c, *P(560, 420), 60, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(lamps[0][0], lamps[0][1] + 240, 520, 0.4), (lamps[1][0], lamps[1][1] + 240, 520, 0.4),
                          (lamps[2][0], lamps[2][1] + 240, 520, 0.4), (jtop[0], jtop[1], 300, 0.45, (255, 150, 90)),
                          (P(Wb, 300, 160)[0], 420, 280, 0.25, (120, 170, 255))],
               ambient=0.9, vign=0.62, top_dark=0.45, bottom_dark=0.35)
    for x_, y_ in lamps:
        c.glow2(x_, y_, 160, GLOW, 0.4)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1580, 1040, 5, 1.0, seed=81)
        fg_table_edge(sub, 1500, 2000, 1010, 120)
        fg_chair_back(sub, 60, 930, 340, 300)
        fg_cable(sub, [(400, 1100), (800, 1070), (1200, 1095)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_rusty_anchor.png")


_G = geo()
LAYOUT["rusty_anchor"] = dict(
        walk_px=STD_WALK,
        hotspots={
            ("Exit", 0): dict(box=EXIT_BOX(_G), stand=(250, 850)),
            ("Junk barrel", 0): dict(box=box3(_G, 30, 130, 0, 290, 70, 170), stand=(420, 800)),
            ("Jukebox", 0): dict(box=box3(_G, 210, 350, 0, 300, 4, 60), stand=(610, 790)),
            ("Captain Gus", 0): dict(npc="hs_captain_gus", feet=(980, 945), stand=(790, 935)),
            ("Commodore Gus", 0): dict(npc="hs_commodore_gus", feet=(980, 945), stand=(790, 935)),
            ("Bar", 0): dict(box=box3(_G, 740, 1240, 0, 112, 0, 120), stand=(1330, 800)),
            ("Parrot", 0): dict(box=box3(_G, 1150, 1250, 210, 380, 90, 90), stand=(1620, 800)),
        },
        entries={"from_downtown": (290, 880)})


# =========================================================================== 4. Starlite Diner
def seated_regular(c, x, y_table, s, skin, top, hair=None, kind="cap", seed=0, face="tired"):
    """A diner regular sitting behind a table: head, shoulders and forearms (screen px; y_table = table top)."""
    rng = random.Random(seed)
    hr = 26 * s
    cx, cy = x, y_table - 92 * s
    torso = blob([(x - 46 * s, y_table + 4), (x - 50 * s, y_table - 40 * s), (x - 30 * s, y_table - 64 * s), (x + 30 * s, y_table - 64 * s),
                  (x + 50 * s, y_table - 40 * s), (x + 46 * s, y_table + 4)], 2)
    c.ink(torso, top, lw=2.8, shade=0.5, sw=14 * s, hi=0.3)
    c.ink(rect(x - 9 * s, cy + hr * 0.7, x + 9 * s, cy + hr * 1.3), skin, lw=2.2, shade=0.5)
    head = ell(cx, cy, hr * 0.92, hr)
    c.ink(head, skin, lw=2.8, shade=0.5, sw=hr * 0.4, scol=shade_col(skin, 0.72), hi=0.35)
    for dx in (-0.36, 0.36):
        ex, ey = cx + dx * hr, cy - hr * 0.05
        if face == "tired":
            c.stroke([(ex - 6 * s, ey), (ex + 6 * s, ey)], 2.2, INK)
        else:
            c.ink(ell(ex, ey, 5 * s, 6 * s), (252, 250, 246), lw=1.6)
            c.ink(ell(ex, ey + 1, 2.4 * s, 2.8 * s), INK, lw=0)
    c.stroke([(cx - 8 * s, cy + hr * 0.5), (cx + 8 * s, cy + hr * 0.46)], 2.0, INK)
    if hair:
        c.ink(blob([(cx - hr, cy), (cx - hr * 0.9, cy - hr * 0.8), (cx, cy - hr * 1.15), (cx + hr * 0.9, cy - hr * 0.8), (cx + hr, cy),
                    (cx + hr * 0.6, cy - hr * 0.5), (cx - hr * 0.6, cy - hr * 0.5)], 2), hair, lw=2.6, shade=0.45, hi=0.4)
    if kind == "cap":
        c.ink(Sh([chaikin([(cx - hr * 1.0, cy - hr * 0.3), (cx - hr * 0.9, cy - hr * 0.95), (cx, cy - hr * 1.2), (cx + hr * 0.9, cy - hr * 0.95),
                           (cx + hr, cy - hr * 0.3)], 1, False)]), (220, 60, 70), lw=2.6, shade=0.4, hi=0.3)
        c.ink(ell(cx + hr * 0.5, cy - hr * 0.32, hr * 0.7, hr * 0.16, -5), (190, 40, 60), lw=2.2, shade=0.3)
        c.ink(rrect(cx - hr * 0.4, cy - hr * 0.95, cx + hr * 0.4, cy - hr * 0.6, 3), (250, 240, 214), lw=1.2)
    return cx, cy


def paint_starlite_diner():
    c, R, rng = std_room(4400, back=STD_BACK, light=(-0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (230, 110, 170)
    LOW = (50, 170, 170)

    def ceil(sub):
        plaster_wall(sub, (150, 90, 150), (110, 60, 120), seed=4401, w=sub.w, h=sub.h)
        for _ in range(8):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 90), (120, 80, 40), 0.25, 0, rng.randint(0, 99))

    def chrome_rail(sub, y):
        sub.ink(rect(-4, y - 10, sub.w + 4, y + 10), (210, 214, 232), lw=2.4, shade=0.4, hi=0.6, hw=3)

    def left(sub):
        two_tone_wall(sub, sub.w, sub.h, mix(WALL, (160, 60, 130), 0.25), LOW, 4402, rail=(210, 214, 232))
        x0, x1 = sub.ax(280), sub.ax(100)
        y0, y1 = sub.by(310), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (220, 50, 70), frame=(210, 214, 232), knob="L", seed=4403)
        porthole(sub, (x0 + x1) / 2, y0 + (y1 - y0) * 0.26, 34)
        exit_sign(sub, (x0 + x1) / 2, y0 - 50, 130, "STREET")
        # jukebox-style coat hooks + a "WAIT TO BE SEATED (WE WON'T)" stand-in sign
        poster(sub, sub.ax(430), sub.by(250), 130, 90, (250, 240, 214),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.25, "PLEASE WAIT", 12, (190, 40, 70)),
                                  p.text(w_ / 2, h_ * 0.5, "TO BE SEATED", 11, (190, 40, 70)),
                                  p.text(w_ / 2, h_ * 0.78, "(WE WON'T)", 9, (60, 60, 110), "Bold")), angle=3, seed=4404, peel="tl")

    def right(sub):
        two_tone_wall(sub, sub.w, sub.h, hi_col(WALL, 0.04), LOW, 4405, rail=(210, 214, 232))
        for k, (za, zb) in enumerate(((40, 190), (240, 390))):
            window_flat(sub, sub.ax(za), sub.by(380), sub.ax(zb), sub.by(200), frame=(210, 214, 232), seed=4406 + k, mullions=0, transoms=0)
        neon(sub, sub.ax(115), sub.by(420), "PIE", 40, (255, 90, 170), glow=0.5)

    def floor(sub):
        tiles(sub, (40, 30, 56), (240, 232, 220), 0, 0, sub.w, sub.h, size=60 * sub.density, seed=4407, chipped=0.1)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=4400)

    def back(sub):
        two_tone_wall(sub, sub.w, sub.h, WALL, LOW, 4408, chips=5, stains=4, rail=(210, 214, 232))
        x0, x1 = sub.ax(200), sub.ax(660)
        y0, y1 = sub.by(260), sub.by(100)
        tiles(sub, (236, 232, 226), (210, 236, 232), x0, y0, x1, y1, size=28, seed=4409, chipped=0.15)
        for _ in range(6):
            stain(sub, rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(16, 40), (140, 90, 40), 0.3, 2, rng.randint(0, 99))
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=4408)
    R.ao(0.5)
    R.edges(w=4.0)

    # pie case (hotspot "Pie case"): glass dome on a pedestal, one too-perfect pie
    R.contact(40, 130, 50, 120, 0.5)
    bx_, by_ = P(85, 0, 85)
    tx_, ty_ = P(85, 120, 85)
    c.stroke([(bx_, by_), (tx_, ty_)], 14, INK, taper=(0, 0))
    c.stroke([(bx_, by_), (tx_, ty_)], 9, (210, 214, 232), taper=(0, 0))
    c.ink(ell(bx_, by_ - 4, 40, 10), (210, 214, 232), lw=2.6, shade=0.4, hi=0.5)
    c.ink(ell(tx_, ty_, 70, 14), (210, 214, 232), lw=2.6, shade=0.4, hi=0.5)
    pie = Sh([[(tx_ - 50, ty_ - 6), (tx_ + 50, ty_ - 6), (tx_ + 44, ty_ - 30), (tx_ - 44, ty_ - 30)]])
    c.ink(pie, (230, 170, 80), lw=2.4, shade=0.4, hi=0.5)
    c.ink(ell(tx_, ty_ - 30, 44, 9), (250, 200, 110), lw=2.2, shade=0.2, hi=0.5)
    for k in range(5):
        c.stroke([(tx_ - 36 + k * 18, ty_ - 34), (tx_ - 30 + k * 18, ty_ - 26)], 1.6, (180, 110, 50))
    dome = Sh([chaikin([(tx_ - 64, ty_ - 6), (tx_ - 62, ty_ - 70), (tx_ - 30, ty_ - 108), (tx_ + 30, ty_ - 108), (tx_ + 62, ty_ - 70),
                        (tx_ + 64, ty_ - 6)], 2, False)])
    c.ink(dome, (200, 240, 255, 60), lw=2.6, oc=(150, 170, 200), shade=0, hi=0.6, hw=8)
    c.ink(ell(tx_, ty_ - 112, 10, 7), (210, 214, 232), lw=2.0, hi=0.6)
    c.stroke([(tx_ - 40, ty_ - 20), (tx_ - 38, ty_ - 80)], 5, (255, 255, 255), opacity=0.35)
    c.ink(rrect(tx_ - 40, ty_ + 18, tx_ + 40, ty_ + 36, 3), (250, 246, 230), lw=1.4)
    c.text(tx_, ty_ + 27, "DISPLAY ONLY", 6, (190, 40, 70), "Bold")
    # grill line: steel counter, griddle, hood, the shelf with the red recipe tin
    hood = R.box(200, 660, 300, 340, 0, 70)
    c.ink(Sh([hood["bottom"]]) if "bottom" in hood else Sh([hood["front"]]), (150, 150, 160), lw=2.6, shade=0.2)
    c.ink(Sh([hood["front"]]), (200, 200, 214), lw=2.8, shade=0.3, hi=0.4)
    shelf_y = 262
    sx0, sy0 = P(260, shelf_y, 0)
    sx1, _ = P(600, shelf_y, 0)
    shelf(c, sx0, sx1, sy0, 16, (210, 214, 232))
    for k, X in enumerate((280, 320, 520, 560)):     # jars + a pepper mill on the shelf
        x_, y_ = P(X, shelf_y, 0)
        c.ink(rrect(x_ - 12, y_ - 34, x_ + 12, y_, 4), rng.choice([(240, 200, 90), (200, 80, 60), (120, 180, 90), (250, 246, 236)]), lw=2.0,
              shade=0.4, hi=0.5)
    tinx, tiny = P(430, shelf_y, 0)
    tin = rrect(tinx - 38, tiny - 58, tinx + 38, tiny, 6)
    c.ink(tin, (210, 40, 50), lw=2.8, shade=0.5, sw=10, hi=0.5, rim=0.2)
    c.ink(rrect(tinx - 41, tiny - 63, tinx + 41, tiny - 49, 4), (230, 60, 60), lw=2.4, shade=0.3, hi=0.5)
    c.text(tinx, tiny - 34, "NONNA'S", 11, (255, 236, 160))
    c.text(tinx, tiny - 18, "KEEP OUT", 8, (255, 236, 160), "Bold")
    c.stroke([(tinx - 26, tiny - 6), (tinx - 6, tiny - 44)], 1.4, (120, 20, 30), opacity=0.7)   # dents
    c.glow2(tinx, tiny - 26, 90, (255, 120, 90), 0.25)
    R.contact(200, 660, 0, 90, 0.55)
    R.ink_box(200, 660, 0, 100, 0, 90, (200, 200, 214), top=(150, 150, 164), seed=4410)
    for k in range(4):
        q = [P(214 + k * 112, 88, 90), P(304 + k * 112, 88, 90), P(304 + k * 112, 14, 90), P(214 + k * 112, 14, 90)]
        c.ink(Sh([q]), (180, 180, 196), lw=2.0, shade=0.3, hi=0.3)
        x_, y_ = P(259 + k * 112, 50, 90)
        c.ink(ell(x_, y_, 9, 9), (60, 60, 70), lw=1.6, hi=0.4)
    c.ink(Sh([[P(200, 76, 91), P(660, 76, 91), P(660, 64, 91), P(200, 64, 91)]]), (60, 200, 196), lw=1.8, shade=0.3)
    gq = [P(220, 102, 10), P(500, 102, 10), P(500, 102, 80), P(220, 102, 80)]
    c.ink(Sh([gq]), (60, 56, 64), lw=2.4, shade=0.2, hi=0.3)
    for k, (X, Z) in enumerate(((250, 30), (300, 55), (350, 30), (400, 55), (450, 35), (470, 62))):   # six eggs, all at a delicate age
        x_, y_ = P(X, 104, Z)
        c.ink(blob([(x_ - 18, y_), (x_ - 10, y_ - 6), (x_ + 12, y_ - 6), (x_ + 18, y_ + 2), (x_ + 4, y_ + 6)], 2), (252, 250, 240), lw=1.8, shade=0.2)
        c.ink(ell(x_ + 1, y_ - 1, 6, 4), (255, 200, 40), lw=1.2, hi=0.6)
    for X in (260, 360, 460):
        x_, y_ = P(X, 110, 40)
        c.stroke([(x_, y_), (x_ - 8, y_ - 30), (x_ + 6, y_ - 60), (x_ - 4, y_ - 90)], 6, (255, 255, 255), opacity=0.25)
    # ticket rail with order slips
    rx0, ry0 = P(210, 290, 0)
    rx1, _ = P(650, 290, 0)
    c.stroke([(rx0, ry0), (rx1, ry0)], 5, (200, 200, 214), taper=(0, 0))
    for k in range(6):
        x_ = rx0 + 30 + k * (rx1 - rx0 - 60) / 5
        c.ink(Sh([rot_pts([(x_ - 14, ry0), (x_ + 14, ry0), (x_ + 14, ry0 + 36), (x_ - 14, ry0 + 36)], rng.uniform(-6, 6), x_, ry0)]),
              (252, 250, 236), lw=1.4, shade=0.2)
    # menu board + freezer door (hotspot "Walk-in freezer")
    mx0, my0 = P(700, 425)
    mx1, my1 = P(940, 300)
    c.ink(rect(mx0 - 12, my0 - 12, mx1 + 12, my1 + 12), (60, 40, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(mx0, my0, mx1, my1), (24, 30, 36), lw=2.2, shade=0.2, tex=0.3)
    c.text((mx0 + mx1) / 2, my0 + 18, "STARLITE SPECIALS", 13, (255, 220, 120))
    for k, (a, b2) in enumerate((("MYSTERY PIE", "ASK"), ("SAL'S MEATLOAF", "7"), ("EGGS (NERVOUS)", "4"), ("COFFEE, IF BREE", "1"))):
        y = my0 + 42 + k * 19
        c.text(mx0 + 14, y, a, 9, (230, 240, 240), "Bold", anchor="lm")
        c.text(mx1 - 14, y, b2, 9, (255, 140, 180), "Bold", anchor="rm")
    fx0, fy0 = P(740, 250)
    fx1, fy1 = P(900, 0)
    c.ink(rect(fx0 - 14, fy0 - 14, fx1 + 14, fy1), (150, 154, 170), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(fx0, fy0, fx1, fy1), (200, 206, 222), lw=2.8, shade=0.4, sw=30, hi=0.5, tex=0.12)
    for yy in np.arange(fy0 + 20, fy1 - 10, 22):
        c.stroke([(fx0 + 8, yy), (fx1 - 8, yy)], 1.2, (160, 166, 186), opacity=0.6, taper=(0, 0))
    c.ink(rrect(fx1 - 34, fy0 + 90, fx1 - 12, fy0 + 160, 5), (120, 124, 140), lw=2.4, shade=0.4, hi=0.5)
    c.ink(Sh([rot_pts([(fx0 + 14, fy0 + 24), (fx1 - 20, fy0 + 24), (fx1 - 20, fy0 + 76), (fx0 + 14, fy0 + 76)], -3, fx0, fy0)]),
          (255, 250, 220), lw=1.8, shade=0.2)
    c.text((fx0 + fx1) / 2 - 4, fy0 + 38, "REAL PIE INSIDE", 8, (40, 90, 160), "Bold", angle=3)
    c.text((fx0 + fx1) / 2 - 4, fy0 + 52, "DOOR STICKS", 7, (190, 40, 70), "Bold", angle=3)
    c.text((fx0 + fx1) / 2 - 4, fy0 + 64, "PULL HARD + PRAY", 7, (190, 40, 70), "Bold", angle=3)
    c.ink(rect(fx0, fy1 - 10, fx1, fy1), (120, 200, 255), lw=0, opacity=0.6)
    c.glow2((fx0 + fx1) / 2, fy1 - 4, 80, (140, 210, 255), 0.4, sy=0.3)
    # clock
    cx_, cy_ = P(1000, 380)
    c.ink(ell(cx_, cy_, 34, 34), (250, 246, 240), lw=3.0, shade=0.3, hi=0.3)
    c.ink(ell(cx_, cy_, 34, 34), (0, 0, 0, 0), lw=4.6, oc=(220, 50, 70), line_only=True)
    c.stroke([(cx_, cy_), (cx_, cy_ - 22)], 2.6, INK, taper=(0, 0))
    c.stroke([(cx_, cy_), (cx_ + 14, cy_ + 8)], 2.6, INK, taper=(0, 0))
    # the booth with the hungry regulars (hotspot "Hungry regulars")
    R.contact(960, 1250, 0, 150, 0.55)
    R.ink_box(960, 1250, 0, 170, 0, 40, (220, 50, 70), top=(240, 90, 100), seed=4411)
    f = R.box(960, 1250, 0, 170, 0, 40)
    for k in range(4):
        t = (k + 0.5) / 4
        a = (f["front"][0][0] + (f["front"][1][0] - f["front"][0][0]) * t, f["front"][0][1] + 8)
        c.stroke([a, (a[0], f["front"][2][1] - 40)], 2.0, (160, 30, 60), opacity=0.7)
    R.ink_box(960, 1250, 0, 60, 40, 80, (200, 40, 64), seed=4412)            # seat
    yt = P(1100, 84, 110)[1]
    regs = [seated_regular(c, P(1010, 84, 60)[0], yt, 1.05, (200, 140, 100), (90, 120, 200), kind="cap", seed=1, face="tired"),
            seated_regular(c, P(1105, 84, 60)[0], yt, 1.0, (250, 214, 190), (160, 80, 170), hair=(220, 220, 236), kind=None, seed=2,
                           face="open")]
    # nurse asleep, face-down on a stack of pancakes
    nx_ = P(1200, 84, 60)[0]
    c.ink(blob([(nx_ - 44, yt + 4), (nx_ - 48, yt - 34), (nx_ - 20, yt - 52), (nx_ + 30, yt - 50), (nx_ + 50, yt - 30), (nx_ + 46, yt + 4)], 2),
          (90, 190, 170), lw=2.8, shade=0.5, hi=0.3)
    R.contact(980, 1230, 90, 140, 0.4)
    R.ink_box(980, 1230, 74, 84, 90, 140, (250, 246, 236), top=(255, 250, 240), seed=4413)   # table top
    c.stroke([P(1105, 0, 115), P(1105, 74, 115)], 8, INK, taper=(0, 0))
    px_, py_ = P(1195, 84, 115)
    for k in range(5):
        c.ink(ell(px_, py_ - k * 7, 30, 8), (220, 160, 80), lw=1.8, shade=0.3, hi=0.4)
    c.ink(ell(px_ + 4, py_ - 44, 24, 20), (230, 190, 160), lw=2.4, shade=0.5, hi=0.3)            # head on the pancakes
    c.ink(Sh([[(px_ - 16, py_ - 58), (px_ + 22, py_ - 58), (px_ + 18, py_ - 70), (px_ - 12, py_ - 70)]]), (250, 250, 250), lw=2.0)
    c.ink(rect(px_ - 2, py_ - 68, px_ + 4, py_ - 60), (230, 50, 60), lw=0)
    c.text(px_ + 40, py_ - 74, "z", 14, (250, 250, 255), stroke=1.2, sc=INK)
    c.text(px_ + 54, py_ - 92, "Z", 18, (250, 250, 255), stroke=1.2, sc=INK)
    for X, Z, col in ((1010, 110, (250, 246, 236)), (1100, 120, (250, 246, 236))):        # empty mugs, waiting for refills
        x_, y_ = P(X, 84, Z)
        c.ink(rrect(x_ - 9, y_ - 20, x_ + 9, y_, 3), col, lw=2.0, shade=0.4, hi=0.4)
        c.ink(ell(x_ + 12, y_ - 10, 5, 6), (0, 0, 0, 0), lw=2.4, oc=col, line_only=True)
    x_, y_ = P(1120, 84, 104)
    c.ink(Sh([rot_pts([(x_ - 20, y_ - 6), (x_ + 20, y_ - 6), (x_ + 20, y_ + 6), (x_ - 20, y_ + 6)], -8, x_, y_)]), (250, 250, 240), lw=1.4)
    # ceiling: teal pendant lamps, a slow fan, cables
    lamps = []
    pipe(c, [P(0, Hb - 24, 260), P(Wb, Hb - 24, 260)], w=30, col=(170, 170, 196), brackets=[P(300, Hb - 24, 260), P(900, Hb - 24, 260)])
    hanging_cable(c, P(620, Hb, 220), 110, sway=12, w=5, col=(60, 160, 160), seed=4)
    for X, Z in ((330, 130), (1150, 200)):
        x_, y_ = P(X, Hb - 110, Z)
        pendant_lamp(c, x_, P(X, Hb, Z)[1], y_, w=110, col=(60, 200, 196), cone_to=900, cone_w=300, cone_strength=0.2)
        lamps.append((x_, y_))
    cobweb(c, *P(0, Hb, 0), 100, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    stain(c, *P(680, 410), 40, (60, 20, 50), 0.2, 2, 5)

    room_grade(c, lights=[(lamps[0][0], 600, 520, 0.42), (lamps[1][0], 600, 520, 0.42), (P(820, 300)[0], 380, 300, 0.2, (255, 220, 120)),
                          (P(350, 104, 40)[0], 560, 280, 0.3, (255, 170, 90)), (P(Wb, 300, 220)[0], 450, 280, 0.25, (140, 160, 255)),
                          (P(Wb, 420, 115)[0], 280, 220, 0.3, (255, 90, 170))],
               ambient=0.95, vign=0.58, top_dark=0.4, bottom_dark=0.35)
    for x_, y_ in lamps:
        c.glow2(x_, y_ + 20, 180, GLOW, 0.3)
    c.painterly(0.05)

    def fg(sub):
        # chrome-edged counter stool tops + a ketchup bottle silhouette
        for X in (1540, 1760):
            sub.ink(ell(X, 1040, 110, 34), FG, lw=0, shade=0.2, hi=0.25)
            sub.ink(rect(X - 14, 1040, X + 14, 1100), FG, lw=0)
        fg_bottles(sub, 120, 1060, 2, 0.9, seed=91)
        fg_cable(sub, [(400, 1100), (800, 1070), (1200, 1095)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_starlite_diner.png")


_G = geo()
_tin = _G.pt(430, 262, 0)
LAYOUT["starlite_diner"] = dict(
        walk_px=STD_WALK,
        hotspots={
            ("Exit", 0): dict(box=EXIT_BOX(_G), stand=(250, 850)),
            ("Pie case", 0): dict(box=box3(_G, 20, 150, 0, 236, 60, 110), stand=(420, 800)),
            ("Sal", 0): dict(npc="hs_sal", feet=(640, 945), stand=(850, 935)),
            ("Recipe tin", 0): dict(box=(int(_tin[0] - 48), int(_tin[1] - 72), int(_tin[0] + 48), int(_tin[1] + 6)), stand=(800, 790)),
            ("Walk-in freezer", 0): dict(box=box3(_G, 726, 914, 0, 264, 0, 0), stand=(1150, 790)),
            ("Hungry regulars", 0): dict(box=box3(_G, 960, 1250, 0, 190, 0, 140), stand=(1480, 800)),
        },
        entries={"from_downtown": (290, 880)})


# =========================================================================== layout -> act4.json, composites
def _sprite_size(name):
    return Image.open(os.path.join(OUT_DIR, name + ".png")).size


def write_layout(path=WORLD):
    """Write walkable, hotspot feet / size / standAt and entry positions into act4.json (nothing else)."""
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
                w, hh = _sprite_size(spec.get("npc") or spec["sprite"])
                h["feet"] = list(px_to_world(*spec["feet"]))
                h["size"] = [spec.get("w", 1.9) if "npc" in spec else round(w / 100, 2), round(hh / 100, 2)]
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


def composite(room_id, out_dir=None, boxes=True, alt=False):
    """Background + sprites at their feet (unscaled, like the game) + Dex depth-scaled at the two front stand
    points and at the back of the walkable area, with hotspot boxes, stand points (red) and entries (blue).
    alt=False shows the start-of-act state (no showWhenFlag hotspots); alt=True shows the flag-swapped state
    (showWhenFlag hotspots in, hideWhenFlag hotspots out)."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(WORLD))
    room = [r for r in data["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))
    shown = [h for h in room["hotspots"] if not h.get("hideWhenFlag" if alt else "showWhenFlag")]
    items = []
    for h in shown:
        slug = re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx))
    stands = sorted([world_to_px(*h["standAt"]) for h in shown], key=lambda p: -p[1])[:2] + [((wp[0][0] + wp[1][0]) / 2, yt)]
    for (sx, sy) in stands:
        k = 1.0 - 0.4 * (yb - sy) / max(1, yb - yt)
        im = dex.resize((int(dex.width * k), int(dex.height * k)), Image.LANCZOS)
        items.append((sy, im, sx))
    for fy, im, fx in sorted(items, key=lambda t: t[0]):
        bg.alpha_composite(im, (int(fx - im.width / 2), int(fy - im.height)))
    if boxes:
        ov = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.line(wp + [wp[0]], fill=(80, 255, 120, 220), width=3)
        for h in shown:
            fx, fy = world_to_px(*h["feet"])
            w, hh = h["size"][0] * 100, h["size"][1] * 100
            d.rectangle([fx - w / 2, fy - hh, fx + w / 2, fy], outline=(255, 230, 60, 255), width=3)
            sx, sy = world_to_px(*h["standAt"])
            d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(255, 80, 80, 255))
            d.text((fx - w / 2 + 4, fy - hh + 4), h["name"], fill=(255, 230, 60, 255))
        for e in room.get("entries", []):
            ex, ey = world_to_px(*e["pos"])
            d.rectangle([ex - 6, ey - 6, ex + 6, ey + 6], fill=(80, 160, 255, 255))
        bg.alpha_composite(ov)
    out = os.path.join(out_dir, "composite_%s%s.png" % (room_id, "_alt" if alt else ""))
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


def contact_sheet(out_dir=None, name="final_bgs.jpg"):
    """All Act 4 backgrounds on one sheet (two per row)."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    ims = [Image.open(os.path.join(OUT_DIR, "bg_%s.png" % r)).convert("RGB").resize((960, 540), Image.LANCZOS) for r in LAYOUT]
    sheet = Image.new("RGB", (1920, 540 * ((len(ims) + 1) // 2)), (20, 10, 30))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    out = os.path.join(out_dir, name)
    sheet.save(out, quality=90)
    print("wrote", out)


# =========================================================================== 5. Bijou Theatre lobby
def damask(sub, x0, y0, x1, y1, col, step=70):
    """Faded flock wallpaper: a diamond lattice of little fleurs (flat space)."""
    for j, y in enumerate(np.arange(y0, y1 + step, step * 0.7)):
        for x in np.arange(x0 + (j % 2) * step / 2, x1 + step, step):
            sub.ink(Sh([[(x, y - 14), (x + 9, y), (x, y + 14), (x - 9, y)]]), col, lw=0, shade=0, hi=0, ao=0, tex=0.2, wob=0.4, opacity=0.55)
            for dx in (-1, 1):
                sub.stroke([(x + dx * 6, y + 4), (x + dx * 18, y - 8), (x + dx * 14, y - 18)], 2.2, col, opacity=0.45, taper=(0.2, 0.6))


def pilaster(c, R, X, w=36, col=(230, 180, 80)):
    x0, y0 = R.pt(X - w / 2, R.Hb - 10, 0)
    x1, y1 = R.pt(X + w / 2, 0, 0)
    c.ink(rect(x0, y0, x1, y1), col, lw=2.8, shade=0.45, sw=12, hi=0.5, hw=5, tex=0.12)
    c.ink(rect(x0 - 8, y0, x1 + 8, y0 + 18), hi_col(col, 0.2), lw=2.4, shade=0.3, hi=0.4)
    c.ink(rect(x0 - 8, y1 - 26, x1 + 8, y1), shade_col(col, 0.8), lw=2.4, shade=0.3)
    for k in range(3):
        xx = x0 + (x1 - x0) * (k + 1) / 4
        c.stroke([(xx, y0 + 26), (xx, y1 - 30)], 1.6, shade_col(col, 0.6), opacity=0.6, taper=(0, 0))


def sconce(c, x, y):
    c.ink(Sh([[(x - 10, y + 10), (x + 10, y + 10), (x + 22, y - 16), (x - 22, y - 16)]]), (255, 220, 150), lw=2.4, shade=0.2, hi=0.4)
    c.ink(rrect(x - 6, y + 10, x + 6, y + 30, 3), (230, 180, 80), lw=2.0, shade=0.4)
    c.glow2(x, y - 6, 110, GLOW, 0.5)
    c.glow2(x, y - 6, 26, (255, 250, 220), 0.6)


def chandelier(c, x, y_ceil, y, s=1.0):
    c.stroke([(x, y_ceil), (x, y - 30 * s)], 4, INK, taper=(0, 0))
    c.ink(ell(x, y, 120 * s, 22 * s), (230, 180, 80), lw=3.0, shade=0.4, hi=0.5)
    c.ink(ell(x, y - 30 * s, 60 * s, 12 * s), (230, 180, 80), lw=2.6, shade=0.4, hi=0.5)
    for k in range(9):
        t = k / 8
        xx = x - 110 * s + t * 220 * s
        yy = y + 10 * s + math.sin(t * math.pi) * 14 * s
        c.stroke([(xx, yy), (xx, yy + 26 * s)], 1.6, (250, 240, 220), taper=(0, 0))
        c.ink(Sh([[(xx, yy + 24 * s), (xx + 5 * s, yy + 34 * s), (xx, yy + 44 * s), (xx - 5 * s, yy + 34 * s)]]), (230, 240, 255), lw=1.2,
              shade=0, hi=0.6)
        on = k % 4 != 2
        bx_, by_ = xx, y - 8 * s - math.sin(t * math.pi) * 8 * s
        c.ink(ell(bx_, by_, 6 * s, 8 * s), (255, 240, 180) if on else (130, 110, 100), lw=1.4)
        if on:
            c.glow2(bx_, by_, 40 * s, GLOW, 0.5)
    c.glow2(x, y, 300 * s, GLOW, 0.3)


def paint_bijou_lobby():
    c, R, rng = std_room(4500, back=STD_BACK, light=(-0.3, -0.95))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (176, 40, 90)
    LOW = (40, 120, 130)
    GOLD = (230, 180, 80)

    def ceil(sub):
        plaster_wall(sub, (110, 40, 90), (80, 26, 70), seed=4501, w=sub.w, h=sub.h)
        for k in range(1, 6):
            y = sub.h * k / 6
            sub.stroke([(0, y), (sub.w, y)], 5, (180, 130, 70), opacity=0.5, taper=(0, 0))
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 100), (40, 16, 40), 0.25, 0, rng.randint(0, 99))

    def wall(sub, seed, base, chips=4):
        grunge_wall(sub, sub.w, sub.h, base, seed=seed, chips=0, stains=3, floor_y=sub.h)
        damask(sub, 0, 0, sub.w, sub.h * 0.6, hi_col(base, 0.22))
        r_ = random.Random(seed)
        for _ in range(chips):
            chip(sub, r_.uniform(0.05, 0.95) * sub.w, r_.uniform(0.1, 0.5) * sub.h, r_.uniform(24, 50), BRICK, MORTAR, base,
                 seed=r_.randint(0, 999))
        y0 = sub.h * 0.6
        wainscot(sub, -6, sub.w + 6, y0, sub.h, LOW, seed=seed, panel_w=150 * getattr(sub, "density", 1.0))
        sub.ink(rect(-4, y0 - 12, sub.w + 4, y0 + 4), GOLD, lw=2.4, shade=0.4, hi=0.5)

    def left(sub):
        wall(sub, 4502, mix(WALL, (130, 30, 90), 0.25))
        left_exit_door(sub, "STREET", door=GOLD, seed=4503)

    def right(sub):
        wall(sub, 4504, hi_col(WALL, 0.04))
        # framed portraits of past ushers (all of them Mortimer)
        for k, z in enumerate((90, 260)):
            x0, x1 = sub.ax(z), sub.ax(z + 120)
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = sub.by(400), sub.by(250)
            sub.ink(rect(x0 - 12, y0 - 12, x1 + 12, y1 + 12), GOLD, lw=2.8, shade=0.4, hi=0.5)
            sub.ink(rect(x0, y0, x1, y1), (60, 40, 60), lw=2.0)
            cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
            sub.ink(ell(cx_, cy_ - 4, 30, 36), (240, 210, 190), lw=2.0)
            sub.ink(Sh([[(cx_ - 26, cy_ - 34), (cx_ + 26, cy_ - 34), (cx_ + 22, cy_ - 54), (cx_ - 22, cy_ - 54)]]), (196, 36, 56), lw=1.8)
            sub.ink(Sh([[(cx_ - 50, y1), (cx_ + 50, y1), (cx_ + 40, cy_ + 34), (cx_ - 40, cy_ + 34)]]), (196, 36, 56), lw=1.8)
            sub.text(cx_, y1 + 30, "MORTIMER, 19%d" % (62 + k * 9), 11, (250, 220, 150))

    def floor(sub):
        def pat(t):
            for j, y in enumerate(np.arange(0, t.h, 90 * t.density)):
                for x in np.arange((j % 2) * 45 * t.density, t.w, 90 * t.density):
                    t.ink(ell(x, y, 14 * t.density, 9 * t.density), (220, 160, 70), lw=0, shade=0, hi=0, ao=0, tex=0.2, opacity=0.5)
        carpet(sub, (140, 30, 70), 0, 0, sub.w, sub.h, seed=4505, pattern=pat)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=4500)

    def back(sub):
        wall(sub, 4506, WALL, chips=5)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=4506)
    R.ao(0.5)
    R.edges(w=4.0)
    for X in (330, 590, 890, 1250):
        pilaster(c, R, X)
    sconces = []
    for X in (330, 590, 890):
        x_, y_ = P(X, 300)
        sconce(c, x_, y_)
        sconces.append((x_, y_))
    # red runner carpet toward the auditorium doors
    run = [P(630, 0, 0), P(850, 0, 0), P(900, 0, 600), P(580, 0, 600)]
    c.ink(Sh([run]), (190, 30, 60), lw=2.4, shade=0.1, hi=0.1, tex=0.3)
    for e in ((630, 580), (850, 900)):
        c.stroke([P(e[0], 0, 0), P(e[1], 0, 600)], 5, GOLD, taper=(0, 0), opacity=0.8)

    # concession stand (hotspot "Concession stand") with the 1961 popcorn machine
    R.contact(30, 300, 30, 130, 0.55)
    f = R.ink_box(30, 300, 0, 104, 30, 130, (60, 140, 150), top=(240, 236, 226), seed=4507)
    fr = f["front"]
    (x0, y0), (x1, _), (_, y1) = fr[0], fr[1], fr[2]
    c.ink(rect(x0 + 14, y0 + 14, x1 - 14, y1 - 30), (40, 30, 60), lw=2.4, shade=0.2)
    for k in range(10):
        c.ink(rrect(x0 + 22 + k * (x1 - x0 - 44) / 10, y1 - 70 - (k % 3) * 8, x0 + 40 + k * (x1 - x0 - 44) / 10, y1 - 36, 3),
              BOOK_COLS[k % 8], lw=1.4, shade=0.3, hi=0.4)
    c.stroke([(x0 + 20, y1 - 34), (x0 + 70, y0 + 20)], 8, (255, 255, 255), opacity=0.15)
    px0, py0 = P(80, 230, 70)
    px1, py1 = P(220, 104, 70)
    c.ink(rect(px0, py0, px1, py1), (220, 40, 56), lw=3.0, shade=0.4, hi=0.4)
    c.ink(rect(px0 + 10, py0 + 30, px1 - 10, py1 - 16), (255, 240, 200, 200), lw=2.0, shade=0.1, hi=0.5)
    for _ in range(70):
        x_, y_ = rng.uniform(px0 + 14, px1 - 14), rng.uniform(py0 + 70, py1 - 20)
        c.ink(ell(x_, y_, 5, 4), (255, 236, 150), lw=0.8, oc=(200, 150, 60), shade=0.3)
    c.ink(rect(px0 - 6, py0 - 4, px1 + 6, py0 + 26), (250, 220, 90), lw=2.4, shade=0.3)
    c.text((px0 + px1) / 2, py0 + 11, "POPCORN", 13, (200, 40, 56))
    c.glow2((px0 + px1) / 2, (py0 + py1) / 2, 130, (255, 220, 140), 0.35)
    sx_, sy_ = P(260, 160, 60)
    c.ink(Sh([rot_pts([(sx_ - 60, sy_ - 34), (sx_ + 60, sy_ - 34), (sx_ + 60, sy_ + 34), (sx_ - 60, sy_ + 34)], 3, sx_, sy_)]), (252, 248, 230), lw=2.0,
          shade=0.2)
    for k, (t, sz) in enumerate((("TICKET HOLDERS ONLY", 7), ("NO TICKETS TIL 12", 7), ("YES, WE KNOW.", 8))):
        c.text(sx_, sy_ - 18 + k * 17, t, sz, (180, 30, 60) if k < 2 else (40, 80, 120), "Bold", angle=-3)
    # movie poster (hotspot "Movie poster")
    mx0, my0 = P(380, 380)
    mx1, my1 = P(530, 150)
    c.ink(rect(mx0 - 14, my0 - 14, mx1 + 14, my1 + 14), GOLD, lw=3.0, shade=0.4, hi=0.5)

    def lighthouse(p, w_, h_):
        p.ink(rect(0, 0, w_, h_), ("v", (40, 30, 90), (230, 110, 120)), lw=0)
        p.ink(rect(0, h_ * 0.72, w_, h_), (40, 60, 120), lw=0)
        p.ink(Sh([[(w_ * 0.42, h_ * 0.72), (w_ * 0.58, h_ * 0.72), (w_ * 0.54, h_ * 0.3), (w_ * 0.46, h_ * 0.3)]]), (250, 246, 240), lw=1.4)
        for k in range(3):
            yy = h_ * (0.38 + k * 0.11)
            p.ink(rect(w_ * 0.44, yy, w_ * 0.56, yy + h_ * 0.04), (220, 50, 70), lw=0)
        p.ink(rect(w_ * 0.45, h_ * 0.24, w_ * 0.55, h_ * 0.3), (255, 236, 140), lw=1.2)
        p.light_cone((w_ * 0.5, h_ * 0.27), (w_ * 1.1, h_ * 0.12), (w_ * 1.1, h_ * 0.38), (255, 246, 180), 0.5, 4)
        for dx, col in ((-0.28, (60, 40, 60)), (0.28, (60, 40, 60))):
            x_ = w_ * (0.5 + dx)
            p.ink(ell(x_, h_ * 0.62, 8, 9), col, lw=0)
            p.ink(Sh([[(x_ - 10, h_ * 0.74), (x_ + 10, h_ * 0.74), (x_ + 7, h_ * 0.65), (x_ - 7, h_ * 0.65)]]), col, lw=0)
        p.text(w_ / 2, h_ * 0.08, "LOVE AMONG THE", 9, (255, 236, 160))
        p.text(w_ / 2, h_ * 0.16, "LIGHTHOUSES", 12, (255, 236, 160))
        p.text(w_ / 2, h_ * 0.86, "TONIGHT · MIDNIGHT", 7, (255, 255, 255), "Bold")
        p.ink(ell(w_ * 0.86, h_ * 0.93, 4, 4), (250, 250, 250), lw=1.0)     # tiny heckler doodle, booing
        p.stroke([(w_ * 0.86, h_ * 0.95), (w_ * 0.86, h_ * 0.99)], 1.2, (250, 250, 250))
        p.text(w_ * 0.78, h_ * 0.92, "boo", 5, (250, 250, 250), "Bold")
    poster(c, (mx0 + mx1) / 2, (my0 + my1) / 2, mx1 - mx0, my1 - my0, (40, 30, 90), lighthouse, angle=0, seed=4508, torn=0)
    # auditorium doors (behind the velvet rope)
    dx0, dy0 = P(625, 290)
    dx1, dy1 = P(855, 0)
    c.ink(rect(dx0 - 18, dy0 - 18, dx1 + 18, dy1), GOLD, lw=3.0, shade=0.4, hi=0.5)
    xm = (dx0 + dx1) / 2
    for (a0, a1) in ((dx0, xm), (xm, dx1)):
        c.ink(rect(a0, dy0, a1, dy1), (150, 24, 50), lw=2.8, shade=0.4, sw=30, hi=0.3, tex=0.15)
        for i in range(3):
            for j in range(5):
                c.ink(ell(a0 + (a1 - a0) * (i + 1) / 4, dy0 + 40 + j * (dy1 - dy0 - 70) / 4, 3.2, 3.2), GOLD, lw=0.8, hi=0.6)
        porthole(c, (a0 + a1) / 2, dy0 + 50, 18)
        c.ink(rrect((a0 + a1) / 2 - 30 if a0 == dx0 else a0 + 8, dy0 + 140, (a0 + a1) / 2 + 30 if a0 == dx0 else a0 + 20, dy0 + 150, 3), GOLD,
              lw=1.6) if False else None
    for xx in (xm - 14, xm + 14):
        c.ink(rrect(xx - 5, dy0 + 120, xx + 5, dy0 + 170, 3), GOLD, lw=2.0, shade=0.3, hi=0.6)
    c.ink(rrect(xm - 110, dy0 - 62, xm + 110, dy0 - 26, 6), (40, 24, 50), lw=2.8, shade=0.3)
    neon(c, xm, dy0 - 44, "AUDITORIUM", 18, (255, 220, 120), glow=0.35)
    c.ink(rect(dx0, dy1 - 8, dx1, dy1), (255, 220, 140), lw=0, opacity=0.7)
    # Heckler Hall of Fame (hotspot) on the back wall, right
    hx0, hy0 = P(1010, 390)
    hx1, hy1 = P(1220, 170)
    c.ink(rect(hx0 - 12, hy0 - 12, hx1 + 12, hy1 + 12), (110, 60, 50), lw=3.0, shade=0.4, hi=0.3)
    c.ink(rect(hx0, hy0, hx1, hy1), (60, 30, 40), lw=2.0, shade=0.2, tex=0.3)
    c.ink(rrect(hx0 + 14, hy0 + 8, hx1 - 14, hy0 + 40, 4), GOLD, lw=2.0, shade=0.3, hi=0.5)
    c.text((hx0 + hx1) / 2, hy0 + 17, "BIJOU HECKLE", 10, (90, 40, 30))
    c.text((hx0 + hx1) / 2, hy0 + 31, "CHAMPION", 10, (90, 40, 30))
    for i in range(5):
        for j in range(8):
            x_ = hx0 + 18 + i * (hx1 - hx0 - 36) / 5
            y_ = hy0 + 52 + j * (hy1 - hy0 - 64) / 8
            blank = (i == 4 and j == 7)
            c.ink(rect(x_, y_, x_ + (hx1 - hx0 - 36) / 5 - 6, y_ + 12), (240, 200, 110) if not blank else (170, 140, 90), lw=1.2, shade=0.2, hi=0.4)
            if not blank:
                c.stroke([(x_ + 6, y_ + 6), (x_ + (hx1 - hx0 - 36) / 5 - 12, y_ + 6)], 1.2, (120, 70, 30), opacity=0.8)
    # costume trunk (hotspot "Costume trunk"): stickers, cracked lid, gorilla arm, tin crown, white wig curls
    R.contact(960, 1140, 50, 140, 0.55)
    f = R.ink_box(960, 1140, 0, 74, 60, 140, (120, 70, 46), top=(150, 90, 60), seed=4509)
    fr = f["front"]
    for t in (0.18, 0.82):
        a = (fr[0][0] + (fr[1][0] - fr[0][0]) * t, fr[0][1])
        c.stroke([a, (a[0], fr[2][1])], 6, (200, 170, 100), taper=(0, 0))
    for k in range(5):
        x_ = fr[0][0] + 30 + k * (fr[1][0] - fr[0][0] - 60) / 4
        y_ = (fr[0][1] + fr[2][1]) / 2 + rng.uniform(-14, 14)
        col = rng.choice([(255, 236, 120), (160, 230, 255), (255, 170, 200), (250, 250, 240)])
        c.ink(ell(x_, y_, 16, 11, rng.uniform(-20, 20)) if k % 2 else Sh([rot_pts([(x_ - 16, y_ - 10), (x_ + 16, y_ - 10), (x_ + 16, y_ + 10),
                                                                                (x_ - 16, y_ + 10)], rng.uniform(-14, 14), x_, y_)]), col, lw=1.6, shade=0.2)
    lid = [P(960, 74, 60), P(1140, 74, 60), P(1140, 150, 40), P(960, 150, 40)]
    c.ink(Sh([lid]), (140, 84, 54), lw=3.0, shade=0.4, hi=0.3)
    tx_, ty_ = P(1000, 80, 100)
    c.ink(limb([(tx_, ty_), (tx_ - 30, ty_ + 24), (tx_ - 46, ty_ + 60)], [26, 22, 18]), (50, 44, 50), lw=2.6, shade=0.4, tex=0.3)   # gorilla arm
    c.ink(ell(tx_ - 48, ty_ + 66, 16, 12), (70, 60, 66), lw=2.2, shade=0.3)
    cx_, cy_ = P(1080, 84, 90)
    c.ink(Sh([[(cx_ - 26, cy_), (cx_ + 26, cy_), (cx_ + 30, cy_ - 30), (cx_ + 14, cy_ - 14), (cx_, cy_ - 34), (cx_ - 14, cy_ - 14), (cx_ - 30, cy_ - 30)]]),
          (210, 214, 230), lw=2.4, shade=0.4, hi=0.6)
    for k in range(4):
        c.ink(ell(cx_ + 34 + k * 10, cy_ - 4 - (k % 2) * 8, 10, 8), (250, 250, 252), lw=1.8, shade=0.4)
    # ceiling: chandelier + cables
    chx, chy = P(Wb / 2, Hb - 45, 220)
    chandelier(c, chx, P(Wb / 2, Hb, 220)[1], chy, 1.1)
    cable(c, P(0, Hb, 180), P(500, Hb, 300), sag=50, w=6, col=(60, 30, 60))
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    hanging_web(c, chx - 90, chy + 20, 60)

    room_grade(c, lights=[(chx, chy + 200, 640, 0.45)] + [(x, y + 40, 260, 0.35) for x, y in sconces] +
               [((px0 + px1) / 2, (py0 + py1) / 2, 260, 0.3, (255, 220, 140)), (xm, dy1 - 20, 300, 0.2, (255, 200, 140))],
               ambient=0.92, vign=0.6, top_dark=0.42, bottom_dark=0.35)
    c.glow2(chx, chy, 220, GLOW, 0.3)
    c.painterly(0.05)

    def fg(sub):
        # theatre seat backs + a stanchion silhouette
        for X in (1560, 1800):
            fg_chair_back(sub, X, 960, 300, 200)
        sub.ink(ell(90, 1000, 26, 26), FG, lw=0)
        sub.ink(rect(80, 1000, 100, 1100), FG, lw=0)
        fg_cable(sub, [(300, 1100), (700, 1070), (1100, 1095)], 16)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_bijou_lobby.png")


_G = geo()
LAYOUT["bijou_lobby"] = dict(
        walk_px=STD_WALK,
        hotspots={
            ("Exit", 0): dict(box=EXIT_BOX(_G), stand=(250, 850)),
            ("Concession stand", 0): dict(box=box3(_G, 30, 300, 0, 240, 30, 130), stand=(460, 800)),
            ("Movie poster", 0): dict(box=box3(_G, 366, 544, 136, 394, 0, 0), stand=(800, 790)),
            ("Mortimer", 0): dict(npc="hs_mortimer", feet=(800, 945), stand=(980, 935)),
            ("Velvet rope", 0): dict(sprite="hs_velvet_rope", feet=ROPE_FEET, stand=(1108, 830)),
            ("Costume trunk", 0): dict(box=box3(_G, 950, 1150, 0, 160, 40, 140), stand=(1380, 800)),
            ("Heckler Hall of Fame", 0): dict(box=box3(_G, 998, 1232, 158, 402, 0, 0), stand=(1440, 790)),
        },
        entries={"from_downtown": (290, 880)})


ASSETS = {
    **{n: (lambda n=n: paint_npc(n)) for n in NPC_FN},
    "hs_velvet_rope": paint_velvet_rope,
    "bg_downtown": paint_downtown, "bg_quickmart": paint_quickmart, "bg_rusty_anchor": paint_rusty_anchor,
    "bg_starlite_diner": paint_starlite_diner, "bg_bijou_lobby": paint_bijou_lobby,
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
            if r == "rusty_anchor":
                composite(r, alt=True)
        contact_sheet()
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
