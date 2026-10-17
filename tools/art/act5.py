#!/usr/bin/env python3
"""
Big Night Out -- Act 5 (Uptown) art: street, art gallery, nightclub, Cafe Snoot, Velour backstage, Mimi, Jett Vex, Brutus,
Pierre, Vivian Quill, Anton, Mr. Pemberton, Grizz, items.

Original art, drawn entirely with the helpers in paint.py (same style: bold dark outlines, warm saturated
cel shading, big heads). Prop positions are read from Assets/_Project/World/act5.json so the painted props
sit exactly inside their click boxes.

Usage:  python3 tools/art/act5.py            # paint everything
        python3 tools/art/act5.py uptown mimi # only assets whose name contains these words
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, Canvas, W_BG, H_BG, WALL_Y, mix, dk, lt, ell, rect, rrect, poly, wonky, cap, bez,  # noqa: E402
                   eye, shoe_shape, light_pass, plank_floor, baseboard, door, poster, rot_pts, ell_pts, Sh,
                   string_lights, checker_floor, block_wall)

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "act5.json")


def boxes(room_id):
    """{hotspot name: (x0, y0, x1, y1)} in background pixels (y down), from act5.json."""
    data = json.load(open(WORLD))
    room = next(r for r in data["rooms"] if r["id"] == room_id)
    out = {}
    for h in room["hotspots"]:
        fx, fy = h["feet"]
        w, hh = h["size"]
        x0 = (fx - w / 2 + 9.6) * 100
        x1 = (fx + w / 2 + 9.6) * 100
        yb = (5.4 - fy) * 100
        out[h["name"]] = (x0, yb - hh * 100, x1, yb)
    return out


def feet_px(room_id, name):
    data = json.load(open(WORLD))
    room = next(r for r in data["rooms"] if r["id"] == room_id)
    h = next(h for h in room["hotspots"] if h["name"] == name)
    return (h["feet"][0] + 9.6) * 100, (5.4 - h["feet"][1]) * 100


def neon(c, pts, color, w=7, glow=True):
    """A bent neon tube: dark outline, coloured tube, white-hot core."""
    c.line(pts, w + 5, OUT)
    c.line(pts, w, color)
    c.line(pts, max(1.5, w * 0.35), lt(color, 0.75))


def neon_text(c, x, y, s, size, color, kind="Italic", angle=0):
    c.text(x, y, s, size, lt(color, 0.75), kind, stroke=size * 0.09, sc=color, angle=angle)


def sky(c, y1, seed=50):
    rng = random.Random(seed)
    c.paint(rect(0, 0, W_BG, y1), ("vy", 0, y1, (24, 20, 70), (120, 52, 128)), ow=0)
    for _ in range(90):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, y1 * 0.6)
        r = rng.choice([1.2, 1.6, 2.2])
        c.paint(ell(sx, sy, r, r), (255, 250, 220), ow=0, opacity=0.8)
    # distant skyline
    x = -20
    while x < W_BG:
        bw = rng.uniform(60, 140)
        top = y1 - rng.uniform(80, 260)
        col = (52, 36, 92)
        c.paint(rect(x, top, x + bw, y1 + 10), col, ow=0)
        if rng.random() < 0.3:
            c.paint(rect(x + bw * 0.45, top - 50, x + bw * 0.55, top), col, ow=0)
            c.paint(ell(x + bw * 0.5, top - 52, 3, 3), (255, 80, 80), ow=0)
        for wy in range(int(top) + 14, int(y1), 24):
            for wx in range(int(x) + 10, int(x + bw) - 10, 20):
                if rng.random() < 0.35:
                    c.paint(rect(wx, wy, wx + 8, wy + 11), (255, 206, 110), ow=0, opacity=0.8)
        x += bw + rng.uniform(4, 20)


def brick(c, x0, y0, x1, y1, base, seed=1, bw=64, bh=26):
    rng = random.Random(seed)

    def pat(p):
        y, row = y0, 0
        while y < y1:
            off = (bw / 2) * (row % 2)
            x = x0 - off
            while x < x1:
                col = mix(base, (40, 20, 30), rng.uniform(0, 0.18)) if rng.random() < 0.5 else \
                    mix(base, (255, 210, 170), rng.uniform(0, 0.12))
                p.rect(x + 2, y + 2, x + bw - 2, y + bh - 2, col)
                x += bw
            y += bh
            row += 1
    c.paint(rect(x0, y0, x1, y1), dk(base, 0.62), ow=0, pattern=pat)


def sidewalk(c, base, seed=9):
    """Paved sidewalk in perspective, curb and a strip of road at the front."""
    plank_floor(c, base, vp=(960, 200), step=190, seed=seed)
    rng = random.Random(seed)
    for _ in range(40):  # gum spots and cracks
        x, y = rng.uniform(0, W_BG), rng.uniform(820, 1020)
        c.paint(ell(x, y, rng.uniform(3, 7), rng.uniform(1.5, 3)), dk(base, 0.7), ow=0, opacity=0.35)
    c.paint(rect(-10, 1036, W_BG + 10, 1052), lt(base, 0.25), ow=3, shade=(0, -4, dk(base, 0.8)))
    c.paint(rect(-10, 1052, W_BG + 10, H_BG + 10), (52, 48, 64), ow=0)
    for x in range(40, W_BG, 220):
        c.paint(rect(x, 1066, x + 110, 1074), (240, 210, 90), ow=0, opacity=0.8)


# =========================================================================== uptown street
def paint_uptown():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    B = boxes("uptown")
    sky(c, 330)

    # ---------- left building: brick, with the shuttle stop in front
    brick(c, -10, 120, 270, WALL_Y, (150, 70, 60), seed=3)
    c.paint(rect(-10, 110, 280, 132), (90, 50, 50), ow=3, hi=(0, 4, (140, 90, 80)))
    for wy in (190, 330):
        c.paint(rect(40, wy, 120, wy + 100), ("v", (255, 214, 120), (230, 140, 70)), ow=3.5)
        c.paint(rect(150, wy, 230, wy + 100), (40, 34, 70), ow=3.5)
        c.paint(rect(30, wy + 100, 130, wy + 112), (200, 170, 140), ow=3)
        c.paint(rect(140, wy + 100, 240, wy + 112), (200, 170, 140), ow=3)
    x0, y0, x1, y1 = B["Campus shuttle"]
    # glass shelter
    c.paint(rect(x0 + 6, y0 + 110, x1 - 10, y1 - 6), (150, 210, 230, 110), ow=3.5)
    c.paint(rect(x0 - 2, y0 + 96, x1 - 2, y0 + 112), (60, 110, 160), ow=3.5, hi=(0, 3, (120, 170, 220)))
    c.paint(poly([(x0 + 16, y1 - 40), (x0 + 50, y0 + 130), (x0 + 66, y0 + 130), (x0 + 32, y1 - 40)]),
            (255, 255, 255), ow=0, opacity=0.25)
    # bench inside the shelter
    c.paint(rect(x0 + 14, y1 - 66, x1 - 18, y1 - 54), (240, 150, 50), ow=3)
    for lx in (x0 + 24, x1 - 28):
        c.paint(rect(lx - 3, y1 - 54, lx + 3, y1 - 8), (80, 80, 90), ow=2.5)
    # sign pole + sign
    px = x1 - 22
    c.paint(rect(px - 5, y0 - 10, px + 5, y1), (150, 150, 160), ow=3, hi=(-2, 0, (220, 220, 230)))
    c.paint(rrect(x0 + 4, y0 + 4, x1 + 6, y0 + 84, 8), (40, 110, 200), shade=(-4, -4), hi=(3, 3, (110, 170, 240), 2))
    c.text((x0 + x1) / 2 + 5, y0 + 26, "CAMPUS", 22, (255, 255, 240))
    c.text((x0 + x1) / 2 + 5, y0 + 52, "SHUTTLE", 17, (255, 230, 90))
    c.paint(poly([(x0 + 22, y0 + 70), (x0 + 40, y0 + 62), (x0 + 40, y0 + 78)]), (255, 255, 240), ow=0)
    c.paint(rect(x0 + 40, y0 + 67, x0 + 80, y0 + 73), (255, 255, 240), ow=0)

    # ---------- gallery facade
    gx0, gx1 = 270, 990
    stone = (236, 226, 204)

    def stone_lines(p):
        for y in range(150, WALL_Y, 64):
            p.line([(gx0, y), (gx1, y)], 1.6, dk(stone, 0.8))
            off = 90 if (y // 64) % 2 else 0
            for x in range(gx0 + off, gx1, 180):
                p.line([(x, y), (x, y + 64)], 1.6, dk(stone, 0.8))
    c.paint(rect(gx0, 120, gx1, WALL_Y), ("vy", 120, WALL_Y, lt(stone, 0.2), dk(stone, 0.86)), pattern=stone_lines)
    c.paint(rect(gx0 - 12, 104, gx1 + 12, 132), (210, 196, 170), shade=(0, -5, (170, 150, 130)))
    # upstairs windows
    for wx in (330, 520, 710, 870):
        c.paint(rect(wx, 170, wx + 90, 270), (36, 30, 66), ow=3.5)
        c.paint(rect(wx + 6, 176, wx + 84, 220), (255, 214, 140), ow=0, opacity=0.25)
        c.paint(rect(wx - 8, 270, wx + 98, 282), (210, 196, 170), ow=3)
    # name sign over the door
    x0, y0, x1, y1 = B["Gallery Pierre"]
    c.paint(rect(x0 - 70, 300, x1 + 70, 356), (30, 30, 34), shade=(0, -5, (10, 10, 14)))
    c.text((x0 + x1) / 2, 328, "GALLERY  PIERRE", 30, (240, 220, 160), "Display")
    # door: tall glass door with a brass handle, white glow from inside
    c.paint(rect(x0 - 16, y0 - 16, x1 + 16, y1 + 2), (60, 56, 60), shade=(-5, 0, (30, 28, 32)))
    c.paint(rect(x0, y0, x1, y1), ("v", (255, 252, 236), (226, 220, 200)), ow=3.5)
    c.paint(rect(x0 + 20, y0 + 60, x0 + 80, y0 + 140), (200, 60, 70), ow=2.5)  # art seen through glass
    c.paint(rect(x1 - 70, y0 + 80, x1 - 26, y0 + 130), (60, 120, 200), ow=2.5)
    c.paint(rect(x0 + 6, y1 - 60, x1 - 6, y1), (200, 190, 170), ow=0, opacity=0.5)
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 4)
    c.paint(poly([(x0 + 14, y1 - 40), (x0 + 60, y0 + 20), (x0 + 76, y0 + 20), (x0 + 30, y1 - 40)]),
            (255, 255, 255), ow=0, opacity=0.35)
    for hx in ((x0 + x1) / 2 - 14, (x0 + x1) / 2 + 14):
        c.paint(rrect(hx - 4, y0 + 130, hx + 4, y0 + 200, 3), (230, 186, 80), ow=2.5, hi=(-1, 0, (255, 240, 180)))
    c.text((x0 + x1) / 2, y0 + 250, "OPENING TONIGHT", 10, (60, 60, 70), "Bold")
    # big display window right of the door (dark-ish so the mime reads in front of it)
    wx0, wx1 = x1 + 50, gx1 - 30
    c.paint(rect(wx0 - 14, 430, wx1 + 14, 760), (60, 56, 60))

    def window_in(p):
        p.rect(wx0, 444, wx1, 746, (70, 64, 96))
        p.rect(wx0, 640, wx1, 746, (96, 86, 110))
        p.rect(wx0 + 40, 490, wx0 + 140, 600, (240, 236, 220))
        p.rect(wx0 + 46, 496, wx0 + 134, 594, (255, 255, 250))
        p.rect(wx1 - 90, 520, wx1 - 30, 640, (230, 226, 210))
    c.paint(rect(wx0, 444, wx1, 746), (70, 64, 96), ow=3.5, pattern=window_in)
    c.paint(poly([(wx0 + 10, 730), (wx0 + 120, 450), (wx0 + 150, 450), (wx0 + 40, 730)]), (255, 255, 255), ow=0,
            opacity=0.12)
    # awnings
    for ax0, ax1 in ((x0 - 30, x1 + 30), (wx0 - 20, wx1 + 20)):
        pts = [(ax0, 380), (ax1, 380), (ax1 + 16, 424), (ax0 - 16, 424)]

        def stripes(p, ax0=ax0, ax1=ax1):
            for sx in range(int(ax0) - 20, int(ax1) + 20, 40):
                p.poly([(sx, 380), (sx + 20, 380), (sx + 22, 424), (sx + 2, 424)], (250, 246, 236))
        c.paint(poly(pts), (30, 30, 34), pattern=stripes, shade=(0, -5))
        for sx in range(int(ax0 - 16), int(ax1 + 16), 24):
            c.paint(ell(sx + 12, 424, 12, 7), (30, 30, 34), ow=2.5)
    # potted topiary by the door
    for tx in (x0 - 50,):
        c.paint(poly([(tx - 24, 790), (tx + 24, 790), (tx + 30, 740), (tx - 30, 740)]), (40, 40, 44), ow=3.5)
        c.line([(tx, 740), (tx, 690)], 4, (90, 60, 40))
        c.paint(ell(tx, 660, 36, 40), (60, 150, 70), shade=(4, 4, (40, 110, 60)), hi=(-4, -4, (120, 200, 110), 3))

    # ---------- poster wall (brick) between gallery and club
    brick(c, gx1, 120, 1200, WALL_Y, (120, 64, 70), seed=5)
    c.paint(rect(gx1 - 4, 104, 1204, 132), (80, 46, 54), ow=3)
    x0, y0, x1, y1 = B["Jett Vex poster"]

    def jett_poster(p, ox, oy):
        w, h = x1 - x0, y1 - y0
        p.rect(ox, oy, ox + w, oy + h, (30, 24, 34))
        for k in range(9):
            a = math.radians(k * 40)
            p.poly([(ox + w / 2, oy + h * 0.55), (ox + w / 2 + 200 * math.cos(a), oy + h * 0.55 + 200 * math.sin(a)),
                    (ox + w / 2 + 200 * math.cos(a + 0.3), oy + h * 0.55 + 200 * math.sin(a + 0.3))], (230, 40, 130))
        # yawning rocker silhouette
        cx, cy = ox + w / 2, oy + h * 0.6
        p.poly([(cx - 34, oy + h), (cx - 24, cy + 20), (cx + 24, cy + 20), (cx + 34, oy + h)], (20, 16, 24))
        p.ell(cx, cy, 24, 26, (250, 214, 180))
        for k in range(6):
            p.poly([(cx - 22 + k * 9, cy - 16), (cx - 18 + k * 9, cy - 48 - (k % 2) * 10), (cx - 12 + k * 9, cy - 18)],
                   (80, 230, 110))
        p.ell(cx - 4, cy + 10, 7, 9, (60, 10, 30))
        p.line([(cx - 14, cy - 4), (cx - 6, cy - 2)], 2.5, OUT)
        p.line([(cx + 4, cy - 2), (cx + 12, cy - 4)], 2.5, OUT)
    pp = poster(int(x1 - x0), int(y1 - y0), (30, 24, 34), jett_poster)
    pp.text(20 + (x1 - x0) / 2, 44, "JETT VEX", 16, (120, 255, 140), "Italic", stroke=2.5)
    pp.text(20 + (x1 - x0) / 2, 66, "LIVE @ VELOUR", 10, (255, 255, 255), "Black")
    pp.text(20 + (x1 - x0) / 2, 20 + (y1 - y0) - 12, "BORED OUT OF MY SKULL TOUR", 6.5, (255, 230, 90), "Black")
    c.stamp(pp, (x0 + x1) / 2, (y0 + y1) / 2, angle=-3)
    # torn old flyers around it
    rng = random.Random(8)
    for fx, fy, fc in ((x0 - 20, y1 + 50, (255, 230, 120)), (x1 + 10, y0 + 30, (150, 220, 255)),
                       (x1 - 30, y1 + 90, (255, 170, 200))):
        c.paint(wonky(fx - 26, fy - 34, fx + 26, fy + 34, 3, rng), fc, ow=3)
        for k in range(3):
            c.line([(fx - 16, fy - 14 + k * 12), (fx + 14, fy - 14 + k * 12)], 2, dk(fc, 0.6))

    # ---------- club facade
    cx0 = 1200
    club = (70, 26, 86)

    def tiles(p):
        for y in range(120, WALL_Y, 40):
            p.line([(cx0, y), (W_BG, y)], 2, dk(club, 0.7))
        for x in range(cx0, W_BG, 40):
            p.line([(x, 120), (x, WALL_Y)], 1.2, lt(club, 0.12))
    c.paint(rect(cx0, 120, W_BG + 10, WALL_Y), ("vy", 120, WALL_Y, dk(club, 0.8), club), pattern=tiles)
    c.paint(rect(cx0 - 6, 104, W_BG + 10, 132), (40, 14, 50), ow=3)
    # big neon sign
    neon_text(c, 1560, 210, "Club", 52, (255, 90, 200), "Italic", angle=6)
    neon_text(c, 1600, 290, "VELOUR", 72, (90, 220, 255), "Display", angle=6)
    neon(c, [(1340, 372), (1880, 336)], (255, 90, 200), 5)
    # marquee around the door
    x0, y0, x1, y1 = B["Club Velour"]
    c.paint(rect(x0 - 30, y0 - 50, x1 + 30, y1 + 2), (230, 186, 80), shade=(-5, 0, (180, 130, 50)))
    for k in range(14):
        bx = x0 - 18 + k * (x1 - x0 + 36) / 13
        c.paint(ell(bx, y0 - 34, 7, 7), (255, 246, 190), ow=2.5)
    for k in range(9):
        by = y0 - 10 + k * (y1 - y0) / 9
        c.paint(ell(x0 - 18, by, 6, 6), (255, 246, 190), ow=2.5)
        c.paint(ell(x1 + 18, by, 6, 6), (255, 246, 190), ow=2.5)
    vel = (150, 30, 90)

    def tufts(p):
        for ty in range(int(y0) + 24, int(y1) - 10, 44):
            for tx in range(int(x0) + 22, int(x1) - 10, 44):
                o = 22 if ((ty - int(y0)) // 44) % 2 else 0
                p.ell(tx + o, ty, 4, 4, dk(vel, 0.6))
                p.ell(tx + o - 1, ty - 1, 2, 2, (255, 210, 120))
    c.paint(rect(x0, y0, x1, y1), ("v", lt(vel, 0.1), dk(vel, 0.8)), ow=3.5, pattern=tufts)
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 3.5)
    for hx in ((x0 + x1) / 2 - 16, (x0 + x1) / 2 + 16):
        c.paint(ell(hx, (y0 + y1) / 2 + 20, 9, 9), (240, 196, 80), ow=3, hi=(-2, -2, (255, 245, 190)))
    # velvet rope + brass stanchions between the door and Brutus
    sx = [x1 + 50, B["Brutus"][2] + 60]
    for s in sx:
        c.shadow(s, 792, 18, 4)
        c.paint(ell(s, 790, 16, 5), (200, 156, 60), ow=3)
        c.paint(rect(s - 4, 700, s + 4, 790), (230, 186, 80), ow=3, hi=(-2, 0, (255, 240, 180)))
        c.paint(ell(s, 698, 9, 9), (240, 200, 90), ow=3, hi=(-2, -2, (255, 245, 190)))
    c.paint(cap(bez((sx[0], 712), ((sx[0] + sx[1]) / 2, 760), (sx[1], 712)), 11), (200, 30, 70), ow=3,
            shade=(0, -3, (140, 20, 60)))
    # far-right: the archway to Cafe Snoot (a warm-lit lane with string lights)
    cafe_arch(c, *B["Cafe Snoot"])

    # ---------- street lamp
    lx = 1000
    c.shadow(lx, 794, 30, 5)
    c.paint(rect(lx - 18, 760, lx + 18, 792), (40, 44, 52), ow=3.5)
    c.paint(rect(lx - 7, 300, lx + 7, 762), (50, 56, 66), ow=3.5, hi=(-3, 0, (100, 110, 130)))
    c.paint(poly([(lx - 30, 300), (lx + 30, 300), (lx + 20, 250), (lx - 20, 250)]), (255, 230, 150), ow=3.5)
    c.paint(poly([(lx - 36, 300), (lx + 36, 300), (lx + 28, 312), (lx - 28, 312)]), (50, 56, 66), ow=3)
    c.paint(poly([(lx - 26, 250), (lx + 26, 250), (lx, 222)]), (50, 56, 66), ow=3)

    # ---------- sidewalk
    sidewalk(c, (150, 140, 156))
    # Mimi's chalk box and her beret of coins
    mx, my = feet_px("uptown", "Mimi")
    chalk = [(mx - 80, my + 22), (mx + 70, my + 22), (mx + 60, my - 22), (mx - 70, my - 22)]
    c.line(chalk + [chalk[0]], 3.5, (250, 250, 240), opacity=0.8)
    c.text(mx - 4, my + 46, "THE BOX", 11, (250, 250, 240), "Bold")
    bx, by = mx + 120, my + 34
    c.shadow(bx, by + 6, 34, 6)
    c.paint(ell(bx, by, 30, 11), (30, 26, 34), hi=(0, -2, (80, 70, 90)))
    for k in range(4):
        c.paint(ell(bx - 12 + k * 8, by - 3 + (k % 2) * 2, 5, 2.5), (240, 200, 80), ow=1.6)

    # ---------- night lighting
    lights = [(lx, 290, 520, 0.6, (255, 200, 120)), (1600, 260, 520, 0.5, (240, 110, 255)),
              (B["Club Velour"][0] + 90, 560, 300, 0.4, (255, 200, 120)), (560, 560, 360, 0.45, (255, 246, 220)),
              (100, 560, 260, 0.3, (140, 200, 255)), (900, 900, 500, 0.15, (255, 220, 200))]
    light_pass(c, 0.7, lights, vign=0.4, front=0.25)
    c.glow(lx, 280, 140, (255, 210, 140), 0.55)
    c.glow(1560, 240, 260, (255, 90, 200), 0.25)
    c.glow(1600, 290, 220, (90, 220, 255), 0.18)
    c.glow(B["Club Velour"][0] + 90, 500, 160, (255, 220, 150), 0.2)
    c.save("bg_uptown.png")


# =========================================================================== art gallery
def framed(c, x0, y0, x1, y1, frame, art_fn, mat=None):
    c.paint(rect(x0, y0, x1, y1), frame, shade=(-5, -5, dk(frame, 0.7)), hi=(3, 3, lt(frame, 0.4), 2))
    m = 12
    if mat:
        c.paint(rect(x0 + m, y0 + m, x1 - m, y1 - m), mat, ow=2.5)
        m += 18
    c.paint(rect(x0 + m, y0 + m, x1 - m, y1 - m), (250, 250, 246), ow=2.5,
            pattern=lambda p: art_fn(p, x0 + m, y0 + m, x1 - m, y1 - m))


def spot_cone(c, x, y_top, y_bot, w0, w1, opacity=0.10):
    c.paint(poly([(x - w0, y_top), (x + w0, y_top), (x + w1, y_bot), (x - w1, y_bot)]), (255, 248, 220), ow=0,
            opacity=opacity)


def paint_art_gallery():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    B = boxes("art_gallery")
    wall = (250, 238, 214)
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, (222, 206, 186), wall), ow=0)
    # ceiling + track lighting rail
    c.paint(rect(0, 0, W_BG, 70), (210, 202, 192), ow=0)
    c.paint(rect(-10, 64, W_BG + 10, 80), (250, 246, 236), ow=3, shade=(0, -4, (210, 200, 186)))
    c.paint(rect(-10, 100, W_BG + 10, 110), (40, 40, 44), ow=2.5)
    spots = [220, 520, (B["Blank canvas"][0] + B["Blank canvas"][2]) / 2, (B["Plinth"][0] + B["Plinth"][2]) / 2,
             1640]
    for sx in spots:
        c.line([(sx, 110), (sx, 128)], 3)
        c.paint(poly(rot_pts([(sx - 14, 124), (sx + 14, 124), (sx + 10, 168), (sx - 10, 168)], 10, sx, 130), 1),
                (40, 40, 44), hi=(-2, 0, (110, 110, 120)))
        c.paint(ell(sx + 4, 168, 10, 4, 10), (255, 250, 210), ow=2)
    # opening-night banner
    c.paint(poly([(950, 120), (1390, 120), (1372, 196), (968, 196)], 1), (200, 40, 60), shade=(0, -5, (150, 24, 50)),
            hi=(0, 4, (240, 100, 110), 2))
    c.text(1170, 144, "OPENING NIGHT", 22, (255, 240, 200), "Black")
    c.text(1170, 176, "NOTHING: A RETROSPECTIVE", 14, (255, 220, 120), "Bold")
    plank_floor(c, (196, 146, 96), vp=(960, 300), step=120, seed=41)
    c.paint(ell(960, 930, 700, 90), (255, 255, 255), ow=0, opacity=0.08)
    baseboard(c, color=(236, 230, 218))

    # ---------- exit doorway with a night-street peek
    x0, y0, x1, y1 = B["Exit"]
    c.paint(rect(x0 - 14, y0 - 14, x1 + 14, y1 + 2), (40, 40, 44), shade=(-4, 0, (20, 20, 24)))

    def street(p):
        p.rect(x0, y0, x1, y1, (40, 34, 80))
        p.rect(x0, y0 + 160, x1, y1, (120, 110, 130))
        p.rect(x0 + 20, y0 + 40, x0 + 60, y0 + 150, (90, 40, 110))
        p.ell(x0 + 110, y0 + 60, 16, 16, (255, 220, 140))
        p.rect(x0 + 106, y0 + 70, x0 + 114, y0 + 170, (50, 56, 66))
    c.paint(rect(x0, y0, x1, y1), (40, 34, 80), ow=3.5, pattern=street)
    c.paint(rrect(x0 + 20, y0 - 70, x1 - 20, y0 - 30, 6), (40, 160, 90), shade=(-3, -3), hi=(3, 3, (110, 220, 150), 2))
    c.text((x0 + x1) / 2, y0 - 50, "EXIT", 20, (255, 255, 240))

    # ---------- small wall pieces (decor)
    def dot_art(p, a, b, c_, d):
        p.ell((a + c_) / 2, (b + d) / 2, 16, 16, (230, 50, 60))
    framed(c, 240, 260, 380, 420, (30, 30, 34), dot_art)
    c.paint(rect(286, 436, 334, 452), (255, 255, 250), ow=2)

    def squares(p, a, b, c_, d):
        p.rect(a, b, c_, d, (40, 100, 200))
        p.rect(a + 22, b + 22, c_ - 22, d - 22, (250, 200, 50))
        p.rect(a + 46, b + 46, c_ - 46, d - 46, (230, 60, 90))
    framed(c, 1360, 250, 1520, 410, (200, 160, 70), squares)
    c.paint(rect(1416, 426, 1464, 442), (255, 255, 250), ow=2)

    def squiggle(p, a, b, c_, d):
        p.rect(a, b, c_, d, (255, 236, 200))
        for k in range(5):
            p.line(bez((a + 10, b + 30 + k * 34), ((a + c_) / 2, b - 20 + k * 40), (c_ - 10, b + 40 + k * 30)), 6,
                   [(230, 80, 60), (60, 150, 90), (60, 90, 200), (250, 180, 40), (150, 60, 160)][k])
    framed(c, 1580, 200, 1800, 430, (30, 30, 34), squiggle, mat=(250, 250, 246))
    c.paint(rect(1666, 442, 1714, 456), (255, 255, 250), ow=2)

    # ---------- canvas spot: picture hooks, spotlight pool and the title card (canvas is a sprite)
    x0, y0, x1, y1 = B["Blank canvas"]
    cxm = (x0 + x1) / 2
    c.paint(ell(cxm, (y0 + y1) / 2, (x1 - x0) * 0.75, (y1 - y0) * 0.72), (255, 250, 220), ow=0, opacity=0.25)
    c.line([(cxm - 60, 110), (x0 + 40, y0 + 4)], 1.4, (120, 120, 130))
    c.line([(cxm + 60, 110), (x1 - 40, y0 + 4)], 1.4, (120, 120, 130))
    c.paint(rect(cxm - 70, y1 + 18, cxm + 70, y1 + 58), (255, 255, 252), ow=2.5, shade=(-2, -2, (220, 216, 206)))
    c.text(cxm, y1 + 31, "NOTHING No. 5", 11, (40, 40, 44), "Black")
    c.text(cxm, y1 + 47, "PRICELESS", 9, (200, 40, 50), "Black")

    # ---------- sculpture: bronze man checking his phone, on a low plinth
    x0, y0, x1, y1 = B["Sculpture"]
    sx = (x0 + x1) / 2
    c.shadow(sx, y1 - 2, 60, 8)
    c.paint(rect(x0 + 6, y1 - 60, x1 - 6, y1), (250, 248, 242), shade=(-6, 0, (214, 208, 198)))
    br, br_sh, br_hi = (190, 120, 60), (130, 76, 40), (240, 180, 110)
    base = y1 - 60
    c.paint(cap([(sx - 10, base), (sx - 8, base - 50)], 16) + cap([(sx + 12, base), (sx + 10, base - 50)], 16), br,
            shade=(-3, 0, br_sh))
    c.paint(poly([(sx - 24, base - 46), (sx + 26, base - 46), (sx + 22, base - 110), (sx - 22, base - 112)], 2), br,
            shade=(-4, 0, br_sh), hi=(3, 3, br_hi, 2))
    c.paint(cap([(sx - 18, base - 104), (sx - 20, base - 70), (sx - 4, base - 66)], 10), br, shade=(-3, 0, br_sh))
    c.paint(cap([(sx + 18, base - 104), (sx + 10, base - 74), (sx - 2, base - 70)], 10), br, shade=(-3, 0, br_sh))
    c.paint(rect(sx - 10, base - 80, sx + 4, base - 62), (60, 60, 70), ow=2.5)
    c.paint(ell(sx - 4, base - 128, 18, 20), br, shade=(-3, 2, br_sh), hi=(3, 3, br_hi, 2))
    c.line([(sx - 14, base - 124), (sx - 8, base - 122)], 2)
    c.line([(sx - 4, base - 123), (sx + 2, base - 124)], 2)
    c.paint(rect(sx - 26, y1 - 34, sx + 26, y1 - 18), (255, 255, 252), ow=2)

    # ---------- plinth with the invisible key
    x0, y0, x1, y1 = B["Plinth"]
    pxm = (x0 + x1) / 2
    spot_cone(c, pxm + 10, 200, y0 + 10, 14, 70, 0.22)
    c.shadow(pxm, y1 - 2, 56, 8)
    c.paint(rect(x0 + 10, y0 + 22, x1 - 10, y1), ("h", (255, 255, 252), (214, 210, 200)), shade=(-6, 0, (200, 194, 184)))
    c.paint(rect(x0 + 2, y0 + 8, x1 - 2, y0 + 24), (255, 255, 252), ow=3.5, shade=(0, -4, (214, 208, 198)))
    c.paint(rect(pxm - 30, y0 + 70, pxm + 30, y0 + 102), (255, 255, 252), ow=2, shade=(-2, -2, (220, 216, 206)))
    c.text(pxm, y0 + 81, "UNTITLED", 7.5, (40, 40, 44), "Black")
    c.text(pxm, y0 + 93, "(KEY)", 7.5, (200, 40, 50), "Black")
    # a faint glint where the key "is"
    for gx, gy, r in ((pxm - 6, y0 - 6, 6), (pxm + 14, y0 - 16, 3.5)):
        c.paint(poly([(gx, gy - r * 2), (gx + r * 0.4, gy - r * 0.4), (gx + r * 2, gy), (gx + r * 0.4, gy + r * 0.4),
                      (gx, gy + r * 2), (gx - r * 0.4, gy + r * 0.4), (gx - r * 2, gy), (gx - r * 0.4, gy - r * 0.4)]),
                (255, 255, 230), ow=0, opacity=0.8)

    # ---------- art supply cart
    x0, y0, x1, y1 = B["Art supplies"]
    wood, wood_sh = (200, 140, 80), (150, 96, 56)
    c.shadow((x0 + x1) / 2, y1 - 2, (x1 - x0) / 2 + 10, 9)
    # sign on a stick
    c.paint(rect(x1 - 30, y0 - 120, x1 - 22, y0 + 40), wood_sh, ow=3)
    c.paint(wonky(x1 - 120, y0 - 170, x1 + 10, y0 - 90, 2, random.Random(4)), (255, 240, 120), shade=(-3, -3))
    c.text(x1 - 55, y0 - 150, "FREE PAINT!", 13, (200, 40, 50))
    c.text(x1 - 55, y0 - 128, "Take some.", 10, (40, 40, 44), "Bold")
    c.text(x1 - 55, y0 - 110, "MAKE SOMETHING", 9.5, (40, 90, 200), "Black")
    # cart body
    c.paint(wonky(x0 + 4, y0 + 60, x1 - 4, y1 - 30, 1.5, random.Random(6)), wood, shade=(-6, 0, wood_sh),
            hi=(0, 4, lt(wood, 0.3)))
    c.paint(rect(x0 + 18, y0 + 76, x1 - 18, y1 - 44), dk(wood, 0.8), ow=3)
    for k, col in enumerate([(230, 50, 120), (60, 200, 90), (40, 40, 50), (250, 200, 40), (60, 120, 230)]):
        tx = x0 + 34 + k * 30
        c.paint(rrect(tx, y0 + 84, tx + 22, y0 + 112, 4), col, ow=2.5, hi=(-2, 0, lt(col, 0.4)))
    for wx in (x0 + 30, x1 - 30):
        c.paint(ell(wx, y1 - 16, 15, 15), (60, 60, 66), hi=(-2, -2, (130, 130, 140)))
        c.paint(ell(wx, y1 - 16, 5, 5), (180, 180, 190), ow=2)
    # jars of brushes + paint pots on top
    jar = (190, 220, 230)
    for jx, cols in ((x0 + 40, [(230, 60, 60), (60, 160, 230), (250, 200, 40)]),
                     (x0 + 92, [(120, 200, 80), (200, 80, 200)])):
        for k, bc in enumerate(cols):
            ang = -18 + k * 16
            ex = jx + 30 * math.sin(math.radians(ang))
            c.line([(jx, y0 + 50), (ex, y0 + 4 - k * 4)], 4.5, (170, 110, 60))
            c.paint(ell(ex, y0 + 2 - k * 4, 5, 9, ang), bc, ow=2.5)
        c.paint(rrect(jx - 18, y0 + 26, jx + 18, y0 + 64, 4), jar, ow=3, hi=(-3, 0, (240, 250, 255)))
    for k, (px_, col) in enumerate(((x0 + 140, (230, 50, 120)), (x0 + 170, (60, 200, 90)))):
        c.paint(rrect(px_ - 14, y0 + 40, px_ + 14, y0 + 64, 4), (240, 240, 236), ow=3)
        c.paint(ell(px_, y0 + 40, 14, 5), col, ow=2.5)
        c.paint(cap([(px_ + 10, y0 + 42), (px_ + 14, y0 + 56)], 5), col, ow=0)

    # ---------- wine & cheese table against the wall (opening night)
    tx0, tx1 = 560, 700
    c.shadow((tx0 + tx1) / 2, 794, 80, 6)
    c.paint(rect(tx0, 700, tx1, 712), (250, 250, 246), ow=3)
    c.paint(poly([(tx0 + 4, 712), (tx1 - 4, 712), (tx1 - 2, 790), (tx0 + 2, 790)]), (250, 250, 246), ow=3,
            shade=(-5, 0, (214, 210, 200)))
    for gx in (tx0 + 26, tx0 + 52):
        c.paint(poly([(gx - 8, 668), (gx + 8, 668), (gx + 4, 686), (gx - 4, 686)]), (240, 220, 160, 200), ow=2.5)
        c.line([(gx, 686), (gx, 698)], 2.5)
        c.paint(ell(gx, 699, 7, 2.5), (230, 230, 230), ow=2)
    c.paint(ell(tx1 - 40, 694, 30, 7), (240, 240, 240), ow=2.5)
    c.paint(poly([(tx1 - 58, 692), (tx1 - 34, 678), (tx1 - 24, 692)]), (255, 220, 90), ow=2.5)
    c.paint(rect(tx1 - 30, 682, tx1 - 16, 692), (255, 200, 70), ow=2.5)

    lights = [(sx, 400, 360, 0.25, (255, 246, 210)) for sx in spots]
    light_pass(c, 0.92, lights, vign=0.32, front=0.18)
    c.save("bg_art_gallery.png")


# =========================================================================== nightclub
def paint_nightclub():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    B = boxes("nightclub")
    rng = random.Random(55)
    wall = (60, 24, 84)

    def panels(p):
        for x in range(0, W_BG, 120):
            p.rect(x + 6, 150, x + 114, WALL_Y - 10, dk(wall, 0.85))
            p.line([(x + 8, 152), (x + 112, 152)], 2, lt(wall, 0.2))
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, (24, 10, 40), wall), ow=0, pattern=panels)
    c.paint(rect(0, 0, W_BG, 120), (18, 8, 30), ow=0)
    # lighting truss
    c.paint(rect(-10, 112, W_BG + 10, 126), (90, 90, 100), ow=3)
    for x in range(0, W_BG, 30):
        c.line([(x, 114), (x + 15, 124)], 1.5, (50, 50, 60))
    for k, (lx, col) in enumerate(((300, (255, 80, 200)), (1150, (80, 220, 255)), (1500, (255, 220, 80)),
                                   (1780, (120, 255, 140)))):
        c.paint(rrect(lx - 16, 126, lx + 16, 160, 5), (40, 40, 50), ow=3)
        c.paint(ell(lx, 162, 12, 5), col, ow=2.5)
    # neon wave stripes along the wall
    for y, col in ((200, (255, 80, 200)), (226, (80, 220, 255))):
        pts = [(x, y + 10 * math.sin(x / 80)) for x in range(-20, W_BG + 30, 20)]
        neon(c, pts, col, 5)

    # ---------- dance floor: light-up tiles
    tile_cols = [(255, 80, 200), (80, 220, 255), (255, 220, 80), (120, 255, 140), (150, 90, 255), (40, 20, 60)]
    vp = (960, 240)
    ys = [WALL_Y + (H_BG - WALL_Y) * ((i / 6) ** 1.4) for i in range(7)]
    xs = list(range(-2400, W_BG + 2400, 150))

    def X(xb, y):
        return vp[0] + (xb - vp[0]) * (y - vp[1]) / (H_BG - vp[1])
    for r in range(6):
        for k in range(len(xs) - 1):
            ya, yb = ys[r], ys[r + 1]
            q = [(X(xs[k], ya), ya), (X(xs[k + 1], ya), ya), (X(xs[k + 1], yb), yb), (X(xs[k], yb), yb)]
            if q[1][0] < -60 or q[0][0] > W_BG + 60:
                if q[2][0] < -60 or q[3][0] > W_BG + 60:
                    continue
            col = tile_cols[rng.randrange(len(tile_cols))] if rng.random() < 0.55 else (40, 20, 60)
            c.paint(poly(q), mix(col, (30, 14, 44), 0.35), ow=0)
    for y in ys:
        c.line([(0, y), (W_BG, y)], 3, (20, 8, 30))
    for xb in xs:
        c.line([(X(xb, WALL_Y), WALL_Y), (X(xb, H_BG), H_BG)], 3, (20, 8, 30))
    c.paint(rect(-10, WALL_Y - 14, W_BG + 10, WALL_Y + 4), (30, 12, 44), ow=3)

    # ---------- exit door with neon sign
    x0, y0, x1, y1 = B["Exit"]
    c.paint(rect(x0 - 12, y0 - 12, x1 + 12, y1 + 2), (30, 14, 40))
    c.paint(rect(x0, y0, x1, y1), ("v", (70, 60, 80), (40, 34, 50)), ow=3.5)
    c.paint(rect(x0 + 16, y0 + 150, x1 - 16, y0 + 168), (150, 150, 160), ow=3, hi=(0, -2, (220, 220, 230)))
    c.paint(rrect(x0 + 18, y0 - 76, x1 - 18, y0 - 30, 6), (20, 30, 24))
    neon_text(c, (x0 + x1) / 2, y0 - 53, "EXIT", 26, (90, 255, 140), "Display")

    # ---------- bar: back shelf with bottles, counter with neon trim, stools
    x0, y0, x1, y1 = B["Bar"]
    c.paint(rect(x0 - 10, 380, x1 + 10, y0 - 10), (40, 18, 54), ow=3.5)
    for sy in (450, 540):
        c.paint(rect(x0, sy, x1, sy + 10), (120, 70, 50), ow=3, hi=(0, -2, (170, 110, 80)))
        bx = x0 + 14
        while bx < x1 - 20:
            col = rng.choice([(80, 200, 120), (230, 80, 160), (250, 190, 60), (90, 160, 240), (240, 240, 230)])
            h = rng.uniform(44, 66)
            c.paint(poly([(bx, sy), (bx + 18, sy), (bx + 18, sy - h * 0.6), (bx + 13, sy - h * 0.75), (bx + 13, sy - h),
                          (bx + 5, sy - h), (bx + 5, sy - h * 0.75), (bx, sy - h * 0.6)], 1), col, ow=2.5,
                    hi=(-2, 0, lt(col, 0.5)))
            bx += rng.uniform(26, 34)
    neon_text(c, (x0 + x1) / 2, 346, "COCKTAILS", 30, (255, 90, 200), "Italic")
    c.paint(rect(x0 - 12, y0 + 6, x1 + 12, y0 + 26), (170, 110, 80), shade=(0, -4, (120, 70, 50)),
            hi=(0, 4, (220, 160, 110)))
    c.paint(rect(x0, y0 + 26, x1, y1), ("v", (110, 40, 90), (60, 20, 60)), ow=3.5,
            pattern=lambda p: [p.rect(xx, y0 + 30, xx + 6, y1, (140, 60, 110)) for xx in range(int(x0) + 20, int(x1), 40)])
    neon(c, [(x0 + 4, y0 + 40), (x1 - 4, y0 + 40)], (80, 220, 255), 4)
    for k, gx in enumerate((x0 + 60, x0 + 200)):
        col = [(255, 120, 200), (120, 255, 160)][k]
        c.paint(poly([(gx - 12, y0 - 26), (gx + 12, y0 - 26), (gx, y0 - 8)]), col, ow=2.5)
        c.line([(gx, y0 - 8), (gx, y0 + 4)], 2.5)
        c.paint(ell(gx, y0 + 5, 8, 2.5), (220, 220, 230), ow=2)
    c.paint(ell(x0 + 70, y0 - 28, 4, 4), (255, 60, 60), ow=1.6)  # cherry
    for sx in (x0 + 50, x0 + 170, x0 + 290):
        c.paint(ell(sx, y1 - 52, 26, 8), (230, 60, 140), ow=3, hi=(0, -2, (255, 140, 200)))
        c.paint(rect(sx - 4, y1 - 46, sx + 4, y1 - 4), (180, 180, 190), ow=2.5)
        c.paint(ell(sx, y1 - 4, 16, 4), (180, 180, 190), ow=2.5)

    # ---------- stage with curtains and the Finals banner
    x0, y0, x1, y1 = B["Stage"]
    cx = (x0 + x1) / 2
    cur = (200, 30, 70)
    c.paint(rect(x0 - 20, 250, x1 + 20, y0), (24, 10, 34), ow=3.5)
    c.paint(ell(cx, y0 - 140, 220, 160), (255, 220, 255), ow=0, opacity=0.12)
    for side in (-1, 1):
        ex = x0 - 50 if side < 0 else x1 + 50
        ix = x0 + 60 if side < 0 else x1 - 60
        pts = [(ex, 240), (ix, 240), (ix + side * -10, 420), (ix + side * 30, y0), (ex, y0)]

        def folds(p, ex=ex, ix=ix):
            for k in range(1, 5):
                fx = ex + (ix - ex) * k / 5
                p.line([(fx, 244), (fx, y0)], 4, dk(cur, 0.65))
                p.line([(fx + 8, 244), (fx + 8, y0)], 2.5, lt(cur, 0.25))
        c.paint(poly(pts), cur, pattern=folds)
        c.paint(ell(ix + side * 12, 420, 14, 9), (240, 196, 80), ow=3)
    c.paint(poly([(x0 - 60, 230), (x1 + 60, 230), (x1 + 60, 270), (x0 - 60, 270)]), cur, shade=(0, -6),
            pattern=lambda p: [p.ell(xx, 270, 22, 12, cur) for xx in range(int(x0) - 50, int(x1) + 60, 44)])
    c.paint(rrect(cx - 190, 284, cx + 190, 370, 12), (250, 220, 60), shade=(-4, -4, (210, 160, 40)),
            hi=(3, 3, (255, 250, 170), 2))
    c.text(cx, 310, "SPEED DATERS LIVE", 28, (200, 30, 70), "Italic")
    c.text(cx, 348, "THE  FINALS", 26, (60, 20, 90), "Black")
    for k in range(10):
        c.paint(ell(cx - 180 + k * 40, 284, 6, 6), (255, 250, 220), ow=2)
    # the platform itself
    c.paint(rect(x0 - 20, y0, x1 + 20, y0 + 16), (230, 186, 80), ow=3.5, hi=(0, 3, (255, 236, 150)))
    c.paint(rect(x0 - 16, y0 + 16, x1 + 16, y1), ("v", (90, 40, 110), (50, 20, 70)), ow=3.5,
            pattern=lambda p: [p.ell(xx, (y0 + y1) / 2 + 8, 5, 5, (255, 240, 180)) for xx in range(int(x0), int(x1) + 1, 50)])
    # stage spotlight pool where Roxy stands
    c.paint(ell(cx, y0 + 2, 90, 14), (255, 250, 220), ow=0, opacity=0.35)

    # ---------- DJ booth + speaker stack between stage and VIP
    dx0, dx1 = 1290, 1470
    for sy, sh in ((520, 140), (660, 132)):
        c.paint(rect(dx0, sy, dx0 + 90, sy + sh), (30, 30, 36), shade=(-4, 0, (14, 14, 18)))
        c.paint(ell(dx0 + 45, sy + sh * 0.62, 32, 32), (60, 60, 70), ow=3,
                pattern=lambda p, sy=sy, sh=sh: p.ell(dx0 + 45, sy + sh * 0.62, 12, 12, (20, 20, 24)))
        c.paint(ell(dx0 + 45, sy + 24, 12, 12), (60, 60, 70), ow=3)
    c.paint(rect(dx0 + 100, 690, dx1, 790), (40, 30, 50), shade=(-4, 0))
    neon(c, [(dx0 + 104, 702), (dx1 - 4, 702)], (255, 90, 200), 4)
    c.text((dx0 + 100 + dx1) / 2, 746, "DJ", 26, (80, 220, 255), "Display")
    for tx in (dx0 + 120, dx0 + 160):
        c.paint(ell(tx, 684, 16, 5), (20, 20, 24), ow=2.5)

    # ---------- VIP booth behind Jett
    vx0, vx1 = 1560, 1910
    neon_text(c, 1760, 420, "VIP", 56, (255, 220, 80), "Display")
    neon(c, [(1650, 470), (1870, 470)], (255, 220, 80), 4)
    booth = (170, 20, 60)
    back = poly([(vx0, 790), (vx0 + 10, 600), (vx0 + 60, 560), (vx1 - 40, 552), (vx1 + 20, 560), (vx1 + 20, 790)], 1)

    def tuft(p):
        for ty in range(580, 700, 40):
            for tx in range(vx0 + 30, vx1 + 20, 50):
                p.ell(tx + (25 if (ty // 40) % 2 else 0), ty, 4, 4, dk(booth, 0.6))
    c.paint(back, booth, pattern=tuft, shade=(-6, -6, dk(booth, 0.7)), hi=(4, 4, lt(booth, 0.3), 2))
    c.paint(wonky(vx0 + 10, 700, vx1 + 30, 790, 2, rng), lt(booth, 0.1), shade=(0, -6, dk(booth, 0.7)))
    # little table with an ice bucket
    c.paint(ell(1800, 720, 50, 12), (230, 186, 80), ow=3)
    c.paint(rrect(1784, 680, 1816, 716, 4), (200, 200, 210), ow=3, hi=(-2, 0, (250, 250, 255)))
    c.line([(1796, 680), (1808, 650)], 6, (40, 90, 60))

    # ---------- disco ball
    x0, y0, x1, y1 = B["Disco ball"]
    bx, by = (x0 + x1) / 2, (y0 + y1) / 2 + 6
    c.line([(bx, 0), (bx, by - 44)], 3, (140, 140, 150))
    for k in range(10):  # light beams
        a = math.radians(20 + k * 16)
        c.paint(poly([(bx, by), (bx + 1400 * math.cos(a) - 30, by + 1400 * math.sin(a)),
                      (bx + 1400 * math.cos(a) + 30, by + 1400 * math.sin(a))]),
                tile_cols[k % 5], ow=0, opacity=0.05)

    def facets(p):
        for yy in range(int(by - 44), int(by + 44), 9):
            for xx in range(int(bx - 44), int(bx + 44), 9):
                v = rng.uniform(0.55, 1.0)
                p.rect(xx + 1, yy + 1, xx + 8, yy + 8, (int(200 * v), int(206 * v), int(230 * v)))
    c.paint(ell(bx, by, 44, 44), (180, 186, 210), pattern=facets, shade=(-6, -6, None))
    for gx, gy in ((bx - 16, by - 20), (bx + 10, by - 6), (bx - 4, by + 18)):
        c.paint(poly([(gx, gy - 10), (gx + 2, gy - 2), (gx + 10, gy), (gx + 2, gy + 2), (gx, gy + 10),
                      (gx - 2, gy + 2), (gx - 10, gy), (gx - 2, gy - 2)]), (255, 255, 255), ow=0)

    backstage_door(c, *B["Backstage door"])

    lights = [(bx, by, 520, 0.3, (220, 200, 255)), ((B["Stage"][0] + B["Stage"][2]) / 2, 560, 420, 0.45, (255, 200, 240)),
              (460, 520, 360, 0.35, (255, 120, 220)), (1760, 520, 380, 0.35, (255, 220, 120)),
              (960, 980, 700, 0.25, (180, 120, 255)), (1590, 640, 280, 0.35, (255, 190, 230))]
    light_pass(c, 0.72, lights, vign=0.45, front=0.15)
    c.glow(bx, by, 120, (230, 220, 255), 0.4)
    c.glow(1760, 430, 200, (255, 220, 80), 0.25)
    c.glow((B["Exit"][0] + B["Exit"][2]) / 2, B["Exit"][1] - 50, 120, (90, 255, 140), 0.45)
    c.glow((B["Bar"][0] + B["Bar"][2]) / 2, 346, 180, (255, 90, 200), 0.25)
    c.save("bg_nightclub.png")



# =========================================================================== characters (all face left)
def glove_hand(c, x, y, ang=0, col=(252, 252, 250), sh=(206, 208, 224)):
    """Flat white-gloved palm pressed on an invisible wall, fingers up."""
    pts = [(x - 7, y + 8), (x - 8, y - 6), (x + 8, y - 6), (x + 7, y + 8)]
    shp = poly(rot_pts(pts, ang, x, y), 2)
    for k, (dx, L) in enumerate(((-6, 11), (-2, 14), (2, 14), (6, 11))):
        shp = shp + cap(rot_pts([(x + dx, y - 4), (x + dx * 1.1, y - 4 - L)], ang, x, y), 4.2)
    shp = shp + cap(rot_pts([(x + 7, y + 2), (x + 13, y - 6)], ang, x, y), 4.2)
    c.paint(shp, col, shade=(2, 1.5, sh))
    c.paint(cap(rot_pts([(x - 8, y + 10), (x + 8, y + 10)], ang, x, y), 5), col, ow=2.2, shade=(0, -1.5, sh))


def paint_mimi():
    c = Canvas(110, 250, ow=3)
    face, face_sh = (252, 248, 244), (214, 210, 226)
    navy, white = (36, 40, 90), (250, 248, 240)
    black, black_hi = (34, 30, 40), (90, 84, 104)
    beret = (210, 36, 60)

    def stripes(p):
        for y in range(84, 160, 9):
            p.rect(0, y, 110, y + 4.5, navy)
    # hair behind (black bob)
    c.paint(ell(62, 56, 28, 27) + poly([(40, 64), (90, 62), (90, 82), (40, 82)], 2), black,
            shade=(4, 0, (20, 18, 26)))
    # far arm: up and forward, palm flat on the wall
    c.paint(cap([(64, 100), (44, 86), (22, 80)], 8.5), white, pattern=stripes, shade=(2, 2, (210, 208, 220)))
    glove_hand(c, 14, 78, -8)
    # legs: slim black trousers, braced against the wall
    c.paint(cap([(64, 150), (68, 196), (74, 232)], 15), black, shade=(3, 0, (18, 16, 22)))
    c.paint(cap([(48, 150), (44, 194), (42, 232)], 15.5), black, shade=(3, 0, (18, 16, 22)), hi=(-2, 0, black_hi))
    for xh, xt, yt, yb in ((86, 60, 232, 244), (54, 24, 234, 247)):
        c.paint(shoe_shape(xh, xt, yt, yb, toe_h=0.5), black, shade=(2, -2, (14, 12, 18)), hi=(-1, 1.5, black_hi, 1))
        c.paint(ell((xh + xt) / 2 - 2, yt + 3, 4, 2), (240, 240, 240), ow=1.2)  # bow
    # torso: striped shirt, suspenders, high-waisted trousers
    torso = poly([(38, 96), (56, 91), (72, 95), (78, 108), (74, 132), (76, 156), (36, 156), (36, 124), (34, 106)], 2)
    c.paint(torso, white, pattern=stripes, shade=(4, 2, (210, 208, 220)))
    c.paint(poly([(36, 138), (76, 138), (77, 158), (35, 158)], 1), black, ow=2.4, shade=(3, 0, (18, 16, 22)))
    for sx0, sx1 in ((44, 46), (64, 62)):
        c.paint(cap([(sx0, 94), (sx1, 140)], 4.5), (200, 30, 50), ow=2)
        c.paint(ell(sx1, 138, 2.4, 2.4), (240, 200, 80), ow=1.4)
    # neck + white collar ruff
    c.paint(cap([(56, 80), (56, 94)], 9), face, shade=(3, 0, face_sh))
    c.paint(poly([(42, 92), (56, 98), (70, 92), (66, 86), (56, 92), (46, 86)], 1), white, ow=2.2)
    # near arm: up and forward, the other palm
    c.paint(cap([(42, 100), (30, 116), (20, 112)], 9), white, pattern=stripes, shade=(2, 2, (210, 208, 220)))
    glove_hand(c, 13, 110, 6)

    # ---- head (white face paint, facing left)
    head = ell(58, 54, 24, 26) + poly([(36, 58), (38, 76), (48, 85), (60, 83), (76, 68)], 2) + ell(33.5, 61, 5, 4.8)
    c.paint(head, face, shade=(4, 3, face_sh), hi=(-3, 3, (255, 255, 255), 2))
    c.paint(ell(78, 60, 5, 7.5), face, shade=(2, 2, face_sh))
    c.curve((34, 64), (31, 65), (30, 62), 1.4)
    # rosy cheek dots
    c.paint(ell(52, 68, 5, 4), (255, 110, 140), ow=0, opacity=0.65)
    # big worried eyes (inner brows raised), black diamond makeup
    eye(c, 52, 54, 8, 10.5, 47.5, 57, 2.6, skin=face, lashes=1, iris=(70, 130, 210))
    eye(c, 37.5, 53.5, 5.5, 9.8, 34, 56.5, 2.2, skin=face, lashes=-1, iris=(70, 130, 210))
    c.paint(poly([(52, 66), (54.5, 71), (52, 76), (49.5, 71)]), black, ow=0)
    c.paint(poly([(52, 34), (54, 38.5), (52, 43), (50, 38.5)]), black, ow=0)
    c.line([(44, 40), (49, 37), (58, 39)], 2.2, black)  # brows raised in the middle
    c.line([(32, 41), (38, 38)], 2.0, black)
    # small red "oh no" mouth
    c.paint(ell(39, 75, 3.6, 4.2), (210, 36, 60), ow=1.8, pattern=lambda p: p.ell(39, 76.5, 1.8, 2, (120, 20, 40)))
    # fringe + bob ends in front
    c.paint(poly([(36, 46), (44, 34), (60, 30), (78, 36), (86, 50), (88, 70), (82, 84), (78, 72), (76, 56), (64, 44),
                  (52, 44), (42, 50)], 2, True), black, shade=(3, 2, (20, 18, 26)), hi=(-2, 2, black_hi, 1.5))
    # beret, tilted
    c.paint(ell(60, 32, 30, 11, -8), beret, shade=(3, 3, dk(beret, 0.7)), hi=(-2, -3, lt(beret, 0.4), 2))
    c.paint(cap([(60, 22), (62, 16)], 3), beret, ow=2)
    c.paint(cap([(40, 38), (78, 33)], 4), dk(beret, 0.75), ow=2)
    c.fit(margin=3)
    c.save("hs_mimi.png")


def paint_jett_vex():
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (246, 206, 180), (210, 150, 140)
    hair, hair_sh, hair_hi = (90, 236, 110), (40, 170, 80), (190, 255, 190)
    leather, leather_sh, leather_hi = (44, 40, 50), (24, 20, 30), (110, 104, 124)
    pink = (255, 70, 160)
    plaid = (200, 30, 50)

    # guitar slung on her back: neck over the far shoulder, body behind the hip
    gcol = (240, 50, 120)
    c.paint(cap([(84, 140), (98, 40)], 7), (90, 56, 34), ow=2.6)
    for k in range(4):
        c.line([(85 + k * 3.2, 116 - k * 22), (88 + k * 3.2, 116 - k * 22)], 1.2, (230, 230, 230))
    c.paint(poly([(94, 42), (104, 40), (106, 22), (96, 20)], 1), OUT, ow=2)
    body = ell(92, 154, 16, 18, -15) + ell(86, 132, 11, 12, -15) + poly([(76, 128), (98, 124), (104, 150), (80, 160)])
    c.paint(body, gcol, shade=(3, 2, dk(gcol, 0.7)), hi=(-2, -2, lt(gcol, 0.4), 1.5))
    c.paint(poly([(84, 140), (98, 136), (102, 158), (88, 164)], 1), (250, 246, 236), ow=2)
    c.paint(rect(86, 150, 100, 154), (40, 40, 46), ow=1.4)
    c.paint(cap([(66, 92), (84, 150)], 4), (30, 26, 34), ow=1.6)  # strap
    # legs: ripped black tights, plaid skirt
    tights = (40, 34, 48)

    def rips(p):
        for x, y, r in ((44, 172, 3.4), (46, 196, 2.6), (64, 184, 3), (66, 206, 2.2)):
            p.ell(x, y, r, r * 0.7, skin)
    c.paint(cap([(64, 150), (66, 196), (68, 220)], 13), tights, pattern=rips, shade=(3, 0, (20, 16, 26)))
    c.paint(cap([(46, 150), (44, 196), (42, 220)], 13.5), tights, pattern=rips, shade=(3, 0, (20, 16, 26)))
    # combat boots
    for xh, xt, yt, yb, top in ((82, 54, 234, 252, 212), (58, 20, 238, 256, 214)):
        shaft = poly([(xh - 20, top), (xh - 1, top - 1), (xh, yt + 4), (xh - 22, yt + 4)], 1)
        foot = shoe_shape(xh, xt, yt, yb, toe_h=0.6)
        c.paint(shaft + foot, (30, 28, 34), shade=(2, -2, (14, 12, 18)), hi=(-2, 2, (90, 86, 100), 1.2))
        c.paint(rect(xt - 4, yb - 4, xh + 2, yb + 2), (60, 56, 66), ow=0, clip=foot)
        c.line([(xt - 1, yb - 4), (xh, yb - 4)], 1.4)
        for k in range(4):
            c.line([(xh - 17, top + 5 + k * 6), (xh - 5, top + 3 + k * 6)], 1.3, (250, 220, 90))
    c.paint(poly([(36, 132), (76, 132), (82, 160), (32, 160)], 1), plaid, ow=2.6,
            pattern=lambda p: [p.line([(x, 132), (x - 4, 160)], 2.2, (40, 20, 30)) for x in range(36, 84, 9)] +
            [p.line([(30, y), (84, y)], 2, (250, 200, 60)) for y in (140, 151)], shade=(3, 0, dk(plaid, 0.7)))
    c.paint(rect(36, 130, 76, 136), (30, 26, 34), ow=2.2)
    for k in range(5):
        c.paint(ell(40 + k * 8, 133, 1.6, 1.6), (220, 220, 230), ow=0)
    # neck + pink tank top
    c.paint(cap([(56, 80), (56, 96)], 9.5), skin, shade=(3, 0, skin_sh))
    c.paint(poly([(42, 94), (70, 94), (72, 134), (40, 134)], 1), pink, shade=(3, 0, dk(pink, 0.7)))
    c.text(56, 112, "★", 13, (255, 240, 120))
    # leather jacket (open), studs on the shoulders
    for side in ((38, 94, 50, 96, 48, 134, 34, 134, 32, 110), (72, 94, 62, 96, 64, 134, 78, 134, 80, 110)):
        pts = [(side[i], side[i + 1]) for i in range(0, 10, 2)]
        c.paint(poly(pts, 1), leather, shade=(3, 2, leather_sh), hi=(-2, 2, leather_hi, 1.5))
    c.paint(poly([(40, 92), (50, 96), (46, 112), (36, 100)], 1), leather_hi, ow=2.2)
    c.paint(poly([(70, 92), (62, 96), (66, 112), (76, 100)], 1), leather_hi, ow=2.2)
    for sx, sy in ((36, 98), (40, 95), (74, 98), (70, 95)):
        c.paint(ell(sx, sy, 1.8, 1.8), (220, 220, 230), ow=1.2)
    # arms crossed: far forearm under, near forearm over, sleeves of the jacket
    c.paint(cap([(74, 100), (78, 120), (60, 124)], 10.5), leather, shade=(2, 2, leather_sh))
    c.paint(ell(50, 120, 5.5, 5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(38, 100), (34, 118), (62, 116)], 10.5), leather, shade=(2, 2, leather_sh), hi=(-1, 1, leather_hi, 1))
    c.paint(ell(66, 115, 5.5, 5), skin, shade=(2, 2, skin_sh))
    c.line([(40, 104), (44, 108)], 1.2, leather_hi)

    # ---- head (facing left, half-lidded, bored)
    head = ell(58, 54, 23, 25) + poly([(36, 58), (38, 76), (48, 84), (60, 82), (76, 66)], 2) + ell(34, 61, 5, 4.8)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, (255, 230, 210), 2))
    c.paint(ell(78, 58, 5.5, 8), skin, shade=(2, 2, skin_sh))
    for k in range(3):  # ear piercings
        c.paint(ell(80 - k * 0.5, 52 + k * 5, 1.6, 1.6), (230, 230, 240), ow=1.2)
    c.curve((35, 64), (32, 65), (31, 62), 1.4)
    c.paint(ell(33, 66, 1.6, 1.6), (0, 0, 0, 0), ow=1.2, oc=(230, 230, 240))  # nose ring
    eye(c, 52, 55, 7.5, 9.5, 47.5, 58, 2.4, lid=0.5, lid_tilt=0.4, skin=skin, iris=(160, 90, 200))
    eye(c, 37.5, 54.5, 5.2, 8.8, 34.5, 57.5, 2.1, lid=0.5, lid_tilt=-0.4, skin=skin, iris=(160, 90, 200))
    c.line([(58, 52), (63, 49)], 2.2)  # eyeliner wings
    c.line([(44, 45), (52, 44), (60, 46)], 2.4, (30, 26, 34))  # flat, unimpressed brows
    c.line([(32, 46), (39, 45)], 2.2, (30, 26, 34))
    c.line([(40, 75), (48, 74.5)], 1.8)  # flat mouth...
    c.paint(ell(36, 76, 8, 7.5), (255, 150, 200), ow=2, hi=(-2, -2, (255, 220, 240), 1.5))  # ...and a gum bubble
    # spiky hair: shaved side, tall green spikes
    c.paint(poly([(62, 36), (80, 40), (84, 56), (78, 50), (66, 44)], 1), (70, 60, 70), ow=2)
    spikes = [(36, 46), (30, 32), (42, 36), (40, 14), (52, 28), (56, 2), (64, 26), (74, 6), (76, 30), (90, 18),
              (84, 38), (78, 40), (64, 36), (50, 38), (42, 46)]
    c.paint(poly(spikes, 1), hair, shade=(3, 2, hair_sh), hi=(-2, 3, hair_hi, 1.5))
    c.line([(46, 34), (50, 22)], 1.3, hair_sh)
    c.line([(62, 30), (68, 16)], 1.3, hair_sh)
    c.fit(margin=3)
    c.save("hs_jett_vex.png")


def paint_brutus():
    c = Canvas(140, 275, ow=3)
    skin, skin_sh, skin_hi = (150, 96, 70), (110, 66, 52), (196, 140, 104)
    tee, tee_sh = (34, 32, 40), (18, 16, 22)
    pants = (52, 52, 62)

    # legs + boots (wide stance)
    c.paint(cap([(84, 176), (88, 220), (92, 246)], 22), pants, shade=(3, 0, (34, 34, 42)))
    c.paint(cap([(56, 176), (52, 220), (50, 246)], 23), pants, shade=(3, 0, (34, 34, 42)), hi=(-2, 0, (90, 90, 104)))
    for xh, xt, yt, yb in ((108, 72, 248, 266), (70, 26, 250, 270)):
        c.paint(shoe_shape(xh, xt, yt, yb, toe_h=0.6), (28, 26, 30), shade=(2, -2, (12, 10, 14)),
                hi=(-1, 2, (80, 78, 90), 1.2))
    c.paint(poly([(44, 164), (100, 164), (104, 184), (40, 184)], 1), pants, shade=(3, 0, (34, 34, 42)))
    c.paint(rect(42, 162, 102, 170), (20, 20, 24), ow=2.2)
    c.paint(rrect(64, 161, 78, 171, 2), (200, 200, 210), ow=1.6)
    # huge torso in a tight black tee
    torso = poly([(26, 94), (60, 84), (100, 86), (120, 100), (116, 132), (104, 168), (40, 168), (28, 134)], 2)
    c.paint(torso, tee, shade=(5, 2, tee_sh), hi=(-3, 3, (80, 76, 96), 2))
    c.text(70, 150, "SECURITY", 9.5, (240, 240, 240), "Black")
    # neck
    c.paint(poly([(52, 70), (82, 70), (88, 92), (48, 92)], 1), skin, shade=(4, 0, skin_sh))
    c.paint(poly([(52, 86), (68, 94), (84, 86), (82, 92), (68, 100), (54, 92)], 1), tee, ow=2.2)
    # earpiece coil down the neck
    c.curve((92, 66), (98, 80), (94, 96), 1.4, (220, 220, 230))
    # crossed arms with a clipboard tucked under: far arm under, near arm over
    c.paint(cap([(110, 100), (118, 126), (82, 132)], 19), skin, shade=(3, 2, skin_sh))
    c.paint(cap([(108, 98), (114, 112)], 24), tee, shade=(3, 2, tee_sh))
    # clipboard sticking out on the left
    c.paint(poly([(10, 112), (40, 104), (48, 146), (18, 154)], 1), (190, 140, 80), shade=(-2, -2, (150, 100, 56)))
    c.paint(poly([(16, 116), (38, 110), (44, 142), (22, 148)], 1), (250, 250, 244), ow=2,
            pattern=lambda p: [p.line([(20, 122 + k * 6 - k * 1.5), (38, 117 + k * 6 - k * 1.5)], 1.2, (120, 140, 200))
                               for k in range(5)])
    c.paint(rrect(20, 104, 32, 112, 2), (170, 176, 186), ow=2)
    c.paint(cap([(32, 100), (22, 126), (66, 136)], 20), skin, shade=(3, 2, skin_sh), hi=(-2, -2, skin_hi, 1.5))
    c.paint(cap([(34, 98), (26, 112)], 25), tee, shade=(3, 2, tee_sh))
    c.paint(ell(84, 132, 10, 9), skin, shade=(2, 2, skin_sh))
    c.line([(80, 126), (78, 136)], 1.2, skin_sh)
    c.line([(86, 126), (84, 137)], 1.2, skin_sh)

    # ---- head: bald, square jaw, shades, facing left
    head = ell(66, 44, 25, 27) + poly([(42, 46), (42, 70), (54, 80), (78, 78), (90, 62), (88, 40)], 2) + \
        ell(40, 52, 5.5, 6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, skin_hi, 2))
    c.paint(ell(56, 22, 9, 4, -20), (230, 190, 160), ow=0, opacity=0.5)  # shiny scalp
    c.paint(ell(88, 50, 6, 9), skin, shade=(2, 2, skin_sh))
    c.paint(ell(90, 50, 3, 4), (40, 40, 46), ow=1.4)  # earpiece
    c.curve((41, 56), (38, 57), (38, 53), 1.4)
    # sunglasses
    c.paint(rrect(46, 38, 66, 52, 5), (20, 20, 26), ow=2.4, hi=(-2, -2, (90, 120, 200), 1.5))
    c.paint(rrect(34, 38, 44, 51, 4), (20, 20, 26), ow=2.4)
    c.line([(44, 42), (46, 42)], 2)
    c.line([(66, 41), (86, 46)], 2.2)
    c.line([(36, 34), (48, 33), (66, 35)], 3, (60, 36, 30))  # unibrow-ish frown over the shades
    # stern mouth + chin dimple
    c.line([(44, 68), (54, 67)], 2.2)
    c.curve((48, 76), (50, 78), (52, 76), 1.2, skin_sh)
    c.fit(margin=3)
    c.save("hs_brutus.png")


def paint_pierre():
    c = Canvas(100, 260, ow=3)
    skin, skin_sh = (252, 220, 196), (220, 166, 150)
    hair, hair_sh = (220, 220, 230), (160, 160, 178)
    blk, blk_sh, blk_hi = (34, 32, 40), (18, 16, 22), (90, 86, 104)
    blazer, blazer_sh = (130, 30, 60), (90, 20, 46)
    trou = (150, 150, 164)

    # far arm: hand on hip, elbow back
    c.paint(cap([(68, 98), (82, 120), (68, 140)], 8), blazer, shade=(3, 2, blazer_sh))
    # long skinny legs, one knee bent elegantly
    c.paint(cap([(60, 150), (62, 196), (64, 234)], 11.5), trou, shade=(3, 0, dk(trou, 0.75)))
    c.paint(cap([(46, 150), (40, 194), (42, 236)], 12), trou, shade=(3, 0, dk(trou, 0.75)), hi=(-2, 0, lt(trou, 0.3)))
    for xh, xt, yt, yb in ((74, 40, 234, 246), (52, 12, 238, 250)):
        c.paint(shoe_shape(xh, xt, yt, yb, pointy=True), blk, shade=(2, -2, blk_sh), hi=(-1, 1.5, blk_hi, 1))
    # turtleneck torso + blazer
    c.paint(poly([(40, 92), (66, 92), (70, 150), (38, 150)], 1), blk, shade=(3, 0, blk_sh))
    for pts in ([(36, 94), (48, 92), (48, 150), (34, 152), (32, 120)], [(70, 94), (60, 92), (62, 150), (74, 152), (74, 120)]):
        c.paint(poly(pts, 1), blazer, shade=(3, 2, blazer_sh), hi=(-2, 2, lt(blazer, 0.3), 1.5))
    c.paint(poly([(40, 92), (48, 96), (46, 116), (38, 102)], 1), dk(blazer, 0.85), ow=2.2)
    c.paint(poly([(66, 92), (60, 96), (62, 116), (70, 102)], 1), dk(blazer, 0.85), ow=2.2)
    c.paint(poly([(38, 104), (42, 102), (44, 108), (40, 110)], 1), (255, 220, 90), ow=1.6)  # pocket square
    # turtleneck collar + long neck
    c.paint(cap([(54, 74), (54, 92)], 9), skin, shade=(3, 0, skin_sh))
    c.paint(rrect(44, 84, 64, 98, 4), blk, ow=2.4, hi=(0, -2, blk_hi))
    # near arm holding a glass of sparkling water, pinky out
    c.paint(cap([(38, 98), (30, 118), (24, 104)], 8), blazer, shade=(3, 2, blazer_sh))
    c.paint(ell(23, 100, 5, 5.5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(27, 98), (32, 93)], 2.6), skin, ow=1.6)
    glass = poly([(14, 74), (30, 74), (26, 90), (18, 90)], 1)
    c.paint(glass, (220, 240, 250), ow=2.2, pattern=lambda p: [p.rect(14, 80, 30, 92, (180, 220, 240)),
                                                               p.ell(20, 84, 1, 1, (255, 255, 255)),
                                                               p.ell(24, 81, 0.8, 0.8, (255, 255, 255))])
    c.line([(22, 90), (22, 100)], 1.8)
    c.paint(ell(22, 101, 5, 1.6), (220, 240, 250), ow=1.6)

    # ---- head: long face, nose in the air, facing left
    head = ell(56, 46, 21, 24) + poly([(36, 52), (38, 70), (46, 78), (58, 76), (72, 60)], 2) + \
        poly([(37, 44), (24, 44), (34, 52)], 1)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, (255, 240, 226), 2))
    c.paint(ell(74, 50, 5, 7.5), skin, shade=(2, 2, skin_sh))
    # closed, superior eyes behind tiny round glasses
    c.curve((44, 42), (48, 45), (52, 42), 1.8)
    c.curve((34, 42), (37, 44), (40, 42), 1.6)
    for gx, gy, r in ((48, 42, 6), (37, 42, 4.6)):
        c.paint(ell(gx, gy, r, r), (0, 0, 0, 0), ow=1.8)
    c.line([(42.5, 41), (41.5, 41)], 1.6)
    c.line([(54, 41), (72, 46)], 1.4)
    c.line([(42, 34), (48, 31), (55, 33)], 2.0, hair_sh)  # one eyebrow raised high
    c.line([(32, 36), (38, 35)], 1.8, hair_sh)
    # pencil moustache + small pursed smirk + pointy goatee
    c.curve((30, 56), (36, 54), (42, 57), 1.6, (120, 110, 120))
    c.line([(34, 62), (41, 61)], 1.6)
    c.paint(poly([(38, 72), (44, 74), (40, 84)], 1), hair, ow=2, shade=(2, 0, hair_sh))
    # swoop of silver hair
    c.paint(poly([(36, 34), (40, 20), (56, 14), (76, 18), (80, 34), (76, 56), (72, 40), (60, 30), (46, 30)], 2, True),
            hair, shade=(3, 2, hair_sh), hi=(-2, 2, (250, 250, 255), 1.5))
    c.paint(poly([(40, 22), (26, 12), (44, 14), (58, 14)], 2), hair, shade=(0, 2, hair_sh))
    c.curve((48, 20), (60, 18), (70, 24), 1.2, hair_sh)
    c.fit(margin=3)
    c.save("hs_pierre.png")



# =========================================================================== wall-hung canvases (sprites so they can vanish)
def canvas_face(c, x0, y0, x1, y1, art=None):
    depth = (x1 - x0) * 0.05
    c.paint(poly([(x1, y0 + depth), (x1 + depth, y0), (x1 + depth, y1 - depth), (x1, y1)]), (214, 204, 186),
            shade=(-2, 0, (190, 180, 160)))
    c.paint(rect(x0, y0 + depth, x1, y1), (252, 250, 244), shade=(-6, -6, (226, 222, 214)),
            hi=(4, 4, (255, 255, 255), 3), pattern=art)


def paint_blank_canvas():
    c = Canvas(260, 260, ow=4)
    canvas_face(c, 6, 6, 246, 250)
    c.fit(margin=2)
    c.save("hs_blank_canvas.png")


def jett_art(p, x0, y0, x1, y1, seed=7):
    rng = random.Random(seed)
    W, H = x1 - x0, y1 - y0
    cols = [(255, 60, 160), (80, 230, 110), (30, 26, 34), (255, 220, 60), (80, 200, 255)]
    p.rect(x0, y0, x1, y1, (255, 248, 240))
    for k in range(9):  # big brush slashes
        col = cols[k % len(cols)]
        a = (x0 + rng.uniform(0, W), y0 + rng.uniform(0, H))
        b = (x0 + rng.uniform(0, W), y0 + rng.uniform(0, H))
        p.line([a, b], W * rng.uniform(0.04, 0.09), col)
    for k in range(40):  # splatter
        col = cols[rng.randrange(len(cols))]
        r = W * rng.uniform(0.006, 0.03)
        p.ell(x0 + rng.uniform(0, W), y0 + rng.uniform(0, H), r, r, col)
    # lightning bolt
    bx, by, s = x0 + W * 0.3, y0 + H * 0.12, W / 240
    bolt = [(bx + 30 * s, by), (bx + 80 * s, by), (bx + 55 * s, by + 70 * s), (bx + 90 * s, by + 70 * s),
            (bx + 10 * s, by + 190 * s), (bx + 35 * s, by + 100 * s), (bx, by + 100 * s)]
    p.poly([(x + 4 * s, y + 4 * s) for x, y in bolt], (30, 26, 34))
    p.poly(bolt, (255, 230, 50))
    # heart
    hx, hy, hs = x0 + W * 0.74, y0 + H * 0.3, W / 240 * 22
    p.ell(hx - hs * 0.55, hy, hs * 0.65, hs * 0.6, (230, 30, 80))
    p.ell(hx + hs * 0.55, hy, hs * 0.65, hs * 0.6, (230, 30, 80))
    p.poly([(hx - hs * 1.15, hy + hs * 0.15), (hx + hs * 1.15, hy + hs * 0.15), (hx, hy + hs * 1.4)], (230, 30, 80))
    # tiny angry Brutus doodle
    dx, dy, d = x0 + W * 0.72, y0 + H * 0.72, W / 240
    p.ell(dx, dy, 22 * d, 24 * d, (30, 26, 34))
    p.ell(dx, dy, 19 * d, 21 * d, (200, 140, 100))
    p.rect(dx - 16 * d, dy - 8 * d, dx + 16 * d, dy + 1 * d, (30, 26, 34))
    p.line([(dx - 8 * d, dy + 11 * d), (dx + 8 * d, dy + 11 * d)], 2.5 * d, (30, 26, 34))
    # signature
    p.line([(x0 + W * 0.08, y1 - H * 0.08), (x0 + W * 0.13, y1 - H * 0.16), (x0 + W * 0.16, y1 - H * 0.07),
            (x0 + W * 0.22, y1 - H * 0.15)], 3 * d, (30, 26, 34))


def paint_something_no_1():
    c = Canvas(260, 260, ow=4)
    canvas_face(c, 6, 6, 246, 250, art=lambda p: jett_art(p, 6, 18, 246, 250))
    c.fit(margin=2)
    c.save("hs_something_no_1.png")


# =========================================================================== inventory icons (128x128)
def icon(name, angle, draw):
    c = Canvas(128, 128, ow=5)
    draw(c)
    if angle:
        c.img = c.img.rotate(angle, resample=paint.Image.BICUBIC, center=(64 * paint.S, 64 * paint.S))
    c.fit(feet=False, fill=112)
    c.save(name)


def paint_icon_vip_pass():
    def draw(c):
        c.curve((40, 8), (64, 40), (88, 8), 5, (255, 220, 80))  # lanyard
        c.paint(rrect(54, 22, 74, 36, 3), (200, 200, 210), ow=3)
        card = rrect(18, 32, 110, 116, 10)
        rng = random.Random(3)

        def glitter(p):
            p.rect(0, 0, 128, 128, (150, 40, 170))
            for _ in range(40):
                x, y = rng.uniform(18, 110), rng.uniform(32, 116)
                p.ell(x, y, 1.6, 1.6, (255, 200, 255))
        c.paint(card, (150, 40, 170), pattern=glitter, shade=(4, 4, (100, 20, 120)), hi=(-3, -3, (220, 120, 230), 3))
        c.text(64, 70, "VIP", 34, (255, 230, 80), "Display", stroke=2.5)
        c.text(64, 100, "CLUB VELOUR", 10, (255, 255, 255), "Black")
        c.paint(rrect(54, 36, 74, 44, 3), (60, 20, 70), ow=2)
    icon("icon_vip_pass.png", -8, draw)


def paint_icon_blank_canvas():
    def draw(c):
        canvas_face(c, 18, 14, 104, 112)
        c.paint(rect(40, 112, 82, 120), (255, 255, 252), ow=2.5)
    icon("icon_blank_canvas.png", 6, draw)


def paint_icon_paint_set():
    def draw(c):
        pal = poly([(14, 70), (24, 40), (60, 26), (100, 34), (118, 62), (106, 92), (70, 104), (40, 112), (22, 100)], 2,
                   True)
        c.paint(pal, (220, 170, 110), shade=(4, 4, (170, 120, 76)), hi=(-3, -3, (250, 210, 160), 3))
        c.paint(ell(36, 86, 9, 8), (0, 0, 0, 0), ow=3)
        for x, y, col in ((44, 48, (255, 60, 160)), (70, 40, (80, 230, 110)), (94, 52, (30, 26, 34)),
                          (98, 76, (255, 220, 60)), (70, 86, (80, 160, 255))):
            c.paint(ell(x, y, 10, 8, 20), col, ow=3, hi=(-2, -2, lt(col, 0.5), 2))
        c.line([(30, 120), (96, 30)], 7, (170, 110, 60))
        c.paint(rect(86, 34, 100, 46), (200, 200, 210), ow=2.5)
        c.paint(poly([(92, 34), (104, 20), (108, 10), (98, 22)], 1), (255, 60, 160), ow=3)
    icon("icon_paint_set.png", -6, draw)


def paint_icon_jett_canvas():
    def draw(c):
        canvas_face(c, 18, 14, 104, 112, art=lambda p: jett_art(p, 18, 18, 104, 112, seed=7))
    icon("icon_jett_canvas.png", -6, draw)


def paint_icon_invisible_key():
    def draw(c):
        key = ell(38, 64, 22, 22) + rect(56, 58, 112, 70) + rect(92, 70, 100, 86) + rect(104, 70, 112, 82)
        c.paint(key, (200, 230, 255, 60), ow=3, oc=(160, 190, 230))
        c.paint(ell(38, 64, 9, 9), (0, 0, 0, 0), ow=3, oc=(160, 190, 230))
        for gx, gy, r in ((30, 40, 8), (96, 46, 6), (70, 92, 5), (18, 84, 4)):
            c.paint(poly([(gx, gy - r * 2), (gx + r * 0.4, gy - r * 0.4), (gx + r * 2, gy), (gx + r * 0.4, gy + r * 0.4),
                          (gx, gy + r * 2), (gx - r * 0.4, gy + r * 0.4), (gx - r * 2, gy), (gx - r * 0.4, gy - r * 0.4)]),
                    (255, 250, 200), ow=2.5)
        c.text(76, 112, "?", 18, (160, 190, 230), "Black")
    icon("icon_invisible_key.png", -20, draw)


def paint_icon_white_glove():
    def draw(c):
        g, gsh = (252, 252, 250), (200, 204, 222)
        hand = rrect(36, 50, 92, 104, 18)
        for x, top in ((40, 18), (54, 8), (68, 10), (82, 22)):
            hand = hand + cap([(x + 2, 60), (x + 2, top + 6)], 13)
        hand = hand + cap([(40, 84), (18, 62)], 13)
        c.paint(hand, g, shade=(4, 3, gsh), hi=(-3, -2, (255, 255, 255), 2))
        for x in (62, 76):
            c.line([(x, 92), (x, 66)], 2, gsh)
        c.paint(rrect(34, 100, 94, 120, 6), g, shade=(0, -3, gsh))
        c.line([(40, 110), (88, 110)], 2, gsh)
    icon("icon_white_glove.png", 12, draw)


def paint_icon_guitar_pick():
    def draw(c):
        col = (90, 230, 110)
        pick = poly([(20, 30), (64, 18), (108, 30), (104, 64), (64, 116), (24, 64)], 3, True)
        c.paint(pick, col, shade=(4, 4, dk(col, 0.7)), hi=(-4, -4, lt(col, 0.5), 3))
        bolt = [(60, 32), (78, 32), (68, 56), (82, 56), (52, 94), (60, 64), (48, 64)]
        c.paint(poly(bolt), (255, 230, 60), ow=3)
        c.paint(ell(94, 38, 6, 4, 30), dk(col, 0.6), ow=0, opacity=0.6)  # chewed corner
    icon("icon_guitar_pick.png", 10, draw)


# =========================================================================== expansion: shared door helpers
def cafe_arch(c, x0, y0, x1, y1):
    """Uptown street: a stone archway at the far right leading down a warm-lit lane to Cafe Snoot."""
    y1 = WALL_Y
    stone = (214, 196, 170)
    # arch frame
    frame = rect(x0 - 18, y0 - 30, x1 + 30, y1 + 2)
    c.paint(frame, ("v", lt(stone, 0.1), dk(stone, 0.8)), shade=(-5, 0, dk(stone, 0.7)))
    opening = rect(x0, y0 + 40, x1, y1) + ell((x0 + x1) / 2, y0 + 42, (x1 - x0) / 2, 42)

    def lane(p):
        p.rect(x0 - 10, y0, x1 + 10, y1, (90, 50, 60))
        p.rect(x0 - 10, y1 - 90, x1 + 10, y1, (150, 110, 90))
        p.poly([(x0 + 20, y1 - 90), (x1 - 20, y1 - 90), (x1 + 10, y1), (x0 - 10, y1)], (180, 140, 110))
        # far cafe front: glowing window + striped awning
        p.rect(x0 + 18, y1 - 190, x1 - 18, y1 - 92, (255, 214, 140))
        p.rect(x0 + 24, y1 - 150, x0 + 50, y1 - 92, (120, 70, 50))
        for k in range(5):
            sx = x0 + 10 + k * 20
            p.poly([(sx, y1 - 214), (sx + 10, y1 - 214), (sx + 10, y1 - 196), (sx, y1 - 196)], (250, 240, 220))
        p.rect(x0 + 6, y1 - 214, x1 - 6, y1 - 196, (150, 30, 50))
        for k in range(5):
            sx = x0 + 10 + k * 20
            p.rect(sx, y1 - 214, sx + 10, y1 - 196, (250, 240, 220))
        # tiny table silhouette
        p.ell((x0 + x1) / 2 + 14, y1 - 60, 16, 4, (60, 40, 40))
        p.line([((x0 + x1) / 2 + 14, y1 - 58), ((x0 + x1) / 2 + 14, y1 - 30)], 3, (60, 40, 40))
    c.paint(opening, (90, 50, 60), ow=3.5, pattern=lane)
    # string lights inside the arch
    for k in range(6):
        bxp = x0 + 10 + k * (x1 - x0 - 20) / 5
        byp = y0 + 70 + 14 * math.sin(k * 1.3)
        c.paint(ell(bxp, byp, 4.5, 6), (255, 226, 140), ow=1.8)
    c.line([(x0 + 6, y0 + 62), (x1 - 6, y0 + 66)], 1.5, (40, 30, 30))
    # keystone + hanging sign
    c.paint(poly([((x0 + x1) / 2 - 16, y0 - 30), ((x0 + x1) / 2 + 16, y0 - 30), ((x0 + x1) / 2 + 10, y0 + 6),
                  ((x0 + x1) / 2 - 10, y0 + 6)]), lt(stone, 0.2), ow=3)
    sx0, sx1, sy0, sy1 = x0 - 24, x1 + 24, y0 - 120, y0 - 50
    c.line([(sx0 + 20, y0 - 30), (sx0 + 20, sy1)], 2.5, (60, 50, 50))
    c.line([(sx1 - 20, y0 - 30), (sx1 - 20, sy1)], 2.5, (60, 50, 50))
    c.paint(rrect(sx0, sy0, sx1, sy1, 8), (150, 30, 50), shade=(-4, -4, (100, 20, 36)), hi=(3, 3, (210, 80, 100), 2))
    c.text((sx0 + sx1) / 2, sy0 + 22, "CAFE", 20, (255, 236, 180), "Display")
    c.text((sx0 + sx1) / 2, sy0 + 48, "SNOOT", 18, (255, 236, 180), "Display")
    c.glow((x0 + x1) / 2, y1 - 140, 110, (255, 200, 120), 0.35)


def backstage_door(c, x0, y0, x1, y1):
    """Nightclub: a black crew door left of the stage, propped open with a guitar case."""
    y1 = WALL_Y
    c.paint(rect(x0 - 10, y0 - 10, x1 + 10, y1 + 2), (24, 14, 30), shade=(-4, 0, (10, 6, 14)))
    # light leaking out of the gap
    c.paint(rect(x1 - 18, y0, x1, y1), (255, 230, 170), ow=0)
    c.paint(rect(x0, y0, x1 - 18, y1), ("v", (60, 56, 66), (34, 30, 40)), ow=3.5)
    c.paint(rect(x0 + 12, y0 + 120, x1 - 30, y0 + 134), (150, 150, 160), ow=2.5, hi=(0, -2, (210, 210, 220)))
    c.text((x0 + x1 - 18) / 2, y0 + 50, "CREW", 15, (250, 220, 90), "Black")
    c.text((x0 + x1 - 18) / 2, y0 + 70, "ONLY", 15, (250, 220, 90), "Black")
    # sign above
    c.paint(rrect(x0 - 6, y0 - 54, x1 + 6, y0 - 18, 5), (20, 20, 26))
    neon_text(c, (x0 + x1) / 2, y0 - 36, "BACKSTAGE", 15, (255, 160, 60), "Display")
    # guitar case wedged in the gap
    gc = (40, 34, 30)
    case = ell(x1 - 6, y1 - 34, 26, 32, 8) + ell(x1 - 2, y1 - 82, 16, 20, 8) + cap([(x1 + 2, y1 - 96), (x1 + 8, y1 - 150)], 12)
    c.paint(case, gc, shade=(3, 2, (20, 16, 14)), hi=(-2, -2, (90, 80, 70), 1.5))
    c.paint(rect(x1 - 16, y1 - 40, x1 + 4, y1 - 34), (200, 180, 120), ow=1.6)
    c.paint(rrect(x1 - 24, y1 - 70, x1 - 4, y1 - 62, 2), (200, 60, 120), ow=1.6)  # sticker
    c.glow(x1 - 8, y0 + 120, 80, (255, 220, 160), 0.3)


# =========================================================================== cafe snoot
def paint_cafe_snoot():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    B = boxes("cafe_snoot")
    sky(c, 320, seed=61)
    rng = random.Random(62)

    # ---------- left: brick wall with the archway back to the street
    brick(c, -10, 100, 240, WALL_Y, (140, 66, 60), seed=63)
    x0, y0, x1, y1 = B["Uptown street"]
    y1 = WALL_Y
    c.paint(rect(x0 - 14, y0 - 20, x1 + 14, y1 + 2), (200, 180, 156), shade=(-4, 0, (150, 130, 110)))
    opening = rect(x0, y0 + 50, x1, y1) + ell((x0 + x1) / 2, y0 + 52, (x1 - x0) / 2, 52)

    def street(p):
        p.rect(x0 - 10, y0, x1 + 10, y1, (40, 30, 80))
        p.rect(x0 - 10, y1 - 70, x1 + 10, y1, (120, 110, 130))
        p.rect(x0 + 10, y0 + 80, x0 + 70, y1 - 70, (70, 26, 86))
        p.ell(x0 + 40, y0 + 120, 22, 10, (255, 90, 200))
        p.rect(x1 - 50, y0 + 110, x1 - 44, y1 - 70, (50, 56, 66))
        p.ell(x1 - 47, y0 + 104, 12, 12, (255, 220, 140))
    c.paint(opening, (40, 30, 80), ow=3.5, pattern=street)
    c.paint(rrect(x0 + 6, y0 - 70, x1 - 6, y0 - 26, 6), (40, 110, 200), shade=(-3, -3), hi=(3, 3, (110, 170, 240), 2))
    c.text((x0 + x1) / 2, y0 - 48, "UPTOWN", 17, (255, 255, 240))

    # ---------- cafe facade: cream stucco, burgundy trim
    fx0 = 240
    cream = (238, 222, 192)

    def stucco(p):
        for _ in range(260):
            x, y = rng.uniform(fx0, W_BG), rng.uniform(120, WALL_Y)
            p.ell(x, y, rng.uniform(2, 6), rng.uniform(1, 3), dk(cream, 0.93))
    c.paint(rect(fx0, 120, W_BG + 10, WALL_Y), ("vy", 120, WALL_Y, lt(cream, 0.15), dk(cream, 0.85)), pattern=stucco)
    c.paint(rect(fx0 - 10, 104, W_BG + 10, 130), (120, 30, 46), ow=3, hi=(0, 4, (170, 60, 76)))
    c.paint(rect(fx0, WALL_Y - 70, W_BG + 10, WALL_Y), (120, 30, 46), ow=3, hi=(0, 4, (160, 56, 70)))  # dado
    # upstairs: little balconies with shutters
    for wx in (330, 700, 1090, 1480, 1780):
        c.paint(rect(wx - 50, 160, wx + 50, 250), (40, 34, 66), ow=3.5,
                pattern=lambda p, wx=wx: p.rect(wx - 44, 166, wx + 44, 206, (255, 210, 140)))
        c.line([(wx, 160), (wx, 250)], 3)
        for side in (-1, 1):
            sx = wx + side * 76
            c.paint(rect(sx - 24, 156, sx + 24, 254), (60, 100, 80), ow=3,
                    pattern=lambda p, sx=sx: [p.line([(sx - 20, yy), (sx + 20, yy)], 2, (40, 70, 56)) for yy in range(164, 252, 10)])
        c.paint(rect(wx - 62, 250, wx + 62, 262), (60, 50, 50), ow=3)
        for k in range(7):
            c.line([(wx - 56 + k * 18.6, 262), (wx - 56 + k * 18.6, 290)], 2.5, (50, 44, 46))
        c.line([(wx - 62, 290), (wx + 62, 290)], 3.5, (50, 44, 46))

    # big sign
    c.paint(rrect(700, 296, 1240, 360, 10), (30, 26, 30), shade=(0, -5, (12, 10, 14)))
    c.text(970, 328, "CAFE  SNOOT", 40, (240, 210, 130), "Display", stroke=1.5)
    c.text(1300, 330, "EST. 1904", 13, (120, 30, 46), "Black")
    c.text(640, 330, "NO FLORALS", 11, (120, 30, 46), "Black")

    # ---------- windows (lit interior) and door
    def interior(p, a, b, cc, d, kind):
        p.rect(a, b, cc, d, (255, 214, 150))
        p.rect(a, d - 70, cc, d, (150, 80, 50))  # counter / wainscot
        p.rect(a, d - 74, cc, d - 66, (90, 40, 30))
        if kind == "case":   # the empty pastry case + espresso machine
            p.rect(a + 30, d - 130, a + 190, d - 74, (230, 246, 250))
            p.rect(a + 34, d - 100, a + 186, d - 96, (190, 200, 210))
            p.ell(a + 110, d - 84, 30, 5, (240, 240, 236))
            p.rect(cc - 140, d - 150, cc - 40, d - 74, (170, 170, 180))
            p.rect(cc - 130, d - 140, cc - 50, d - 120, (90, 90, 100))
            p.ell(cc - 90, d - 158, 26, 8, (200, 160, 70))
            p.rect(cc - 110, d - 116, cc - 104, d - 96, (60, 60, 66))
            p.rect(cc - 78, d - 116, cc - 72, d - 96, (60, 60, 66))
        else:   # hanging lamps and a framed menu
            for lx in (a + (cc - a) * 0.3, a + (cc - a) * 0.7):
                p.line([(lx, b), (lx, b + 50)], 2, (60, 40, 30))
                p.ell(lx, b + 58, 18, 10, (250, 240, 200))
            p.rect(a + 40, b + 100, a + 110, b + 170, (90, 40, 30))
            p.rect(a + 46, b + 106, a + 104, b + 164, (250, 240, 220))
    for (wx0, wx1, kind) in ((262, 520, "lamp"), (740, 1110, "case"), (1360, 1610, "lamp")):
        c.paint(rect(wx0 - 12, 430, wx1 + 12, 726), (90, 26, 40), shade=(-4, 0, (60, 16, 26)))
        c.paint(rect(wx0, 444, wx1, 712), (255, 214, 150), ow=3.5,
                pattern=lambda p, wx0=wx0, wx1=wx1, kind=kind: interior(p, wx0, 444, wx1, 712, kind))
        c.line([((wx0 + wx1) / 2, 444), ((wx0 + wx1) / 2, 712)], 3.5)
        c.paint(poly([(wx0 + 14, 700), (wx0 + 90, 456), (wx0 + 112, 456), (wx0 + 36, 700)]), (255, 255, 255), ow=0,
                opacity=0.2)
        c.text((wx0 + wx1) / 2, 600, "", 10, (0, 0, 0))
    c.text(850, 548, "CROISSANTS: SOLD OUT", 11, (120, 30, 46), "Black")
    # door behind Anton
    ax = (B["Anton"][0] + B["Anton"][2]) / 2
    dx0, dx1 = ax - 66, ax + 66
    c.paint(rect(dx0 - 14, 440, dx1 + 14, WALL_Y + 2), (90, 26, 40), shade=(-4, 0, (60, 16, 26)))
    c.paint(rect(dx0, 454, dx1, WALL_Y), ("v", (255, 222, 160), (220, 160, 100)), ow=3.5)
    c.paint(rect(dx0 + 14, 470, dx1 - 14, 640), (255, 236, 190), ow=2.5)
    c.text((dx0 + dx1) / 2, 520, "OUVERT", 12, (120, 30, 46), "Black")
    c.paint(rrect(dx1 - 26, 640, dx1 - 16, 700, 3), (230, 186, 80), ow=2.5)

    # ---------- striped awning over the whole terrace
    ax0, ax1, ay0, ay1 = 250, W_BG + 20, 372, 424

    def stripes(p):
        for sx in range(ax0 - 40, ax1 + 40, 56):
            p.poly([(sx, ay0), (sx + 28, ay0), (sx + 32, ay1), (sx + 4, ay1)], (250, 242, 226))
    c.paint(poly([(ax0, ay0), (ax1, ay0), (ax1 + 10, ay1), (ax0 - 18, ay1)]), (150, 30, 50), pattern=stripes,
            shade=(0, -6, (100, 20, 36)))
    for sx in range(ax0 - 18, ax1, 28):
        c.paint(ell(sx + 14, ay1, 14, 9), (150, 30, 50) if (sx // 28) % 2 else (250, 242, 226), ow=2.5)
    bulbs = string_lights(c, [(260, 446), (700, 452), (1160, 446), (1620, 452), (1930, 446)],
                          [(255, 230, 150), (255, 200, 120)], spacing=56, sag=22, seed=64)

    # ---------- floor: terrace tiles
    checker_floor(c, (196, 176, 160), (168, 148, 140), vp=(960, 300), cols=120, rows=7)
    c.paint(rect(-10, WALL_Y - 4, W_BG + 10, WALL_Y + 6), (100, 30, 40), ow=2.5)

    # ---------- specials board (A-frame chalkboard)
    x0, y0, x1, y1 = B["Specials board"]
    c.shadow((x0 + x1) / 2, y1 - 4, 60, 8)
    for lx0, lx1 in ((x0 + 8, x0 + 22), (x1 - 8, x1 - 22)):
        c.line([((lx0 + lx1) / 2 + (6 if lx0 < x0 + 50 else -6), y0 + 10), (lx0, y1 - 4)], 7, (120, 80, 50))
    c.paint(rrect(x0 + 6, y0 + 4, x1 - 6, y1 - 34, 6), (130, 86, 50), shade=(-3, -3, (90, 56, 30)))
    c.paint(rect(x0 + 16, y0 + 14, x1 - 16, y1 - 44), (36, 46, 40), ow=2.5)
    for k, (t, col) in enumerate((("TONIGHT", (255, 240, 200)), ("espresso $9", (250, 250, 240)),
                                  ("double $30", (250, 250, 240)), ("croissant", (250, 250, 240)),
                                  ("SOLD OUT", (255, 120, 120)), ("opinions FREE", (140, 220, 255)))):
        c.text((x0 + x1) / 2, y0 + 30 + k * 17, t, 10 if k else 12, col, "Bold")

    # ---------- planter where Mr. Pemberton sits (his plaque says DO NOT FEED)
    px, py = feet_px("cafe_snoot", "Mr. Pemberton")
    c.shadow(px, WALL_Y + 2, 90, 7)
    c.paint(rect(px - 76, py + 18, px + 76, WALL_Y + 2), ("h", (210, 196, 176), (160, 146, 130)),
            shade=(-5, 0, (140, 126, 110)))
    c.paint(rect(px - 82, py + 10, px + 82, py + 24), (220, 206, 186), ow=3)
    hedge = ell(px - 40, py + 6, 44, 14) + ell(px + 38, py + 6, 44, 14) + ell(px, py + 4, 40, 12)
    c.paint(hedge, (60, 130, 70), shade=(3, 3, (40, 96, 56)), hi=(-2, -3, (110, 180, 100), 2))
    c.paint(rrect(px - 46, py + 34, px + 46, py + 62, 3), (210, 170, 80), ow=2.5, hi=(-1, -1, (250, 220, 140)))
    c.text(px, py + 43, "MR. PEMBERTON", 7.5, (60, 40, 20), "Black")
    c.text(px, py + 54, "DO NOT FEED", 7.5, (140, 30, 30), "Black")

    # ---------- Vivian's tall bistro table (she stands; sitting is for people with nothing to say)
    vx = B["Vivian Quill"][2] + 60
    c.shadow(vx, WALL_Y + 4, 44, 6)
    c.paint(ell(vx, WALL_Y, 30, 7), (50, 50, 56), ow=3)
    c.paint(rect(vx - 4, 652, vx + 4, WALL_Y - 4), (70, 70, 80), ow=2.5, hi=(-1, 0, (130, 130, 140)))
    c.paint(ell(vx, 648, 50, 11), (250, 248, 242), ow=3, shade=(0, -3, (210, 206, 200)))
    c.paint(rect(vx - 40, 626, vx - 2, 644), (240, 236, 222), ow=2,
            pattern=lambda p: [p.line([(vx - 36, 630 + k * 4), (vx - 6, 630 + k * 4)], 1, (90, 90, 100)) for k in range(4)])
    c.paint(poly([(vx + 10, 630), (vx + 28, 630), (vx + 25, 644), (vx + 13, 644)], 1), (255, 255, 255), ow=2.2)
    c.paint(ell(vx + 19, 645, 13, 3), (255, 255, 255), ow=1.8)
    c.paint(ell(vx + 19, 631, 8, 2.5), (90, 50, 30), ow=1.4)
    c.line([(vx + 34, 646), (vx + 46, 634)], 2.5, (200, 40, 50))

    # ---------- newspaper vending box
    x0, y0, x1, y1 = B["Newspaper stand"]
    y1 = WALL_Y + 6
    c.shadow((x0 + x1) / 2, y1, 60, 7)
    c.paint(rect(x0 + 18, y1 - 24, x0 + 26, y1), (60, 70, 90), ow=2.5)
    c.paint(rect(x1 - 26, y1 - 24, x1 - 18, y1), (60, 70, 90), ow=2.5)
    c.paint(rrect(x0 + 6, y0 + 10, x1 - 6, y1 - 22, 6), (50, 90, 170), shade=(-5, -5, (30, 60, 120)),
            hi=(3, 3, (100, 140, 220), 2))
    c.paint(rect(x0 + 16, y0 + 40, x1 - 16, y0 + 100), (250, 248, 236), ow=2.5,
            pattern=lambda p: [p.rect(x0 + 20, y0 + 60, x1 - 20, y0 + 70, (40, 40, 44)),
                               p.rect(x0 + 20, y0 + 76, x0 + 50, y0 + 96, (220, 220, 220)),
                               [p.line([(x0 + 56, y0 + 78 + k * 5), (x1 - 20, y0 + 78 + k * 5)], 1.2, (120, 120, 130))
                                for k in range(4)]])
    c.text((x0 + x1) / 2, y0 + 50, "UPTOWN SNEER", 8.5, (40, 40, 44), "Black")
    c.text((x0 + x1) / 2, y0 + 26, "SNEER", 13, (255, 255, 240), "Display")
    c.paint(rect(x0 + 30, y0 + 112, x1 - 30, y0 + 120), (30, 40, 60), ow=2)

    # ---------- the empty reserved table + two chairs
    x0, y0, x1, y1 = B["Empty table"]
    tx = (x0 + x1) / 2
    c.shadow(tx, WALL_Y + 6, 90, 8)
    for cx_, flip in ((x0 + 18, -1), (x1 - 18, 1)):
        c.line([(cx_, WALL_Y + 2), (cx_ + flip * 4, 730)], 4, (60, 60, 66))
        c.line([(cx_ - flip * 26, WALL_Y + 2), (cx_ - flip * 22, 730)], 4, (60, 60, 66))
        c.paint(ell(cx_ - flip * 12, 728, 26, 6), (150, 30, 50), ow=2.5)
        c.paint(cap([(cx_ + flip * 4, 728), (cx_ + flip * 8, 670)], 5), (60, 60, 66), ow=2)
        c.paint(cap([(cx_ + flip * 8, 672), (cx_ - flip * 20, 668)], 5), (60, 60, 66), ow=2)
    c.paint(ell(tx, WALL_Y + 2, 26, 6), (50, 50, 56), ow=2.5)
    c.paint(rect(tx - 4, 712, tx + 4, WALL_Y), (70, 70, 80), ow=2.5)
    c.paint(ell(tx, 708, 52, 11), (250, 248, 242), ow=3, shade=(0, -3, (210, 206, 200)))
    c.paint(poly([(tx - 18, 704), (tx + 18, 704), (tx + 12, 684), (tx - 12, 684)], 1), (255, 255, 252), ow=2)
    c.text(tx, 694, "RESERVED", 6.5, (120, 30, 46), "Black")

    # ---------- flower boxes under the right window, far-right potted tree
    c.paint(ell(1840, 690, 50, 70), (60, 130, 70), shade=(4, 4, (40, 96, 56)), hi=(-4, -4, (110, 180, 100), 3))
    c.paint(poly([(1806, WALL_Y + 2), (1874, WALL_Y + 2), (1882, 740), (1798, 740)]), (150, 30, 50), ow=3.5,
            shade=(-4, 0, (100, 20, 36)))
    c.line([(1840, 740), (1840, 700)], 5, (90, 60, 40))

    lights = [(x, y, 170, 0.18, col) for (x, y, col) in bulbs[::2]]
    lights += [(390, 580, 300, 0.35, (255, 200, 130)), (925, 580, 380, 0.45, (255, 200, 130)),
               (1485, 580, 300, 0.35, (255, 200, 130)), (ax, 600, 220, 0.35, (255, 200, 130)),
               (100, 560, 200, 0.25, (140, 160, 255)), (960, 940, 600, 0.15, (255, 220, 200))]
    light_pass(c, 0.72, lights, vign=0.38, front=0.22)
    c.glow(970, 328, 260, (255, 200, 120), 0.18)
    c.save("bg_cafe_snoot.png")


# =========================================================================== velour backstage
def paint_velour_backstage():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    B = boxes("velour_backstage")
    rng = random.Random(71)
    block_wall(c, 0, 0, W_BG, WALL_Y, (70, 72, 86), (104, 104, 116), bw=140, bh=64, seed=72)
    # painted stripe + stencilled words
    c.paint(rect(-10, 400, W_BG + 10, 430), (150, 30, 90), ow=0, opacity=0.85)
    c.text(1180, 380, "NO STAGE DIVING IN THE GREEN ROOM", 15, (240, 240, 240), "Black")
    # ceiling pipes and cable trays
    c.paint(rect(-10, 0, W_BG + 10, 70), (40, 40, 48), ow=0)
    for py, pc in ((80, (150, 150, 160)), (108, (190, 90, 60))):
        c.paint(rect(-10, py, W_BG + 10, py + 16), pc, ow=3, hi=(0, 4, lt(pc, 0.35)), shade=(0, -3, dk(pc, 0.7)))
        for bx in range(60, W_BG, 260):
            c.paint(rect(bx, py - 4, bx + 14, py + 20), dk(pc, 0.7), ow=2.5)
    for k in range(5):  # drooping cables
        a = rng.uniform(0, W_BG)
        c.line(bez((a, 128), (a + 80, 200 + rng.uniform(0, 50)), (a + 180, 128)), 3, (30, 30, 34))
    bulbs = string_lights(c, [(220, 160), (720, 150), (1220, 160), (1720, 150), (1930, 160)],
                          [(255, 240, 200)], spacing=70, sag=26, seed=73)
    # gig posters on the wall
    for (gx, gy, col, t) in ((260, 300, (255, 220, 60), "VEX"), (1180, 250, (90, 220, 255), "LOUD"),
                             (1640, 300, (255, 90, 200), "NO"), (1880, 470, (120, 255, 140), "VEX")):
        sub = poster(80, 110, col, lambda p, ox, oy, col=col: p.rect(ox + 8, oy + 40, ox + 72, oy + 96, dk(col, 0.6)))
        sub.text(60, 50, t, 20, (30, 26, 34), "Display")
        c.stamp(sub, gx, gy, angle=rng.uniform(-6, 6))

    # ---------- floor: scuffed concrete with gaffer-tape marks
    c.paint(rect(0, WALL_Y, W_BG, H_BG), ("vy", WALL_Y, H_BG, (86, 80, 88), (50, 46, 54)), ow=0)
    for _ in range(80):
        x, y = rng.uniform(0, W_BG), rng.uniform(WALL_Y + 10, H_BG)
        c.paint(ell(x, y, rng.uniform(4, 16), rng.uniform(1.5, 4)), (30, 26, 34), ow=0, opacity=0.18)
    for (tx, ty) in ((520, 900), (980, 960), (1420, 880), (300, 1010)):
        c.paint(rect(tx - 34, ty - 5, tx + 34, ty + 5), (250, 220, 70), ow=1.5, opacity=0.85)
        c.paint(rect(tx - 5, ty - 30, tx + 5, ty + 30), (250, 220, 70), ow=1.5, opacity=0.85)
    c.paint(rect(-10, WALL_Y - 14, W_BG + 10, WALL_Y + 4), (40, 38, 46), ow=3)

    # ---------- exit door to the club
    x0, y0, x1, y1 = B["Club floor"]
    y1 = WALL_Y
    c.paint(rect(x0 - 12, y0 - 12, x1 + 12, y1 + 2), (30, 28, 36))
    c.paint(rect(x0, y0, x1, y1), ("v", (60, 56, 70), (36, 32, 44)), ow=3.5)
    c.paint(rect(x0 + 16, y0 + 140, x1 - 16, y0 + 156), (150, 150, 160), ow=3, hi=(0, -2, (220, 220, 230)))
    c.paint(rrect(x0 + 12, y0 - 70, x1 - 12, y0 - 26, 6), (20, 30, 24))
    neon_text(c, (x0 + x1) / 2, y0 - 48, "TO CLUB", 20, (255, 90, 200), "Display")
    c.text((x0 + x1) / 2, y0 + 60, "STAGE LEFT", 12, (250, 220, 90), "Black")

    # ---------- dressing table + bulb mirror
    x0, y0, x1, y1 = B["Dressing mirror"]
    y1 = WALL_Y + 6
    wood = (120, 70, 50)
    c.shadow((x0 + x1) / 2, y1, 110, 8)
    c.paint(rect(x0 + 10, y1 - 110, x1 - 10, y1 - 96), lt(wood, 0.15), ow=3, hi=(0, 3, lt(wood, 0.4)))
    c.paint(rect(x0 + 16, y1 - 96, x1 - 16, y1 - 4), wood, shade=(-5, 0, dk(wood, 0.7)),
            pattern=lambda p: [p.rect(x0 + 26, y1 - 86 + k * 30, x1 - 26, y1 - 62 + k * 30, dk(wood, 0.85)) for k in range(3)])
    for k in range(3):
        c.paint(ell((x0 + x1) / 2, y1 - 74 + k * 30, 8, 3), (230, 186, 80), ow=1.8)
    mx0, mx1, my0, my1 = x0 + 26, x1 - 26, y0 + 4, y1 - 116
    c.paint(rect(mx0 - 14, my0 - 14, mx1 + 14, my1 + 6), (40, 36, 44), shade=(-4, -4, (20, 18, 24)))
    c.paint(rect(mx0, my0, mx1, my1), ("v", (170, 190, 210), (110, 120, 150)), ow=3)
    c.paint(poly([(mx0 + 10, my1 - 10), (mx0 + 50, my0 + 6), (mx0 + 70, my0 + 6), (mx0 + 30, my1 - 10)]),
            (255, 255, 255), ow=0, opacity=0.3)
    c.text((mx0 + mx1) / 2, (my0 + my1) / 2 - 6, "YOU ARE NOT", 12, (230, 40, 90), "Italic", angle=-4)
    c.text((mx0 + mx1) / 2, (my0 + my1) / 2 + 14, "BORING - J", 12, (230, 40, 90), "Italic", angle=-4)
    n = 0
    for k in range(7):
        bxp = mx0 - 6 + k * (mx1 - mx0 + 12) / 6
        on = k not in (2, 5)
        c.paint(ell(bxp, my0 - 8, 7, 7), (255, 246, 200) if on else (120, 116, 110), ow=2.2)
    for k in range(4):
        byp = my0 + 12 + k * (my1 - my0 - 10) / 3
        for sx in (mx0 - 8, mx1 + 8):
            c.paint(ell(sx, byp, 7, 7), (255, 246, 200) if (k + int(sx)) % 3 else (120, 116, 110), ow=2.2)
    # makeup + hairspray on the table
    for k, col in enumerate(((230, 60, 120), (80, 230, 110), (40, 40, 46))):
        c.paint(rrect(x0 + 34 + k * 22, y1 - 132, x0 + 48 + k * 22, y1 - 110, 3), col, ow=2)
    c.paint(rrect(x1 - 60, y1 - 160, x1 - 38, y1 - 110, 4), (200, 200, 210), ow=2.5, hi=(-2, 0, (250, 250, 255)))
    c.paint(rect(x1 - 56, y1 - 170, x1 - 42, y1 - 160), (230, 60, 120), ow=2)

    # ---------- costume rack
    x0, y0, x1, y1 = B["Costume rack"]
    y1 = WALL_Y + 6
    c.shadow((x0 + x1) / 2, y1, 100, 8)
    for lx in (x0 + 14, x1 - 14):
        c.paint(rect(lx - 4, y0 + 12, lx + 4, y1 - 16), (170, 170, 180), ow=2.5, hi=(-1, 0, (230, 230, 240)))
        c.paint(ell(lx, y1 - 10, 10, 10), (40, 40, 46), ow=2.5)
    c.paint(rect(x0 + 6, y1 - 30, x1 - 6, y1 - 22), (170, 170, 180), ow=2.5)
    c.paint(rect(x0 + 4, y0 + 8, x1 - 4, y0 + 18), (190, 190, 200), ow=2.5, hi=(0, -2, (240, 240, 250)))
    outfits = [((40, 40, 50), "jacket"), ((230, 60, 120), "dress"), ((30, 30, 34), "cape"), ((200, 30, 50), "plaid"),
               ((80, 230, 110), "tee")]
    w = (x1 - x0 - 30) / len(outfits)
    for k, (col, kind) in enumerate(outfits):
        hx = x0 + 22 + k * w + w / 2
        c.curve((hx - 6, y0 + 10), (hx, y0 - 2), (hx + 6, y0 + 10), 2, (200, 200, 210))
        top = y0 + 24
        bot = top + (150 if kind in ("cape", "dress") else 110)
        sh = poly([(hx - w * 0.5, top + 6), (hx + w * 0.5, top + 6), (hx + w * 0.62, bot), (hx - w * 0.62, bot)], 2)
        pat = None
        if kind == "jacket":
            pat = lambda p, hx=hx: [p.ell(hx - 8 + (j % 3) * 8, top + 20 + (j // 3) * 16, 2, 2, (220, 220, 230)) for j in range(15)]
        elif kind == "plaid":
            pat = lambda p, hx=hx: [p.line([(hx - 30, yy), (hx + 30, yy)], 2.5, (250, 200, 60)) for yy in range(int(top) + 14, int(bot), 18)]
        c.paint(sh, col, pattern=pat, shade=(3, 0, dk(col, 0.7)), hi=(-2, 0, lt(col, 0.3), 1.5))
        if kind == "cape":
            c.text(hx, top + 80, "NO", 16, (255, 255, 255), "Display")

    # ---------- road case behind Grizz
    gx = feet_px("velour_backstage", "Grizz")[0]
    c.paint(rect(gx - 100, 690, gx + 100, WALL_Y + 4), (34, 32, 38), shade=(-5, 0, (18, 16, 22)), hi=(0, 4, (80, 78, 90)))
    for cx_, cy_ in ((gx - 100, 690), (gx + 100, 690), (gx - 100, WALL_Y + 4), (gx + 100, WALL_Y + 4)):
        c.paint(rect(cx_ - 12, cy_ - 12, cx_ + 12, cy_ + 12), (190, 190, 200), ow=2.5)
    c.text(gx, 724, "VEX / FRAGILE", 13, (250, 250, 250), "Black")
    c.paint(rect(gx - 30, 696, gx + 30, 702), (250, 220, 70), ow=0)  # gaffer tape

    # ---------- the croissant's stool + empty glass dome (the croissant itself is a sprite)
    sx, sy = feet_px("velour_backstage", "Rider croissant")
    c.shadow(sx, WALL_Y + 4, 34, 5)
    for lx in (sx - 18, sx + 18):
        c.line([(sx + (lx - sx) * 0.4, sy + 8), (lx, WALL_Y + 2)], 4, (170, 170, 180))
    c.paint(ell(sx, sy + 4, 30, 7), (150, 30, 90), ow=3, hi=(0, -2, (210, 80, 150)))
    c.paint(ell(sx, sy + 1, 28, 5), (240, 240, 236), ow=2.5)  # plate

    # ---------- rider table
    x0, y0, x1, y1 = B["Rider table"]
    y1 = WALL_Y + 6
    c.shadow((x0 + x1) / 2, y1, 120, 8)
    cloth = (40, 40, 48)
    c.paint(poly([(x0 + 4, y0 + 40), (x1 - 4, y0 + 40), (x1 + 4, y1 - 4), (x0 - 4, y1 - 4)], 1), cloth,
            shade=(-5, 0, (24, 24, 30)), pattern=lambda p: [p.line([(xx, y0 + 44), (xx + 4, y1 - 4)], 2, (60, 60, 70))
                                                          for xx in range(int(x0) + 30, int(x1), 40)])
    c.paint(rect(x0, y0 + 32, x1, y0 + 44), (70, 70, 80), ow=3)
    # gummy bowl (green only)
    bx = x0 + 50
    c.paint(poly([(bx - 34, y0 + 6), (bx + 34, y0 + 6), (bx + 24, y0 + 32), (bx - 24, y0 + 32)], 1), (230, 230, 240),
            ow=2.5, hi=(-2, 0, (255, 255, 255)))
    for k in range(9):
        c.paint(ell(bx - 26 + k * 6.5, y0 + 4 - (k % 3) * 3, 5, 6), (80, 230, 110), ow=1.6)
    # boxed espresso machine
    c.paint(rect(x0 + 100, y0 - 40, x0 + 170, y0 + 32), (200, 160, 110), shade=(-4, -4, (160, 120, 80)),
            pattern=lambda p: p.line([(x0 + 100, y0 - 20), (x0 + 170, y0 - 20)], 6, (240, 220, 120)))
    c.text(x0 + 135, y0 + 6, "ESPRESSO", 8, (60, 40, 20), "Black")
    c.text(x0 + 135, y0 + 18, "(unopened)", 7, (60, 40, 20), "Bold")
    # rider card
    c.paint(rect(x1 - 46, y0 + 2, x1 - 10, y0 + 30), (255, 255, 250), ow=2,
            pattern=lambda p: [p.line([(x1 - 42, y0 + 10 + k * 5), (x1 - 14, y0 + 10 + k * 5)], 1, (80, 80, 90)) for k in range(4)])
    c.text(x1 - 28, y0 + 6, "RIDER", 6, (200, 30, 60), "Black")

    # ---------- amp stack
    x0, y0, x1, y1 = B["Amp stack"]
    y1 = WALL_Y + 6
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2 + 14, 8)
    cab_h = (y1 - y0 - 70) / 2
    for k in range(2):
        cy0 = y1 - (k + 1) * cab_h
        c.paint(rect(x0 + 6, cy0, x1 - 6, cy0 + cab_h - 4), (30, 30, 34), shade=(-5, 0, (14, 14, 18)),
                hi=(0, 3, (70, 70, 80)))

        def grille(p, cy0=cy0):
            for yy in range(int(cy0) + 16, int(cy0 + cab_h) - 16, 8):
                p.line([(x0 + 18, yy), (x1 - 18, yy)], 1.5, (60, 56, 66))
        c.paint(rect(x0 + 16, cy0 + 12, x1 - 16, cy0 + cab_h - 16), (44, 40, 50), ow=2.5, pattern=grille)
    hy0 = y0 + 10
    c.paint(rrect(x0 + 2, hy0, x1 - 2, hy0 + 60, 6), (36, 34, 40), shade=(-4, -4, (18, 16, 22)), hi=(3, 3, (90, 86, 100), 2))
    c.paint(rect(x0 + 14, hy0 + 12, x1 - 14, hy0 + 48), (230, 186, 80), ow=2.5)
    for k, lab in enumerate(("LOUD", "LOUDER", "SORRY")):
        kx = x0 + 34 + k * (x1 - x0 - 68) / 2
        c.paint(ell(kx, hy0 + 28, 8, 8), (30, 30, 34), ow=2, hi=(-2, -2, (120, 120, 130)))
        c.text(kx, hy0 + 43, lab, 5.5, (40, 30, 20), "Black")
    c.text((x0 + x1) / 2, y1 - cab_h * 0.5 - 4, "VEX", 18, (240, 240, 240), "Display")

    # ---------- set list taped to the wall
    x0, y0, x1, y1 = B["Set list"]
    rng2 = random.Random(5)

    def setlist(p):
        p.rect(x0, y0, x1, y1, (252, 250, 240))
        for k in range(5):
            yy = y0 + 22 + k * 16
            p.line([(x0 + 10, yy), (x1 - 12 - rng2.uniform(0, 20), yy)], 2, (40, 40, 50))
            p.line([(x0 + 8, yy + 2), (x1 - 10, yy - 2)], 1.6, (220, 40, 60))
        p.line([(x0 + 12, y1 - 18), (x1 - 20, y1 - 22)], 3, (255, 60, 160))
    c.paint(wonky(x0 + 4, y0 + 4, x1 - 4, y1 - 4, 2, rng2), (252, 250, 240), pattern=setlist, shade=(-2, -2, (210, 206, 196)))
    for tx, ty in ((x0 + 10, y0 + 6), (x1 - 10, y0 + 6)):
        c.paint(rect(tx - 10, ty - 5, tx + 10, ty + 5), (40, 40, 44), ow=0, opacity=0.9)
    c.text((x0 + x1) / 2, y0 + 14, "SET", 9, (40, 40, 50), "Black")
    # fire extinguisher, far right
    c.paint(rrect(1856, 600, 1890, 700, 10), (210, 40, 40), shade=(-3, 0, (150, 20, 20)), hi=(2, 0, (255, 120, 110), 2))
    c.paint(rect(1866, 588, 1880, 602), (40, 40, 44), ow=2)

    lights = [(x, y, 200, 0.22, col) for (x, y, col) in bulbs]
    lights += [((B["Dressing mirror"][0] + B["Dressing mirror"][2]) / 2, 600, 260, 0.35, (255, 236, 190)),
               (960, 940, 700, 0.2, (255, 220, 200)), (B["Club floor"][2] - 40, 600, 220, 0.2, (255, 120, 220))]
    light_pass(c, 0.66, lights, vign=0.42, front=0.2)
    c.glow((B["Dressing mirror"][0] + B["Dressing mirror"][2]) / 2, B["Dressing mirror"][1], 120, (255, 240, 200), 0.3)
    c.save("bg_velour_backstage.png")


# =========================================================================== new characters (all face left)
def paint_anton():
    c = Canvas(100, 255, ow=3)
    skin, skin_sh = (250, 214, 186), (214, 160, 140)
    hair, hair_hi = (30, 26, 34), (90, 86, 110)
    white, white_sh = (252, 250, 244), (206, 208, 220)
    blk, blk_sh = (34, 32, 40), (18, 16, 22)
    # far arm: bent, napkin draped over the forearm
    c.paint(cap([(66, 100), (78, 124), (60, 132)], 8.5), white, shade=(3, 2, white_sh))
    # legs: black trousers, one heel turned in (very correct posture)
    c.paint(cap([(58, 150), (60, 196), (62, 236)], 11.5), blk, shade=(3, 0, blk_sh))
    c.paint(cap([(44, 150), (42, 196), (42, 238)], 12), blk, shade=(3, 0, blk_sh), hi=(-2, 0, (80, 76, 96)))
    c.line([(44, 156), (42, 236)], 1.2, (90, 86, 104))
    for xh, xt, yt, yb in ((72, 42, 236, 247), (52, 14, 238, 251)):
        c.paint(shoe_shape(xh, xt, yt, yb, pointy=True), blk, shade=(2, -2, blk_sh), hi=(-1, 1.5, (110, 106, 124), 1))
    # white waiter's jacket, short, double row of buttons
    jacket = poly([(36, 94), (54, 89), (70, 94), (74, 120), (72, 152), (34, 152), (34, 122)], 2)
    c.paint(jacket, white, shade=(4, 2, white_sh), hi=(-2, 2, (255, 255, 255), 1.5))
    for k in range(3):
        c.paint(ell(46, 112 + k * 12, 2, 2), (230, 186, 80), ow=1.2)
        c.paint(ell(60, 112 + k * 12, 2, 2), (230, 186, 80), ow=1.2)
    c.paint(rect(34, 146, 72, 154), blk, ow=2)  # sash/belt
    # neck, collar, bow tie
    c.paint(cap([(53, 74), (53, 92)], 8.5), skin, shade=(3, 0, skin_sh))
    c.paint(poly([(42, 92), (53, 98), (64, 92), (60, 86), (53, 92), (46, 86)], 1), white, ow=2)
    c.paint(poly([(44, 90), (53, 94), (44, 99)], 1) + poly([(62, 90), (53, 94), (62, 99)], 1), blk, ow=1.8)
    c.paint(ell(53, 94, 2.4, 2.4), blk, ow=1.2)
    # near arm: straight down, tray hand held up with nothing on it... no: hand flat by the hip, very stiff
    c.paint(cap([(38, 98), (32, 124), (34, 140)], 8.5), white, shade=(3, 2, white_sh))
    c.paint(ell(34, 144, 5, 5.5), skin, shade=(2, 2, skin_sh))
    # napkin over far forearm, hanging
    c.paint(poly([(62, 124), (80, 122), (82, 150), (76, 146), (70, 152), (64, 146)], 1), white, ow=2.2,
            shade=(2, 0, white_sh))
    # ---- head: long, nose up, slicked hair, pencil moustache
    head = ell(55, 46, 21, 24) + poly([(35, 50), (36, 68), (46, 77), (58, 75), (70, 60)], 2) + \
        poly([(36, 44), (25, 40), (34, 52)], 1)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, (255, 236, 220), 2))
    c.paint(ell(73, 49, 5, 7.5), skin, shade=(2, 2, skin_sh))
    # half-closed disdainful eyes
    eye(c, 47, 44, 6, 7.5, 44, 46, 2.0, lid=0.55, lid_tilt=-0.5, skin=skin)
    eye(c, 35, 44, 4.4, 7, 33, 46, 1.8, lid=0.55, lid_tilt=0.5, skin=skin)
    c.line([(41, 35), (47, 33), (53, 35)], 2.0, hair)
    c.line([(31, 37), (36, 36)], 1.8, hair)
    c.line([(28, 58), (34, 56), (40, 58)], 2.2, hair)  # pencil moustache
    c.curve((32, 64), (36, 66), (40, 63), 1.5)          # tight little frown
    # slicked hair with a perfect parting
    c.paint(poly([(34, 34), (38, 22), (54, 16), (72, 20), (78, 36), (76, 52), (72, 40), (56, 30), (42, 30)], 2, True),
            hair, shade=(3, 2, (14, 12, 18)), hi=(-2, 2, hair_hi, 1.5))
    c.curve((44, 22), (56, 18), (68, 22), 1.2, hair_hi)
    c.fit(margin=3)
    c.save("hs_anton.png")


def paint_vivian_quill():
    c = Canvas(105, 255, ow=3)
    skin, skin_sh = (242, 214, 196), (206, 160, 150)
    hair, hair_sh, hair_hi = (226, 226, 236), (170, 170, 188), (255, 255, 255)
    blk, blk_sh, blk_hi = (34, 30, 42), (16, 14, 22), (88, 82, 104)
    red = (200, 30, 50)
    # long black coat-dress
    coat = poly([(38, 92), (56, 88), (72, 94), (78, 140), (86, 226), (30, 228), (34, 150), (34, 112)], 2)
    c.paint(coat, blk, shade=(4, 2, blk_sh), hi=(-2, 2, blk_hi, 1.5))
    c.line([(52, 120), (48, 226)], 1.4, blk_hi)
    # boots peeking out
    for xh, xt, yt, yb in ((76, 48, 232, 246), (54, 20, 234, 249)):
        c.paint(shoe_shape(xh, xt, yt, yb, pointy=True), (60, 20, 30), shade=(2, -2, (30, 10, 16)),
                hi=(-1, 1.5, (130, 60, 70), 1))
    c.paint(rect(30, 222, 86, 236), blk, ow=2.4)
    # red silk scarf
    c.paint(poly([(42, 90), (66, 90), (62, 100), (50, 104), (44, 98)], 1), red, ow=2.2, shade=(2, 1, dk(red, 0.7)))
    c.paint(poly([(52, 100), (60, 100), (62, 140), (52, 136)], 1), red, ow=2.2, shade=(2, 0, dk(red, 0.7)))
    # neck
    c.paint(cap([(54, 74), (54, 90)], 8), skin, shade=(3, 0, skin_sh))
    # far arm: holding a notebook up against the chest
    c.paint(cap([(70, 100), (76, 126), (56, 128)], 8), blk, shade=(3, 2, blk_sh))
    c.paint(poly([(30, 110), (56, 106), (60, 140), (34, 144)], 1), (250, 246, 230), ow=2.5,
            pattern=lambda p: [p.line([(36, 116 + k * 6), (54, 113 + k * 6)], 1.1, (110, 110, 130)) for k in range(5)],
            shade=(-2, -2, (210, 204, 190)))
    c.paint(ell(56, 127, 5, 4.5), skin, shade=(2, 2, skin_sh))
    # near arm: hand raised holding a pen like a dagger
    c.paint(cap([(38, 98), (26, 118), (20, 102)], 8), blk, shade=(3, 2, blk_sh), hi=(-1, 1, blk_hi, 1))
    c.paint(ell(20, 99, 5, 5.5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(18, 102), (12, 76)], 2.6), red, ow=1.6)
    c.paint(cap([(12, 78), (11, 72)], 1.6), (230, 186, 80), ow=1)
    # ---- head: sharp, older, silver bob, big glasses on a chain
    head = ell(56, 48, 21, 24) + poly([(36, 52), (38, 70), (48, 78), (60, 76), (72, 62)], 2) + ell(34, 56, 4.5, 4.5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, (255, 236, 224), 2))
    c.line([(44, 66), (48, 70)], 1.1, skin_sh)  # laugh line (never used)
    c.curve((35, 59), (32, 60), (32, 56), 1.3)
    eye(c, 47, 46, 6.2, 7.6, 43.5, 47, 2.1, lid=0.25, lid_tilt=-0.3, skin=skin, iris=(90, 110, 140))
    eye(c, 35.5, 46, 4.4, 7, 33, 47, 1.8, lid=0.25, lid_tilt=0.3, skin=skin, iris=(90, 110, 140))
    for gx, gy, r in ((47, 46, 9.5), (35, 46, 7)):
        c.paint(ell(gx, gy, r, r * 0.92), (0, 0, 0, 0), ow=2.4)
    c.line([(41.5, 45), (42.2, 45)], 2.2)
    c.line([(56.5, 45), (70, 48)], 1.8)
    c.curve((70, 48), (76, 74), (64, 92), 1.0, (230, 186, 80))  # glasses chain
    c.line([(40, 34), (47, 31), (55, 34)], 2.2, hair_sh)  # one brow arched
    c.line([(30, 37), (37, 36)], 2.0, hair_sh)
    c.line([(37, 68), (44, 67.5)], 1.8, (150, 40, 60))   # thin red unimpressed mouth
    # silver bob with a sharp fringe, two pens behind the ear
    c.paint(cap([(66, 34), (82, 20)], 2.4), (40, 90, 200), ow=1.4)
    c.paint(cap([(70, 36), (86, 30)], 2.4), (40, 160, 90), ow=1.4)
    c.paint(poly([(34, 36), (40, 22), (56, 16), (74, 20), (82, 34), (82, 62), (76, 72), (72, 60), (72, 44), (60, 34),
                  (46, 36), (38, 40)], 2, True), hair, shade=(3, 2, hair_sh), hi=(-2, 2, hair_hi, 1.5))
    c.line([(36, 38), (60, 34)], 1.5, hair_sh)
    c.fit(margin=3)
    c.save("hs_vivian_quill.png")


def paint_mr_pemberton():
    c = Canvas(84, 70, ow=3)
    grey, grey_sh, grey_hi = (150, 150, 170), (104, 104, 128), (196, 196, 214)
    # tail
    c.paint(poly([(60, 40), (82, 36), (80, 50), (60, 52)], 1), dk(grey, 0.8), shade=(2, 2, grey_sh))
    c.line([(66, 40), (78, 40)], 1.2, (60, 60, 80))
    # legs
    for lx in (36, 46):
        c.line([(lx, 54), (lx - 1, 64)], 2.6, (230, 110, 110))
        c.line([(lx - 6, 65), (lx + 4, 65)], 2.4, (230, 110, 110))
    # plump body
    body = ell(46, 42, 24, 16)
    c.paint(body, grey, shade=(3, 3, grey_sh), hi=(-2, -2, grey_hi, 1.5))
    # wing with dark bars
    c.paint(ell(54, 40, 15, 10, -8), grey_hi, shade=(2, 2, grey_sh),
            pattern=lambda p: [p.line([(50, 36 + k * 6), (64, 34 + k * 6)], 2, (70, 70, 90)) for k in range(2)])
    # puffed iridescent neck (the "cravat")
    c.paint(ell(32, 32, 13, 13), (90, 140, 120), shade=(2, 2, (60, 90, 110)),
            pattern=lambda p: [p.ell(30, 36, 9, 6, (150, 90, 170)), p.ell(28, 30, 5, 3, (120, 200, 160))])
    # head
    c.paint(ell(28, 18, 10, 9.5), grey, shade=(2, 2, grey_sh), hi=(-1, -1, grey_hi, 1))
    c.paint(poly([(19, 17), (10, 20), (19, 22)], 1), (60, 50, 50), ow=2)  # beak
    c.paint(ell(19.5, 16, 2.6, 2), (250, 250, 250), ow=1.2)               # cere
    # one smug half-lidded eye
    eye(c, 26, 15, 4.2, 4.2, 24.5, 15.5, 1.6, lid=0.5, lid_tilt=0.6, skin=grey, iris=(240, 120, 40), ow=1.6)
    c.fit(margin=2)
    c.save("hs_mr_pemberton.png")


def paint_grizz():
    c = Canvas(145, 270, ow=3)
    skin, skin_sh, skin_hi = (232, 180, 150), (190, 130, 110), (250, 210, 186)
    beard, beard_sh, beard_hi = (140, 76, 40), (100, 50, 26), (190, 120, 70)
    tee, tee_sh = (36, 34, 42), (18, 16, 22)
    jeans, jeans_sh = (60, 80, 130), (40, 56, 96)
    # legs: big work jeans + boots
    c.paint(cap([(86, 176), (90, 218), (92, 244)], 21), jeans, shade=(3, 0, jeans_sh))
    c.paint(cap([(58, 176), (54, 218), (52, 244)], 22), jeans, shade=(3, 0, jeans_sh), hi=(-2, 0, lt(jeans, 0.3)))
    for xh, xt, yt, yb in ((108, 74, 246, 264), (72, 28, 248, 268)):
        c.paint(shoe_shape(xh, xt, yt, yb, toe_h=0.6), (110, 70, 40), shade=(2, -2, (70, 44, 24)),
                hi=(-1, 2, (170, 120, 80), 1.2))
        c.line([(xt + 4, yb - 3), (xh, yb - 3)], 1.6, (50, 30, 20))
    # tool belt with a roll of gaffer tape and a torch
    c.paint(rect(40, 164, 106, 178), (120, 80, 40), ow=2.4, hi=(0, -2, (170, 120, 70)))
    c.paint(ell(98, 182, 11, 11), (250, 220, 70), ow=2.4, pattern=lambda p: p.ell(98, 182, 4.5, 4.5, (60, 50, 30)))
    c.paint(rrect(42, 172, 52, 200, 3), (60, 60, 66), ow=2.2)
    # big belly, band tee
    torso = poly([(30, 96), (60, 86), (96, 88), (114, 104), (116, 150), (108, 172), (38, 172), (28, 140)], 2)
    c.paint(torso, tee, shade=(5, 2, tee_sh), hi=(-3, 3, (80, 76, 96), 2))
    c.text(88, 150, "CREW", 11, (90, 236, 110), "Black")
    c.text(88, 162, "1994-NOW", 6, (240, 240, 240), "Black")
    # neck
    c.paint(poly([(54, 72), (84, 72), (88, 92), (50, 92)], 1), skin, shade=(4, 0, skin_sh))
    # arms forward, hands together at the chest, holding a little pink half-scarf (knitting with no needles)
    c.paint(cap([(108, 102), (114, 130), (84, 128)], 16), skin, shade=(3, 2, skin_sh))
    c.paint(cap([(106, 100), (112, 112)], 20), tee, shade=(3, 2, tee_sh))
    c.paint(cap([(34, 102), (28, 126), (62, 124)], 17), skin, shade=(3, 2, skin_sh), hi=(-2, -2, skin_hi, 1.5))
    c.paint(cap([(36, 100), (30, 114)], 21), tee, shade=(3, 2, tee_sh))
    c.paint(ell(64, 120, 9, 8), skin, shade=(2, 2, skin_sh))
    c.paint(ell(84, 120, 9, 8), skin, shade=(2, 2, skin_sh))
    c.line([(28, 118), (32, 124)], 1.2, skin_sh)
    # the half-knitted pink scarf hanging from his hands
    scarf = poly([(62, 116), (78, 116), (50, 176), (34, 170)], 1)
    c.paint(scarf, (255, 140, 190), shade=(2, 2, (220, 90, 150)),
            pattern=lambda p: [p.line([(30, yy + 40), (90, yy)], 1.4, (230, 100, 160)) for yy in range(90, 170, 7)])
    for k in range(4):
        c.line([(36 + k * 4, 172 + k * 0.6), (35 + k * 4, 180)], 1.6, (255, 140, 190))
    # tattoo on the near forearm
    c.paint(rect(36, 116, 50, 124), (60, 90, 180), ow=1.2, opacity=0.7)
    # ---- head: beanie, big bushy beard, kind eyes
    head = ell(68, 46, 24, 25) + ell(43, 56, 5, 5.5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 3, skin_hi, 2))
    c.paint(ell(90, 50, 6, 8.5), skin, shade=(2, 2, skin_sh))
    bd = poly([(42, 56), (48, 76), (58, 96), (76, 100), (92, 86), (94, 60), (86, 62), (76, 70), (58, 70), (48, 60)], 2, True)
    c.paint(bd, beard, shade=(3, 3, beard_sh), hi=(-2, 2, beard_hi, 1.5),
            pattern=lambda p: [p.line([(52 + k * 6, 72), (54 + k * 6, 94)], 1.2, beard_sh) for k in range(6)])
    c.paint(ell(52, 66, 9, 4), beard, ow=2, shade=(1, 1, beard_sh))  # moustache
    c.curve((42, 58), (39, 60), (39, 55), 1.4)
    eye(c, 56, 48, 6, 7, 52.5, 49.5, 2.2, lid=0.3, lid_tilt=0.4, skin=skin, iris=(90, 140, 90))
    eye(c, 44, 48, 4.4, 6.4, 41.5, 49.5, 1.9, lid=0.3, lid_tilt=-0.4, skin=skin, iris=(90, 140, 90))
    c.line([(49, 38), (56, 36), (63, 39)], 2.8, beard_sh)  # soft worried brows
    c.line([(38, 40), (44, 38)], 2.5, beard_sh)
    # beanie
    bean = (230, 120, 40)
    c.paint(ell(68, 30, 27, 18) + rect(41, 28, 95, 38), bean, shade=(3, 2, dk(bean, 0.72)), hi=(-2, -2, lt(bean, 0.35), 2),
            pattern=lambda p: [p.line([(xx, 16), (xx, 40)], 1.6, dk(bean, 0.82)) for xx in range(46, 94, 6)])
    c.paint(rrect(39, 32, 97, 42, 4), dk(bean, 0.85), ow=2.4)
    c.fit(margin=3)
    c.save("hs_grizz.png")


def paint_rider_croissant():
    """The croissant on its little stool backstage, under a glass dome: vanishes once Grizz hands it over."""
    c = Canvas(70, 64, ow=3)
    gold, gold_sh, gold_hi = (226, 160, 70), (180, 110, 44), (252, 210, 130)
    dome = ell(35, 36, 30, 28)
    c.paint(dome, (210, 236, 255), ow=0, opacity=0.22, clip=rect(0, 0, 70, 60))
    cro = ell(35, 50, 20, 9, -4) + ell(16, 52, 7, 6, 30) + ell(54, 51, 7, 6, -30)
    c.paint(cro, gold, shade=(2, 2, gold_sh), hi=(-2, -2, gold_hi, 1.5),
            pattern=lambda p: [p.line([(22 + k * 8, 44), (26 + k * 8, 58)], 1.6, gold_sh) for k in range(4)])
    # glass dome outline + glints, drawn over the croissant
    arc = [(35 + 30 * math.cos(math.radians(a)), 36 + 28 * math.sin(math.radians(a))) for a in range(180, 361, 6)]
    arc = [(x, min(y, 60)) for x, y in arc]
    c.line([(5, 60)] + arc + [(65, 60)], 2.4, (130, 150, 186))
    c.paint(ell(35, 8, 4, 3), (200, 210, 230), ow=1.8)
    c.paint(poly([(14, 34), (18, 20), (22, 20), (18, 36)]), (255, 255, 255), ow=0, opacity=0.7)
    c.line([(3, 60), (67, 60)], 2.4, (130, 150, 186))
    c.fit(margin=2)
    c.save("hs_rider_croissant.png")


# =========================================================================== new inventory icons
def paint_icon_mime_beret():
    def draw(c):
        red = (210, 36, 60)
        c.paint(ell(64, 70, 50, 26, -6), red, shade=(4, 4, dk(red, 0.7)), hi=(-3, -4, lt(red, 0.4), 3))
        c.paint(cap([(24, 82), (104, 74)], 9), dk(red, 0.75), ow=3)
        c.paint(cap([(64, 46), (68, 30)], 5), red, ow=3)
        for k in range(3):
            c.line([(40 + k * 22, 60), (48 + k * 22, 74)], 1.5, dk(red, 0.82))
    icon("icon_mime_beret.png", -8, draw)


def paint_icon_paint_smock():
    def draw(c):
        blk, blk_sh = (40, 38, 46), (20, 18, 24)
        sm = poly([(40, 16), (88, 16), (98, 30), (120, 52), (106, 64), (96, 54), (98, 118), (30, 118), (32, 54), (22, 64),
                   (8, 52), (30, 30)], 1)
        rng = random.Random(9)

        def splat(p):
            for _ in range(22):
                col = rng.choice([(255, 60, 160), (80, 230, 110), (255, 220, 60), (80, 160, 255), (250, 250, 240)])
                p.ell(rng.uniform(24, 104), rng.uniform(26, 114), rng.uniform(2, 6), rng.uniform(2, 5), col)
        c.paint(sm, blk, pattern=splat, shade=(4, 3, blk_sh), hi=(-3, -2, (100, 96, 110), 2))
        c.paint(poly([(48, 16), (64, 36), (80, 16)], 1), (250, 240, 220), ow=3)
        c.paint(rect(46, 78, 82, 100), dk(blk, 0.8), ow=2.5)  # pocket
    icon("icon_paint_smock.png", 4, draw)


def paint_icon_artiste_outfit():
    def draw(c):
        blk, blk_sh = (40, 38, 46), (20, 18, 24)
        sm = poly([(40, 44), (88, 44), (98, 56), (118, 74), (106, 84), (96, 76), (98, 122), (30, 122), (32, 76), (22, 84),
                   (10, 74), (30, 56)], 1)
        rng = random.Random(4)
        c.paint(sm, blk, shade=(4, 3, blk_sh), hi=(-3, -2, (100, 96, 110), 2),
                pattern=lambda p: [p.ell(rng.uniform(26, 102), rng.uniform(52, 118), rng.uniform(2, 6), rng.uniform(2, 4),
                                         rng.choice([(255, 60, 160), (80, 230, 110), (255, 220, 60)])) for _ in range(16)])
        red = (210, 36, 60)
        c.paint(ell(66, 34, 40, 18, -10), red, shade=(3, 3, dk(red, 0.7)), hi=(-2, -3, lt(red, 0.4), 2))
        c.paint(cap([(30, 44), (100, 34)], 7), dk(red, 0.75), ow=3)
        c.paint(cap([(66, 16), (70, 6)], 4), red, ow=2.5)
    icon("icon_artiste_outfit.png", 0, draw)


def paint_icon_grizz_needles():
    def draw(c):
        blue, blue_sh = (70, 120, 220), (40, 80, 170)
        c.paint(ell(46, 80, 30, 28), blue, shade=(4, 4, blue_sh), hi=(-3, -3, (140, 180, 250), 2),
                pattern=lambda p: [p.line(bez((20 + k * 9, 60), (46, 80 + k * 2), (24 + k * 10, 104)), 1.6, blue_sh)
                                   for k in range(6)])
        c.curve((70, 92), (96, 110), (112, 96), 3, blue)
        for (ax, ay, bx, by) in ((54, 116, 116, 14), (40, 112, 104, 10)):
            c.paint(cap([(ax, ay), (bx, by)], 5.5), (210, 170, 100), shade=(1, 1, (160, 120, 60)), hi=(-1, -1, (250, 220, 160), 1))
            c.paint(ell(bx + (bx - ax) * 0.02, by - 2, 6, 6), (240, 196, 80), ow=2.5)
    icon("icon_grizz_needles.png", 0, draw)


def paint_icon_rider_croissant():
    def draw(c):
        gold, gold_sh, gold_hi = (226, 160, 70), (180, 110, 44), (252, 210, 130)
        cro = ell(64, 66, 40, 22, -6) + ell(24, 74, 16, 13, 30) + ell(104, 70, 16, 13, -30)
        c.paint(cro, gold, shade=(4, 4, gold_sh), hi=(-3, -4, gold_hi, 3),
                pattern=lambda p: [p.line([(38 + k * 14, 48), (44 + k * 14, 86)], 3, gold_sh) for k in range(5)])
        for k in range(3):
            c.paint(ell(46 + k * 18, 56, 4, 2), (255, 236, 190), ow=0, opacity=0.8)
    icon("icon_rider_croissant.png", -6, draw)


def paint_icon_rave_review():
    def draw(c):
        rng = random.Random(12)

        def scrawl(p):
            p.rect(0, 0, 128, 128, (252, 250, 240))
            for k in range(4):
                y = 66 + k * 12
                p.line([(24, y), (104 - rng.uniform(0, 20), y)], 2, (60, 60, 80))
        c.paint(wonky(12, 12, 116, 116, 3, rng), (252, 250, 240), pattern=scrawl, shade=(-3, -3, (214, 210, 196)))
        for x in range(24, 108, 12):
            c.line([(x, 112), (x + 6, 118)], 1.4, (214, 210, 196))
        c.text(64, 28, "SOMETHING,", 13, (200, 30, 50), "Black")
        c.text(64, 44, "FINALLY.", 13, (200, 30, 50), "Black")
        for k in range(5):
            sx, sy, r = 28 + k * 18, 58, 7
            pts = [(sx + (r if j % 2 == 0 else r * 0.45) * math.cos(math.radians(-90 + j * 36)),
                    sy + (r if j % 2 == 0 else r * 0.45) * math.sin(math.radians(-90 + j * 36))) for j in range(10)]
            c.paint(poly(pts), (255, 210, 50), ow=2, opacity=1.0 if k < 4 else 0.85)
    icon("icon_rave_review.png", -8, draw)


ASSETS_EXPANSION = {"bg_cafe_snoot": paint_cafe_snoot, "bg_velour_backstage": paint_velour_backstage,
                    "hs_anton": paint_anton, "hs_vivian_quill": paint_vivian_quill,
                    "hs_mr_pemberton": paint_mr_pemberton, "hs_grizz": paint_grizz,
                    "hs_rider_croissant": paint_rider_croissant,
                    "icon_mime_beret": paint_icon_mime_beret, "icon_paint_smock": paint_icon_paint_smock,
                    "icon_artiste_outfit": paint_icon_artiste_outfit, "icon_grizz_needles": paint_icon_grizz_needles,
                    "icon_rider_croissant": paint_icon_rider_croissant, "icon_rave_review": paint_icon_rave_review}


# =========================================================================== registry
ASSETS = {"bg_uptown": paint_uptown, "bg_art_gallery": paint_art_gallery, "bg_nightclub": paint_nightclub,
          "hs_mimi": paint_mimi, "hs_jett_vex": paint_jett_vex, "hs_brutus": paint_brutus, "hs_pierre": paint_pierre,
          "hs_blank_canvas": paint_blank_canvas, "hs_something_no_1": paint_something_no_1,
          "icon_vip_pass": paint_icon_vip_pass, "icon_blank_canvas": paint_icon_blank_canvas,
          "icon_paint_set": paint_icon_paint_set, "icon_jett_canvas": paint_icon_jett_canvas,
          "icon_invisible_key": paint_icon_invisible_key, "icon_white_glove": paint_icon_white_glove,
          "icon_guitar_pick": paint_icon_guitar_pick}
ASSETS.update(ASSETS_EXPANSION)


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
