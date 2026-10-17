#!/usr/bin/env python3
"""
Big Night Out -- extra Act 1 (Freshman) art: Gil's room 216, the Student Union cafeteria, the library's
upper stacks, their new characters (Boomer the sleepwalker, Doreen the night cook, Kyle in the possum
suit, Percival Thorne the slam poet), the props that appear or disappear, and the new item icons.

All original, drawn procedurally with the helpers in paint.py (same style: bold dark outlines,
warm saturated cel shading, big-headed characters).

Usage:  python3 tools/art/act1_more.py              # paint everything
        python3 tools/art/act1_more.py kyle icon    # paint assets whose name contains these words
Prop positions are read from Assets/_Project/World/act1.json so the art lines up with the click boxes.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, W_BG, H_BG, WALL_Y, Canvas, Image, Sh, baseboard, bankers_lamp, bez, block_wall,  # noqa: E402
                   book_row, cap, carpet, checker_floor, dk, door, ell, ell_pts, eye, icon, light_pass, lt, mix,
                   night_window, plank_floor, poly, rect, rrect, shoe_shape, wonky)

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "act1.json")


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


def trim_bottom(c):
    """Shift a prop down so its lowest solid pixel sits on the bottom edge (the sprite pivot is the feet)."""
    import numpy as np
    a = np.asarray(c.img.getchannel("A"))
    rows = np.nonzero((a > 16).any(axis=1))[0]
    if len(rows) == 0:
        return
    gap = a.shape[0] - 1 - rows.max()
    if gap > 0:
        out = Image.new("RGBA", c.img.size, (0, 0, 0, 0))
        out.alpha_composite(c.img.crop((0, 0, c.img.width, c.img.height - gap)), (0, gap))
        c.img = out


def poster_rect(c, x0, y0, x1, y1, col, rng, tape=(240, 232, 200)):
    c.paint(wonky(x0, y0, x1, y1, 2.5, rng), col, shade=(-4, -4, dk(col, 0.8)))
    for tx, ty in ((x0 + 6, y0 + 3), (x1 - 6, y0 + 3)):
        c.paint(rect(tx - 10, ty - 6, tx + 10, ty + 6), tape, ow=0, opacity=0.85)


# =========================================================================== backgrounds
def paint_gil_room():
    """Room 216: bunk bed, record crate, desk with turntable, window. Boomer, the alarm clock and the
    air freshener are separate sprites."""
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(216)
    block_wall(c, 0, 0, W_BG, WALL_Y, (60, 92, 84), (112, 150, 120), seed=216)
    c.paint(rect(0, 0, W_BG, 46), (40, 60, 56), ow=0)
    c.paint(rect(-10, 40, W_BG + 10, 54), (220, 200, 160), ow=3, shade=(0, -4))
    plank_floor(c, (150, 96, 60), seed=217)
    baseboard(c, color=(80, 50, 36))
    # rug with a record-groove pattern
    c.paint(ell(1000, 930, 430, 62), (60, 50, 70), ow=3,
            pattern=lambda p: [p.ell(1000, 930, 430 - k * 50, 62 - k * 7, (60, 50, 70) if k % 2 else (80, 66, 96))
                               for k in range(8)] + [p.ell(1000, 930, 40, 7, (220, 60, 60))])

    # --- posters
    poster_rect(c, 560, 150, 760, 420, (250, 196, 80), rng)
    c.paint(ell(660, 260, 66, 66), (40, 30, 30), ow=3,
            pattern=lambda p: [p.ell(660, 260, 50 - k * 10, 50 - k * 10, (40 + k * 8, 30, 30)) for k in range(4)])
    c.paint(ell(660, 260, 18, 18), (220, 60, 60), ow=2.5)
    c.text(660, 360, "SPIN", 34, (40, 30, 30), "Display")
    c.text(660, 396, "OR DIE", 20, (40, 30, 30))
    poster_rect(c, 820, 190, 960, 400, (60, 120, 200), rng)
    c.paint(cap([(870, 360), (900, 250), (930, 236)], 10), (240, 196, 80), ow=3)  # saxophone
    c.paint(ell(868, 360, 20, 14), (240, 196, 80), ow=3)
    c.text(890, 222, "JAZZ", 22, (255, 250, 230))
    c.text(890, 386, "NIGHT", 16, (255, 250, 230))
    # a sign taped to the wall
    poster_rect(c, 1080, 300, 1270, 400, (250, 248, 236), rng)
    c.text(1175, 332, "QUIET HOURS", 16, (180, 40, 50))
    c.text(1175, 362, "(BOOMER, THIS", 13, (60, 60, 80), "Bold")
    c.text(1175, 382, "MEANS YOU)", 13, (60, 60, 80), "Bold")

    # --- window over the right wall, with a hook for the air freshener
    fx0, fy0, fx1, fy1 = box("gil_room", "Air freshener")
    night_window(c, 1340, 190, 1600, 440, seed=218)
    c.paint(ell((fx0 + fx1) / 2, 474, 7, 7), (200, 200, 210), ow=2.5)  # latch hook

    # --- bunk bed (left)
    x0, y0, x1, y1 = box("gil_room", "Bunk bed")
    wood = (150, 96, 56)
    for px in (x0 + 8, x1 - 8):
        c.paint(rect(px - 12, y0, px + 12, y1), wood, shade=(-4, 0, dk(wood, 0.72)), hi=(3, 0, lt(wood, 0.3)))
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2, 10, 0.4)
    for top, sheet, blanket in ((y0 + 70, (240, 236, 220), (60, 90, 170)), (y0 + 260, (240, 236, 220), (180, 70, 60))):
        c.paint(rect(x0 + 18, top, x1 - 18, top + 50), wood, shade=(0, -4, dk(wood, 0.72)))
        c.paint(rrect(x0 + 22, top - 26, x1 - 22, top + 6, 8), blanket, shade=(0, -5, dk(blanket, 0.75)),
                hi=(0, 4, lt(blanket, 0.3)))
        c.paint(ell(x0 + 60, top - 26, 34, 14), sheet, shade=(0, -3))
    c.paint(cap([(x0 + 20, y0 + 30), (x1 - 20, y0 + 30)], 8), wood, ow=3)
    # top bunk is Gil's (saxophone pillow), bottom bunk empty and rumpled
    c.paint(rrect(x0 + 120, y0 + 10, x0 + 200, y0 + 48, 6), (250, 220, 120), ow=3)
    c.text(x0 + 160, y0 + 30, "GIL", 14, (120, 70, 30))
    c.paint(rrect(x0 + 130, y0 + 210, x0 + 230, y0 + 248, 6), (220, 60, 50), ow=3)
    c.text(x0 + 180, y0 + 229, "BOOMER", 12, (255, 250, 230))
    # ladder on the bunk
    for k in range(4):
        c.line([(x1 - 10, y0 + 90 + k * 50), (x1 + 20, y0 + 90 + k * 50)], 5, OUT)
        c.line([(x1 - 10, y0 + 90 + k * 50), (x1 + 20, y0 + 90 + k * 50)], 2.5, wood)
    c.line([(x1 + 22, y0 + 70), (x1 + 22, y1)], 7, OUT)
    c.line([(x1 + 22, y0 + 70), (x1 + 22, y1)], 4, wood)
    # socks on the floor by the bunk (the smell)
    for sx, sy, col in ((300, 840, (240, 240, 230)), (380, 862, (200, 200, 210)), (240, 880, (240, 240, 230))):
        c.paint(cap([(sx, sy), (sx + 30, sy + 4), (sx + 38, sy - 8)], 12), col, ow=3)
    for k in range(3):
        c.curve((330 + k * 20, 820), (320 + k * 20, 790), (336 + k * 20, 770), 2.4, (120, 160, 60), 0.6)

    # --- record crate
    x0, y0, x1, y1 = box("gil_room", "Record crate")
    cr = (90, 120, 200)
    c.shadow((x0 + x1) / 2, y1 - 4, (x1 - x0) / 2 + 4, 7)
    rec_cols = [(220, 60, 60), (250, 200, 70), (60, 160, 120), (130, 80, 170), (40, 40, 40), (240, 140, 60)]
    for k in range(9):
        rx = x0 + 10 + k * 12
        col = rec_cols[k % len(rec_cols)]
        c.paint(rect(rx, y0 - 10 + (k % 3) * 5, rx + 18, y0 + 50), col, ow=2.5, shade=(-2, 0, dk(col, 0.75)))
    c.paint(rect(x0, y0 + 30, x1, y1 - 4), cr, shade=(-5, 0, dk(cr, 0.72)), hi=(0, 3, lt(cr, 0.3)),
            pattern=lambda p: [p.rect(x0 + 10 + k * 28, y0 + 42, x0 + 26 + k * 28, y1 - 14, dk(cr, 0.7)) for k in range(4)])

    # --- desk with turntable (turntable inside its box, alarm clock spot left empty)
    tx0, ty0, tx1, ty1 = box("gil_room", "Turntable")
    dsk = (160, 104, 64)
    dx0, dx1, dtop = 900, 1300, ty1
    c.shadow((dx0 + dx1) / 2, WALL_Y + 6, 210, 10, 0.4)
    for lx in (dx0 + 16, dx1 - 16):
        c.paint(rect(lx - 10, dtop + 10, lx + 10, WALL_Y + 4), dk(dsk, 0.85), ow=3)
    c.paint(rect(dx1 - 150, dtop + 14, dx1 - 26, WALL_Y - 40), dsk, shade=(-5, 0, dk(dsk, 0.72)),
            pattern=lambda p: p.rect(dx1 - 140, dtop + 40, dx1 - 36, dtop + 50, dk(dsk, 0.7)))
    c.paint(rect(dx0 - 10, dtop, dx1 + 10, dtop + 18), dsk, hi=(0, 3, lt(dsk, 0.35)), shade=(0, -4, dk(dsk, 0.75)))
    tb = (40, 36, 44)
    c.paint(rrect(tx0 + 4, ty0 + 22, tx1 - 4, ty1, 6), (190, 120, 70), shade=(-3, -3, (140, 84, 50)),
            hi=(0, 3, (230, 170, 110)))
    c.paint(ell(tx0 + 62, ty0 + 30, 52, 12), tb, ow=3,
            pattern=lambda p: [p.ell(tx0 + 62, ty0 + 30, 44 - k * 9, 10 - k * 2, (60 + k * 6, 54, 64)) for k in range(4)])
    c.paint(ell(tx0 + 62, ty0 + 30, 10, 3), (250, 196, 80), ow=1.6)
    c.line([(tx1 - 22, ty0 + 20), (tx1 - 30, ty0 + 30), (tx0 + 96, ty0 + 32)], 3, (200, 200, 210))
    c.paint(ell(tx1 - 22, ty0 + 20, 6, 6), (200, 200, 210), ow=2)
    # speakers either side
    for sx in (dx0 + 4, dx1 - 64):
        pass
    c.paint(rrect(dx0 - 4, dtop - 110, dx0 + 56, dtop, 4), (60, 50, 50), shade=(-3, 0),
            pattern=lambda p: [p.ell(dx0 + 26, dtop - 76, 18, 18, (30, 26, 30)), p.ell(dx0 + 26, dtop - 30, 12, 12, (30, 26, 30))])

    # --- door to the hallway (right)
    x0, y0, x1, y1 = box("gil_room", "Door to hallway")
    door(c, x0 + 6, y0 + 4, x1 - 6, y1 - 6, (70, 110, 80), knob="L")
    c.paint(rrect(x0 + 30, y0 + 50, x1 - 30, y0 + 100, 4), (250, 248, 236), ow=3)
    c.text((x0 + x1) / 2, y0 + 75, "EXIT", 14, (60, 60, 80))

    lights = [(1470, 300, 420, 0.25, (150, 170, 255)), (1000, 560, 500, 0.5, (255, 220, 150)),
              (960, 120, 900, 0.18, (255, 220, 170))]
    light_pass(c, 0.72, lights, vign=0.4)
    c.save("bg_gil_room.png")


def paint_student_union():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(4040)
    wall = (232, 176, 104)
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, (200, 140, 86), wall), ow=0)
    # tiled lower wall
    tile = (70, 150, 150)

    def tiles(p):
        for x in range(0, W_BG, 40):
            p.line([(x, 600), (x, WALL_Y)], 1.6, dk(tile, 0.8))
        for y in range(600, WALL_Y, 40):
            p.line([(0, y), (W_BG, y)], 1.6, dk(tile, 0.8))
    c.paint(rect(0, 600, W_BG, WALL_Y), tile, ow=0, pattern=tiles)
    c.paint(rect(-10, 592, W_BG + 10, 608), (250, 220, 150), ow=3, shade=(0, -3))
    paint.drop_ceiling(c, 80, (220, 210, 190), panels=(400, 960, 1520))
    checker_floor(c, (230, 220, 200), (120, 150, 160), vp=(960, 300))
    baseboard(c, color=(60, 110, 110))
    # pennant banner
    paint.bunting(c, 1000, 1560, 120, "GO POKEY", [(150, 150, 160), (240, 120, 160)], sag=26)

    # --- exit doors (glass, night outside)
    x0, y0, x1, y1 = box("student_union", "Quad")
    fr = (170, 176, 184)
    c.paint(rect(x0 - 10, y0 - 10, x1 + 10, y1), fr, shade=(-4, 0, dk(fr, 0.75)))
    for k in range(2):
        gx0 = x0 + 4 + k * (x1 - x0) / 2
        gx1 = gx0 + (x1 - x0) / 2 - 8
        c.paint(rect(gx0, y0 + 4, gx1, y1 - 4), ("v", (40, 40, 100), (120, 60, 120)), ow=3,
                pattern=lambda p, gx0=gx0: [p.ell(gx0 + 20, y0 + 60, 3, 3, (255, 250, 220)),
                                            p.poly([(gx0 + 6, y1 - 30), (gx0 + 30, y0 + 20), (gx0 + 40, y0 + 20),
                                                    (gx0 + 16, y1 - 30)], (160, 140, 200))])
        c.paint(rrect(gx1 - 14 if k == 0 else gx0 + 6, y0 + 150, gx1 - 6 if k == 0 else gx0 + 14, y0 + 230, 3),
                (210, 214, 220), ow=2)
    c.paint(rrect(x0 + 10, y0 - 54, x1 - 10, y0 - 18, 5), (40, 40, 40), ow=3)
    c.text((x0 + x1) / 2, y0 - 36, "QUAD", 18, (90, 255, 140))

    # --- menu board
    x0, y0, x1, y1 = box("student_union", "Menu board")
    c.paint(rrect(x0, y0, x1, y1, 6), (40, 36, 30), shade=(-4, -4), hi=(3, 3, (90, 76, 60), 2))
    c.paint(rect(x0 + 12, y0 + 12, x1 - 12, y1 - 12), (36, 56, 44), ow=2)
    c.text((x0 + x1) / 2, y0 + 34, "TONIGHT", 22, (250, 220, 120), "Display")
    for k, (item, price) in enumerate((("ONION SOUP", "$2"), ("MYSTERY LOAF", "$3"), ("POSSUM WAFFLE", "MASCOT ONLY"))):
        y = y0 + 70 + k * 30
        c.text(x0 + 24, y, item, 15, (245, 245, 235), "Bold", anchor="lm")
        c.text(x1 - 24, y, price, 15, (240, 150, 160) if k == 2 else (245, 245, 235), "Bold", anchor="rm")

    # --- grill counter
    x0, y0, x1, y1 = box("student_union", "Grill counter")
    steel = (196, 200, 208)
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2 + 10, 10, 0.4)
    # hood above
    c.paint(rect(x0 + 40, y0 + 6, x1 - 40, y0 + 34), (60, 60, 66), ow=3)  # griddle back
    c.paint(rect(x0, y0 + 30, x1, y1), steel, shade=(-6, 0, dk(steel, 0.72)), hi=(0, 4, lt(steel, 0.4)),
            pattern=lambda p: [p.line([(x0 + 10 + k * 70, y0 + 46), (x0 + 10 + k * 70, y1 - 6)], 2, dk(steel, 0.8))
                               for k in range(7)])
    c.paint(rect(x0 - 8, y0 + 22, x1 + 8, y0 + 40), lt(steel, 0.2), ow=3)
    # soup pot + possum waffle iron on the counter top
    c.paint(rrect(x0 + 40, y0 - 50, x0 + 130, y0 + 24, 8), (180, 60, 50), shade=(-4, 0, (130, 40, 36)),
            hi=(3, 0, (230, 110, 90)))
    c.paint(ell(x0 + 85, y0 - 50, 46, 9), (200, 160, 90), ow=3)
    for k in range(3):
        c.curve((x0 + 60 + k * 18, y0 - 60), (x0 + 50 + k * 18, y0 - 86), (x0 + 66 + k * 18, y0 - 110), 2.4,
                (255, 255, 255), 0.5)
    c.text(x0 + 85, y0 - 8, "SOUP", 13, (255, 240, 220))
    wx = x0 + 300
    c.paint(rrect(wx - 70, y0 - 6, wx + 70, y0 + 24, 6), (60, 60, 66), ow=3)
    c.paint(ell(wx, y0 - 10, 56, 16), (90, 90, 100), shade=(0, -3, (60, 60, 66)), hi=(0, 3, (150, 150, 160)))
    for ex in (wx - 34, wx + 34):  # possum ears on the lid
        c.paint(ell(ex, y0 - 26, 12, 12), (90, 90, 100), ow=3, pattern=lambda p, ex=ex: p.ell(ex, y0 - 26, 6, 6, (240, 140, 160)))
    c.paint(ell(wx, y0 - 8, 6, 5), (240, 140, 160), ow=2)

    # --- soda fountain (out of order)
    x0, y0, x1, y1 = box("student_union", "Soda fountain")
    red = (210, 50, 50)
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2 + 6, 7)
    c.paint(rrect(x0, y0, x1, y1, 8), red, shade=(-5, 0, dk(red, 0.72)), hi=(0, 4, lt(red, 0.35)))
    c.paint(rrect(x0 + 12, y0 + 16, x1 - 12, y0 + 90, 5), (250, 240, 220), ow=3)
    c.text((x0 + x1) / 2, y0 + 40, "FIZZ", 22, red, "Display")
    c.text((x0 + x1) / 2, y0 + 70, "FOUNTAIN", 12, (60, 60, 70))
    for k in range(3):
        nx = x0 + 30 + k * 35
        c.paint(rrect(nx - 8, y0 + 110, nx + 8, y0 + 140, 3), (200, 200, 210), ow=2.5)
    c.paint(rect(x0 + 12, y0 + 160, x1 - 12, y0 + 170), (60, 60, 66), ow=2)
    c.paint(wonky(x0 - 8, y0 + 120, x1 + 8, y0 + 168, 2, rng), (250, 240, 120), shade=(-3, -3, (210, 190, 80)))
    c.text((x0 + x1) / 2, y0 + 144, "OUT OF ORDER", 13, (180, 30, 30))
    c.paint(rect(x0 + 14, y1 - 60, x1 - 14, y1 - 14), dk(red, 0.8), ow=2.5)

    # --- Kyle's table (Kyle himself is a sprite)
    kx0, ky0, kx1, ky1 = box("student_union", "Kyle")
    tw = (200, 200, 190)
    tx = kx1 + 120
    c.shadow(tx, 852, 120, 10, 0.4)
    c.paint(rect(tx - 10, 760, tx + 10, 850), (80, 80, 90), ow=3)
    c.paint(ell(tx, 850, 50, 8), (80, 80, 90), ow=3)
    c.paint(ell(tx, 756, 120, 20), tw, shade=(0, -4, dk(tw, 0.8)), hi=(0, 3, lt(tw, 0.4)))
    c.paint(rrect(tx - 60, 726, tx - 20, 752, 4), (250, 250, 240), ow=2.5)  # tray
    c.paint(ell(tx + 40, 740, 16, 7), (240, 236, 220), ow=2.5)
    # chairs stacked upside down on a table in the back corner
    bx = 1850
    c.paint(rect(bx - 70, 690, bx + 70, 704), tw, ow=3, shade=(0, -3))
    c.paint(rect(bx - 6, 704, bx + 6, WALL_Y), (80, 80, 90), ow=2.5)
    for lx in (bx - 50, bx + 40):
        c.paint(rect(lx, 600, lx + 8, 690), (220, 120, 60), ow=2.5)
    c.paint(rect(bx - 54, 640, bx + 50, 656), (220, 120, 60), ow=2.5)

    # --- bulletin board
    x0, y0, x1, y1 = box("student_union", "Bulletin board")
    cork = (196, 140, 80)
    c.paint(wonky(x0, y0, x1, y1, 1.5, rng), (120, 80, 48), shade=(-4, -4))
    c.paint(rect(x0 + 12, y0 + 12, x1 - 12, y1 - 12), cork, ow=2,
            pattern=lambda p: [p.ell(rng.uniform(x0, x1), rng.uniform(y0, y1), 1.4, 1.4, dk(cork, 0.8)) for _ in range(60)])
    poster_rect(c, x0 + 22, y0 + 24, x0 + 120, y0 + 150, (40, 30, 50), rng)
    c.text(x0 + 71, y0 + 50, "STACKS", 13, (250, 220, 120))
    c.text(x0 + 71, y0 + 70, "SLAM", 17, (250, 220, 120), "Display")
    c.paint(ell(x0 + 71, y0 + 106, 14, 8), (220, 50, 60), ow=2)  # beret
    c.text(x0 + 71, y0 + 134, "37-0", 12, (255, 250, 230))
    poster_rect(c, x0 + 108, y0 + 100, x1 - 18, y1 - 22, (250, 248, 236), rng)
    c.text((x0 + x1 + 90) / 2, y0 + 120, "LOST", 11, (180, 40, 50))
    c.text((x0 + x1 + 90) / 2, y0 + 138, "GLOVE", 9, (60, 60, 70), "Bold")

    lights = [(400, 100, 500, 0.4, (255, 240, 200)), (960, 100, 500, 0.4, (255, 240, 200)),
              (1520, 100, 500, 0.4, (255, 240, 200))]
    light_pass(c, 0.78, lights, vign=0.38)
    c.save("bg_student_union.png")


def paint_library_stacks():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(3737)
    wp = (70, 54, 82)

    def paper(p):
        for x in range(0, W_BG, 60):
            p.rect(x, 60, x + 22, 560, lt(wp, 0.06))
    c.paint(rect(0, 0, W_BG, 560), ("vy", 60, 560, dk(wp, 0.75), wp), ow=0, pattern=paper)
    # sloped attic beams
    beam = (96, 60, 40)
    for bx in (0, 640, 1280, 1920):
        c.paint(rect(bx - 22, 0, bx + 22, 560), beam, shade=(-5, 0, dk(beam, 0.72)), hi=(4, 0, lt(beam, 0.25)))
    c.paint(rect(-10, 0, W_BG + 10, 44), dk(beam, 0.8), ow=3)
    wd = (100, 60, 40)
    c.paint(rect(0, 560, W_BG, WALL_Y), wd, ow=0,
            pattern=lambda p: [p.rect(x, 590, x + 100, 760, dk(wd, 0.85)) for x in range(10, W_BG, 120)])
    c.paint(rect(-10, 552, W_BG + 10, 572), (80, 48, 30), ow=3, hi=(0, 4, (130, 86, 56)), shade=(0, -4))
    plank_floor(c, (120, 76, 46), seed=3738)
    baseboard(c, color=(60, 36, 24))
    # cobwebs in the corners
    for cx, sgn in ((60, 1), (1860, -1)):
        for k in range(4):
            c.curve((cx, 50), (cx + sgn * (30 + k * 26), 70 + k * 18), (cx + sgn * (8 + k * 34), 50 + k * 34), 1.4,
                    (220, 220, 230), 0.5)

    # --- round window with the moon
    c.paint(ell(1300, 230, 110, 110), (150, 100, 60), shade=(-5, -5, (110, 70, 40)))

    def moon(p):
        p.ell(1300, 230, 100, 100, (40, 40, 100))
        p.ell(1336, 196, 34, 34, (255, 246, 200))
        for sx, sy in ((1240, 180), (1270, 290), (1350, 280), (1230, 250)):
            p.ell(sx, sy, 2, 2, (255, 250, 220))
    c.paint(ell(1300, 230, 96, 96), (40, 40, 100), ow=3, pattern=moon)
    c.line([(1300, 134), (1300, 326)], 5, (150, 100, 60))
    c.line([(1204, 230), (1396, 230)], 5, (150, 100, 60))

    # --- hatch in the floor with the ladder poking up (left)
    x0, y0, x1, y1 = box("library_stacks", "Ladder down")
    c.paint(poly([(x0 - 10, y1 - 20), (x1 + 10, y1 - 20), (x1 + 30, y1 + 30), (x0 - 30, y1 + 30)]), (30, 20, 16), ow=3)
    lad = (170, 110, 60)
    for k in range(4):
        y = y0 + 40 + k * 50
        c.line([(x0 + 30, y), (x1 - 30, y)], 7, OUT)
        c.line([(x0 + 30, y), (x1 - 30, y)], 3.5, lad)
    for rx in (x0 + 30, x1 - 30):
        c.line([(rx, y0 + 10), (rx, y1 + 20)], 8, OUT)
        c.line([(rx, y0 + 10), (rx, y1 + 20)], 4.5, lad)
    c.paint(rect(x0 + 20, y0 + 2, x1 - 20, y0 + 14), (214, 168, 70), ow=2)
    # safety railing
    c.line([(x1 + 10, y0 + 30), (x1 + 10, y1 - 10)], 5, (60, 40, 30))
    c.line([(x0 - 20, y0 + 30), (x1 + 10, y0 + 30)], 5, (60, 40, 30))

    # --- dusty shelves
    x0, y0, x1, y1 = box("library_stacks", "Dusty shelves")
    sw = (96, 58, 36)
    c.shadow((x0 + x1) / 2, y1, (x1 - x0) / 2 + 20, 12, 0.5)
    c.paint(wonky(x0, y0 + 10, x1, y1, 1.5, rng), sw, shade=(-8, 0, dk(sw, 0.72)), hi=(6, 0, lt(sw, 0.2)))
    c.paint(rect(x0 + 16, y0 + 34, x1 - 16, y1 - 18), (40, 24, 18), ow=3)
    cols = [(120, 110, 100), (100, 120, 110), (140, 110, 80), (110, 96, 120), (150, 140, 120)]
    shelves = [y0 + 34 + k * (y1 - y0 - 52) / 5 for k in range(6)]
    for i in range(5):
        top, bot = shelves[i], shelves[i + 1]
        book_row(c, x0 + 20, x1 - 20, bot - 10, (bot - top) * 0.5, (bot - top) * 0.8, rng, cols)
        c.paint(rect(x0 + 10, bot - 10, x1 - 10, bot), lt(sw, 0.1), ow=3)
        c.paint(rect(x0 + 18, top + 4, x1 - 18, top + 10), (220, 220, 220), ow=0, opacity=0.25)  # dust
    c.paint(wonky(x0 - 10, y0, x1 + 10, y0 + 26, 1.2, rng), lt(sw, 0.1), shade=(0, -5, dk(sw, 0.72)))

    # --- slam chalkboard
    x0, y0, x1, y1 = box("library_stacks", "Slam chalkboard")
    c.paint(rrect(x0, y0, x1, y1, 5), (130, 86, 50), shade=(-4, -4))
    c.paint(rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10), (40, 60, 50), ow=2)
    c.text((x0 + x1) / 2, y0 + 34, "STACKS SLAM", 18, (240, 240, 230))
    c.text((x0 + x1) / 2, y0 + 64, "CHAMP: P. THORNE", 12, (240, 240, 230), "Bold")
    c.text((x0 + x1) / 2, y0 + 88, "37 - 0", 18, (250, 220, 120))
    for k in range(9):
        fx, fy = x0 + 30 + k * 18, y0 + 122
        c.paint(ell(fx, fy, 6, 6), (0, 0, 0, 0), ow=1.4, oc=(240, 240, 230))
        c.line([(fx - 3, fy + 2.5), (fx + 3, fy + 2.5)], 1.2, (240, 240, 230))
        c.line([(fx - 2, fy - 1), (fx - 2, fy + 3)], 1, (140, 190, 255))

    # --- open mic + beanbags
    x0, y0, x1, y1 = box("library_stacks", "Open mic")
    mx = (x0 + x1) / 2
    c.shadow(mx, y1 - 4, 34, 6)
    c.paint(ell(mx, y1 - 8, 30, 8), (50, 50, 56), ow=3)
    c.line([(mx, y1 - 10), (mx, y0 + 60)], 7, OUT)
    c.line([(mx, y1 - 10), (mx, y0 + 60)], 3.5, (170, 170, 180))
    c.line([(mx, y0 + 60), (mx - 20, y0 + 30)], 6, OUT)
    c.line([(mx, y0 + 60), (mx - 20, y0 + 30)], 3, (170, 170, 180))
    c.paint(ell(mx - 24, y0 + 22, 11, 16, -30), (60, 60, 66), hi=(-2, -2, (140, 140, 150), 1.5),
            pattern=lambda p: [p.line([(mx - 34, y0 + 14 + k * 5), (mx - 14, y0 + 14 + k * 5)], 0.8, (110, 110, 120)) for k in range(6)])
    for bx, col in ((1460, (200, 70, 80)), (1560, (70, 120, 180)), (1500, (220, 170, 60))):
        by = 800 if bx != 1500 else 820
        c.shadow(bx, by + 10, 52, 8)
        c.paint(poly(ell_pts(bx, by - 10, 50, 30), 1), col, shade=(4, 4, dk(col, 0.72)), hi=(-3, -3, lt(col, 0.3), 2))

    # --- bust of the founder on a pedestal
    x0, y0, x1, y1 = box("library_stacks", "Plumworth bust")
    mar = (226, 222, 214)
    bxm = (x0 + x1) / 2
    c.shadow(bxm, y1, 70, 8)
    c.paint(rect(bxm - 46, y0 + 110, bxm + 46, y1), mar, shade=(-6, 0, dk(mar, 0.75)), hi=(4, 0, lt(mar, 0.3)))
    c.paint(rect(bxm - 56, y0 + 100, bxm + 56, y0 + 118), mar, ow=3, shade=(0, -3))
    c.paint(rect(bxm - 56, y1 - 16, bxm + 56, y1), mar, ow=3, shade=(0, -3))
    c.paint(poly([(bxm - 50, y0 + 100), (bxm - 40, y0 + 70), (bxm + 40, y0 + 70), (bxm + 50, y0 + 100)], 1), mar,
            shade=(-4, 0, dk(mar, 0.75)))
    c.paint(ell(bxm, y0 + 40, 30, 36), mar, shade=(-5, 2, dk(mar, 0.78)), hi=(3, -3, (255, 255, 250), 2))
    c.paint(ell(bxm - 34, y0 + 30, 10, 10), mar, ow=3)  # side curls
    c.paint(ell(bxm + 34, y0 + 30, 10, 10), mar, ow=3)
    c.line([(bxm - 14, y0 + 36), (bxm - 6, y0 + 36)], 2.4)
    c.line([(bxm + 6, y0 + 36), (bxm + 14, y0 + 36)], 2.4)
    c.curve((bxm - 12, y0 + 56), (bxm, y0 + 50), (bxm + 12, y0 + 56), 2.2)
    c.text(bxm, y0 + 150, "A.P.", 14, (120, 116, 110))
    c.paint(ell(bxm + 4, y0 + 8, 22, 6), (220, 220, 220), ow=0, opacity=0.4)  # dust on the head

    lights = [(1300, 260, 560, 0.35, (150, 170, 255)), (mx, 600, 380, 0.25, (255, 220, 150)),
              (960, 300, 900, 0.12, (255, 220, 170))]
    light_pass(c, 0.62, lights, vign=0.5)
    c.glow(1300, 230, 140, (200, 210, 255), 0.25)
    c.save("bg_library_stacks.png")


# =========================================================================== characters
def paint_boomer():
    """Boomer: huge linebacker sleepwalking in pyjamas and a nightcap, arms out, eyes shut. Faces left."""
    c = Canvas(150, 300, ow=3)
    skin, skin_sh = (232, 176, 136), (196, 128, 100)
    pj, pj_sh = (110, 140, 220), (70, 96, 176)
    star = (250, 230, 120)

    def stars(p):
        r2 = random.Random(9)
        for _ in range(26):
            x, y = r2.uniform(10, 125), r2.uniform(90, 250)
            p.ell(x, y, 2.2, 2.2, star)

    # legs (wide stance) + slippers shaped like footballs
    c.paint(cap([(80, 190), (86, 250)], 24), pj, pattern=stars, shade=(4, 0, pj_sh))
    c.paint(cap([(52, 190), (44, 252)], 25), pj, pattern=stars, shade=(4, 0, pj_sh))
    for sx, sy in ((88, 258), (40, 260)):
        c.paint(ell(sx - 6, sy, 20, 9), (150, 90, 50), shade=(2, -2, (110, 62, 36)), hi=(-2, 2, (200, 130, 80), 1.5))
        c.line([(sx - 16, sy - 2), (sx + 4, sy - 2)], 1.4, (250, 250, 240))
    # far arm reaching forward (left)
    c.paint(cap([(64, 108), (30, 118), (8, 116)], 18), pj, pattern=stars, shade=(2, 3, pj_sh))
    c.paint(ell(6, 116, 9, 8), skin, shade=(2, 2, skin_sh))
    # huge barrel body
    body = poly([(38, 96), (66, 88), (96, 96), (110, 130), (108, 196), (66, 204), (28, 198), (22, 150), (26, 116)], 2)
    c.paint(body, pj, pattern=stars, shade=(6, 0, pj_sh), hi=(-3, 3, lt(pj, 0.3), 2))
    for by in (118, 142, 166, 186):
        c.paint(ell(56, by, 2.6, 2.6), (250, 250, 240), ow=1.4)
    c.paint(poly([(44, 96), (68, 96), (58, 112)], 1), lt(pj, 0.2), ow=2)  # collar
    # near arm reaching forward
    c.paint(cap([(46, 112), (22, 130), (4, 132)], 19), pj, pattern=stars, shade=(2, 3, pj_sh))
    c.paint(ell(2, 132, 9.5, 8.5), skin, shade=(2, 2, skin_sh))
    # thick neck + head (facing left, eyes shut, mouth open snoring)
    c.paint(cap([(60, 80), (60, 96)], 26), skin, shade=(4, 0, skin_sh))
    head = ell(62, 56, 28, 27) + poly([(36, 60), (38, 80), (52, 88), (74, 86), (88, 70)], 2) + ell(36, 62, 7, 7)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (250, 206, 170), 2.5))
    c.paint(ell(90, 60, 6, 9), skin, shade=(2, 2, skin_sh))
    for ex, ey, w in ((56, 56, 8), (39, 56, 5.5)):  # closed, dreaming eyes
        c.paint(ell(ex, ey, w, 5), (214, 150, 120), ow=0)
        c.curve((ex - w, ey), (ex, ey + 5), (ex + w, ey), 2.6)
        c.line([(ex + w * 0.2, ey + 4), (ex + w * 0.1, ey + 7)], 1.4)
    c.line([(48, 46), (62, 45)], 3, (90, 60, 40))
    c.line([(33, 47), (40, 46)], 2.8, (90, 60, 40))
    c.paint(ell(44, 76, 7, 6), (110, 30, 40), ow=2.2, pattern=lambda p: p.ell(44, 80, 4.5, 2.4, (230, 110, 110)))
    c.paint(ell(32, 64, 3, 2.2), skin_sh, ow=0)
    # drool
    c.paint(cap([(40, 82), (39, 90)], 2.4), (180, 220, 255), ow=1.2)
    # nightcap flopping back with a pompom (sits high, eyes stay visible)
    capc = (220, 60, 60)
    c.paint(poly([(38, 36), (50, 16), (74, 12), (92, 24), (112, 50), (120, 82), (108, 64), (90, 38), (60, 34)], 2),
            capc, shade=(3, 3, dk(capc, 0.72)), hi=(-2, 2, lt(capc, 0.3), 1.5),
            pattern=lambda p: [p.line([(42 + k * 14, 36 - k * 2), (54 + k * 14, 14 + k * 2)], 3, (250, 250, 240)) for k in range(5)])
    c.paint(rrect(36, 30, 92, 40, 5), (250, 250, 240), ow=2.4)
    c.paint(ell(120, 86, 9, 9), (250, 250, 240), ow=2.4)
    # snore "z"
    c.text(16, 30, "Z", 14, (250, 250, 255), stroke=1.5)
    c.text(4, 12, "z", 10, (250, 250, 255), stroke=1.2)
    c.fit(margin=3)
    c.save("hs_boomer.png")


def paint_doreen():
    """Doreen: night cook. Hairnet over red curls, white uniform, apron, big spatula. Faces left."""
    c = Canvas(110, 255, ow=3)
    skin, skin_sh = (200, 136, 100), (160, 100, 76)
    hair, hair_sh = (200, 80, 50), (150, 50, 34)
    uni, uni_sh = (246, 244, 236), (200, 200, 214)
    apron, apron_sh = (90, 150, 140), (60, 110, 104)
    # legs + clogs
    c.paint(cap([(64, 200), (66, 238)], 13), (240, 240, 236), shade=(3, 0, uni_sh))
    c.paint(cap([(44, 200), (40, 240)], 14), (240, 240, 236), shade=(3, 0, uni_sh))
    for xh, xt, yt, yb in ((74, 52, 236, 250), (52, 24, 238, 252)):
        c.paint(shoe_shape(xh, xt, yt, yb, toe_h=0.6), (90, 70, 120), shade=(3, -2, (60, 46, 90)),
                hi=(-2, 2, (140, 120, 170), 1.5))
    # far arm on the hip
    c.paint(cap([(76, 106), (90, 132), (76, 150)], 12), uni, shade=(3, 2, uni_sh))
    c.paint(ell(76, 150, 6.5, 6), skin, shade=(2, 2, skin_sh))
    # sturdy body + skirt-length tunic
    body = poly([(30, 100), (56, 92), (80, 100), (86, 140), (88, 206), (24, 206), (24, 150), (26, 120)], 2)
    c.paint(body, uni, shade=(5, 0, uni_sh), hi=(-3, 3, (255, 255, 250), 2))
    # apron
    c.paint(poly([(34, 126), (80, 126), (84, 208), (30, 208)], 1), apron, shade=(4, 0, apron_sh),
            hi=(-2, 2, lt(apron, 0.3), 1.5),
            pattern=lambda p: [p.ell(56, 150, 13, 9, (240, 240, 230)), p.line([(44, 176), (68, 176)], 2, apron_sh)])
    c.text(56, 150, "D", 10, apron, "Black")
    c.paint(cap([(36, 128), (46, 100)], 4), apron, ow=2)
    c.paint(cap([(78, 128), (68, 100)], 4), apron, ow=2)
    # name tag
    c.paint(rrect(62, 108, 78, 116, 2), (250, 220, 90), ow=1.6)
    # near arm holding a giant spatula up
    c.paint(cap([(34, 106), (20, 132), (14, 112)], 13), uni, shade=(3, 2, uni_sh))
    c.paint(cap([(14, 108), (12, 52)], 4.5), (60, 50, 50), ow=2.2)
    c.paint(rrect(0, 26, 26, 56, 3), (200, 204, 212), ow=2.6, hi=(-2, 2, (240, 244, 248), 1.5),
            pattern=lambda p: [p.line([(5 + k * 6, 30), (5 + k * 6, 52)], 1.4, (150, 154, 160)) for k in range(3)])
    c.paint(ell(15, 108, 7.5, 7), skin, shade=(2, 2, skin_sh))
    # neck + head
    c.paint(cap([(56, 84), (56, 98)], 12), skin, shade=(3, 0, skin_sh))
    head = ell(58, 58, 24, 25) + poly([(36, 62), (40, 82), (54, 90), (68, 86), (80, 72)], 2) + ell(34, 64, 6, 6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (226, 166, 126), 2.5))
    c.paint(ell(80, 62, 5.5, 8), skin, shade=(2, 2, skin_sh))
    eye(c, 54, 56, 7.5, 8.5, 50.5, 57.5, 2.3, lid=0.3, skin=skin, iris=(90, 60, 40), lashes=-1)
    eye(c, 39, 55.5, 5.2, 8, 36.5, 57, 2.0, lid=0.3, skin=skin, iris=(90, 60, 40))
    c.line([(46, 43), (54, 41), (62, 44)], 2.6, hair_sh)
    c.line([(33, 44), (40, 42)], 2.4, hair_sh)
    c.paint(ell(44, 68, 4, 3), (200, 110, 100), ow=0, opacity=0.5)  # blush
    c.curve((36, 76), (44, 82), (52, 76), 2.2)  # wide grin
    c.paint(ell(34, 64, 2.4, 2), skin_sh, ow=0)
    # big red curls under a hairnet
    for hx, hy, r in ((40, 36, 10), (52, 30, 11), (66, 30, 11), (78, 38, 10), (84, 52, 9), (34, 46, 8)):
        c.paint(ell(hx, hy, r, r), hair, shade=(2, 2, hair_sh), hi=(-1.5, -1.5, (240, 130, 90), 1))
    net = Sh([ell_pts(60, 32, 30, 15)])
    c.paint(net, (0, 0, 0, 0), ow=1.4, oc=(240, 240, 250))
    for k in range(5):
        c.line([(36 + k * 12, 20), (40 + k * 12, 44)], 0.8, (240, 240, 250), opacity=0.7)
    for k in range(3):
        c.line([(34, 26 + k * 7), (88, 26 + k * 7)], 0.8, (240, 240, 250), opacity=0.7)
    c.fit(margin=3)
    c.save("hs_doreen.png")


def possum_head(c, cx, cy, s=1.0):
    """Pokey the Possum's costume head; (cx, cy) = centre of the face."""
    fur, fur_sh = (156, 156, 168), (110, 110, 126)
    pink = (246, 150, 170)
    for ex in (-1, 1):
        c.paint(ell(cx + ex * 26 * s, cy - 26 * s, 13 * s, 14 * s), fur, shade=(2, 2, fur_sh),
                pattern=lambda p, ex=ex: p.ell(cx + ex * 26 * s, cy - 26 * s, 7 * s, 8 * s, pink))
    c.paint(ell(cx, cy, 34 * s, 30 * s), fur, shade=(4 * s, 3 * s, fur_sh), hi=(-3, -3, (210, 210, 220), 2 * s))
    c.paint(poly([(cx - 22 * s, cy + 4 * s), (cx, cy - 6 * s), (cx + 22 * s, cy + 4 * s), (cx, cy + 30 * s)], 2),
            (246, 240, 236), shade=(2, 2, (210, 200, 200)))
    for ex in (-1, 1):
        c.paint(ell(cx + ex * 13 * s, cy - 6 * s, 9 * s, 10 * s), (255, 255, 255), ow=2.4)
        c.paint(ell(cx + ex * 11 * s, cy - 4 * s, 4.5 * s, 5.5 * s), (24, 16, 14), ow=0)
        c.paint(ell(cx + ex * 10 * s, cy - 6 * s, 1.6 * s, 1.6 * s), (255, 255, 255), ow=0)
    c.paint(ell(cx, cy + 24 * s, 6 * s, 4.5 * s), pink, ow=2.2, hi=(-1, -1, (255, 210, 220)))
    c.paint(rect(cx - 6 * s, cy + 30 * s, cx + 6 * s, cy + 36 * s), (255, 255, 255), ow=1.8)
    c.line([(cx, cy + 30 * s), (cx, cy + 36 * s)], 1.2)


