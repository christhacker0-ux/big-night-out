#!/usr/bin/env python3
"""
Big Night Out -- Act 4 "Off Campus" art (downtown, quickmart, rusty_anchor).

Original art, drawn with the helpers in paint.py (same outlines, palette rules and cel shading).
Props are painted into the backgrounds inside the hotspot boxes from World/act4.json, so the click
areas and the art line up. Characters (Bree Marlowe, Lou, Captain Gus) are separate sprites.

Usage:  python3 tools/art/act4.py            # paint everything
        python3 tools/art/act4.py bree icon  # only assets whose name contains these words
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (OUT, Canvas, Sh, W_BG, H_BG, WALL_Y, mix, dk, lt, poly, ell, rect, rrect, wonky, cap, bez,  # noqa
                   eye, shoe_shape, light_pass, baseboard, plank_floor, checker_floor, drop_ceiling, poster,
                   string_lights, icon, ell_pts)
from PIL import ImageOps  # noqa: E402

WORLD = os.path.join(paint.ROOT, "Assets", "_Project", "World", "act4.json")


# --------------------------------------------------------------------------- hotspot boxes from the JSON
def boxes(room_id):
    """name -> (x0, y0, x1, y1) in background pixels, from the hotspot feet/size in act4.json."""
    data = json.load(open(WORLD))
    out = {}
    for r in data["rooms"]:
        if r["id"] != room_id:
            continue
        for h in r["hotspots"]:
            fx, fy = h["feet"]
            w, hh = h["size"]
            out[h["name"]] = ((fx - w / 2 + 9.6) * 100, (5.4 - fy - hh) * 100, (fx + w / 2 + 9.6) * 100,
                              (5.4 - fy) * 100)
    return out


def feet_px(room_id, name):
    x0, y0, x1, y1 = boxes(room_id)[name]
    return (x0 + x1) / 2, y1


# --------------------------------------------------------------------------- shared props
def captain_hat(c, cx, cy, s=1.0, rot=0.0):
    """White-topped captain's hat with a black brim and a gold anchor badge; (cx, cy) = middle of the band."""
    def T(pts):
        return paint.rot_pts([(cx + x * s, cy + y * s) for x, y in pts], rot, cx, cy)
    top = (246, 244, 236)
    c.paint(poly(T([(-30, -2), (-36, -20), (-24, -32), (0, -36), (24, -32), (36, -20), (30, -2)]), 2), top,
            shade=(3 * s, 3 * s, (206, 204, 220)), hi=(-2 * s, 2 * s, (255, 255, 250), 1.5 * s))
    c.paint(poly(T([(-30, -10), (30, -10), (30, 2), (-30, 2)]), 1), (34, 40, 70), ow=2.4 * s ** 0.5,
            hi=(0, 1.5 * s, (80, 90, 140)))
    c.line(T([(-30, -5), (30, -5)]), 1.6 * s, (240, 196, 80))
    # badge: little anchor on a gold leaf
    bx, by = T([(0, -18)])[0]
    c.paint(ell(bx, by, 8 * s, 7 * s), (240, 196, 80), ow=2 * s ** 0.5, hi=(-1, -1, (255, 240, 170)))
    c.line([(bx, by - 4 * s), (bx, by + 4 * s)], 1.4 * s, (110, 70, 30))
    c.curve((bx - 4 * s, by + 1 * s), (bx, by + 6 * s), (bx + 4 * s, by + 1 * s), 1.2 * s, (110, 70, 30))
    c.paint(poly(T([(-30, 0), (30, 0), (34, 6), (14, 12), (-14, 12), (-34, 6)]), 1), (22, 22, 30),
            hi=(0, 2 * s, (90, 90, 110), 1 * s))


def camera_body(c, x, y, s=1.0, full=False):
    """Yellow-and-black disposable camera; (x, y) = top-left."""
    def X(v):
        return x + v * s

    def Y(v):
        return y + v * s
    body = rrect(X(0), Y(0), X(96), Y(56), 8 * s)
    c.paint(body, (255, 204, 40), shade=(4 * s, 4 * s, (214, 150, 30)), hi=(-3 * s, -3 * s, (255, 240, 150), 2 * s),
            pattern=lambda p: p.rect(X(0), Y(36), X(96), Y(56), (30, 30, 36)))
    c.line([(X(0), Y(36)), (X(96), Y(36))], 2.5 * s)
    c.paint(ell(X(58), Y(30), 18 * s, 18 * s), (40, 40, 48), ow=3 * s ** 0.5)
    c.paint(ell(X(58), Y(30), 11 * s, 11 * s), (80, 120, 190), ow=2 * s ** 0.5,
            hi=(-3 * s, -3 * s, (200, 230, 255), 2 * s))
    c.paint(rrect(X(8), Y(8), X(30), Y(22), 3 * s), (150, 200, 230), ow=2 * s ** 0.5)  # viewfinder
    c.paint(rrect(X(76), Y(-7), X(92), Y(1), 2 * s), (60, 60, 70), ow=2 * s ** 0.5)  # shutter button
    c.paint(ell(X(84), Y(46), 6 * s, 6 * s), (200, 200, 210), ow=2 * s ** 0.5)  # winder
    if full:
        c.paint(rrect(X(4), Y(40), X(40), Y(54), 3 * s), (226, 40, 54), ow=2 * s ** 0.5)
        c.text(X(22), Y(47), "FULL", 7.5 * s, (255, 255, 255))
    else:
        c.text(X(22), Y(46.5), "27", 8 * s, (255, 220, 60))


