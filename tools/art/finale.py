#!/usr/bin/env python3
"""
Big Night Out -- Finale art (the Speed Daters Live TV studio).

Original art, drawn procedurally with the helpers in paint.py (same style: bold dark outlines,
warm saturated cel shading, big-headed characters). Props are painted exactly inside the hotspot
boxes read from Assets/_Project/World/finale.json, so the art and the click areas line up.

Usage:  python3 tools/art/finale.py            # paint everything
        python3 tools/art/finale.py chet icon  # only assets whose name contains these words
Output: Assets/_Project/Art/Painted/bg_tv_studio.png, bg_tv_green_room.png, bg_tv_control_booth.png,
        hs_chet_studwell.png, hs_gloria_puff.png, hs_norma_fade.png, hs_reserved_sign.png,
        hs_playback_deck.png, hs_empty_deck.png, icon_<item>.png
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, W_BG, H_BG, WALL_Y, Canvas, mix, dk, lt, rot_pts, bez, poly, ell, rect, rrect,  # noqa: E402
                   wonky, cap, eye, shoe_shape, light_pass, sparkle, icon, poster, door, checker_floor)

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "finale.json")


def boxes(room_id="tv_studio"):
    """Hotspot name -> (x0, y0, x1, y1) in background pixels, from the room JSON."""
    room = [r for r in json.load(open(WORLD))["rooms"] if r["id"] == room_id][0]
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


def wardrobe_rack(c, wr, rng):
    """Chrome clothes rack with jackets, a feather boa and the MIC PACKS box, inside box wr."""
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
    c.paint(rrect(750, 236, 890, 290, 8), (60, 20, 26), shade=(-3, -3), hi=(3, 3, (120, 50, 60), 2))
    c.paint(rrect(760, 244, 880, 282, 5), (240, 40, 50), ow=2.5, hi=(0, 3, (255, 140, 130)))
    c.text(820, 263, "ON AIR", 22, (255, 250, 230), "Black", stroke=1.5, sc=(140, 10, 20))
    c.line([(820, 236), (820, 96)], 2.5, (40, 40, 50))

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

    # --- green room door (under the booth window) and the control booth window
    green_room_door(c, B["Green room door"])
    booth_window(c, B["Control booth window"])

    # --- light beams from the truss onto the set and the audience
    for sx, tx, tw in ((1260, 1350, 110), (1560, 1500, 140), (1840, 1640, 110)):
        c.paint(poly([(sx - 14, 140), (sx + 14, 140), (tx + tw, 800), (tx - tw, 800)]), (255, 248, 210), ow=0,
                opacity=0.08)
    for sx, tx in ((330, 420), (700, 640)):
        c.paint(poly([(sx - 14, 140), (sx + 14, 140), (tx + 120, 700), (tx - 120, 700)]), (200, 220, 255), ow=0,
                opacity=0.06)

    lights = [(1560, 260, 700, 0.55, (255, 120, 200)), (1350, 600, 420, 0.4, (255, 230, 180)),
              (500, 560, 520, 0.35, (255, 210, 170)), (820, 260, 260, 0.3, (255, 120, 110)),
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


# =========================================================================== studio additions
def green_room_door(c, box):
    """Plain backstage door with a paper star that says GREEN ROOM (it is not green)."""
    x0, y0, x1, y1 = box
    x0, x1 = x0 + 6, x1 - 6
    y0 += 18
    cas = (70, 66, 80)
    c.paint(rect(x0 - 12, y0 - 12, x1 + 12, y1 + 2), cas, shade=(-4, 0, dk(cas, 0.7)))
    dcol = (96, 120, 150)
    c.paint(rect(x0, y0, x1, y1), ("v", lt(dcol, 0.12), dk(dcol, 0.85)), ow=3, shade=(-6, 0, dk(dcol, 0.75)))
    for (py0, py1) in ((y0 + 22, y0 + 104), (y0 + 128, y1 - 20)):
        c.paint(rrect(x0 + 16, py0, x1 - 16, py1, 4), dcol, ow=2.5, shade=(0, -4, dk(dcol, 0.78)),
                hi=(0, 3, lt(dcol, 0.3)))
    cx = (x0 + x1) / 2
    star(c, cx, y0 + 62, 34, (255, 226, 80), ow=3)
    c.paint(rrect(x0 + 14, y0 + 112, x1 - 14, y0 + 144, 4), (240, 236, 220), ow=2.5)
    c.text(cx, y0 + 128, "GREEN ROOM", 10, (150, 40, 60), "Black")
    for tx, ty in ((cx - 26, y0 + 30), (cx + 26, y0 + 30)):
        c.paint(rect(tx - 8, ty - 5, tx + 8, ty + 5), (240, 232, 200), ow=0, opacity=0.85)
    kx, ky = x1 - 16, y0 + (y1 - y0) * 0.55
    c.paint(ell(kx, ky, 8, 8), (240, 196, 80), ow=3, hi=(-2, -2, (255, 245, 190)), shade=(3, 3))
    c.paint(rrect(x0 + 18, y1 - 60, x1 - 18, y1 - 44, 3), (200, 200, 210), ow=2)  # kick plate
    c.line([(x0 - 12, y1 + 2), (x1 + 12, y1 + 2)], 3)


def booth_window(c, box):
    """Dark control-booth window high on the studio wall, a director silhouette inside."""
    x0, y0, x1, y1 = box
    fr = (60, 60, 72)
    c.paint(rrect(x0, y0, x1, y1, 6), fr, shade=(-4, -4, dk(fr, 0.7)), hi=(3, 3, (110, 110, 130), 2))

    def inside(p):
        p.rect(x0, y0, x1, y1, (24, 30, 52))
        for k in range(3):  # little monitors glowing inside
            p.rect(x0 + 18 + k * 34, y0 + 30, x0 + 44 + k * 34, y0 + 50, (90, 160, 210))
        p.ell(x0 + 70, y1 - 46, 18, 20, (12, 14, 26))  # director's head
        p.rect(x0 + 40, y1 - 30, x0 + 100, y1, (12, 14, 26))
        p.line([(x0 + 52, y1 - 60), (x0 + 70, y1 - 72), (x0 + 88, y1 - 60)], 4, (12, 14, 26))  # headset band
        p.line([(x0 + 52, y1 - 50), (x0 + 60, y1 - 38)], 3, (12, 14, 26))
        p.poly([(x0 + 10, y0 + 10), (x0 + 40, y0 + 10), (x0 + 10, y0 + 60)], (120, 140, 190))
    c.paint(rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10), (24, 30, 52), ow=3, pattern=inside)
    c.paint(rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10), (255, 255, 255), ow=0, opacity=0.06)
    c.paint(rrect(x0 + 20, y1 - 4, x1 - 20, y1 + 18, 3), (30, 30, 34), ow=2.5)
    c.text((x0 + x1) / 2, y1 + 7, "CONTROL", 9, (255, 220, 120), "Black")


# =========================================================================== green room background
def bulb_mirror(c, x0, y0, x1, y1):
    c.paint(rrect(x0, y0, x1, y1, 10), (236, 220, 196), shade=(-4, -4, (190, 170, 150)), hi=(3, 3, (255, 246, 230), 2))

    def glass(p):
        p.rect(x0 + 22, y0 + 22, x1 - 22, y1 - 22, (150, 186, 200))
        p.poly([(x0 + 40, y0 + 22), (x0 + 90, y0 + 22), (x0 + 22, y0 + 110), (x0 + 22, y0 + 60)], (200, 226, 236))
        p.poly([(x0 + 110, y0 + 22), (x0 + 128, y0 + 22), (x0 + 22, y0 + 160), (x0 + 22, y0 + 136)], (190, 220, 230))
    c.paint(rect(x0 + 22, y0 + 22, x1 - 22, y1 - 22), (150, 186, 200), ow=3, pattern=glass)
    n = 6
    for k in range(n):
        for (bx, by) in ((x0 + 11, y0 + 18 + k * (y1 - y0 - 36) / (n - 1)), (x1 - 11, y0 + 18 + k * (y1 - y0 - 36) / (n - 1))):
            c.paint(ell(bx, by, 8, 8), (255, 246, 200), ow=2.2)
            c.glow(bx, by, 26, (255, 230, 160), 0.45)
    for k in range(1, n - 1):
        bx = x0 + 11 + k * (x1 - x0 - 22) / (n - 1)
        c.paint(ell(bx, y0 + 11, 8, 8), (255, 246, 200), ow=2.2)
        c.glow(bx, y0 + 11, 26, (255, 230, 160), 0.45)


def makeup_station(c, box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    # mirror on the wall
    bulb_mirror(c, x0 + 18, y0 + 4, x1 - 18, y0 + 186)
    # counter with makeup
    top = y0 + 196
    c.paint(rect(x0 - 4, top, x1 + 4, top + 16), (230, 140, 160), ow=3, hi=(0, 3, (255, 200, 210)))
    c.paint(rect(x0 + 6, top + 16, x1 - 6, top + 110), ("v", (196, 110, 130), (150, 80, 100)), ow=3,
            pattern=lambda p: [p.line([(x0 + 6, top + 50 + k * 30), (x1 - 6, top + 50 + k * 30)], 2.4, (110, 50, 70))
                               for k in range(2)])
    for k, col in enumerate(((240, 60, 90), (250, 200, 160), (130, 80, 160), (60, 160, 200), (250, 120, 160))):
        bx = x0 + 22 + k * 30
        c.paint(rrect(bx, top - 22 - (k % 2) * 8, bx + 12, top, 2), col, ow=2)
    c.paint(cap([(x1 - 40, top - 2), (x1 - 34, top - 40)], 6), (250, 230, 200), ow=2)  # brush cup
    c.paint(rrect(x1 - 52, top - 22, x1 - 22, top, 3), (120, 200, 210), ow=2.2)
    for k in range(4):
        c.line([(x1 - 46 + k * 7, top - 22), (x1 - 50 + k * 9, top - 46)], 2.2, (150, 100, 70))
        c.paint(ell(x1 - 50 + k * 9, top - 48, 3, 4), (240, 200, 210), ow=1.4)
    # big makeup chair in front
    seat = (190, 40, 70)
    c.shadow(cx, y1 - 4, 82, 9, 0.55)
    c.paint(rrect(cx - 10, y1 - 70, cx + 10, y1 - 22, 3), (200, 204, 216), ow=2.5, hi=(-2, 0, (255, 255, 255)))
    c.paint(ell(cx, y1 - 14, 56, 12), (150, 154, 170), ow=3, hi=(0, -2, (220, 224, 236)))
    c.paint(rrect(cx - 64, y1 - 210, cx + 64, y1 - 104, 22), ("v", lt(seat, 0.15), dk(seat, 0.8)),
            shade=(-5, -4, dk(seat, 0.65)), hi=(4, 4, lt(seat, 0.35), 2),
            pattern=lambda p: [p.line([(cx - 60 + k * 30, y1 - 206), (cx - 60 + k * 30, y1 - 108)], 2, dk(seat, 0.7))
                               for k in range(1, 4)])
    c.paint(rrect(cx - 30, y1 - 236, cx + 30, y1 - 204, 12), seat, shade=(-3, -3, dk(seat, 0.7)))  # headrest
    c.paint(rrect(cx - 84, y1 - 112, cx + 84, y1 - 70, 16), ("v", lt(seat, 0.1), dk(seat, 0.8)),
            shade=(0, -4, dk(seat, 0.65)), hi=(0, 3, lt(seat, 0.35)))
    for sx in (-1, 1):
        c.paint(rrect(cx + sx * 84 - 14, y1 - 150, cx + sx * 84 + 14, y1 - 96, 7), (220, 224, 236), ow=2.5,
                hi=(-1, -1, (255, 255, 255)))
    c.line([(cx + 20, y1 - 60), (cx + 46, y1 - 40)], 4, (200, 204, 216))  # foot pump
    c.paint(rrect(cx + 40, y1 - 46, cx + 66, y1 - 34, 3), (120, 124, 136), ow=2)


def craft_table(c, box, rng):
    x0, y0, x1, y1 = box
    cloth = (250, 244, 232)
    top = y0 + 78
    c.shadow((x0 + x1) / 2, y1 - 2, (x1 - x0) / 2 + 4, 9, 0.5)
    for lx in (x0 + 26, x1 - 26):
        c.paint(rect(lx - 6, top + 40, lx + 6, y1 - 2), (120, 90, 70), ow=2.5)
    c.paint(poly([(x0, top), (x1, top), (x1 + 6, top + 74), (x0 - 6, top + 74)]), cloth,
            shade=(0, -5, (214, 206, 196)),
            pattern=lambda p: [p.rect(x0 - 6, top + 6 + k * 20, x1 + 6, top + 14 + k * 20, (240, 120, 130))
                               for k in range(4)])
    c.paint(cap([(x0 - 6, top + 74), (x1 + 6, top + 74)], 6), cloth, ow=2.5)
    # bowl of cheese puffs
    bx = x0 + 56
    for k in range(16):
        c.paint(ell(bx + rng.uniform(-30, 30), top - 14 - rng.uniform(0, 14), 7, 4.5, rng.uniform(0, 180)),
                (255, 150, 40), ow=1.6, hi=(-1, -1, (255, 210, 120)))
    c.paint(poly([(bx - 40, top - 16), (bx + 40, top - 16), (bx + 28, top + 2), (bx - 28, top + 2)]), (90, 160, 210),
            hi=(0, 2, (170, 210, 240)))
    c.text(bx, top - 7, "PUFFS", 8, (255, 255, 255), "Black")
    # cup of bendy straws
    sx = x0 + 136
    for k, col in enumerate(((255, 110, 170), (90, 200, 230), (255, 220, 80), (120, 220, 120), (255, 110, 170))):
        tx = sx - 10 + k * 5
        c.line([(tx, top - 28), (tx + (k - 2) * 3, top - 58), (tx + (k - 2) * 7, top - 64)], 3.2, OUT)
        c.line([(tx, top - 28), (tx + (k - 2) * 3, top - 58), (tx + (k - 2) * 7, top - 64)], 1.8, col)
    c.paint(poly([(sx - 16, top - 34), (sx + 16, top - 34), (sx + 12, top), (sx - 12, top)]), (250, 250, 250),
            hi=(-2, 0, (255, 255, 255)), pattern=lambda p: p.rect(sx - 16, top - 22, sx + 16, top - 16, (240, 100, 140)))
    # plate with the licked eclair + sticky note
    ex = x1 - 58
    c.paint(ell(ex, top - 4, 40, 9), (250, 250, 252), ow=2.5)
    c.paint(cap([(ex - 24, top - 12), (ex + 20, top - 14)], 14), (230, 180, 110), ow=2.5)
    c.paint(cap([(ex - 22, top - 17), (ex + 8, top - 19)], 7), (110, 60, 40), ow=0)
    c.paint(ell(ex + 20, top - 14, 8, 8), (250, 250, 252), ow=0)  # the bite
    c.paint(rect(ex - 6, top - 64, ex + 34, top - 30), (255, 240, 110), ow=2,
            pattern=lambda p: [p.line([(ex - 1, top - 54 + k * 8), (ex + 28, top - 54 + k * 8)], 1.2, (200, 60, 60))
                               for k in range(3)])
    c.text(ex + 14, top - 56, "CHET'S", 6.5, (200, 40, 40), "Black")
    c.line([(ex + 14, top - 30), (ex + 10, top - 16)], 1.4, (120, 120, 120))


def booth_stairs_door(c, box):
    x0, y0, x1, y1 = box
    dx0, dx1 = x0 + 50, x1 - 14
    dy0 = y0 + 26
    cas = (60, 62, 70)
    c.paint(rect(dx0 - 12, dy0 - 12, dx1 + 12, y1 + 2), cas, shade=(-4, 0, dk(cas, 0.7)))
    steel = (120, 126, 140)
    c.paint(rect(dx0, dy0, dx1, y1), ("v", lt(steel, 0.1), dk(steel, 0.8)), ow=3, shade=(-6, 0, dk(steel, 0.7)))

    def stairs(p):
        p.rect(dx0 + 30, dy0 + 40, dx1 - 30, dy0 + 150, (40, 44, 60))
        for k in range(6):
            yy = dy0 + 140 - k * 18
            xx = dx0 + 34 + k * 14
            p.rect(xx, yy, dx1 - 30, yy + 10, (90, 96, 120))
        p.line([(dx0 + 34, dy0 + 120), (dx1 - 34, dy0 + 50)], 3, (200, 200, 210))
    c.paint(rect(dx0 + 30, dy0 + 40, dx1 - 30, dy0 + 150), (40, 44, 60), ow=3, pattern=stairs)
    c.paint(rect(dx0 + 30, dy0 + 40, dx1 - 30, dy0 + 150), (255, 255, 255), ow=0, opacity=0.07)
    c.paint(rrect(dx0 + 18, dy0 + 166, dx1 - 18, dy0 + 214, 4), (250, 210, 60), ow=2.5,
            pattern=lambda p: [p.poly([(dx0 + 18 + k * 22, dy0 + 214), (dx0 + 30 + k * 22, dy0 + 214),
                                       (dx0 + 42 + k * 22, dy0 + 166), (dx0 + 30 + k * 22, dy0 + 166)], (40, 40, 40))
                               for k in range(0, 7, 2)])
    c.paint(rrect(dx0 + 26, dy0 + 172, dx1 - 26, dy0 + 208, 3), (255, 255, 255), ow=2)
    c.text((dx0 + dx1) / 2, dy0 + 183, "CREW ONLY", 11, (200, 30, 40), "Black")
    c.text((dx0 + dx1) / 2, dy0 + 198, "CONTROL BOOTH", 8, (40, 40, 60), "Black")
    c.paint(cap([(dx1 - 22, dy0 + 240), (dx1 - 22, dy0 + 270)], 8), (220, 224, 236), ow=2.5)  # push bar handle
    c.line([(dx0 - 12, y1 + 2), (dx1 + 12, y1 + 2)], 3)
    # intercom on the wall left of the door
    ix0, iy0 = x0 + 4, dy0 + 120
    c.paint(rrect(ix0, iy0, ix0 + 34, iy0 + 70, 5), (200, 204, 216), shade=(-2, -2, (150, 154, 170)),
            hi=(2, 2, (255, 255, 255), 1))
    for k in range(4):
        c.line([(ix0 + 8, iy0 + 10 + k * 6), (ix0 + 26, iy0 + 10 + k * 6)], 1.6, (60, 60, 70))
    c.paint(ell(ix0 + 17, iy0 + 50, 10, 10), (230, 40, 50), ow=2.2, hi=(-2, -2, (255, 140, 140)))
    c.text(ix0 + 17, iy0 + 64, "TALK", 6, (40, 40, 60), "Black")
    # door camera
    c.paint(rrect(dx1 - 4, dy0 - 40, dx1 + 22, dy0 - 24, 3), (40, 40, 48), ow=2)
    c.paint(ell(dx1 + 22, dy0 - 32, 4, 6), (90, 140, 220), ow=1.6)
    c.paint(ell(dx1 - 1, dy0 - 36, 2, 2), (255, 60, 60), ow=0)


def paint_tv_green_room():
    B = boxes("tv_green_room")
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(707)
    # --- wallpaper: dusty peach with cream stripes (it is NOT green)
    wall = (226, 156, 128)

    def stripes(p):
        for x in range(-20, W_BG + 40, 80):
            p.rect(x, 0, x + 26, WALL_Y, lt(wall, 0.16))
            p.line([(x + 40, 0), (x + 40, WALL_Y)], 2, dk(wall, 0.88))
        for x in range(10, W_BG, 80):
            for y in range(60, WALL_Y, 90):
                p.ell(x + 30, y + (x // 80 % 2) * 45, 4, 4, dk(wall, 0.85))
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, dk(wall, 0.85), wall), ow=0, pattern=stripes)
    # chair rail + wainscot
    c.paint(rect(-10, 560, W_BG + 10, WALL_Y), ("v", (120, 70, 90), (90, 50, 70)), ow=3,
            pattern=lambda p: [p.rect(x, 590, x + 130, WALL_Y - 30, (106, 60, 80)) for x in range(20, W_BG, 160)])
    for x in range(20, W_BG, 160):
        c.paint(rect(x, 590, x + 130, WALL_Y - 30), (0, 0, 0, 0), ow=2.4, oc=(70, 36, 54))
    c.paint(rect(-10, 548, W_BG + 10, 566), (240, 210, 170), ow=3, hi=(0, 3, (255, 240, 210)))
    # ceiling strip with dressing-room bulbs
    c.paint(rect(0, 0, W_BG, 60), (70, 40, 50), ow=0)
    c.line([(0, 60), (W_BG, 60)], 4)
    for x in range(60, W_BG, 140):
        c.line([(x, 60), (x, 84)], 2, (40, 30, 30))
        c.paint(ell(x, 92, 10, 12), (255, 246, 200), ow=2.2)
        c.glow(x, 92, 34, (255, 230, 160), 0.35)

    # --- posters: past seasons
    def season_poster(p, x, y, n, col):
        p.rect(x, y, x + 150, y + 200, col)
        p.ell(x + 75, y + 80, 52, 48, (255, 90, 170))
        p.ell(x + 50, y + 66, 26, 24, (255, 120, 190))
        p.ell(x + 100, y + 66, 26, 24, (255, 120, 190))
        p.poly([(x + 26, y + 76), (x + 124, y + 76), (x + 75, y + 128)], (255, 120, 190))
        p.rect(x + 10, y + 150, x + 140, y + 186, (255, 236, 90))
    for i, (px_, py_, n, col, ang) in enumerate(((210, 170, 1, (60, 30, 90), -3), (560, 150, 2, (30, 60, 100), 2))):
        sub = poster(150, 200, col, lambda p, x, y, n=n, col=col: season_poster(p, x, y, n, col))
        sub.text(95, 190, "SEASON %d" % n, 15, (90, 30, 60), "Black")
        sub.text(95, 102, "SDL", 22, (255, 255, 255), "Black", stroke=2)
        c.stamp(sub, px_ + 75, py_ + 100, ang)
    # framed glossy of Roxy (signed)
    fx0, fy0 = 1330, 170
    c.paint(rect(fx0, fy0, fx0 + 170, fy0 + 210), (230, 190, 90), shade=(-4, -4, (170, 130, 50)), hi=(3, 3, (255, 236, 160), 2))

    def glossy(p):
        p.rect(fx0 + 14, fy0 + 14, fx0 + 156, fy0 + 196, (250, 180, 210))
        p.ell(fx0 + 85, fy0 + 210, 60, 70, (232, 40, 150))
        p.ell(fx0 + 85, fy0 + 92, 34, 40, (250, 200, 162))
        p.ell(fx0 + 85, fy0 + 60, 44, 30, (92, 40, 60))
        p.ell(fx0 + 112, fy0 + 92, 14, 34, (92, 40, 60))
        p.ell(fx0 + 85, fy0 + 110, 14, 6, (150, 20, 60))
        p.ell(fx0 + 85, fy0 + 108, 11, 2.5, (255, 255, 255))
        for ex in (-12, 12):
            p.ell(fx0 + 85 + ex, fy0 + 88, 6, 7, (255, 255, 255))
            p.ell(fx0 + 85 + ex - 1, fy0 + 89, 3, 3.5, (110, 60, 200))
        p.line([(fx0 + 24, fy0 + 170), (fx0 + 70, fy0 + 150), (fx0 + 100, fy0 + 176), (fx0 + 146, fy0 + 156)], 3,
               (40, 30, 120))
    c.paint(rect(fx0 + 14, fy0 + 14, fx0 + 156, fy0 + 196), (250, 180, 210), ow=3, pattern=glossy)
    c.text(fx0 + 85, fy0 + 232, "XOXO ROXY", 13, (120, 40, 80), "Italic")
    # wall clock
    c.paint(ell(1140, 210, 46, 46), (250, 248, 240), ow=4, shade=(-3, -3, (200, 196, 190)))
    for k in range(12):
        a = math.radians(k * 30)
        c.line([(1140 + 36 * math.cos(a), 210 + 36 * math.sin(a)), (1140 + 42 * math.cos(a), 210 + 42 * math.sin(a))], 2)
    c.line([(1140, 210), (1140, 178)], 4)
    c.line([(1140, 210), (1164, 220)], 3)
    c.paint(ell(1140, 210, 4, 4), (230, 40, 50), ow=0)
    # QUIET PLEASE sign over the booth door
    bs = B["Booth stairs"]
    c.paint(rrect(bs[0] + 60, bs[1] - 70, bs[2] - 20, bs[1] - 22, 6), (40, 20, 30), ow=3)
    c.text((bs[0] + 60 + bs[2] - 20) / 2, bs[1] - 46, "QUIET PLEASE", 16, (255, 90, 80), "Black")
    c.glow((bs[0] + 40 + bs[2]) / 2, bs[1] - 46, 90, (255, 80, 70), 0.25)

    # --- floor: checker lino
    checker_floor(c, (196, 70, 90), (246, 230, 210), vp=(960, 300), cols=120, rows=7)
    c.paint(rect(-10, WALL_Y - 12, W_BG + 10, WALL_Y + 4), (70, 36, 54), ow=3)  # baseboard
    # rug under the couch area
    c.paint(ell(1440, 870, 200, 40), (110, 70, 150), ow=3,
            pattern=lambda p: (p.ell(1440, 870, 160, 30, (140, 100, 180)), p.ell(1440, 870, 120, 22, (110, 70, 150))))

    # --- studio door (left)
    d = B["Studio door"]
    door(c, d[0] + 6, d[1] + 10, d[2] - 6, d[3], (150, 60, 60), knob="R", casing=(80, 50, 60))
    c.paint(rrect(d[0] + 16, d[1] - 52, d[2] - 16, d[1] - 14, 5), (30, 30, 34), ow=3)
    c.text((d[0] + d[2]) / 2, d[1] - 33, "STUDIO", 18, (255, 236, 160), "Black")
    c.paint(rrect(d[0] + 34, d[1] + 40, d[2] - 34, d[1] + 70, 4), (240, 40, 50), ow=2.5)
    c.text((d[0] + d[2]) / 2, d[1] + 55, "ON AIR", 12, (255, 250, 230), "Black")

    # --- couch (decor) between Gloria and the booth door
    cx0, cx1, cy = 1352, 1536, 790
    sofa = (90, 160, 160)
    c.shadow((cx0 + cx1) / 2, cy, (cx1 - cx0) / 2 + 10, 10, 0.5)
    c.paint(rrect(cx0, cy - 170, cx1, cy - 70, 22), ("v", lt(sofa, 0.15), dk(sofa, 0.85)), shade=(0, -5, dk(sofa, 0.7)),
            hi=(0, 4, lt(sofa, 0.35), 2))
    c.paint(rrect(cx0 - 10, cy - 100, cx1 + 10, cy - 36, 16), sofa, shade=(0, -5, dk(sofa, 0.7)), hi=(0, 3, lt(sofa, 0.3)))
    for ax in (cx0 - 14, cx1 - 26):
        c.paint(rrect(ax, cy - 120, ax + 40, cy - 34, 16), dk(sofa, 0.9), shade=(-3, 0, dk(sofa, 0.65)), hi=(2, 2, lt(sofa, 0.25)))
    for lx in (cx0 + 6, cx1 - 18):
        c.paint(rect(lx, cy - 36, lx + 12, cy - 4), (90, 60, 40), ow=2.5)
    c.paint(rrect(cx0 + 50, cy - 140, cx0 + 110, cy - 96, 12), (255, 200, 80), ow=2.5, shade=(-2, -2, (220, 150, 50)))
    c.paint(rrect(cx1 - 104, cy - 140, cx1 - 44, cy - 96, 12), (240, 100, 150), ow=2.5, shade=(-2, -2, (190, 60, 110)))

    # --- the props inside their hotspot boxes
    craft_table(c, B["Craft services"], rng)
    wardrobe_rack(c, B["Wardrobe rack"], rng)
    makeup_station(c, B["Makeup chair"])
    booth_stairs_door(c, B["Booth stairs"])

    lights = [(1000, 300, 520, 0.45, (255, 230, 180)), (300, 200, 500, 0.3, (255, 220, 170)),
              (1500, 300, 520, 0.3, (255, 220, 190)), (960, 900, 700, 0.25, (255, 230, 200))]
    light_pass(c, 0.86, lights, vign=0.32, front=0.1)
    c.save("bg_tv_green_room.png")


# =========================================================================== control booth background
def monitor_wall(c, box):
    x0, y0, x1, y1 = box
    rack = (40, 42, 52)
    c.paint(rrect(x0, y0, x1, y1, 6), rack, shade=(-4, -4, dk(rack, 0.7)), hi=(3, 3, (90, 92, 110), 2))
    cols, rows = 4, 3
    mw, mh = (x1 - x0 - 30) / cols, (y1 - y0 - 30) / rows
    pics = ["stage", "audience", "teeth", "deck", "bars", "lot", "roxy", "clock", "chet", "heart", "dex", "bars"]
    for r in range(rows):
        for k in range(cols):
            mx0, my0 = x0 + 15 + k * mw + 5, y0 + 15 + r * mh + 5
            mx1, my1 = mx0 + mw - 10, my0 + mh - 10
            kind = pics[r * cols + k]

            def pic(p, kind=kind, mx0=mx0, my0=my0, mx1=mx1, my1=my1):
                w, h = mx1 - mx0, my1 - my0
                cx, cy = (mx0 + mx1) / 2, (my0 + my1) / 2
                if kind == "stage":
                    p.rect(mx0, my0, mx1, my1, (190, 40, 130))
                    for i in range(6):
                        p.line([(mx0 + i * w / 6 + 6, my0), (mx0 + i * w / 6 + 6, my1)], 2, (230, 90, 170))
                    p.rect(mx0, my1 - h * 0.25, mx1, my1, (240, 196, 80))
                elif kind == "audience":
                    p.rect(mx0, my0, mx1, my1, (70, 44, 96))
                    for i in range(7):
                        for j in range(2):
                            p.ell(mx0 + 10 + i * (w - 20) / 6, my0 + h * 0.4 + j * h * 0.3, 6, 7,
                                  [(240, 186, 140), (160, 104, 72), (255, 214, 178)][(i + j) % 3])
                elif kind == "teeth":
                    p.rect(mx0, my0, mx1, my1, (240, 182, 130))
                    p.ell(cx, cy, w * 0.38, h * 0.22, (150, 30, 50))
                    p.rect(cx - w * 0.34, cy - h * 0.14, cx + w * 0.34, cy + h * 0.04, (255, 255, 255))
                elif kind == "deck":
                    p.rect(mx0, my0, mx1, my1, (30, 32, 44))
                    p.rect(cx - w * 0.3, cy - h * 0.2, cx + w * 0.3, cy + h * 0.25, (80, 80, 96))
                    p.rect(cx - w * 0.2, cy - h * 0.1, cx + w * 0.2, cy + h * 0.1, (240, 120, 210))
                    p.ell(cx + w * 0.34, cy - h * 0.3, 4, 4, (255, 60, 60))
                elif kind == "bars":
                    cl = [(250, 250, 250), (250, 230, 60), (60, 230, 230), (60, 220, 80), (230, 60, 220), (230, 50, 50),
                          (50, 60, 230)]
                    for i, col in enumerate(cl):
                        p.rect(mx0 + i * w / 7, my0, mx0 + (i + 1) * w / 7 + 1, my1, col)
                elif kind == "lot":
                    p.rect(mx0, my0, mx1, my1, (40, 50, 70))
                    p.rect(mx0, cy + h * 0.1, mx1, my1, (70, 70, 80))
                    p.rect(cx - w * 0.25, cy - h * 0.05, cx + w * 0.25, cy + h * 0.2, (230, 60, 60))
                    p.ell(cx - w * 0.15, cy + h * 0.22, 5, 5, (20, 20, 20))
                    p.ell(cx + w * 0.15, cy + h * 0.22, 5, 5, (20, 20, 20))
                elif kind == "roxy":
                    p.rect(mx0, my0, mx1, my1, (250, 170, 210))
                    p.ell(cx, my1, w * 0.3, h * 0.35, (232, 40, 150))
                    p.ell(cx, cy - h * 0.05, w * 0.15, h * 0.22, (250, 200, 162))
                    p.ell(cx, cy - h * 0.22, w * 0.2, h * 0.15, (92, 40, 60))
                elif kind == "clock":
                    p.rect(mx0, my0, mx1, my1, (20, 10, 14))
                elif kind == "chet":
                    p.rect(mx0, my0, mx1, my1, (90, 160, 200))
                    p.ell(cx, my1, w * 0.3, h * 0.35, (250, 246, 236))
                    p.ell(cx, cy - h * 0.02, w * 0.15, h * 0.22, (240, 182, 130))
                    p.ell(cx + w * 0.02, cy - h * 0.26, w * 0.2, h * 0.14, (255, 214, 90))
                    p.ell(cx + w * 0.14, cy, 3, 3, (240, 220, 200))
                elif kind == "heart":
                    p.rect(mx0, my0, mx1, my1, (40, 10, 50))
                    p.ell(cx - w * 0.1, cy - h * 0.08, w * 0.12, h * 0.16, (255, 90, 170))
                    p.ell(cx + w * 0.1, cy - h * 0.08, w * 0.12, h * 0.16, (255, 90, 170))
                    p.poly([(cx - w * 0.22, cy - h * 0.02), (cx + w * 0.22, cy - h * 0.02), (cx, cy + h * 0.3)],
                           (255, 90, 170))
                elif kind == "dex":
                    p.rect(mx0, my0, mx1, my1, (120, 80, 150))
                    p.ell(cx, my1, w * 0.3, h * 0.35, (40, 200, 200))
                    p.ell(cx, cy - h * 0.02, w * 0.15, h * 0.22, (255, 212, 172))
                    for i in range(5):
                        p.poly([(cx - w * 0.18 + i * w * 0.09, cy - h * 0.16), (cx - w * 0.14 + i * w * 0.09, cy - h * 0.42),
                                (cx - w * 0.1 + i * w * 0.09, cy - h * 0.16)], (255, 140, 40))
                # scanlines
                for yy in range(int(my0) + 3, int(my1), 5):
                    p.line([(mx0, yy), (mx1, yy)], 1, (0, 0, 0))
            c.paint(rrect(mx0 - 3, my0 - 3, mx1 + 3, my1 + 3, 3), (20, 20, 26), ow=2.5)
            c.paint(rect(mx0, my0, mx1, my1), (30, 30, 40), ow=1.5, pattern=pic)
            if kind == "clock":
                c.text((mx0 + mx1) / 2, (my0 + my1) / 2, "4:00", 22, (255, 60, 60), "Black")
            c.paint(rect(mx0, my0, mx1, my1), (180, 220, 255), ow=0, opacity=0.08)
            c.text(mx0 + 12, my1 - 8, str(r * cols + k + 1), 7, (255, 255, 255), "Black")
    for k in range(4):  # little tally lamps
        c.paint(ell(x0 + 40 + k * 110, y1 - 6, 4, 4), (255, 60, 60) if k == 0 else (60, 200, 90), ow=1.6)


def studio_view_window(c, x0, y0, x1, y1):
    """The big booth window looking down at the studio floor."""
    fr = (50, 52, 62)
    c.paint(rect(x0 - 16, y0 - 16, x1 + 16, y1 + 16), fr, shade=(-4, -4, dk(fr, 0.7)), hi=(3, 3, (100, 100, 120), 2))

    def view(p):
        p.rect(x0, y0, x1, y1, (60, 30, 70))
        # sequin curtain across the back, seen from above
        for x in range(int(x0), int(x1), 22):
            p.line([(x, y0), (x + 4, y0 + (y1 - y0) * 0.55)], 6, (176, 34, 120))
            p.line([(x + 8, y0), (x + 10, y0 + (y1 - y0) * 0.55)], 2, (230, 90, 170))
        hx, hy = x0 + (x1 - x0) * 0.6, y0 + 90
        p.ell(hx - 30, hy - 10, 36, 32, (255, 90, 170))
        p.ell(hx + 30, hy - 10, 36, 32, (255, 90, 170))
        p.poly([(hx - 64, hy), (hx + 64, hy), (hx, hy + 60)], (255, 90, 170))
        p.rect(x0, y0 + (y1 - y0) * 0.55, x1, y1, (120, 76, 136))  # studio floor
        p.rect(x0, y0 + (y1 - y0) * 0.55, x1, y0 + (y1 - y0) * 0.55 + 14, (240, 196, 80))
        # tiny people: Roxy at the podium, Chet, the audience edge
        rx, ry = x0 + (x1 - x0) * 0.45, y0 + (y1 - y0) * 0.72
        p.rect(rx + 16, ry - 10, rx + 40, ry + 22, (236, 50, 140))
        p.ell(rx, ry - 18, 8, 9, (250, 200, 162))
        p.ell(rx, ry - 26, 10, 7, (92, 40, 60))
        p.rect(rx - 8, ry - 8, rx + 8, ry + 24, (232, 40, 150))
        cx, cy = x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.75
        p.ell(cx, cy - 18, 8, 9, (240, 182, 130))
        p.ell(cx, cy - 27, 10, 7, (255, 214, 90))
        p.rect(cx - 8, cy - 8, cx + 8, cy + 24, (250, 246, 236))
        for i in range(8):
            p.ell(x0 + 24 + i * 26, y1 - 18, 9, 10, [(240, 186, 140), (160, 104, 72), (255, 214, 178)][i % 3])
            p.rect(x0 + 15 + i * 26, y1 - 8, x0 + 33 + i * 26, y1, [(70, 120, 180), (200, 90, 60), (90, 150, 90)][i % 3])
    c.paint(rect(x0, y0, x1, y1), (60, 30, 70), ow=3, pattern=view)
    # glass reflections + mullions
    for gx in (x0 + 40, x0 + (x1 - x0) * 0.55):
        c.paint(poly([(gx, y0), (gx + 60, y0), (gx - 40, y1), (gx - 100, y1)]), (255, 255, 255), ow=0, opacity=0.07)
    for k in (1, 2):
        mx = x0 + (x1 - x0) * k / 3
        c.paint(rect(mx - 6, y0, mx + 6, y1), fr, ow=2.5)
    c.glow(x0 + (x1 - x0) * 0.6, y0 + 100, 200, (255, 80, 170), 0.18)


def paint_tv_control_booth():
    B = boxes("tv_control_booth")
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(808)
    wall_top, wall_bot = (26, 30, 46), (52, 58, 82)
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, wall_top, wall_bot), ow=0)
    # acoustic foam wedges
    for row, y in enumerate(range(90, 560, 64)):
        for x in range(0 + (row % 2) * 32, W_BG, 64):
            c.paint(poly([(x, y), (x + 56, y), (x + 28, y + 56)]), (48, 54, 76), ow=2, oc=(20, 22, 34))
            c.paint(poly([(x + 28, y + 56), (x + 56, y), (x + 56, y + 56)]), (36, 40, 60), ow=0)
    c.paint(rect(0, 0, W_BG, 70), (16, 18, 28), ow=0)
    c.line([(0, 70), (W_BG, 70)], 4)
    for x in (300, 960, 1600):  # recessed ceiling spots
        c.paint(ell(x, 70, 40, 8), (255, 244, 210), ow=2.5)
        c.paint(poly([(x - 36, 72), (x + 36, 72), (x + 180, 600), (x - 180, 600)]), (255, 240, 200), ow=0, opacity=0.05)
    # big window down onto the studio
    studio_view_window(c, 1220, 120, 1880, 470)
    c.paint(rect(1196, 486, 1904, 504), (90, 94, 110), ow=3, hi=(0, 2, (150, 154, 170)))  # sill
    # countdown clock
    c.paint(rrect(820, 150, 1100, 250, 10), (20, 10, 14), ow=4, hi=(3, 3, (70, 50, 60), 2))
    c.text(960, 200, "00:04:00", 46, (255, 50, 50), "Black", stroke=2, sc=(110, 0, 0))
    c.glow(960, 200, 170, (255, 40, 40), 0.3)
    c.text(960, 270, "TO AIR", 18, (255, 120, 110), "Black")
    # ON AIR light over the stairs
    c.paint(rrect(30, 380, 190, 430, 8), (60, 20, 26), shade=(-3, -3), hi=(3, 3, (120, 50, 60), 2))
    c.paint(rrect(40, 388, 180, 422, 5), (110, 40, 46), ow=2.5)
    c.text(110, 405, "ON AIR", 20, (220, 150, 140), "Black")

    # floor: dark carpet tiles with cables
    fl = (44, 46, 60)
    c.paint(rect(0, WALL_Y, W_BG, H_BG), ("vy", WALL_Y, H_BG, (70, 72, 90), (34, 36, 48)), ow=0)
    for x in range(-600, W_BG + 600, 150):
        c.line([(960 + (x - 960) * 0.55, WALL_Y), (x, H_BG)], 1.6, (20, 20, 30), opacity=0.5)
    for y in (830, 890, 970, 1060):
        c.line([(0, y), (W_BG, y)], 1.4, (20, 20, 30), opacity=0.5)
    c.line(bez((1000, 812), (1150, 840), (1300, 808)), 4, (16, 16, 22))
    c.line(bez((300, 806), (480, 830), (720, 800)), 4, (16, 16, 22))
    c.paint(rect(-10, WALL_Y - 12, W_BG + 10, WALL_Y + 4), (20, 22, 30), ow=3)

    # --- long console under the monitors (decor)
    con = (70, 72, 88)
    c.paint(poly([(240, 640), (790, 640), (800, 676), (230, 676)]), (90, 92, 110), hi=(0, 3, (140, 144, 160)))
    c.paint(rect(236, 674, 794, WALL_Y), ("v", con, dk(con, 0.75)), ow=3,
            pattern=lambda p: [p.rect(250 + k * 136, 694, 360 + k * 136, 770, dk(con, 0.85)) for k in range(4)])
    for k in range(18):
        bx = 262 + k * 28
        c.paint(rrect(bx, 646, bx + 18, 660, 2), [(255, 80, 80), (255, 210, 60), (90, 220, 120), (90, 160, 230)][k % 4],
                ow=1.6)
    # coffee counter (under the coffee maker)
    cm = B["Coffee maker"]
    ctop = cm[3]
    c.paint(rect(cm[0] - 40, ctop, cm[2] + 40, ctop + 14), (150, 120, 90), ow=3, hi=(0, 2, (200, 170, 130)))
    c.paint(rect(cm[0] - 34, ctop + 14, cm[2] + 34, WALL_Y), ("v", (120, 90, 70), (90, 64, 50)), ow=3,
            pattern=lambda p: p.line([((cm[0] + cm[2]) / 2, ctop + 14), ((cm[0] + cm[2]) / 2, WALL_Y)], 2, (60, 40, 30)))
    for kx in ((cm[0] + cm[2]) / 2 - 14, (cm[0] + cm[2]) / 2 + 14):
        c.paint(ell(kx, ctop + 50, 4, 4), (230, 200, 120), ow=1.6)
    # Norma's rolling chair (decor, between Norma and the deck)
    chx, chy = 1222, WALL_Y + 30
    c.shadow(chx, chy, 44, 8, 0.5)
    for k in (-1, 0, 1):
        c.paint(cap([(chx, chy - 30), (chx + k * 34, chy - 4)], 6), (40, 40, 48), ow=2.2)
        c.paint(ell(chx + k * 34, chy - 2, 6, 5), (20, 20, 26), ow=2)
    c.paint(rect(chx - 5, chy - 70, chx + 5, chy - 30), (150, 154, 170), ow=2.2)
    c.paint(rrect(chx - 40, chy - 84, chx + 40, chy - 62, 8), (60, 50, 90), ow=3, hi=(0, 2, (110, 96, 150)))
    c.paint(rrect(chx - 30, chy - 170, chx + 30, chy - 88, 12), (60, 50, 90), ow=3, hi=(2, 2, (110, 96, 150)))
    c.paint(rect(chx - 4, chy - 92, chx + 4, chy - 80), (40, 40, 48), ow=2)
    c.text(chx, chy - 130, "DIRECTOR", 8, (255, 220, 120), "Black")

    # --- props inside their hotspot boxes
    monitor_wall(c, B["Monitor wall"])
    # stairs down (left)
    s = B["Stairs down"]
    sx0, sy0, sx1, sy1 = s
    c.paint(rect(sx0, sy0 + 20, sx1, sy1), (14, 14, 20), ow=4)
    for k in range(7):
        yy = sy0 + 70 + k * 30
        c.paint(rect(sx0 + 6, yy, sx1 - 6 - k * 4, yy + 14), (80, 84, 100), ow=2, hi=(0, 2, (130, 134, 150)))
    c.paint(cap([(sx1 + 4, sy0 + 40), (sx1 + 4, sy1)], 7), (200, 204, 216), ow=2.5)
    c.paint(cap([(sx0 + 10, sy0 + 90), (sx1 + 4, sy0 + 40)], 6), (200, 204, 216), ow=2.5)
    c.paint(rrect(sx0 + 18, sy0 - 26, sx1 - 18, sy0 + 10, 4), (40, 160, 90), ow=3)
    c.text((sx0 + sx1) / 2, sy0 - 8, "STAIRS", 14, (255, 255, 255), "Black")
    # coffee maker
    cx0, cy0, cx1, cy1 = cm
    c.paint(rrect(cx0 + 6, cy0 + 4, cx1 - 6, cy1, 6), (40, 40, 48), shade=(-3, -3, (20, 20, 26)), hi=(2, 2, (100, 100, 120), 2))
    c.paint(rect(cx0 + 18, cy0 + 50, cx1 - 18, cy1 - 8), (20, 20, 26), ow=2)
    c.paint(poly([(cx0 + 22, cy0 + 62), (cx1 - 22, cy0 + 62), (cx1 - 26, cy1 - 12), (cx0 + 26, cy1 - 12)]),
            (200, 230, 240), ow=2.5, pattern=lambda p: p.rect(cx0 + 22, cy0 + 80, cx1 - 22, cy1 - 12, (90, 50, 30)))
    c.paint(rect(cx0 + 12, cy0 + 14, cx1 - 12, cy0 + 40), (250, 248, 236), ow=2,
            pattern=lambda p: [p.line([(cx0 + 16, cy0 + 22 + k * 7), (cx1 - 16, cy0 + 22 + k * 7)], 1, (200, 60, 60))
                               for k in range(3)])
    c.text((cx0 + cx1) / 2, cy0 + 27, "NORMA'S", 8, (200, 40, 40), "Black")
    c.paint(ell(cx1 - 14, cy0 + 50, 3, 3), (90, 230, 120), ow=1.2)
    for k in range(3):  # steam
        c.curve((cx0 + 30 + k * 12, cy0 + 2), (cx0 + 22 + k * 12, cy0 - 14), (cx0 + 32 + k * 12, cy0 - 30), 2,
                (230, 230, 240), opacity=0.5)
    c.paint(ell(cx0 - 22, ctop - 10, 12, 10), (250, 250, 250), ow=2.5)  # mug
    c.text(cx0 - 22, ctop - 10, "#1", 7, (200, 40, 80), "Black")
    # director's desk with talkback mic
    t = B["Talkback mic"]
    tx0, ty0, tx1, ty1 = t
    desk = (80, 84, 100)
    c.shadow((tx0 + tx1) / 2, ty1 - 2, (tx1 - tx0) / 2, 8, 0.5)
    top = ty0 + 92
    c.paint(poly([(tx0 + 4, top), (tx1 - 4, top), (tx1, top + 30), (tx0, top + 30)]), (110, 114, 130),
            hi=(0, 3, (160, 164, 180)))
    c.paint(rect(tx0 + 6, top + 30, tx1 - 6, ty1), ("v", desk, dk(desk, 0.7)), ow=3,
            pattern=lambda p: [p.rect(tx0 + 20 + k * 74, top + 46, tx0 + 80 + k * 74, ty1 - 14, dk(desk, 0.85))
                               for k in range(3)])
    for k in range(14):  # faders
        fx = tx0 + 20 + k * 15
        c.line([(fx, top + 6), (fx + 1, top + 26)], 1.6, (20, 20, 26))
        c.paint(rect(fx - 3, top + 8 + (k * 5) % 12, fx + 3, top + 13 + (k * 5) % 12), (230, 230, 240), ow=1.2)
    # gooseneck mic
    gx = tx1 - 60
    c.paint(rrect(gx - 26, top - 16, gx + 26, top + 2, 4), (40, 40, 48), ow=2.5)
    c.paint(rrect(gx - 18, top - 14, gx + 2, top - 4, 2), (230, 40, 50), ow=1.6)
    c.text(gx + 14, top - 8, "TALK", 6, (255, 220, 120), "Black")
    c.line(bez((gx + 10, top - 16), (gx + 30, top - 70), (gx - 10, top - 86)), 6, OUT)
    c.line(bez((gx + 10, top - 16), (gx + 30, top - 70), (gx - 10, top - 86)), 3, (170, 174, 190))
    c.paint(ell(gx - 16, top - 88, 10, 8, -30), (60, 60, 70), ow=2.5,
            pattern=lambda p: [p.line([(gx - 26, top - 92 + k * 3), (gx - 6, top - 92 + k * 3)], 1, (120, 120, 130))
                               for k in range(5)])
    # stopwatch + clipboard on the desk
    c.paint(rect(tx0 + 40, top - 10, tx0 + 96, top + 2), (186, 130, 72), ow=2.2)
    c.paint(ell(tx0 + 130, top - 8, 12, 11), (220, 224, 236), ow=2.5, pattern=lambda p: p.line(
        [(tx0 + 130, top - 8), (tx0 + 134, top - 15)], 1.4, (200, 40, 40)))

    lights = [(1550, 300, 600, 0.45, (255, 120, 200)), (960, 200, 360, 0.35, (255, 80, 80)),
              (530, 430, 460, 0.45, (150, 210, 255)), (300, 70, 500, 0.25, (255, 240, 200)),
              (960, 900, 700, 0.2, (200, 210, 255))]
    light_pass(c, 0.78, lights, vign=0.35, front=0.12)
    c.save("bg_tv_control_booth.png")


# =========================================================================== new characters
def paint_gloria_puff():
    """Makeup artist: towering platinum beehive, lavender smock full of brushes, giant powder puff."""
    c = Canvas(110, 270, ow=3)
    skin, skin_sh = (232, 170, 130), (196, 128, 100)
    hair, hair_sh, hair_hi = (252, 230, 150), (214, 180, 96), (255, 250, 220)
    smock, smock_sh = (190, 150, 230), (146, 106, 190)
    pants, pants_sh = (60, 50, 70), (36, 30, 44)
    shoe, shoe_sh = (230, 60, 120), (170, 30, 90)
    # beehive behind the head
    hive = poly([(32, 60), (26, 40), (28, 20), (38, 6), (56, 1), (74, 4), (88, 16), (92, 36), (88, 58), (78, 68),
                 (42, 68)], 2, True)
    c.paint(hive, hair, shade=(3, 3, hair_sh), hi=(-3, 3, hair_hi, 2),
            pattern=lambda p: [p.line(bez((34 + k * 3, 52 - k * 9), (60, 30 - k * 9), (86 - k * 2, 50 - k * 9)), 1.6,
                                      hair_sh) for k in range(5)])
    c.paint(ell(78, 20, 6, 4, 30), (240, 60, 120), ow=2)  # bow
    c.paint(ell(88, 22, 6, 4, -30), (240, 60, 120), ow=2)
    # far arm with the powder puff raised
    c.paint(cap([(74, 104), (92, 112), (98, 92)], 8.5), smock, shade=(3, 2, smock_sh))
    c.paint(ell(99, 86, 6.5, 6), skin, shade=(2, 2, skin_sh))
    c.paint(ell(100, 78, 13, 10), (255, 214, 226), ow=2.5, hi=(-2, -2, (255, 245, 250), 2))
    c.paint(ell(100, 70, 4, 3), (240, 120, 160), ow=1.6)
    for k in range(5):  # powder cloud
        c.paint(ell(92 + k * 4, 62 - k * 3, 3 + k * 0.5, 3 + k * 0.5), (255, 250, 250), ow=0, opacity=0.7)
    # legs + pink kitten heels
    c.paint(cap([(60, 190), (64, 238)], 10.5), pants, shade=(3, 0, pants_sh))
    c.paint(cap([(46, 190), (40, 240)], 11), pants, shade=(3, 0, pants_sh))
    for xh, xt, yt, yb in ((72, 48, 236, 250), (50, 18, 239, 254)):
        c.paint(shoe_shape(xh, xt, yt, yb, pointy=True), shoe, shade=(3, -2, shoe_sh), hi=(-2, 2, (255, 140, 190), 1.5))
    # smock: wide, knee length, with a pocket full of brushes
    body = poly([(34, 96), (54, 90), (76, 96), (82, 112), (86, 196), (24, 196), (28, 112)], 2)
    c.paint(body, smock, shade=(5, 2, smock_sh), hi=(-3, 3, (220, 196, 250), 2),
            pattern=lambda p: [p.ell(30 + (k * 17) % 54, 110 + (k * 23) % 80, 1.8, 1.8, (255, 230, 250)) for k in range(18)])
    c.paint(rrect(44, 140, 74, 164, 3), smock_sh, ow=2.2)
    for k, col in enumerate(((240, 60, 90), (90, 60, 160), (250, 200, 80), (60, 160, 200))):
        bx = 48 + k * 7
        c.line([(bx, 142), (bx - 1 + k, 122)], 2.6, (150, 100, 70))
        c.paint(ell(bx - 1 + k, 120, 2.4, 4), col, ow=1.2)
    c.paint(poly([(48, 92), (64, 92), (56, 110)]), (255, 250, 246), ow=2)
    # measuring tape round the neck
    c.paint(cap([(42, 94), (40, 134)], 4), (250, 220, 80), ow=1.6)
    c.paint(cap([(70, 94), (72, 128)], 4), (250, 220, 80), ow=1.6)
    # near arm on the hip
    c.paint(cap([(34, 102), (22, 128), (34, 146)], 8.5), smock, shade=(3, 2, smock_sh))
    c.paint(ell(36, 146, 6, 6), skin, shade=(2, 2, skin_sh))
    # neck + head (3/4, facing left)
    c.paint(cap([(56, 80), (56, 96)], 9), skin, shade=(3, 0, skin_sh))
    head = ell(56, 60, 21, 23) + poly([(36, 62), (40, 80), (52, 88), (64, 86), (76, 72)], 2) + ell(34, 64, 4.6, 4.4)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (250, 200, 166), 2.5))
    c.paint(ell(76, 64, 5, 7), skin, shade=(2, 2, skin_sh))
    c.paint(ell(77, 74, 3.4, 3.4), (120, 230, 220), ow=1.6)  # earring
    c.curve((35, 67), (32, 68), (32, 65), 1.4)
    c.paint(ell(52, 73, 6, 3.2), (255, 90, 130), ow=0, opacity=0.6)  # lots of blush
    c.paint(ell(39, 72, 3.4, 2.4), (255, 90, 130), ow=0, opacity=0.5)
    # cat-eye glasses
    eye(c, 52, 59, 7, 8, 48.5, 60, 2.3, lid=0.25, skin=skin, lashes=1, iris=(60, 150, 120))
    eye(c, 38, 58.5, 5, 7.6, 35.5, 59.5, 2.0, lid=0.25, skin=skin, lashes=-1, iris=(60, 150, 120))
    c.paint(poly([(42, 52), (60, 50), (64, 46), (62, 66), (44, 66)], 1), (0, 0, 0, 0), ow=2.4, oc=(200, 40, 110))
    c.paint(poly([(32, 53), (42, 52), (42, 65), (32, 64), (30, 50)], 1), (0, 0, 0, 0), ow=2.2, oc=(200, 40, 110))
    c.line([(42, 56), (44, 56)], 2, (200, 40, 110))
    # bright red lips, talking mid-sentence
    c.paint(ell(46, 79, 7, 4), (210, 20, 50), ow=2, pattern=lambda p: p.ell(46, 80, 4, 1.6, (120, 10, 30)))
    # front swoop of hair over the forehead
    front = poly([(34, 52), (36, 40), (48, 34), (66, 34), (80, 40), (84, 56), (78, 54), (66, 44), (52, 44), (40, 50)], 2, True)
    c.paint(front, hair, shade=(3, 3, hair_sh), hi=(-2, 3, hair_hi, 2))
    c.curve((80, 44), (88, 60), (82, 72), 3.4, hair)
    c.fit(margin=3)
    c.save("hs_gloria_puff.png")


def paint_norma_fade():
    """TV director: headset, chunky glasses, mustard cardigan with pencils, stopwatch, clipboard."""
    c = Canvas(110, 250, ow=3)
    skin, skin_sh = (196, 140, 106), (160, 104, 80)
    hair, hair_sh, hair_hi = (150, 150, 158), (106, 106, 116), (210, 210, 220)
    card, card_sh = (226, 172, 60), (180, 126, 36)
    shirt = (250, 250, 244)
    pants, pants_sh = (50, 56, 80), (30, 34, 54)
    shoe, shoe_sh = (60, 40, 30), (36, 22, 16)
    # far arm holding a clipboard up, pointing at the viewer
    c.paint(cap([(74, 100), (90, 120), (96, 104)], 8.5), card, shade=(3, 2, card_sh))
    c.paint(rrect(84, 86, 108, 118, 2), (186, 130, 72), ow=2.2)
    c.paint(rect(87, 92, 105, 116), (250, 250, 244), ow=1.4,
            pattern=lambda p: [p.line([(89, 96 + k * 4), (103, 96 + k * 4)], 0.9, (150, 170, 210)) for k in range(5)])
    c.paint(ell(94, 106, 6, 5.5), skin, shade=(2, 2, skin_sh))
    # legs + sensible shoes
    c.paint(cap([(62, 160), (66, 222)], 12), pants, shade=(3, 0, pants_sh))
    c.paint(cap([(46, 160), (40, 224)], 12.5), pants, shade=(3, 0, pants_sh))
    for xh, xt, yt, yb in ((74, 48, 220, 236), (52, 16, 223, 240)):
        c.paint(shoe_shape(xh, xt, yt, yb), shoe, shade=(3, -2, shoe_sh), hi=(-2, 2, (120, 90, 70), 1.5))
    # cardigan over a white shirt
    torso = poly([(32, 96), (54, 90), (76, 96), (82, 110), (80, 166), (30, 166), (28, 110)], 2)
    c.paint(torso, card, shade=(5, 2, card_sh), hi=(-3, 3, (250, 214, 120), 2))
    c.paint(poly([(48, 92), (64, 92), (62, 166), (50, 166)], 1), shirt, ow=2.2)
    for y in (110, 128, 146):
        c.paint(ell(46, y, 2.2, 2.2), (120, 80, 30), ow=1.2)
    for k, col in enumerate(((240, 200, 60), (230, 60, 60), (60, 120, 220))):  # pencils in pocket
        c.line([(68 + k * 4, 128), (68 + k * 4, 114)], 2.4, col)
    c.paint(rect(64, 124, 82, 140), card_sh, ow=2)
    # stopwatch on a cord
    c.curve((48, 92), (56, 118), (64, 92), 1.6, (40, 40, 48))
    c.paint(ell(56, 124, 7, 7), (220, 224, 236), ow=2.2, pattern=lambda p: p.line([(56, 124), (59, 119)], 1.2, (200, 40, 40)))
    # near arm, hand on headset mic
    c.paint(cap([(34, 100), (24, 124), (30, 92)], 8.5), card, shade=(3, 2, card_sh))
    c.paint(ell(30, 88, 6, 6), skin, shade=(2, 2, skin_sh))
    # neck + head
    c.paint(cap([(56, 76), (56, 94)], 10), skin, shade=(3, 0, skin_sh))
    head = ell(56, 56, 22, 24) + poly([(34, 58), (38, 76), (50, 86), (62, 84), (76, 70)], 2) + ell(33, 61, 4.8, 4.6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (220, 166, 130), 2.5))
    c.curve((34, 64), (31, 65), (31, 62), 1.4)
    # chunky black glasses, frazzled eyes wide open
    eye(c, 51, 56, 7.5, 8.5, 47.5, 57, 2.4, lid=0.05, skin=skin)
    eye(c, 37, 55.5, 5.4, 8, 34.5, 56.5, 2.1, lid=0.05, skin=skin)
    c.paint(rrect(42, 46, 62, 66, 4), (0, 0, 0, 0), ow=3.4, oc=(20, 20, 26))
    c.paint(rrect(30, 46, 42, 65, 3), (0, 0, 0, 0), ow=3, oc=(20, 20, 26))
    c.line([(62, 52), (74, 54)], 2.6, (20, 20, 26))
    c.line([(43, 41), (52, 38), (61, 41)], 2.4, hair_sh)
    c.line([(31, 42), (38, 40)], 2.2, hair_sh)
    # tight frown
    c.line([(38, 76), (44, 74), (50, 76)], 2)
    # grey bob
    bob = poly([(32, 50), (32, 36), (44, 26), (62, 24), (78, 30), (84, 46), (84, 74), (76, 76), (74, 52), (66, 40),
                (52, 38), (40, 44), (36, 54)], 2, True)
    c.paint(bob, hair, shade=(3, 3, hair_sh), hi=(-2, 3, hair_hi, 2))
    c.curve((44, 30), (60, 26), (76, 34), 1.4, hair_hi)
    # headset: band over the bob, ear cup, boom mic to the mouth
    c.curve((40, 34), (60, 14), (80, 40), 3.2, (40, 40, 48))
    c.paint(ell(78, 58, 8, 10), (40, 40, 48), ow=2.5, hi=(-2, -2, (100, 100, 120)))
    c.line(bez((76, 66), (64, 84), (44, 80)), 3.4, OUT)
    c.line(bez((76, 66), (64, 84), (44, 80)), 1.8, (90, 90, 104))
    c.paint(ell(42, 80, 4, 3), (40, 40, 48), ow=1.8)
    c.fit(margin=3)
    c.save("hs_norma_fade.png")


# =========================================================================== props that change
def paint_reserved_sign():
    c = Canvas(80, 120, ow=3)
    brass, brass_sh = (230, 190, 80), (180, 130, 40)
    c.paint(ell(40, 112, 26, 6), brass, shade=(0, -2, brass_sh), hi=(0, 2, (255, 236, 160)))
    c.paint(cap([(40, 110), (40, 56)], 5), brass, shade=(2, 0, brass_sh), hi=(-1, 0, (255, 240, 180)))
    c.paint(rect(6, 14, 74, 58), brass, shade=(-2, -2, brass_sh))
    c.paint(rect(11, 18, 69, 54), (252, 250, 240), ow=2)
    c.text(40, 28, "RESERVED", 9.5, (200, 40, 60), "Black")
    c.text(40, 40, "C. STUDWELL", 7, (40, 40, 60), "Black")
    c.text(40, 49, "ALL NIGHT", 6, (40, 40, 60), "Black")
    c.fit(margin=2)
    c.save("hs_reserved_sign.png")


def deck_prop(name, loaded):
    c = Canvas(200, 160, ow=3)
    cart = (60, 62, 76)
    # wheeled cart
    for wx in (24, 176):
        c.paint(ell(wx, 150, 8, 7), (20, 20, 26), ow=2.5)
    c.paint(rect(14, 96, 186, 142), ("v", cart, dk(cart, 0.75)), ow=3, hi=(0, 3, lt(cart, 0.3)),
            pattern=lambda p: [p.rect(24 + k * 54, 104, 70 + k * 54, 134, dk(cart, 0.85)) for k in range(3)])
    # transmitter box with bendy antenna
    c.paint(rrect(118, 50, 182, 96, 4), (40, 40, 48), hi=(0, 2, (100, 100, 120)))
    for k in range(4):
        c.line([(126, 60 + k * 7), (156, 60 + k * 7)], 2, (20, 20, 26))
    c.paint(ell(170, 62, 5, 5), (255, 60, 60) if loaded else (90, 30, 30), ow=2)
    if loaded:
        c.glow(170, 62, 20, (255, 60, 60), 0.6)
    c.line(bez((164, 50), (172, 26), (160, 6)), 4, OUT)
    c.line(bez((164, 50), (172, 26), (160, 6)), 2, (190, 194, 206))
    c.paint(ell(160, 6, 4, 4), (190, 194, 206), ow=2)
    if loaded:
        for r in (10, 16):
            c.curve((150, 12 - r * 0.2), (160 - r, 6), (150, 0 + r * 0.1), 1.6, (255, 120, 200), opacity=0.6)
    # tape deck
    c.paint(rrect(16, 44, 116, 96, 5), (30, 30, 36), hi=(0, 2, (90, 90, 110)))
    c.paint(rect(26, 52, 92, 82), (80, 84, 100), ow=2)
    if loaded:
        c.paint(rect(30, 56, 88, 78), (255, 140, 220), ow=2,
                pattern=lambda p: [paint.sparkle(p, 34 + (k * 13) % 50, 59 + (k * 7) % 16, 2.2, (255, 255, 255))
                                   for k in range(8)])
        c.paint(rect(42, 62, 76, 72), (60, 50, 70), ow=1.6)
        for wx in (49, 69):
            c.paint(ell(wx, 67, 3, 3), (250, 250, 250), ow=1.2)
    for k in range(4):
        c.paint(rrect(96 + (k % 2) * 10, 54 + (k // 2) * 14, 104 + (k % 2) * 10, 62 + (k // 2) * 14, 1),
                (200, 200, 210), ow=1.4)
    # label
    c.paint(rect(18, 26, 114, 46), (255, 240, 110), ow=2)
    c.text(66, 31.5, "CH. CHET", 6.5, (200, 40, 40), "Black")
    c.text(66, 40, "DO NOT TOUCH", 5.5, (200, 40, 40), "Black")
    c.fit(margin=2)
    c.save(name)


def paint_playback_deck():
    deck_prop("hs_playback_deck.png", True)


def paint_empty_deck():
    deck_prop("hs_empty_deck.png", False)


# =========================================================================== new inventory icons
def paint_icon_reserved_card():
    def draw(c):
        c.paint(rect(14, 34, 114, 96), (252, 250, 240), shade=(4, 4, (210, 206, 196)), hi=(-3, -3, (255, 255, 255), 2))
        c.paint(rect(22, 42, 106, 88), (0, 0, 0, 0), ow=2, oc=(230, 190, 80))
        c.text(64, 56, "RESERVED", 14, (200, 40, 60), "Black")
        c.text(64, 74, "C. STUDWELL", 10, (40, 40, 60), "Black")
        star(c, 104, 34, 10, (255, 226, 80), ow=3)
    icon("icon_reserved_card.png", 8, draw)


def paint_icon_scandal_lipstick():
    def draw(c):
        c.paint(rrect(42, 70, 86, 122, 5), (230, 190, 80), shade=(4, 0, (180, 130, 40)), hi=(-3, 0, (255, 236, 160), 2))
        c.paint(rect(46, 58, 82, 72), (200, 204, 216), hi=(-2, 0, (255, 255, 255)))
        c.paint(poly([(50, 58), (78, 58), (78, 30), (62, 12), (50, 22)], 1), (220, 20, 50), shade=(3, 0, (160, 10, 30)),
                hi=(-2, 0, (255, 110, 120), 2))
        c.text(64, 98, "SR", 16, (120, 70, 20), "Black")
    icon("icon_scandal_lipstick.png", -18, draw)


def paint_icon_chet_protest_sign():
    def draw(c):
        c.paint(rect(12, 22, 116, 92), (252, 250, 240), shade=(4, 4, (210, 206, 196)))
        c.text(64, 42, "CHET IS", 17, (220, 20, 50), "Black")
        c.text(64, 64, "A CHEAT", 17, (220, 20, 50), "Black")
        c.paint(rrect(42, 74, 86, 88, 4), (255, 255, 255), ow=2)
        for k in range(4):
            c.line([(48 + k * 10, 74), (48 + k * 10, 88)], 1.2, (180, 180, 200))
    icon("icon_chet_protest_sign.png", -6, draw)


def paint_icon_runner_lanyard():
    def draw(c):
        c.line(bez((30, 10), (64, 90), (98, 10)), 9, OUT)
        c.line(bez((30, 10), (64, 90), (98, 10)), 6, (40, 110, 220))
        c.paint(rrect(40, 64, 88, 122, 5), (250, 250, 252), shade=(3, 3, (200, 204, 216)))
        c.paint(rect(40, 64, 88, 80), (40, 110, 220), ow=0)
        c.text(64, 72, "CREW", 10, (255, 255, 255), "Black")
        c.text(64, 94, "KEVIN", 11, (40, 40, 60), "Black")
        c.text(64, 108, "ALL ACCESS", 6, (200, 40, 60), "Black")
        c.paint(rect(58, 56, 70, 66), (200, 204, 216), ow=2)
    icon("icon_runner_lanyard.png", 6, draw)


def headphones(c, col=(60, 220, 230), straw=False):
    c.line(bez((24, 70), (64, -6), (104, 70)), 12, OUT)
    c.line(bez((24, 70), (64, -6), (104, 70)), 7, (40, 40, 46))
    for x in (22, 106):
        c.paint(ell(x, 82, 18, 24), col, shade=(3, 3, dk(col, 0.7)), hi=(-3, -3, lt(col, 0.4), 2))
        c.paint(ell(x, 82, 8, 13), (40, 40, 46), ow=2)
    if straw:
        c.line([(30, 96), (46, 116), (80, 118)], 7, OUT)
        c.line([(30, 96), (46, 116), (80, 118)], 4, (255, 110, 170))
        for k in range(3):
            c.line([(44 + k * 3, 110 + k * 2), (49 + k * 3, 116)], 1, (200, 60, 120))
        c.paint(ell(84, 118, 5, 5), (255, 110, 170), ow=2.5)


def paint_icon_dolly_headphones():
    icon("icon_dolly_headphones.png", -6, lambda c: headphones(c))


def paint_icon_crew_headset():
    icon("icon_crew_headset.png", -6, lambda c: headphones(c, straw=True))


def paint_icon_runner_disguise():
    def draw(c):
        headphones(c, straw=True)
        c.line(bez((40, 96), (64, 130), (88, 96)), 5, (40, 110, 220))
        c.paint(rrect(50, 100, 78, 126, 3), (250, 250, 252), ow=2.5, pattern=lambda p: p.rect(50, 100, 78, 108, (40, 110, 220)))
        c.text(64, 117, "KEV", 7, (40, 40, 60), "Black")
    icon("icon_runner_disguise.png", 0, draw)


def paint_icon_bendy_straw():
    def draw(c):
        c.line([(30, 120), (52, 40), (62, 30), (100, 14)], 16, OUT)
        c.line([(30, 120), (52, 40), (62, 30), (100, 14)], 10, (255, 250, 250))
        for k in range(6):
            y = 112 - k * 14
            x = 30 + (52 - 30) * (120 - y) / 80
            c.line([(x - 5, y), (x + 5, y - 3)], 3.5, (255, 110, 170))
        for k in range(4):
            c.line([(50 + k * 3, 42 - k * 3), (56 + k * 3, 46 - k * 3)], 1.4, (180, 180, 190))
    icon("icon_bendy_straw.png", 0, draw)


def paint_icon_studio_cheese_puff():
    def draw(c):
        puff = poly([(20, 70), (30, 46), (52, 38), (66, 50), (86, 36), (108, 52), (112, 78), (96, 96), (70, 90),
                     (48, 102), (26, 92)], 2, True)
        c.paint(puff, (255, 150, 40), shade=(4, 4, (220, 100, 20)), hi=(-3, -3, (255, 210, 120), 3),
                pattern=lambda p: [p.ell(30 + (k * 19) % 76, 50 + (k * 13) % 44, 2.4, 2.4, (255, 200, 90)) for k in range(14)])
    icon("icon_studio_cheese_puff.png", 10, draw)


def paint_icon_nibbles_on_loan():
    def draw(c):
        cup = poly([(26, 64), (102, 64), (92, 122), (36, 122)], 1)
        fur, fur_sh = (230, 170, 100), (190, 130, 70)
        c.paint(ell(64, 54, 30, 26), fur, shade=(3, 3, fur_sh), hi=(-3, -3, (250, 210, 160), 2))
        for ex in (44, 84):
            c.paint(ell(ex, 32, 9, 9), fur, shade=(2, 2, fur_sh), pattern=lambda p, ex=ex: p.ell(ex, 33, 5, 5, (255, 180, 190)))
        c.paint(ell(54, 50, 4.5, 5), (24, 16, 14), ow=0)
        c.paint(ell(74, 50, 4.5, 5), (24, 16, 14), ow=0)
        c.paint(ell(53, 48, 1.6, 1.6), (255, 255, 255), ow=0)
        c.paint(ell(73, 48, 1.6, 1.6), (255, 255, 255), ow=0)
        c.paint(ell(64, 60, 4, 3), (255, 140, 150), ow=1.6)
        for s in (-1, 1):
            c.line([(64 + s * 8, 62), (64 + s * 22, 58)], 1.2)
        c.paint(ell(92, 70, 9, 6, 20), (255, 150, 40), ow=2)  # his cheese puff
        c.paint(cup, (250, 250, 250), shade=(4, 0, (210, 214, 226)),
                pattern=lambda p: [p.rect(26 + k * 18, 64, 34 + k * 18, 122, (240, 90, 120)) for k in range(5)])
        c.text(64, 100, "ON LOAN", 9, (40, 40, 60), "Black")
    icon("icon_nibbles_on_loan.png", 0, draw)


def paint_icon_chet_cheat_tape():
    def draw(c):
        cassette(c, (40, 40, 48), (255, 140, 220), "CHET'S", "COMEBACKS", (90, 20, 70), glitter=True)
        star(c, 108, 30, 12, (255, 236, 90), ow=3)
    icon("icon_chet_cheat_tape.png", 8, draw)


def paint_icon_bun_pencil():
    def draw(c):
        c.paint(poly([(18, 112), (30, 96), (100, 26), (112, 38), (42, 108)], 1), (250, 200, 50), shade=(3, 3, (210, 150, 30)),
                hi=(-2, -2, (255, 236, 140), 2))
        c.paint(poly([(18, 112), (30, 96), (42, 108)], 1), (240, 210, 170), ow=3)
        c.paint(poly([(18, 112), (22, 106), (24, 110)], 1), (40, 40, 40), ow=0)
        c.paint(poly([(96, 30), (104, 22), (116, 34), (108, 42)], 1), (200, 204, 216), ow=3)
        c.paint(poly([(104, 22), (110, 16), (122, 28), (116, 34)], 1), (240, 130, 150), ow=3)
        c.line([(36, 98), (98, 36)], 1.4, (200, 140, 30))
    icon("icon_bun_pencil.png", 0, draw)



ASSETS = {"bg_tv_studio": paint_tv_studio, "hs_chet_studwell": paint_chet_studwell,
          "bg_tv_green_room": paint_tv_green_room, "bg_tv_control_booth": paint_tv_control_booth,
          "hs_gloria_puff": paint_gloria_puff, "hs_norma_fade": paint_norma_fade,
          "hs_reserved_sign": paint_reserved_sign, "hs_playback_deck": paint_playback_deck,
          "hs_empty_deck": paint_empty_deck,
          "icon_lapel_mic": paint_icon_lapel_mic, "icon_nine_volt": paint_icon_nine_volt,
          "icon_soda_water": paint_icon_soda_water, "icon_cocktail_napkin": paint_icon_cocktail_napkin,
          "icon_studio_walkie": paint_icon_studio_walkie,
          "icon_chet_mixtape": paint_icon_chet_mixtape, "icon_floor_fillers_tape": paint_icon_floor_fillers_tape,
          "icon_reserved_card": paint_icon_reserved_card, "icon_scandal_lipstick": paint_icon_scandal_lipstick,
          "icon_chet_protest_sign": paint_icon_chet_protest_sign, "icon_runner_lanyard": paint_icon_runner_lanyard,
          "icon_dolly_headphones": paint_icon_dolly_headphones, "icon_bendy_straw": paint_icon_bendy_straw,
          "icon_crew_headset": paint_icon_crew_headset, "icon_runner_disguise": paint_icon_runner_disguise,
          "icon_studio_cheese_puff": paint_icon_studio_cheese_puff, "icon_nibbles_on_loan": paint_icon_nibbles_on_loan,
          "icon_chet_cheat_tape": paint_icon_chet_cheat_tape, "icon_bun_pencil": paint_icon_bun_pencil}


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