def paint_kyle():
    """Kyle: sweaty student in the bottom of a grey possum suit, holding the costume head. Faces left."""
    c = Canvas(130, 260, ow=3)
    skin, skin_sh = (250, 214, 180), (220, 158, 130)
    fur, fur_sh, fur_hi = (156, 156, 168), (110, 110, 126), (200, 200, 212)
    pink = (246, 150, 170)

    def furry(p):
        r2 = random.Random(3)
        for _ in range(70):
            x, y = r2.uniform(10, 120), r2.uniform(90, 250)
            p.line([(x, y), (x + 2, y + 5)], 1.0, fur_sh)
    # tail curling behind
    c.paint(cap([(92, 190), (116, 200), (124, 176), (114, 160)], 8), pink, ow=2.6, shade=(2, 2, (210, 110, 130)))
    # legs + big paw feet
    c.paint(cap([(70, 196), (74, 234)], 20), fur, pattern=furry, shade=(3, 0, fur_sh))
    c.paint(cap([(46, 196), (40, 236)], 21), fur, pattern=furry, shade=(3, 0, fur_sh))
    for sx, sy in ((74, 244), (36, 246)):
        c.paint(ell(sx - 6, sy, 18, 10), fur_sh, hi=(-2, -2, fur, 1.5))
        for k in range(3):
            c.paint(ell(sx - 18 + k * 7, sy - 4, 3, 3), pink, ow=1.4)
    # suit body (belly patch)
    body = poly([(30, 96), (60, 90), (88, 98), (94, 140), (92, 202), (60, 206), (26, 200), (22, 150), (24, 116)], 2)
    c.paint(body, fur, pattern=furry, shade=(5, 0, fur_sh), hi=(-3, 3, fur_hi, 2))
    c.paint(ell(58, 160, 22, 30), (236, 228, 220), ow=2.4, shade=(2, 0, (200, 192, 190)))
    # far arm (paw glove) resting
    c.paint(cap([(80, 108), (92, 140), (86, 162)], 15), fur, pattern=furry, shade=(3, 2, fur_sh))
    c.paint(ell(86, 164, 9, 8), fur_sh, hi=(-1, -1, fur, 1))
    # near arm holding the costume head against the hip
    c.paint(cap([(36, 106), (22, 138), (30, 160)], 15), fur, pattern=furry, shade=(3, 2, fur_sh))
    possum_head(c, 24, 178, 0.72)
    c.paint(ell(34, 162, 9, 8), fur_sh, hi=(-1, -1, fur, 1))
    # neck ring of the suit + human head
    c.paint(ell(58, 94, 22, 7), fur_sh, ow=2.4)
    c.paint(cap([(58, 80), (58, 94)], 13), skin, shade=(3, 0, skin_sh))
    head = ell(60, 54, 24, 25) + poly([(38, 58), (42, 78), (54, 86), (68, 84), (82, 68)], 2) + ell(36, 60, 6, 6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 232, 206), 2.5))
    c.paint(ell(82, 58, 5.5, 8), skin, shade=(2, 2, skin_sh))
    eye(c, 55, 53, 7.5, 8.5, 51.5, 55.5, 2.3, lid=0.42, lid_tilt=0.8, skin=skin, iris=(70, 120, 60))
    eye(c, 40, 52.5, 5.2, 8, 37.5, 55, 2.0, lid=0.42, lid_tilt=-0.6, skin=skin, iris=(70, 120, 60))
    c.line([(48, 40), (56, 41), (62, 44)], 2.4, (100, 70, 40))
    c.line([(34, 42), (41, 40)], 2.2, (100, 70, 40))
    c.curve((40, 74), (46, 71), (52, 75), 2.0)  # wobbly frown
    c.paint(ell(36, 60, 2.4, 2), skin_sh, ow=0)
    # sweat drops + headband + flattened hair
    c.paint(rrect(36, 30, 84, 38, 3), (230, 60, 60), ow=2.2)
    hair = (190, 140, 70)
    c.paint(poly([(36, 30), (42, 18), (58, 12), (74, 14), (86, 26), (84, 32)], 1), hair, shade=(2, 2, dk(hair, 0.72)))
    for dx, dy in ((30, 44), (86, 44), (88, 72)):
        c.paint(poly([(dx, dy - 6), (dx + 3, dy), (dx, dy + 3), (dx - 3, dy)], 2, True), (170, 220, 255), ow=1.6)
    c.fit(margin=3)
    c.save("hs_kyle.png")