# =========================================================================== characters
def paint_bree_marlowe():
    """Diner waitress / actress. Drawn facing left, then mirrored so she faces right (into the room)."""
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (252, 206, 170), (216, 146, 118)
    hair, hair_sh, hair_hi = (226, 84, 46), (172, 48, 36), (255, 150, 90)
    dress, dress_sh, dress_hi = (98, 206, 196), (56, 150, 156), (170, 236, 226)
    apron, apron_sh = (252, 250, 244), (210, 206, 222)
    red = (226, 44, 64)

    # high ponytail behind the head, bouncing back
    c.paint(poly([(70, 30), (88, 22), (102, 34), (104, 56), (98, 78), (90, 66), (86, 48), (74, 42)], 2, True), hair,
            shade=(3, 2, hair_sh), hi=(-2, 2, hair_hi, 1.5),
            pattern=lambda p: [p.line(bez((84, 30), (100, 46 + k * 4), (94, 70)), 1.2, hair_sh) for k in range(2)])
    c.paint(ell(78, 30, 5, 4), red, ow=2)  # scrunchie
    # far arm: flung up and back, dramatic
    c.paint(cap([(72, 100), (90, 82), (98, 56)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(ell(99, 50, 6.5, 7, 20) + cap([(96, 44), (95, 37)], 3) + cap([(101, 44), (103, 37)], 3) +
            cap([(104, 48), (108, 43)], 3), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(70, 100), (80, 92)], 14), dress, shade=(3, 2, dress_sh))
    c.paint(ell(82, 90, 3.5, 7, 50), (255, 255, 255), ow=2)
    # legs + white sneakers with red laces (pointing left)
    c.paint(cap([(60, 176), (64, 232)], 10.5), skin, shade=(3, 0, skin_sh))
    c.paint(cap([(46, 176), (42, 234)], 11), skin, shade=(3, 0, skin_sh))
    for xh, xt, yt, yb in ((76, 46, 236, 252), (56, 18, 239, 256)):
        sh = shoe_shape(xh, xt, yt, yb)
        c.paint(sh, (250, 248, 240), shade=(2, -2, (210, 208, 220)),
                pattern=lambda p, xt=xt, yb=yb: p.ell(xt + 7, yb - 5, 8, 5, red))
        c.line([(xh + 2, yb - 4), (xt + 1, yb - 4)], 1.4)
        for k in range(3):
            c.line([(xh - 12 - k * 4, yt + 1 + k), (xh - 14 - k * 4, yt + 4 + k)], 1.3, red)
    c.paint(poly([(40, 226), (50, 226), (50, 234), (40, 234)]), (255, 255, 255), ow=2)  # socks
    c.paint(poly([(58, 224), (68, 224), (68, 232), (58, 232)]), (255, 255, 255), ow=2)
    # neck
    c.paint(cap([(56, 80), (56, 96)], 9.5), skin, shade=(3, 0, skin_sh))
    # mint diner dress, flared skirt
    dress_sh_ = poly([(36, 96), (54, 90), (74, 96), (78, 110), (72, 134), (86, 182), (24, 182), (38, 134),
                      (32, 110)], 2)
    c.paint(dress_sh_, dress, shade=(4, 2, dress_sh), hi=(-3, 3, dress_hi, 2))
    c.paint(poly([(46, 90), (56, 98), (66, 90), (68, 98), (56, 104), (44, 98)], 1), (255, 255, 255), ow=2)  # collar
    # apron with a pocket full of straws + order pad
    ap = poly([(38, 132), (74, 132), (80, 176), (32, 176)], 1)
    c.paint(ap, apron, shade=(3, 0, apron_sh),
            pattern=lambda p: [p.ell(44 + k * 9, 176, 4.5, 3, (236, 232, 240)) for k in range(5)])
    c.paint(rect(36, 128, 76, 135), apron, ow=2.2)
    c.paint(rrect(44, 146, 62, 162, 2), apron, ow=2, shade=(2, 0, apron_sh))
    c.line([(48, 146), (46, 136)], 2.2, red)
    c.line([(53, 146), (54, 134)], 2.2, (60, 160, 220))
    # name tag (no lettering, it would be mirrored)
    c.paint(rrect(60, 106, 74, 114, 2), red, ow=1.8)
    c.line([(63, 110), (71, 110)], 1.4, (255, 240, 240))
    # near arm: holding an order pad like a script
    c.paint(cap([(38, 100), (30, 120), (22, 108)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(cap([(38, 98), (34, 108)], 14), dress, shade=(3, 2, dress_sh))
    c.paint(ell(33, 110, 7, 3.5, -10), (255, 255, 255), ow=2)
    c.paint(poly([(8, 94), (24, 92), (26, 112), (10, 114)], 1), (252, 248, 226), ow=2.2,
            pattern=lambda p: [p.line([(11, 99 + k * 4), (22, 98 + k * 4)], 1, (120, 140, 190)) for k in range(4)])
    c.paint(ell(22, 106, 6, 6.5), skin, shade=(2, 2, skin_sh))

    # ---- head (3/4 facing left)
    head = ell(56, 56, 23, 25.5) + poly([(34, 60), (38, 78), (50, 87), (62, 84), (76, 70)], 2) + ell(32, 62, 5, 4.6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 228, 200), 2.5))
    c.paint(ell(77, 62, 5.5, 8), skin, shade=(2, 2, skin_sh))
    c.curve((33, 65), (30, 66), (29, 63), 1.4)
    for fx, fy in ((46, 68), (50, 70), (54, 68), (40, 68)):
        c.paint(ell(fx, fy, 0.9, 0.9), (200, 110, 70), ow=0)
    c.paint(ell(50, 72, 6, 3.4), (255, 120, 130), ow=0, opacity=0.5)
    # eyes: big, looking up and off at the horizon
    eye(c, 52, 55, 8.2, 10, 48, 51.5, 2.5, skin=skin, lashes=1, iris=(70, 140, 70))
    eye(c, 37, 54.5, 5.6, 9.2, 34, 51, 2.2, skin=skin, lashes=-1, iris=(70, 140, 70))
    c.line([(44, 38), (52, 34), (62, 37)], 2.2, hair_sh)  # brows high = drama
    c.line([(31, 41), (38, 37.5)], 2.0, hair_sh)
    # open mouth mid-line ("Land ho!")
    c.paint(ell(43, 78, 6, 5.5), (150, 30, 50), ow=2,
            pattern=lambda p: (p.rect(37, 72, 49, 75.5, (255, 255, 255)), p.ell(43, 82, 4, 2.4, (255, 120, 140))))
    # bangs + pencil behind the ear
    front = poly([(30, 48), (34, 32), (46, 22), (62, 18), (78, 24), (86, 38), (84, 56), (80, 66), (76, 50),
                  (68, 40), (60, 44), (52, 38), (44, 44), (38, 42)], 2, True)
    c.paint(front, hair, shade=(3, 3, hair_sh), hi=(-2, 3, hair_hi, 2))
    c.curve((46, 28), (58, 22), (72, 28), 1.6, hair_hi)
    c.paint(cap([(70, 46), (90, 36)], 4), (255, 214, 60), ow=2)
    c.paint(cap([(88, 37), (92, 35)], 4), (255, 150, 160), ow=2)
    c.img = ImageOps.mirror(c.img)
    c.fit(margin=3)
    c.save("hs_bree_marlowe.png")


def paint_lou():
    """Deadpan quickmart clerk, arms crossed, faces left."""
    c = Canvas(110, 255, ow=3)
    skin, skin_sh = (198, 140, 104), (156, 100, 78)
    hair, hair_sh, hair_hi = (40, 34, 44), (22, 18, 28), (110, 90, 140)
    tee, tee_sh = (52, 50, 62), (32, 30, 42)
    vest, vest_sh, vest_hi = (64, 168, 92), (40, 120, 70), (130, 210, 140)
    jeans, jeans_sh = (60, 60, 80), (40, 40, 58)
    boot = (52, 40, 36)
    ink = (60, 90, 150)

    # legs + boots (pointing left), weight on one hip
    c.paint(cap([(64, 160), (68, 200), (66, 228)], 16), jeans, shade=(3, 0, jeans_sh))
    c.paint(cap([(46, 160), (42, 200), (42, 230)], 17), jeans, shade=(3, 0, jeans_sh))
    for xh, xt, yt, yb in ((80, 50, 234, 250), (58, 20, 238, 254)):
        sh = shoe_shape(xh, xt, yt, yb, toe_h=0.6) + rect(xh - 20, yt - 12, xh, yt + 4)
        c.paint(sh, boot, shade=(3, -2, dk(boot, 0.7)), hi=(-2, 2, lt(boot, 0.3), 1.5))
        c.paint(rect(xt - 2, yb - 4, xh + 2, yb + 2), (30, 24, 22), ow=0, clip=sh)
    # torso: black tee + green store vest
    c.paint(cap([(55, 80), (55, 96)], 10.5), skin, shade=(3, 0, skin_sh))
    torso = poly([(32, 96), (54, 90), (76, 96), (80, 120), (76, 162), (34, 162), (30, 120)], 2)
    c.paint(torso, tee, shade=(4, 0, tee_sh))
    c.paint(poly([(30, 100), (46, 96), (50, 162), (32, 162), (28, 124)], 1), vest, shade=(3, 0, vest_sh),
            hi=(-2, 2, vest_hi, 1.5))
    c.paint(poly([(64, 96), (78, 100), (80, 124), (76, 162), (60, 162)], 1), vest, shade=(3, 0, vest_sh))
    c.paint(rrect(34, 116, 46, 124, 2), (255, 255, 255), ow=1.8)  # name badge, blank
    c.line([(36, 120), (44, 120)], 1.2, (200, 40, 50))
    c.paint(rect(32, 150, 78, 158), (36, 32, 36), ow=2)  # belt
    # crossed arms: far forearm under, near forearm over, tattoos
    c.paint(cap([(74, 104), (80, 130), (60, 132)], 9), skin, shade=(3, 2, skin_sh),
            pattern=lambda p: [p.ell(74, 116, 2.4, 3.4, ink), p.ell(70, 130, 2, 2, (210, 60, 80))])
    c.paint(cap([(36, 104), (32, 126), (68, 128)], 9.5), skin, shade=(3, 2, skin_sh),
            pattern=lambda p: (p.poly([(42, 124), (46, 120), (50, 124), (46, 130)], (210, 60, 80)),
                               p.line([(54, 125), (62, 126)], 1.6, ink),
                               p.ell(34, 114, 2.4, 3, ink)))
    c.paint(ell(70, 128, 5.5, 5), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(36, 98), (33, 112)], 15), tee, shade=(3, 0, tee_sh))
    c.paint(cap([(72, 98), (76, 112)], 15), tee, shade=(3, 0, tee_sh))

    # ---- head (3/4 facing left), flat deadpan expression
    head = ell(56, 55, 23, 25) + poly([(34, 60), (37, 76), (48, 85), (62, 83), (76, 70)], 2) + ell(32, 60, 5, 4.6)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (226, 172, 132), 2.5))
    c.paint(ell(77, 61, 5.5, 8), skin, shade=(2, 2, skin_sh))
    for k in range(3):  # ear piercings
        c.paint(ell(80 + k * 1.2, 56 + k * 5, 1.6, 1.6), (220, 220, 230), ow=1.2)
    c.curve((33, 63), (30, 64), (29, 61), 1.4)
    eye(c, 52, 56, 7.8, 8.6, 48.5, 58, 2.4, lid=0.5, lid_tilt=0, skin=skin, iris=(120, 80, 50), lashes=1)
    eye(c, 37, 55.5, 5.4, 8, 34.5, 57.5, 2.1, lid=0.5, lid_tilt=0, skin=skin, iris=(120, 80, 50), lashes=-1)
    c.line([(44, 44), (52, 43), (62, 44)], 2.6, hair)  # flat brows
    c.line([(31, 46), (39, 45)], 2.4, hair)
    c.paint(poly([(37, 75), (46, 74.5), (54, 75.5), (52, 78.5), (45, 79.5), (38, 78)], 1), (120, 40, 80), ow=1.8)
    c.line([(37, 76.5), (46, 76.6), (54, 76.6)], 1.6)  # flat mouth, dark plum lipstick
    # hair: short, swept, shaved side; beanie
    c.paint(poly([(32, 46), (36, 34), (50, 28), (70, 30), (80, 40), (82, 58), (78, 62), (74, 48), (62, 42),
                  (52, 44), (40, 46)], 2, True), hair, shade=(3, 2, hair_sh), hi=(-2, 2, hair_hi, 1.5))
    c.paint(poly([(76, 46), (82, 50), (82, 64), (78, 66)], 1), (90, 78, 96), ow=0, opacity=0.7)
    c.paint(cap([(32, 48), (28, 74), (30, 100), (26, 118)], 9), hair, shade=(2, 2, hair_sh),
            pattern=lambda p: [p.line([(24, 60 + k * 12), (34, 66 + k * 12)], 1.4, hair_hi) for k in range(5)])
    c.paint(ell(26, 122, 5, 4), (226, 112, 40), ow=2)
    beanie = poly([(30, 38), (34, 20), (50, 10), (68, 10), (82, 20), (86, 36), (80, 40), (56, 36), (34, 42)], 2)
    c.paint(beanie, (226, 112, 40), shade=(3, 3, (180, 76, 30)), hi=(-2, 2, (255, 170, 90), 1.5),
            pattern=lambda p: [p.line([(36 + k * 7, 24), (36 + k * 7, 40)], 1.4, (190, 86, 34)) for k in range(7)])
    c.paint(poly([(30, 36), (86, 34), (86, 42), (30, 44)], 1), (240, 130, 50), ow=2.2)
    # pencil behind the near ear... and one in the beanie
    c.paint(cap([(64, 18), (88, 6)], 4), (255, 214, 60), ow=2)
    c.paint(cap([(86, 7), (90, 5)], 4), (255, 150, 160), ow=2)
    c.fit(margin=3)
    c.save("hs_lou.png")


