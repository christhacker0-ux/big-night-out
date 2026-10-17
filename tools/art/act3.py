#!/usr/bin/env python3
"""
Big Night Out -- Act 3 "Lab Rats" art (Science Hall, Lab 3B, rooftop).

Original art, drawn procedurally with the helpers in paint.py (same style: bold dark outlines,
warm saturated cel shading, big-headed characters). Prop positions are read from
Assets/_Project/World/act3.json so the painted props sit exactly inside their hotspot boxes.

Usage:  python3 tools/art/act3.py            # paint everything
        python3 tools/art/act3.py lab mina   # paint assets whose name contains these words
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, W_BG, H_BG, WALL_Y, Canvas, mix, dk, lt, poly, ell, rect, rrect, wonky, cap, bez,  # noqa: E402
                   block_wall, baseboard, drop_ceiling, checker_floor, door, fire_door, light_pass, eye, icon,
                   shoe_shape)
from PIL import Image, ImageOps  # noqa: E402

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "act3.json")


def boxes(room_id):
    """Hotspot name -> pixel box (x0, y0, x1, y1) and feet pixel (fx, fy)."""
    data = json.load(open(WORLD))
    out = {}
    for r in data["rooms"]:
        if r["id"] != room_id:
            continue
        for h in r["hotspots"]:
            fx, fy = h["feet"]
            sx, sy = h["size"]
            x0 = (fx - sx / 2 + 9.6) * 100
            x1 = (fx + sx / 2 + 9.6) * 100
            y1 = (5.4 - fy) * 100
            y0 = (5.4 - fy - sy) * 100
            out[h["name"]] = (x0, y0, x1, y1)
    return out


def ceiling_glows(c, xs, y=60):
    for cx in xs:
        c.glow(cx, y, 140, (240, 250, 255), 0.45)


# =========================================================================== shared little things
def hamster(c, cx, cy, s=1.0, sleepy=False, cheeks=True):
    """Golden hamster sitting up, facing RIGHT. (cx, cy) = bottom centre (feet)."""
    fur, fur_sh, belly = (236, 160, 70), (196, 112, 50), (255, 236, 200)

    def T(x, y):
        return (cx + x * s, cy + y * s)
    body = poly([T(-26, 0), T(-30, -18), T(-24, -38), T(-6, -48), T(14, -44), T(26, -28), T(24, -8), T(14, 0)], 2, True)
    c.paint(body, fur, shade=(-3 * s, 2 * s, fur_sh), hi=(3 * s, 3 * s, (255, 200, 120), 2 * s),
            pattern=lambda p: p.ell(cx + 6 * s, cy - 16 * s, 14 * s, 15 * s, belly))
    # ears
    for ex, ey in ((-8, -60), (10, -60)):
        c.paint(ell(*T(ex, ey), 6 * s, 6.5 * s), fur, shade=(-1.5 * s, 1, fur_sh),
                pattern=lambda p, ex=ex, ey=ey: p.ell(cx + ex * s, cy + (ey + 1) * s, 3.2 * s, 3.5 * s, (255, 150, 160)))
    head = ell(*T(4, -50), 20 * s, 16 * s)
    if cheeks:
        head = head + ell(*T(16, -42), 10 * s, 9 * s) + ell(*T(-8, -42), 9 * s, 8 * s)
    c.paint(head, fur, shade=(-3 * s, 2 * s, fur_sh), hi=(2 * s, 3 * s, (255, 200, 120), 1.5 * s),
            pattern=lambda p: p.ell(cx + 14 * s, cy - 44 * s, 10 * s, 7 * s, belly))
    # eyes + nose + whiskers
    for ex in (2, 16):
        if sleepy:
            c.curve(T(ex - 3, -54), T(ex, -51), T(ex + 3, -54), 1.6 * s ** 0.5)
        else:
            c.paint(ell(*T(ex, -54), 2.6 * s, 3 * s), (24, 16, 14), ow=0)
            c.paint(ell(*T(ex - 0.8, -55.2), 1 * s, 1 * s), (255, 255, 255), ow=0)
    c.paint(ell(*T(24, -48), 2.4 * s, 1.8 * s), (230, 90, 110), ow=1.2 * s ** 0.5)
    for k in (-1, 1):
        c.line([T(26, -46 + k * 1.5), T(34, -48 + k * 4)], 0.8 * s ** 0.5, OUT)
    c.curve(T(18, -43), T(21, -40), T(24, -43), 1.2 * s ** 0.5)
    # paws
    for px in (4, 14):
        c.paint(ell(*T(px, -26), 3.5 * s, 3 * s), (255, 200, 180), ow=1.6 * s ** 0.5)
    for px in (-14, 8):
        c.paint(ell(*T(px, -1), 6 * s, 3 * s), (255, 190, 170), ow=1.8 * s ** 0.5)


def seed(c, x, y, ang, s=1.0):
    """Striped sunflower seed."""
    sh = ell(x, y, 7 * s, 4 * s, ang)
    c.paint(sh, (40, 36, 44), ow=2 * s ** 0.5,
            pattern=lambda p: [p.line([(x + math.cos(math.radians(ang)) * -6 * s + math.sin(math.radians(ang)) * k * s,
                                        y + math.sin(math.radians(ang)) * -6 * s - math.cos(math.radians(ang)) * k * s),
                                       (x + math.cos(math.radians(ang)) * 6 * s + math.sin(math.radians(ang)) * k * s,
                                        y + math.sin(math.radians(ang)) * 6 * s - math.cos(math.radians(ang)) * k * s)],
                                      0.9 * s, (236, 232, 220)) for k in (-1.8, 0, 1.8)])


def cardboard_tube(c, x0, y0, x1, y1, r, interior=(70, 44, 30), col=(204, 150, 96)):
    """Horizontal tube from (x0,y0) to (x1,y1) with radius r; open end at (x1, y1)."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    body = cap([(x0, y0), (x1, y1)], 2 * r)
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))

    def seams(p):
        for k in range(-3, 6):
            t = k / 4
            ax, ay = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            p.line([(ax - nx * r * 1.1, ay - ny * r * 1.1), (ax + (x1 - x0) * 0.18 + nx * r * 1.1,
                                                               ay + (y1 - y0) * 0.18 + ny * r * 1.1)], 1.6, dk(col, 0.8))
    c.paint(body, col, shade=(nx * 4, ny * 4, dk(col, 0.78)), hi=(-nx * 3, -ny * 3, lt(col, 0.35), 2), pattern=seams)
    c.paint(ell(x1, y1, r * 0.42, r, ang), lt(col, 0.2), ow=3)
    c.paint(ell(x1 + math.cos(math.radians(ang)) * 1, y1, r * 0.3, r * 0.8, ang), interior, ow=0)


def goggles(c, cx, cy, s=1.0, rot=0, col=(255, 128, 36)):
    def T(pts):
        return paint.rot_pts([(cx + x * s, cy + y * s) for x, y in pts], rot, cx, cy)
    c.paint(cap(T([(-46, 2), (-30, -2)]), 7 * s), (60, 60, 70), ow=2.5)
    c.paint(cap(T([(30, -2), (46, 2)]), 7 * s), (60, 60, 70), ow=2.5)
    frame = poly(T([(-34, -16), (-4, -14), (0, -8), (4, -14), (34, -16), (38, 0), (32, 16), (8, 16), (0, 8),
                    (-8, 16), (-32, 16), (-38, 0)]), 2)
    c.paint(frame, col, shade=(0, 3 * s, dk(col, 0.7)), hi=(0, -2 * s, lt(col, 0.4), 1.5 * s))
    for lx in (-18, 18):
        lens = ell(*T([(lx, 1)])[0], 13 * s, 10 * s, rot)
        c.paint(lens, (150, 220, 240), ow=2.5, hi=(3 * s, 3 * s, (230, 250, 255), 2 * s), shade=(-2, -2, (100, 170, 200)))
    for vx in (-26, 26):
        c.paint(ell(*T([(vx, -11)])[0], 2 * s, 2 * s), dk(col, 0.6), ow=0)