def paint_percival():
    """Percival Thorne: slam poet. Beret, black turtleneck, long red scarf, goatee, holding Ivy's notebook.
    Drawn facing left, then mirrored so he faces right (toward the mic)."""
    c = Canvas(110, 270, ow=3)
    skin, skin_sh = (240, 206, 176), (206, 150, 128)
    blk, blk_sh, blk_hi = (50, 44, 58), (30, 26, 38), (90, 84, 104)
    scarf, scarf_sh = (200, 40, 50), (140, 24, 40)
    # skinny legs + pointy boots
    c.paint(cap([(60, 186), (64, 250)], 10), (40, 40, 50), shade=(2, 0, (24, 24, 30)))
    c.paint(cap([(46, 186), (42, 252)], 10), (40, 40, 50), shade=(2, 0, (24, 24, 30)))
    for xh, xt, yt, yb in ((70, 46, 248, 262), (50, 18, 250, 264)):
        c.paint(shoe_shape(xh, xt, yt, yb, pointy=True), (110, 60, 40), shade=(3, -2, (70, 36, 24)),
                hi=(-2, 2, (170, 100, 70), 1.5))
    # far arm raised, snapping fingers
    c.paint(cap([(70, 102), (86, 80), (88, 58)], 9), blk, shade=(2, 2, blk_sh))
    c.paint(ell(88, 54, 6, 6.5), skin, shade=(2, 2, skin_sh))
    for k in range(3):
        a = math.radians(-60 + k * 40)
        c.line([(88 + 10 * math.cos(a), 54 + 10 * math.sin(a) - 4), (88 + 15 * math.cos(a), 54 + 15 * math.sin(a) - 4)],
               1.6, (250, 220, 100))
    # thin body in a turtleneck
    torso = poly([(38, 96), (56, 90), (72, 96), (74, 140), (72, 192), (36, 192), (34, 140), (34, 110)], 2)
    c.paint(torso, blk, shade=(4, 0, blk_sh), hi=(-3, 3, blk_hi, 2))
    c.paint(rrect(42, 84, 70, 98, 4), blk, ow=2.4, hi=(0, 2, blk_hi))
    c.line([(54, 140), (56, 190)], 1.2, blk_sh)
    # long scarf, one end over the shoulder
    c.paint(cap([(42, 92), (40, 150), (44, 196)], 11), scarf, shade=(2, 0, scarf_sh),
            pattern=lambda p: [p.line([(34, 160 + k * 10), (52, 160 + k * 10)], 1.6, scarf_sh) for k in range(4)])
    c.paint(cap([(46, 92), (70, 92)], 11), scarf, shade=(0, 2, scarf_sh))
    for fx in (38, 43, 48):
        c.line([(fx, 198), (fx, 206)], 1.6, scarf)
    # near arm holding Ivy's green notebook against the chest
    nb = (90, 150, 90)
    c.paint(rrect(20, 116, 50, 156, 3), nb, shade=(3, 0, dk(nb, 0.72)), hi=(-2, 2, lt(nb, 0.3), 1.5))
    c.paint(ell(35, 132, 5, 5), (250, 250, 240), ow=1.4, pattern=lambda p: p.ell(35, 132, 2, 2, (250, 210, 60)))
    c.paint(cap([(38, 104), (26, 128), (36, 142)], 9), blk, shade=(2, 2, blk_sh))
    c.paint(ell(38, 142, 5.5, 5), skin, shade=(2, 2, skin_sh))
    # neck + long face, chin up, smug
    c.paint(cap([(56, 72), (56, 86)], 10), skin, shade=(3, 0, skin_sh))
    head = ell(58, 50, 21, 24) + poly([(38, 54), (40, 76), (52, 86), (64, 82), (76, 66)], 2) + ell(36, 56, 6, 6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 228, 204), 2.5))
    c.paint(ell(78, 54, 5, 7.5), skin, shade=(2, 2, skin_sh))
    eye(c, 52, 49, 7, 8, 48.5, 50.5, 2.2, lid=0.55, lid_tilt=-1.0, skin=skin, iris=(60, 80, 120))
    eye(c, 38, 48.5, 5, 7.5, 35.5, 50, 1.9, lid=0.55, lid_tilt=0.8, skin=skin, iris=(60, 80, 120))
    c.line([(44, 36), (52, 33), (60, 35)], 2.4, (40, 30, 30))  # arched brow
    c.line([(32, 38), (39, 36)], 2.2, (40, 30, 30))
    c.curve((38, 70), (44, 72), (52, 68), 1.8)  # smirk
    c.paint(poly([(40, 76), (48, 76), (46, 90), (42, 90)], 1), (50, 36, 30), ow=1.6)  # goatee
    c.line([(38, 66), (52, 64)], 2.4, (50, 36, 30))  # thin mustache
    c.paint(ell(36, 56, 2.2, 2), skin_sh, ow=0)
    # slicked hair + red beret tilted
    c.paint(poly([(38, 40), (40, 30), (54, 24), (70, 26), (80, 38), (80, 52), (74, 42), (60, 36), (46, 38)], 1),
            (40, 30, 30), shade=(2, 2, (24, 18, 18)))
    ber = (40, 36, 46)
    c.paint(ell(60, 24, 30, 11, -8), ber, shade=(2, 3, dk(ber, 0.7)), hi=(-2, -2, (90, 84, 100), 1.5))
    c.paint(cap([(60, 14), (62, 8)], 3), ber, ow=2)
    c.img = c.img.transpose(Image.FLIP_LEFT_RIGHT)
    c.fit(margin=3)
    c.save("hs_percival_thorne.png")