def paint_captain_gus():
    """Old sailor on his bar stool (the stool is part of the sprite), facing left."""
    c = Canvas(120, 245, ow=3)
    skin, skin_sh = (240, 182, 150), (204, 128, 110)
    beard, beard_sh = (246, 244, 240), (196, 196, 214)
    coat, coat_sh, coat_hi = (40, 56, 104), (26, 36, 74), (80, 100, 160)
    pants, pants_sh = (70, 64, 70), (46, 40, 50)
    chrome, chrome_sh = (196, 204, 214), (130, 140, 160)
    seat = (196, 52, 52)

    # the stool: base, pole, foot ring, seat
    c.paint(ell(66, 238, 24, 6), chrome, shade=(0, -2, chrome_sh), hi=(0, 2, (240, 244, 255)))
    c.paint(rect(62, 160, 70, 236), chrome, ow=2.5, shade=(-3, 0, chrome_sh), hi=(2, 0, (240, 244, 255)))
    c.paint(ell(66, 200, 20, 5), (0, 0, 0, 0), ow=3, oc=OUT)
    c.paint(ell(66, 200, 20, 5), (0, 0, 0, 0), ow=1.4, oc=chrome)
    c.paint(ell(70, 158, 24, 7), seat, shade=(0, -2, (150, 30, 40)), hi=(0, 2, (255, 120, 110)))
    # legs: thighs forward (left) over the seat, shins down, boots on the foot ring
    c.paint(cap([(66, 150), (36, 152), (34, 196)], 17), pants, shade=(3, 0, pants_sh))
    c.paint(cap([(74, 148), (46, 146), (50, 192)], 16), pants, shade=(3, 0, pants_sh))
    for xh, xt, yt, yb in ((48, 20, 196, 210), (62, 32, 192, 204)):
        c.paint(shoe_shape(xh, xt, yt, yb, toe_h=0.6), (60, 40, 30), shade=(3, -2, (40, 26, 20)),
                hi=(-2, 2, (110, 80, 60), 1.5))
    # big belly coat
    body = poly([(46, 90), (66, 84), (88, 92), (96, 120), (94, 150), (80, 158), (52, 158), (40, 140), (38, 112)], 2)
    c.paint(body, coat, shade=(4, 0, coat_sh), hi=(-3, 2, coat_hi, 2))
    for by in (112, 128, 144):
        for bx in (54, 70):
            c.paint(ell(bx, by, 2.6, 2.6), (240, 196, 80), ow=1.6)
    c.paint(poly([(52, 86), (64, 104), (58, 112), (46, 96)], 1), coat_hi, ow=2)  # lapel
    # far arm resting on the (implied) bar behind, near arm holding a mug on his knee
    c.paint(cap([(88, 100), (100, 128), (92, 142)], 13), coat, shade=(3, 0, coat_sh))
    c.paint(cap([(48, 100), (40, 126), (26, 136)], 13), coat, shade=(3, 0, coat_sh))
    c.paint(rect(30, 130, 40, 142), (240, 196, 80), ow=0, opacity=0.0)
    mug = rrect(8, 118, 26, 142, 3)
    c.paint(mug, (230, 200, 120), shade=(3, 0, (190, 150, 80)),
            pattern=lambda p: p.rect(8, 118, 26, 124, (255, 250, 236)))
    c.paint(ell(17, 118, 9, 3), (255, 250, 236), ow=2)
    c.paint(ell(26, 134, 7, 6.5), skin, shade=(2, 2, skin_sh))
    # ---- head (3/4 facing left), giant beard
    head = ell(60, 50, 24, 25) + ell(36, 56, 9, 8)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (255, 214, 186), 2.5))
    c.paint(ell(82, 56, 6, 8.5), skin, shade=(2, 2, skin_sh))
    c.paint(ell(34, 56, 7, 6), (240, 110, 110), ow=2, hi=(-1, -1, (255, 180, 170)))  # red nose
    bd = poly([(40, 62), (50, 66), (62, 62), (78, 64), (84, 78), (80, 100), (68, 116), (56, 112), (44, 116),
               (36, 100), (32, 80)], 2, True)
    c.paint(bd, beard, shade=(4, 3, beard_sh),
            pattern=lambda p: [p.line(bez((44 + k * 8, 70), (42 + k * 8, 92), (48 + k * 7, 108)), 1.2, beard_sh)
                               for k in range(4)])
    c.paint(poly([(30, 62), (40, 60), (50, 64), (44, 70), (34, 70)], 2, True), beard, shade=(2, 2, beard_sh))  # mustache
    c.line([(38, 72), (46, 73)], 1.8, (150, 40, 50))
    # eyes: twinkly, a bit squinty from forty years of sun
    eye(c, 54, 44, 7, 7.6, 51, 45, 2.4, lid=0.35, lid_tilt=-1, skin=skin, iris=(60, 120, 200))
    eye(c, 40, 43.5, 5, 7, 38, 44.5, 2.0, lid=0.35, lid_tilt=1, skin=skin, iris=(60, 120, 200))
    c.line([(46, 32), (54, 30), (62, 33)], 3.2, beard)  # bushy white brows
    c.line([(34, 35), (41, 33)], 3.0, beard)
    c.curve((59, 50), (63, 52), (61, 56), 1.2, skin_sh)  # crow's feet
    captain_hat(c, 58, 30, 0.95, -8)
    c.fit(margin=3)
    c.save("hs_captain_gus.png")


# =========================================================================== icons
def paint_icon_fishing_net():
    def draw(c):
        c.paint(cap([(20, 116), (70, 52)], 8), (176, 120, 70), shade=(2, 2, (130, 84, 50)), hi=(-2, -2, (220, 170, 110)))
        bag = ell(86, 52, 26, 30, -30)
        c.paint(bag, (236, 226, 196), ow=4, shade=(3, 3, (200, 186, 150)))
        for k in range(9):
            c.paint(cap([(52 + k * 9, 14), (62 + k * 9, 96)], 1.6), (150, 120, 80), ow=0, clip=bag)
            c.paint(cap([(52, 22 + k * 9), (124, 30 + k * 9)], 1.6), (150, 120, 80), ow=0, clip=bag)
        c.paint(bag, (0, 0, 0, 0), ow=4)
        hoop = ell(86, 38, 32, 26, -30)
        c.paint(hoop, (0, 0, 0, 0), ow=6, oc=OUT)
        c.paint(hoop, (0, 0, 0, 0), ow=3, oc=(150, 150, 160))
        c.paint(ell(94, 70, 6, 5), (120, 180, 90), ow=2)  # bit of seaweed
    icon("icon_fishing_net.png", 0, draw)


def paint_icon_wish_quarter():
    def draw(c):
        s = (206, 210, 220)
        c.paint(ell(64, 66, 46, 46), s, shade=(5, 5, (150, 156, 176)), hi=(-4, -4, (250, 252, 255), 4))
        c.paint(ell(64, 66, 36, 36), (0, 0, 0, 0), ow=2.5, oc=(130, 136, 156))
        c.text(64, 66, "25", 30, (130, 136, 156))
        for k in range(28):
            a = math.radians(k * 360 / 28)
            c.line([(64 + 42 * math.cos(a), 66 + 42 * math.sin(a)), (64 + 46 * math.cos(a), 66 + 46 * math.sin(a))],
                   1.4, (150, 156, 176))
        paint_star(c, 104, 26, 10, (255, 255, 255))
        c.paint(ell(96, 108, 7, 9), (150, 210, 255), ow=2.5, hi=(-1, -1, (240, 250, 255)))  # still wet
        c.paint(paint.Sh([paint.ell_pts(64, 66, 40, 40, 0, 20, 200, 250)]), (255, 255, 255), ow=0, opacity=0.6)
    icon("icon_wish_quarter.png", -10, draw)


def paint_icon_gus_coaster():
    def draw(c):
        c.paint(ell(64, 64, 52, 52), (232, 214, 170), shade=(4, 4, (196, 170, 120)), hi=(-3, -3, (250, 240, 210), 3),
                pattern=lambda p: p.ell(84, 80, 18, 16, (210, 180, 140)))
        c.paint(ell(64, 64, 44, 44), (0, 0, 0, 0), ow=2, oc=(196, 60, 60))
        c.text(64, 50, "HEAD", 24, (40, 50, 110), "Black")
        c.text(64, 72, "fair winds", 10, (40, 50, 110), "Bold", angle=-6)
        c.text(64, 86, "- Gus", 10, (40, 50, 110), "Bold", angle=-6)
        c.line([(64, 96), (64, 110)], 2, (40, 50, 110))
        c.line([(59, 99), (69, 99)], 2, (40, 50, 110))
        c.curve((57, 104), (64, 112), (71, 104), 2, (40, 50, 110))
    icon("icon_gus_coaster.png", 8, draw)


def paint_icon_captains_hat():
    def draw(c):
        captain_hat(c, 64, 74, 1.5, -8)
    icon("icon_captains_hat.png", 0, draw)


def paint_icon_disposable_camera():
    def draw(c):
        camera_body(c, 16, 40, 1.0)
    icon("icon_disposable_camera.png", -8, draw)


def paint_icon_full_camera():
    def draw(c):
        camera_body(c, 16, 40, 1.0, full=True)
        for k, (x, y) in enumerate(((18, 28), (110, 36), (108, 104))):
            paint_star(c, x, y, 7, (255, 236, 120))
    icon("icon_full_camera.png", 8, draw)


def paint_star(c, x, y, s, col):
    pts = []
    for k in range(10):
        r = s if k % 2 == 0 else s * 0.42
        a = math.radians(-90 + k * 36)
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    c.paint(poly(pts), col, ow=2)


def headshot_print(c, x, y, w, h, ang):
    sub = Canvas(int(w + 30), int(h + 30), ow=3)

    def pic(p):
        p.rect(15, 15, 15 + w, 15 + h, (120, 190, 230))
        p.rect(15, 15 + h * 0.62, 15 + w, 15 + h, (60, 140, 190))
        cx = 15 + w / 2
        p.ell(cx, 15 + h * 0.98, w * 0.34, h * 0.3, (98, 206, 196))  # shoulders
        p.ell(cx, 15 + h * 0.48, w * 0.2, h * 0.22, (252, 206, 170))  # face
        p.poly([(cx - w * 0.26, 15 + h * 0.32), (cx + w * 0.26, 15 + h * 0.32), (cx + w * 0.2, 15 + h * 0.16),
                (cx - w * 0.2, 15 + h * 0.16)], (246, 244, 236))  # captain hat
        p.rect(cx - w * 0.28, 15 + h * 0.3, cx + w * 0.28, 15 + h * 0.36, (22, 22, 30))
        p.ell(cx + w * 0.26, 15 + h * 0.5, w * 0.1, h * 0.14, (226, 84, 46))  # hair
        p.ell(cx - w * 0.07, 15 + h * 0.46, 2, 2, OUT)
        p.ell(cx + w * 0.07, 15 + h * 0.46, 2, 2, OUT)
        p.ell(cx, 15 + h * 0.57, 4, 3, (150, 30, 50))
    sub.paint(rect(10, 10, 20 + w, 20 + h), (252, 250, 244))
    sub.paint(rect(15, 15, 15 + w, 15 + h), (120, 190, 230), ow=2, pattern=pic)
    c.stamp(sub, x, y, ang)


def paint_icon_headshots():
    def draw(c):
        headshot_print(c, 54, 62, 62, 76, 12)
        headshot_print(c, 70, 64, 62, 76, -6)
        paint_star(c, 108, 22, 9, (255, 220, 60))
    icon("icon_headshots.png", 0, draw)


def paint_icon_diner_name_tag():
    def draw(c):
        red = (226, 44, 64)
        c.paint(rrect(10, 34, 118, 94, 10), red, shade=(4, 4, (170, 24, 50)), hi=(-3, -3, (255, 120, 130), 3))
        c.paint(rrect(18, 42, 110, 86, 6), (0, 0, 0, 0), ow=2, oc=(255, 220, 220))
        c.text(64, 54, "HI, I'M", 10, (255, 236, 236), "Bold")
        c.text(64, 72, "BREE", 22, (255, 255, 255), stroke=1.5)
        paint_star(c, 104, 36, 9, (255, 220, 60))
        c.line([(30, 30), (98, 30)], 3, (180, 180, 190))  # pin
    icon("icon_diner_name_tag.png", -8, draw)


