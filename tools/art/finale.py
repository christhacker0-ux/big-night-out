#!/usr/bin/env python3
"""
Big Night Out -- Finale art (the Speed Daters Live TV studio).

Original art, drawn procedurally with the helpers in paint.py (same style: bold dark outlines,
warm saturated cel shading, big-headed characters). Props are painted exactly inside the hotspot
boxes read from Assets/_Project/World/finale.json, so the art and the click areas line up.

Usage:  python3 tools/art/finale.py            # paint everything
        python3 tools/art/finale.py chet icon  # only assets whose name contains these words
Output: Assets/_Project/Art/Painted/bg_tv_studio.png, hs_chet_studwell.png, icon_<item>.png
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, W_BG, H_BG, WALL_Y, Canvas, mix, dk, lt, rot_pts, bez, poly, ell, rect, rrect,  # noqa: E402
                   wonky, cap, eye, shoe_shape, light_pass, sparkle, icon)

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "finale.json")


def boxes():
    """Hotspot name -> (x0, y0, x1, y1) in background pixels, from the room JSON."""
    room = [r for r in json.load(open(WORLD))["rooms"] if r["id"] == "tv_studio"][0]
    out = {}
    for h in room["hotspots"]:
        (fx, fy), (w, hh) = h["feet"], h["size"]
        out[h["name"]] = ((fx - w / 2 + 9.6) * 100, (5.4 - fy - hh) * 100, (fx + w / 2 + 9.6) * 100, (5.4 - fy) * 100)
    return out


def px(x, y):
    return (x + 9.6) * 100, (5.4 - y) * 100


def star(c, x, y, r, col, ow=1.4):
    c.paint(poly([(x, y - r), (x + r * 0.3, y - r * 0.3), (x + r, y), (x + r * 0.3, y + r * 0.3), (x, y + r),
                  (x - r * 0.3, y + r * 0.3), (x - r, y), (x - r * 0.3, y - r * 0.3)]), col, ow=ow)


# =========================================================================== audience busts
SKINS = [(255, 214, 178), (240, 186, 140), (206, 142, 100), (160, 104, 72), (120, 76, 56), (250, 200, 170)]


def bust(c, x, yb, skin, outfit, hair, style, extra=None, pre=None, s=1.0, face="smile", look=1.5, lid=0.0, opat=None):
    """A small seated audience member, head + shoulders, base at (x, yb). Faces the viewer, eyes toward the set."""
    sk_sh = dk(skin, 0.82)
    hx, hy = x, yb - 56 * s
    hs = hair
    hsh = dk(hair, 0.72)
    # hair behind the head
    if style in ("long", "pony_long"):
        c.paint(poly([(hx - 18 * s, hy - 8 * s), (hx + 18 * s, hy - 8 * s), (hx + 21 * s, hy + 30 * s),
                      (hx - 21 * s, hy + 30 * s)], 2), hs, ow=2.5, shade=(2, 0, hsh))
    elif style == "bob":
        c.paint(poly([(hx - 19 * s, hy - 6 * s), (hx + 19 * s, hy - 6 * s), (hx + 19 * s, hy + 14 * s),
                      (hx - 19 * s, hy + 14 * s)], 2), hs, ow=2.5, shade=(2, 0, hsh))
    elif style == "wild":
        r2 = random.Random(int(x))
        blob = ell(hx, hy - 4 * s, 26 * s, 24 * s)
        for k in range(9):
            a = math.radians(k * 40 + r2.uniform(-10, 10))
            blob = blob + ell(hx + 24 * s * math.cos(a), hy - 4 * s + 22 * s * math.sin(a), 9 * s, 9 * s)
        c.paint(blob, hs, ow=2.5, shade=(2, 2, hsh), hi=(-2, -2, lt(hs, 0.3), 1))
    if pre:
        pre(c, x, yb, s)
    # torso + neck
    torso = poly([(x - 25 * s, yb), (x - 23 * s, yb - 24 * s), (x - 13 * s, yb - 35 * s), (x + 13 * s, yb - 35 * s),
                  (x + 23 * s, yb - 24 * s), (x + 25 * s, yb)], 2)
    c.paint(cap([(x, yb - 44 * s), (x, yb - 34 * s)], 9 * s), skin, ow=2.5, shade=(2, 0, sk_sh))
    c.paint(torso, outfit, ow=2.5, shade=(3, 0, dk(outfit, 0.75)), hi=(-2, 2, lt(outfit, 0.3), 1), pattern=opat)
    # head
    c.paint(ell(hx, hy, 15 * s, 16.5 * s), skin, ow=2.5, shade=(2.5, 2, sk_sh), hi=(-2, 2, lt(skin, 0.25), 1.5))
    for ex in (-5.5, 5.5):
        c.paint(ell(hx + ex * s, hy + 1 * s, 3.6 * s, 4.6 * s), (255, 255, 255), ow=1.6)
        c.paint(ell(hx + (ex + look) * s, hy + 1.5 * s, 1.7 * s, 2.1 * s), OUT, ow=0)
        if lid:
            c.paint(rect(hx + (ex - 4) * s, hy - 4 * s, hx + (ex + 4) * s, hy + (-4 + 9 * lid) * s), skin, ow=0,
                    clip=ell(hx + ex * s, hy + 1 * s, 3.6 * s, 4.6 * s))
            c.line([(hx + (ex - 3.6) * s, hy + (-4 + 9 * lid) * s), (hx + (ex + 3.6) * s, hy + (-4 + 9 * lid) * s)],
                   1.4)
    for ex in (-9, 9):
        c.paint(ell(hx + ex * s, hy + 7 * s, 3 * s, 1.8 * s), (255, 120, 130), ow=0, opacity=0.5)
    if face == "smile":
        m = [(hx - 7 * s, hy + 8.5 * s), (hx + 7 * s, hy + 8.5 * s)] + \
            [(hx + 7 * s * math.cos(math.radians(a)), hy + 8.5 * s + 5.5 * s * math.sin(math.radians(a)))
             for a in range(20, 170, 25)]
        c.paint(poly(m), (120, 24, 44), ow=1.5,
                pattern=lambda p: p.rect(hx - 8 * s, hy + 8 * s, hx + 8 * s, hy + 10.5 * s, (255, 255, 255)))
    elif face == "open":
        c.paint(ell(hx, hy + 11 * s, 3.6 * s, 4 * s), (120, 24, 44), ow=1.5,
                pattern=lambda p: p.ell(hx, hy + 13.5 * s, 2.4 * s, 1.4 * s, (255, 120, 140)))
    elif face == "flat":
        c.line([(hx - 4 * s, hy + 10 * s), (hx + 4 * s, hy + 10 * s)], 1.6)
    elif face == "smirk":
        c.line([(hx - 4 * s, hy + 10 * s), (hx + 2 * s, hy + 10 * s), (hx + 5 * s, hy + 8 * s)], 1.6)
    # hair in front
    if style in ("long", "bob", "pony", "pony_long", "short", "bun"):
        cap_pts = [(hx - 16 * s, hy + 2 * s), (hx - 15 * s, hy - 12 * s), (hx - 6 * s, hy - 19 * s),
                   (hx + 8 * s, hy - 19 * s), (hx + 16 * s, hy - 10 * s), (hx + 16 * s, hy + 2 * s),
                   (hx + 11 * s, hy - 7 * s), (hx, hy - 9 * s), (hx - 9 * s, hy - 6 * s)]
        c.paint(poly(cap_pts, 2), hs, ow=2.5, shade=(2, 2, hsh), hi=(-2, 2, lt(hs, 0.3), 1))
    if style == "bun":
        c.paint(ell(hx, hy - 22 * s, 8 * s, 7 * s), hs, ow=2.5, shade=(2, 2, hsh))
    if style in ("pony", "pony_long"):
        c.paint(cap([(hx + 14 * s, hy - 10 * s), (hx + 24 * s, hy), (hx + 22 * s, hy + 16 * s)], 7 * s), hs, ow=2.5,
                shade=(2, 0, hsh))
    if extra:
        extra(c, x, yb, s, hx, hy)


def generic_person(c, x, yb, rng, s=1.0):
    skin = rng.choice(SKINS)
    hair = rng.choice([(60, 40, 30), (30, 24, 24), (150, 90, 40), (230, 190, 100), (110, 60, 40), (90, 90, 96)])
    outfit = rng.choice([(70, 120, 180), (200, 90, 60), (90, 150, 90), (180, 160, 60), (130, 80, 150), (60, 160, 160),
                         (200, 120, 150), (110, 110, 120)])
    style = rng.choice(["short", "short", "long", "bob", "pony", "bun"])
    bust(c, x, yb, skin, outfit, hair, style, s=s, face=rng.choice(["smile", "open", "smile"]),
         look=rng.uniform(0.5, 2.0))


# --- the ten women, each with something that says who she is
def lacey(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(hx - 16, hy - 10), (hx + 16, hy - 10), (hx + 14, hy - 4), (hx - 14, hy - 4)], 1),
                (230, 60, 110), ow=2.2)  # pink bandana band
        c.paint(poly([(x - 8, yb - 35), (x, yb - 24), (x + 8, yb - 35)]), (255, 246, 248), ow=2)
        c.line([(x - 22, yb - 22), (x - 10, yb - 30), (x + 10, yb - 30), (x + 22, yb - 22)], 1.6, (255, 236, 240))
    bust(c, x, yb, (234, 172, 128), (255, 112, 168), (250, 198, 92), "long", ex, face="open", lid=0.2)


def ivy(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        for gx in (-6, 6):
            c.paint(ell(hx + gx, hy + 1, 6, 5), (30, 26, 40), ow=2)  # the famous sunglasses
            c.paint(ell(hx + gx - 2, hy - 1, 1.6, 1.2), (160, 170, 220), ow=0)
        c.line([(hx - 1, hy), (hx + 1, hy)], 1.6)
        c.paint(rect(x - 5, yb - 32, x + 5, yb), (240, 236, 220), ow=0)
        c.paint(ell(x + 18, yb - 14, 3, 3), (255, 255, 255), ow=1.4)  # daisy pin
    bust(c, x, yb, (238, 196, 160), (214, 160, 50), (130, 84, 46), "pony_long", ex, face="smile")


def tess(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        for k in range(7):  # pearls
            c.paint(ell(x - 9 + k * 3, yb - 33 + abs(k - 3) * -0.6 + 3, 1.7, 1.7), (255, 252, 240), ow=1)
        c.paint(poly([(hx - 15, hy - 11), (hx + 15, hy - 11), (hx + 13, hy - 7), (hx - 13, hy - 7)], 1),
                (240, 90, 150), ow=2)  # pink headband
        # clipboard held up
        c.paint(rrect(x + 6, yb - 30, x + 30, yb - 2, 2), (186, 130, 72), ow=2.2)
        c.paint(rect(x + 10, yb - 26, x + 27, yb - 4), (250, 250, 244), ow=1.6,
                pattern=lambda p: [p.line([(x + 12, yb - 22 + k * 4), (x + 25, yb - 22 + k * 4)], 1, (150, 170, 210))
                                   for k in range(5)])
        c.paint(rect(x + 14, yb - 32, x + 22, yb - 27), (170, 176, 186), ow=1.6)
    bust(c, x, yb, (250, 214, 186), (245, 130, 170), (120, 70, 40), "pony", ex, face="smile")


def bree(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(x - 9, yb - 35), (x, yb - 26), (x + 9, yb - 35)]), (255, 255, 255), ow=2)  # collar
        c.paint(rect(x + 8, yb - 22, x + 20, yb - 16), (255, 255, 255), ow=1.5)  # name tag
        c.line([(hx + 4, hy - 26), (hx + 14, hy - 16)], 2.4, (240, 196, 60))  # pencil in the bun
    bust(c, x, yb, (252, 214, 188), (120, 190, 200), (214, 90, 40), "bun", ex, face="smile")


def lou(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        # store vest over a grey tee, arms crossed
        c.paint(poly([(x - 23, yb), (x - 21, yb - 24), (x - 12, yb - 34), (x - 4, yb - 34), (x - 6, yb)], 1),
                (40, 130, 70), ow=2)
        c.paint(poly([(x + 23, yb), (x + 21, yb - 24), (x + 12, yb - 34), (x + 4, yb - 34), (x + 6, yb)], 1),
                (40, 130, 70), ow=2)
        c.paint(cap([(x - 20, yb - 12), (x + 20, yb - 14)], 9), (110, 110, 118), ow=2.2)
        c.paint(ell(x - 20, yb - 12, 4.5, 4.5), (150, 100, 72), ow=1.8)
        c.paint(ell(x + 20, yb - 14, 4.5, 4.5), (150, 100, 72), ow=1.8)
        c.paint(poly([(hx - 16, hy - 6), (hx - 14, hy - 18), (hx, hy - 23), (hx + 14, hy - 18), (hx + 16, hy - 6)], 2),
                (240, 130, 40), ow=2.2)  # orange beanie
        c.paint(cap([(hx - 14, hy - 2), (hx - 18, hy + 30)], 6), (34, 28, 30), ow=2)  # braid
        c.line([(hx - 9, hy - 6 + 2), (hx - 2, hy - 4 + 2)], 1.8)  # flat brows
        c.line([(hx + 2, hy - 2), (hx + 9, hy - 4)], 1.8)
    bust(c, x, yb, (150, 100, 72), (110, 110, 118), (34, 28, 30), "short", ex, face="flat", lid=0.35)


def dolly(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.curve((x - 14, yb - 36), (x, yb - 26), (x + 14, yb - 36), 4, (40, 40, 46))  # headphones round the neck
        c.paint(ell(x - 15, yb - 36, 5, 6), (60, 220, 230), ow=2)
        c.paint(ell(x + 15, yb - 36, 5, 6), (60, 220, 230), ow=2)
        for k, col in enumerate(((120, 255, 120), (255, 120, 220), (255, 240, 90))):  # glow sticks held up
            c.paint(cap([(x - 30 + k * 4, yb - 24), (x - 36 + k * 6, yb - 60)], 4), col, ow=1.8)
        c.glow(x - 30, yb - 44, 22, (200, 255, 200), 0.35)
    bust(c, x, yb, (230, 180, 150), (70, 110, 200), (255, 90, 180), "pony_long", ex, face="open")


def mina(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(x - 9, yb - 35), (x - 4, yb), (x - 20, yb)], 1), (250, 250, 250), ow=2)  # lab coat lapels
        c.paint(poly([(x + 9, yb - 35), (x + 4, yb), (x + 20, yb)], 1), (250, 250, 250), ow=2)
        # Professor Nibbles on her shoulder
        c.paint(ell(x + 20, yb - 40, 7, 6), (230, 170, 100), ow=2, shade=(1.5, 1.5, (200, 130, 80)))
        c.paint(ell(x + 16, yb - 45, 2.4, 2.4), (255, 190, 190), ow=1.4)
        c.paint(ell(x + 18, yb - 40, 1.1, 1.1), OUT, ow=0)
    bust(c, x, yb, (250, 220, 196), (250, 250, 250), (150, 80, 220), "wild", ex, face="open")


def sky(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(hx - 16, hy - 6), (hx - 14, hy - 18), (hx, hy - 23), (hx + 14, hy - 18), (hx + 16, hy - 6)], 2),
                (240, 130, 40), ow=2.2)  # beanie
        c.paint(rect(hx - 17, hy - 9, hx + 17, hy - 4), dk((240, 130, 40), 0.8), ow=2)
        # megaphone raised
        c.paint(poly([(x + 14, yb - 46), (x + 34, yb - 58), (x + 38, yb - 40), (x + 18, yb - 38)], 1), (230, 60, 50),
                ow=2.2, shade=(0, 2, (170, 30, 40)))
        c.paint(ell(x + 36, yb - 49, 3.5, 9.5, 20), (255, 255, 250), ow=2)
        c.paint(ell(x + 14, yb - 34, 5, 5), (160, 104, 72), ow=1.8)
    bust(c, x, yb, (160, 104, 72), (60, 110, 200), (30, 24, 24), "long", ex, face="open")


def mimi(c, x, yb):
    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(hx - 16, hy - 12), (hx - 2, hy - 22), (hx + 18, hy - 16), (hx + 14, hy - 10)], 2),
                (200, 40, 50), ow=2)  # beret
        c.paint(ell(hx + 1, hy - 23, 2, 2), (200, 40, 50), ow=1.5)
        for k in (-4, 4):  # little painted tear and brows
            c.line([(hx + k * 1.4 - 2, hy - 6), (hx + k * 1.4 + 2, hy - 7)], 1.4)
        c.paint(ell(hx - 5, hy + 7, 1, 2), (80, 120, 230), ow=0)
        # white-gloved hands pressing an invisible wall
        for gx in (-24, 24):
            c.paint(ell(x + gx, yb - 50, 6, 7), (255, 255, 255), ow=2)
            c.line([(x + gx, yb - 43), (x + gx * 0.8, yb - 30)], 4, (255, 255, 255))
    stripes = lambda p: [p.rect(x - 26, yb - 30 + k * 8, x + 26, yb - 26 + k * 8, (30, 30, 40)) for k in range(4)]
    bust(c, x, yb, (255, 250, 246), (250, 250, 250), (30, 26, 34), "short", ex, face="smile", opat=stripes)


def jett(c, x, yb):
    def pre(c, x, yb, s):
        # tall green spikes behind the head
        spikes = []
        for k in range(6):
            a = -150 + k * 24
            spikes += [(x + 12 * math.cos(math.radians(a)), yb - 66 + 12 * math.sin(math.radians(a))),
                       (x + 30 * math.cos(math.radians(a + 12)), yb - 66 + 30 * math.sin(math.radians(a + 12)))]
        c.paint(poly([(x - 8, yb - 66)] + spikes + [(x + 8, yb - 66)]), (110, 230, 70), ow=2.5,
                shade=(2, 2, (60, 170, 50)))

    def ex(c, x, yb, s, hx, hy):
        c.paint(poly([(x - 23, yb), (x - 21, yb - 24), (x - 12, yb - 34), (x - 3, yb - 34), (x - 8, yb)], 1),
                (40, 36, 44), ow=2, hi=(-1, 1, (100, 96, 110)))  # leather jacket
        c.paint(poly([(x + 23, yb), (x + 21, yb - 24), (x + 12, yb - 34), (x + 3, yb - 34), (x + 8, yb)], 1),
                (40, 36, 44), ow=2, hi=(-1, 1, (100, 96, 110)))
        for k in range(3):
            c.paint(ell(x - 16 + k * 4, yb - 24 + k * 3, 1.4, 1.4), (220, 220, 230), ow=0.8)
        c.paint(ell(hx + 15, hy + 4, 2, 2), (0, 0, 0, 0), ow=1.4, oc=(220, 220, 230))  # earring
    bust(c, x, yb, (240, 200, 176), (230, 40, 60), (110, 230, 70), "none", ex, pre=pre, face="flat", lid=0.5)


# =========================================================================== studio background
def neon_text(c, x, y, s, size, col, glow_col, angle=0, kind="Italic"):
    c.text(x, y, s, size, col, kind, stroke=3, sc=dk(glow_col, 0.6), angle=angle)


def paint_tv_studio():
    B = boxes()
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(606)

    # --- back wall: deep plum with acoustic foam panels on the left half
    wall_top, wall_bot = (44, 26, 62), (92, 46, 96)
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, wall_top, wall_bot), ow=0)
    panel = (110, 58, 112)
    for row, y in enumerate(range(130, 700, 92)):
        for x in range(200 + (row % 2) * 30, 1170, 104):
            if x + 92 > 1180:
                continue
            c.paint(rrect(x, y, x + 92, y + 82, 10), ("v", lt(panel, 0.08), dk(panel, 0.85)), ow=3,
                    shade=(-3, -3, dk(panel, 0.7)), hi=(3, 3, lt(panel, 0.2), 2))
            for k in range(3):
                c.line([(x + 14, y + 22 + k * 20), (x + 78, y + 22 + k * 20)], 2, dk(panel, 0.7), opacity=0.6)
    # dark ceiling + lighting truss
    c.paint(rect(0, 0, W_BG, 90), (22, 14, 30), ow=0)
    truss = (190, 194, 206)
    c.paint(rect(-10, 40, W_BG + 10, 80), (0, 0, 0, 0), ow=3)
    c.line([(-10, 42), (W_BG + 10, 42)], 5, truss)
    c.line([(-10, 78), (W_BG + 10, 78)], 5, truss)
    for x in range(-10, W_BG + 10, 36):
        c.line([(x, 42), (x + 36, 78)], 2.5, truss)
        c.line([(x, 78), (x, 42)], 2.0, dk(truss, 0.8))
    spots = [(330, 1), (700, 1), (1260, -1), (1560, -1), (1840, -1)]
    for sx, d in spots:
        c.paint(rect(sx - 4, 80, sx + 4, 96), (60, 60, 70), ow=2.5)
        c.paint(poly(rot_pts([(sx - 18, 96), (sx + 18, 96), (sx + 14, 140), (sx - 14, 140)], -25 * d, sx, 96)),
                (40, 40, 52), shade=(-3, 0), hi=(3, 0, (90, 90, 110), 2))

    # --- ON AIR light over the camera
    c.paint(rrect(870, 236, 1010, 290, 8), (60, 20, 26), shade=(-3, -3), hi=(3, 3, (120, 50, 60), 2))
    c.paint(rrect(880, 244, 1000, 282, 5), (240, 40, 50), ow=2.5, hi=(0, 3, (255, 140, 130)))
    c.text(940, 263, "ON AIR", 22, (255, 250, 230), "Black", stroke=1.5, sc=(140, 10, 20))
    c.line([(940, 236), (940, 96)], 2.5, (40, 40, 50))

    # --- set: sequin curtain backdrop behind the riser
    cur = (176, 34, 120)
    sx0, sx1 = 1175, 1930

    def sequin(p):
        r2 = random.Random(5)
        for x in range(sx0, sx1, 34):
            p.line([(x, 110), (x + 4, 704)], 5, dk(cur, 0.68))
            p.line([(x + 12, 110), (x + 14, 704)], 2.5, lt(cur, 0.25))
        for _ in range(420):
            x, y = r2.uniform(sx0, sx1), r2.uniform(110, 700)
            if r2.random() < 0.18:
                paint.sparkle(p, x, y, r2.uniform(3, 6), (255, 230, 250))
            else:
                p.ell(x, y, 1.6, 1.6, r2.choice([(255, 150, 210), (255, 220, 120), (240, 120, 200)]))
    c.paint(rect(sx0, 96, sx1, 704), ("vy", 96, 704, dk(cur, 0.7), cur), pattern=sequin, ow=3)
    # swagged valance across the top of the set
    val = (120, 20, 90)
    pts = [(sx0 - 4, 92), (sx1 + 4, 92), (sx1 + 4, 128)]
    n = 7
    for i in range(n):
        xa = sx1 - (sx1 - sx0) * (i + 1) / n
        xm = (sx1 - (sx1 - sx0) * i / n + xa) / 2
        pts += [(xm, 160), (xa, 128)]
    c.paint(poly(pts, 2), val, shade=(0, -6, dk(val, 0.7)), hi=(0, 4, lt(val, 0.3), 2),
            pattern=lambda p: [p.ell(sx0 + (sx1 - sx0) * (i + 0.5) / n, 150, 7, 7, (255, 210, 90)) for i in range(n)])

    # --- giant neon logo: heart + SPEED DATERS LIVE
    hx, hy = 1560, 250
    heart = ell(hx - 60, hy - 30, 72, 66) + ell(hx + 60, hy - 30, 72, 66) + poly(
        [(hx - 128, hy - 6), (hx + 128, hy - 6), (hx, hy + 120)], 1)
    c.paint(heart, (40, 10, 50), ow=5, oc=(255, 90, 170))
    c.paint(heart, (0, 0, 0, 0), ow=2, oc=(255, 220, 240))
    c.glow(hx, hy, 260, (255, 60, 160), 0.38)
    neon_text(c, hx, hy - 54, "SPEED", 58, (255, 236, 90), (255, 140, 30), angle=4)
    neon_text(c, hx, hy + 6, "DATERS", 58, (255, 236, 90), (255, 140, 30), angle=4)
    c.paint(rrect(hx - 70, hy + 46, hx + 70, hy + 88, 12), (230, 30, 60), ow=4, oc=(255, 230, 240),
            hi=(0, 4, (255, 120, 130)))
    c.text(hx, hy + 67, "LIVE!", 30, (255, 255, 255), "Black")
    for k in range(16):  # marquee bulbs around the heart
        a = math.radians(k * 360 / 16)
        bx, by = hx + 200 * math.cos(a), hy + 10 + 150 * math.sin(a)
        c.paint(ell(bx, by, 7, 7), (255, 240, 170), ow=2.5)
        c.glow(bx, by, 22, (255, 220, 120), 0.4)

    # --- riser (top 700-742, front face 742-800) across the set
    rx0 = 1165
    wd = (60, 40, 90)
    c.paint(poly([(rx0 + 10, 700), (W_BG + 10, 700), (W_BG + 10, 744), (rx0, 744)]), ("v", lt(wd, 0.25), wd),
            hi=(0, 3, lt(wd, 0.4)),
            pattern=lambda p: [p.line([(x, 702), (x - 6, 742)], 1.4, dk(wd, 0.7)) for x in range(rx0 + 60, W_BG, 90)])
    c.paint(rect(rx0, 742, W_BG + 10, 802), ("v", (230, 40, 120), (150, 20, 90)), shade=(0, -6, (110, 10, 70)))
    c.paint(rect(rx0, 738, W_BG + 10, 752), (240, 196, 80), ow=3, hi=(0, 3, (255, 236, 150)))
    for x in range(rx0 + 24, W_BG, 46):
        c.paint(ell(x, 776, 6, 6), (255, 244, 190), ow=2.5)
        c.glow(x, 776, 20, (255, 210, 120), 0.35)

    # --- hosting podium (beside Roxy, on the riser)
    rox = B["Roxy Vale"]
    px0 = rox[2] + 8
    pod = (236, 50, 140)
    c.shadow(px0 + 62, 740, 74, 8, 0.5)
    c.paint(poly([(px0, 612), (px0 + 124, 612), (px0 + 112, 742), (px0 + 12, 742)], 1), ("h", lt(pod, 0.15), dk(pod, 0.8)),
            shade=(-6, 0, dk(pod, 0.65)), hi=(5, 0, lt(pod, 0.35), 3))
    c.paint(rrect(px0 - 8, 598, px0 + 132, 618, 4), (250, 214, 90), hi=(0, 3, (255, 244, 180)), shade=(0, -3))
    c.paint(ell(px0 + 62, 676, 30, 30), (255, 240, 250), ow=3,
            pattern=lambda p: (p.ell(px0 + 52, 670, 11, 10, (240, 40, 100)), p.ell(px0 + 72, 670, 11, 10, (240, 40, 100)),
                               p.poly([(px0 + 42, 674), (px0 + 82, 674), (px0 + 62, 694)], (240, 40, 100))))
    c.paint(rect(px0 + 20, 586, px0 + 70, 600), (250, 250, 240), ow=2)  # cue cards
    c.line([(px0 + 26, 592), (px0 + 60, 592)], 1.2, (150, 150, 180))

    # --- sound board on a stand (on the riser)
    sb = B["Sound board"]
    x0, y0, x1, y1 = sb
    c.shadow((x0 + x1) / 2, y1 - 2, (x1 - x0) / 2, 7, 0.5)
    for lx in (x0 + 16, x1 - 16):
        c.paint(rect(lx - 5, y0 + 60, lx + 5, y1 - 2), (60, 60, 70), ow=2.5)
    c.paint(rect(x0 + 10, y1 - 20, x1 - 10, y1 - 12), (60, 60, 70), ow=2.5)
    desk = (54, 52, 66)
    c.paint(poly([(x0 + 4, y0 + 22), (x1 - 4, y0 + 22), (x1, y0 + 66), (x0, y0 + 66)]), desk,
            shade=(0, -4, dk(desk, 0.7)), hi=(0, 3, lt(desk, 0.3)))
    for k in range(9):  # faders
        fx = x0 + 74 + k * 9
        c.line([(fx, y0 + 32), (fx - 1, y0 + 58)], 1.6, (20, 20, 26))
        c.paint(rect(fx - 3, y0 + 36 + (k * 7) % 18, fx + 3, y0 + 42 + (k * 7) % 18), (230, 230, 240), ow=1.4)
    for k, col in enumerate(((255, 80, 80), (255, 210, 60), (90, 220, 120))):
        c.paint(ell(x0 + 120 + k * 12, y0 + 27, 3, 3), col, ow=1.4)
    # two tape decks, labelled 1 and 2
    for k in range(2):
        dx = x0 + 8 + k * 32
        c.paint(rrect(dx, y0 + 30, dx + 28, y0 + 60, 3), (30, 30, 36), ow=2)
        c.paint(rect(dx + 4, y0 + 36, dx + 24, y0 + 50), (90, 100, 120), ow=1.4)
        c.text(dx + 14, y0 + 55, str(k + 1), 7, (255, 230, 120), "Black")
    # tape sticking out of deck 1 (Chet's, gold)
    c.paint(rect(x0 + 12, y0 + 22, x0 + 32, y0 + 34), (240, 200, 60), ow=1.8)
    # little monitor speaker on top
    c.paint(rrect(x1 - 42, y0, x1 - 10, y0 + 24, 3), (40, 40, 48), ow=2.5)
    c.paint(ell(x1 - 26, y0 + 12, 7, 7), (20, 20, 26), ow=1.6)
    c.text((x0 + x1) / 2, y0 + 82, "SOUND", 9, (220, 220, 240), "Black")

    # --- Chet's floor mark (under his feet) and Dex's contestant mark
    def tape_x(cx, cy, w, h, col, label, lcol):
        c.paint(cap([(cx - w, cy - h), (cx + w, cy + h)], 9), col, ow=2.5)
        c.paint(cap([(cx - w, cy + h), (cx + w, cy - h)], 9), col, ow=2.5)
        c.text(cx, cy + h + 14, label, 13, lcol, "Black", stroke=1.5, sc=OUT)

    # --- floor: glossy studio floor
    fl = (40, 30, 60)
    c.paint(rect(0, WALL_Y, W_BG, H_BG), ("vy", WALL_Y, H_BG, (128, 78, 140), (70, 44, 96)), ow=0)
    for k in range(9):  # glossy streaks
        gx = 120 + k * 210
        c.paint(poly([(gx, 812), (gx + 40, 812), (gx + 10, 1060), (gx - 40, 1060)]), (255, 230, 250), ow=0,
                opacity=0.05)
    # reflection of the neon heart + sequins
    c.paint(ell(1560, 900, 300, 60), (255, 60, 160), ow=0, opacity=0.14)
    c.paint(ell(1560, 900, 160, 30), (255, 220, 120), ow=0, opacity=0.10)
    for x in range(-600, W_BG + 600, 140):  # floor panel seams in perspective
        c.line([(960 + (x - 960) * 0.55, WALL_Y), (x, H_BG)], 1.6, (14, 8, 24), opacity=0.5)
    for y in (830, 885, 960, 1050):
        c.line([(0, y), (W_BG, y)], 1.4, (14, 8, 24), opacity=0.4)
    # cables snaking along the back of the floor (flat)
    c.line(bez((830, 800), (700, 830), (520, 812)), 4, (20, 20, 26))
    c.line(bez((980, 796), (1080, 820), (1170, 806)), 4, (20, 20, 26))
    # floor edge under the riser and the wall
    c.paint(rect(-10, WALL_Y - 10, rx0, WALL_Y + 4), (30, 18, 40), ow=3)
    # re-paint riser front bottom edge over the floor
    c.line([(rx0, 802), (W_BG, 802)], 3)

    chet = B["Chet Studwell"]
    tape_x((chet[0] + chet[2]) / 2, chet[3] - 4, 28, 9, (90, 220, 255), "CHET ★", (90, 220, 255))
    m = B["Contestant mark"]
    mx, my = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2 - 8
    c.paint(ell(mx, my + 4, 74, 18), (255, 240, 120), ow=0, opacity=0.12)
    tape_x(mx, my, 40, 11, (255, 226, 60), "DEC", (255, 226, 60))

    # --- applause sign hanging from the truss
    ap = B["Applause sign"]
    ax0, ay0, ax1, ay1 = ap
    for cx in (ax0 + 30, ax1 - 30):
        c.line([(cx, 80), (cx, ay0)], 2.5, (150, 150, 160))
    c.paint(rrect(ax0, ay0, ax1, ay1, 10), (60, 22, 30), shade=(-4, -4), hi=(4, 4, (120, 50, 60), 2))
    c.paint(rrect(ax0 + 10, ay0 + 10, ax1 - 10, ay1 - 10, 6), (230, 40, 50), ow=2.5, hi=(0, 3, (255, 140, 130)))
    c.text((ax0 + ax1) / 2, (ay0 + ay1) / 2, "APPLAUSE", 34, (255, 250, 220), "Black", stroke=2, sc=(140, 10, 20))
    c.glow((ax0 + ax1) / 2, (ay0 + ay1) / 2, 170, (255, 80, 60), 0.35)

    # --- stage door (exit) with EXIT sign
    d = B["Stage door"]
    dx0, dy0, dx1, dy1 = d
    cas = (70, 66, 80)
    c.paint(rect(dx0 - 12, dy0 - 12, dx1 + 12, dy1 + 2), cas, shade=(-4, 0, dk(cas, 0.7)))
    door = (150, 60, 60)
    c.paint(rect(dx0, dy0, dx1, dy1), ("v", lt(door, 0.1), dk(door, 0.85)), ow=3, shade=(-6, 0, dk(door, 0.75)))
    c.paint(rect(dx0 + 14, dy0 + 128, dx1 - 14, dy0 + 140), (200, 200, 210), ow=2.5, hi=(0, 2, (250, 250, 255)))
    dcx = (dx0 + dx1) / 2
    c.paint(ell(dcx, dy0 + 62, 30, 30), (200, 204, 216), hi=(-2, -2, (250, 250, 255), 2))
    c.paint(ell(dcx, dy0 + 62, 21, 21), ("v", (255, 210, 120), (230, 140, 60)), ow=3,
            pattern=lambda p: p.poly([(dcx - 14, dy0 + 70), (dcx - 4, dy0 + 48), (dcx + 2, dy0 + 48), (dcx - 8, dy0 + 72)],
                                     (255, 240, 200)))
    c.paint(rrect(dx0 + 22, dy0 + 160, dx1 - 22, dy0 + 196, 4), (240, 236, 220), ow=2.5)
    c.text(dcx, dy0 + 172, "STAGE", 11, (150, 40, 40), "Black")
    c.text(dcx, dy0 + 186, "DOOR", 11, (150, 40, 40), "Black")
    c.paint(ell(dx1 - 18, dy0 + 150, 7, 7), (240, 196, 80), ow=2.5, hi=(-2, -2, (255, 245, 190)))
    c.paint(rrect(dx0 + 16, dy0 - 64, dx1 - 16, dy0 - 26, 5), (30, 30, 34), ow=3)
    c.text((dx0 + dx1) / 2, dy0 - 45, "EXIT", 22, (255, 70, 60), "Black")
    c.glow((dx0 + dx1) / 2, dy0 - 45, 70, (255, 60, 50), 0.35)
    c.paint(poly([(dx0 + 10, dy0 - 45), (dx0 + 22, dy0 - 54), (dx0 + 22, dy0 - 36)]), (255, 70, 60), ow=0)

    # --- audience bleachers with the ten women and lots of fans
    au = B["Studio audience"]
    bx0, by0, bx1, by1 = au
    seat = (78, 50, 110)
    c.paint(rect(bx0, by0 + 40, bx1, by1), ("v", dk(seat, 0.6), seat), ow=3)
    rows = [by0 + 120, by0 + 222, by0 + 324]  # base lines of the back, middle and front rows
    rgen = random.Random(11)
    n = 10
    step = (bx1 - bx0 - 40) / n
    xs = [bx0 + 20 + step * (i + 0.5) for i in range(n)]
    # back row: fans, two with signs
    for i, x in enumerate(xs):
        generic_person(c, x + (step / 2 if i % 2 else 0) * 0, rows[0], rgen)
    c.paint(rect(bx0, rows[0] - 6, bx1, rows[0] + 22), ("v", lt(seat, 0.2), seat), hi=(0, 3, lt(seat, 0.4)))

    def sign(cx, cy, w, h, text, col, tcol, ang):
        sub = Canvas(int(w + 40), int(h + 70), ow=3)
        sub.line([(20 + w / 2, 20 + h / 2), (20 + w / 2, 20 + h + 40)], 5, (150, 100, 60))
        sub.paint(wonky(20, 20, 20 + w, 20 + h, 1.5, random.Random(int(w))), col)
        sub.text(20 + w / 2, 20 + h / 2, text, 17, tcol, "Black")
        c.stamp(sub, cx, cy, ang)
    sign(xs[2], rows[0] - 76, 96, 40, "GO DEX!", (255, 240, 120), (220, 30, 90), 6)
    sign(xs[7], rows[0] - 72, 120, 40, "WHO IS DEX?", (255, 255, 255), (60, 60, 140), -5)
    # middle row: Dolly, Mina, Sky, Mimi, Jett among fans
    mid = {1: dolly, 3: mina, 5: sky, 7: mimi, 9: jett}
    for i, x in enumerate(xs):
        if i in mid:
            mid[i](c, x, rows[1])
        else:
            generic_person(c, x, rows[1], rgen)
    c.paint(rect(bx0, rows[1] - 6, bx1, rows[1] + 22), ("v", lt(seat, 0.2), seat), hi=(0, 3, lt(seat, 0.4)))
    # front row: Lacey, Ivy, Tess, Bree, Lou
    front = {0: lacey, 2: ivy, 4: tess, 6: bree, 8: lou}
    for i, x in enumerate(xs):
        if i in front:
            front[i](c, x, rows[2])
        else:
            generic_person(c, x, rows[2], rgen)
    # front rail panel
    rail = (200, 40, 110)
    c.paint(rect(bx0 - 6, rows[2] - 6, bx1 + 6, by1), ("v", rail, dk(rail, 0.7)), hi=(0, 4, lt(rail, 0.3)),
            pattern=lambda p: [p.ell(x, rows[2] + 26, 4, 4, (255, 240, 170)) for x in range(int(bx0 + 20), int(bx1), 40)])
    c.paint(rect(bx0 - 10, rows[2] - 12, bx1 + 10, rows[2] - 2), (240, 196, 80), ow=3, hi=(0, 2, (255, 236, 150)))
    c.text((bx0 + bx1) / 2, rows[2] + 44, "STUDIO AUDIENCE", 16, (255, 236, 200), "Black", stroke=1.5, sc=(90, 10, 50))

    # --- studio camera on a pedestal
    cam = B["Studio camera"]
    cx0, cy0, cx1, cy1 = cam
    ccx = (cx0 + cx1) / 2
    c.shadow(ccx, cy1 - 2, 70, 9, 0.55)
    for k in (-1, 0, 1):  # pedestal legs + casters
        c.paint(cap([(ccx, cy1 - 70), (ccx + k * 56, cy1 - 12)], 8), (70, 70, 84), ow=2.5)
        c.paint(ell(ccx + k * 56, cy1 - 8, 9, 7), (30, 30, 36), ow=2.5)
    c.paint(rrect(ccx - 12, cy0 + 120, ccx + 12, cy1 - 60, 4), ("h", (150, 154, 170), (90, 92, 108)), ow=3)
    c.paint(ell(ccx, cy0 + 120, 30, 9), (90, 92, 108), ow=3)
    body = (60, 62, 76)
    c.paint(wonky(cx0 + 6, cy0 + 30, cx1 - 30, cy0 + 112, 1.5, rng, corner=8), ("v", lt(body, 0.15), dk(body, 0.85)),
            shade=(-5, -5, dk(body, 0.65)), hi=(4, 4, lt(body, 0.3), 2))
    # lens hood pointing right, toward the set
    c.paint(poly([(cx1 - 34, cy0 + 44), (cx1, cy0 + 34), (cx1, cy0 + 108), (cx1 - 34, cy0 + 98)]), (40, 40, 50),
            hi=(0, 3, (90, 90, 110)))
    c.paint(ell(cx1 - 2, cy0 + 71, 6, 34), (110, 140, 220), ow=3, hi=(-2, 0, (200, 220, 255)))
    # viewfinder on the back + handles
    c.paint(rrect(cx0 + 2, cy0 + 2, cx0 + 64, cy0 + 40, 4), (40, 40, 48), hi=(0, 3, (90, 90, 110)))
    c.paint(rect(cx0 + 10, cy0 + 9, cx0 + 56, cy0 + 33), (120, 200, 230), ow=2,
            pattern=lambda p: p.ell(cx0 + 33, cy0 + 21, 6, 5, (255, 120, 180)))
    c.line([(cx0 + 10, cy0 + 100), (cx0 - 6, cy0 + 140)], 6, (40, 40, 48))
    c.paint(rrect(cx0 + 70, cy0 + 50, cx0 + 108, cy0 + 70, 3), (240, 240, 230), ow=2)
    c.text(cx0 + 89, cy0 + 60, "CAM 1", 8.5, (40, 40, 60), "Black")
    c.paint(ell(cx1 - 44, cy0 + 26, 7, 7), (255, 50, 50), ow=2.5)  # tally light
    c.glow(cx1 - 44, cy0 + 26, 34, (255, 60, 60), 0.5)
    # coil of cable at the base
    c.line(bez((ccx + 40, cy1 - 6), (ccx + 120, cy1 + 4), (ccx + 160, cy1 + 10)), 4, (20, 20, 26))

    # --- wardrobe rack
    wr = B["Wardrobe rack"]
    wx0, wy0, wx1, wy1 = wr
    chrome = (200, 204, 216)
    c.shadow((wx0 + wx1) / 2, wy1 - 2, (wx1 - wx0) / 2 + 6, 7, 0.5)
    for lx in (wx0 + 8, wx1 - 8):
        c.paint(cap([(lx, wy0 + 30), (lx, wy1 - 14)], 6), chrome, ow=2.5, hi=(-1, 0, (255, 255, 255)))
        c.paint(ell(lx, wy1 - 8, 8, 6), (40, 40, 48), ow=2.5)
    c.paint(cap([(wx0 + 4, wy0 + 30), (wx1 - 4, wy0 + 30)], 6), chrome, ow=2.5)
    c.paint(cap([(wx0 + 8, wy1 - 30), (wx1 - 8, wy1 - 30)], 5), chrome, ow=2.5)
    clothes = [((255, 200, 60), "sequin"), ((60, 200, 220), "plain"), ((240, 240, 250), "tux"), ((230, 60, 140), "sequin")]
    cw = (wx1 - wx0 - 24) / len(clothes)
    for i, (col, kind) in enumerate(clothes):
        gx = wx0 + 12 + cw * (i + 0.5)
        c.curve((gx - 6, wy0 + 30), (gx, wy0 + 18), (gx + 4, wy0 + 30), 2, (150, 150, 160))
        jacket = poly([(gx - 15, wy0 + 40), (gx - 6, wy0 + 32), (gx + 6, wy0 + 32), (gx + 15, wy0 + 40),
                       (gx + 16, wy0 + 140), (gx - 16, wy0 + 140)], 1)
        pat = None
        if kind == "sequin":
            pat = lambda p, gx=gx, col=col: [paint.sparkle(p, gx - 12 + (k * 7) % 26, wy0 + 44 + (k * 13) % 92, 2.2,
                                                            lt(col, 0.6)) for k in range(14)]
        elif kind == "tux":
            pat = lambda p, gx=gx: (p.poly([(gx - 5, wy0 + 34), (gx + 5, wy0 + 34), (gx, wy0 + 60)], (30, 30, 36)),
                                    p.ell(gx, wy0 + 40, 4, 2, (30, 30, 36)),
                                    [p.ell(gx, wy0 + 70 + k * 14, 1.6, 1.6, (30, 30, 36)) for k in range(4)])
        c.paint(jacket, col, ow=2.5, shade=(3, 0, dk(col, 0.72)), pattern=pat)
    # feather boa draped over the bar
    for k in range(12):
        t = k / 11
        bx = wx0 + 10 + (wx1 - wx0 - 20) * t
        by = wy0 + 30 + math.sin(t * math.pi) * 34
        c.paint(ell(bx, by, 9, 7, k * 30), (255, 120, 200), ow=2, hi=(-1, -1, (255, 200, 230)))
    # box of mic packs on the bottom shelf
    c.paint(wonky(wx0 + 18, wy1 - 70, wx1 - 18, wy1 - 32, 1.5, rng), (200, 150, 90), shade=(-3, -3, (160, 110, 70)))
    c.text((wx0 + wx1) / 2, wy1 - 52, "MIC PACKS", 9.5, (60, 30, 20), "Black")
    for k in range(3):
        c.paint(rrect(wx0 + 30 + k * 22, wy1 - 82, wx0 + 46 + k * 22, wy1 - 66, 2), (40, 40, 48), ow=2)
        c.line([(wx0 + 34 + k * 22, wy1 - 82), (wx0 + 34 + k * 22, wy1 - 92)], 1.6)

    # --- light beams from the truss onto the set and the audience
    for sx, tx, tw in ((1260, 1350, 110), (1560, 1500, 140), (1840, 1640, 110)):
        c.paint(poly([(sx - 14, 140), (sx + 14, 140), (tx + tw, 800), (tx - tw, 800)]), (255, 248, 210), ow=0,
                opacity=0.08)
    for sx, tx in ((330, 420), (700, 640)):
        c.paint(poly([(sx - 14, 140), (sx + 14, 140), (tx + 120, 700), (tx - 120, 700)]), (200, 220, 255), ow=0,
                opacity=0.06)

    lights = [(1560, 260, 700, 0.55, (255, 120, 200)), (1350, 600, 420, 0.4, (255, 230, 180)),
              (500, 560, 520, 0.35, (255, 210, 170)), (940, 260, 260, 0.3, (255, 120, 110)),
              (100, 500, 260, 0.2, (255, 120, 100)), (1640, 760, 400, 0.3, (255, 220, 160))]
    light_pass(c, 0.8, lights, vign=0.38, front=0.12)
    c.glow(1560, 250, 240, (255, 90, 180), 0.22)
    for sx, d in spots:
        c.glow(sx, 136, 40, (255, 250, 220), 0.55)
    c.save("bg_tv_studio.png")


# =========================================================================== Chet Studwell (rival)
def paint_chet_studwell():
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (240, 182, 130), (204, 136, 96)
    hair, hair_sh, hair_hi = (255, 214, 90), (220, 160, 50), (255, 246, 190)
    jk, jk_sh, jk_hi = (250, 246, 236), (206, 200, 210), (255, 255, 255)
    polo, polo_sh = (255, 130, 120), (220, 84, 90)
    pants, pants_sh = (240, 236, 226), (196, 190, 196)
    loafer, loafer_sh = (150, 80, 40), (100, 50, 30)
    grape, grape_sh = (130, 60, 190), (90, 30, 140)

    # far arm: thumbs-up to the camera, raised behind his head side
    c.paint(cap([(74, 100), (92, 112), (98, 88)], 9), jk, shade=(3, 2, jk_sh))
    # finger guns, aimed at the room
    c.paint(ell(99, 86, 7.5, 7) + cap([(95, 82), (84, 80)], 4.6) + cap([(101, 81), (101, 72)], 4.4), skin,
            shade=(2, 2, skin_sh))
    c.line([(96, 89), (102, 89)], 1.2, skin_sh)
    c.paint(cap([(72, 100), (90, 112)], 16), jk, shade=(3, 2, jk_sh))
    # legs, wide confident stance
    c.paint(cap([(64, 150), (70, 196), (72, 236)], 16), pants, shade=(3, 0, pants_sh))
    c.paint(cap([(46, 150), (38, 196), (32, 238)], 17), pants, shade=(3, 0, pants_sh))
    c.line([(52, 154), (40, 230)], 1.2, pants_sh)
    # loafers pointing left, with gold buckles
    for xh, xt, yt, yb in ((86, 54, 238, 252), (48, 12, 241, 256)):
        foot = shoe_shape(xh, xt, yt, yb)
        c.paint(foot, loafer, shade=(3, -2, loafer_sh), hi=(-2, 2, lt(loafer, 0.35), 1.5))
        c.paint(rect(xt + 12 * (1 if xt < xh else -1) - 4, yt + 1, xt + 12 * (1 if xt < xh else -1) + 4, yt + 5),
                (250, 210, 80), ow=1.4)
    # white jacket + popped salmon collar
    torso = poly([(30, 94), (52, 88), (76, 92), (82, 106), (78, 132), (82, 158), (56, 162), (28, 158), (32, 130),
                  (26, 106)], 2)
    c.paint(torso, jk, shade=(5, 2, jk_sh), hi=(-3, 3, jk_hi, 2))
    c.paint(poly([(44, 92), (62, 92), (60, 140), (48, 140)], 1), polo, ow=2.2, shade=(2, 0, polo_sh))
    # gold chain
    c.curve((46, 98), (54, 112), (62, 98), 1.8, (250, 210, 80))
    # lapels
    c.paint(poly([(40, 92), (48, 94), (54, 140), (44, 124), (36, 104)], 1), jk_sh, ow=2.2)
    c.paint(poly([(66, 92), (60, 94), (56, 140), (66, 122), (72, 104)], 1), jk_sh, ow=2.2)
    c.paint(ell(55, 146, 2.4, 2.4), (250, 210, 80), ow=1.4)
    # popped collar points
    c.paint(poly([(42, 92), (40, 76), (52, 86)], 1), polo, ow=2.2, shade=(1, 0, polo_sh))
    c.paint(poly([(64, 92), (68, 76), (56, 86)], 1), polo, ow=2.2, shade=(1, 0, polo_sh))
    # earpiece wire from ear down into the collar
    c.curve((76, 70), (84, 84), (66, 92), 1.4, (240, 220, 200))
    # near arm holding a giant grape soda in front of him
    c.paint(cap([(32, 100), (24, 124), (26, 138)], 9), jk, shade=(3, 2, jk_sh))
    c.paint(cap([(32, 98), (25, 120)], 16), jk, shade=(3, 2, jk_sh))
    cup = poly([(6, 116), (32, 116), (29, 154), (9, 154)], 1)
    c.paint(cup, grape, shade=(3, 0, grape_sh), hi=(-2, 0, (190, 130, 240), 1.5),
            pattern=lambda p: (p.rect(4, 128, 34, 137, (255, 255, 255)), p.ell(19, 132.5, 5, 3, grape)))
    c.paint(ell(19, 116, 13.5, 3.8), (250, 250, 250), ow=2.2)
    c.line([(21, 116), (27, 96), (33, 94)], 3.2, OUT)
    c.line([(21, 116), (27, 96), (33, 94)], 1.6, (255, 230, 80))
    c.paint(ell(29, 140, 7, 7.5) + cap([(24, 136), (20, 136)], 4) + cap([(25, 143), (20, 143)], 4), skin,
            shade=(2, 2, skin_sh))
    c.paint(poly([(12, 154), (15, 161), (12, 165), (9, 161)], 1), grape, ow=1.6)  # drip

    # neck
    c.paint(cap([(56, 76), (56, 92)], 11), skin, shade=(3, 0, skin_sh))
    # ---- head: 3/4 facing left, huge square jaw
    head = ell(56, 50, 23, 25) + poly([(32, 52), (32, 74), (42, 86), (66, 86), (78, 70), (78, 50)], 1) + \
        ell(32, 58, 5.5, 5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, lt(skin, 0.3), 2.5))
    c.line([(45, 83), (45, 86)], 1.4, skin_sh)  # chin cleft
    c.paint(ell(78, 58, 5.5, 8), skin, shade=(2, 2, skin_sh))  # ear
    c.paint(ell(78, 66, 3, 3), (240, 220, 200), ow=1.6)  # earpiece bud
    c.curve((32, 61), (29, 62), (29, 59), 1.4)  # nostril
    # smug half-lidded eyes, one brow cocked
    eye(c, 50, 50, 7.5, 8.5, 46.5, 51.5, 2.3, lid=0.42, lid_tilt=-0.6, skin=skin, iris=(60, 140, 220))
    eye(c, 36, 50, 5.2, 7.6, 33.5, 51.5, 2.0, lid=0.42, lid_tilt=0.6, skin=skin, iris=(60, 140, 220))
    c.line([(42, 36), (50, 32), (60, 35)], 2.6, hair_sh)
    c.line([(30, 41), (37, 39.5)], 2.4, hair_sh)
    # enormous perfect grin
    grin = poly([(34, 66), (46, 68), (60, 65), (66, 62), (62, 73), (48, 78), (37, 74)], 1)
    c.paint(grin, (255, 255, 255), ow=2.2)
    c.line([(36, 70), (48, 72.5), (63, 67)], 1.0, (180, 180, 200))
    for tx in (42, 48, 54, 60):
        c.line([(tx, 67.5), (tx, 75)], 0.8, (190, 190, 210))
    c.paint(poly([(30, 60), (31.5, 64.5), (36, 66), (31.5, 67.5), (30, 72), (28.5, 67.5), (24, 66), (28.5, 64.5)]),
            (255, 255, 240), ow=1.4)
    # tall blond pompadour swooping forward
    pomp = [(32, 44), (28, 30), (34, 14), (50, 4), (72, 2), (88, 10), (92, 26), (86, 44), (80, 58), (76, 46),
            (70, 34), (58, 32), (46, 34), (38, 42)]
    c.paint(poly(pomp, 2, True), hair, shade=(3, 3, hair_sh), hi=(-3, 3, hair_hi, 2))
    c.curve((40, 18), (58, 6), (82, 12), 1.6, hair_sh)
    c.curve((44, 26), (62, 14), (84, 22), 1.4, hair_sh)
    c.curve((36, 32), (40, 20), (54, 12), 2.2, hair_hi)
    c.fit(margin=3)
    c.save("hs_chet_studwell.png")


# =========================================================================== inventory icons
def paint_icon_lapel_mic():
    def draw(c):
        c.curve((86, 60), (110, 90), (96, 110), 3, (30, 30, 36))
        body = rrect(22, 40, 82, 116, 8)
        c.paint(body, (50, 50, 60), shade=(5, 5, (30, 30, 40)), hi=(-4, -4, (110, 110, 130), 3))
        c.paint(cap([(30, 40), (26, 10)], 5), (40, 40, 48))
        c.paint(ell(26, 10, 5, 5), (40, 40, 48))
        c.paint(rrect(32, 54, 72, 78, 3), (30, 30, 36), ow=2.5)
        c.text(52, 66, "EMPTY", 8, (255, 90, 80))
        c.paint(ell(70, 100, 5, 5), (90, 20, 20), ow=2.5)  # dead light
        c.paint(rrect(86, 48, 110, 62, 4), (40, 40, 48), hi=(0, 2, (120, 120, 140)))  # clip mic
        c.paint(ell(112, 55, 7, 7), (60, 60, 70), ow=3,
                pattern=lambda p: [p.line([(106, 50 + k * 3), (118, 50 + k * 3)], 1, (120, 120, 130)) for k in range(4)])
    icon("icon_lapel_mic.png", -8, draw)


def paint_icon_nine_volt():
    def draw(c):
        b = rrect(30, 34, 98, 118, 6)
        c.paint(b, (250, 150, 40), shade=(5, 0, (210, 100, 30)), hi=(-4, 0, (255, 210, 130), 3),
                pattern=lambda p: p.rect(30, 34, 98, 66, (40, 40, 48)))
        c.text(64, 92, "9V", 26, (40, 30, 30))
        c.paint(rect(30, 64, 98, 68), (240, 200, 80), ow=0)
        c.paint(rrect(40, 20, 58, 36, 3), (200, 204, 216), hi=(0, 2, (255, 255, 255)))
        c.paint(ell(80, 28, 10, 9), (200, 204, 216), hi=(0, 2, (255, 255, 255)),
                pattern=lambda p: [p.poly(rot_pts([(80, 22), (85, 28), (80, 34), (75, 28)], k * 45, 80, 28),
                                          (150, 154, 170)) for k in range(2)])
        c.paint(poly([(22, 14), (30, 4), (26, 16), (34, 16), (20, 30), (24, 18), (16, 18)]), (255, 236, 80), ow=3)
    icon("icon_nine_volt.png", 10, draw)


def paint_icon_soda_water():
    def draw(c):
        bottle = poly([(44, 120), (84, 120), (86, 60), (74, 40), (73, 18), (55, 18), (54, 40), (42, 60)], 2)
        c.paint(bottle, (170, 220, 236), shade=(5, 0, (120, 180, 210)), hi=(-4, 0, (230, 250, 255), 3))
        for bx, by, r in ((56, 100, 3), (70, 88, 2.4), (62, 74, 2.6), (74, 108, 2.2), (58, 62, 2)):
            c.paint(ell(bx, by, r, r), (240, 252, 255), ow=1.4)
        c.paint(rect(42, 76, 86, 100), (40, 120, 200), ow=3, clip=bottle)
        c.text(64, 83, "CLUB", 9.5, (255, 255, 255))
        c.text(64, 94, "SODA", 9.5, (255, 255, 255))
        c.paint(rrect(52, 8, 76, 20, 3), (60, 160, 90), ow=3.5, hi=(0, 2, (140, 220, 160)))
    icon("icon_soda_water.png", 10, draw)


def paint_icon_cocktail_napkin():
    def draw(c):
        c.paint(poly([(20, 44), (96, 30), (110, 96), (34, 112)], 1), (238, 238, 232), shade=(4, 4, (200, 200, 210)))
        c.paint(poly([(14, 36), (90, 24), (104, 88), (28, 102)], 1), (255, 255, 252), hi=(-3, -3, (255, 255, 255), 2),
                pattern=lambda p: [p.line([(20 + k * 3, 42 + k * 15), (94 + k * 3, 30 + k * 15)], 3, (90, 160, 220))
                                   for k in (0, 4)])
        c.text(59, 64, "BREE'S", 13, (230, 70, 80), "Italic", angle=8)
        c.text(60, 80, "DINER", 11, (90, 160, 220), "Black", angle=8)
    icon("icon_cocktail_napkin.png", -6, draw)


def paint_icon_studio_walkie():
    def draw(c):
        c.paint(cap([(42, 40), (40, 6)], 9), (40, 40, 48), hi=(-2, 0, (110, 110, 130)))
        body = rrect(30, 34, 96, 122, 10)
        c.paint(body, (50, 52, 62), shade=(5, 5, (30, 30, 40)), hi=(-4, -4, (110, 110, 130), 3))
        c.paint(rrect(40, 46, 86, 70, 4), (120, 200, 140), ow=3,
                pattern=lambda p: p.rect(44, 56, 70, 60, (60, 120, 80)))
        for k in range(4):
            c.line([(42, 80 + k * 8), (84, 80 + k * 8)], 3, (30, 30, 36))
        c.paint(ell(78, 30, 6, 6), (230, 60, 60), ow=2.5)
        c.text(64, 110, "CHET", 17, (255, 140, 220), "Italic", stroke=1.5, sc=(120, 20, 90))
        for k in range(5):
            star(c, 34 + k * 15, 94 + (k % 2) * 24, 4, (255, 240, 120))
    icon("icon_studio_walkie.png", -10, draw)


def paint_icon_sign_out_sheet():
    def draw(c):
        c.paint(wonky(18, 16, 110, 124, 1.5, random.Random(4), corner=6), (186, 130, 72), shade=(-4, -4),
                hi=(3, 3, (220, 170, 110), 2))

        def rows(p):
            for k in range(8):
                y = 46 + k * 9
                p.line([(30, y), (98, y)], 1.4, (150, 170, 210))
            p.line([(56, 38), (56, 114)], 1.4, (150, 170, 210))
            p.line([(30, 64), (54, 62)], 2.2, (40, 60, 160))
            p.line([(60, 64), (92, 62)], 2.2, (200, 40, 120))
        c.paint(rect(26, 32, 102, 118), (250, 250, 244), ow=2.5, pattern=rows)
        c.text(64, 40, "EQUIPMENT", 8, (60, 40, 120))
        c.paint(ell(78, 63, 20, 8), (0, 0, 0, 0), ow=2.5, oc=(230, 40, 60))  # circled entry
        c.paint(rrect(46, 8, 82, 30, 4), (170, 176, 186), hi=(0, 3, (230, 236, 240)))
    icon("icon_sign_out_sheet.png", 6, draw)


def cassette(c, shell, label, text1, text2, tcol, glitter=False):
    c.paint(rrect(8, 26, 120, 102, 8), shell, shade=(5, 5, dk(shell, 0.7)), hi=(-4, -4, lt(shell, 0.3), 3))
    c.paint(rrect(18, 34, 110, 78, 4), label, ow=3)
    if glitter:
        r2 = random.Random(7)
        for _ in range(14):
            c.paint(ell(r2.choice([r2.uniform(22, 32), r2.uniform(96, 106)]), r2.uniform(38, 74), 1.6, 1.6),
                    (255, 255, 255), ow=0)
    c.text(64, 46, text1, 12, tcol, "Black")
    c.text(64, 60, text2, 8.5, tcol, "Black")
    c.paint(rrect(38, 64, 90, 78, 6), (40, 36, 44), ow=2.5)
    for wx in (50, 78):
        c.paint(ell(wx, 71, 5.5, 5.5), (250, 250, 250), ow=2,
                pattern=lambda p, wx=wx: [p.line([(wx, 71), (wx + 5 * math.cos(math.radians(a)),
                                                             71 + 5 * math.sin(math.radians(a)))], 1.2, OUT)
                                          for a in (0, 120, 240)])
    c.paint(poly([(30, 102), (36, 88), (92, 88), (98, 102)]), dk(shell, 0.85), ow=3)
    for hx in (44, 84):
        c.paint(ell(hx, 96, 3, 3), (30, 30, 36), ow=0)


def paint_icon_chet_mixtape():
    def draw(c):
        cassette(c, (60, 60, 70), (250, 210, 70), "CHET'S", "PUMP-UP JAMS 9", (120, 40, 20))
        star(c, 108, 30, 13, (255, 236, 90), ow=3)
    icon("icon_chet_mixtape.png", -8, draw)


def paint_icon_floor_fillers_tape():
    def draw(c):
        cassette(c, (60, 220, 230), (255, 120, 210), "DOLLY'S", "FLOOR-FILLERS", (60, 20, 90), glitter=True)
        c.paint(poly([(98, 6), (112, 2), (116, 16), (104, 22)], 1), (120, 255, 120), ow=2.5)  # glow-stick nub
    icon("icon_floor_fillers_tape.png", 8, draw)


ASSETS = {"bg_tv_studio": paint_tv_studio, "hs_chet_studwell": paint_chet_studwell,
          "icon_lapel_mic": paint_icon_lapel_mic, "icon_nine_volt": paint_icon_nine_volt,
          "icon_soda_water": paint_icon_soda_water, "icon_cocktail_napkin": paint_icon_cocktail_napkin,
          "icon_studio_walkie": paint_icon_studio_walkie, "icon_sign_out_sheet": paint_icon_sign_out_sheet,
          "icon_chet_mixtape": paint_icon_chet_mixtape, "icon_floor_fillers_tape": paint_icon_floor_fillers_tape}


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