# =========================================================================== props that appear / disappear
def paint_room_216():
    """Gil's door in the dorm hallway (matches the other hallway doors)."""
    x0, y0, x1, y1 = box("dorm_hallway", "Room 216")
    w, h = x1 - x0, y1 - y0
    c = Canvas(int(w + 40), int(h + 20), ow=4)
    door(c, 20, 18, 20 + w, 18 + h - 2, (64, 120, 90), knob="R")
    c.paint(rrect(20 + w / 2 - 28, 46, 20 + w / 2 + 28, 74, 6), (230, 190, 90), ow=3, hi=(0, 2, (255, 230, 150)))
    c.text(20 + w / 2, 60, "216", 18, (60, 40, 20))
    c.paint(wonky(20 + w / 2 - 40, 92, 20 + w / 2 + 40, 150, 1.5, random.Random(216)), (250, 248, 236), ow=2.5)
    c.text(20 + w / 2, 110, "DO NOT", 11, (180, 40, 50))
    c.text(20 + w / 2, 132, "DISTURB", 11, (180, 40, 50))
    c.text(20 + w / 2, 146, "(EVER)", 8, (60, 60, 80), "Bold")
    trim_bottom(c)
    c.save("hs_room_216.png")


def paint_union_sign():
    """Wooden signpost on the quad pointing to the Student Union."""
    x0, y0, x1, y1 = box("campus", "Student Union")
    c = Canvas(150, int(y1 - y0) + 10, ow=4)
    H = c.h
    wood, wood_sh = (176, 116, 64), (126, 78, 42)
    c.shadow(75, H - 6, 30, 5)
    c.paint(rect(68, 30, 82, H - 6), wood, shade=(-3, 0, wood_sh), hi=(2, 0, lt(wood, 0.3)))
    c.paint(poly([(12, 40), (124, 40), (144, 64), (124, 88), (12, 88)]), (60, 130, 90), shade=(0, -4, (40, 96, 64)),
            hi=(0, 3, (110, 190, 140)))
    c.text(68, 56, "STUDENT", 13, (255, 250, 230))
    c.text(68, 76, "UNION", 15, (255, 250, 230))
    c.paint(poly([(6, 106), (118, 106), (118, 140), (6, 140), (-10, 123)]), (220, 140, 60), shade=(0, -4, dk((220, 140, 60), 0.75)))
    c.text(64, 123, "FOOD", 15, (60, 30, 20))
    c.paint(ell(110, 20, 12, 10), (156, 156, 168), ow=2.5, pattern=lambda p: p.ell(110, 24, 3, 2.5, (246, 150, 170)))
    for ex in (101, 119):
        c.paint(ell(ex, 11, 4, 4), (156, 156, 168), ow=2)
    trim_bottom(c)
    c.save("hs_student_union.png")