# =========================================================================== Science Hall
def paint_science_hall():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(303)
    B = boxes("science_hall")
    upper = (238, 182, 84)
    c.paint(rect(0, 0, W_BG, 560), ("vy", 120, 560, (220, 150, 70), upper), ow=0)
    for x in range(0, W_BG, 44):
        c.line([(x + rng.uniform(-4, 4), 130), (x + rng.uniform(-4, 4), 556)], 6, (255, 225, 160), opacity=0.06)
    lower = (52, 140, 150)
    block_wall(c, 0, 560, W_BG, WALL_Y, lower, dk(lower, 0.9), bw=60, bh=40, mortar=0.28, seed=31)
    c.paint(rect(-10, 552, W_BG + 10, 570), (196, 80, 60), ow=3, hi=(0, 4, (236, 130, 96)), shade=(0, -4))
    drop_ceiling(c, 130, (214, 206, 186), panels=(330, 960, 1590))
    checker_floor(c, (232, 214, 176), (98, 126, 160), cols=120, rows=7)
    baseboard(c, color=(60, 44, 52))

    # hanging SCIENCE HALL banner
    c.line([(760, 130), (780, 160)], 3, (70, 70, 80))
    c.line([(1160, 130), (1140, 160)], 3, (70, 70, 80))
    c.paint(wonky(740, 158, 1180, 232, 2, rng), (40, 70, 140), shade=(-5, -5, (26, 46, 100)),
            hi=(4, 4, (90, 130, 210), 2))
    c.text(960, 196, "SCIENCE HALL", 38, (255, 220, 80), stroke=0)
    for ax in (772, 1148):
        c.paint(ell(ax, 196, 13, 13), (0, 0, 0, 0), ow=3, oc=(255, 220, 80))
        c.paint(ell(ax, 196, 13, 5, 30), (0, 0, 0, 0), ow=2, oc=(255, 220, 80))
        c.paint(ell(ax, 196, 13, 5, -30), (0, 0, 0, 0), ow=2, oc=(255, 220, 80))

    # --- glass double doors to the quad
    x0, y0, x1, y1 = B["Campus"]
    cas = (200, 206, 214)
    c.paint(rect(x0, y0, x1, y1), cas, shade=(-5, 0, dk(cas, 0.75)), hi=(0, 4, lt(cas, 0.3)))
    for lx0, lx1 in ((x0 + 12, (x0 + x1) / 2 - 3), ((x0 + x1) / 2 + 3, x1 - 12)):
        def night(p, lx0=lx0, lx1=lx1):
            for _ in range(14):
                p.ell(rng.uniform(lx0, lx1), rng.uniform(y0 + 20, y0 + 150), 1.6, 1.6, (255, 250, 220))
            p.ell((x0 + x1) / 2 - 10, y1 - 150, 70, 60, (30, 70, 60))  # tree
            p.rect((x0 + x1) / 2 - 16, y1 - 120, (x0 + x1) / 2 - 4, y1, (60, 40, 40))
            p.rect(lx0, y1 - 60, lx1, y1, (40, 90, 60))
            p.ell(x1 - 50, y1 - 120, 10, 10, (255, 230, 150))
            p.line([(x1 - 50, y1 - 110), (x1 - 50, y1 - 50)], 3, (40, 40, 50))
            p.poly([(lx0 + 6, y1 - 40), (lx0 + 40, y0 + 20), (lx0 + 56, y0 + 20), (lx0 + 22, y1 - 40)], (255, 255, 255, 40))
        c.paint(rect(lx0, y0 + 12, lx1, y1 - 2), ("v", (40, 36, 100), (110, 70, 140)), ow=3, pattern=night)
        c.paint(rrect(lx0 + 8, y0 + 170, lx1 - 8, y0 + 182, 4), (230, 232, 236), ow=2.5, hi=(0, 2, (255, 255, 255)))
    c.paint(rrect(x0 + 10, y0 - 46, x1 - 10, y0 - 10, 5), (36, 140, 84), shade=(-3, -3, (24, 100, 60)),
            hi=(2, 2, (110, 200, 140), 1.5))
    c.text((x0 + x1) / 2, y0 - 28, "< TO THE QUAD", 16, (255, 255, 240))

    # --- notice board with MISSING poster
    x0, y0, x1, y1 = B["Notice board"]
    c.paint(wonky(x0, y0, x1, y1, 2, rng), (150, 96, 56), shade=(-6, -6, (110, 70, 40)))
    c.paint(wonky(x0 + 12, y0 + 12, x1 - 12, y1 - 12, 1.5, rng), (210, 164, 106), ow=3,
            pattern=lambda p: [p.ell(rng.uniform(x0 + 12, x1 - 12), rng.uniform(y0 + 12, y1 - 12), 1.6, 1.6,
                                     (160, 116, 70)) for _ in range(120)])
    mp = Canvas(110, 140, ow=3)
    mp.paint(rect(5, 5, 105, 135), (255, 250, 236), shade=(-3, -3, (220, 214, 200)))
    mp.text(55, 20, "MISSING", 17, (210, 40, 50))
    mp.paint(ell(55, 72, 30, 30), (255, 236, 200), ow=2.5)
    hamster(mp, 53, 96, 0.62)
    mp.text(55, 114, "PROF. NIBBLES", 9, OUT, "Black")
    mp.text(55, 126, "loves seeds+tubes", 7.5, (80, 60, 60), "Bold")
    c.stamp(mp, x0 + 64, y0 + 82, -4)
    c.paint(ell(x0 + 64, y0 + 18, 5, 5), (230, 50, 60), ow=2)
    sp = Canvas(80, 100, ow=3)
    sp.paint(rect(5, 5, 75, 95), (255, 220, 60), shade=(-3, -3, (220, 180, 40)))
    sp.text(40, 20, "SAFETY", 12, OUT)
    goggles(sp, 40, 46, 0.62)
    sp.text(40, 70, "GOGGLES ON", 8.5, OUT, "Bold")
    sp.text(40, 84, "NO DRINKING!", 8.5, (200, 30, 40), "Bold")
    c.stamp(sp, x1 - 50, y0 + 62, 5)
    c.paint(ell(x1 - 50, y0 + 16, 5, 5), (50, 120, 230), ow=2)
    c.paint(rect(x1 - 92, y1 - 46, x1 - 20, y1 - 22), (170, 230, 250), ow=2.5)
    c.text(x1 - 56, y1 - 34, "TUTOR $5", 8.5, (30, 60, 120))

    # --- wall clock
    c.paint(ell(700, 380, 42, 42), (250, 248, 240), ow=5, shade=(-4, -4, (220, 220, 214)))
    for k in range(12):
        a = math.radians(k * 30)
        c.line([(700 + 33 * math.cos(a), 380 + 33 * math.sin(a)), (700 + 38 * math.cos(a), 380 + 38 * math.sin(a))], 2.5)
    c.line([(700, 380), (700, 352)], 4)
    c.line([(700, 380), (722, 392)], 3)
    c.paint(ell(700, 380, 4, 4), (220, 40, 50), ow=2)

    # --- air vent near the floor
    x0, y0, x1, y1 = B["Air vent"]
    vy0, vy1 = y0 + 8, y1 - 18
    c.paint(rect(x0 + 6, vy0, x1 - 6, vy1), (176, 182, 190), shade=(-3, -3, (130, 136, 146)), hi=(0, 3, (220, 224, 230)))

    def slats(p):
        for k in range(6):
            yy = vy0 + 8 + k * ((vy1 - vy0 - 14) / 5.6)
            p.rect(x0 + 14, yy, x1 - 14, yy + 5, (40, 34, 48))
    c.paint(rect(x0 + 12, vy0 + 6, x1 - 12, vy1 - 6), (120, 126, 136), ow=2.5, pattern=slats)
    for sx, sy in ((x0 + 10, vy0 + 4), (x1 - 10, vy0 + 4), (x0 + 10, vy1 - 4), (x1 - 10, vy1 - 4)):
        c.paint(ell(sx, sy, 2.5, 2.5), (90, 90, 100), ow=1.5)
    for k in range(4):
        seed(c, x0 + 30 + k * 18 + rng.uniform(-4, 4), y1 + 10 + rng.uniform(-2, 6), rng.uniform(-40, 40), 0.7)

    # --- Mr. Bones the skeleton on a stand
    x0, y0, x1, y1 = B["Mr. Bones"]
    paint_skeleton(c, (x0 + x1) / 2, y1, (y1 - y0))

    # --- lab door
    x0, y0, x1, y1 = B["Lab door"]
    door(c, x0 + 16, y0 + 40, x1 - 16, y1, (64, 110, 170), knob="R", panels=False)
    gx0, gy0, gx1, gy1 = x0 + 46, y0 + 70, x1 - 46, y0 + 160
    c.paint(rect(gx0, gy0, gx1, gy1), ("v", (150, 230, 220), (80, 170, 170)), ow=3,
            pattern=lambda p: [p.poly([(gx0 + 6, gy1 - 6), (gx0 + 26, gy0 + 4), (gx0 + 38, gy0 + 4), (gx0 + 18, gy1 - 6)],
                                      (230, 255, 250)), p.ell(gx1 - 24, gy1 - 20, 9, 12, (255, 120, 170))])
    c.paint(rrect(x0 + 34, y0 - 4, x1 - 34, y0 + 30, 5), (250, 248, 236), ow=3, shade=(-3, -3, (214, 210, 200)))
    c.text((x0 + x1) / 2, y0 + 13, "LAB 3B", 19, (40, 60, 120))
    tx, ty = (x0 + x1) / 2, y0 + 210
    c.paint(poly([(tx, ty - 26), (tx + 28, ty + 20), (tx - 28, ty + 20)], 1), (255, 214, 40), ow=3.5)
    c.text(tx, ty + 6, "!", 26, OUT)
    sp = Canvas(110, 70, ow=3)
    sp.paint(poly([(55, 4), (66, 24), (104, 26), (74, 42), (86, 66), (55, 52), (24, 66), (36, 42), (6, 26), (44, 24)], 1),
             (255, 90, 160), shade=(-3, -3, (210, 50, 120)))
    sp.text(55, 33, "DARE", 12, (255, 255, 240))
    sp.text(55, 46, "ROUND!", 9, (255, 255, 240))
    c.stamp(sp, tx, y0 + 300, 8)

    # --- periodic table poster
    x0, y0, x1, y1 = B["Periodic table"]
    cols = [(255, 140, 120), (255, 200, 90), (140, 220, 150), (120, 190, 250), (210, 160, 250), (250, 240, 220)]

    def table(p):
        p.rect(x0 + 10, y0 + 10, x1 - 10, y0 + 40, (40, 40, 70))
        cw, ch = (x1 - x0 - 28) / 18, (y1 - y0 - 70) / 7
        for r in range(7):
            for k in range(18):
                if r == 0 and 0 < k < 17:
                    continue
                if r in (1, 2) and 1 < k < 12:
                    continue
                col = cols[0 if k < 2 else (5 if k > 16 else (1 if k < 12 else (2 if k < 15 else 3)))]
                if r > 4 and 2 < k < 12:
                    col = cols[4]
                xx, yy = x0 + 14 + k * cw, y0 + 50 + r * ch
                p.rect(xx, yy, xx + cw - 2, yy + ch - 2, col)
    c.paint(wonky(x0, y0, x1, y1, 2, rng), (250, 248, 238), shade=(-4, -4, (214, 210, 200)), pattern=table)
    c.text((x0 + x1) / 2, y0 + 25, "PERIODIC TABLE", 15, (255, 230, 120))
    c.paint(rect(x1 - 40, y1 - 52, x1 - 14, y1 - 26), (120, 70, 40), ow=2.5)
    c.text(x1 - 27, y1 - 39, "Ch", 10, (255, 230, 200))
    for tx_, ty_ in ((x0 + 6, y0 + 6), (x1 - 6, y0 + 6)):
        c.paint(rect(tx_ - 10, ty_ - 6, tx_ + 10, ty_ + 6), (240, 232, 200), ow=0, opacity=0.85)

    # --- roof stairs fire door + ROOF sign
    x0, y0, x1, y1 = B["Roof stairs"]
    fire_door(c, x0 + 12, y0 + 20, x1 - 12, y1)
    c.paint(rrect(x0 + 18, y0 - 40, x1 - 18, y0 + 4, 5), (220, 60, 50), shade=(-3, -3, (170, 40, 40)),
            hi=(2, 2, (255, 130, 110), 1.5))
    c.text((x0 + x1) / 2, y0 - 18, "ROOF ^", 18, (255, 250, 230))

    # little potted plant between periodic table and stairs (on the wall line, out of the walk band)
    px, py = 1660, WALL_Y + 2
    c.shadow(px, py, 28, 6)
    for k, ang in enumerate((-60, -30, -10, 15, 40, 70)):
        L = 54 - abs(ang) * 0.3
        a = math.radians(ang - 90)
        c.paint(ell(px + math.cos(a) * L * 0.6, py - 46 + math.sin(a) * L * 0.6, L * 0.5, 11, ang - 90), (70, 170, 80),
                ow=3, shade=(2, 2, (40, 120, 60)))
    c.paint(poly([(px - 24, py - 48), (px + 24, py - 48), (px + 18, py), (px - 18, py)], 1), (210, 100, 60),
            shade=(-4, 0), hi=(0, 3, (240, 150, 100)))

    lights = [(330, 120, 640, 0.35, (230, 245, 255)), (960, 120, 700, 0.40, (230, 245, 255)),
              (1590, 120, 640, 0.35, (230, 245, 255)), (120, 640, 260, 0.35, (150, 140, 255)),
              (1220, 560, 280, 0.25, (170, 255, 240))]
    light_pass(c, 0.78, lights, vign=0.45)
    ceiling_glows(c, (330, 960, 1590))
    c.save("bg_science_hall.png")


