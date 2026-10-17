#!/usr/bin/env python3
"""
Big Night Out -- Act 2 (Greek Week) art: Greek Row, the frat house, the Fuse Box bar,
Tess Calloway, Chad Thunderclap, Dolly Spark, Fernanda the flamingo and the act's item icons.

All original, drawn procedurally with the helpers in paint.py (same style: bold dark outlines,
warm saturated cel shading, big-headed characters).

Usage:  python3 tools/art/act2.py            # paint everything
        python3 tools/art/act2.py tess icon  # paint assets whose name contains these words
Prop positions are read from Assets/_Project/World/act2.json so the art lines up with the click boxes.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, W_BG, H_BG, WALL_Y, Canvas, Image, bez, cap, dk, ell, eye, lt, mix, poly,  # noqa: E402
                   rect, rrect, shoe_shape, wonky)

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "act2.json")


# --------------------------------------------------------------------------- hotspot boxes from the JSON
def _load_boxes():
    data = json.load(open(WORLD))
    out = {}
    for r in data["rooms"]:
        for h in r["hotspots"]:
            fx, fy = h["feet"]
            w, hh = h["size"]
            x0 = (fx - w / 2 + 9.6) * 100
            x1 = (fx + w / 2 + 9.6) * 100
            y1 = (5.4 - fy) * 100
            y0 = y1 - hh * 100
            out[(r["id"], h["name"])] = (x0, y0, x1, y1)
    return out


BOX = _load_boxes()


def box(room, name):
    return BOX[(room, name)]


def flip(c):
    c.img = c.img.transpose(Image.FLIP_LEFT_RIGHT)


# =========================================================================== characters
def paint_tess():
    """Tess Calloway: sorority president. Pearls, pink cardigan, headband, clipboard. Faces right."""
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (250, 210, 182), (220, 152, 132)
    hair, hair_sh, hair_hi = (132, 70, 42), (92, 44, 32), (186, 110, 66)
    card, card_sh, card_hi = (255, 130, 168), (214, 80, 128), (255, 186, 210)
    navy, navy_sh = (56, 64, 136), (36, 40, 96)
    loaf = (126, 64, 40)

    # (drawn facing LEFT, flipped at the end)
    # bob hair behind the head
    c.paint(poly([(34, 44), (60, 26), (86, 38), (92, 62), (90, 84), (80, 90), (70, 82), (44, 80)], 2, True), hair,
            shade=(4, 0, hair_sh))
    # far arm: hand on hip
    c.paint(cap([(72, 100), (88, 118), (72, 134)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(ell(70, 134, 6, 5.5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(70, 98), (86, 116), (80, 126)], 14), card, shade=(3, 2, card_sh))
    c.paint(ell(80, 127, 7.5, 3.5, -40), lt(card, 0.3), ow=2.2)
    # legs: skin + white knee socks + loafers pointing left
    c.paint(cap([(64, 160), (66, 200), (64, 222)], 12), skin, shade=(3, 0, skin_sh))
    c.paint(cap([(48, 160), (45, 200), (44, 224)], 12.5), skin, shade=(3, 0, skin_sh))
    for x0, y0, x1, y1 in ((58, 206, 71, 236), (38, 208, 51, 238)):
        c.paint(rrect(x0, y0, x1, y1, 3), (250, 248, 240), ow=2.6, shade=(3, 0, (214, 210, 224)))
        c.line([(x0 + 1, y0 + 5), (x1 - 1, y0 + 5)], 1.2, card_sh)
    for xh, xt, yt, yb in ((72, 46, 234, 250), (52, 22, 236, 252)):
        sh = shoe_shape(xh, xt, yt, yb, toe_h=0.6)
        c.paint(sh, loaf, shade=(3, -2, dk(loaf, 0.72)), hi=(-2, 2, lt(loaf, 0.35), 1.5))
        c.line([(xh - 8, yt + 3), (xh - 16, yt + 4)], 1.6)
        c.paint(ell(xh - 12, yt + 4.5, 2, 1.5), (240, 196, 80), ow=1.2)
    # pleated navy skirt with a pink stripe
    skirt = poly([(38, 128), (74, 128), (82, 164), (30, 164)], 1)

    def pleats(p):
        for x in range(30, 86, 8):
            p.line([(56 + (x - 56) * 0.6, 130), (x, 166)], 1.4, navy_sh)
        p.rect(20, 154, 90, 158, card)
    c.paint(skirt, navy, pattern=pleats, shade=(4, 0, navy_sh))
    # neck
    c.paint(cap([(56, 80), (56, 96)], 9.5), skin, shade=(3, 0, skin_sh))
    # torso: white blouse under a pink cardigan
    torso = poly([(38, 94), (54, 90), (72, 93), (76, 104), (74, 132), (38, 132), (34, 114), (33, 102)], 2)
    c.paint(torso, card, shade=(4, 2, card_sh), hi=(-3, 3, card_hi, 2),
            pattern=lambda p: [p.ell(56, y, 1.5, 1.5, (255, 246, 248)) for y in (110, 120)])
    c.paint(poly([(48, 91), (63, 91), (58, 132), (52, 132)], 1), (252, 250, 244), ow=2.0)
    c.line([(55, 104), (55, 131)], 1.2, (200, 200, 214))
    c.paint(poly([(45, 89), (55, 96), (49, 103), (42, 95)], 1), (252, 250, 244), ow=2)  # collar
    c.paint(poly([(57, 96), (66, 88), (71, 95), (62, 103)], 1), (252, 250, 244), ow=2)
    # pearls
    for k in range(9):
        a = math.radians(200 - k * 22.5)
        px, py = 56 + 11 * math.cos(a) * -1, 95 + 7 * math.sin(a) * -1 + 4
        c.paint(ell(px, py, 2.1, 2.1), (255, 252, 240), ow=1.2, hi=(-0.6, -0.6, (255, 255, 255)))
    # near arm hugging a clipboard to the chest
    c.paint(cap([(38, 100), (30, 118), (44, 124)], 8), skin, shade=(3, 2, skin_sh))
    cb = poly([(22, 98), (52, 96), (54, 134), (24, 136)])
    c.paint(cb, (176, 120, 70), shade=(3, 2, (130, 84, 50)))
    c.paint(poly([(26, 102), (49, 101), (50, 131), (28, 132)]), (252, 252, 246), ow=2,
            pattern=lambda p: [p.line([(30, 108 + i * 5), (46 - (i % 2) * 6, 108 + i * 5)], 1.0, (120, 130, 170))
                               for i in range(5)])
    c.paint(rrect(31, 94, 43, 101, 2), (200, 200, 210), ow=2)
    c.line([(32, 112), (34, 115), (38, 110)], 1.4, (220, 50, 90))
    c.paint(ell(44, 124, 6, 5.5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(38, 98), (32, 110), (36, 118)], 14), card, shade=(3, 2, card_sh))
    c.paint(ell(37, 119, 7, 3.5, 10), lt(card, 0.3), ow=2.2)

    # ---- head (3/4, facing left)
    head = ell(58, 56, 23.5, 26) + poly([(36, 60), (40, 78), (50, 87), (62, 84), (76, 70)], 2) + ell(33.5, 62, 5, 4.8)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 228, 206), 2.5))
    c.curve((34, 65), (31, 66), (30, 63), 1.4)
    c.paint(ell(51, 70, 6, 3.4), (255, 130, 140), ow=0, opacity=0.5)
    c.paint(ell(37, 69, 3.5, 2.6), (255, 130, 140), ow=0, opacity=0.45)
    eye(c, 54, 58, 8, 10, 50, 59, 2.4, lid=0.22, lid_tilt=-0.8, skin=skin, lashes=1, iris=(70, 130, 210))
    eye(c, 38.5, 57.5, 5.6, 9.4, 35.5, 58.5, 2.1, lid=0.22, lid_tilt=0.8, skin=skin, lashes=-1, iris=(70, 130, 210))
    # perfectly arched brows, one raised (judging you, kindly)
    c.line([(46, 43), (53, 39), (62, 42)], 2.2, hair_sh)
    c.line([(33, 47), (40, 45)], 2.0, hair_sh)
    # polite pageant smile
    c.paint(poly([(38, 74), (46, 77), (54, 74), (52, 79), (44, 81), (40, 78)], 1), (214, 70, 110), ow=1.8)
    c.paint(poly([(41, 75.5), (46, 77.5), (52, 75.2), (50, 77), (44, 78.5)], 1), (255, 255, 255), ow=0)
    # pearl earring
    c.paint(ell(77, 72, 2.6, 2.6), (255, 252, 240), ow=1.4)
    c.paint(ell(78, 62, 5.5, 8), skin, shade=(2, 2, skin_sh))
    # bob front + side-swept bangs
    c.paint(poly([(34, 50), (40, 36), (56, 30), (74, 32), (86, 44), (90, 62), (88, 82), (80, 86), (78, 70),
                  (74, 54), (62, 46), (50, 46), (40, 52)], 2, True), hair, shade=(3, 2, hair_sh),
            hi=(-2, 3, hair_hi, 1.5))
    c.curve((80, 50), (86, 66), (82, 82), 1.3, hair_sh)
    c.curve((60, 46), (52, 40), (40, 44), 1.3, hair_sh)
    # big pink headband with a bow
    c.paint(cap(bez((36, 42), (58, 22), (82, 36), 14), 6), card, shade=(0, 2, card_sh), hi=(0, -1.5, card_hi))
    c.paint(poly([(70, 30), (84, 20), (86, 34)], 1) + poly([(70, 30), (80, 40), (64, 42)], 1), card,
            shade=(2, 2, card_sh))
    c.paint(ell(71, 31, 3.5, 3.5), card_sh, ow=2)
    flip(c)
    c.fit(margin=3)
    c.save("hs_tess_calloway.png")


def paint_chad():
    """Chad Thunderclap: frat president in a toga and laurel wreath, arms crossed. Faces left."""
    c = Canvas(120, 260, ow=3)
    skin, skin_sh, skin_hi = (240, 176, 128), (204, 128, 96), (255, 210, 170)
    hair, hair_sh, hair_hi = (250, 214, 110), (214, 162, 60), (255, 240, 180)
    toga, toga_sh = (250, 248, 238), (204, 200, 220)
    trim = (230, 176, 50)
    leaf_c, leaf_sh = (110, 170, 70), (70, 120, 50)

    # legs (bare calves, sandals)
    c.paint(cap([(72, 180), (74, 210), (72, 236)], 14), skin, shade=(3, 0, skin_sh))
    c.paint(cap([(44, 180), (40, 210), (38, 238)], 15), skin, shade=(3, 0, skin_sh))
    for xh, xt, yt, yb in ((82, 54, 238, 252), (50, 16, 240, 256)):
        sole = poly([(xh + 2, yb - 5), (xt, yb - 5), (xt - 2, yb), (xh + 3, yb)], 1)
        foot = shoe_shape(xh, xt, yt, yb - 3, toe_h=0.6)
        c.paint(foot, skin, shade=(3, -2, skin_sh))
        c.paint(sole, (150, 96, 54), ow=2.4)
        for t in (0.3, 0.6):
            x = xh + (xt - xh) * t
            c.line([(x + 2, yt + 1), (x - 3, yb - 4)], 2.2, (130, 80, 44))
        c.line([(xh - 2, yt - 14), (xh - 10, yt - 6)], 2.2, (130, 80, 44))
        c.line([(xh - 12, yt - 14), (xh - 2, yt - 4)], 2.2, (130, 80, 44))
    # toga body: wide, falls to the knees, bare far shoulder
    body = poly([(28, 98), (60, 92), (96, 96), (100, 130), (94, 160), (90, 196), (60, 200), (26, 196), (24, 160),
                 (22, 128)], 2)

    def folds(p):
        for k in range(5):
            p.line(bez((30 + k * 4, 100 + k * 8), (60, 130 + k * 10), (94, 112 + k * 16), 12), 2.4, toga_sh)
        p.rect(20, 188, 104, 196, trim)
    # bare far shoulder + arm (muscles!)
    c.paint(ell(90, 104, 15, 13), skin, shade=(4, 3, skin_sh), hi=(-3, -3, skin_hi, 2))
    c.paint(body, toga, pattern=folds, shade=(5, 0, toga_sh))
    c.line([(66, 96), (96, 120)], 1.6, toga_sh)
    # sash over the near shoulder
    c.paint(poly([(26, 96), (48, 90), (66, 120), (56, 150), (40, 124)], 1), toga, shade=(3, 2, toga_sh))
    c.paint(cap([(30, 94), (62, 136)], 4), trim, ow=2.2)
    # neck (thick)
    c.paint(cap([(58, 78), (58, 96)], 20), skin, shade=(4, 0, skin_sh))
    # crossed arms (big forearms across the chest)
    c.paint(cap([(98, 108), (102, 124), (40, 126)], 15), skin, shade=(3, 3, skin_sh), hi=(-2, -2, skin_hi, 1.5))
    c.paint(ell(36, 124, 9, 8), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(22, 104), (18, 122), (82, 116)], 15), skin, shade=(3, 3, skin_sh), hi=(-2, -2, skin_hi, 1.5))
    c.paint(ell(86, 114, 9, 8), skin, shade=(2, 2, skin_sh))
    c.line([(82, 110), (86, 108)], 1.3, skin_sh)
    c.paint(poly([(30, 92), (44, 92), (34, 112), (22, 112), (20, 100)], 1), toga, shade=(2, 2, toga_sh))  # drape
    # gold wrist cuff
    c.paint(rrect(28, 116, 36, 130, 2), trim, ow=2.2, hi=(-1, 0, (255, 230, 140)))

    # ---- head (3/4 facing left; square jaw)
    head = ell(60, 50, 24, 25) + poly([(36, 50), (36, 74), (46, 84), (70, 84), (82, 66)], 1) + ell(35, 56, 5, 5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, skin_hi, 2.5))
    c.paint(ell(80, 56, 5.5, 8), skin, shade=(2, 2, skin_sh))
    c.curve((36, 60), (32, 61), (32, 57), 1.4)
    c.line([(49, 80), (49, 84)], 1.4, skin_sh)  # chin dimple
    eye(c, 54, 52, 7.5, 8.5, 50, 53, 2.3, lid=0.42, lid_tilt=-0.5, skin=skin, iris=(80, 150, 210))
    eye(c, 39.5, 51.5, 5.2, 7.8, 37, 52.5, 2.0, lid=0.42, lid_tilt=0.5, skin=skin, iris=(80, 150, 210))
    c.line([(46, 41), (54, 39), (62, 41)], 2.8, hair_sh)
    c.line([(34, 42), (41, 41)], 2.6, hair_sh)
    # big smug grin
    grin = poly([(36, 68), (46, 70), (58, 67), (56, 74), (46, 77), (39, 74)], 1)
    c.paint(grin, (255, 255, 255), ow=1.8)
    c.line([(37.5, 70.5), (47, 72.5), (57, 69.5)], 1.1)
    c.curve((58, 66), (61, 67), (60, 70), 1.4)
    # blond swoop
    c.paint(poly([(36, 40), (38, 28), (50, 20), (70, 20), (84, 30), (86, 46), (80, 52), (78, 40), (66, 34),
                  (52, 36), (42, 34)], 2, True), hair, shade=(3, 2, hair_sh), hi=(-2, 3, hair_hi, 1.5))
    c.paint(poly([(40, 30), (30, 26), (26, 32), (38, 36)], 1), hair, ow=2.4, shade=(2, 2, hair_sh))
    c.curve((48, 26), (60, 24), (72, 30), 1.3, hair_sh)
    # laurel wreath
    for k in range(7):
        t = k / 6
        x = 38 + 46 * t
        y = 34 - 10 * math.sin(math.pi * t) + 2
        c.paint(ell(x, y, 5.5, 2.6, -30 + 60 * t), leaf_c, ow=2, shade=(1, 1, leaf_sh))
        c.paint(ell(x + 2, y + 4, 4.5, 2.2, 30 + 30 * t), leaf_c, ow=2, shade=(1, 1, leaf_sh))
    c.fit(margin=3)
    c.save("hs_chad_thunderclap.png")


def paint_dolly():
    """Dolly Spark: DJ. Neon hair, headphones, safety-pinned denim jacket, glow bracelets. Faces left."""
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (204, 146, 112), (166, 104, 86)
    hair, hair_sh, hair_hi = (255, 82, 170), (200, 40, 130), (255, 170, 214)
    teal = (40, 220, 210)
    denim, denim_sh, denim_hi = (110, 160, 220), (70, 110, 176), (170, 206, 246)
    black = (44, 36, 56)
    tights, tights2 = (130, 60, 190), (40, 30, 60)

    # high ponytail behind
    c.paint(poly([(70, 30), (92, 22), (104, 40), (100, 70), (94, 92), (86, 74), (84, 50)], 2, True), hair,
            shade=(3, 2, hair_sh), pattern=lambda p: p.poly([(92, 70), (104, 60), (100, 96), (88, 92)], teal))
    # far arm: hand on hip, glow bracelets
    c.paint(cap([(72, 100), (88, 120), (72, 136)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(ell(70, 136, 6, 5.5), skin, shade=(2, 2, skin_sh))
    for k, col in enumerate(((80, 255, 120), (255, 90, 200))):
        c.paint(ell(79 - k * 3, 128 + k * 3, 5.5, 2.2, -40), (0, 0, 0, 0), ow=2.2, oc=col)
    c.paint(cap([(70, 98), (86, 116)], 15), denim, shade=(3, 2, denim_sh))
    # legs: striped tights + chunky platform sneakers pointing left
    stripes = lambda p: [p.rect(20, y, 90, y + 4, tights2) for y in range(160, 236, 9)]
    c.paint(cap([(64, 156), (68, 196), (64, 222)], 12), tights, shade=(3, 0, dk(tights, 0.7)), pattern=stripes)
    c.paint(cap([(46, 156), (42, 196), (42, 224)], 12.5), tights, shade=(3, 0, dk(tights, 0.7)), pattern=stripes)
    for xh, xt, yt, yb in ((78, 48, 228, 248), (58, 22, 230, 252)):
        sh = shoe_shape(xh, xt, yt, yb - 6, toe_h=0.65)
        c.paint(sh, (250, 248, 240), shade=(3, -2, (206, 204, 220)),
                pattern=lambda p, xh=xh, xt=xt, yt=yt: p.ell(xt + 9, yt + 9, 7, 5, (255, 82, 170)))
        c.paint(rrect(min(xh, xt) - 1, yb - 7, max(xh, xt) + 3, yb + 2, 3), teal, ow=2.6,
                hi=(0, 2, lt(teal, 0.4)))
        for k in range(3):
            c.line([(xh - 12 - k * 4, yt + 1 + k), (xh - 10 - k * 4, yt + 5 + k)], 1.3)
    # black mini skirt
    c.paint(poly([(38, 128), (74, 128), (80, 160), (32, 160)], 1), black, shade=(4, 0, dk(black, 0.6)),
            pattern=lambda p: p.rect(30, 128, 82, 133, (70, 60, 84)))
    c.paint(ell(46, 131, 2, 2), (230, 230, 240), ow=1.2)  # belt stud
    c.paint(ell(60, 131, 2, 2), (230, 230, 240), ow=1.2)
    # neck
    c.paint(cap([(56, 80), (56, 96)], 9.5), skin, shade=(3, 0, skin_sh))
    # black tank top
    c.paint(poly([(44, 92), (68, 92), (72, 130), (40, 130)], 1), black, shade=(3, 0, dk(black, 0.6)),
            pattern=lambda p: (p.ell(56, 112, 7, 7, (255, 82, 170)), p.ell(56, 112, 3, 3, black)))
    # cropped denim jacket, open, covered in safety pins + patches
    def jacket_bits(p):
        rng = random.Random(9)
        for _ in range(16):
            x, y = rng.uniform(26, 82), rng.uniform(96, 128)
            if 42 < x < 70:
                continue
            a = rng.uniform(0, math.pi)
            p.line([(x, y), (x + 6 * math.cos(a), y + 6 * math.sin(a))], 1.6, (226, 228, 236))
            p.ell(x, y, 1.3, 1.3, (190, 194, 206))
    left = poly([(32, 94), (48, 90), (48, 130), (34, 130), (30, 110)], 1)
    right = poly([(64, 90), (74, 94), (78, 110), (76, 130), (64, 130)], 1)
    c.paint(left, denim, shade=(3, 2, denim_sh), hi=(-2, 2, denim_hi, 1.5), pattern=jacket_bits)
    c.paint(right, denim, shade=(3, 2, denim_sh), pattern=jacket_bits)
    c.paint(ell(38, 120, 5, 5), (255, 214, 60), ow=1.8)  # smiley patch
    c.line([(36, 121), (38, 123), (40, 121)], 1.0)
    c.paint(rrect(66, 116, 76, 126, 2), (255, 90, 120), ow=1.8)  # lightning patch
    c.line([(72, 117), (69, 121), (73, 121), (70, 125)], 1.2, (255, 240, 120))
    c.paint(poly([(44, 89), (52, 95), (48, 104), (40, 96)], 1), denim_hi, ow=2)
    c.paint(poly([(60, 95), (68, 88), (72, 96), (64, 104)], 1), denim_hi, ow=2)
    # big headphones around the neck
    c.curve((42, 98), (56, 112), (72, 98), 4.5, (40, 40, 46))
    c.paint(ell(70, 95, 6, 8, 15), black, ow=2.4, pattern=lambda p: p.ell(70, 95, 3.5, 5, teal, 15))
    c.paint(ell(43, 97, 7.5, 9.5, -15), black, ow=2.6, pattern=lambda p: p.ell(42, 97, 4.5, 6, teal, -15))
    # near arm: raised, rock-on hand
    c.paint(cap([(36, 98), (24, 90), (22, 66)], 8), skin, shade=(3, 2, skin_sh))
    hand = ell(22, 62, 6.5, 6) + cap([(18, 58), (16, 48)], 3.4) + cap([(26, 58), (28, 48)], 3.4)
    c.paint(hand, skin, shade=(2, 2, skin_sh))
    c.paint(ell(23, 74, 5, 2.2, 80), (0, 0, 0, 0), ow=2.2, oc=(80, 255, 120))
    c.paint(cap([(38, 98), (28, 92)], 15), denim, shade=(3, 2, denim_sh))
    c.paint(ell(26, 90, 4, 7.5, 30), denim_hi, ow=2.2)

    # ---- head (3/4, facing left)
    head = ell(58, 56, 23.5, 26) + poly([(36, 60), (40, 78), (50, 87), (62, 84), (76, 70)], 2) + ell(33.5, 62, 5, 4.8)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (226, 176, 140), 2.5))
    c.curve((34, 65), (31, 66), (30, 63), 1.4)
    c.paint(ell(33, 64, 1.1, 1.1), (240, 240, 250), ow=0.8)  # nose stud
    c.paint(ell(51, 70, 6, 3.4), (240, 100, 140), ow=0, opacity=0.45)
    eye(c, 54, 58, 8, 10, 50, 58, 2.5, lid=0.18, skin=skin, lashes=1, iris=(150, 80, 200))
    eye(c, 38.5, 57.5, 5.6, 9.4, 35.5, 57.5, 2.2, lid=0.18, skin=skin, lashes=-1, iris=(150, 80, 200))
    c.line([(61, 52), (67, 48)], 2.4)  # winged liner
    c.line([(44, 44), (52, 41), (60, 43)], 2.2, (60, 30, 50))
    c.line([(33, 47), (40, 45)], 2.0, (60, 30, 50))
    # big open grin
    c.paint(poly([(38, 72), (48, 74), (56, 70), (54, 78), (46, 82), (40, 78)], 1), (110, 30, 50), ow=1.8,
            pattern=lambda p: (p.rect(38, 71, 58, 75, (255, 255, 255)), p.ell(47, 80, 5, 2.4, (240, 110, 120))))
    c.paint(ell(78, 62, 5.5, 8), skin, shade=(2, 2, skin_sh))
    for k in range(3):
        c.paint(ell(78 + k * 0.6, 56 + k * 5, 1.6, 1.6), (0, 0, 0, 0), ow=1.4, oc=(230, 230, 240))
    # asymmetric neon bob with long bangs and teal tips
    c.paint(poly([(30, 52), (34, 36), (48, 28), (66, 26), (82, 32), (90, 46), (88, 64), (82, 68), (78, 54),
                  (70, 44), (58, 44), (48, 52), (42, 64), (34, 66)], 2, True), hair, shade=(3, 2, hair_sh),
            hi=(-2, 3, hair_hi, 1.5), pattern=lambda p: p.poly([(28, 58), (44, 56), (42, 70), (30, 70)], teal))
    c.curve((70, 34), (58, 38), (46, 50), 1.3, hair_sh)
    c.paint(ell(78, 26, 7, 5, -20), black, ow=2.2)  # hair tie
    c.fit(margin=3)
    c.save("hs_dolly_spark.png")


def draw_flamingo(c, cx, by, s=1.0, base=True, legs=True):
    """Fernanda: a seven-foot inflatable flamingo. (cx, by) = bottom centre of her inflatable base."""
    pink, pink_sh, pink_hi = (255, 112, 168), (220, 66, 132), (255, 186, 214)
    def T(x, y):
        return (cx + x * s, by + y * s)
    def P(pts):
        return [T(*q) for q in pts]
    if base:
        c.paint(ell(*T(0, -10), 34 * s, 10 * s), (90, 200, 220), shade=(0, -3 * s, (60, 150, 180)),
                hi=(0, 2.5 * s, (180, 240, 250)))
        c.paint(ell(*T(0, -14), 24 * s, 5 * s), (60, 150, 180), ow=0)
    # legs
    if legs:
        c.paint(cap(P([(-5, -16), (-5, -60), (-8, -98)]), 4.5 * s), pink_sh, ow=2.4)
        c.paint(cap(P([(8, -16), (6, -50), (14, -62), (4, -76), (-2, -98)]), 4.5 * s), pink, ow=2.4)
        c.paint(ell(*T(6, -50), 4 * s, 4 * s), pink, ow=2.2)
    # body: plump inflatable with a seam
    body = poly(P([(-38, -128), (-30, -150), (0, -158), (26, -150), (40, -132), (32, -108), (8, -96), (-20, -98),
                   (-38, -110)]), 2, True)
    c.paint(body, pink, shade=(4 * s, 4 * s, pink_sh), hi=(-4 * s, -4 * s, pink_hi, 3 * s))
    c.line(P([(-30, -126), (0, -118), (30, -126)]), 1.3 * s, pink_sh)
    # wing
    c.paint(poly(P([(-24, -134), (6, -142), (24, -128), (6, -114), (-18, -116)]), 2, True), pink_hi,
            ow=2.4, shade=(2 * s, 2 * s, pink))
    for k in range(3):
        c.line(P([(-14 + k * 9, -130), (-8 + k * 9, -120)]), 1.2 * s, pink_sh)
    # tail feathers
    c.paint(poly(P([(-36, -128), (-50, -140), (-46, -126), (-52, -118), (-36, -114)]), 1), pink, ow=2.4,
            shade=(2, 2, pink_sh))
    # S-neck
    neck = bez(T(22, -146), T(48, -190), T(14, -214), 18) + bez(T(14, -214), T(-10, -238), T(16, -248), 10)[1:]
    c.paint(cap(neck, 12 * s), pink, shade=(3 * s, 0, pink_sh), hi=(-2.5 * s, 0, pink_hi, 1.5 * s))
    # head + beak
    c.paint(ell(*T(18, -250), 11 * s, 10 * s), pink, shade=(2, 2, pink_sh), hi=(-2, -2, pink_hi, 1.5))
    beak = poly(P([(26, -256), (42, -248), (40, -234), (34, -238), (28, -244)]), 1)
    c.paint(beak, (255, 236, 200), ow=2.4)
    c.paint(poly(P([(38, -250), (44, -246), (42, -232), (37, -236)]), 1), (40, 30, 40), ow=0, clip=beak)
    # eye with long lashes (she's fabulous)
    c.paint(ell(*T(18, -252), 3.5 * s, 4 * s), (255, 255, 255), ow=1.8)
    c.paint(ell(*T(19.5, -252), 1.6 * s, 2 * s), OUT, ow=0)
    for k in range(3):
        c.line(P([(15 + k * 2.5, -256), (13 + k * 3, -261)]), 1.3)
    # inflation valve
    c.paint(ell(*T(-26, -106), 3 * s, 3 * s), (255, 240, 250), ow=1.6)


def paint_fernanda():
    c = Canvas(160, 260, ow=3)
    draw_flamingo(c, 80, 256, 1.0)
    c.fit(margin=3)
    c.save("hs_fernanda.png")


def paint_bedsheet():
    """The bedsheet hanging on the sorority clothesline: pegs at the very top, so it hangs from the painted line."""
    c = Canvas(130, 160, ow=3)
    white, sh = (252, 250, 244), (210, 206, 226)
    pts = [(10, 6), (120, 6), (122, 60), (118, 110), (124, 152), (100, 146), (78, 154), (54, 146), (30, 154),
           (8, 148), (12, 100), (6, 50)]

    def folds(p):
        for x in (34, 64, 96):
            p.line(bez((x, 10), (x + 6, 80), (x - 4, 150)), 3, sh)
        p.rect(0, 22, 140, 30, (170, 210, 240))  # blue stripe hem near the top
    c.paint(poly(pts, 1), white, pattern=folds, shade=(4, 0, sh), hi=(-3, 0, (255, 255, 255)))
    for x in (24, 66, 108):
        c.paint(rrect(x - 4, 0, x + 4, 16, 2), (190, 140, 90), ow=2.2)
    c.save("hs_bedsheet.png")


ASSETS = {"hs_tess_calloway": paint_tess, "hs_chad_thunderclap": paint_chad, "hs_dolly_spark": paint_dolly,
          "hs_fernanda": paint_fernanda, "hs_bedsheet": paint_bedsheet}



# =========================================================================== scenery helpers
def night_sky(c, y1, seed=1):
    rng = random.Random(seed)
    c.paint(rect(0, 0, W_BG, y1), ("vy", 0, y1, (26, 22, 72), (150, 66, 128)), ow=0)
    for _ in range(140):
        x, y = rng.uniform(0, W_BG), rng.uniform(0, y1 * 0.6)
        r = rng.choice([1.2, 1.6, 2.2])
        c.paint(ell(x, y, r, r), (255, 250, 220), ow=0, opacity=rng.uniform(0.5, 1))
    c.paint(ell(1560, 110, 46, 46), (255, 246, 200), ow=4, hi=(-4, -4, (255, 255, 240), 4))
    c.paint(ell(1578, 98, 40, 40), (34, 28, 82), ow=0, opacity=0.0)
    for cx, cy, r in ((1546, 100, 8), (1574, 126, 6), (1550, 132, 4)):
        c.paint(ell(cx, cy, r, r), (236, 220, 170), ow=0, opacity=0.7)


def trees(c, y, seed=2):
    rng = random.Random(seed)
    x = -60
    while x < W_BG + 60:
        r = rng.uniform(60, 110)
        col = (40, 34, 74)
        c.paint(cap([(x, y), (x, y - 60)], 14), (34, 26, 50), ow=0)
        c.paint(poly(paint.ell_pts(x, y - 60 - r * 0.6, r, r * 0.85), 2, True), col, ow=0)
        x += rng.uniform(110, 190)


def clapboard(c, x0, y0, x1, y1, col, step=22):
    c.paint(rect(x0, y0, x1, y1), ("vy", y0, y1, lt(col, 0.1), dk(col, 0.88)), shade=(-6, 0, dk(col, 0.8)),
            pattern=lambda p: [p.line([(x0, y), (x1, y)], 2.2, dk(col, 0.72)) for y in range(int(y0) + step, int(y1), step)])


def lit_window(c, x0, y0, x1, y1, glass=(255, 214, 120), frame=(250, 246, 236), shutters=None, curtain_c=None):
    if shutters:
        c.paint(rect(x0 - 26, y0, x0 - 6, y1), shutters, ow=3, pattern=lambda p: [
            p.line([(x0 - 24, y), (x0 - 8, y)], 1.6, dk(shutters, 0.7)) for y in range(int(y0) + 8, int(y1), 10)])
        c.paint(rect(x1 + 6, y0, x1 + 26, y1), shutters, ow=3, pattern=lambda p: [
            p.line([(x1 + 8, y), (x1 + 24, y)], 1.6, dk(shutters, 0.7)) for y in range(int(y0) + 8, int(y1), 10)])
    c.paint(rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), frame, shade=(-3, -3, dk(frame, 0.8)))

    def inner(p):
        if curtain_c:
            p.poly([(x0, y0), (x0 + (x1 - x0) * 0.3, y0), (x0 + 8, y1)], curtain_c)
            p.poly([(x1, y0), (x1 - (x1 - x0) * 0.3, y0), (x1 - 8, y1)], curtain_c)
    c.paint(rect(x0, y0, x1, y1), ("v", lt(glass, 0.3), glass), ow=3, pattern=inner)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    c.paint(rect(mx - 4, y0, mx + 4, y1), frame, ow=2.5)
    c.paint(rect(x0, my - 4, x1, my + 4), frame, ow=2.5)


def column(c, x, y0, y1, w=30, col=(250, 246, 236)):
    c.paint(rect(x - w / 2, y0 + 14, x + w / 2, y1 - 12), col, shade=(-6, 0, dk(col, 0.8)), hi=(5, 0, (255, 255, 250)),
            pattern=lambda p: [p.line([(x + k, y0 + 18), (x + k, y1 - 16)], 1.4, dk(col, 0.82)) for k in (-7, 0, 7)])
    c.paint(rect(x - w / 2 - 7, y0, x + w / 2 + 7, y0 + 14), col, shade=(0, -4, dk(col, 0.8)))
    c.paint(rect(x - w / 2 - 7, y1 - 12, x + w / 2 + 7, y1), col, shade=(0, -4, dk(col, 0.8)))


def pavers(c, base, y0=WALL_Y):
    c.paint(rect(0, y0, W_BG, H_BG), ("vy", y0, H_BG, lt(base, 0.1), dk(base, 0.85)), ow=0)
    vp = (960, 300)
    rows = [y0 + (H_BG - y0) * ((i / 7) ** 1.45) for i in range(8)]
    for y in rows[1:]:
        c.line([(0, y), (W_BG, y)], 2, dk(base, 0.6), opacity=0.5)
    for ri in range(7):
        ya, yb = rows[ri], rows[ri + 1]
        off = 70 * (ri % 2)
        for xb in range(-2400, W_BG + 2400, 140):
            def X(y):
                return vp[0] + (xb + off - vp[0]) * (y - vp[1]) / (H_BG - vp[1])
            if -20 < X(ya) < W_BG + 20:
                c.line([(X(ya), ya), (X(yb), yb)], 2, dk(base, 0.6), opacity=0.5)
    c.paint(rect(0, y0, W_BG, y0 + 10), dk(base, 0.7), ow=0, opacity=0.6)  # curb shadow


def lamp_post(c, x, top, base=WALL_Y, col=(50, 46, 70)):
    c.paint(rect(x - 6, top + 30, x + 6, base), col, shade=(-3, 0))
    c.paint(rect(x - 14, base - 18, x + 14, base), col, shade=(-3, 0))
    c.paint(poly([(x - 18, top + 30), (x + 18, top + 30), (x + 12, top), (x - 12, top)]), (255, 236, 160), ow=3)
    c.paint(poly([(x - 22, top), (x + 22, top), (x, top - 16)]), col, ow=3)
    c.paint(rect(x - 20, top + 28, x + 20, top + 34), col, ow=2.5)


def sign_text(c, x, y, s, size, col, stroke=0, kind="Black", sc=OUT):
    c.text(x, y, s, size, col, kind, stroke=stroke, sc=sc)


# =========================================================================== Greek Row
def paint_greek_row():
    R = "greek_row"
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(22)
    night_sky(c, WALL_Y, seed=3)
    trees(c, 640, seed=5)
    # lawn strip behind the sidewalk
    c.paint(rect(0, 660, W_BG, WALL_Y), ("vy", 660, WALL_Y, (70, 140, 80), (46, 110, 64)), ow=0)
    pavers(c, (176, 150, 150))

    # ---- campus path + signpost (exit, left edge)
    bx0, by0, bx1, by1 = box(R, "To campus")
    lamp_post(c, bx0 + 34, by0 - 40, by1 - 10)
    c.paint(rect(bx1 - 40, by0 + 70, bx1 - 30, by1 - 8), (130, 84, 50), shade=(-3, 0))
    c.paint(poly([(bx0 + 8, by0 + 100), (bx1 - 6, by0 + 92), (bx1 - 6, by0 + 132), (bx0 + 8, by0 + 138),
                  (bx0 - 6, by0 + 118)], 1), (240, 196, 80), shade=(0, -4, (200, 150, 50)))
    c.text(bx0 + 66, by0 + 116, "CAMPUS", 15, (90, 40, 30))
    c.paint(ell(bx0 + 60, by1 - 30, 70, 34), (50, 120, 64), shade=(-5, -5, (36, 90, 50)),
            hi=(4, 4, (90, 170, 90), 3))  # hedge

    # ---- clothesline (the bedsheet itself is its own sprite, hung from this line)
    sx0, sy0, sx1, sy1 = box(R, "Bedsheet")
    line_y = sy0 + 4
    p0, p1 = sx0 - 30, 372
    for px in (p0, p1):
        c.paint(rect(px - 6, line_y - 20, px + 6, WALL_Y - 6), (196, 150, 100), shade=(-3, 0, (150, 104, 70)))
        c.paint(rect(px - 22, line_y - 26, px + 22, line_y - 16), (196, 150, 100), ow=3)
    c.line([(p0 - 18, line_y - 20), (p1 + 18, line_y - 20)], 2.2, (230, 230, 230))
    c.line([(p0, line_y), (p1, line_y)], 2.5, (236, 236, 236))
    # monogrammed towels + a pink sock
    for tx, col in ((sx1 + 8, (255, 160, 190)),):
        c.paint(wonky(tx, line_y, tx + 44, line_y + 74, 2, rng), col, shade=(3, 0, dk(col, 0.8)))
        c.text(tx + 22, line_y + 40, "TC", 14, (255, 250, 250), "Italic")
        c.paint(rrect(tx + 18, line_y - 6, tx + 26, line_y + 8, 2), (190, 140, 90), ow=2)
    c.paint(poly([(352, line_y), (364, line_y), (364, line_y + 30), (372, line_y + 40), (352, line_y + 40)], 1),
            (255, 120, 170), ow=3)

    # ---- sorority house
    pink = (255, 168, 196)
    hx0, hx1, htop = 400, 950, 340
    clapboard(c, hx0, htop, hx1, WALL_Y, pink)
    c.paint(poly([(hx0 - 40, htop + 6), ((hx0 + hx1) / 2, 196), (hx1 + 40, htop + 6)]), (130, 60, 96),
            shade=(0, -6, (96, 40, 72)))
    c.paint(poly([(hx0 + 50, htop - 8), ((hx0 + hx1) / 2, 222), (hx1 - 50, htop - 8)]), (250, 244, 236),
            shade=(0, -5, (214, 206, 214)))
    c.text((hx0 + hx1) / 2, 302, "ΦΛΑ", 40, (230, 170, 60), stroke=2)
    lit_window(c, 470, 380, 560, 470, shutters=(214, 70, 120), curtain_c=(255, 120, 170))
    lit_window(c, 790, 380, 880, 470, shutters=(214, 70, 120), curtain_c=(255, 120, 170))
    lit_window(c, 760, 540, 880, 660, shutters=(214, 70, 120), curtain_c=(255, 120, 170))
    # front door with fanlight
    dx0, dx1 = 520, 600
    c.paint(ell((dx0 + dx1) / 2, 552, 46, 30), (250, 244, 236), shade=(-3, -3))
    c.paint(ell((dx0 + dx1) / 2, 552, 36, 22), (255, 214, 120), ow=3)
    paint.door(c, dx0, 556, dx1, 740, (214, 60, 110), knob="R", casing=(250, 244, 236))
    c.paint(ell(dx0 + 40, 600, 16, 16), (60, 150, 80), ow=3, pattern=lambda p: [
        p.ell(dx0 + 40, 600, 10, 10, (214, 60, 110))])  # wreath
    # porch: floor, railing, columns
    c.paint(rect(hx0 - 10, 736, hx1 + 10, 760), (250, 244, 236), shade=(0, -5, (214, 206, 214)))
    for x0, x1 in ((hx0 + 10, 500), (640, hx1 - 10)):
        c.paint(rect(x0, 680, x1, 690), (250, 244, 236), ow=3)
        for x in range(int(x0) + 12, int(x1), 18):
            c.paint(rect(x - 3, 690, x + 3, 736), (250, 244, 236), ow=2)
    for x in (430, 500, 640, 920):
        column(c, x, 352, 738, 28)
    c.paint(rect(hx0 - 10, 336, hx1 + 10, 356), (250, 244, 236), shade=(0, -4, (214, 206, 214)))
    for k, y in enumerate((760, 775)):
        c.paint(rect(530 - k * 10, y, 610 + k * 10, y + 15), (240, 230, 222), shade=(0, -4, (200, 190, 200)))
    # hedges
    for hx, hw in ((690, 52), (930, 40)):
        c.paint(ell(hx, 760, hw, 30), (50, 120, 64), shade=(-5, -5, (36, 90, 50)), hi=(4, 4, (90, 170, 90), 3))
    # Fernanda's stand + plaque (she stands here again once she is home)
    fx0, fy0, fx1, fy1 = box(R, "Flamingo stand")
    fcx = (fx0 + fx1) / 2
    c.shadow(fcx, fy1 - 4, 46, 8)
    c.paint(ell(fcx, fy1 - 12, 42, 11), (200, 196, 206), shade=(0, -4, (150, 146, 170)))
    c.paint(rect(fcx - 34, fy1 - 46, fcx + 34, fy1 - 12), (220, 216, 226), shade=(-4, 0, (170, 166, 190)))
    c.paint(ell(fcx, fy1 - 46, 34, 8), (236, 232, 240), ow=3)
    c.paint(rrect(fcx - 26, fy1 - 38, fcx + 26, fy1 - 20, 3), (230, 180, 70), ow=2.5, hi=(0, 2, (255, 226, 140)))
    c.text(fcx, fy1 - 29, "FERNANDA", 8, (90, 50, 20))
    for dx in (-8, 8):
        c.paint(ell(fcx + dx, fy1 - 47, 4, 2), (255, 140, 180), ow=1.5)

    # ---- frat house (brick)
    fr0, fr1, ftop = 1190, 1710, 330
    paint.block_wall(c, fr0, ftop, fr1, WALL_Y, (178, 84, 62), (140, 60, 50), bw=60, bh=26, mortar=0.35, seed=8)
    c.paint(rect(fr0, ftop, fr1, WALL_Y), (0, 0, 0, 0), ow=4)
    c.paint(poly([(fr0 - 40, ftop + 6), ((fr0 + fr1) / 2, 186), (fr1 + 40, ftop + 6)]), (60, 50, 70),
            shade=(0, -6, (40, 34, 50)))
    c.paint(poly([(fr0 + 60, ftop - 8), ((fr0 + fr1) / 2, 212), (fr1 - 60, ftop - 8)]), (236, 226, 206),
            shade=(0, -5, (200, 190, 180)))
    c.text((fr0 + fr1) / 2, 294, "ΘΗΚ", 40, (60, 90, 170), stroke=2)
    party = [(255, 80, 200), (80, 220, 255), (255, 220, 80)]
    lit_window(c, 1225, 380, 1295, 460, glass=party[0])
    lit_window(c, 1600, 380, 1670, 460, glass=party[1])
    lit_window(c, 1530, 560, 1650, 660, glass=party[2])
    # bedsheet banner
    ban = wonky(1500, 476, 1690, 536, 4, rng)
    c.paint(ban, (250, 248, 238), shade=(3, 0, (210, 206, 226)))
    c.text(1595, 494, "TOGA PARTY", 17, (220, 40, 60), "Italic")
    c.text(1595, 518, "TONITE!!", 15, (40, 90, 200), "Italic")
    # double door
    ddx0, ddy0, ddx1, ddy1 = box(R, "Frat house door")
    c.paint(rect(ddx0 - 16, ddy0 - 16, ddx1 + 16, ddy1), (236, 226, 206), shade=(-4, 0, (200, 190, 180)))
    for a, b, kn in ((ddx0, (ddx0 + ddx1) / 2, "R"), ((ddx0 + ddx1) / 2, ddx1, "L")):
        paint.door(c, a, ddy0, b, ddy1, (110, 60, 36), knob=kn, casing=(110, 60, 36))
    c.paint(rect(ddx0, ddy0 + 30, ddx1, ddy0 + 50), (230, 180, 60), ow=2.5)
    c.text((ddx0 + ddx1) / 2, ddy0 + 40, "NO TOGA NO ENTRY", 8, (60, 30, 20))
    for x in (ddx0 - 44, ddx1 + 44):
        column(c, x, 352, ddy1, 30, (236, 226, 206))
    c.paint(rect(ddx0 - 70, 336, ddx1 + 70, 356), (236, 226, 206), shade=(0, -4, (200, 190, 180)))
    for k, y in enumerate((ddy1 - 12, ddy1 + 2)):
        c.paint(rect(ddx0 - 20 - k * 12, y, ddx1 + 20 + k * 12, y + 14), (200, 196, 190), shade=(0, -4))
    # red cups on the lawn
    for cx_, cy_ in ((1240, 778), (1690, 770)):
        c.paint(poly([(cx_ - 8, cy_), (cx_ + 8, cy_ - 4), (cx_ + 10, cy_ + 8), (cx_ - 8, cy_ + 10)], 1),
                (220, 40, 50), ow=2.5)

    # ---- quiz podium + Speed Daters Live sign between the houses
    c.paint(rect(1000, 430, 1012, WALL_Y), (60, 50, 70), shade=(-3, 0))
    c.paint(rect(1158, 430, 1170, WALL_Y), (60, 50, 70), shade=(-3, 0))
    c.paint(rrect(980, 360, 1190, 440, 12), (110, 30, 120), shade=(-5, -5, (70, 20, 90)),
            hi=(4, 4, (170, 70, 180), 3))
    for k in range(18):
        a = k / 18
        x = 990 + 190 * a
        c.paint(ell(x, 366, 4, 4), (255, 230, 120), ow=1.6)
        c.paint(ell(x, 434, 4, 4), (255, 230, 120), ow=1.6)
    c.text(1085, 388, "SPEED DATERS", 20, (255, 226, 80), stroke=2)
    c.text(1085, 416, "LIVE!", 20, (255, 120, 200), "Italic", stroke=2)
    px0, py0, px1, py1 = box(R, "Quiz podium")
    pcx = (px0 + px1) / 2
    c.shadow(pcx, py1 - 2, 60, 9, 0.5)
    pod = poly([(px0 + 6, py0 + 30), (px1 - 6, py0 + 30), (px1 - 14, py1 - 6), (px0 + 14, py1 - 6)])
    c.paint(pod, (150, 50, 170), shade=(-6, 0, (100, 30, 130)), hi=(5, 0, (200, 110, 220)),
            pattern=lambda p: [p.ell(pcx + 30 * math.cos(k), py0 + 80 + 30 * math.sin(k * 1.7), 2, 2, (255, 230, 150))
                               for k in range(14)])
    c.paint(rect(px0, py0 + 20, px1, py0 + 34), (230, 180, 60), shade=(0, -4, (190, 130, 40)))
    c.paint(paint.Sh([paint.ell_pts(pcx, py0 + 74, 22, 22)]), (255, 214, 60), ow=3)
    c.text(pcx, py0 + 74, "?", 26, (150, 50, 170))
    c.text(pcx, py1 - 26, "QUIZ", 15, (255, 240, 200), stroke=1.5)
    c.paint(ell(pcx, py0 + 20, 18, 14), (230, 40, 50), shade=(3, 3, (170, 20, 40)), hi=(-3, -3, (255, 140, 130), 2))
    c.paint(rect(pcx - 22, py0 + 16, pcx + 22, py0 + 22), (60, 60, 70), ow=2.5)
    # GREEK WEEK bunting across the gap
    paint.bunting(c, 940, 1220, 250, list("GREEK"), [(230, 60, 120), (60, 170, 220), (250, 190, 50), (130, 80, 200),
                                                     (60, 180, 110)], sag=16)
    lamp_post(c, 1186, 470)

    # ---- Fuse Box bar (right edge)
    bx0, by0, bx1, by1 = box(R, "Fuse Box bar")
    paint.block_wall(c, bx0 - 26, 380, W_BG + 10, WALL_Y, (70, 56, 90), (50, 40, 66), bw=50, bh=24, mortar=0.4, seed=4)
    c.paint(rect(bx0 - 26, 380, W_BG + 10, WALL_Y), (0, 0, 0, 0), ow=4)
    c.paint(rect(bx0 - 36, 370, W_BG + 10, 392), (40, 34, 50), ow=3)
    c.paint(rrect(bx0 + 4, by0 + 6, bx1 - 4, by0 + 66, 8), (30, 26, 40), shade=(-3, -3))
    c.text((bx0 + bx1) / 2, by0 + 26, "FUSE", 22, (30, 26, 40), stroke=2, sc=(120, 116, 130))
    c.text((bx0 + bx1) / 2, by0 + 52, "BOX", 22, (30, 26, 40), stroke=2, sc=(120, 116, 130))
    c.paint(poly([(bx1 - 30, by0 + 10), (bx1 - 40, by0 + 32), (bx1 - 30, by0 + 32), (bx1 - 38, by0 + 58)]),
            (0, 0, 0, 0), ow=2, oc=(120, 116, 130))
    paint.door(c, bx0 + 30, by0 + 96, bx1 - 30, by1 - 8, (60, 40, 90), knob="L", panels=False, casing=(40, 34, 50))
    c.paint(ell((bx0 + bx1) / 2, by0 + 150, 22, 22), (240, 200, 120), ow=4, pattern=lambda p: p.ell(
        (bx0 + bx1) / 2, by0 + 150, 16, 16, (255, 220, 150)))  # porthole, candle glow
    c.paint(rect(bx0 + 40, by0 + 196, bx1 - 40, by0 + 226), (250, 246, 236), ow=2.5, opacity=0.95)
    c.text((bx0 + bx1) / 2, by0 + 211, "OPEN*", 10, (60, 40, 90))

    lights = [(515, 425, 180, 0.4, (255, 200, 120)), (835, 425, 180, 0.4, (255, 200, 120)),
              (820, 600, 200, 0.4, (255, 200, 120)), (560, 552, 120, 0.4, (255, 214, 120)),
              (1260, 420, 160, 0.4, party[0]), (1635, 420, 160, 0.4, party[1]), (1590, 610, 200, 0.45, party[2]),
              (1186, 470, 360, 0.5, (255, 236, 170)), (74, 380, 340, 0.45, (255, 236, 170)),
              (1085, 600, 420, 0.45, (255, 150, 220)), (1820, 650, 120, 0.3, (255, 200, 120))]
    paint.light_pass(c, 0.66, lights, vign=0.45)
    c.glow(1186, 490, 110, (255, 236, 170), 0.55)
    c.glow(74, 360, 110, (255, 236, 170), 0.55)
    c.glow(1085, 400, 160, (255, 120, 200), 0.3)
    c.save("bg_greek_row.png")


# =========================================================================== frat house interior
def paint_frat_house():
    R = "frat_house"
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(1912)
    wall = (140, 40, 50)
    c.paint(rect(0, 0, W_BG, 560), ("vy", 60, 560, dk(wall, 0.7), wall), ow=0,
            pattern=lambda p: [p.rect(x, 0, x + 22, 560, dk(wall, 0.86)) for x in range(0, W_BG, 64)])
    wood = (120, 70, 40)
    c.paint(rect(0, 560, W_BG, WALL_Y), ("vy", 560, WALL_Y, wood, dk(wood, 0.8)), ow=0,
            pattern=lambda p: [p.line([(x, 572), (x, WALL_Y)], 3, dk(wood, 0.6)) for x in range(0, W_BG, 96)])
    c.paint(rect(-10, 552, W_BG + 10, 572), lt(wood, 0.2), ow=3, shade=(0, -4))
    c.paint(rect(0, 0, W_BG, 50), (50, 30, 34), ow=0)
    c.paint(rect(-10, 46, W_BG + 10, 60), (170, 110, 60), ow=3)
    paint.plank_floor(c, (140, 80, 44), seed=31)
    paint.baseboard(c, color=(70, 40, 26))

    # dance floor tiles (flat, on the floor)
    dx0, dy0, dx1, dy1 = box(R, "Dance floor")
    cols = [(255, 80, 200), (80, 220, 255), (255, 220, 80), (120, 255, 140)]
    for r in range(3):
        for k in range(7):
            y0 = WALL_Y + 6 + r * 30
            x0 = dx0 - 70 + k * 70 - r * 14
            c.paint(poly([(x0, y0), (x0 + 66, y0), (x0 + 66 - 4, y0 + 28), (x0 - 4, y0 + 28)]),
                    cols[(r + k) % 4], ow=2.5, opacity=0.85)
    # TOGA banner
    ban = wonky(260, 120, 1060, 210, 5, rng)
    c.paint(ban, (250, 248, 238), shade=(4, 0, (210, 206, 226)))
    c.text(660, 166, "TOGA!  TOGA!  TOGA!", 46, (220, 40, 60), "Italic", stroke=2)
    # window
    paint.night_window(c, 1730, 260, 1880, 460, seed=17)
    # big wooden paddle
    c.paint(poly([(1260, 250), (1340, 250), (1350, 380), (1310, 400), (1250, 380)], 1), (196, 130, 70),
            shade=(-5, 0, (150, 96, 50)))
    c.paint(rect(1288, 400, 1312, 470), (196, 130, 70), shade=(-3, 0, (150, 96, 50)))
    c.text(1300, 320, "ΘΗΚ", 26, (110, 40, 30))

    # front door (left edge)
    fx0, fy0, fx1, fy1 = box(R, "Front door")
    paint.door(c, fx0 + 14, fy0 + 14, fx1 - 6, fy1 - 10, (110, 60, 36), knob="R")
    c.paint(rrect(fx0 + 34, fy0 + 40, fx1 - 26, fy0 + 70, 4), (236, 226, 206), ow=2.5)
    c.text((fx0 + fx1) / 2 + 4, fy0 + 55, "EXIT", 12, (120, 30, 30))

    # keg on ice
    kx0, ky0, kx1, ky1 = box(R, "Root beer keg")
    kcx = (kx0 + kx1) / 2
    c.shadow(kcx, ky1 - 4, 56, 9, 0.5)
    # keg first (it stands in the tub), then the tub, ice and label on top
    c.paint(rrect(kx0 + 20, ky0 + 22, kx1 - 20, ky1 - 26, 10), (200, 206, 214), shade=(-6, 0, (140, 146, 160)),
            hi=(5, 0, (240, 244, 250)), pattern=lambda p: [p.line([(kx0 + 18, y), (kx1 - 18, y)], 3, (150, 156, 170))
                                                         for y in (ky0 + 34, ky0 + 82)])
    c.paint(rect(kcx - 6, ky0 + 6, kcx + 6, ky0 + 24), (80, 80, 90), ow=2.5)
    c.line([(kcx + 6, ky0 + 12), (kcx + 24, ky0 + 18), (kcx + 30, ky0 + 40)], 3.5, (40, 40, 50))
    c.paint(rect(kx0 + 24, ky0 + 44, kx1 - 24, ky0 + 76), (250, 240, 200), ow=2.5)
    c.text(kcx, ky0 + 53, "THE HARD", 7.5, (140, 40, 30))
    c.text(kcx, ky0 + 67, "STUFF", 10, (140, 40, 30))
    tub = poly([(kx0 + 2, ky1 - 44), (kx1 - 2, ky1 - 44), (kx1 - 10, ky1 - 4), (kx0 + 10, ky1 - 4)], 1)
    for ix in range(5):
        c.paint(rrect(kx0 + 6 + ix * 17, ky1 - 54 + (ix % 2) * 4, kx0 + 20 + ix * 17, ky1 - 42 + (ix % 2) * 4, 3),
                (220, 240, 255), ow=2)
    c.paint(tub, (90, 120, 200), shade=(-5, 0, (60, 80, 150)), hi=(4, 0, (150, 180, 240)))
    for k in range(3):
        c.paint(poly([(kx1 + 4, ky1 - 6 - k * 16), (kx1 + 22, ky1 - 6 - k * 16), (kx1 + 24, ky1 - 22 - k * 16),
                      (kx1 + 2, ky1 - 22 - k * 16)]), (220, 40, 50), ow=2.5)

    # frat composite photos
    px0, py0, px1, py1 = box(R, "Frat photos")
    for r in range(2):
        for k in range(3):
            x0 = px0 + 8 + k * 64
            y0 = py0 + 6 + r * 66
            c.paint(rect(x0, y0, x0 + 56, y0 + 56), (60, 40, 30), shade=(-3, -3), hi=(2, 2, (110, 80, 50)))
            c.paint(rect(x0 + 6, y0 + 6, x0 + 50, y0 + 50), (210, 196, 160), ow=2,
                    pattern=lambda p, x0=x0, y0=y0: [
                        (p.ell(x0 + 12 + j * 10, y0 + 22 + (j % 2) * 10, 3.5, 3.5, (110, 90, 70)),
                         p.rect(x0 + 8 + j * 10, y0 + 28 + (j % 2) * 10, x0 + 16 + j * 10, y0 + 50, (250, 248, 240)))
                        for j in range(4)])
            c.text(x0 + 28, y0 + 52, str(1912 + (r * 3 + k) * 19), 6, (60, 40, 30), "Bold")

    # spotlight on Fernanda (her sprite stands here; when she's gone the light hits an empty floor)
    ex0, ey0, ex1, ey1 = box(R, "Fernanda")
    ecx = (ex0 + ex1) / 2
    c.paint(rrect(ecx - 30, 52, ecx + 30, 80, 6), (50, 50, 60), ow=3)
    c.paint(ell(ecx, ey1 - 6, 90, 18), (40, 30, 30), ow=0, opacity=0.4)
    c.paint(rect(ecx - 70, ey1 - 26, ecx + 70, ey1 - 4), (40, 24, 60), ow=3)  # little stage
    c.paint(rect(ecx - 70, ey1 - 26, ecx + 70, ey1 - 20), (220, 180, 60), ow=0)
    for sx in (ecx - 110, ecx + 110):  # velvet rope posts
        c.paint(rect(sx - 5, ey1 - 70, sx + 5, ey1 - 4), (230, 180, 60), ow=2.5)
        c.paint(ell(sx, ey1 - 72, 8, 8), (230, 180, 60), ow=2.5)
    c.curve((ecx - 110, ey1 - 64), (ecx - 90, ey1 - 30), (ecx - 70, ey1 - 40), 5, (180, 30, 60))
    c.curve((ecx + 70, ey1 - 40), (ecx + 90, ey1 - 30), (ecx + 110, ey1 - 64), 5, (180, 30, 60))

    # dancers in togas (silhouettes) + disco ball
    for i, (x, h, arms) in enumerate(((dx0 + 30, 190, 1), (dx0 + 100, 214, -1), (dx0 + 170, 200, 1),
                                      (dx0 + 240, 186, 0), (dx0 + 290, 206, -1))):
        sil = (60, 30, 80)
        y1 = dy1 - 4
        c.paint(ell(x, y1 - h + 18, 17, 19) + poly([(x - 22, y1 - h + 40), (x + 22, y1 - h + 40), (x + 18, y1 - 50),
                                                       (x - 18, y1 - 50)], 1) +
                cap([(x - 8, y1 - 50), (x - 10, y1)], 11) + cap([(x + 8, y1 - 50), (x + 12, y1)], 11), sil,
                shade=(4, 0, (40, 20, 60)))
        c.paint(poly([(x - 20, y1 - h + 44), (x + 4, y1 - h + 40), (x + 18, y1 - 60), (x - 16, y1 - 54)], 1),
                (230, 228, 240), ow=3, shade=(3, 0, (180, 176, 210)))
        if arms:
            c.paint(cap([(x + 16 * arms, y1 - h + 48), (x + 30 * arms, y1 - h + 10), (x + 26 * arms, y1 - h - 14)], 9),
                    sil)
            c.paint(cap([(x - 16 * arms, y1 - h + 48), (x - 34 * arms, y1 - h + 70)], 9), sil)
        else:
            c.paint(cap([(x - 18, y1 - h + 48), (x - 36, y1 - h + 14)], 9) + cap([(x + 18, y1 - h + 48),
                                                                                    (x + 36, y1 - h + 14)], 9), sil)
    bcx = (dx0 + dx1) / 2
    c.line([(bcx, 60), (bcx, 120)], 2.5)
    c.paint(ell(bcx, 150, 32, 32), (200, 206, 220), pattern=lambda p: [
        p.rect(bcx - 32 + i * 10, 118 + j * 10, bcx - 24 + i * 10, 126 + j * 10, rng.choice(
            [(240, 244, 255), (160, 170, 200), (255, 140, 220), (140, 230, 255)])) for i in range(7) for j in range(7)])
    # speakers flanking the dance floor
    for sx in (dx0 - 70, dx1 + 30):
        c.paint(rect(sx, 610, sx + 56, WALL_Y), (40, 36, 46), shade=(-4, 0), pattern=lambda p, sx=sx: [
            p.ell(sx + 28, y, 18, 18, (80, 76, 90)) for y in (650, 720)])
        for y in (650, 720):
            c.paint(ell(sx + 28, y, 9, 9), (30, 26, 34), ow=2)

    # breaker box
    bx0, by0, bx1, by1 = box(R, "Breaker box")
    c.paint(rect(bx0 + 4, by0 + 6, bx1 - 4, by1 - 4), (150, 156, 164), shade=(-4, -4, (110, 114, 124)),
            hi=(3, 3, (196, 200, 208)))
    c.paint(rect(bx0 + 12, by0 + 16, bx1 - 12, by1 - 14), (60, 62, 70), ow=3)
    for k, (fx, fy) in enumerate(((bx0 + 30, by0 + 40), (bx1 - 30, by0 + 40), (bx0 + 30, by0 + 80))):
        c.paint(ell(fx, fy, 11, 11), (200, 150, 80), ow=2.5)
        c.paint(ell(fx, fy, 6, 6), (255, 230, 160), ow=1.6)
    c.paint(ell(bx1 - 30, by0 + 80, 13, 13), (230, 180, 60), ow=3, hi=(-2, -2, (255, 230, 150)))
    c.text(bx1 - 30, by0 + 80, "30", 8, (90, 40, 20))
    c.paint(poly([(bx1 - 4, by0 + 6), (bx1 + 22, by0 + 14), (bx1 + 22, by1 - 10), (bx1 - 4, by1 - 4)]),
            (170, 176, 184), shade=(3, 0))  # open door
    c.paint(rect(bx0 + 20, by0 - 14, bx1 - 20, by0 + 2), (255, 220, 60), ow=2)
    c.text((bx0 + bx1) / 2, by0 - 6, "MAIN", 8, (40, 30, 20))

    lights = [(ecx, ey0 + 60, 330, 0.85, (255, 240, 190)), (bcx, 300, 520, 0.55, (255, 120, 220)),
              (bcx + 150, 700, 380, 0.4, (90, 210, 255)), (1805, 360, 240, 0.25, (150, 150, 255)),
              (660, 160, 500, 0.25, (255, 200, 150))]
    paint.light_pass(c, 0.55, lights, vign=0.5)
    # spotlight cone
    c.paint(poly([(ecx - 22, 80), (ecx + 22, 80), (ecx + 96, ey1 - 6), (ecx - 96, ey1 - 6)]), (255, 246, 200),
            ow=0, opacity=0.16)
    c.glow(ecx, ey1 - 20, 120, (255, 240, 190), 0.35)
    c.glow(bcx, 150, 110, (255, 200, 255), 0.5)
    for k in range(10):
        a = rng.uniform(0, math.tau)
        c.glow(bcx + math.cos(a) * rng.uniform(200, 700), 200 + rng.uniform(0, 400), 20,
               rng.choice(cols), 0.6)
    c.save("bg_frat_house.png")


# =========================================================================== the Fuse Box bar
def paint_fuse_box():
    R = "fuse_box"
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(30)
    paint.block_wall(c, 0, 0, W_BG, WALL_Y, (86, 52, 72), (60, 36, 54), bw=90, bh=40, mortar=0.4, seed=33)
    c.paint(rect(0, 0, W_BG, 46), (30, 22, 34), ow=0)
    c.paint(rect(-10, 40, W_BG + 10, 54), (60, 44, 60), ow=3)
    paint.plank_floor(c, (96, 56, 40), seed=34)
    paint.baseboard(c, color=(40, 26, 30))
    # unlit neon signs
    for (x, y, s, size) in ((1150, 200, "DANCE", 54), (560, 180, "BAR", 44)):
        c.text(x, y, s, size, (50, 40, 60), "Italic", stroke=2.5, sc=(140, 130, 150))
    c.paint(poly([(1360, 150), (1330, 210), (1360, 210), (1326, 270)]), (0, 0, 0, 0), ow=3, oc=(140, 130, 150))
    # unlit string lights
    paint.string_lights(c, [(0, 80), (640, 120), (1280, 80), (1920, 120)], [(120, 110, 130)], sag=20)

    # door (left edge)
    fx0, fy0, fx1, fy1 = box(R, "Door")
    paint.door(c, fx0 + 14, fy0 + 14, fx1 - 6, fy1 - 10, (60, 40, 90), knob="R", panels=False, casing=(40, 30, 40))
    c.paint(ell((fx0 + fx1) / 2 + 4, fy0 + 90, 20, 20), (60, 50, 90), ow=4)

    # back bar shelves + counter
    cx0, cy0, cx1, cy1 = box(R, "Bar counter")
    for y in (380, 470, 560):
        c.paint(rect(cx0 - 10, y, cx1 + 10, y + 12), (130, 80, 44), shade=(0, -4))
        x = cx0
        while x < cx1 - 16:
            h = rng.uniform(40, 70)
            col = rng.choice([(60, 160, 80), (200, 120, 40), (120, 50, 40), (80, 120, 200), (230, 210, 120)])
            sh = poly([(x, y), (x + 18, y), (x + 18, y - h + 22), (x + 12, y - h + 10), (x + 12, y - h),
                       (x + 6, y - h), (x + 6, y - h + 10), (x, y - h + 22)], 1)
            c.paint(sh, col, ow=3, shade=(-3, 0), hi=(3, 0, lt(col, 0.4), 2))
            x += rng.uniform(26, 40)
    c.shadow((cx0 + cx1) / 2, cy1 - 2, (cx1 - cx0) / 2 + 10, 12, 0.5)
    c.paint(rect(cx0 + 10, cy0 + 26, cx1 - 10, cy1 - 6), (110, 60, 36), shade=(-6, 0, (80, 40, 26)),
            pattern=lambda p: [p.line([(x, cy0 + 30), (x, cy1 - 8)], 3, (80, 44, 28)) for x in range(int(cx0) + 50,
                                                                                                     int(cx1), 60)])
    c.paint(wonky(cx0, cy0 + 12, cx1, cy0 + 30, 1.5, rng), (160, 100, 56), hi=(0, 4, (200, 140, 80)), shade=(0, -4))
    # tip jar + candles on the bar
    c.paint(rrect(cx1 - 70, cy0 - 26, cx1 - 40, cy0 + 12, 4), (200, 230, 240, 200), ow=3,
            pattern=lambda p: p.rect(cx1 - 70, cy0, cx1 - 40, cy0 + 12, (120, 190, 110)))
    c.paint(rect(cx1 - 76, cy0 - 40, cx1 - 34, cy0 - 26), (250, 246, 236), ow=2)
    c.text(cx1 - 55, cy0 - 33, "FUSES", 7, (60, 40, 30), "Bold")
    candles = []
    for x in (cx0 + 50, cx0 + 160):
        c.paint(rect(x - 7, cy0 - 18, x + 7, cy0 + 12), (250, 240, 220), ow=3, shade=(-2, 0))
        c.paint(ell(x, cy0 - 26, 5, 9), (255, 200, 80), ow=2, hi=(-1, -1, (255, 250, 200)))
        candles.append((x, cy0 - 26))

    # fuse panel
    px0, py0, px1, py1 = box(R, "Fuse panel")
    pcx = (px0 + px1) / 2
    c.paint(rect(px0 + 4, py0 + 8, px1 - 4, py1 - 4), (150, 156, 164), shade=(-4, -4, (110, 114, 124)),
            hi=(3, 3, (196, 200, 208)))
    c.paint(rect(px0 + 14, py0 + 22, px1 - 14, py1 - 16), (60, 62, 70), ow=3)
    c.paint(ell(pcx, (py0 + py1) / 2 + 4, 15, 15), (40, 36, 40), ow=3)
    c.paint(ell(pcx, (py0 + py1) / 2 + 4, 9, 9), (20, 18, 20), ow=1.5)
    c.paint(ell(pcx - 4, (py0 + py1) / 2, 4, 3), (90, 80, 70), ow=0, opacity=0.6)
    c.paint(rect(px0 + 20, py0 - 6, px1 - 20, py0 + 10), (255, 220, 60), ow=2)
    c.text(pcx, py0 + 2, "30A", 8, (40, 30, 20))
    c.line([(pcx, py1 - 4), (pcx + 6, py1 + 40), (pcx - 10, WALL_Y - 20)], 3, (30, 26, 34))

    # request chalkboard
    bx0, by0, bx1, by1 = box(R, "Request board")
    c.paint(rect(bx0, by0, bx1, by1), (130, 84, 46), shade=(-5, -5), hi=(3, 3, (180, 120, 70)))
    c.paint(rect(bx0 + 10, by0 + 10, bx1 - 10, by1 - 10), (40, 60, 50), ow=3)
    bcx = (bx0 + bx1) / 2
    chalk = (236, 240, 230)
    c.text(bcx, by0 + 30, "DJ DOLLY", 14, (255, 170, 210), "Bold")
    c.text(bcx, by0 + 48, "SPARK", 14, (255, 170, 210), "Bold")
    c.text(bcx, by0 + 66, "tonight!", 11, chalk, "Semi")
    c.line([(bx0 + 24, by0 + 80), (bx1 - 24, by0 + 80)], 1.6, chalk)
    c.text(bcx, by0 + 96, "Dolly's #1:", 10, chalk, "Semi")
    c.text(bcx, by0 + 116, "DISCO", 15, (255, 210, 90), "Black")
    c.text(bcx, by0 + 134, "VOLCANO", 15, (255, 140, 60), "Black")
    c.text(bcx, by0 + 156, "TOGA TOGA TOGA", 8, chalk, "Semi")
    c.line([(bx0 + 22, by0 + 156), (bx1 - 22, by0 + 154)], 2, (255, 120, 120))

    # DJ booth
    jx0, jy0, jx1, jy1 = box(R, "DJ booth")
    c.shadow((jx0 + jx1) / 2, jy1 - 2, (jx1 - jx0) / 2 + 10, 12, 0.5)
    c.paint(rect(jx0 + 6, jy0 + 34, jx1 - 6, jy1 - 6), (90, 40, 130), shade=(-6, 0, (60, 26, 96)),
            pattern=lambda p: [p.ell(rng.uniform(jx0, jx1), rng.uniform(jy0 + 40, jy1), 2, 2, (255, 210, 255))
                               for _ in range(40)])
    c.text((jx0 + jx1) / 2, (jy0 + jy1) / 2 + 24, "DJ DOLLY", 20, (255, 120, 200), "Italic", stroke=2)
    c.paint(rect(jx0, jy0 + 24, jx1, jy0 + 40), (40, 36, 50), ow=3)
    for tx in (jx0 + 50, jx1 - 50):
        c.paint(ell(tx, jy0 + 22, 38, 9), (30, 28, 36), ow=3)
        c.paint(ell(tx, jy0 + 20, 30, 7), (20, 18, 24), ow=1.5, pattern=lambda p, tx=tx: p.ell(tx, jy0 + 20, 8, 2,
                                                                                            (255, 90, 170)))
    lx = (jx0 + jx1) / 2
    c.paint(poly([(lx - 26, jy0 + 22), (lx + 26, jy0 + 22), (lx + 30, jy0 - 14), (lx - 22, jy0 - 14)]),
            (200, 206, 214), shade=(-3, 0), pattern=lambda p: [
                p.ell(lx - 14 + k * 9, jy0 - 2 + (k % 2) * 8, 4, 4, ((255, 90, 170), (60, 220, 210), (255, 214, 60))[k % 3])
                for k in range(5)])

    # Big Bertha amp
    ax0, ay0, ax1, ay1 = box(R, "Big Bertha")
    c.shadow((ax0 + ax1) / 2, ay1 - 2, (ax1 - ax0) / 2 + 8, 10, 0.5)
    c.paint(rrect(ax0 + 6, ay0 + 10, ax1 - 6, ay1 - 6, 8), (36, 32, 40), shade=(-6, 0, (24, 20, 28)),
            hi=(4, 0, (70, 64, 80)))
    c.paint(rect(ax0 + 18, ay0 + 22, ax1 - 18, ay0 + 54), (220, 210, 190), ow=3)
    c.text((ax0 + ax1) / 2, ay0 + 38, "BIG BERTHA", 14, (200, 40, 70))
    for k in range(6):
        c.paint(ell(ax0 + 30 + k * 20, ay0 + 70, 5, 5), (220, 200, 120), ow=2)
    for y in (ay0 + 140, ay0 + 230):
        c.paint(ell((ax0 + ax1) / 2, y, 52, 40), (60, 56, 66), ow=3, pattern=lambda p, y=y: [
            p.ell((ax0 + ax1) / 2, y, r, r * 0.77, (50, 46, 56) if r % 16 else (76, 72, 84)) for r in range(48, 8, -8)])
        c.paint(ell((ax0 + ax1) / 2, y, 14, 11), (30, 28, 34), ow=2.5)
    c.curve((ax0 + 10, ay1 - 30), (ax0 - 120, ay1 + 10), (jx1 - 10, jy1 - 30), 4, (30, 26, 34))

    lights = [(x, y, 230, 0.75, (255, 180, 90)) for x, y in candles] + \
             [(1000, 300, 900, 0.18, (200, 120, 255)), ((bx0 + bx1) / 2, 540, 220, 0.3, (255, 200, 140))]
    paint.light_pass(c, 0.6, lights, vign=0.45)
    for x, y in candles:
        c.glow(x, y, 50, (255, 200, 90), 0.6)
    c.save("bg_fuse_box.png")


# =========================================================================== icons (128x128)
icon = paint.icon


def paint_icon_bedsheet():
    def draw(c):
        white, sh = (252, 250, 244), (210, 206, 226)
        for k, y in enumerate((88, 64, 40)):
            c.paint(poly([(20 + k * 4, y), (108 - k * 4, y - 4), (110 - k * 4, y + 22), (18 + k * 4, y + 26)], 1),
                    white, shade=(0, -4, sh), hi=(0, 3, (255, 255, 255)),
                    pattern=lambda p, y=y: p.rect(0, y + 8, 128, y + 12, (170, 210, 240)))
    icon("icon_bedsheet.png", -6, draw)


def paint_icon_safety_pin():
    def draw(c):
        silver, sh = (210, 216, 226), (140, 146, 166)
        c.paint(cap([(30, 96), (98, 30)], 7), silver, shade=(2, 2, sh))
        c.paint(cap([(36, 104), (104, 38)], 7), silver, shade=(2, 2, sh))
        c.paint(ell(28, 102, 14, 14), (0, 0, 0, 0), ow=5)
        c.paint(ell(28, 102, 14, 14), (0, 0, 0, 0), ow=3, oc=silver)
        c.paint(rrect(88, 18, 114, 44, 6), (240, 196, 80), shade=(2, 2, (200, 150, 50)), hi=(-2, -2, (255, 236, 160)))
    icon("icon_safety_pin.png", 0, draw)


def paint_icon_toga():
    def draw(c):
        white, sh = (252, 250, 244), (206, 202, 224)
        body = poly([(30, 20), (70, 14), (104, 30), (100, 110), (24, 114), (28, 60)], 2)
        c.paint(body, white, shade=(5, 0, sh), pattern=lambda p: [
            p.line(bez((34, 24 + k * 14), (66, 50 + k * 14), (100, 40 + k * 18)), 2.4, sh) for k in range(4)] +
            [p.rect(0, 100, 128, 110, (230, 176, 50))])
        c.paint(ell(70, 22, 10, 10), (230, 176, 50), ow=3, hi=(-2, -2, (255, 230, 140)))
        c.line([(64, 22), (78, 22)], 2.5, (150, 156, 170))
    icon("icon_toga.png", 4, draw)


def paint_icon_frat_fuse():
    def draw(c):
        c.paint(rrect(42, 74, 86, 110, 4), (210, 160, 70), shade=(4, 0, (160, 110, 40)), hi=(-3, 0, (255, 220, 140)),
                pattern=lambda p: [p.line([(38, y), (90, y + 4)], 2.5, (150, 100, 40)) for y in (80, 90, 100)])
        c.paint(rect(56, 108, 72, 118), (200, 200, 210), ow=3)
        c.paint(ell(64, 54, 40, 26), (240, 236, 226), shade=(4, 4, (200, 196, 210)))
        c.paint(ell(64, 46, 28, 16), (200, 230, 240), ow=3, pattern=lambda p: p.line([(46, 46), (82, 46)], 2.5,
                                                                                      (180, 140, 60)))
        c.text(64, 68, "30A", 16, (200, 40, 50))
    icon("icon_frat_fuse.png", -10, draw)


def paint_icon_fernanda():
    def draw(c):
        draw_flamingo(c, 60, 190, 0.7, base=False, legs=False)
    icon("icon_fernanda.png", 0, draw)


def paint_icon_sorority_pin():
    def draw(c):
        gold, gsh, ghi = (240, 196, 80), (196, 140, 50), (255, 240, 170)
        shield = poly([(24, 20), (104, 20), (104, 64), (64, 112), (24, 64)], 2)
        c.paint(shield, gold, shade=(4, 4, gsh), hi=(-4, -4, ghi, 3))
        c.paint(poly([(36, 30), (92, 30), (92, 62), (64, 98), (36, 62)], 2), (255, 140, 180), ow=3)
        c.text(64, 50, "ΦΛΑ", 20, (255, 250, 230), stroke=1.5)
        for x, y in ((36, 30), (92, 30), (64, 98)):
            c.paint(ell(x, y, 5, 5), (255, 252, 240), ow=2)
        c.line([(46, 76), (82, 76)], 2.2, (200, 60, 120))
    icon("icon_sorority_pin.png", -8, draw)


def paint_icon_glow_bracelet():
    def draw(c):
        g = (110, 255, 130)
        c.paint(ell(64, 64, 52, 36, -15), (0, 0, 0, 0), ow=20)
        c.paint(ell(64, 64, 52, 36, -15), (0, 0, 0, 0), ow=13, oc=g)
        c.paint(ell(64, 64, 52, 36, -15), (0, 0, 0, 0), ow=4, oc=(230, 255, 230))
        c.paint(rrect(98, 70, 120, 86, 4), (230, 230, 240), ow=3)
        c.glow(64, 64, 64, (110, 255, 130), 0.25)
    icon("icon_glow_bracelet.png", 0, draw)


ASSETS.update({"bg_greek_row": paint_greek_row, "bg_frat_house": paint_frat_house, "bg_fuse_box": paint_fuse_box,
               "icon_bedsheet": paint_icon_bedsheet, "icon_safety_pin": paint_icon_safety_pin,
               "icon_toga": paint_icon_toga, "icon_frat_fuse": paint_icon_frat_fuse,
               "icon_fernanda": paint_icon_fernanda, "icon_sorority_pin": paint_icon_sorority_pin,
               "icon_glow_bracelet": paint_icon_glow_bracelet})


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