def draw_alarm(c, cx, cy, s=1.0):
    red = (220, 50, 50)
    for ex in (-1, 1):
        c.paint(ell(cx + ex * 20 * s, cy - 26 * s, 12 * s, 9 * s, ex * 25), (230, 196, 80), shade=(0, 2, (180, 140, 50)),
                hi=(0, -2, (255, 240, 170), 1.5))
    c.paint(cap([(cx, cy - 30 * s), (cx, cy - 36 * s)], 4 * s), (200, 160, 60), ow=2)
    for ex in (-1, 1):
        c.paint(cap([(cx + ex * 16 * s, cy + 22 * s), (cx + ex * 22 * s, cy + 32 * s)], 4 * s), (60, 60, 66), ow=2)
    c.paint(ell(cx, cy, 28 * s, 28 * s), red, shade=(4, 3, dk(red, 0.72)), hi=(-3, -3, lt(red, 0.35), 2))
    c.paint(ell(cx, cy, 21 * s, 21 * s), (250, 248, 236), ow=2.6)
    for k in range(12):
        a = math.radians(k * 30)
        c.line([(cx + 16 * s * math.cos(a), cy + 16 * s * math.sin(a)), (cx + 19 * s * math.cos(a), cy + 19 * s * math.sin(a))], 1.6)
    c.line([(cx, cy), (cx, cy - 13 * s)], 2.6)
    c.line([(cx, cy), (cx + 9 * s, cy + 4 * s)], 2.6)
    c.text(cx, cy + 9 * s, "GAME DAY", 4 * s, (180, 40, 50))


