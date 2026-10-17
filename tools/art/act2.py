#!/usr/bin/env python3
"""
Big Night Out -- Act 2 (Greek Week) art: Greek Row, the frat house, the Fuse Box bar, the sorority parlor,
the frat basement, Tess Calloway, Chad Thunderclap, Dolly Spark, Mother Whitlock, Moose, Dunk, Fernanda the
flamingo, the confiscated record and the act's item icons.

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
    # window (above the breaker box, leaving the right wall free for the basement door)
    paint.night_window(c, 1590, 220, 1700, 380, seed=17)
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

    # basement door (right edge)
    qx0, qy0, qx1, qy1 = box(R, "Basement door")
    qcx = (qx0 + qx1) / 2
    paint.door(c, qx0 + 16, qy0 + 16, qx1 - 14, qy1 - 8, (92, 72, 58), knob="L", casing=(170, 110, 60))
    c.paint(wonky(qx0 + 24, qy0 + 44, qx1 - 20, qy0 + 96, 2, rng), (236, 226, 206), ow=2.5,
            shade=(2, 2, (200, 190, 170)))
    c.text(qcx + 2, qy0 + 62, "BASEMENT", 13, (150, 30, 30))
    c.text(qcx + 2, qy0 + 82, "PLEDGES + DUNK", 8, (60, 40, 30), "Bold")
    c.line([(qx0 + 36, qy1 - 6), (qx1 - 30, qy1 - 6)], 3, (40, 26, 20))  # light strip under the door
    lights = [(ecx, ey0 + 60, 330, 0.85, (255, 240, 190)), (bcx, 300, 520, 0.55, (255, 120, 220)),
              (bcx + 150, 700, 380, 0.4, (90, 210, 255)), (1645, 300, 200, 0.25, (150, 150, 255)),
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

# =========================================================================== expansion: new cast
def paint_whitlock():
    """Mother Whitlock: sorority housemother. Silver bun, cat-eye glasses, lilac cardigan, white gloves,
    teacup and saucer. Faces right (drawn facing left, flipped)."""
    c = Canvas(110, 256, ow=3)
    skin, skin_sh = (246, 214, 192), (212, 160, 142)
    hair, hair_sh, hair_hi = (226, 226, 238), (170, 170, 194), (255, 255, 255)
    card, card_sh, card_hi = (186, 150, 222), (138, 104, 182), (222, 200, 246)
    tweed, tweed_sh = (118, 96, 112), (84, 64, 82)
    glove, glove_sh = (252, 252, 248), (206, 204, 220)
    shoe = (58, 42, 50)

    # bun behind the head
    c.paint(ell(70, 22, 15, 13), hair, shade=(3, 3, hair_sh), hi=(-2, -2, hair_hi, 1.5))
    c.curve((60, 18), (70, 12), (80, 20), 1.3, hair_sh)
    c.curve((62, 26), (72, 32), (82, 24), 1.3, hair_sh)
    # far arm: gloved hand on hip
    c.paint(cap([(72, 100), (88, 120), (74, 136)], 8), card, shade=(3, 2, card_sh))
    c.paint(ell(72, 136, 6, 5.5), glove, shade=(2, 2, glove_sh))
    # stockinged legs + sensible shoes pointing left
    for x0, x1 in ((58, 70), (40, 52)):
        c.paint(rect(x0, 206, x1, 236), (232, 196, 176), ow=2.6, shade=(3, 0, (196, 156, 140)))
    for xh, xt, yt, yb in ((72, 48, 232, 250), (54, 26, 234, 252)):
        sh = shoe_shape(xh, xt, yt, yb, toe_h=0.6)
        c.paint(sh, shoe, shade=(3, -2, dk(shoe, 0.6)), hi=(-2, 2, lt(shoe, 0.35), 1.5))
        c.paint(rect(xh - 4, yb - 6, xh + 1, yb), shoe, ow=2)  # little heel
    # long tweed skirt
    def tweed_pat(p):
        for x in range(20, 96, 7):
            p.line([(x, 124), (x - 4, 214)], 1.0, tweed_sh)
        for y in range(128, 214, 7):
            p.line([(20, y), (96, y + 2)], 1.0, lt(tweed, 0.15))
    c.paint(poly([(36, 124), (76, 124), (84, 212), (28, 212)], 1), tweed, pattern=tweed_pat, shade=(4, 0, tweed_sh))
    # neck
    c.paint(cap([(56, 80), (56, 96)], 9), skin, shade=(3, 0, skin_sh))
    # cardigan with a lace collar and a brooch
    torso = poly([(36, 94), (54, 89), (72, 92), (78, 106), (76, 130), (36, 130), (32, 114), (31, 102)], 2)
    c.paint(torso, card, shade=(4, 2, card_sh), hi=(-3, 3, card_hi, 2),
            pattern=lambda p: [p.ell(57, y, 1.6, 1.6, (250, 246, 250)) for y in (106, 116, 126)])
    c.line([(57, 98), (57, 130)], 1.3, card_sh)
    c.paint(poly([(42, 88), (56, 96), (50, 104), (40, 96)], 1), (252, 250, 244), ow=2,
            pattern=lambda p: [p.ell(44 + k * 3, 98 + k, 0.9, 0.9, (210, 206, 220)) for k in range(4)])
    c.paint(poly([(58, 96), (68, 87), (74, 95), (64, 104)], 1), (252, 250, 244), ow=2,
            pattern=lambda p: [p.ell(62 + k * 3, 98 - k, 0.9, 0.9, (210, 206, 220)) for k in range(4)])
    c.paint(ell(47, 112, 4.2, 4.2), (240, 196, 80), ow=1.8, hi=(-1, -1, (255, 240, 170)),
            pattern=lambda p: p.ell(47, 112, 2, 2, (140, 60, 120)))
    # near arm: holding a saucer and a teacup in front of her
    c.paint(cap([(38, 100), (30, 114), (22, 118)], 8.5), card, shade=(3, 2, card_sh))
    c.paint(ell(19, 117, 5.5, 4.8), glove, shade=(2, 2, glove_sh))
    c.paint(ell(16, 112, 14, 3.4), (250, 250, 252), ow=2.2, shade=(0, 1.5, (200, 200, 220)),
            pattern=lambda p: p.line([(4, 112), (28, 112)], 0.8, (200, 120, 170)))
    cup = poly([(7, 98), (25, 98), (23, 109), (9, 109)], 1)
    c.paint(cup, (250, 250, 252), ow=2.2, shade=(2, 0, (204, 204, 222)),
            pattern=lambda p: (p.rect(6, 101, 26, 103.5, (214, 120, 170)), p.ell(16, 105, 2.2, 2.2, (214, 120, 170))))
    c.paint(ell(27, 103, 3.5, 3, 0), (0, 0, 0, 0), ow=1.8)
    for k, x in enumerate((12, 18)):
        c.curve((x, 94), (x - 3, 88), (x + 1, 82), 1.2, (230, 230, 240), opacity=0.8)
    c.paint(cap([(36, 98), (32, 108)], 14), card, shade=(3, 2, card_sh))

    # ---- head (3/4, facing left)
    head = ell(58, 56, 23, 25) + poly([(36, 60), (40, 78), (50, 86), (62, 84), (76, 70)], 2) + ell(33.5, 62, 4.6, 4.6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 232, 214), 2.5))
    c.curve((34, 65), (31, 66), (31, 63), 1.3)
    c.paint(ell(50, 70, 5.5, 3.2), (240, 140, 150), ow=0, opacity=0.45)  # rouge
    # wrinkles + laugh lines (she never laughs, but the lines are there)
    c.curve((44, 74), (42, 78), (45, 81), 1.0, skin_sh)
    c.curve((63, 60), (66, 62), (66, 66), 1.0, skin_sh)
    eye(c, 54, 58, 6.5, 6.8, 51, 59, 2.1, lid=0.38, lid_tilt=-0.6, skin=skin, iris=(110, 90, 150))
    eye(c, 39.5, 58, 4.6, 6.4, 37, 59, 1.9, lid=0.38, lid_tilt=0.6, skin=skin, iris=(110, 90, 150))
    # cat-eye glasses + chain
    c.paint(poly([(44, 51), (64, 50), (66, 46), (63, 64), (46, 65)], 1), (0, 0, 0, 0), ow=2.4, oc=(130, 70, 140))
    c.paint(poly([(31, 52), (42, 52), (42, 64), (33, 64), (29, 48)], 1), (0, 0, 0, 0), ow=2.2, oc=(130, 70, 140))
    c.line([(42, 55), (45, 55)], 2.0, (130, 70, 140))
    c.curve((66, 54), (80, 80), (70, 96), 1.0, (230, 190, 80))
    # one stern raised brow
    c.line([(46, 44), (54, 40), (63, 43)], 2.2, hair_sh)
    c.line([(32, 47), (40, 46)], 2.0, hair_sh)
    # small pursed mouth
    c.paint(ell(41, 76, 4, 2), (186, 80, 110), ow=1.6)
    c.line([(39, 76), (43, 76)], 1.0, (120, 40, 70))
    # ear + pearl
    c.paint(ell(78, 62, 5.2, 7.5), skin, shade=(2, 2, skin_sh))
    c.paint(ell(78, 71, 2.4, 2.4), (255, 252, 240), ow=1.3)
    # silver hair swept up into the bun
    c.paint(poly([(34, 52), (38, 38), (52, 30), (70, 30), (84, 40), (90, 56), (86, 70), (80, 60), (74, 48),
                  (62, 42), (50, 42), (40, 48)], 2, True), hair, shade=(3, 2, hair_sh), hi=(-2, 3, hair_hi, 1.5))
    for k in range(3):
        c.curve((42 + k * 10, 44), (52 + k * 8, 34), (64 + k * 6, 30), 1.1, hair_sh)
    flip(c)
    c.fit(margin=3)
    c.save("hs_mother_whitlock.png")


MOOSE_SKIN, MOOSE_SH, MOOSE_HI = (238, 190, 152), (202, 142, 112), (255, 216, 184)
BEANIE, BEANIE_SH, BEANIE_HI = (66, 108, 214), (42, 70, 160), (130, 166, 240)


def pledge_beanie(c, cx, cy, r, rot=0.0):
    """Blue pledge beanie (dome + little brim + white P). (cx, cy) = centre of the brim."""
    def R(x, y):
        a = math.radians(rot)
        return (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))
    dome = poly([R(-r, 0), R(-r * 0.92, -r * 0.55), R(-r * 0.5, -r * 0.92), R(0, -r * 1.02), R(r * 0.5, -r * 0.92),
                 R(r * 0.92, -r * 0.55), R(r, 0)], 2)
    c.paint(dome, BEANIE, shade=(2, 2, BEANIE_SH), hi=(-2, -2, BEANIE_HI, 1.5),
            pattern=lambda p: [p.line([R(-r * 0.9 + k * r * 0.45, -r * 0.1), R(k * r * 0.12 - r * 0.2, -r * 0.95)],
                                      1.0, BEANIE_SH) for k in range(5)])
    c.paint(poly([R(-r * 1.25, 1), R(r * 0.2, -1), R(r * 0.2, r * 0.3), R(-r * 1.3, r * 0.32)], 1), BEANIE_SH, ow=2.2)
    c.paint(ell(*R(0, -r * 1.02), r * 0.14, r * 0.12), (250, 250, 255), ow=1.6)
    c.text(*R(r * 0.18, -r * 0.48), "P", max(7, r * 0.75), (255, 255, 255), "Black", stroke=0.8, sc=BEANIE_SH)


def paint_moose():
    """Moose: the frat's last pledge. Huge, gentle, starving. Toga, blue pledge beanie, clip-on necktie.
    Faces left (toward Dex)."""
    c = Canvas(130, 262, ow=3)
    skin, skin_sh, skin_hi = MOOSE_SKIN, MOOSE_SH, MOOSE_HI
    toga, toga_sh = (250, 248, 238), (204, 200, 220)
    trim = BEANIE
    tie, tie_sh = (40, 52, 116), (24, 30, 74)

    # legs + sandals (thick)
    c.paint(cap([(80, 186), (82, 214), (80, 238)], 17), skin, shade=(3, 0, skin_sh))
    c.paint(cap([(48, 186), (44, 214), (42, 240)], 18), skin, shade=(3, 0, skin_sh))
    for xh, xt, yt, yb in ((92, 60, 238, 252), (56, 18, 240, 256)):
        foot = shoe_shape(xh, xt, yt, yb - 3, toe_h=0.6)
        c.paint(foot, skin, shade=(3, -2, skin_sh))
        c.paint(poly([(xh + 2, yb - 5), (xt, yb - 5), (xt - 2, yb), (xh + 3, yb)], 1), (150, 96, 54), ow=2.4)
        for t in (0.3, 0.6):
            x = xh + (xt - xh) * t
            c.line([(x + 2, yt + 1), (x - 3, yb - 4)], 2.2, (130, 80, 44))
    # big round toga body
    body = poly([(24, 102), (64, 92), (106, 100), (114, 136), (110, 170), (104, 200), (64, 206), (22, 200), (16, 166),
                 (16, 130)], 2, True)

    def folds(p):
        for k in range(5):
            p.line(bez((26 + k * 4, 104 + k * 8), (64, 136 + k * 10), (108, 118 + k * 16), 12), 2.4, toga_sh)
        p.rect(10, 192, 120, 200, trim)
    c.paint(ell(100, 108, 16, 14), skin, shade=(4, 3, skin_sh), hi=(-3, -3, skin_hi, 2))  # bare far shoulder
    c.paint(body, toga, pattern=folds, shade=(5, 0, toga_sh))
    c.paint(poly([(20, 100), (46, 92), (68, 124), (58, 158), (40, 130)], 1), toga, shade=(3, 2, toga_sh))
    c.paint(cap([(24, 98), (62, 140)], 4), trim, ow=2.2)
    # thick neck
    c.paint(cap([(62, 80), (62, 98)], 22), skin, shade=(4, 0, skin_sh))
    # clip-on necktie, over the toga
    c.paint(poly([(56, 96), (68, 96), (66, 104), (58, 104)], 1), tie, ow=2.2)
    c.paint(poly([(58, 104), (66, 104), (72, 148), (62, 158), (52, 148)], 1), tie, ow=2.4, shade=(2, 0, tie_sh),
            pattern=lambda p: [p.ell(58 + (k % 2) * 6, 114 + k * 9, 1.6, 1.4, (240, 200, 80)) for k in range(5)])
    c.paint(rect(55, 97, 69, 100), (210, 214, 224), ow=1.4)  # the clip
    # hands clasped nervously in front of the belly
    c.paint(cap([(106, 112), (110, 140), (78, 158)], 15), skin, shade=(3, 3, skin_sh))
    c.paint(cap([(22, 112), (16, 140), (50, 160)], 15), skin, shade=(3, 3, skin_sh))
    c.paint(ell(66, 162, 15, 10), skin, shade=(3, 3, skin_sh), hi=(-2, -2, skin_hi, 1.5))
    for k in range(3):
        c.line([(58 + k * 6, 156), (60 + k * 6, 166)], 1.2, skin_sh)

    # ---- head (big, round, worried)
    head = ell(62, 52, 27, 27) + poly([(36, 54), (38, 74), (50, 86), (74, 86), (88, 66)], 2) + ell(36, 58, 5.5, 5.5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, skin_hi, 2.5))
    c.paint(ell(86, 58, 6, 8.5), skin, shade=(2, 2, skin_sh))
    c.paint(ell(36, 60, 5, 4.5), lt(skin_sh, 0.2), ow=2)  # round nose
    c.paint(ell(52, 70, 6, 3.5), (240, 130, 130), ow=0, opacity=0.45)
    eye(c, 56, 52, 6.5, 7.5, 52, 53, 2.6, lid=0.1, skin=skin, iris=(110, 80, 50))
    eye(c, 41, 52, 4.6, 7, 38.5, 53, 2.3, lid=0.1, skin=skin, iris=(110, 80, 50))
    # worried brows (up in the middle)
    c.line([(48, 38), (56, 41), (64, 44)], 2.6, (110, 70, 44))
    c.line([(34, 44), (40, 39)], 2.4, (110, 70, 44))
    # small worried "o" mouth
    c.paint(ell(44, 76, 4, 4.4), (120, 40, 50), ow=1.8, pattern=lambda p: p.ell(44, 78.5, 2.5, 1.6, (230, 110, 120)))
    # stubble
    c.paint(poly([(38, 74), (50, 86), (74, 86), (84, 70)], 1), (120, 90, 70), ow=0, opacity=0.12)
    # pledge beanie
    pledge_beanie(c, 62, 34, 26, -6)
    c.fit(margin=3)
    c.save("hs_moose.png")


def draw_cot(c, ox, oy):
    """Camp cot in sprite space (230 x 100, legs on y=100), shifted by (ox, oy)."""
    canvas_c, canvas_sh = (96, 120, 70), (66, 86, 48)
    frame = (150, 156, 166)
    for x0, x1 in ((24, 70), (160, 206)):  # X legs
        c.line([(ox + x0, oy + 72), (ox + x1, oy + 98)], 4, frame)
        c.line([(ox + x1, oy + 72), (ox + x0, oy + 98)], 4, frame)
        c.line([(ox + x0, oy + 72), (ox + x1, oy + 98)], 1.5, lt(frame, 0.3))
    c.paint(rrect(ox + 8, oy + 62, ox + 222, oy + 76, 5), canvas_c, ow=3, shade=(0, 3, canvas_sh),
            hi=(0, -2, lt(canvas_c, 0.3)))
    c.line([(ox + 10, oy + 69), (ox + 220, oy + 69)], 1.5, canvas_sh)


def paint_sleeping_moose():
    """Moose asleep on the basement cot, hugging a pink pillow. Laid out to sit exactly on the painted cot."""
    c = Canvas(230, 100, ow=3)
    skin, skin_sh, skin_hi = MOOSE_SKIN, MOOSE_SH, MOOSE_HI
    toga, toga_sh = (250, 248, 238), (204, 200, 220)
    draw_cot(c, 0, 0)
    # pillow under his head
    c.paint(wonky(10, 44, 60, 66, 2), (250, 248, 240), shade=(0, 3, (210, 206, 224)))
    # big toga mound (body), feet sticking up at the end
    body = poly([(48, 64), (60, 40), (100, 28), (150, 30), (186, 42), (200, 64)], 2, True)
    c.paint(body, toga, shade=(0, 4, toga_sh), hi=(0, -3, (255, 255, 255), 1.5),
            pattern=lambda p: [p.line(bez((70 + k * 26, 36), (80 + k * 26, 50), (74 + k * 26, 64)), 2.2, toga_sh)
                               for k in range(5)] + [p.rect(40, 58, 210, 64, BEANIE)])
    for fx in (204, 214):
        c.paint(ell(fx, 52, 6, 11, 10), skin, shade=(2, 2, skin_sh))
        c.paint(poly([(fx - 7, 60), (fx + 7, 58), (fx + 7, 63), (fx - 7, 65)]), (150, 96, 54), ow=2)
    # arm over a pink pillow he's hugging
    c.paint(ell(104, 34, 22, 14, -8), (255, 140, 186), shade=(2, 3, (220, 90, 150)), hi=(-2, -2, (255, 196, 220)))
    c.paint(cap([(70, 44), (96, 30), (120, 34)], 12), skin, shade=(2, 3, skin_sh), hi=(-1, -2, skin_hi, 1))
    c.paint(ell(122, 35, 7, 6), skin, shade=(2, 2, skin_sh))
    # head on the pillow (profile, facing up)
    head = ell(36, 42, 20, 18)
    c.paint(head, skin, shade=(3, 3, skin_sh), hi=(-2, -3, skin_hi, 2))
    c.paint(ell(32, 26, 5, 4.5), lt(skin_sh, 0.2), ow=2)  # nose pointing up
    c.line([(24, 36), (30, 38)], 2.0)  # closed eyes
    c.line([(38, 34), (44, 36)], 2.0)
    c.paint(ell(36, 49, 4.5, 3.5), (120, 40, 50), ow=1.8)  # snoring mouth
    pledge_beanie(c, 16, 42, 15, -90)
    # z z z
    for k, (x, y, sz) in enumerate(((52, 18, 10), (64, 8, 13), (80, 0, 16))):
        c.text(x, y + 6, "z" if k < 2 else "Z", sz, (200, 220, 255), "Black", stroke=1.4)
    c.save("hs_sleeping_moose.png")


def paint_dunk():
    """Dunk: seventh-year senior who lives in the frat basement. Faded toga, wilted laurel, sunglasses at night,
    a big mug, flip-flops. Faces right (drawn facing left, flipped)."""
    c = Canvas(116, 256, ow=3)
    skin, skin_sh, skin_hi = (226, 170, 132), (186, 124, 96), (246, 200, 164)
    hair, hair_sh = (112, 78, 52), (78, 52, 34)
    toga, toga_sh = (236, 226, 188), (196, 182, 148)
    leaf_c, leaf_sh = (150, 140, 70), (110, 96, 50)

    # legs + flip-flops
    c.paint(cap([(70, 184), (72, 214), (70, 238)], 13), skin, shade=(3, 0, skin_sh))
    c.paint(cap([(46, 184), (42, 214), (40, 240)], 13.5), skin, shade=(3, 0, skin_sh))
    c.line([(66, 196), (74, 200)], 1.2, hair_sh)  # leg hair, a little
    for xh, xt, yt, yb in ((80, 52, 238, 250), (52, 18, 240, 252)):
        c.paint(poly([(xh + 3, yb - 4), (xt - 2, yb - 4), (xt - 3, yb + 1), (xh + 4, yb + 1)], 1), (60, 160, 200),
                ow=2.4)
        c.paint(shoe_shape(xh, xt, yt, yb - 4, toe_h=0.7), skin, shade=(3, -2, skin_sh))
        mx = (xh + xt) / 2
        c.line([(mx + 6, yt + 2), (mx - 4, yb - 6), (mx - 10, yt + 4)], 2.0, (60, 160, 200))
    # faded toga, a bit too short, coffee stain, slight belly
    body = poly([(30, 98), (58, 92), (88, 96), (96, 128), (94, 160), (88, 192), (58, 196), (28, 192), (24, 158),
                 (24, 126)], 2)

    def folds(p):
        for k in range(4):
            p.line(bez((32 + k * 4, 102 + k * 9), (60, 132 + k * 10), (90, 116 + k * 16), 12), 2.2, toga_sh)
        p.ell(74, 168, 6, 4, (196, 160, 110))
        p.rect(20, 184, 100, 191, (180, 150, 80))
    c.paint(ell(84, 104, 13, 11), skin, shade=(4, 3, skin_sh), hi=(-3, -3, skin_hi, 2))
    c.paint(body, toga, pattern=folds, shade=(5, 0, toga_sh))
    c.curve((40, 150), (62, 172), (90, 150), 1.4, toga_sh)  # belly line
    c.paint(poly([(28, 96), (48, 90), (64, 122), (54, 150), (40, 124)], 1), toga, shade=(3, 2, toga_sh))
    # neck
    c.paint(cap([(56, 80), (56, 96)], 12), skin, shade=(3, 0, skin_sh))
    # far arm hanging relaxed
    c.paint(cap([(90, 104), (98, 132), (94, 156)], 9.5), skin, shade=(3, 2, skin_sh))
    c.paint(ell(94, 158, 6, 6), skin, shade=(2, 2, skin_sh))
    # near arm holding a big mug
    c.paint(cap([(34, 102), (24, 124), (36, 134)], 9.5), skin, shade=(3, 2, skin_sh))
    mug = rrect(14, 112, 38, 140, 3)
    c.paint(mug, (250, 248, 240), ow=2.4, shade=(3, 0, (206, 204, 220)),
            pattern=lambda p: (p.rect(10, 118, 42, 124, (210, 60, 60)), p.rect(10, 128, 42, 130, (210, 60, 60))))
    c.paint(ell(12, 126, 5, 7), (0, 0, 0, 0), ow=2.2)
    c.paint(ell(26, 113, 11, 2.2), (110, 70, 40), ow=1.4)
    c.curve((22, 108), (19, 100), (24, 92), 1.2, (230, 230, 240), opacity=0.8)
    c.paint(ell(38, 132, 6, 5.5), skin, shade=(2, 2, skin_sh))

    # ---- head (3/4, facing left), scruffy beard, sunglasses
    head = ell(58, 54, 23, 25) + poly([(36, 58), (38, 76), (50, 86), (64, 84), (78, 68)], 2) + ell(34, 60, 5, 5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, skin_hi, 2.5))
    c.paint(ell(78, 60, 5.5, 8), skin, shade=(2, 2, skin_sh))
    beard = poly([(36, 66), (42, 64), (52, 70), (64, 68), (76, 62), (78, 72), (68, 86), (52, 92), (40, 86)], 2, True)
    c.paint(beard, hair, shade=(3, 3, hair_sh), pattern=lambda p: [p.line([(40 + k * 5, 76), (42 + k * 5, 86)], 1.0,
                                                                         hair_sh) for k in range(7)])
    c.paint(poly([(38, 74), (46, 76), (52, 74), (50, 79), (42, 80)], 1), (150, 60, 60), ow=1.6)  # lazy grin
    c.line([(40, 75.5), (51, 75)], 1.0, (255, 255, 255))
    # sunglasses
    c.paint(rrect(44, 48, 64, 60, 4), (30, 30, 40), ow=2.2, hi=(-2, -2, (110, 120, 160), 1.2))
    c.paint(rrect(30, 48, 42, 60, 3), (30, 30, 40), ow=2.2, hi=(-1.5, -1.5, (110, 120, 160), 1))
    c.line([(42, 52), (44, 52)], 2.2, (30, 30, 40))
    c.line([(64, 52), (76, 56)], 2.0, (30, 30, 40))
    # messy hair
    c.paint(poly([(32, 46), (34, 32), (44, 24), (58, 20), (74, 26), (86, 38), (88, 56), (82, 66), (78, 50), (68, 40),
                  (54, 42), (42, 40)], 2, True), hair, shade=(3, 2, hair_sh), hi=(-2, 3, lt(hair, 0.3), 1.5))
    for k in range(4):
        c.curve((40 + k * 11, 30 - k), (44 + k * 11, 22), (38 + k * 12, 18), 2.2, hair)
    # wilted laurel wreath, a few leaves drooping
    for k in range(6):
        t = k / 5
        x = 36 + 48 * t
        y = 36 - 10 * math.sin(math.pi * t) + 2
        c.paint(ell(x, y + 3, 5, 2.4, 70 + 20 * t), leaf_c, ow=2, shade=(1, 1, leaf_sh))
    flip(c)
    c.fit(margin=3)
    c.save("hs_dunk.png")


def draw_record_sleeve(c, x0, y0, s, angle_vinyl=True):
    """Disco Volcano sleeve with the vinyl peeking out, top-left at (x0, y0), side s."""
    if angle_vinyl:
        c.paint(ell(x0 + s * 0.78, y0 + s * 0.5, s * 0.46, s * 0.46), (30, 26, 34), ow=max(2, s / 20),
                pattern=lambda p: [p.ell(x0 + s * 0.78, y0 + s * 0.5, s * r, s * r, c_)
                                   for r, c_ in ((0.40, (46, 42, 54)), (0.34, (30, 26, 34)), (0.28, (46, 42, 54)),
                                                 (0.14, (255, 150, 60)), (0.03, (30, 26, 34)))])
    sleeve = rect(x0, y0, x0 + s, y0 + s)

    def art(p):
        p.rect(x0, y0 + s * 0.62, x0 + s, y0 + s, (120, 40, 110))
        p.poly([(x0 + s * 0.18, y0 + s * 0.78), (x0 + s * 0.42, y0 + s * 0.36), (x0 + s * 0.58, y0 + s * 0.36),
                (x0 + s * 0.82, y0 + s * 0.78)], (90, 50, 50))
        p.poly([(x0 + s * 0.42, y0 + s * 0.36), (x0 + s * 0.5, y0 + s * 0.14), (x0 + s * 0.58, y0 + s * 0.36)],
               (255, 200, 60))
        for k in range(5):
            a = math.radians(-160 + k * 35)
            p.line([(x0 + s * 0.5, y0 + s * 0.3), (x0 + s * (0.5 + 0.34 * math.cos(a)), y0 + s * (0.3 + 0.34 * math.sin(a)))],
                   max(1, s / 30), (255, 230, 120))
        for k in range(6):
            p.ell(x0 + s * (0.12 + 0.15 * k), y0 + s * 0.9, s * 0.04, s * 0.04, (255, 120, 200))
    c.paint(sleeve, ("v", (255, 120, 60), (220, 50, 70)), ow=max(2, s / 18), pattern=art,
            shade=(-2, -2, (180, 40, 60)))


def paint_disco_record_prop():
    """The confiscated Disco Volcano record on a little brass display stand (on top of the cabinet)."""
    c = Canvas(80, 76, ow=3)
    gold, gsh = (230, 182, 70), (180, 130, 40)
    c.line([(26, 72), (40, 36), (54, 72)], 3.2, gold)
    c.paint(rrect(14, 66, 66, 74, 3), gold, ow=2.4, hi=(0, -2, (255, 230, 150)), shade=(0, 2, gsh))
    draw_record_sleeve(c, 14, 10, 46)
    c.paint(rect(16, 56, 60, 64), gold, ow=2.2, hi=(0, -1.5, (255, 230, 150)))  # ledge
    # little confiscation tag on a string
    c.line([(18, 12), (8, 26)], 1.2, (90, 70, 60))
    c.paint(poly([(2, 24), (14, 24), (14, 38), (2, 38)]), (250, 244, 220), ow=1.8,
            pattern=lambda p: [p.line([(4, 28 + k * 4), (12, 28 + k * 4)], 0.9, (180, 40, 40)) for k in range(3)])
    c.fit(margin=2)
    c.save("hs_disco_volcano_record.png")


ASSETS.update({"hs_mother_whitlock": paint_whitlock, "hs_moose": paint_moose, "hs_sleeping_moose": paint_sleeping_moose,
               "hs_dunk": paint_dunk, "hs_disco_volcano_record": paint_disco_record_prop})


# =========================================================================== the sorority parlor
def paint_sorority_parlor():
    R = "sorority_parlor"
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(1921)
    paper, paper2 = (238, 168, 186), (226, 148, 170)

    def wallpaper(p):
        for x in range(0, W_BG, 60):
            p.rect(x, 0, x + 26, 570, paper2)
        for x in range(30, W_BG, 60):
            for y in range(70, 560, 64):
                yy = y + (x // 60 % 2) * 32
                p.ell(x - 17, yy, 5, 4, (214, 90, 130))
                p.ell(x - 13, yy - 2, 4, 3.5, (240, 120, 160))
                p.ell(x - 22, yy + 6, 4, 2, (110, 160, 100), rot=-30)
    c.paint(rect(0, 0, W_BG, 570), ("vy", 40, 570, dk(paper, 0.82), paper), ow=0, pattern=wallpaper)
    # crown moulding
    c.paint(rect(0, 0, W_BG, 44), (250, 244, 236), ow=0, pattern=lambda p: [p.rect(x, 30, x + 20, 44, (226, 214, 214))
                                                                              for x in range(0, W_BG, 34)])
    c.paint(rect(-10, 40, W_BG + 10, 56), (240, 228, 224), ow=3)
    # cream wainscoting with raised panels
    cream = (250, 240, 226)
    c.paint(rect(0, 566, W_BG, WALL_Y), ("vy", 566, WALL_Y, cream, dk(cream, 0.9)), ow=0)
    c.paint(rect(-10, 556, W_BG + 10, 576), lt(cream, 0.2), ow=3, shade=(0, -4, dk(cream, 0.8)))
    for x in range(30, W_BG, 160):
        c.paint(rrect(x, 600, x + 130, 750, 6), cream, ow=2.5, shade=(0, -4, dk(cream, 0.82)), hi=(0, 3, (255, 252, 246)))
    paint.plank_floor(c, (150, 92, 66), seed=61)
    paint.baseboard(c, color=(236, 222, 210))
    # big oval rug
    c.paint(ell(1000, 940, 760, 120), (150, 40, 70), ow=4, pattern=lambda p: (
        p.ell(1000, 940, 730, 104, (220, 170, 80)), p.ell(1000, 940, 712, 96, (150, 40, 70)),
        [p.ell(1000 + 560 * math.cos(a), 940 + 76 * math.sin(a), 16, 6, (230, 120, 150))
         for a in [k * math.tau / 20 for k in range(20)]], p.ell(1000, 940, 160, 26, (230, 120, 150)),
        p.ell(1000, 940, 120, 18, (150, 40, 70))))

    # front door (left edge)
    fx0, fy0, fx1, fy1 = box(R, "Front door")
    paint.door(c, fx0 + 14, fy0 + 14, fx1 - 6, fy1 - 10, (214, 60, 110), knob="R", casing=(250, 244, 236))
    # small framed photo of Fernanda by the door
    c.paint(rect(196, 300, 266, 380), (230, 182, 70), shade=(-3, -3, (180, 130, 40)), hi=(2, 2, (255, 230, 150)))
    c.paint(rect(204, 308, 258, 372), (180, 220, 240), ow=2.5)
    draw_flamingo(c, 231, 368, 0.22, base=False)

    # founder portrait: oval gilt frame
    px0, py0, px1, py1 = box(R, "Founder portrait")
    pcx, pcy = (px0 + px1) / 2, (py0 + py1) / 2 - 8
    c.paint(ell(pcx, pcy, 64, 80), (230, 182, 70), shade=(-5, -5, (176, 126, 40)), hi=(4, 4, (255, 232, 150), 3),
            pattern=lambda p: [p.ell(pcx + 58 * math.cos(a), pcy + 74 * math.sin(a), 4, 4, (255, 226, 140))
                               for a in [k * math.tau / 24 for k in range(24)]])
    def portrait(p):
        p.rect(px0, py0, px1, py1, (70, 40, 60))
        p.poly([(pcx - 44, pcy + 76), (pcx - 30, pcy + 26), (pcx + 30, pcy + 26), (pcx + 44, pcy + 76)], (110, 70, 140))
        p.ell(pcx, pcy - 6, 20, 25, (240, 206, 182))
        p.ell(pcx, pcy - 32, 22, 12, (90, 70, 60))
        p.ell(pcx, pcy - 46, 12, 10, (90, 70, 60))
        p.line([(pcx - 14, pcy - 14), (pcx - 4, pcy - 18)], 3.5, (60, 40, 30))  # the eyebrows
        p.line([(pcx + 4, pcy - 18), (pcx + 14, pcy - 15)], 3.5, (60, 40, 30))
        p.ell(pcx - 8, pcy - 8, 2.4, 2.4, (40, 30, 30))
        p.ell(pcx + 8, pcy - 8, 2.4, 2.4, (40, 30, 30))
        p.line([(pcx - 6, pcy + 8), (pcx + 6, pcy + 8)], 2.2, (150, 60, 70))
        for k in range(7):
            p.ell(pcx - 14 + k * 4.6, pcy + 26 + (3 - abs(k - 3)) * 1.5, 2.2, 2.2, (255, 250, 240))
    c.paint(ell(pcx, pcy, 50, 66), (70, 40, 60), ow=3, pattern=portrait)
    c.paint(rrect(pcx - 46, py1 - 16, pcx + 46, py1 + 2, 3), (230, 182, 70), ow=2.5, hi=(0, 2, (255, 232, 150)))
    c.text(pcx, py1 - 7, "PRUDENCE LAMBERT 1921", 7, (80, 40, 20), "Bold")

    # tall window with lush drapes (the famous curtains)
    wx0, wx1, wy0, wy1 = 780, 990, 150, 470
    c.paint(rect(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14), (250, 244, 236), shade=(-4, -4, (214, 206, 214)))
    paint.night_window(c, wx0, wy0, wx1, wy1, seed=21, frame=(250, 244, 236))
    c.paint(rrect(wx0 - 80, wy0 - 40, wx1 + 80, wy0 - 22, 8), (230, 182, 70), ow=3, hi=(0, 3, (255, 232, 150)))
    paint.curtain(c, wx0 - 70, wx0 + 30, wy0 - 30, wy1 + 70, (196, 60, 110), side="L", seed=5)
    paint.curtain(c, wx1 - 30, wx1 + 70, wy0 - 30, wy1 + 70, (196, 60, 110), side="R", seed=6)
    c.paint(wonky(wx0 - 90, wy0 - 34, wx1 + 90, wy0 + 26, 2, rng), (214, 80, 130), shade=(0, -5, (160, 40, 90)),
            pattern=lambda p: [p.ell(x, wy0 + 26, 14, 10, (214, 80, 130)) for x in range(wx0 - 80, wx1 + 90, 36)])
    for x in (wx0 - 24, wx1 + 24):  # tie-backs
        c.paint(ell(x, wy1 + 2, 12, 8), (230, 182, 70), ow=2.5)
    # wingback armchair behind Mother Whitlock
    ax = 820
    c.shadow(ax + 20, WALL_Y + 24, 130, 14, 0.4)
    c.paint(poly([(ax - 90, 600), (ax - 70, 540), (ax + 110, 540), (ax + 130, 600), (ax + 120, 800), (ax - 80, 800)], 2),
            (120, 70, 150), shade=(-6, 0, (84, 46, 110)), hi=(5, 0, (160, 110, 190)),
            pattern=lambda p: [p.ell(ax - 40 + (k % 4) * 50, 580 + (k // 4) * 50, 3, 3, (90, 50, 120)) for k in range(16)])
    for sx in (ax - 110, ax + 130):
        c.paint(rrect(sx - 22, 660, sx + 22, 790, 14), (120, 70, 150), shade=(-4, 0, (84, 46, 110)))
    c.paint(rrect(ax - 80, 720, ax + 120, 790, 10), (140, 90, 170), shade=(0, -4, (96, 56, 124)))
    for lx in (ax - 110, ax + 132):
        c.paint(rect(lx - 6, 788, lx + 6, 812), (110, 70, 44), ow=2.5)

    # tea cart
    tx0, ty0, tx1, ty1 = box(R, "Tea cart")
    tcx = (tx0 + tx1) / 2
    c.shadow(tcx, ty1 - 4, 84, 9, 0.45)
    silver = (206, 210, 222)
    for y in (ty0 + 50, ty0 + 92):
        c.paint(rrect(tx0 + 6, y, tx1 - 6, y + 10, 4), silver, ow=3, hi=(0, -2, (244, 246, 252)), shade=(0, 2, (150, 154, 170)))
    for x in (tx0 + 14, tx1 - 14):
        c.paint(rect(x - 3, ty0 + 30, x + 3, ty1 - 14), silver, ow=2.2)
        c.paint(ell(x, ty1 - 10, 9, 9), (60, 60, 70), ow=2.5, pattern=lambda p, x=x: p.ell(x, ty1 - 10, 3, 3, silver))
    c.paint(cap([(tx1 - 14, ty0 + 30), (tx1 + 6, ty0 + 20)], 4), silver, ow=2.2)  # handle
    # teapot + sandwich tiers on top
    c.paint(ell(tx0 + 50, ty0 + 30, 22, 18), (252, 250, 246), ow=3, shade=(3, 2, (214, 210, 224)),
            pattern=lambda p: p.ell(tx0 + 50, ty0 + 30, 7, 7, (230, 120, 170)))
    c.paint(cap([(tx0 + 28, ty0 + 30), (tx0 + 16, ty0 + 18)], 4.5), (252, 250, 246), ow=2.4)
    c.paint(ell(tx0 + 50, ty0 + 12, 7, 4), (252, 250, 246), ow=2.4)
    c.line([(tx1 - 46, ty0 + 48), (tx1 - 46, ty0 - 6)], 3, (230, 182, 70))
    for k, (y, r) in enumerate(((ty0 + 46, 30), (ty0 + 22, 22), (ty0 + 2, 15))):
        c.paint(ell(tx1 - 46, y, r, 4.5), (252, 250, 246), ow=2.4)
        for j in range(int(r // 9)):
            sx = tx1 - 46 - r + 10 + j * 14
            c.paint(poly([(sx - 6, y - 1), (sx + 6, y - 1), (sx, y - 10)]), (252, 244, 210), ow=1.8,
                    pattern=lambda p, sx=sx, y=y: p.rect(sx - 6, y - 5, sx + 6, y - 4, (120, 190, 110)))

    # manners sampler (embroidery in a gold frame)
    mx0, my0, mx1, my1 = box(R, "Manners sampler")
    c.paint(rect(mx0 + 4, my0 + 4, mx1 - 4, my1 - 4), (230, 182, 70), shade=(-4, -4, (176, 126, 40)),
            hi=(3, 3, (255, 232, 150)))
    def stitches(p):
        for k in range(0, int(mx1 - mx0 - 36), 8):
            for yy in (my0 + 20, my1 - 20):
                p.line([(mx0 + 18 + k, yy - 2), (mx0 + 22 + k, yy + 2)], 1.2, (200, 60, 110))
                p.line([(mx0 + 22 + k, yy - 2), (mx0 + 18 + k, yy + 2)], 1.2, (200, 60, 110))
        for k in range(4):
            p.line([(mx0 + 26, my0 + 54 + k * 9), (mx1 - 26 - (k % 2) * 14, my0 + 54 + k * 9)], 1.4, (110, 90, 150))
        p.ell(mx1 - 30, my1 - 34, 4, 3, (255, 120, 170))
        p.line([(mx1 - 30, my1 - 31), (mx1 - 30, my1 - 24)], 1, (255, 120, 170))
    c.paint(rect(mx0 + 14, my0 + 14, mx1 - 14, my1 - 14), (250, 244, 224), ow=2.5, pattern=stitches)
    c.text((mx0 + mx1) / 2, my0 + 38, "RULES OF", 9, (60, 110, 80), "Bold")
    c.text((mx0 + mx1) / 2, my0 + 48, "THE PARLOR", 8, (60, 110, 80), "Bold")

    # grandfather clock between sampler and cabinet
    gx = 1250
    c.shadow(gx, WALL_Y + 6, 46, 8, 0.4)
    c.paint(poly([(gx - 34, 440), (gx, 410), (gx + 34, 440), (gx + 34, 560), (gx + 26, 560), (gx + 26, 760),
                  (gx + 36, 760), (gx + 36, WALL_Y + 6), (gx - 36, WALL_Y + 6), (gx - 36, 760), (gx - 26, 760),
                  (gx - 26, 560), (gx - 34, 560)], 1), (120, 66, 40), shade=(-5, 0, (84, 44, 26)),
            hi=(4, 0, (160, 100, 60)))
    c.paint(ell(gx, 480, 24, 24), (250, 244, 226), ow=3, pattern=lambda p: (
        [p.ell(gx + 18 * math.cos(a), 480 + 18 * math.sin(a), 1.6, 1.6, (60, 40, 30)) for a in
         [k * math.tau / 12 for k in range(12)]],
        p.line([(gx, 480), (gx, 466)], 2, (60, 40, 30)), p.line([(gx, 480), (gx + 10, 484)], 2, (60, 40, 30))))
    c.paint(rect(gx - 16, 580, gx + 16, 740), (60, 36, 26), ow=3, pattern=lambda p: (
        p.line([(gx, 580), (gx + 6, 700)], 2, (230, 182, 70)), p.ell(gx + 6, 704, 9, 9, (230, 182, 70))))

    # confiscation cabinet
    cx0, cy0, cx1, cy1 = box(R, "Confiscation cabinet")
    ccx = (cx0 + cx1) / 2
    wood, wood_sh = (130, 74, 44), (92, 50, 30)
    c.shadow(ccx, cy1 - 2, 100, 12, 0.45)
    c.paint(rect(cx0 + 2, cy0 + 2, cx1 - 2, cy1 - 4), wood, shade=(-6, 0, wood_sh), hi=(4, 0, (170, 108, 66)))
    c.paint(rect(cx0 - 8, cy0 - 8, cx1 + 8, cy0 + 10), wood, ow=3, shade=(0, -4, wood_sh))
    glass_x0, glass_x1, glass_y0, glass_y1 = cx0 + 16, cx1 - 16, cy0 + 26, cy1 - 54

    def contents(p):
        p.rect(glass_x0, glass_y0, glass_x1, glass_y1, (190, 210, 222))
        for y in (glass_y0 + 62, glass_y0 + 128):
            p.rect(glass_x0, y, glass_x1, y + 6, wood_sh)
        # top shelf: airhorn
        hx = glass_x0 + 30
        p.rect(hx - 10, glass_y0 + 22, hx + 10, glass_y0 + 60, (230, 50, 60))
        p.poly([(hx - 10, glass_y0 + 22), (hx + 10, glass_y0 + 22), (hx + 24, glass_y0 + 4), (hx - 24, glass_y0 + 4)],
               (250, 230, 90))
        # top shelf: cassette
        p.rect(glass_x1 - 64, glass_y0 + 34, glass_x1 - 14, glass_y0 + 60, (40, 40, 50))
        p.rect(glass_x1 - 58, glass_y0 + 38, glass_x1 - 20, glass_y0 + 48, (250, 240, 200))
        p.ell(glass_x1 - 48, glass_y0 + 53, 4, 4, (200, 200, 210))
        p.ell(glass_x1 - 30, glass_y0 + 53, 4, 4, (200, 200, 210))
        # middle shelf: catapult (bucket on a spoon arm)
        p.rect(glass_x0 + 10, glass_y0 + 118, glass_x0 + 70, glass_y0 + 126, (140, 96, 60))
        p.line([(glass_x0 + 30, glass_y0 + 118), (glass_x0 + 90, glass_y0 + 82)], 4, (140, 96, 60))
        p.ell(glass_x0 + 96, glass_y0 + 80, 13, 9, (60, 140, 220))
        p.ell(glass_x0 + 96, glass_y0 + 76, 9, 5, (120, 200, 250))
        # bottom shelf: forty-one red cups
        for k in range(6):
            x = glass_x0 + 8 + k * 22
            for j in range(2):
                p.poly([(x, glass_y1 - 2 - j * 12), (x + 16, glass_y1 - 2 - j * 12), (x + 14, glass_y1 - 30 - j * 12),
                        (x + 2, glass_y1 - 30 - j * 12)], (220, 40, 50))
        # glass sheen
        p.poly([(glass_x0 + 20, glass_y1), (glass_x0 + 70, glass_y0), (glass_x0 + 92, glass_y0), (glass_x0 + 42, glass_y1)],
               (230, 240, 250))
    c.paint(rect(glass_x0, glass_y0, glass_x1, glass_y1), (190, 210, 222), ow=3, pattern=contents)
    c.line([(ccx, glass_y0), (ccx, glass_y1)], 4, wood)
    c.paint(ell(ccx + 10, (glass_y0 + glass_y1) / 2, 4, 6), (230, 182, 70), ow=2)  # lock
    c.paint(rrect(ccx - 58, cy1 - 44, ccx + 58, cy1 - 18, 3), (230, 182, 70), ow=2.5, hi=(0, 2, (255, 232, 150)))
    c.text(ccx, cy1 - 31, "CONFISCATED", 13, (80, 30, 20))
    for x in (cx0 + 10, cx1 - 10):
        c.paint(rect(x - 6, cy1 - 8, x + 6, cy1 + 2), wood_sh, ow=2)

    # chandelier
    chx = 1560
    c.line([(chx, 56), (chx, 100)], 2.5)
    c.paint(ell(chx, 110, 70, 14), (230, 182, 70), ow=3, hi=(0, -3, (255, 232, 150)))
    for k in range(7):
        x = chx - 60 + k * 20
        c.paint(rect(x - 3, 82, x + 3, 102), (252, 248, 236), ow=2)
        c.paint(ell(x, 76, 3.5, 6), (255, 220, 120), ow=1.6)
        c.paint(ell(x, 128 + (k % 2) * 8, 3, 5), (230, 240, 255), ow=1.4)

    lights = [(chx, 120, 900, 0.5, (255, 220, 170)), (pcx, pcy, 160, 0.2, (255, 220, 160)),
              (885, 300, 260, 0.25, (150, 150, 255)), (ccx, cy0 + 60, 240, 0.25, (255, 230, 190)),
              (tcx, ty0, 200, 0.2, (255, 220, 160))]
    paint.light_pass(c, 0.72, lights, vign=0.4)
    for k in range(7):
        c.glow(chx - 60 + k * 20, 76, 26, (255, 220, 120), 0.6)
    c.save("bg_sorority_parlor.png")


# =========================================================================== the frat basement
def paint_frat_basement():
    R = "frat_basement"
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(2019)
    paint.block_wall(c, 0, 0, W_BG, WALL_Y, (128, 124, 120), (96, 92, 92), bw=96, bh=44, mortar=0.4, seed=71)
    # ceiling joists + pipes
    c.paint(rect(0, 0, W_BG, 70), (60, 46, 38), ow=0)
    for x in range(-20, W_BG + 40, 140):
        c.paint(rect(x, 0, x + 30, 84), (110, 76, 50), ow=3, shade=(-4, 0, (80, 54, 36)))
    c.paint(cap([(-10, 104), (W_BG + 10, 104)], 14), (150, 156, 166), shade=(0, 3, (110, 114, 124)),
            hi=(0, -3, (200, 204, 212)))
    c.paint(cap([(-10, 132), (700, 132), (720, 152), (720, 260)], 9), (184, 110, 70), shade=(0, 2, (140, 80, 50)))
    for x in (300, 900, 1500):
        c.paint(rect(x - 10, 92, x + 10, 116), (120, 124, 132), ow=2.5)
    # concrete floor
    conc = (120, 116, 112)
    c.paint(rect(0, WALL_Y, W_BG, H_BG), ("vy", WALL_Y, H_BG, lt(conc, 0.08), dk(conc, 0.8)), ow=0)
    for _ in range(10):
        x, y = rng.uniform(60, 1860), rng.uniform(820, 1060)
        c.line([(x, y), (x + rng.uniform(-60, 60), y + rng.uniform(-10, 14)), (x + rng.uniform(-90, 90), y + rng.uniform(4, 24))],
               2, dk(conc, 0.6), opacity=0.6)
    c.paint(ell(1150, 960, 120, 18), dk(conc, 0.75), ow=0, opacity=0.5)  # old stain
    c.paint(ell(420, 1010, 70, 12), dk(conc, 0.75), ow=0, opacity=0.4)
    c.paint(ell(960, 1000, 220, 30), (40, 120, 150), ow=3, opacity=0.9, pattern=lambda p: (
        p.ell(960, 1000, 200, 24, (60, 150, 170)), p.ell(960, 1000, 120, 14, (40, 120, 150))))  # sad rug
    paint.baseboard(c, color=(80, 76, 74), h=12)
    # high basement window with moonlight
    paint.night_window(c, 600, 170, 780, 250, seed=29, frame=(150, 146, 140), mull=False)
    # posters
    for (x, y, ang, txt, col) in ((1180, 250, -4, "BEER PONG\nCHAMPS 2019", (40, 90, 200)), (1440, 230, 3, "DUNK\n4 LIFE", (220, 60, 60))):
        lines = txt.split("\n")
        def draw(p, ox, oy, lines=lines, col=col):
            p.rect(ox, oy, ox + 150, oy + 30, col)
        sub = paint.poster(150, 110, (250, 240, 210), draw, ang)
        for k, ln in enumerate(lines):
            sub.text(95, 76 + k * 26, ln, 15, (60, 40, 30), "Black")
        c.img.alpha_composite(sub.img.rotate(ang, resample=Image.BICUBIC, expand=False), (int((x - 20) * paint.S), int((y - 20) * paint.S)))

    # mascot trophy shelf
    sx0, sy0, sx1, sy1 = box(R, "Mascot shelf")
    shelf_y = sy1 - 14
    c.paint(rect(sx0 - 6, shelf_y, sx1 + 6, shelf_y + 14), (150, 100, 60), ow=3, shade=(0, -4, (110, 70, 40)))
    for x in (sx0 + 20, sx1 - 20):
        c.paint(poly([(x - 4, shelf_y + 14), (x + 4, shelf_y + 14), (x + 4, shelf_y + 44), (x - 22, shelf_y + 14)]),
                (90, 90, 96), ow=2.5)
    # garden gnome in a grad cap
    gx = sx0 + 34
    c.paint(ell(gx, shelf_y - 20, 16, 20), (60, 120, 200), ow=3, shade=(2, 2, (40, 90, 160)))
    c.paint(ell(gx, shelf_y - 46, 11, 11), (246, 206, 176), ow=2.5)
    c.paint(poly([(gx - 12, shelf_y - 40), (gx + 12, shelf_y - 40), (gx, shelf_y - 30)], 1), (250, 250, 250), ow=2.2)
    c.paint(poly([(gx - 16, shelf_y - 58), (gx + 16, shelf_y - 58), (gx + 10, shelf_y - 54), (gx - 10, shelf_y - 54)]),
            (30, 30, 40), ow=2.2)
    c.paint(poly([(gx - 20, shelf_y - 62), (gx, shelf_y - 70), (gx + 20, shelf_y - 62), (gx, shelf_y - 56)]),
            (30, 30, 40), ow=2.2)
    c.line([(gx + 12, shelf_y - 62), (gx + 18, shelf_y - 50)], 1.6, (240, 196, 60))
    # plaster goat
    gox = sx0 + 92
    c.paint(ell(gox, shelf_y - 22, 24, 14), (236, 232, 222), ow=3, shade=(2, 2, (196, 190, 184)))
    for lx in (gox - 14, gox - 4, gox + 6, gox + 16):
        c.paint(rect(lx - 2.5, shelf_y - 12, lx + 2.5, shelf_y), (236, 232, 222), ow=2)
    c.paint(ell(gox + 26, shelf_y - 36, 10, 8, 20), (236, 232, 222), ow=2.5)
    c.curve((gox + 24, shelf_y - 44), (gox + 18, shelf_y - 56), (gox + 26, shelf_y - 58), 2.2)
    # giant foam finger
    ffx = sx0 + 150
    c.paint(poly([(ffx - 16, shelf_y), (ffx + 16, shelf_y), (ffx + 18, shelf_y - 40), (ffx + 6, shelf_y - 40),
                  (ffx + 6, shelf_y - 90), (ffx - 6, shelf_y - 90), (ffx - 6, shelf_y - 40), (ffx - 18, shelf_y - 40)], 2),
            (250, 200, 40), shade=(3, 0, (210, 150, 20)))
    c.text(ffx, shelf_y - 20, "#1", 12, (200, 40, 50))
    # empty reserved spot + tag
    c.paint(rect(sx1 - 30, shelf_y - 18, sx1 - 2, shelf_y - 2), (250, 244, 220), ow=2,
            pattern=lambda p: [p.line([(sx1 - 27, shelf_y - 13 + k * 5), (sx1 - 6, shelf_y - 13 + k * 5)], 1, (200, 60, 120))
                               for k in range(2)])

    # lava lamp on an upturned crate + saggy plaid couch behind Dunk
    c.paint(rect(340, 700, 402, WALL_Y + 10), (170, 120, 70), ow=3, pattern=lambda p: [
        p.line([(340, y), (402, y)], 2, (130, 86, 50)) for y in (726, 752, 778)])
    c.paint(poly([(360, 700), (382, 700), (390, 650), (378, 600), (364, 600), (352, 650)], 1), (120, 200, 255, 230), ow=3,
            pattern=lambda p: (p.ell(370, 668, 9, 12, (255, 90, 170)), p.ell(374, 628, 6, 8, (255, 90, 170))))
    c.paint(rect(356, 690, 386, 704), (150, 156, 166), ow=2.5)
    c.paint(rect(362, 592, 380, 604), (150, 156, 166), ow=2.5)
    couch, couch_sh = (150, 90, 60), (110, 60, 40)
    plaid = lambda p: ([p.rect(x, 600, x + 10, 820, (120, 60, 40)) for x in range(400, 760, 40)] +
                       [p.rect(400, y, 760, y + 8, (176, 120, 70)) for y in range(620, 820, 40)])
    c.paint(wonky(420, 620, 740, 720, 4, rng), couch, pattern=plaid, shade=(-5, 0, couch_sh))
    c.paint(wonky(420, 700, 740, 780, 4, rng), lt(couch, 0.1), pattern=plaid, shade=(0, -4, couch_sh))
    for x0 in (404, 712):
        c.paint(wonky(x0, 660, x0 + 40, 790, 4, rng), couch, pattern=plaid, shade=(-3, 0, couch_sh))
    c.paint(ell(520, 712, 30, 10, -8), dk(couch, 0.7), ow=0, opacity=0.5)  # the Dunk-shaped dent

    # ping-pong table
    tx0, ty0, tx1, ty1 = box(R, "Ping-pong table")
    tcx = (tx0 + tx1) / 2
    c.shadow(tcx, ty1 - 6, 140, 12, 0.45)
    for x in (tx0 + 20, tx1 - 20):
        c.paint(rect(x - 5, ty0 + 44, x + 5, ty1 - 8), (60, 60, 66), ow=2.5)
    top = poly([(tx0 + 10, ty0 + 30), (tx1 - 10, ty0 + 30), (tx1, ty0 + 50), (tx0, ty0 + 50)])
    c.paint(top, (40, 130, 80), shade=(0, -4, (26, 90, 56)), pattern=lambda p: (
        p.line([(tx0 + 6, ty0 + 40), (tx1 - 6, ty0 + 40)], 1.6, (240, 250, 240)),
        p.line([(tcx, ty0 + 30), (tcx, ty0 + 50)], 1.6, (240, 250, 240))))
    c.paint(rect(tx0, ty0 + 50, tx1, ty0 + 58), (26, 90, 56), ow=2.5)
    for k in range(10):  # knotted sock net
        x = tcx - 4 + (k % 2) * 4
        c.paint(ell(x, ty0 + 10 + k * 2.2, 5, 3), rng.choice([(250, 250, 250), (230, 60, 60), (60, 90, 200)]), ow=1.4)
    c.line([(tcx - 2, ty0 + 6), (tcx - 2, ty0 + 32)], 2.0)
    for (px, py, col) in ((tx0 + 50, ty0 + 24, (220, 40, 50)), (tx1 - 60, ty0 + 22, (40, 40, 50))):
        c.paint(ell(px, py, 12, 12), col, ow=2.5)
        c.paint(rect(px - 3, py + 10, px + 3, py + 22), (180, 130, 80), ow=2)
    c.paint(ell(tcx + 40, ty0 + 36, 4, 4), (255, 250, 240), ow=1.6)

    # pledge rules whiteboard
    wx0, wy0, wx1, wy1 = box(R, "Pledge rules")
    c.paint(rect(wx0, wy0, wx1, wy1), (200, 204, 212), shade=(-4, -4, (150, 154, 166)), hi=(3, 3, (236, 240, 246)))
    c.paint(rect(wx0 + 8, wy0 + 8, wx1 - 8, wy1 - 8), (250, 252, 252), ow=2.5)
    c.text((wx0 + wx1) / 2, wy0 + 24, "PLEDGE RULES", 14, (40, 70, 180), "Black")
    for k in range(4):
        y = wy0 + 44 + k * 16
        c.text(wx0 + 22, y, f"{k + 1}.", 10, (40, 70, 180), "Bold")
        c.line([(wx0 + 32, y), (wx1 - 22 - rng.uniform(0, 40), y + rng.uniform(-1, 1))], 1.6, (60, 80, 160))
    c.text((wx0 + wx1) / 2, wy1 - 18, "RULE 2, MOOSE!!", 10, (210, 40, 40), "Black")
    c.paint(rect(wx0 + 20, wy1 - 4, wx1 - 20, wy1 + 4), (170, 174, 184), ow=2)
    for k, col in enumerate(((210, 40, 40), (40, 70, 180), (40, 150, 70))):
        c.paint(rrect(wx0 + 28 + k * 18, wy1 - 6, wx0 + 42 + k * 18, wy1 - 1, 2), col, ow=1.4)

    # empty cot (Moose's sprite lies exactly on top when he's off duty)
    mx0, my0, mx1, my1 = box(R, "Sleeping Moose")
    mcx = (mx0 + mx1) / 2
    c.shadow(mcx, my1 - 4, 110, 10, 0.4)
    draw_cot(c, mcx - 115, my1 - 100)

    # washer + dryer
    dx0, dy0, dx1, dy1 = box(R, "Dryer")
    for (x0, x1, label, drum) in ((dx0 - 120, dx0 - 8, "WASH", False), (dx0 + 6, dx1 - 6, "DRY", True)):
        c.shadow((x0 + x1) / 2, dy1 - 4, (x1 - x0) / 2 + 6, 8, 0.4)
        c.paint(rrect(x0, dy0 + 10, x1, dy1 - 6, 6), (236, 238, 242), shade=(-5, 0, (186, 190, 200)),
                hi=(4, 0, (252, 252, 255)))
        c.paint(rect(x0, dy0 + 10, x1, dy0 + 34), (200, 204, 214), ow=2.5)
        cx_, cy_ = (x0 + x1) / 2, dy0 + 86
        c.text(x0 + 22, dy0 + 22, label, 9, (60, 60, 70), "Bold")
        if drum:
            c.paint(ell(x1 - 16, dy0 + 22, 5, 5), (230, 40, 40), ow=1.6)
            c.paint(ell(x1 - 32, dy0 + 22, 6, 6), (90, 90, 100), ow=1.6)

            def beanies(p, cx_=cx_, cy_=cy_):
                p.ell(cx_, cy_, 40, 40, (40, 44, 60))
                for k in range(7):
                    a = k * 0.9
                    bx, by = cx_ + 20 * math.cos(a), cy_ + 18 * math.sin(a) + 6
                    p.ell(bx, by, 12, 8, BEANIE, rot=k * 40)
                    p.ell(bx - 2, by - 2, 5, 3, BEANIE_HI, rot=k * 40)
                p.poly([(cx_ - 30, cy_ + 20), (cx_ - 8, cy_ - 36), (cx_ + 4, cy_ - 36), (cx_ - 18, cy_ + 20)],
                       (200, 220, 240))
        else:
            def beanies(p, cx_=cx_, cy_=cy_):
                p.ell(cx_, cy_, 40, 40, (150, 190, 220))
                p.ell(cx_, cy_ + 16, 36, 18, (200, 230, 250))
        c.paint(ell(cx_, cy_, 44, 44), (180, 186, 198), ow=3, shade=(3, 3, (140, 146, 160)))
        c.paint(ell(cx_, cy_, 34, 34), (40, 44, 60), ow=2.5, pattern=beanies)
    # laundry basket overflowing with togas
    c.paint(poly([(dx1 + 6, dy1 - 50), (dx1 + 76, dy1 - 50), (dx1 + 68, dy1 - 6), (dx1 + 14, dy1 - 6)]), (210, 200, 160),
            ow=3, pattern=lambda p: [p.line([(dx1 + 6, y), (dx1 + 76, y)], 1.6, (170, 160, 120)) for y in
                                     range(int(dy1 - 44), int(dy1 - 6), 8)])
    c.paint(wonky(dx1 + 2, dy1 - 74, dx1 + 80, dy1 - 46, 4, rng), (250, 248, 238), shade=(0, 3, (210, 206, 224)))

    # stairs up (right edge)
    s0x, s0y, s1x, s1y = box(R, "Stairs up")
    n = 9
    wood, wood_sh = (150, 100, 60), (110, 70, 40)
    c.paint(poly([(s0x, s1y), (s1x + 30, s0y - 40), (s1x + 30, s1y)]), (70, 60, 56), ow=0)  # under-stair shadow
    for k in range(n):
        t0 = k / n
        x = s0x + (s1x + 30 - s0x) * t0
        y = s1y - (s1y - s0y + 40) * t0
        w = (s1x + 30 - s0x) / n
        h = (s1y - s0y + 40) / n
        c.paint(rect(x, y - h, x + w + 40, y - h + 10), wood, ow=3, hi=(0, -2, lt(wood, 0.3)))
        c.paint(rect(x, y - h + 10, x + w + 40, y), wood_sh, ow=2.5)
    c.paint(cap([(s0x + 10, s1y - 100), (s1x + 30, s0y - 140)], 7), (130, 86, 50), shade=(0, 2, wood_sh))  # rail
    for k in range(0, n, 2):
        t0 = (k + 0.5) / n
        x = s0x + 10 + (s1x + 20 - s0x) * t0
        y = s1y - 100 - (s1y - s0y + 40) * t0
        c.line([(x, y), (x, y + 96)], 3.5, (130, 86, 50))
    c.paint(rect(s1x - 40, 0, W_BG + 10, s0y - 70), (40, 30, 26), ow=3)  # opening up to the party
    c.paint(rect(s1x - 30, 0, W_BG, s0y - 80), (180, 60, 140), ow=0, opacity=0.5)

    # bare bulb on a cord
    bbx = 1000
    c.line([(bbx, 110), (bbx, 300)], 2.2)
    c.paint(rect(bbx - 6, 300, bbx + 6, 314), (120, 120, 130), ow=2)
    c.paint(ell(bbx, 326, 12, 14), (255, 240, 180), ow=2.5)

    lights = [(bbx, 330, 820, 0.62, (255, 230, 170)), (370, 650, 260, 0.45, (255, 100, 200)),
              (690, 210, 200, 0.2, (150, 150, 255)), (s1x - 40, 120, 300, 0.4, (255, 120, 220))]
    paint.light_pass(c, 0.5, lights, vign=0.5)
    c.glow(bbx, 326, 120, (255, 240, 190), 0.7)
    c.glow(370, 650, 70, (255, 120, 200), 0.5)
    c.save("bg_frat_basement.png")


# =========================================================================== new item icons
def paint_icon_volcano_smoothie():
    def draw(c):
        cup = poly([(36, 34), (92, 34), (84, 120), (44, 120)], 1)
        c.paint(cup, ("v", (255, 170, 60), (240, 80, 40)), shade=(5, 0, (200, 60, 30)),
                pattern=lambda p: [p.ell(50 + k * 9, 60 + (k % 3) * 18, 3, 3, (255, 220, 120)) for k in range(5)])
        c.paint(poly([(40, 44), (52, 44), (50, 110), (46, 110)]), (255, 255, 255), ow=0, opacity=0.35)
        c.paint(ell(64, 34, 32, 9), (250, 250, 255, 200), ow=4)
        c.paint(ell(64, 26, 24, 12), (250, 250, 255, 200), ow=4)
        c.paint(cap([(70, 24), (82, 2)], 7), (255, 255, 255), ow=4,
                pattern=lambda p: [p.line([(64 + k * 4, 30 - k * 6), (78 + k * 4, 24 - k * 6)], 3, (230, 50, 80))
                                   for k in range(5)])
        c.paint(poly([(88, 38), (110, 30), (118, 40), (98, 52)], 2), (220, 30, 40), hi=(-2, -2, (255, 120, 110)))
        c.paint(poly([(108, 30), (114, 22), (120, 30)], 1), (60, 150, 60), ow=3)
    icon("icon_volcano_smoothie.png", 0, draw)


def paint_icon_clip_on_tie():
    def draw(c):
        navy, navy_sh = (44, 56, 124), (26, 32, 80)
        c.paint(poly([(50, 20), (78, 20), (74, 38), (54, 38)], 1), navy, shade=(2, 2, navy_sh))
        c.paint(poly([(54, 38), (74, 38), (88, 100), (64, 122), (40, 100)], 1), navy, shade=(4, 0, navy_sh),
                hi=(-3, 0, (80, 96, 170)),
                pattern=lambda p: [p.ell(56 + (k % 2) * 14, 52 + k * 13, 3.2, 2.6, (240, 200, 80)) for k in range(5)])
        c.paint(rrect(44, 12, 84, 22, 3), (210, 214, 224), hi=(0, -2, (250, 250, 255)))
        c.line([(52, 22), (52, 32)], 3, (170, 176, 190))
    icon("icon_clip_on_tie.png", -12, draw)


def paint_icon_pledge_beanie():
    def draw(c):
        pledge_beanie(c, 70, 92, 46, 0)
    icon("icon_pledge_beanie.png", -8, draw)


def paint_icon_disco_record():
    def draw(c):
        draw_record_sleeve(c, 10, 22, 84)
    icon("icon_disco_record.png", 0, draw)


ASSETS.update({"bg_sorority_parlor": paint_sorority_parlor, "bg_frat_basement": paint_frat_basement,
               "icon_volcano_smoothie": paint_icon_volcano_smoothie, "icon_clip_on_tie": paint_icon_clip_on_tie,
               "icon_pledge_beanie": paint_icon_pledge_beanie, "icon_disco_record": paint_icon_disco_record})



def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        # Rooms and characters are now painted by the *_style2.py scripts; a plain run
        # only repaints item icons. Name a file explicitly to paint the old version.
        if not want and name.startswith(("bg_", "hs_", "player_")):
            continue
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