def paint_skeleton(c, cx, by, h):
    """Model skeleton in a lab coat on a rolling stand; (cx, by) = floor contact, h = total height."""
    s = h / 260.0
    bone, bone_sh = (246, 240, 220), (206, 196, 176)

    def T(x, y):
        return (cx + x * s, by - y * s)
    c.shadow(cx, by, 52 * s, 7 * s, 0.4)
    # stand
    for dx in (-40, 0, 40):
        c.line([T(0, 14), T(dx, 4)], 4 * s, (70, 74, 84))
        c.paint(ell(*T(dx, 4), 6 * s, 5 * s), (40, 40, 46), ow=2)
    c.line([T(0, 14), T(0, 120)], 6 * s, (110, 116, 126))
    # legs
    for sgn in (-1, 1):
        c.paint(cap([T(sgn * 12, 120), T(sgn * 14, 70)], 7 * s), bone, shade=(-2, 0, bone_sh))
        c.paint(ell(*T(sgn * 14, 70), 6 * s, 5 * s), bone, ow=2.5)
        c.paint(cap([T(sgn * 14, 70), T(sgn * 12, 26)], 6 * s), bone, shade=(-2, 0, bone_sh))
        c.paint(poly([T(sgn * 12 - 7, 28), T(sgn * 12 + 7, 28), T(sgn * 12 + sgn * 18, 18), T(sgn * 12 - 4, 18)], 1), bone,
                ow=2.5)
    # lab coat (open, hanging off the shoulders)
    coat = (250, 250, 246)
    c.paint(poly([T(-30, 208), T(30, 208), T(36, 110), T(-36, 110)], 2), coat, shade=(-5, 0, (210, 214, 226)))
    # ribcage visible in the open coat
    c.paint(poly([T(-14, 206), T(14, 206), T(12, 150), T(-12, 150)], 1), (60, 56, 70), ow=2.5)
    for k in range(5):
        yy = 198 - k * 10
        c.curve(T(-13, yy), T(0, yy - 6), T(13, yy), 3.2 * s, bone)
    c.line([T(0, 206), T(0, 128)], 4 * s, bone)
    c.paint(poly([T(-14, 136), T(14, 136), T(10, 118), T(-10, 118)], 1), bone, ow=2.5)  # pelvis
    # lapels + name tag
    c.paint(poly([T(-16, 208), T(-30, 208), T(-24, 170), T(-14, 160)], 1), coat, ow=2.5, shade=(-2, 0, (210, 214, 226)))
    c.paint(poly([T(16, 208), T(30, 208), T(24, 170), T(14, 160)], 1), coat, ow=2.5, shade=(-2, 0, (210, 214, 226)))
    c.paint(rect(*T(-28, 176), *T(-16, 168)), (250, 220, 80), ow=2)
    c.line([T(22, 180), T(22, 196)], 2.5 * s, (40, 90, 200))  # pen in pocket
    # arms: one waving
    c.paint(cap([T(-28, 204), T(-40, 170), T(-38, 134)], 7 * s), coat, shade=(-2, 0, (210, 214, 226)))
    c.paint(cap([T(-38, 134), T(-36, 118)], 4 * s), bone, ow=2.5)
    c.paint(cap([T(28, 204), T(46, 228), T(52, 258)], 7 * s), coat, shade=(-2, 0, (210, 214, 226)))
    for k in range(4):
        c.line([T(52, 258), T(46 + k * 4, 270 + (k % 2) * 3)], 2.5 * s, bone)
    # skull
    c.paint(cap([T(0, 208), T(0, 216)], 6 * s), bone, ow=2.5)
    skull = ell(*T(0, 236), 20 * s, 22 * s) + poly([T(-12, 220), T(12, 220), T(10, 208), T(-10, 208)], 1)
    c.paint(skull, bone, shade=(-3, 2, bone_sh), hi=(3, 3, (255, 255, 245), 2))
    for ex in (-8, 8):
        c.paint(ell(*T(ex, 238), 6 * s, 6.5 * s), (50, 40, 50), ow=2)
    c.paint(poly([T(0, 232), T(3, 226), T(-3, 226)]), (50, 40, 50), ow=1.5)
    c.line([T(-10, 216), T(10, 216)], 1.6)
    for k in range(-3, 4):
        c.line([T(k * 3, 219), T(k * 3, 213)], 1.2)