def paint_alarm_clock_prop():
    c = Canvas(70, 70, ow=3)
    draw_alarm(c, 35, 36, 0.95)
    c.fit(margin=2)
    c.save("hs_alarm_clock.png")


def draw_pine(c, cx, top, s=1.0, string=True):
    g, g_sh = (60, 160, 80), (36, 110, 56)
    if string:
        c.line([(cx, top - 26 * s), (cx, top + 4 * s)], 1.6, (240, 236, 220))
    tree = poly([(cx, top), (cx + 12 * s, top + 16 * s), (cx + 6 * s, top + 16 * s), (cx + 18 * s, top + 34 * s),
                 (cx + 9 * s, top + 34 * s), (cx + 22 * s, top + 54 * s), (cx + 4 * s, top + 54 * s),
                 (cx + 4 * s, top + 64 * s), (cx - 4 * s, top + 64 * s), (cx - 4 * s, top + 54 * s),
                 (cx - 22 * s, top + 54 * s), (cx - 9 * s, top + 34 * s), (cx - 18 * s, top + 34 * s),
                 (cx - 6 * s, top + 16 * s), (cx - 12 * s, top + 16 * s)])
    c.paint(tree, g, shade=(3, 2, g_sh), hi=(-2, -2, (130, 220, 140), 1.5))
    c.paint(rrect(cx - 12 * s, top + 36 * s, cx + 12 * s, top + 46 * s, 2), (250, 248, 236), ow=1.6)