def paint_icon_finished_crossword():
    def draw(c):
        c.paint(poly([(14, 16), (114, 12), (116, 116), (12, 114)]), (246, 242, 226), shade=(4, 4, (210, 204, 186)))
        n, x0, y0, s = 5, 22, 28, 16
        black = {(0, 3), (1, 1), (3, 0), (4, 2), (2, 0), (4, 4), (3, 3)}
        for i in range(n):
            for j in range(n):
                col = (40, 36, 44) if (i, j) in black else (255, 255, 255)
                c.paint(rect(x0 + j * s, y0 + i * s, x0 + (j + 1) * s, y0 + (i + 1) * s), col, ow=1.8)
        for j, ch in enumerate("HEAD"):
            c.text(x0 + (j + 1) * s + s / 2, y0 + 2 * s + s / 2 + 1, ch, 10, (40, 60, 150))
        c.text(64, 20, "17 ACROSS", 7, (60, 60, 60), "Bold")
        c.paint(ell(64, 92, 24, 9), (0, 0, 0, 0), ow=0)
        c.curve((40, 102), (64, 116), (90, 100), 3, (220, 40, 60))  # a smile, in pen
        c.paint(cap([(92, 112), (122, 82)], 5), (255, 214, 60), ow=2.5)
    icon("icon_finished_crossword.png", 6, draw)


# =========================================================================== scenery helpers
def neon_text(c, x, y, s, size, col, angle=0):
    c.text(x, y, s, size, col, stroke=2.2, sc=OUT, angle=angle)
    c.glow(x, y, size * len(s) * 0.38 + 30, col, 0.25)


def brick_facade(c, x0, y0, x1, y1, col, seed=0):
    rng = random.Random(seed)

    def bricks(p):
        bh = 22
        for row, y in enumerate(range(int(y0), int(y1), bh)):
            p.line([(x0, y), (x1, y)], 1.6, dk(col, 0.62))
            off = 24 * (row % 2)
            for x in range(int(x0) - off, int(x1), 48):
                p.line([(x, y), (x, y + bh)], 1.4, dk(col, 0.62))
                if rng.random() < 0.08:
                    p.rect(x + 3, y + 3, x + 44, y + bh - 3, lt(col, 0.12))
    c.paint(rect(x0, y0, x1, y1), ("vy", y0, y1, lt(col, 0.06), dk(col, 0.85)), ow=3, pattern=bricks)