# =========================================================================== Lab 3B
def paint_lab():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(3)
    B = boxes("lab")
    upper = (240, 168, 120)
    c.paint(rect(0, 0, W_BG, 560), ("vy", 120, 560, (220, 136, 104), upper), ow=0)
    for y in range(150, 556, 46):  # subtle wallpaper stripes of beaker motifs
        for x in range(40 + (y // 46 % 2) * 60, W_BG, 120):
            c.paint(poly([(x - 7, y - 10), (x + 7, y - 10), (x + 7, y - 2), (x + 13, y + 10), (x - 13, y + 10),
                          (x - 7, y - 2)]), (255, 210, 160), ow=0, opacity=0.28)
    block_wall(c, 0, 560, W_BG, WALL_Y, (238, 238, 226), (200, 206, 200), bw=50, bh=50, mortar=0.3, seed=41)
    c.paint(rect(-10, 552, W_BG + 10, 570), (40, 150, 150), ow=3, hi=(0, 4, (90, 200, 190)), shade=(0, -4))
    drop_ceiling(c, 120, (206, 214, 206), panels=(330, 960, 1590))
    checker_floor(c, (226, 232, 216), (60, 150, 140), cols=130, rows=7)
    baseboard(c, color=(40, 90, 96))

    # --- door back to the hallway
    x0, y0, x1, y1 = B["Hallway"]
    door(c, x0 + 14, y0 + 30, x1 - 14, y1, (200, 90, 60), knob="R", panels=False)
    gx0, gy0, gx1, gy1 = x0 + 44, y0 + 60, x1 - 44, y0 + 150
    c.paint(rect(gx0, gy0, gx1, gy1), ("v", (250, 210, 140), (220, 150, 90)), ow=3,
            pattern=lambda p: p.poly([(gx0 + 6, gy1 - 6), (gx0 + 24, gy0 + 4), (gx0 + 36, gy0 + 4), (gx0 + 18, gy1 - 6)],
                                     (255, 240, 210)))
    c.paint(rrect(x0 + 24, y0 - 34, x1 - 24, y0 + 0, 5), (36, 140, 84), shade=(-3, -3, (24, 100, 60)),
            hi=(2, 2, (110, 200, 140), 1.5))
    c.text((x0 + x1) / 2, y0 - 17, "< HALL", 16, (255, 255, 240))

    # --- recycling bin with paper-towel tubes
    x0, y0, x1, y1 = B["Recycling bin"]
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2 + 6, 7, 0.45)
    for k, (dx, ang) in enumerate(((-18, -70), (4, -100), (20, -60))):
        a = math.radians(ang)
        bx, byy = (x0 + x1) / 2 + dx, y0 + 42
        cardboard_tube(c, bx, byy, bx + math.cos(a) * 36, byy + math.sin(a) * 36, 9)
    blue = (40, 110, 220)
    c.paint(poly([(x0 + 2, y0 + 30), (x1 - 2, y0 + 30), (x1 - 8, y1), (x0 + 8, y1)], 1), blue, shade=(-5, 0, dk(blue, 0.75)),
            hi=(4, 0, lt(blue, 0.3), 2))
    c.paint(rrect(x0 - 2, y0 + 24, x1 + 2, y0 + 38, 4), dk(blue, 0.85), ow=3)
    rx, ry = (x0 + x1) / 2, y0 + 78
    for k in range(3):
        a = math.radians(k * 120 - 90)
        b = math.radians(k * 120 + 10)
        c.curve((rx + 16 * math.cos(a), ry + 16 * math.sin(a)), (rx + 22 * math.cos((a + b) / 2), ry + 22 * math.sin((a + b) / 2)),
                (rx + 16 * math.cos(b), ry + 16 * math.sin(b)), 4, (255, 255, 255))

    # --- the big vent (grate hanging open)
    x0, y0, x1, y1 = B["Big vent"]
    vx0, vy0, vx1, vy1 = x0 + 10, y0 + 6, x1 - 10, y1 - 14
    c.paint(rect(vx0 - 8, vy0 - 8, vx1 + 8, vy1 + 8), (176, 182, 190), shade=(-3, -3, (130, 136, 146)))
    c.paint(rect(vx0, vy0, vx1, vy1), ("v", (20, 14, 30), (60, 50, 70)), ow=3,
)
    grate = poly([(vx1 - 6, vy1 + 2), (vx1 + 40, vy1 - 12), (vx1 + 48, vy0 + 6), (vx1 + 4, vy0 + 16)], 0)
    c.paint(grate, (150, 156, 166), shade=(3, 0, (110, 116, 126)),
            pattern=lambda p: [p.line([(vx1 + k * 7, vy1 - k * 2.5), (vx1 + 6 + k * 7, vy0 + 14 - k * 1.5)], 2.2, (60, 60, 70))
                               for k in range(1, 6)])
    for k in range(5):
        seed(c, x0 + 22 + k * 20 + rng.uniform(-4, 4), y1 + 2 + rng.uniform(0, 8), rng.uniform(-40, 40), 0.7)

    # --- shelf of jars behind Mina
    sx0, sx1 = 640, 930
    for sy in (300, 420):
        c.paint(rect(sx0, sy, sx1, sy + 14), (150, 96, 60), ow=3, hi=(0, 3, (196, 140, 96)))
        for bx in (sx0 + 20, sx1 - 20):
            c.paint(poly([(bx - 4, sy + 14), (bx + 4, sy + 14), (bx + 4, sy + 40), (bx - 4, sy + 30)]), (100, 70, 50), ow=2.5)
        x = sx0 + 16
        while x < sx1 - 30:
            w = rng.uniform(26, 44)
            h = rng.uniform(40, 80)
            col = rng.choice([(120, 220, 140), (250, 120, 160), (120, 190, 255), (255, 200, 80), (200, 140, 250)])
            jar = rrect(x, sy - h, x + w, sy, 6)
            c.paint(jar, (230, 240, 240), shade=(-3, 0, (200, 210, 214)))
            c.paint(rect(x, sy - h * 0.62, x + w, sy), col, ow=0, clip=jar, opacity=0.85)
            c.paint(rect(x + 2, sy - h - 8, x + w - 2, sy - h + 2), (90, 90, 100), ow=2.5)
            c.paint(rect(x + 6, sy - h * 0.5, x + w - 6, sy - h * 0.3), (255, 250, 236), ow=1.5)
            c.paint(jar, (0, 0, 0, 0), ow=3)
            x += w + rng.uniform(8, 18)
    sp = Canvas(140, 60, ow=3)
    sp.paint(rect(5, 5, 135, 55), (255, 255, 255), shade=(-3, -3, (220, 220, 230)))
    sp.text(70, 22, "THINK", 15, (200, 40, 60))
    sp.text(70, 41, "SAFETY!", 13, (40, 90, 200))
    c.stamp(sp, 785, 210, -3)

    # --- lab bench
    bx0, bx1, btop = 960, 1530, 662
    c.shadow((bx0 + bx1) / 2, WALL_Y + 6, (bx1 - bx0) / 2 + 10, 10, 0.4)
    cab = (70, 120, 160)
    c.paint(rect(bx0 + 12, btop + 14, bx1 - 12, WALL_Y + 4), cab, shade=(-5, 0, dk(cab, 0.75)), hi=(0, 4, lt(cab, 0.25)))
    for k in range(4):
        dx0 = bx0 + 24 + k * (bx1 - bx0 - 48) / 4
        dx1 = dx0 + (bx1 - bx0 - 48) / 4 - 10
        c.paint(rect(dx0, btop + 28, dx1, WALL_Y - 10), lt(cab, 0.1), ow=2.5, shade=(-3, -3, dk(cab, 0.8)))
        c.paint(rrect((dx0 + dx1) / 2 - 16, btop + 40, (dx0 + dx1) / 2 + 16, btop + 48, 3), (220, 220, 226), ow=2)
    c.paint(rect(bx0, btop - 4, bx1, btop + 16), (50, 50, 64), ow=3.5, hi=(0, 3, (100, 100, 120)))

    # beakers (blue glowing one with a label)
    x0, y0, x1, y1 = B["Beakers"]
    base = btop - 3
    bk = poly([(x0 + 8, y0 + 30), (x0 + 50, y0 + 30), (x0 + 52, base), (x0 + 6, base)], 1)
    c.paint(bk, (220, 244, 250), shade=(-3, 0, (190, 214, 226)))
    c.paint(rect(x0, y0 + 46, x0 + 60, base), (60, 160, 255), ow=0, clip=bk, opacity=0.95)
    c.paint(rect(x0 + 12, y0 + 58, x0 + 46, y0 + 74), (255, 250, 236), ow=2)
    c.text(x0 + 29, y0 + 66, "NOT A DRINK", 4.5, (200, 30, 40), "Bold")
    c.paint(bk, (0, 0, 0, 0), ow=3.5)
    for bb in ((x0 + 22, y0 + 22, 4), (x0 + 34, y0 + 12, 3), (x0 + 28, y0 + 2, 2.5)):
        c.paint(ell(bb[0], bb[1], bb[2], bb[2]), (160, 220, 255), ow=2)
    fl = poly([(x0 + 72, y0 + 14), (x0 + 84, y0 + 14), (x0 + 84, y0 + 40), (x1 - 2, base), (x0 + 56, base), (x0 + 72, y0 + 40)], 1)
    c.paint(fl, (220, 244, 250))
    c.paint(rect(x0 + 50, y0 + 58, x1, base), (110, 230, 90), ow=0, clip=fl)
    c.paint(fl, (0, 0, 0, 0), ow=3.5)
    c.paint(rect(x0 + 70, y0 + 6, x0 + 86, y0 + 16), (200, 120, 70), ow=2.5)

    # hamster cage (empty, door open, wheel)
    x0, y0, x1, y1 = B["Hamster cage"]
    base = btop - 3
    c.paint(rect(x0 + 2, base - 18, x1 - 2, base), (250, 120, 160), shade=(-3, 0, (200, 70, 120)))
    c.paint(rect(x0 + 6, base - 14, x1 - 6, base - 4), (250, 226, 150), ow=0)  # bedding
    wx, wy = x0 + 46, base - 44
    c.paint(ell(wx, wy, 28, 28), (0, 0, 0, 0), ow=4, oc=(255, 210, 60))
    for k in range(8):
        a = math.radians(k * 45)
        c.line([(wx, wy), (wx + 26 * math.cos(a), wy + 26 * math.sin(a))], 1.6, (220, 180, 50))
    c.line([(wx, wy), (wx + 4, base - 16)], 3, (150, 150, 160))
    c.paint(rrect(x1 - 30, y0 + 28, x1 - 18, y0 + 66, 4), (180, 230, 250), ow=2.5)
    c.line([(x1 - 24, y0 + 66), (x1 - 30, y0 + 76)], 2.5, (150, 150, 160))
    cage = rrect(x0 + 2, y0 + 8, x1 - 2, base - 18, 18)
    for k in range(13):
        xx = x0 + 8 + k * (x1 - x0 - 16) / 12
        c.line([(xx, y0 + 14), (xx, base - 18)], 1.8, (190, 196, 206))
    c.paint(cage, (0, 0, 0, 0), ow=3.5)
    c.paint(rrect(x0 + 2, y0 + 8, x1 - 2, y0 + 18, 5), (250, 120, 160), ow=3)
    # open door swung out
    c.paint(poly([(x1 - 2, base - 60), (x1 + 18, base - 70), (x1 + 18, base - 30), (x1 - 2, base - 22)]),
            (0, 0, 0, 0), ow=3, oc=(150, 156, 166))
    # mascot cushion (where Nibbles sits once he's home)
    nb = B["Professor Nibbles"]
    ncx = (nb[0] + nb[2]) / 2
    c.paint(ell(ncx, base - 6, 30, 9), (150, 70, 200), shade=(0, -3, (110, 40, 160)), hi=(0, 2, (200, 140, 240), 1.5))
    for tx_ in (ncx - 28, ncx + 28):
        c.paint(ell(tx_, base - 4, 4, 3), (255, 210, 60), ow=2)
    # bunsen burner + test tube rack at the right end of the bench
    c.paint(rect(1440, btop - 14, 1490, btop - 4), (90, 90, 100), ow=3)
    c.paint(rect(1458, btop - 60, 1472, btop - 14), (150, 156, 166), ow=3, hi=(2, 0, (200, 204, 214)))
    c.paint(poly([(1465, btop - 100), (1476, btop - 70), (1465, btop - 60), (1454, btop - 70)], 2, True), (80, 160, 255),
            ow=2.5, pattern=lambda p: p.ell(1465, btop - 70, 4, 8, (200, 240, 255)))
    c.paint(rect(1384, btop - 40, 1430, btop - 30), (170, 110, 70), ow=2.5)
    for k, col in enumerate(((255, 90, 120), (255, 200, 60), (120, 220, 140))):
        tx_ = 1392 + k * 14
        tt = rrect(tx_ - 4, btop - 66, tx_ + 4, btop - 10, 4)
        c.paint(tt, (230, 244, 250))
        c.paint(rect(tx_ - 6, btop - 40, tx_ + 6, btop - 10), col, ow=0, clip=tt)
        c.paint(tt, (0, 0, 0, 0), ow=2.5)
    c.paint(rect(1380, btop - 26, 1434, btop - 4), (170, 110, 70), ow=2.5)

    # --- chalkboard: DO HAMSTERS PREFER JAZZ?
    x0, y0, x1, y1 = B["Chalkboard"]
    c.paint(rect(x0, y0, x1, y1), (150, 100, 60), shade=(-5, -5, (110, 70, 40)), hi=(3, 3, (190, 140, 90)))
    c.paint(rect(x0 + 12, y0 + 12, x1 - 12, y1 - 12), ("v", (52, 92, 76), (36, 70, 58)), ow=3)
    chalk = (240, 244, 230)
    c.text((x0 + x1) / 2, y0 + 36, "DO HAMSTERS PREFER JAZZ?", 17, chalk, "Bold")
    c.line([(x0 + 40, y0 + 52), (x1 - 40, y0 + 54)], 2, chalk, opacity=0.8)
    gx, gy = x0 + 36, y1 - 40
    c.line([(gx, y0 + 66), (gx, gy), (gx + 170, gy)], 2.5, chalk)
    for k, (hh, lab) in enumerate(((62, "JAZZ"), (14, "METAL"), (26, "POLKA"))):
        bxx = gx + 18 + k * 52
        c.paint(rect(bxx, gy - hh, bxx + 30, gy), (0, 0, 0, 0), ow=2.5, oc=chalk)
        c.text(bxx + 15, gy + 10, lab, 8, chalk, "Bold")
    c.text(gx + 33, gy - 72, "+40%!", 11, (255, 230, 120), "Bold")
    c.text(x1 - 72, y0 + 84, "wheel speed", 10, chalk, "Bold")
    c.text(x1 - 72, y0 + 104, "= jazz^2", 11, chalk, "Bold")
    c.text(x1 - 72, y0 + 132, "polka: filed", 9, chalk, "Bold")
    c.text(x1 - 72, y0 + 146, "a complaint", 9, chalk, "Bold")
    c.paint(rect(x0 + 40, y1 - 12, x0 + 110, y1 - 2), (150, 100, 60), ow=2.5)
    c.paint(rect(x0 + 50, y1 - 18, x0 + 70, y1 - 12), chalk, ow=2)

    # --- DARE ROUND banner
    x0, y0, x1, y1 = B["Dare Round banner"]
    c.line([(x0 + 20, 120), (x0 + 30, y0 + 10)], 3, (60, 60, 70))
    c.line([(x1 - 20, 120), (x1 - 30, y0 + 10)], 3, (60, 60, 70))
    ban = poly([(x0, y0 + 6), (x1, y0 + 6), (x1 - 14, (y0 + y1) / 2), (x1, y1), (x0, y1), (x0 + 14, (y0 + y1) / 2)], 1)

    def glitter(p):
        for _ in range(160):
            p.ell(rng.uniform(x0, x1), rng.uniform(y0, y1), 1.6, 1.6, (255, 200, 240))
    c.paint(ban, (220, 40, 140), shade=(0, -6, (170, 20, 110)), hi=(0, 4, (255, 120, 200), 2), pattern=glitter)
    c.text((x0 + x1) / 2, y0 + 36, "SPEED DATERS LIVE", 16, (255, 240, 160))
    c.text((x0 + x1) / 2, y0 + 78, "DARE ROUND", 40, (255, 255, 255), "Italic", stroke=3, sc=(120, 10, 80))
    for sx_, sy_ in ((x0 + 30, y0 + 24), (x1 - 30, y0 + 28), (x0 + 40, y1 - 22), (x1 - 40, y1 - 18)):
        c.paint(poly([(sx_, sy_ - 10), (sx_ + 3, sy_ - 3), (sx_ + 10, sy_), (sx_ + 3, sy_ + 3), (sx_, sy_ + 10),
                      (sx_ - 3, sy_ + 3), (sx_ - 10, sy_), (sx_ - 3, sy_ - 3)]), (255, 240, 120), ow=2)

    # --- safety shower
    x0, y0, x1, y1 = B["Safety shower"]
    mx = (x0 + x1) / 2
    yel = (255, 200, 40)
    c.shadow(mx, y1, 40, 7, 0.35)
    c.paint(rect(mx - 8, y0 + 30, mx + 8, y1), yel, shade=(-3, 0, dk(yel, 0.75)), hi=(2, 0, lt(yel, 0.4)))
    c.paint(cap([(mx, y0 + 34), (mx - 30, y0 + 34)], 14), yel, shade=(0, 3, dk(yel, 0.75)))
    c.paint(poly([(mx - 64, y0 + 64), (mx - 2, y0 + 64), (mx - 18, y0 + 38), (mx - 46, y0 + 38)], 1), (200, 204, 214),
            shade=(0, -4, (150, 156, 166)))
    c.line([(mx - 36, y0 + 66), (mx - 36, y0 + 150)], 2, (90, 90, 100))
    c.paint(rrect(mx - 44, y0 + 150, mx - 28, y0 + 168, 4), (40, 160, 90), ow=2.5)
    c.paint(rrect(mx - 50, y0 + 190, mx + 50, y0 + 240, 6), (40, 160, 90), shade=(-3, -3, (20, 110, 60)))
    c.text(mx, y0 + 206, "SAFETY", 13, (255, 255, 240))
    c.text(mx, y0 + 226, "SHOWER", 13, (255, 255, 240))
    c.paint(ell(mx, y1 - 4, 46, 8), (60, 160, 90), ow=3, opacity=0.9)

    # stage spotlights for the show
    for lx, ly, ang in ((1440, 150, 30), (1760, 150, -30)):
        c.paint(rrect(lx - 22, ly - 14, lx + 22, ly + 14, 6), (40, 40, 48), ow=3)
        c.paint(ell(lx + (12 if ang > 0 else -12), ly + 6, 10, 12), (255, 250, 220), ow=2.5)

    lights = [(330, 110, 620, 0.32, (230, 245, 255)), (960, 110, 700, 0.38, (230, 245, 255)),
              (1590, 110, 620, 0.35, (230, 245, 255)), (1020, 600, 220, 0.5, (90, 170, 255)),
              (1600, 700, 420, 0.45, (255, 140, 210))]
    light_pass(c, 0.8, lights, vign=0.45)
    ceiling_glows(c, (330, 960, 1590))
    c.glow(1020, 610, 90, (90, 170, 255), 0.55)
    c.glow(1465, btop - 80, 50, (120, 190, 255), 0.6)
    c.glow(1600, 380, 260, (255, 120, 200), 0.25)
    c.save("bg_lab.png")


# =========================================================================== rooftop
def paint_rooftop():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(33)
    B = boxes("rooftop")
    PAR = 612  # top of the parapet

    def sky(p):
        for _ in range(170):
            x, y = rng.uniform(0, W_BG), rng.uniform(0, 460)
            r = rng.choice([1.2, 1.6, 2.2, 2.8])
            p.ell(x, y, r, r, (255, 250, 220))
    c.paint(rect(0, 0, W_BG, PAR + 20), ("vy", 0, PAR, (26, 22, 76), (176, 76, 120)), ow=0, pattern=sky)
    # moon
    c.paint(ell(1460, 150, 62, 62), (255, 244, 200), ow=4, hi=(-5, -5, (255, 255, 236), 4),
            pattern=lambda p: [p.ell(1440, 136, 12, 10, (236, 220, 170)), p.ell(1480, 176, 9, 8, (236, 220, 170)),
                               p.ell(1486, 124, 6, 5, (236, 220, 170))])
    c.glow(1460, 150, 200, (255, 240, 200), 0.25)
    # far skyline: Downtown on the right with neon, campus on the left
    for layer, (col, hmin, hmax, wmin, wmax) in enumerate((((80, 46, 110), 120, 260, 50, 110), ((48, 30, 82), 60, 170, 40, 90))):
        x = -20
        while x < W_BG:
            bw = rng.uniform(wmin, wmax)
            down = x > 1150
            h = rng.uniform(hmin, hmax) * (1.35 if down else 0.8)
            top = PAR - h
            sh = rect(x, top, x + bw, PAR + 10)
            if not down and rng.random() < 0.35:
                sh = sh + poly([(x, top), (x + bw / 2, top - 34), (x + bw, top)])
            c.paint(sh, col, ow=0)
            for wy in range(int(top + 12), PAR - 6, 20):
                for wx in range(int(x + 8), int(x + bw - 10), 16):
                    if rng.random() < (0.5 if down else 0.3):
                        c.paint(rect(wx, wy, wx + 7, wy + 10), rng.choice([(255, 206, 92), (255, 150, 200), (140, 230, 255)])
                                if down else (255, 206, 92), ow=0, opacity=0.8 - layer * 0.2)
            x += bw + rng.uniform(-8, 12)
    # neon DOWNTOWN sign on a far roof
    c.text(1350, 560, "DOWNTOWN", 20, (255, 120, 200), "Black", stroke=0)
    c.glow(1350, 560, 90, (255, 90, 200), 0.35)
    # campus dome + clock tower on the left
    c.paint(ell(640, PAR - 80, 70, 56) + rect(570, PAR - 80, 710, PAR + 10), (64, 38, 96), ow=0)
    c.paint(rect(860, PAR - 230, 920, PAR + 10) + poly([(850, PAR - 230), (890, PAR - 290), (930, PAR - 230)]),
            (64, 38, 96), ow=0)
    c.paint(ell(890, PAR - 196, 18, 18), (255, 230, 150), ow=3)
    c.line([(890, PAR - 196), (890, PAR - 208)], 2)
    c.line([(890, PAR - 196), (898, PAR - 192)], 2)
    # the quad stage lights in the distance
    for k, col in enumerate(((255, 90, 160), (255, 220, 90), (90, 220, 255))):
        c.glow(1440 + k * 50, PAR - 40, 46, col, 0.5)

    # water tower (behind the parapet)
    x0, y0, x1, y1 = B["Water tower"]
    mx = (x0 + x1) / 2
    leg = (110, 70, 80)
    for lx in (x0 + 26, x1 - 26):
        c.line([(lx, y0 + 190), (lx + (8 if lx < mx else -8), PAR + 20)], 9, leg)
    c.line([(x0 + 30, y0 + 250), (x1 - 30, y0 + 330)], 4, leg)
    c.line([(x1 - 30, y0 + 250), (x0 + 30, y0 + 330)], 4, leg)
    tank = rrect(x0 + 8, y0 + 50, x1 - 8, y0 + 200, 20)
    tcol = (200, 110, 90)
    c.paint(tank, tcol, shade=(-8, 0, dk(tcol, 0.72)), hi=(6, 0, lt(tcol, 0.3), 3),
            pattern=lambda p: [p.line([(x0 + 8 + k * 23, y0 + 54), (x0 + 8 + k * 23, y0 + 198)], 1.6, dk(tcol, 0.85))
                               for k in range(1, 8)])
    c.paint(poly([(x0, y0 + 56), (mx, y0 + 2), (x1, y0 + 56)], 1), (150, 80, 80), shade=(-5, 0, (110, 56, 66)))
    c.text(mx, y0 + 112, "DEX WAS", 18, (255, 250, 230), "Black")
    c.text(mx, y0 + 138, "HERE", 18, (255, 250, 230), "Black")
    c.paint(rect(x0 + 4, y0 + 196, x1 - 4, y0 + 206), (90, 60, 70), ow=3)

    # parapet (brick) + coping
    c.paint(rect(0, PAR, W_BG, WALL_Y), ("vy", PAR, WALL_Y, (176, 86, 70), (130, 58, 60)), ow=0)
    row = 0
    for y in range(PAR + 22, WALL_Y, 30):
        c.line([(0, y), (W_BG, y)], 2, (60, 20, 30), opacity=0.35)
        off = 40 * (row % 2)
        for x in range(-off, W_BG, 80):
            c.line([(x, y), (x, y + 30)], 2, (60, 20, 30), opacity=0.35)
        row += 1
    c.paint(rect(-10, PAR - 6, W_BG + 10, PAR + 22), (196, 186, 176), ow=4, hi=(0, 4, (236, 230, 220)), shade=(0, -5))
    # roof floor: tar with gravel
    fcol = (86, 74, 104)
    c.paint(rect(0, WALL_Y, W_BG, H_BG), ("vy", WALL_Y, H_BG, (110, 96, 126), dk(fcol, 0.8)), ow=0)
    for _ in range(1400):
        y = rng.uniform(WALL_Y + 4, H_BG)
        t = (y - WALL_Y) / (H_BG - WALL_Y)
        r = 1.0 + 2.6 * t
        c.paint(ell(rng.uniform(0, W_BG), y, r, r * 0.7), rng.choice([(140, 128, 150), (60, 52, 74), (170, 150, 160)]),
                ow=0, opacity=0.7)
    for k in range(5):  # tar seams
        yy = WALL_Y + (H_BG - WALL_Y) * ((k + 1) / 6) ** 1.4
        c.line([(0, yy), (W_BG, yy + rng.uniform(-6, 6))], 2.4, (40, 32, 50), opacity=0.45)
    c.line([(0, WALL_Y), (W_BG, WALL_Y)], 4)

    # stairwell hut
    x0, y0, x1, y1 = B["Stairwell door"]
    hut = (190, 170, 150)
    c.paint(rect(-10, y0 - 120, x1 + 50, y1), hut, shade=(-8, 0, dk(hut, 0.75)), hi=(0, 6, lt(hut, 0.3)))
    c.paint(rect(-20, y0 - 136, x1 + 66, y0 - 116), (110, 80, 90), ow=4)
    door(c, x0 + 14, y0 + 20, x1 - 14, y1, (60, 130, 120), knob="R", panels=True)
    c.paint(rrect(x0 + 22, y0 - 40, x1 - 22, y0 - 6, 5), (36, 140, 84), shade=(-3, -3, (24, 100, 60)),
            hi=(2, 2, (110, 200, 140), 1.5))
    c.text((x0 + x1) / 2, y0 - 23, "STAIRS", 15, (255, 255, 240))
    # caged bulb above the door
    bx_, by_ = (x0 + x1) / 2, y0 - 80
    c.paint(rect(bx_ - 10, by_ - 18, bx_ + 10, by_ - 8), (60, 60, 70), ow=3)
    c.paint(ell(bx_, by_ + 6, 13, 16), (255, 236, 160), ow=3)
    for k in (-6, 0, 6):
        c.line([(bx_ + k, by_ - 8), (bx_ + k * 1.6, by_ + 20)], 1.6, (60, 60, 70))

    # protest signs leaning on the parapet
    x0, y0, x1, y1 = B["Protest signs"]
    signs = [(x0 + 40, (255, 240, 120), ["FREE", "NIBBLES"], -8, (200, 30, 60)),
             (x0 + 180, (150, 230, 250), ["JAZZ IS", "NOT", "CONSENT"], 7, (30, 60, 140)),
             (x0 + 110, (255, 170, 200), ["HAMSTERS", "ARE PEOPLE", "TOO"], -2, (120, 20, 80))]
    for sx_, col, lines, ang, tc in signs:
        sub = Canvas(90, 170, ow=3.5)
        sub.line([(45, 70), (45, 166)], 7, (170, 120, 70))
        sub.paint(wonky(6, 8, 84, 84, 2, rng), col, shade=(-3, -3, dk(col, 0.85)))
        for i, ln in enumerate(lines):
            sub.text(45, 8 + 76 * (i + 0.7) / (len(lines) + 0.4), ln, 12 if len(lines) < 3 else 8.5, tc)
        c.stamp(sub, sx_, y1 - 85, ang)

    # bird feeder on a pole
    x0, y0, x1, y1 = B["Bird feeder"]
    mx = (x0 + x1) / 2
    c.shadow(mx, y1, 40, 7, 0.45)
    c.paint(poly([(mx - 30, y1), (mx + 30, y1), (mx + 20, y1 - 10), (mx - 20, y1 - 10)]), (90, 90, 100), ow=3)
    c.paint(rect(mx - 6, y0 + 90, mx + 6, y1 - 8), (110, 116, 126), shade=(-2, 0), hi=(2, 0, (170, 176, 186)))
    wood = (196, 110, 56)
    fy0 = y0 + 8
    c.paint(rect(mx - 58, fy0 + 116, mx + 58, fy0 + 132), wood, ow=3.5, hi=(0, 3, lt(wood, 0.3)))
    c.paint(rect(mx - 42, fy0 + 40, mx + 42, fy0 + 118), (220, 236, 240), shade=(-4, 0, (190, 206, 214)),
            pattern=lambda p: [p.ell(mx - 34 + (k * 13) % 70, fy0 + 70 + (k * 7) % 46, 5, 3,
                                     (40, 36, 44) if k % 2 else (236, 226, 200)) for k in range(34)])
    c.paint(rect(mx - 46, fy0 + 40, mx - 38, fy0 + 118), wood, ow=3)
    c.paint(rect(mx + 38, fy0 + 40, mx + 46, fy0 + 118), wood, ow=3)
    c.paint(poly([(mx - 66, fy0 + 48), (mx, fy0 - 4), (mx + 66, fy0 + 48)], 1), (200, 50, 50), shade=(0, -6, (150, 30, 40)),
            hi=(0, 4, (255, 110, 100)))
    for k in range(6):
        seed(c, mx - 48 + k * 19, fy0 + 140 + (k % 2) * 4, rng.uniform(-30, 30), 0.7)

    # roof antenna / satellite dish between Sky and the feeder (on the parapet)
    c.paint(ell(860, PAR - 34, 34, 30, -20), (220, 220, 226), shade=(-4, 3, (180, 180, 190)))
    c.line([(862, PAR - 30), (884, PAR - 54)], 3)
    c.paint(ell(886, PAR - 56, 4, 4), (220, 40, 50), ow=2)
    c.line([(860, PAR - 6), (860, PAR + 2)], 6, (90, 90, 100))

    lights = [(130, 400, 380, 0.55, (255, 220, 140)), (1460, 150, 900, 0.35, (200, 200, 255)),
              (1460, 560, 380, 0.25, (255, 120, 200))]
    light_pass(c, 0.78, lights, vign=0.4, front=0.35)
    c.glow(bx_, by_ + 6, 120, (255, 220, 140), 0.55)
    c.save("bg_rooftop.png")


# =========================================================================== characters
def paint_mina():
    """Dr. Mina Volt: wild hair, lab coat, clipboard. Faces RIGHT."""
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (250, 200, 160), (220, 146, 120)
    hair, hair_sh, hair_hi = (130, 50, 170), (90, 30, 130), (190, 110, 230)
    coat, coat_sh = (250, 250, 246), (196, 200, 220)
    top = (40, 190, 170)
    pants, pants_sh = (60, 50, 90), (40, 32, 66)

    # wild hair cloud behind everything
    rng = random.Random(5)
    pts = []
    for k in range(22):
        a = math.radians(k * 360 / 22)
        r = 46 + (16 if k % 2 else -2) + rng.uniform(-4, 4)
        pts.append((52 + r * math.cos(a) * 1.0, 44 + r * math.sin(a) * 0.82))
    c.paint(poly(pts, 1, True), hair, shade=(-4, 3, hair_sh), hi=(4, -3, hair_hi, 2),
            pattern=lambda p: [p.line(bez((40 + k * 8, 20), (30 + k * 10, 50), (36 + k * 9, 80)), 1.6, hair_sh)
                               for k in range(5)])
    # far arm (behind body) hanging, holding a pencil
    c.paint(cap([(40, 102), (30, 128), (32, 152)], 8), skin, shade=(-2, 0, skin_sh))
    c.paint(cap([(42, 100), (32, 126)], 15), coat, shade=(-3, 0, coat_sh))
    # legs
    c.paint(cap([(48, 176), (46, 210), (42, 232)], 13), pants, shade=(-3, 0, pants_sh))
    c.paint(cap([(64, 176), (66, 210), (72, 234)], 13), pants, shade=(-3, 0, pants_sh))
    for xh, xt, yt, yb in ((28, 58, 232, 248), (60, 94, 236, 252)):
        sh = shoe_shape(xh, xt, yt, yb)
        c.paint(sh, (255, 210, 60), shade=(0, -2, (220, 160, 40)),
                pattern=lambda pn, xh=xh, xt=xt, yb=yb: pn.rect(xh - 4, yb - 5, xt + 2, yb + 2, (250, 250, 240)))
        c.line([(xh - 2, yb - 4.5), (xt - 1, yb - 4.5)], 1.4)
    # lab coat body (long, open)
    body = poly([(36, 96), (56, 90), (76, 96), (82, 140), (86, 196), (64, 200), (56, 186), (46, 200), (26, 196),
                 (30, 140)], 2)
    c.paint(body, coat, shade=(-5, 0, coat_sh))
    c.paint(poly([(48, 94), (64, 94), (62, 172), (52, 172)], 1), top, ow=2.4, shade=(-2, 0, dk(top, 0.8)))
    c.line([(50, 176), (62, 176)], 2, pants)
    # lapels
    c.paint(poly([(46, 92), (52, 96), (50, 132), (40, 112)], 1), coat, ow=2.2, shade=(-1.5, 0, coat_sh))
    c.paint(poly([(66, 92), (60, 96), (62, 132), (72, 112)], 1), coat, ow=2.2, shade=(-1.5, 0, coat_sh))
    # pocket with pens
    c.paint(rect(66, 112, 78, 124), coat, ow=2.2)
    for k, col in enumerate(((220, 40, 60), (40, 90, 220), (40, 170, 80))):
        c.line([(68 + k * 4, 104), (68 + k * 4, 114)], 2.2, col)
    c.paint(rect(32, 160, 44, 174), coat, ow=2.2)
    # name badge
    c.paint(rect(36, 116, 46, 124), (255, 220, 70), ow=1.8)
    # neck
    c.paint(cap([(58, 78), (58, 94)], 10), skin, shade=(-2.5, 0, skin_sh))
    # near arm holding a clipboard against her chest
    c.paint(poly([(78, 110), (102, 104), (106, 140), (84, 146)], 1), (170, 110, 60), ow=2.6,
            pattern=lambda p: [p.rect(84, 112, 102, 140, (255, 252, 240)),
                               p.line([(87, 118), (100, 117)], 1, (120, 120, 140)),
                               p.line([(87, 124), (99, 123)], 1, (120, 120, 140)),
                               p.line([(87, 130), (97, 129)], 1, (120, 120, 140))])
    c.paint(rect(88, 102, 96, 108), (180, 180, 190), ow=2)
    c.paint(cap([(74, 100), (84, 124), (92, 120)], 8), skin, shade=(-2, 0, skin_sh))
    c.paint(cap([(72, 98), (82, 120)], 15), coat, shade=(-3, 0, coat_sh))
    c.paint(ell(94, 120, 6, 6.5), skin, shade=(-1.5, 1.5, skin_sh))

    # head facing right
    head = ell(58, 48, 24, 26) + poly([(40, 60), (52, 76), (68, 78), (80, 66), (82, 50)], 2) + ell(82, 56, 5.5, 5)
    c.paint(head, skin, shade=(-4, 3, skin_sh), hi=(4, 4, (255, 226, 200), 2.5))
    c.curve((82, 59), (85, 60), (86, 57), 1.4)
    c.paint(ell(66, 64, 6, 3.4), (255, 130, 140), ow=0, opacity=0.5)
    c.paint(ell(84, 62, 3.2, 2.4), (255, 130, 140), ow=0, opacity=0.45)
    # eyes: wide, worried, lashes
    eye(c, 62, 48, 8, 10, 65.5, 49, 2.5, lid=0.12, skin=skin, lashes=1, iris=(60, 140, 220))
    eye(c, 77.5, 47.5, 5.5, 9.2, 80, 48.5, 2.2, lid=0.12, skin=skin, lashes=1, iris=(60, 140, 220))
    c.line([(54, 33), (60, 31), (68, 34)], 2.2, hair_sh)
    c.line([(73, 34), (79, 31.5), (84, 33)], 2.0, hair_sh)
    # worried 'o' mouth
    c.paint(ell(74, 69, 3.5, 3), (130, 30, 50), ow=1.8)
    # front hair: spiky fringe and a pencil stuck in it
    fringe = [(30, 40), (36, 22), (46, 14), (60, 10), (72, 14), (82, 24), (86, 34), (78, 30), (72, 36), (66, 28),
              (58, 34), (52, 26), (44, 36), (38, 48), (34, 58)]
    c.paint(poly(fringe, 1), hair, shade=(-3, 2, hair_sh), hi=(2, 3, hair_hi, 1.5))
    c.line([(26, 6), (44, 22)], 4, (255, 210, 60))
    c.line([(26, 6), (22, 2)], 4, (250, 150, 160))
    c.paint(ell(36, 56, 6, 9), skin, shade=(-1.5, 1, skin_sh))  # ear
    c.paint(ell(36, 66, 2.6, 2.6), (60, 200, 220), ow=1.5)  # earring
    c.fit(margin=3)
    c.save("hs_dr_mina_volt.png")


def megaphone(c, x, y, s=1.0, col=(240, 70, 60)):
    """Megaphone pointing RIGHT; (x, y) = handle grip."""
    c.paint(rrect(x - 4 * s, y - 2 * s, x + 4 * s, y + 18 * s, 3 * s), (50, 50, 60), ow=2.4)
    cone = poly([(x - 14 * s, y - 8 * s), (x + 14 * s, y - 14 * s), (x + 38 * s, y - 28 * s), (x + 40 * s, y + 18 * s),
                 (x + 14 * s, y + 4 * s), (x - 14 * s, y + 2 * s)], 1)
    c.paint(cone, col, shade=(0, 3 * s, dk(col, 0.72)), hi=(0, -3 * s, lt(col, 0.4), 1.5 * s))
    c.paint(ell(x + 39 * s, y - 5 * s, 6 * s, 23 * s), (250, 250, 240), ow=2.4,
            pattern=lambda p: p.ell(x + 39 * s, y - 5 * s, 3 * s, 15 * s, (200, 200, 210)))
    c.paint(rrect(x - 20 * s, y - 10 * s, x - 10 * s, y + 4 * s, 3 * s), (250, 250, 240), ow=2.4)


def paint_sky():
    """Sky Rivera: beanie, denim jacket full of buttons, megaphone. Faces RIGHT."""
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (176, 112, 76), (138, 82, 60)
    hair, hair_sh = (40, 26, 30), (20, 12, 16)
    denim, denim_sh, denim_hi = (80, 120, 200), (52, 80, 152), (140, 176, 236)
    beanie = (240, 120, 40)
    pants, pants_sh = (110, 130, 70), (80, 96, 50)
    boot = (90, 56, 46)

    # short hair at the back
    c.paint(poly([(30, 40), (52, 30), (64, 40), (62, 74), (46, 82), (32, 70)], 2, True), hair, shade=(-3, 2, hair_sh))
    # far arm (fist raised, protest pose) behind the head side
    c.paint(cap([(42, 100), (22, 82), (14, 44)], 8.5), skin, shade=(-2, 0, skin_sh))
    c.paint(ell(13, 36, 7.5, 8.5), skin, shade=(-2, 1, skin_sh))
    for k in range(3):
        c.line([(8 + k * 4, 32), (8 + k * 4, 37)], 1.2, skin_sh)
    c.paint(cap([(44, 102), (24, 84)], 16), denim, shade=(-3, 0, denim_sh))
    # legs (cargo pants) + boots
    c.paint(cap([(48, 170), (44, 206), (40, 228)], 15), pants, shade=(-3, 0, pants_sh))
    c.paint(cap([(66, 170), (68, 206), (72, 230)], 15), pants, shade=(-3, 0, pants_sh))
    c.paint(rect(36, 196, 46, 208), pants, ow=2)
    for xh, xt, yt, yb in ((26, 60, 230, 248), (60, 96, 233, 251)):
        sh = shoe_shape(xh, xt, yt, yb, toe_h=0.6)
        c.paint(sh, boot, shade=(0, -2, dk(boot, 0.7)), hi=(2, 2, lt(boot, 0.3), 1.2))
        c.paint(rect(xh - 6, yb - 4, xt + 2, yb + 2), (40, 30, 30), ow=0, clip=sh)
    # torso: striped shirt under the jacket
    shirt = poly([(46, 96), (66, 96), (66, 168), (46, 168)], 1)
    c.paint(shirt, (250, 248, 236), ow=2.4,
            pattern=lambda p: [p.rect(40, y, 72, y + 4, (220, 50, 70)) for y in range(100, 168, 9)])
    # jacket
    jl = poly([(36, 96), (52, 92), (52, 170), (32, 166), (32, 130)], 2)
    jr = poly([(60, 92), (76, 96), (82, 130), (80, 166), (62, 170)], 2)
    c.paint(jl, denim, shade=(-4, 0, denim_sh), hi=(2, 0, denim_hi, 1))
    c.paint(jr, denim, shade=(-4, 0, denim_sh), hi=(2, 0, denim_hi, 1))
    c.line([(36, 158), (50, 160)], 1.4, denim_hi)
    c.line([(64, 160), (80, 158)], 1.4, denim_hi)
    # buttons all over the jacket
    for bx, by, col in ((40, 112, (255, 220, 60)), (44, 140, (255, 90, 160)), (70, 112, (90, 220, 120)),
                        (74, 136, (120, 180, 255)), (38, 126, (255, 140, 60))):
        c.paint(ell(bx, by, 4.2, 4.2), col, ow=1.8, hi=(-1, -1, (255, 255, 240)))
    # neck
    c.paint(cap([(56, 80), (56, 96)], 10), skin, shade=(-2.5, 0, skin_sh))
    # near arm holding the megaphone up to her mouth
    c.paint(cap([(76, 100), (88, 120), (82, 90)], 8.5), skin, shade=(-2, 0, skin_sh))
    c.paint(cap([(74, 98), (86, 116)], 16), denim, shade=(-3, 0, denim_sh))
    megaphone(c, 84, 82, 0.95)
    c.paint(ell(83, 88, 6, 6.5), skin, shade=(-1.5, 1, skin_sh))

    # head
    head = ell(56, 52, 23, 25) + poly([(38, 62), (50, 78), (66, 80), (78, 68), (80, 54)], 2) + ell(79, 58, 5, 5)
    c.paint(head, skin, shade=(-4, 3, skin_sh), hi=(4, 4, (210, 150, 110), 2.5))
    c.curve((80, 61), (83, 62), (84, 59), 1.4)
    c.paint(ell(66, 68, 5.5, 3.2), (240, 100, 110), ow=0, opacity=0.45)
    eye(c, 61, 52, 7.5, 9.5, 64.5, 53, 2.4, lid=0.25, lid_tilt=-0.8, skin=skin, lashes=1, iris=(110, 70, 40))
    eye(c, 75.5, 51.5, 5.2, 8.8, 78, 52.5, 2.1, lid=0.25, lid_tilt=-0.8, skin=skin, lashes=1, iris=(110, 70, 40))
    # determined brows
    c.line([(54, 41), (62, 42), (69, 45)], 2.6, hair)
    c.line([(72, 45), (78, 42), (83, 42)], 2.4, hair)
    # shouting mouth (half hidden by the megaphone bell is fine)
    c.paint(poly([(68, 70), (78, 69), (76, 77), (70, 77)], 1), (120, 30, 50), ow=1.8,
            pattern=lambda p: p.ell(73, 76, 3, 1.6, (230, 110, 120)))
    c.paint(ell(34, 58, 5.5, 8), skin, shade=(-1.5, 1, skin_sh))  # ear
    c.paint(ell(34, 68, 2.4, 2.4), (255, 220, 60), ow=1.4)
    # beanie with pompom
    c.paint(poly([(30, 44), (34, 24), (48, 14), (66, 14), (78, 22), (84, 40), (58, 36)], 2), beanie,
            shade=(-3, 2, dk(beanie, 0.75)), hi=(2, 3, lt(beanie, 0.35), 1.5),
            pattern=lambda p: [p.line([(36 + k * 7, 40), (40 + k * 6, 18)], 1.4, dk(beanie, 0.82)) for k in range(7)])
    c.paint(poly([(28, 40), (58, 34), (86, 38), (86, 46), (58, 42), (28, 48)], 1), dk(beanie, 0.85), ow=2.4)
    c.paint(ell(56, 12, 8, 7.5), (255, 230, 120), ow=2.4, hi=(-1.5, -1.5, (255, 250, 210)))
    # bangs peeking out
    c.paint(poly([(62, 42), (74, 42), (70, 50), (66, 46), (62, 50)], 1), hair, ow=2)
    c.fit(margin=3)
    c.save("hs_sky_rivera.png")


def paint_pigeon():
    """A very large, very rude pigeon. Drawn facing right, mirrored to face LEFT (toward the room)."""
    c = Canvas(90, 75, ow=3)
    grey, grey_sh, grey_hi = (150, 150, 176), (110, 108, 140), (196, 196, 216)
    # tail
    c.paint(poly([(10, 34), (2, 44), (6, 50), (24, 46)], 1), dk(grey, 0.8), ow=2.6)
    body = poly([(14, 36), (30, 24), (52, 22), (64, 30), (66, 48), (54, 60), (30, 60), (16, 50)], 2, True)
    c.paint(body, grey, shade=(-3, 3, grey_sh), hi=(3, -2, grey_hi, 1.5))
    # wing
    c.paint(poly([(22, 36), (44, 30), (54, 40), (46, 52), (26, 50)], 2, True), grey_sh, ow=2.4,
            pattern=lambda p: [p.line([(30, 44), (48, 40)], 1.2, (80, 80, 110)), p.line([(30, 48), (46, 46)], 1.2, (80, 80, 110))])
    # iridescent neck + head
    c.paint(ell(62, 30, 12, 13), (90, 170, 150), ow=2.6, pattern=lambda p: p.ell(64, 34, 9, 7, (170, 100, 190)))
    c.paint(ell(68, 18, 12, 11), grey, shade=(-2, 2, grey_sh), hi=(2, 2, grey_hi, 1))
    c.paint(poly([(78, 16), (88, 20), (78, 23)], 1), (230, 170, 80), ow=2.2)
    c.paint(ell(78, 15, 2.6, 1.6), (255, 255, 255), ow=1)
    # grumpy eye
    c.paint(ell(71, 15, 4, 4), (255, 140, 40), ow=1.8)
    c.paint(ell(71.5, 15.5, 1.8, 1.8), OUT, ow=0)
    c.line([(66, 9), (76, 12)], 2.2)
    # feet
    for fx in (34, 48):
        c.line([(fx, 58), (fx, 68)], 2.6, (230, 120, 110))
        c.line([(fx - 5, 70), (fx + 6, 70)], 2.6, (230, 120, 110))
    c.fit(margin=2)
    c.img = ImageOps.mirror(c.img)
    c.save("hs_pigeon.png")


def paint_nibbles():
    """Professor Nibbles, retired lab mascot, on his cushion. Mirrored to face LEFT."""
    c = Canvas(80, 60, ow=3)
    hamster(c, 40, 58, 0.78, cheeks=True)
    # tiny graduation cap
    c.paint(poly([(26, 10), (46, 4), (62, 10), (44, 16)], 1), (40, 40, 60), ow=2.2)
    c.paint(rect(38, 12, 50, 18), (40, 40, 60), ow=2)
    c.line([(46, 10), (56, 16), (56, 22)], 1.4, (255, 210, 60))
    c.fit(margin=2)
    c.img = ImageOps.mirror(c.img)
    c.save("hs_professor_nibbles.png")


# =========================================================================== icons
def paint_icon_cardboard_tube():
    def draw(c):
        cardboard_tube(c, 24, 92, 100, 36, 20)
    icon("icon_cardboard_tube.png", 0, draw)


def paint_icon_bird_seed():
    def draw(c):
        rng = random.Random(8)
        c.paint(poly([(18, 112), (110, 112), (98, 92), (64, 74), (30, 92)], 2, True), (200, 160, 110),
                shade=(4, 4, (160, 120, 80)), hi=(-3, -3, (230, 200, 150), 2))
        for k in range(14):
            seed(c, rng.uniform(30, 98), rng.uniform(70, 104) - (k // 5) * 10, rng.uniform(0, 180), 1.6)
        for x_, y_, a in ((40, 40, 30), (70, 30, -20), (90, 50, 60)):
            seed(c, x_, y_, a, 1.8)
    icon("icon_bird_seed.png", 0, draw)


def paint_icon_hamster_trap():
    def draw(c):
        cardboard_tube(c, 18, 84, 92, 46, 20)
        for k, (x_, y_, a) in enumerate(((104, 54, 20), (110, 74, -40), (96, 72, 70), (116, 40, 10))):
            seed(c, x_, y_, a, 1.3)
        c.paint(poly([(30, 70), (70, 52), (76, 66), (36, 84)], 1), (255, 240, 120), ow=2.5)
        c.text(52, 68, "HOTEL", 8.5, (200, 40, 60), angle=24)
    icon("icon_hamster_trap.png", 0, draw)


def paint_icon_nibbles_in_tube():
    def draw(c):
        cardboard_tube(c, 14, 90, 76, 58, 22)
        hamster(c, 92, 98, 0.95, sleepy=True)
    icon("icon_nibbles_in_tube.png", 0, draw)


def paint_icon_spare_batteries():
    def draw(c):
        for (x0, y0, x1, y1, col) in ((20, 92, 96, 36, (40, 170, 90)), (34, 108, 110, 52, (230, 70, 50))):
            body = cap([(x0, y0), (x1, y1)], 28)
            ang = math.atan2(y1 - y0, x1 - x0)
            c.paint(body, (40, 40, 48), shade=(4, 4, (20, 20, 26)))
            mx, my = x0 + (x1 - x0) * 0.62, y0 + (y1 - y0) * 0.62
            c.paint(cap([(x0, y0), (mx, my)], 28), col, ow=0, clip=body, shade=(4, 4, dk(col, 0.75)),
                    hi=(-3, -3, lt(col, 0.4), 2))
            c.paint(body, (0, 0, 0, 0), ow=4)
            tx, ty = x1 + math.cos(ang) * 16, y1 + math.sin(ang) * 16
            c.paint(cap([(x1 + math.cos(ang) * 10, y1 + math.sin(ang) * 10), (tx, ty)], 10), (220, 170, 90), ow=3)
            c.text(x0 + (x1 - x0) * 0.35, y0 + (y1 - y0) * 0.35, "AA", 11, (255, 255, 240),
                   angle=-math.degrees(ang))
    icon("icon_spare_batteries.png", 0, draw)


def paint_icon_retirement_plan():
    def draw(c):
        paper = poly([(24, 14), (100, 10), (106, 116), (22, 118)], 1)
        c.paint(paper, (255, 250, 236), shade=(4, 4, (220, 210, 196)),
                pattern=lambda p: [p.line([(34, 44 + k * 10), (94, 42 + k * 10)], 1.4, (170, 170, 190)) for k in range(5)])
        c.text(63, 26, "RETIREMENT", 10, (40, 60, 140))
        c.text(63, 38, "PLAN", 9, (40, 60, 140))
        c.curve((32, 104), (44, 92), (56, 104), 2, (40, 60, 200))
        c.line([(56, 104), (62, 98)], 2, (40, 60, 200))
        px, py = 86, 98
        c.paint(ell(px, py, 9, 7), (200, 40, 60), ow=0)
        for dx, dy in ((-9, -10), (-3, -14), (4, -14), (10, -9)):
            c.paint(ell(px + dx, py + dy, 3.4, 3.8), (200, 40, 60), ow=0)
    icon("icon_retirement_plan.png", -6, draw)


def paint_icon_safety_goggles():
    def draw(c):
        goggles(c, 64, 64, 1.25)
    icon("icon_safety_goggles.png", -8, draw)


def paint_icon_protest_button():
    def draw(c):
        c.paint(ell(64, 64, 52, 52), (255, 90, 150), shade=(5, 5, (210, 50, 110)), hi=(-4, -4, (255, 170, 200), 3))
        c.paint(ell(64, 64, 42, 42), (255, 240, 120), ow=3)
        hamster(c, 64, 84, 0.72)
        c.line([(84, 60), (94, 40)], 5, (255, 200, 180))
        c.paint(ell(95, 37, 6, 6), (255, 200, 180), ow=2.2)
        c.text(64, 22, "FREE", 13, (255, 255, 255), stroke=2)
        c.text(64, 104, "NIBBLES", 13, (255, 255, 255), stroke=2)
    icon("icon_protest_button.png", 0, draw)


ASSETS = {"bg_science_hall": paint_science_hall, "bg_lab": paint_lab, "bg_rooftop": paint_rooftop,
          "hs_dr_mina_volt": paint_mina, "hs_sky_rivera": paint_sky, "hs_pigeon": paint_pigeon,
          "hs_professor_nibbles": paint_nibbles,
          "icon_cardboard_tube": paint_icon_cardboard_tube, "icon_bird_seed": paint_icon_bird_seed,
          "icon_hamster_trap": paint_icon_hamster_trap, "icon_nibbles_in_tube": paint_icon_nibbles_in_tube,
          "icon_spare_batteries": paint_icon_spare_batteries, "icon_retirement_plan": paint_icon_retirement_plan,
          "icon_safety_goggles": paint_icon_safety_goggles, "icon_protest_button": paint_icon_protest_button}


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