def paint_air_freshener_prop():
    c = Canvas(50, 100, ow=3)
    draw_pine(c, 25, 30, 1.0)
    c.fit(margin=2)
    c.save("hs_air_freshener.png")


# =========================================================================== item icons (128x128)
def paint_icon_pine_freshener():
    icon("icon_pine_freshener.png", 8, lambda c: draw_pine(c, 64, 30, 1.45))


def paint_icon_possum_head():
    icon("icon_possum_head.png", -6, lambda c: possum_head(c, 64, 70, 1.4))


def paint_icon_possum_waffle():
    def draw(c):
        wf, wf_sh = (226, 160, 70), (180, 110, 40)
        for ex in (-1, 1):
            c.paint(ell(64 + ex * 32, 34, 14, 14), wf, shade=(2, 2, wf_sh),
                    pattern=lambda p, ex=ex: p.ell(64 + ex * 32, 34, 7, 7, (255, 250, 240)))
        sh = ell(64, 70, 46, 40)
        c.paint(sh, wf, shade=(4, 4, wf_sh), hi=(-3, -3, (250, 200, 120), 2),
                pattern=lambda p: [p.line([(20 + k * 14, 30), (20 + k * 14, 110)], 3, wf_sh) for k in range(7)] +
                [p.line([(18, 38 + k * 14), (110, 38 + k * 14)], 3, wf_sh) for k in range(6)])
        c.paint(ell(50, 60, 6, 6), (40, 30, 30), ow=0)
        c.paint(ell(78, 60, 6, 6), (40, 30, 30), ow=0)
        c.paint(ell(64, 84, 8, 6), (246, 150, 170), ow=2.5)
        c.paint(ell(64, 24, 16, 9), (255, 250, 240), ow=2.5)  # whipped cream
    icon("icon_possum_waffle.png", -4, draw)