def upper_windows(c, x0, x1, y0, y1, rng, lit_p=0.55, w=56, h=78):
    n = max(1, int((x1 - x0) // (w + 44)))
    gap = ((x1 - x0) - n * w) / (n + 1)
    for row_y in range(int(y0), int(y1) - h, h + 56):
        for k in range(n):
            wx = x0 + gap + k * (w + gap)
            lit = rng.random() < lit_p
            glass = ("v", (255, 222, 130), (255, 164, 80)) if lit else ("v", (70, 66, 120), (44, 40, 86))
            c.paint(rect(wx - 6, row_y - 6, wx + w + 6, row_y + h + 6), (226, 210, 180), ow=3)
            c.paint(rect(wx, row_y, wx + w, row_y + h), glass, ow=2.5)
            c.line([(wx + w / 2, row_y), (wx + w / 2, row_y + h)], 3, (226, 210, 180))
            c.line([(wx, row_y + h * 0.5), (wx + w, row_y + h * 0.5)], 3, (226, 210, 180))
            if lit and rng.random() < 0.4:  # a little silhouette / plant
                c.paint(ell(wx + w * 0.3, row_y + h * 0.82, 9, 7), (60, 120, 70), ow=2)


def sidewalk(c, base, y0=WALL_Y):
    c.paint(rect(0, y0, W_BG, H_BG), ("vy", y0, H_BG, lt(base, 0.08), dk(base, 0.8)), ow=0)
    vp = (960, 300)
    for xb in range(-2000, W_BG + 2200, 200):
        xa = vp[0] + (xb - vp[0]) * (y0 - vp[1]) / (H_BG - vp[1])
        c.line([(xa, y0), (xb, H_BG)], 2.2, dk(base, 0.6), opacity=0.55)
    for y in (836, 900, 980):
        c.line([(0, y), (W_BG, y)], 2.2, dk(base, 0.6), opacity=0.55)
    # curb + a strip of road at the very bottom
    c.paint(rect(-10, 1040, W_BG + 10, 1052), lt(base, 0.25), ow=3)
    c.paint(rect(-10, 1052, W_BG + 10, H_BG + 10), (50, 46, 60), ow=0)
    for x in range(40, W_BG, 260):
        c.paint(rect(x, 1066, x + 120, 1074), (240, 210, 80), ow=0, opacity=0.8)


# =========================================================================== backgrounds
def paint_downtown():
    B = boxes("downtown")
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(404)
    # --- night sky
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, 520, (26, 22, 70), (110, 50, 120)), ow=0)
    for _ in range(90):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, 260)
        c.paint(ell(sx, sy, 1.6, 1.6), (255, 246, 220), ow=0, opacity=rng.uniform(0.4, 0.9))
    c.paint(ell(1000, 92, 40, 40), (255, 244, 200), ow=3, hi=(-3, -3, (255, 255, 240), 3))
    c.paint(ell(986, 84, 6, 5), (236, 222, 180), ow=0)
    c.paint(ell(1012, 104, 8, 6), (236, 222, 180), ow=0)
    c.glow(1000, 92, 140, (200, 200, 255), 0.25)
    # distant skyline silhouettes
    far = (64, 44, 104)
    bx = -20
    while bx < W_BG:
        w = rng.uniform(60, 140)
        top = rng.uniform(150, 300)
        c.paint(rect(bx, top, bx + w, WALL_Y), far, ow=0)
        for wy in range(int(top) + 14, WALL_Y - 20, 26):
            for wx in range(int(bx) + 10, int(bx + w) - 12, 20):
                if rng.random() < 0.3:
                    c.paint(rect(wx, wy, wx + 8, wy + 12), (255, 200, 110), ow=0, opacity=0.7)
        bx += w + rng.uniform(-10, 6)

    # --- bus stop (box) on the left edge
    x0, y0, x1, y1 = B["Bus stop"]
    brick_facade(c, -10, 200, 250, WALL_Y, (150, 76, 70), seed=1)
    upper_windows(c, 0, 240, 236, 420, rng, w=50, h=70)
    c.paint(rect(x0 + 6, y0 + 70, x1 - 6, y1 - 2), (120, 180, 220, 90), ow=3)  # glass shelter
    c.paint(rect(x0 - 2, y0 + 56, x1 + 2, y0 + 74), (40, 110, 160), ow=3, hi=(0, 3, (90, 160, 210)))
    c.line([(x0 + 8, y0 + 74), (x0 + 8, y1)], 5, (60, 70, 80))
    c.line([(x1 - 8, y0 + 74), (x1 - 8, y1)], 5, (60, 70, 80))
    c.paint(rect(x0 + 16, y1 - 70, x1 - 16, y1 - 58), (176, 120, 70), ow=3, hi=(0, 3, (220, 170, 110)))  # bench
    c.line([(x0 + 26, y1 - 58), (x0 + 26, y1)], 4, (60, 70, 80))
    c.line([(x1 - 26, y1 - 58), (x1 - 26, y1)], 4, (60, 70, 80))
    c.paint(rect(x0 + 18, y1 - 140, x1 - 18, y1 - 80), (250, 230, 120), ow=3,  # lawyer ad on the shelter
            pattern=lambda p: (p.ell(x0 + 50, y1 - 112, 14, 16, (240, 190, 150)),
                               p.line([(x0 + 40, y1 - 106), (x0 + 60, y1 - 106)], 3, OUT)))
    c.text(x0 + 105, y1 - 120, "HURT?", 11, (180, 40, 50))
    c.text(x0 + 105, y1 - 102, "CALL BOB", 10, (180, 40, 50))
    # sign on a pole, poking above
    c.line([(x1 - 30, y0 - 10), (x1 - 30, y0 + 56)], 5, (60, 70, 80))
    c.paint(rrect(x0 + 8, y0 - 6, x1 - 8, y0 + 40, 6), (40, 120, 70), shade=(-3, -3), hi=(3, 3, (90, 180, 120), 2))
    c.text((x0 + x1) / 2, y0 + 8, "CAMPUS", 13, (255, 255, 240))
    c.text((x0 + x1) / 2, y0 + 26, "SHUTTLE", 12, (255, 255, 240))
    c.paint(poly([(x0 + 4, y0 + 17), (x0 + 16, y0 + 9), (x0 + 16, y0 + 25)]), (255, 255, 240), ow=0)

    # --- Starlite Diner (box: whole facade below the sign)
    x0, y0, x1, y1 = B["Starlite Diner"]
    brick_facade(c, 250, 140, 700, WALL_Y, (120, 90, 120), seed=2)
    upper_windows(c, 260, 690, 176, 300, rng, w=56, h=70)
    c.paint(rrect(x0 - 10, y0, x1 + 10, y1, 30), ("v", (230, 236, 244), (160, 170, 190)), ow=4,
            hi=(0, 5, (255, 255, 255), 3))  # chrome body
    c.paint(rect(x0 - 10, y0 + 140, x1 + 10, y0 + 170), (226, 44, 64), ow=3)  # red stripe
    for k in range(5):  # chrome ribs
        c.line([(x0 + 14, y0 + 30 + k * 22), (x1 - 14, y0 + 30 + k * 22)], 2.2, (150, 160, 184), opacity=0.8)
    c.paint(rrect(x0 + 60, y0 + 38, x1 - 60, y0 + 116, 10), (40, 30, 60), ow=3)
    neon_text(c, (x0 + x1) / 2, y0 + 64, "OPEN 24 HOURS", 19, (120, 240, 255))
    c.text((x0 + x1) / 2, y0 + 96, "HOT COFFEE  COLD PIE", 12, (255, 200, 90), "Bold")
    for k in range(3):  # big windows with booths + pie
        wx0 = x0 + 10 + k * 104
        if k == 1:
            continue
        c.paint(rrect(wx0, y0 + 186, wx0 + 90, y1 - 70, 10), ("v", (255, 226, 150), (255, 170, 90)), ow=3,
                pattern=lambda p, wx0=wx0: (p.rect(wx0, y1 - 120, wx0 + 90, y1 - 70, (200, 50, 60)),
                                            p.ell(wx0 + 30, y1 - 128, 16, 6, (240, 200, 120)),
                                            p.poly([(wx0 + 54, y1 - 126), (wx0 + 78, y1 - 126), (wx0 + 66, y1 - 140)],
                                                   (250, 220, 150)),
                                            p.rect(wx0, y0 + 186, wx0 + 90, y0 + 200, (255, 240, 200))))
    dx0 = x0 + 118
    c.paint(rrect(dx0, y0 + 186, dx0 + 84, y1, 8), (226, 44, 64), ow=3, shade=(-4, 0))  # door
    c.paint(rrect(dx0 + 12, y0 + 200, dx0 + 72, y0 + 290, 6), ("v", (255, 226, 150), (255, 170, 90)), ow=3)
    c.paint(ell(dx0 + 14, y0 + 320, 5, 5), (240, 196, 80), ow=2)
    c.paint(rrect(dx0 + 14, y0 + 236, dx0 + 70, y0 + 262, 4), (255, 255, 255), ow=2)
    c.text(dx0 + 42, y0 + 249, "OPEN", 11, (226, 44, 64))
    c.paint(rect(x0 - 16, y1 - 70, x1 + 16, y1), (120, 128, 150), ow=3, hi=(0, 3, (200, 206, 220)))  # kick plate
    # neon sign above the roof
    c.paint(rrect(x0 + 10, y0 - 70, x1 - 10, y0 + 10, 14), (40, 30, 60), ow=4)
    neon_text(c, (x0 + x1) / 2 - 10, y0 - 42, "STARLITE", 30, (255, 110, 170))
    neon_text(c, (x0 + x1) / 2 - 10, y0 - 10, "DINER", 22, (110, 230, 255))
    paint_star(c, x1 - 26, y0 - 52, 22, (255, 230, 90))
    c.glow(x1 - 26, y0 - 52, 70, (255, 230, 90), 0.4)
    c.text((x0 + x1) / 2, y0 + 155, "PIE 23 HOURS A DAY", 12, (255, 255, 240))

    # parking meter where Bree rehearses
    c.paint(rect(752, 640, 760, 792), (90, 96, 110), ow=3)
    c.paint(rrect(738, 590, 774, 646, 10), (150, 156, 170), ow=3, hi=(-2, 2, (210, 214, 226)),
            pattern=lambda p: p.ell(756, 612, 10, 10, (250, 250, 230)))
    c.line([(756, 612), (762, 606)], 2)

    # --- fountain plaza
    x0, y0, x1, y1 = B["Fountain"]
    brick_facade(c, 700, 180, 1110, WALL_Y, (176, 120, 80), seed=3)
    upper_windows(c, 712, 1100, 220, 470, rng, w=58, h=80)
    c.paint(rect(700, 470, 1110, 520), (90, 60, 50), ow=3)  # awning band of a closed bank
    c.text(905, 495, "FIRST BANK OF DOWNTOWN", 18, (255, 220, 140))
    cx = (x0 + x1) / 2
    c.shadow(cx, y1 - 4, 130, 14, 0.4)
    stone, stone_sh = (200, 196, 210), (150, 146, 170)
    c.paint(ell(cx, y1 - 70, 116, 28), stone, ow=4, shade=(0, -5, stone_sh))
    c.paint(rect(cx - 116, y1 - 70, cx + 116, y1 - 16) + ell(cx, y1 - 16, 116, 22), stone, ow=4,
            shade=(-6, 0, stone_sh), hi=(4, 0, (240, 238, 248), 3))
    c.paint(ell(cx, y1 - 70, 102, 20), ("v", (110, 190, 230), (60, 130, 200)), ow=3,
            pattern=lambda p: [p.ell(cx + rng.uniform(-80, 80), y1 - 70 + rng.uniform(-10, 10), 4, 2.4,
                                     rng.choice([(255, 220, 90), (220, 220, 230)])) for _ in range(26)])
    c.paint(ell(cx + 30, y1 - 66, 6, 3), (255, 236, 120), ow=1.6)  # THE quarter
    c.glow(cx + 30, y1 - 66, 20, (255, 240, 160), 0.6)
    c.paint(rect(cx - 12, y0 + 70, cx + 12, y1 - 74), stone, ow=3, shade=(-3, 0, stone_sh))
    c.paint(ell(cx, y0 + 70, 46, 12), stone, ow=3, shade=(0, -3, stone_sh))
    for sgn in (-1, 1):  # water arcs
        c.curve((cx, y0 + 40), (cx + sgn * 64, y0), (cx + sgn * 88, y1 - 76), 7, (170, 230, 255), 0.85)
        c.curve((cx, y0 + 40), (cx + sgn * 40, y0 + 10), (cx + sgn * 56, y0 + 66), 5, (200, 240, 255), 0.85)
    c.paint(ell(cx, y0 + 34, 12, 16), (200, 240, 255), ow=2.5)
    for k in range(8):
        c.paint(ell(cx + rng.uniform(-95, 95), y1 - 74 + rng.uniform(-6, 2), 3, 3), (230, 250, 255), ow=0)

    # --- Quickmart storefront
    x0, y0, x1, y1 = B["Quickmart"]
    c.paint(rect(1110, 300, 1400, WALL_Y), ("vy", 300, WALL_Y, (226, 226, 206), (190, 186, 170)), ow=3)
    c.paint(rect(1104, 330, 1406, 420), (60, 170, 90), ow=4, hi=(0, 4, (120, 220, 140)))
    c.text(1255, 375, "QUICKMART", 40, (255, 250, 220), stroke=3)
    c.text(1255, 440, "WE HAVE EVERYTHING*", 13, (60, 60, 70), "Bold")
    c.paint(rect(x0, y0, x1, y1), ("v", (230, 250, 255), (160, 220, 240)), ow=4,
            pattern=lambda p: [p.rect(x0 + 12, y0 + 50 + k * 70, x1 - 12, y0 + 56 + k * 70, (200, 170, 120))
                               for k in range(4)])  # glass door with shelves behind
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 4)
    c.paint(rect(x0 + 20, y0 + 120, x1 - 20, y0 + 150), (250, 250, 250), ow=2.5)
    c.text((x0 + x1) / 2, y0 + 135, "PUSH / PULL", 11, (200, 40, 50))
    c.paint(rrect(x0 + 56, y0 + 20, x1 - 56, y0 + 46, 6), (226, 44, 64), ow=2.5)
    c.text((x0 + x1) / 2, y0 + 33, "OPEN", 12, (255, 255, 255))
    c.glow((x0 + x1) / 2, y0 + 33, 60, (255, 80, 90), 0.35)
    for wx0 in (1124, 1340):  # side windows with slushie posters
        c.paint(rect(wx0, y0 + 10, wx0 + 50, y1 - 70), ("v", (255, 246, 210), (240, 220, 170)), ow=3)
    c.paint(rect(1128, y0 + 40, 1170, y0 + 110), (60, 150, 220), ow=2.5)
    c.text(1149, y0 + 75, "SLUSH", 9, (255, 255, 255), angle=90)
    c.paint(rect(1344, y0 + 40, 1386, y0 + 110), (255, 200, 60), ow=2.5)
    c.text(1365, y0 + 75, "GUM", 11, (200, 40, 50), angle=90)

    # --- Bijou Theatre: marquee (box) and doors below
    x0, y0, x1, y1 = B["Bijou Theatre"]
    c.paint(rect(1400, 60, 1760, WALL_Y), ("vy", 60, WALL_Y, (150, 50, 70), (110, 36, 60)), ow=4,
            pattern=lambda p: [p.line([(x, 60), (x, WALL_Y)], 2, (130, 40, 64)) for x in range(1420, 1760, 40)])
    c.paint(rrect(1540, 60, 1620, 300, 10), (240, 196, 80), ow=4, hi=(-3, 0, (255, 236, 160), 2))  # vertical sign
    for k, ch in enumerate("BIJOU"):
        neon_text(c, 1580, 92 + k * 44, ch, 30, (255, 90, 120))
    c.paint(poly([(x0 - 14, y0 + 10), (x1 + 14, y0 + 10), (x1 - 4, y1), (x0 + 4, y1)]), (60, 30, 50), ow=4)
    c.paint(rect(x0, y0 + 26, x1, y1 - 18), (252, 246, 220), ow=3)
    rngb = random.Random(5)
    for k in range(32):  # bulbs, some out
        bx = x0 + 8 + k * (x1 - x0 - 16) / 31
        on = rngb.random() > 0.3
        for by in (y0 + 18, y1 - 9):
            c.paint(ell(bx, by, 4, 4), (255, 240, 150) if on else (110, 90, 80), ow=1.6)
            if on:
                c.glow(bx, by, 10, (255, 230, 140), 0.35)
    c.text((x0 + x1) / 2, y0 + 70, "MIDNIGHT CLASSICS", 26, (40, 30, 50))
    c.text((x0 + x1) / 2, y0 + 106, "OLD MOVIES  NEW POPCORN", 15, (200, 40, 60), "Bold")
    c.text((x0 + x1) / 2, y0 + 134, "COUPLES SOFA FRONT ROW", 12, (60, 60, 120), "Bold")
    for dx in (1430, 1520, 1650):  # doors under the marquee
        c.paint(rect(dx, 560, dx + 80, WALL_Y), (90, 30, 50), ow=3,
                pattern=lambda p, dx=dx: p.rect(dx + 10, 580, dx + 70, 700, (255, 210, 120)))
        c.paint(rect(dx + 36, 640, dx + 44, 680), (240, 196, 80), ow=2)
    c.paint(rect(1430, 520, 1510, 556), (240, 196, 80), ow=3)
    c.text(1470, 538, "TICKETS", 11, (90, 30, 50))
    # TV camera on a tripod, pointed at the date table (Speed Daters Live set)
    tx = 1690
    for dx2 in (-30, 0, 30):
        c.line([(tx, 660), (tx + dx2, WALL_Y + 4)], 4, (50, 50, 60))
    c.paint(rrect(tx - 34, 610, tx + 30, 662, 6), (60, 62, 72), ow=3, hi=(-2, 2, (110, 112, 130)))
    c.paint(rrect(tx - 60, 618, tx - 32, 648, 4), (40, 40, 48), ow=3)
    c.paint(ell(tx - 60, 633, 6, 14), (120, 180, 230), ow=2.5)
    c.paint(ell(tx + 18, 620, 5, 5), (230, 40, 40), ow=2)
    c.glow(tx + 18, 620, 16, (255, 60, 60), 0.6)
    c.paint(rect(tx - 20, 664, tx + 16, 690), (232, 40, 150), ow=2.5)
    c.text(tx - 2, 677, "SDL", 9, (255, 255, 255))
    # little date table with a candle, between the camera and Roxy
    c.paint(ell(1606, 742, 30, 7), (250, 246, 236), ow=3)
    c.line([(1606, 746), (1606, 790)], 4, (60, 60, 70))
    c.paint(ell(1606, 792, 18, 4), (60, 60, 70), ow=2)
    c.paint(rect(1600, 718, 1612, 740), (255, 250, 230), ow=2)
    c.paint(ell(1606, 712, 3.5, 6), (255, 200, 60), ow=1.4)
    c.glow(1606, 712, 30, (255, 200, 100), 0.6)

    # --- Rusty Anchor door (box), right edge
    x0, y0, x1, y1 = B["Rusty Anchor"]
    wood = (110, 70, 44)
    c.paint(rect(1760, 140, W_BG + 10, WALL_Y), ("vy", 140, WALL_Y, (96, 62, 44), (70, 44, 34)), ow=4,
            pattern=lambda p: [p.line([(1760, y), (W_BG, y)], 2, (50, 30, 24)) for y in range(160, WALL_Y, 34)])
    c.paint(rect(x0 + 6, y0 + 40, x1 - 6, y1), wood, ow=3, shade=(-5, 0, dk(wood, 0.75)),
            pattern=lambda p: [p.line([(x, y0 + 40), (x, y1)], 2, dk(wood, 0.7)) for x in range(int(x0) + 30, int(x1), 26)])
    c.paint(ell((x0 + x1) / 2, y0 + 120, 28, 28), (200, 150, 60), ow=4, hi=(-2, -2, (255, 220, 130)))
    c.paint(ell((x0 + x1) / 2, y0 + 120, 19, 19), ("v", (255, 210, 120), (230, 150, 70)), ow=2.5)
    c.paint(ell(x0 + 22, y0 + 230, 6, 6), (200, 150, 60), ow=2)
    # hanging sign with an anchor
    c.line([(1770, 230), (1890, 230)], 4, (40, 30, 26))
    c.paint(rrect(1772, 238, 1890, 312, 8), (226, 214, 180), ow=3, shade=(-3, -3))
    c.text(1831, 256, "THE RUSTY", 12, (110, 40, 30))
    c.text(1831, 296, "ANCHOR", 16, (110, 40, 30))
    c.line([(1831, 266), (1831, 284)], 3, (40, 40, 60))
    c.curve((1820, 278), (1831, 290), (1842, 278), 3, (40, 40, 60))
    buoy = Sh([ell_pts(1840, 172, 30, 30) + list(reversed(ell_pts(1840, 172, 16, 16)))])
    c.paint(buoy, (250, 250, 244), shade=(3, 3, (210, 206, 220)),
            pattern=lambda p: [p.poly([(1840, 172), (1840 + 40 * math.cos(math.radians(a)), 172 + 40 * math.sin(math.radians(a))),
                                       (1840 + 40 * math.cos(math.radians(a + 45)), 172 + 40 * math.sin(math.radians(a + 45)))],
                                      (226, 44, 54)) for a in (0, 90, 180, 270)])

    # --- lamp posts + sidewalk
    sidewalk(c, (150, 146, 160))
    baseboard(c, y=WALL_Y + 6, h=10, color=(110, 106, 122))
    lamps = [paint.lamp_post(c, 230, 806, 300), paint.lamp_post(c, 1378, 806, 300)]

    lights = [(l[0], l[1], 380, 0.55, (255, 210, 130)) for l in lamps] + [
        (460, 380, 420, 0.4, (255, 120, 180)), (1255, 380, 300, 0.4, (120, 255, 160)),
        (1580, 420, 420, 0.5, (255, 200, 120)), (1830, 520, 240, 0.35, (255, 170, 90)),
        (1000, 760, 300, 0.25, (120, 200, 255))]
    light_pass(c, 0.68, lights, vign=0.42)
    for l in lamps:
        c.glow(l[0], l[1], 120, (255, 220, 140), 0.45)
    c.save("bg_downtown.png")


def snack_shelf(c, x0, x1, y0, y1, rows, rng):
    c.paint(rect(x0, y0, x1, y1), (220, 224, 230), ow=3, shade=(-5, 0, (180, 184, 196)))
    h = (y1 - y0) / rows
    cols = [(226, 60, 60), (255, 200, 50), (60, 150, 220), (90, 190, 90), (240, 120, 40), (180, 90, 200),
            (250, 250, 240)]
    for r in range(rows):
        sy = y0 + (r + 1) * h
        x = x0 + 8
        while x < x1 - 20:
            w = rng.uniform(16, 30)
            hh = h * rng.uniform(0.5, 0.82)
            col = rng.choice(cols)
            if rng.random() < 0.3:
                c.paint(ell(x + w / 2, sy - hh / 2 - 4, w / 2, hh / 2), col, ow=2.2, hi=(-2, -2, lt(col, 0.4)))
            else:
                c.paint(rect(x, sy - hh - 6, x + w, sy - 6), col, ow=2.2, shade=(-3, 0),
                        pattern=lambda p, x=x, w=w, sy=sy, hh=hh: p.rect(x + 3, sy - hh * 0.7, x + w - 3,
                                                                        sy - hh * 0.5, (255, 255, 255)))
            x += w + 4
        c.paint(rect(x0, sy - 8, x1, sy), (160, 166, 180), ow=2.5)


def paint_quickmart():
    B = boxes("quickmart")
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(77)
    wall = (186, 226, 210)
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, lt(wall, 0.15), wall), ow=0)
    c.paint(rect(0, 560, W_BG, WALL_Y), (226, 96, 70), ow=0,  # stripe band
            pattern=lambda p: p.rect(0, 572, W_BG, 586, (255, 214, 90)))
    drop_ceiling(c, 120, (232, 236, 232), panels=(320, 960, 1600))
    checker_floor(c, (236, 236, 226), (150, 200, 190), vp=(960, 200), cols=130, rows=6)
    baseboard(c, color=(80, 110, 110))
    # back-wall snack shelves
    snack_shelf(c, 700, 1120, 220, 540, 4, rng)
    snack_shelf(c, 1460, 1900, 220, 540, 4, rng)
    c.paint(rrect(740, 156, 1080, 206, 8), (60, 170, 90), ow=3)
    c.text(910, 181, "SNACKS  &  REGRETS", 20, (255, 250, 220))
    c.paint(rrect(1500, 156, 1860, 206, 8), (60, 150, 220), ow=3)
    c.text(1680, 181, "BATTERIES  GUM  SOCKS", 18, (255, 250, 220))
    # employee of the month: Lou, not smiling
    c.paint(rect(1222, 300, 1338, 430), (240, 196, 80), ow=3, shade=(-3, -3))
    c.paint(rect(1236, 314, 1324, 396), (120, 180, 200), ow=2.5,
            pattern=lambda p: (p.ell(1280, 380, 30, 20, (64, 168, 92)), p.ell(1280, 350, 22, 24, (198, 140, 104)),
                               p.poly([(1258, 340), (1262, 324), (1298, 324), (1302, 340)], (226, 112, 40)),
                               p.line([(1270, 352), (1278, 352)], 2, OUT), p.line([(1284, 352), (1292, 352)], 2, OUT),
                               p.line([(1272, 366), (1290, 366)], 2.4, OUT)))
    c.text(1280, 412, "EMPLOYEE", 10, (90, 40, 30))
    c.text(1280, 424, "OF THE MONTH x 40", 8, (90, 40, 30), "Bold")

    def brain(p, ox, oy):
        p.rect(ox, oy, ox + 170, oy + 230, (60, 150, 255))
        for k in range(10):
            a = math.radians(k * 36)
            p.poly([(ox + 85, oy + 140), (ox + 85 + 200 * math.cos(a), oy + 140 + 200 * math.sin(a)),
                    (ox + 85 + 200 * math.cos(a + 0.3), oy + 140 + 200 * math.sin(a + 0.3))], (100, 180, 255))
        p.poly([(ox + 55, oy + 110), (ox + 115, oy + 110), (ox + 105, oy + 205), (ox + 65, oy + 205)], (255, 255, 255))
        p.ell(ox + 85, oy + 108, 34, 18, (60, 200, 255))
        p.line([(ox + 92, oy + 100), (ox + 106, oy + 60)], 5, (255, 80, 120))
    bp = poster(170, 230, (60, 150, 255), brain, angle=0)
    bp.text(105, 52, "BRAIN FREEZE", 17, (255, 255, 255), stroke=1.6)
    bp.text(105, 74, "GUARANTEED", 14, (255, 240, 120), stroke=1.4)
    c.stamp(bp, 380, 330, angle=-3)

    # --- exit (glass door to the night street)
    x0, y0, x1, y1 = B["Exit"]
    c.paint(rect(x0 - 8, y0 - 8, x1 + 8, y1), (200, 204, 214), ow=3, shade=(-4, 0))
    c.paint(rect(x0 + 4, y0 + 4, x1 - 4, y1), ("v", (40, 30, 90), (120, 50, 120)), ow=3,
            pattern=lambda p: [p.rect(x0 + 14 + k * 40, y0 + 120 - k * 30, x0 + 44 + k * 40, y1, (30, 24, 60))
                               for k in range(4)] + [p.ell(x0 + 60, y0 + 60, 18, 8, (255, 110, 170))])
    c.paint(poly([(x0 + 20, y1 - 20), (x0 + 80, y0 + 20), (x0 + 100, y0 + 20), (x0 + 40, y1 - 20)]),
            (255, 255, 255), ow=0, opacity=0.12)
    c.paint(rect(x0 + 30, y0 + 170, x1 - 30, y0 + 186), (200, 204, 214), ow=2.5)
    c.paint(rrect(x0 + 20, y0 - 50, x1 - 20, y0 - 16, 6), (226, 44, 64), ow=3)
    c.text((x0 + x1) / 2, y0 - 33, "EXIT", 16, (255, 255, 255))

    # --- flower bucket
    x0, y0, x1, y1 = B["Flower bucket"]
    cx = (x0 + x1) / 2
    c.shadow(cx, y1 - 4, 60, 8)
    for k in range(9):
        fx = x0 + 14 + k * (x1 - x0 - 28) / 8
        fy = y0 + 10 + (k % 3) * 14
        c.line([(cx + (fx - cx) * 0.3, y1 - 60), (fx, fy)], 3, (60, 120, 60))
        c.paint(ell(fx, fy, 11, 10), (210, 40, 60), ow=2.5, hi=(-2, -2, (255, 110, 120)),
                pattern=lambda p, fx=fx, fy=fy: p.line([(fx - 5, fy), (fx + 4, fy - 3)], 1.4, (150, 20, 40)))
    c.paint(poly([(x0 + 14, y1 - 66), (x1 - 14, y1 - 66), (x1 - 24, y1 - 4), (x0 + 24, y1 - 4)]), (170, 176, 190),
            shade=(-5, 0), hi=(4, 0, (220, 224, 236), 2))
    c.paint(rrect(x0 + 30, y1 - 52, x1 - 30, y1 - 24, 3), (255, 255, 255), ow=2)
    c.text(cx, y1 - 38, "$5", 13, (200, 40, 50))

    # --- slushie machine on a cabinet
    x0, y0, x1, y1 = B["Slushie machine"]
    c.paint(rect(x0, y1 - 90, x1, y1), (200, 90, 70), ow=3, shade=(-5, 0))
    c.paint(rect(x0 + 6, y0 + 10, x1 - 6, y1 - 90), (220, 224, 234), ow=3, shade=(-5, 0, (180, 184, 196)))
    for k, col in enumerate(((60, 150, 255), (240, 50, 70), (140, 100, 60))):
        tx = x0 + 18 + k * 44
        c.paint(rrect(tx, y0 + 34, tx + 36, y0 + 150, 10), col, ow=3, hi=(-3, 0, lt(col, 0.4), 2),
                pattern=lambda p, tx=tx: p.line([(tx + 8, y0 + 60), (tx + 28, y0 + 80), (tx + 8, y0 + 100),
                                                 (tx + 28, y0 + 120)], 3, (255, 255, 255)))
        c.paint(rect(tx + 12, y0 + 150, tx + 24, y0 + 170), (60, 60, 70), ow=2)
    c.paint(rect(x0 + 6, y0 - 26, x1 - 6, y0 + 12), (60, 150, 255), ow=3)
    c.text((x0 + x1) / 2, y0 - 7, "SLUSH-O-MATIC", 13, (255, 255, 255))
    c.paint(rrect(x0 + 100, y0 + 176, x0 + 148, y0 + 196, 4), (255, 255, 255), ow=2)
    c.text(x0 + 124, y0 + 186, "DON'T", 10, (140, 100, 60))

    # --- counter with register, gum, bell, crossword
    x0, y0, x1, y1 = B["Counter"]
    ct = (226, 96, 70)
    c.shadow((x0 + x1) / 2, y1 - 2, 190, 10, 0.4)
    c.paint(rect(x0, y0 + 40, x1, y1), ct, ow=4, shade=(-6, 0), hi=(0, 4, lt(ct, 0.3)),
            pattern=lambda p: [p.rect(x0 + 20 + k * 90, y0 + 70, x0 + 90 + k * 90, y1 - 20, dk(ct, 0.88))
                               for k in range(4)])
    c.paint(rect(x0 - 10, y0 + 28, x1 + 10, y0 + 44), (250, 246, 236), ow=3, shade=(0, -4))
    c.paint(poly([(x1 - 150, y0 + 28), (x1 - 140, y0 - 30), (x1 - 40, y0 - 30), (x1 - 30, y0 + 28)]), (70, 70, 84),
            ow=3, hi=(0, 3, (120, 120, 140)))  # register
    c.paint(rect(x1 - 130, y0 - 54, x1 - 50, y0 - 30), (40, 40, 48), ow=3,
            pattern=lambda p: p.rect(x1 - 124, y0 - 50, x1 - 56, y0 - 34, (90, 220, 120)))
    for k in range(3):
        c.paint(rect(x0 + 20 + k * 34, y0 - 10, x0 + 48 + k * 34, y0 + 28),
                [(255, 120, 170), (120, 200, 255), (255, 220, 70)][k], ow=2.5, shade=(-3, 0))  # gum
    c.paint(ell(x0 + 150, y0 + 22, 14, 6), (240, 196, 80), ow=2.5, hi=(-2, -2, (255, 240, 170)))
    c.paint(ell(x0 + 150, y0 + 16, 10, 9), (240, 196, 80), ow=2.5, hi=(-2, -2, (255, 240, 170)))  # bell
    c.paint(poly([(x0 + 180, y0 + 30), (x0 + 196, y0 + 14), (x0 + 250, y0 + 16), (x0 + 240, y0 + 32)]),
            (246, 242, 226), ow=2.5,
            pattern=lambda p: [p.line([(x0 + 200 + k * 8, y0 + 16), (x0 + 192 + k * 8, y0 + 30)], 1, (60, 60, 60))
                               for k in range(7)])
    c.line([(x0 + 236, y0 + 12), (x0 + 258, y0 - 4)], 3, (255, 214, 60))

    # --- 1-hour photo kiosk
    x0, y0, x1, y1 = B["1-Hour Photo"]
    ky = (255, 210, 60)
    c.shadow((x0 + x1) / 2, y1 - 2, 90, 9)
    c.paint(rrect(x0, y0 + 30, x1, y1, 12), ky, ow=4, shade=(-6, 0, (210, 160, 40)), hi=(4, 4, (255, 240, 150), 2))
    c.paint(rrect(x0 - 6, y0, x1 + 6, y0 + 60, 8), (226, 44, 64), ow=3)
    c.text((x0 + x1) / 2, y0 + 20, "1-HOUR", 17, (255, 255, 255))
    c.text((x0 + x1) / 2, y0 + 42, "PHOTO", 15, (255, 240, 150))
    c.paint(rrect(x0 + 24, y0 + 84, x1 - 24, y0 + 150, 6), (40, 50, 70), ow=3,
            pattern=lambda p: p.rect(x0 + 32, y0 + 92, x1 - 32, y0 + 142, (120, 200, 240)))
    c.paint(rect(x0 + 40, y0 + 176, x1 - 40, y0 + 186), (40, 40, 48), ow=2.5)  # slot
    c.paint(rect(x0 + 28, y0 + 204, x1 - 28, y0 + 236), (255, 255, 255), ow=2,
            pattern=lambda p: p.rect(x0 + 32, y0 + 208, x1 - 32, y0 + 214, (60, 60, 70)))

    # --- freezer glow on the far right
    c.paint(rect(1720, 600, 1910, WALL_Y), (150, 200, 230), ow=3,
            pattern=lambda p: [p.rect(1730 + k * 62, 612, 1780 + k * 62, WALL_Y - 10, (210, 240, 255)) for k in range(3)])
    c.text(1815, 640, "ICE", 18, (40, 90, 160))

    lights = [(320, 60, 700, 0.5, (230, 255, 240)), (960, 60, 760, 0.55, (230, 255, 240)),
              (1600, 60, 700, 0.5, (230, 255, 240)), (1815, 700, 200, 0.3, (160, 220, 255)),
              (100, 600, 240, 0.25, (200, 120, 255))]
    light_pass(c, 0.78, lights, vign=0.35, front=0.2)
    c.save("bg_quickmart.png")