def paint_icon_boomer_alarm():
    icon("icon_boomer_alarm.png", -8, lambda c: draw_alarm(c, 64, 70, 1.6))


def paint_icon_ivy_notebook():
    def draw(c):
        nb, nb_sh = (90, 150, 90), (60, 110, 64)
        c.paint(rrect(30, 16, 104, 114, 6), (250, 244, 226), shade=(-3, 0, (210, 200, 180)))
        c.paint(rrect(24, 12, 98, 110, 6), nb, shade=(4, 3, nb_sh), hi=(-3, -3, lt(nb, 0.3), 2))
        for k in range(6):
            c.paint(ell(26, 22 + k * 16, 5, 3), (200, 200, 210), ow=2)
        for k in range(5):
            a = math.radians(k * 72)
            c.paint(ell(62 + 12 * math.cos(a), 56 + 12 * math.sin(a), 8, 6, k * 72), (255, 255, 250), ow=2)
        c.paint(ell(62, 56, 6, 6), (250, 210, 60), ow=2)
        c.paint(rect(40, 84, 84, 96), (250, 244, 226), ow=2)
        c.text(62, 90, "POEMS", 7, (60, 90, 60))
    icon("icon_ivy_notebook.png", 6, draw)


ASSETS = {"bg_gil_room": paint_gil_room, "bg_student_union": paint_student_union,
          "bg_library_stacks": paint_library_stacks,
          "hs_boomer": paint_boomer, "hs_doreen": paint_doreen, "hs_kyle": paint_kyle,
          "hs_percival_thorne": paint_percival,
          "hs_room_216": paint_room_216, "hs_student_union": paint_union_sign,
          "hs_alarm_clock": paint_alarm_clock_prop, "hs_air_freshener": paint_air_freshener_prop,
          "icon_pine_freshener": paint_icon_pine_freshener, "icon_possum_head": paint_icon_possum_head,
          "icon_possum_waffle": paint_icon_possum_waffle, "icon_boomer_alarm": paint_icon_boomer_alarm,
          "icon_ivy_notebook": paint_icon_ivy_notebook}


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