def paint_rusty_anchor():
    B = boxes("rusty_anchor")
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(1852)
    wood = (146, 88, 56)

    def planks(p):
        for y in range(0, WALL_Y, 46):
            p.line([(0, y), (W_BG, y)], 2.6, dk(wood, 0.6))
            off = rng.uniform(0, 300)
            for x in range(int(-off), W_BG, 300):
                p.line([(x, y), (x, y + 46)], 2.2, dk(wood, 0.6))
                p.ell(x + 12, y + 23, 2, 2, dk(wood, 0.5))
            if rng.random() < 0.5:
                gx = rng.uniform(0, W_BG)
                p.line([(gx, y + 18), (gx + 60, y + 20)], 1.4, lt(wood, 0.2))
    c.paint(rect(0, 0, W_BG, WALL_Y), ("vy", 0, WALL_Y, dk(wood, 0.8), wood), ow=0, pattern=planks)
    plank_floor(c, (140, 84, 50), seed=31)
    baseboard(c, color=(70, 40, 28))
    # ceiling beams + net draped across
    for bx in (300, 960, 1620):
        c.paint(rect(bx - 30, 0, bx + 30, 60), (80, 48, 32), ow=3, shade=(-4, 0))
    c.paint(rect(-10, 50, W_BG + 10, 80), (80, 48, 32), ow=3, hi=(0, 4, (130, 84, 56)))
    netc = (210, 190, 140)
    for k in range(11):
        c.curve((k * 190, 80), (k * 190 + 95, 170), (k * 190 + 190, 80), 2, netc, 0.7)
        c.curve((k * 190, 80), (k * 190 + 95, 130), (k * 190 + 190, 80), 2, netc, 0.6)
    for k in range(40):
        x = k * 48
        c.line([(x, 80), (x + 10, 120 + 30 * math.sin(k * 0.8) ** 2)], 1.6, netc, opacity=0.6)
    for sx, col in ((520, (255, 140, 60)), (1300, (255, 200, 80))):  # starfish in the net
        paint_star(c, sx, 120, 20, col)
    # lanterns
    lanterns = []
    for lx in (400, 1060, 1500):
        c.line([(lx, 80), (lx, 196)], 3, (40, 30, 26))
        c.paint(rrect(lx - 22, 196, lx + 22, 256, 6), (255, 210, 110), ow=3,
                pattern=lambda p, lx=lx: [p.line([(lx + d, 196), (lx + d, 256)], 3, (60, 50, 44)) for d in (-10, 10)])
        c.paint(poly([(lx - 28, 198), (lx + 28, 198), (lx + 14, 184), (lx - 14, 184)]), (60, 50, 44), ow=3)
        lanterns.append((lx, 226))
    # portholes with the night harbour outside
    for px in (900,):
        c.paint(ell(px, 330, 56, 56), (200, 150, 60), ow=4, hi=(-3, -3, (255, 220, 130), 3))
        c.paint(ell(px, 330, 42, 42), ("v", (30, 30, 90), (40, 80, 130)), ow=3,
                pattern=lambda p, px=px: (p.ell(px + 14, 314, 8, 8, (255, 246, 200)),
                                          p.rect(px - 42, 346, px + 42, 380, (30, 50, 100))))
        for k in range(8):
            a = math.radians(k * 45)
            c.paint(ell(px + 49 * math.cos(a), 330 + 49 * math.sin(a), 3.5, 3.5), (140, 100, 40), ow=1.6)
    # ship's wheel + life ring
    wc = (150, 92, 50)
    for k in range(8):
        a = math.radians(k * 45)
        c.paint(cap([(560 + 40 * math.cos(a), 330 + 40 * math.sin(a)), (560 + 72 * math.cos(a), 330 + 72 * math.sin(a))],
                    10), wc, ow=3)
    c.paint(ell(560, 330, 52, 52), (0, 0, 0, 0), ow=9, oc=OUT)
    c.paint(ell(560, 330, 52, 52), (0, 0, 0, 0), ow=5, oc=wc)
    c.paint(ell(560, 330, 14, 14), wc, ow=3, hi=(-2, -2, lt(wc, 0.3)))
    ring = Sh([ell_pts(1110, 470, 52, 52) + list(reversed(ell_pts(1110, 470, 30, 30)))])
    c.paint(ring, (250, 250, 244), shade=(4, 4, (210, 206, 220)),
            pattern=lambda p: [p.poly([(1110, 470), (1110 + 70 * math.cos(math.radians(a)), 470 + 70 * math.sin(math.radians(a))),
                                       (1110 + 70 * math.cos(math.radians(a + 45)), 470 + 70 * math.sin(math.radians(a + 45)))],
                                      (226, 44, 54)) for a in (0, 90, 180, 270)])
    c.text(1110, 548, "S.S. SALTY MARGARET", 10, (240, 220, 180))

    # --- exit door
    x0, y0, x1, y1 = B["Exit"]
    door_c = (96, 58, 38)
    c.paint(rect(x0 - 10, y0 - 10, x1 + 10, y1), (70, 44, 30), ow=3)
    c.paint(rect(x0, y0, x1, y1), door_c, ow=3, shade=(-5, 0),
            pattern=lambda p: [p.line([(x, y0), (x, y1)], 2, dk(door_c, 0.7)) for x in range(int(x0) + 26, int(x1), 26)])
    c.paint(ell((x0 + x1) / 2, y0 + 90, 30, 30), (200, 150, 60), ow=4)
    c.paint(ell((x0 + x1) / 2, y0 + 90, 20, 20), ("v", (60, 40, 110), (130, 60, 120)), ow=2.5)
    c.paint(ell(x1 - 20, y0 + 190, 6, 6), (200, 150, 60), ow=2)
    c.paint(rrect(x0 + 10, y0 - 52, x1 - 10, y0 - 18, 6), (40, 120, 70), ow=3)
    c.text((x0 + x1) / 2, y0 - 35, "DRY LAND", 13, (255, 255, 240))

    # --- junk barrel with net pole, boot, rope, spoon
    x0, y0, x1, y1 = B["Junk barrel"]
    bc = (150, 96, 56)
    cx = (x0 + x1) / 2
    c.shadow(cx, y1 - 6, 70, 9)
    c.line([(cx + 20, y1 - 100), (cx + 46, y0 + 4)], 6, (176, 120, 70))  # net pole
    c.paint(ell(cx + 52, y0 + 16, 22, 15, -20), (220, 200, 150, 120), ow=3,
            pattern=lambda p: [p.line([(cx + 30 + k * 9, y0), (cx + 36 + k * 9, y0 + 34)], 1.2, (180, 160, 120))
                               for k in range(5)])
    c.paint(poly([(cx - 40, y1 - 100), (cx - 46, y0 + 40), (cx - 20, y0 + 36), (cx - 16, y0 + 60), (cx - 4, y0 + 64),
                  (cx - 6, y1 - 100)], 1), (60, 120, 80), ow=3, shade=(-3, 0))  # rubber boot
    c.line([(cx, y1 - 104), (cx - 6, y0 + 40)], 3, (190, 190, 200))  # spoon
    c.paint(ell(cx - 6, y0 + 36, 6, 9), (190, 190, 200), ow=2)
    body = poly([(x0 + 10, y1 - 110), (x1 - 10, y1 - 110), (x1, y1 - 60), (x1 - 12, y1 - 6), (x0 + 12, y1 - 6),
                 (x0, y1 - 60)], 2)
    c.paint(body, bc, shade=(-6, 0, dk(bc, 0.72)), hi=(5, 0, lt(bc, 0.3), 3),
            pattern=lambda p: [p.line([(x0 + 26 + k * 22, y1 - 110), (x0 + 22 + k * 22, y1 - 6)], 2, dk(bc, 0.7))
                               for k in range(5)])
    for by in (y1 - 92, y1 - 26):
        c.paint(rect(x0 + 2, by - 5, x1 - 2, by + 5), (90, 90, 100), ow=2.5, clip=body)
    c.paint(ell(cx, y1 - 110, (x1 - x0) / 2 - 10, 10), (60, 36, 24), ow=3)
    c.paint(Sh([ell_pts(cx + 18, y1 - 112, 18, 8) + list(reversed(ell_pts(cx + 18, y1 - 112, 9, 4)))]),
            (210, 180, 120), ow=2.4)  # coil of rope

    # --- jukebox
    x0, y0, x1, y1 = B["Jukebox"]
    cx = (x0 + x1) / 2
    c.shadow(cx, y1 - 2, 96, 10)
    jb = (170, 60, 80)
    shape = Sh([ell_pts(cx, y0 + 80, (x1 - x0) / 2, 80, 0, 24, 180, 360) + [(x1, y1), (x0, y1)]])
    c.paint(shape, jb, shade=(-7, 0, dk(jb, 0.7)), hi=(5, 3, lt(jb, 0.3), 3))
    arch = Sh([ell_pts(cx, y0 + 86, (x1 - x0) / 2 - 16, 66, 0, 24, 180, 360) + [(x1 - 16, y0 + 150), (x0 + 16, y0 + 150)]])
    c.paint(arch, ("v", (255, 220, 100), (255, 110, 60)), ow=3,
            pattern=lambda p: [p.line([(x0 + 22 + k * 23, y0 + 30), (x0 + 22 + k * 23, y0 + 150)], 4,
                                      [(255, 90, 140), (120, 220, 255), (150, 255, 120), (255, 240, 120)][k % 4])
                               for k in range(6)])
    c.paint(rect(x0 + 18, y0 + 160, x1 - 18, y0 + 200), (250, 246, 230), ow=3,
            pattern=lambda p: [p.line([(x0 + 26, y0 + 168 + k * 10), (x1 - 26, y0 + 168 + k * 10)], 2, (150, 60, 80))
                               for k in range(3)])
    c.paint(rect(x0 + 18, y0 + 210, x1 - 18, y1 - 14), (60, 40, 50), ow=3,
            pattern=lambda p: [p.ell(x0 + 40 + (k % 4) * 26, y0 + 226 + (k // 4) * 18, 7, 5, (200, 200, 210))
                               for k in range(8)])
    c.paint(rrect(cx - 8, y0 + 202, cx + 8, y0 + 208, 2), (40, 40, 48), ow=2)  # coin slot
    c.glow(cx, y0 + 90, 120, (255, 160, 90), 0.5)

    # --- bar: back shelf with bottles, then the counter
    x0, y0, x1, y1 = B["Bar"]
    c.paint(rect(1180, 420, 1700, 434), (80, 48, 32), ow=3)
    c.paint(rect(1180, 520, 1700, 534), (80, 48, 32), ow=3)
    for k in range(18):
        bx = 1200 + k * 28
        for sy in (420, 520):
            col = rng.choice([(60, 140, 80), (150, 70, 40), (90, 60, 140), (200, 170, 70), (60, 110, 170)])
            hgt = rng.uniform(56, 80)
            c.paint(rrect(bx, sy - hgt + 24, bx + 20, sy, 5) + rect(bx + 6, sy - hgt, bx + 14, sy - hgt + 30), col,
                    ow=2.4, hi=(-2, 0, lt(col, 0.4), 1.5))
    c.paint(rrect(1300, 300, 1580, 360, 8), (230, 214, 170), ow=3, shade=(-3, -3))
    c.text(1440, 318, "SELF-SERVE", 16, (110, 40, 30))
    c.text(1440, 342, "PAY THE PARROT", 14, (40, 60, 110))
    bar = (110, 64, 40)
    c.shadow((x0 + x1) / 2 - 20, y1, 270, 10, 0.4)
    c.paint(rect(1180, y0 + 20, x1 + 40, y1), bar, ow=4, shade=(-6, 0, dk(bar, 0.7)),
            pattern=lambda p: [p.rect(1196 + k * 96, y0 + 50, 1270 + k * 96, y1 - 16, dk(bar, 0.85)) for k in range(5)])
    c.paint(rect(1170, y0, x1 + 50, y0 + 24), lt(bar, 0.15), ow=4, hi=(0, 4, lt(bar, 0.45)))
    c.paint(rect(1180, y1 - 30, x1 + 40, y1 - 22), (200, 150, 60), ow=2.5)  # brass foot rail
    # a couple of mugs and a bowl of peanuts on the bar
    for mx in (1300, 1520):
        c.paint(rrect(mx, y0 - 30, mx + 22, y0 + 2, 3), (230, 200, 120), ow=2.5,
                pattern=lambda p, mx=mx: p.rect(mx, y0 - 30, mx + 22, y0 - 22, (255, 250, 236)))
    c.paint(ell(1420, y0 - 4, 26, 8), (60, 110, 160), ow=2.5,
            pattern=lambda p: [p.ell(1406 + k * 7, y0 - 9, 4, 3, (210, 160, 90)) for k in range(5)])

    # --- parrot on a perch stand
    x0, y0, x1, y1 = B["Parrot"]
    cx = (x0 + x1) / 2
    c.shadow(cx, WALL_Y + 4, 34, 6)
    c.line([(cx, y1 - 10), (cx, WALL_Y)], 6, (100, 66, 40))
    c.paint(ell(cx, WALL_Y, 26, 6), (100, 66, 40), ow=3)
    c.paint(cap([(x0 + 6, y1 - 14), (x1 - 6, y1 - 14)], 8), (130, 84, 50), ow=3)
    green, green_sh = (60, 190, 80), (40, 130, 70)
    c.paint(poly([(cx - 4, y1 - 20), (cx + 10, y1 + 30), (cx + 20, y1 + 34), (cx + 14, y1 - 22)], 1), (230, 50, 50),
            ow=3)  # tail
    c.paint(ell(cx, y0 + 70, 26, 38, 10), green, shade=(4, 3, green_sh), hi=(-3, -2, (150, 240, 140), 2))
    c.paint(ell(cx + 8, y0 + 74, 14, 26, 15), (250, 210, 60), ow=2.5, shade=(2, 2, (220, 160, 40)))  # wing
    c.paint(ell(cx - 6, y0 + 30, 20, 20), green, shade=(3, 3, green_sh))
    c.paint(poly([(cx - 22, y0 + 26), (cx - 40, y0 + 36), (cx - 24, y0 + 44)], 2), (250, 210, 60), ow=2.5)  # beak
    c.paint(ell(cx - 10, y0 + 24, 5, 5), (255, 255, 255), ow=2)
    c.paint(ell(cx - 11, y0 + 24, 2, 2), OUT, ow=0)
    c.paint(ell(cx + 2, y0 + 26, 6, 6), (30, 26, 30), ow=1.6)  # eye patch (it doesn't need it)
    c.line([(cx - 6, y0 + 16), (cx + 14, y0 + 34)], 1.6)
    for fx in (cx - 6, cx + 6):
        c.line([(fx, y1 - 20), (fx, y1 - 10)], 2.4, (230, 140, 120))

    lights = [(lx, ly, 420, 0.6, (255, 190, 110)) for lx, ly in lanterns] + [
        ((B["Jukebox"][0] + B["Jukebox"][2]) / 2, 600, 360, 0.55, (255, 120, 120)),
        (900, 330, 160, 0.2, (140, 160, 255)), (1340, 330, 160, 0.2, (140, 160, 255))]
    light_pass(c, 0.74, lights, vign=0.42)
    for lx, ly in lanterns:
        c.glow(lx, ly, 110, (255, 200, 120), 0.5)
    c.save("bg_rusty_anchor.png")


ASSETS = {"bg_downtown": paint_downtown, "bg_quickmart": paint_quickmart, "bg_rusty_anchor": paint_rusty_anchor,
          "hs_bree_marlowe": paint_bree_marlowe, "hs_lou": paint_lou, "hs_captain_gus": paint_captain_gus,
          "icon_fishing_net": paint_icon_fishing_net, "icon_wish_quarter": paint_icon_wish_quarter,
          "icon_gus_coaster": paint_icon_gus_coaster, "icon_captains_hat": paint_icon_captains_hat,
          "icon_disposable_camera": paint_icon_disposable_camera, "icon_full_camera": paint_icon_full_camera,
          "icon_headshots": paint_icon_headshots, "icon_diner_name_tag": paint_icon_diner_name_tag,
          "icon_finished_crossword": paint_icon_finished_crossword}


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
