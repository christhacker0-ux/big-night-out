#!/usr/bin/env python3
"""
Big Night Out -- Act 3 ("Lab Rats") repainted in "style 2" (see Docs/ART_STYLE.md).

Paints the five Act 3 backgrounds (Science Hall, Lab 3B, rooftop, basement, faculty lounge), the Act 3
characters (Dr. Mina Volt, Sky Rivera, Dot Pruitt, Professor Crumb) and the Act 3 prop sprites (pigeon,
Professor Nibbles, Mr. Bones' coat, the shower puddle) with tools/art/style2.py, in the same look as
act1_style2.py: perspective rooms, grungy magenta / teal walls, warm lamp light, violet shadows, dark
out-of-focus foreground framing and tall characters at the same scale as Dex.

This supersedes the Act 3 painters in act3.py (which still runs and would overwrite these files: use
this script for them). Item icons are unchanged and still come from act3.py.

Usage:  python3 tools/art/act3_style2.py              # paint everything
        python3 tools/art/act3_style2.py lab mina     # paint assets whose name contains these words
        python3 tools/art/act3_style2.py --layout     # write LAYOUT (walkable, hotspots, entries) into act3.json
        BNO_COMPOSITES=/some/dir python3 tools/art/act3_style2.py --composite [room ids]
"""
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style2 import *  # noqa: F401,F403,E402
import act1_style2 as A1  # noqa: E402  (shared helpers: walls, doors, windows, outfit bits)
from act1_style2 import (grunge_wall, skirting, two_tone_wall, window_flat, doorway_flat, panel_light,  # noqa: E402
                         exit_sign, corkboard, fire_extinguisher, legs, soft_shade, glasses, folds, hair_strands,
                         clip_draw, sprite_grade, banker_lamp, BRICK, MORTAR, DEX_H)

WORLD = os.path.join(ROOT, "Assets", "_Project", "World", "act3.json")
Y_TOP, Y_BOT = 762, 975
NPC_FEET_Y = 945            # world y -4.05, the same as Act 1
LAYOUT = {}


def std_room(seed, back=(330, 250, 1590, 690), light=(-0.3, -0.95), fc=1000, vp_x=960):
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=light, lw=3.4, seed=seed)
    R = Room(c, (vp_x, vp_for_walk(Y_TOP, Y_BOT)), back, fc=fc)
    return c, R, random.Random(seed)


def side_door(sub, z0, z1, h, col, frame=(230, 214, 226), window=False, sign=None, knob="R", seed=0):
    """A door on a side wall, in that wall's flat space (a = Z, b = Y)."""
    x0, x1 = sorted((sub.ax(z0), sub.ax(z1)))
    flat_door(sub, x0, sub.by(h), x1, sub.by(0), col, frame=frame, knob=knob, window=window, sign=sign, seed=seed)
    return x0, x1, sub.by(h), sub.by(0)


def wall_clock(c, x, y, r=34, col=(250, 246, 236), rim=(60, 50, 80), t=(10, 9)):
    c.ink(ell(x, y, r + 6, r + 6), rim, lw=3.0, shade=0.4, hi=0.4, hw=3)
    c.ink(ell(x, y, r, r), col, lw=2.0, shade=0.3, sw=8, hi=0)
    for k in range(12):
        a = math.radians(k * 30)
        c.stroke([(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78), (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)],
                 2.0 if k % 3 == 0 else 1.2, INK, taper=(0, 0))
    hh, mm = t
    for ang, L, w in ((hh * 30 + mm * 0.5, 0.5, 3.4), (mm * 6, 0.78, 2.2)):
        a = math.radians(ang - 90)
        c.stroke([(x, y), (x + math.cos(a) * r * L, y + math.sin(a) * r * L)], w, INK, taper=(0, 0.3))
    c.ink(ell(x, y, 3, 3), (220, 50, 70), lw=1.2)


def caged_light(c, x, y, r=12, col=(255, 236, 170), strength=0.5, cone_to=None):
    """Bulkhead work light with a wire cage, mounted on a wall at (x, y)."""
    c.ink(rrect(x - r * 1.1, y - r * 1.6, x + r * 1.1, y - r * 1.0, 3), (70, 66, 80), lw=2.2, shade=0.3)
    c.ink(ell(x, y, r, r * 1.05), col, lw=2.0, shade=0, hi=0, ao=0)
    for k in (-0.5, 0, 0.5):
        c.stroke([(x + r * k, y - r * 1.0), (x + r * k * 1.4, y + r * 0.9)], 1.4, (60, 56, 70), taper=(0, 0))
    c.stroke(ell_pts(x, y, r * 1.08, r * 0.4, 0, 20, 0, 180), 1.4, (60, 56, 70), taper=(0, 0))
    c.glow2(x, y, r * 10, GLOW, strength)
    c.glow2(x, y, r * 2.6, (255, 255, 230), 0.7)
    if cone_to:
        c.light_cone((x, y), (x - r * 14, cone_to), (x + r * 14, cone_to), strength=0.18, blur_px=30)


def potted_plant(c, x, y, s=1.0, col=(50, 150, 110), pot=(210, 110, 70), seed=0):
    rng = random.Random(seed)
    for k in range(7):
        a = math.radians(-90 + rng.uniform(-60, 60))
        L = 70 * s * rng.uniform(0.6, 1.0)
        tip = (x + math.cos(a) * L, y - 30 * s + math.sin(a) * L)
        mid = (x + math.cos(a) * L * 0.5 + rng.uniform(-10, 10) * s, y - 30 * s + math.sin(a) * L * 0.5)
        spine = bez((x, y - 30 * s), mid, tip, 12)
        wv = [3 * s] + [12 * s * math.sin(math.pi * i / 12) + 2 for i in range(1, 12)] + [2]
        c.ink(limb(spine, wv, smooth=0), mix(col, (30, 90, 80), rng.uniform(0, 0.4)), lw=2.0, shade=0.35, hi=0.3, ao=0)
    c.ink(Sh([[(x - 24 * s, y - 38 * s), (x + 24 * s, y - 38 * s), (x + 18 * s, y), (x - 18 * s, y)]]), pot, lw=2.6, shade=0.45,
          hi=0.35)
    c.ink(rect(x - 27 * s, y - 44 * s, x + 27 * s, y - 34 * s), hi_col(pot, 0.1), lw=2.2, shade=0.3)


# =========================================================================== layout -> act3.json, composites
def _sprite_size(name):
    im = Image.open(os.path.join(OUT_DIR, name + ".png"))
    return im.size


def _inside(poly_px, x, y):
    n, ins = len(poly_px), False
    for i in range(n):
        (x0, y0), (x1, y1) = poly_px[i], poly_px[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            ins = not ins
    return ins


def write_layout(path=WORLD):
    data = json.load(open(path))
    problems = []
    for room in data["rooms"]:
        L = LAYOUT.get(room["id"])
        if not L:
            continue
        wp = L["walk_px"]
        ys = [p[1] for p in wp]
        if min(ys) != Y_TOP or max(ys) != Y_BOT:
            problems.append("%s: walkable spans %s..%s" % (room["id"], min(ys), max(ys)))
        room["walkable"] = [v for p in wp for v in px_to_world(*p)]
        for e in room.get("entries", []):
            if e["name"] in L["entries"]:
                e["pos"] = list(px_to_world(*L["entries"][e["name"]]))
            else:
                problems.append("%s: no layout for entry %s" % (room["id"], e["name"]))
            if not _inside(wp, *world_to_px(*e["pos"])):
                problems.append("%s: entry %s outside walkable" % (room["id"], e["name"]))
        seen = {}
        for h in room["hotspots"]:
            n = seen.get(h["name"], 0)
            seen[h["name"]] = n + 1
            spec = L["hotspots"].get((h["name"], n))
            if not spec:
                problems.append("%s: no layout for %s %d" % (room["id"], h["name"], n))
                continue
            if "npc" in spec or "sprite" in spec:
                nm = spec.get("npc") or spec["sprite"]
                w, hh = _sprite_size(nm)
                fx, fy = spec["feet"]
                bw = spec.get("w", 1.9) if "npc" in spec else round(w / 100, 2)
                h["feet"] = list(px_to_world(fx, fy))
                h["size"] = [bw, round(hh / 100, 2)]
            else:
                x0, y0, x1, y1 = spec["box"]
                h["feet"] = list(px_to_world((x0 + x1) / 2, y1))
                h["size"] = [round((x1 - x0) / 100, 2), round((y1 - y0) / 100, 2)]
            h["standAt"] = list(px_to_world(*spec["stand"]))
            if not _inside(wp, *spec["stand"]):
                problems.append("%s: stand point of %s outside walkable" % (room["id"], h["name"]))
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    print("updated", os.path.relpath(path, ROOT))
    for p in problems:
        print("  PROBLEM:", p)


COMPOSITE_DIR = os.environ.get("BNO_COMPOSITES", os.path.join(ROOT, "..", "composites"))


def composite(room_id, out_dir=None, boxes=True, flags=()):
    """Background + sprites at their feet (unscaled, like the game) + Dex (depth-scaled) at the two front
    stand points and at the back of the walkable area, with hotspot boxes and the walkable outline.
    flags: showWhenFlag values to treat as set (to see the conditional sprites)."""
    out_dir = out_dir or COMPOSITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(WORLD))
    room = [r for r in data["rooms"] if r["id"] == room_id][0]
    bg = Image.open(os.path.join(OUT_DIR, "bg_%s.png" % room_id)).convert("RGBA")
    walk = room.get("walkable")
    wp = [world_to_px(walk[i], walk[i + 1]) for i in range(0, len(walk), 2)]
    yb, yt = max(p[1] for p in wp), min(p[1] for p in wp)
    dex = Image.open(os.path.join(OUT_DIR, "player_dex.png"))
    items = []
    for h in room["hotspots"]:
        if h.get("showWhenFlag") and h["showWhenFlag"] not in flags:
            continue
        if h.get("hideWhenFlag") and h["hideWhenFlag"] in flags:
            continue
        slug = re.sub("[^a-z0-9]+", "_", h["name"].lower()).strip("_")
        path = os.path.join(OUT_DIR, "hs_%s.png" % slug)
        if os.path.exists(path):
            fx, fy = world_to_px(*h["feet"])
            items.append((fy, Image.open(path), fx, False))
    stands = [world_to_px(*h["standAt"]) for h in room["hotspots"] if not h.get("showWhenFlag")]
    stands = sorted(stands, key=lambda p: -p[1])[:2] + [((wp[0][0] + wp[1][0]) / 2, yt)]
    for (sx, sy) in stands:
        k = 1.0 - 0.4 * (yb - sy) / max(1, yb - yt)
        im = dex.resize((int(dex.width * k), int(dex.height * k)), Image.LANCZOS)
        items.append((sy, im, sx, True))
    for fy, im, fx, is_dex in sorted(items, key=lambda t: t[0]):
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
    out = os.path.join(out_dir, "composite_%s%s.png" % (room_id, "_flags" if flags else ""))
    bg.convert("RGB").save(out)
    print("wrote", out)
    return out


# =========================================================================== 1. Science Hall
def skeleton(c, x, y_floor, h, coat=False):
    """Mr. Bones: a model skeleton on a rolling stand, feet on the stand base at (x, y_floor), h tall.
    Drawn as a friendly cartoon (round skull, big eye sockets), one hand raised in a wave."""
    BONE, BONE_SH = (244, 236, 214), (186, 170, 168)
    u = h / 100.0
    P = lambda a, b: (x + a * u, y_floor - b * u)
    # stand: base with castors, pole up the back to the skull
    c.ink(Sh([[P(-20, 3), P(20, 3), P(16, -1), P(-16, -1)]]), (80, 80, 100), lw=2.6, shade=0.3, hi=0.3)
    for a in (-17, 0, 17):
        c.ink(ell(*P(a, -2.5), 3.2 * u, 3.2 * u), (40, 36, 50), lw=2.0, shade=0.2)
    c.stroke([P(-3, 2), P(-3, 88)], 3.0 * u, INK, taper=(0, 0))
    c.stroke([P(-3, 2), P(-3, 88)], 1.6 * u, (150, 150, 170), taper=(0, 0))
    kw = dict(lw=2.6, shade=0.45, scol=BONE_SH, hi=0.4, hw=3, tex=0.1)

    def bone(a, b, w):
        c.ink(limb([P(*a), P(*b)], [w * u * 1.15, w * u * 0.8], smooth=0), BONE, **kw)
        for q in (a, b):
            c.ink(ell(*P(*q), w * u * 0.62, w * u * 0.62), BONE, lw=2.2, shade=0.3, scol=BONE_SH, hi=0.3)
    # legs and feet
    for sx in (-1, 1):
        bone((sx * 5, 47), (sx * 6, 25), 3.2)
        bone((sx * 6, 25), (sx * 6, 5), 2.8)
        c.ink(blob([P(sx * 6 - 2, 6), P(sx * 6 + 8, 4.5), P(sx * 6 + 9, 2.2), P(sx * 6 - 3, 2.2)], 1), BONE, lw=2.2, shade=0.3,
              scol=BONE_SH)
    # pelvis
    for sx in (-1, 1):
        c.ink(blob([P(sx * 1, 52.5), P(sx * 7.5, 54), P(sx * 8.2, 50), P(sx * 5, 46.5), P(sx * 1, 47.5)], 1), BONE, **kw)
    # spine
    for k in range(9):
        c.ink(rrect(*P(-2.2, 54 + k * 3.4 + 2.4), *P(2.2, 54 + k * 3.4), 2), BONE, lw=1.8, shade=0.3, scol=BONE_SH, hi=0.3)
    # ribcage
    for k in range(5):
        yy = 76 - k * 4.2
        w = 11 - abs(k - 1.5) * 1.3
        for sx in (-1, 1):
            c.stroke([P(0, yy + 1.2), P(sx * w * 0.8, yy + 0.4), P(sx * w, yy - 2.6)], 2.6 * u, INK, taper=(0.1, 0.4), smooth=1)
            c.stroke([P(0, yy + 1.2), P(sx * w * 0.8, yy + 0.4), P(sx * w, yy - 2.6)], 1.5 * u, BONE, taper=(0.1, 0.4), smooth=1)
    c.ink(rrect(*P(-1.6, 80), *P(1.6, 62), 2), BONE, lw=1.8, shade=0.3, scol=BONE_SH)
    # collarbones and arms: near arm hanging, far arm waving
    bone((-12, 80), (12, 80), 1.6)
    bone((-12, 79), (-15, 61), 2.2)
    bone((-15, 61), (-15, 45), 1.9)
    bone((12, 79), (22, 92), 2.2)
    bone((22, 92), (24, 108), 1.9)
    for k, a in enumerate((-30, -10, 10, 30)):
        ar = math.radians(a - 90)
        c.stroke([P(24, 109), P(24 + math.cos(ar) * 5, 109 - math.sin(ar) * 5)], 1.5 * u, INK, taper=(0, 0.3))
    for k, a in enumerate((-20, 0, 20)):
        c.stroke([P(-15, 44), P(-15 + a * 0.12, 39)], 1.3 * u, INK, taper=(0, 0.3))
    # skull: round cranium, big friendly sockets, a grin
    sx_, sy_ = P(1, 90)
    r = 9.2 * u
    c.ink(rrect(sx_ - r * 0.45, sy_ - r * 0.1, sx_ + r * 0.55, sy_ + r * 0.55, 4), BONE, lw=2.4, shade=0.3, scol=BONE_SH)
    c.ink(ell(sx_, sy_ - r * 0.55, r, r * 0.95), BONE, lw=2.8, shade=0.5, sw=r * 0.5, scol=BONE_SH, hi=0.45, hw=r * 0.25)
    for ex in (-0.38, 0.38):
        c.ink(ell(sx_ + ex * r, sy_ - r * 0.5, r * 0.28, r * 0.32), (50, 30, 60), lw=2.0, shade=0, hi=0)
        c.ink(ell(sx_ + ex * r + r * 0.06, sy_ - r * 0.58, r * 0.08, r * 0.08), (255, 250, 230), lw=0, shade=0, hi=0)
    c.ink(Sh([[(sx_ - r * 0.08, sy_ - r * 0.12), (sx_ + r * 0.08, sy_ - r * 0.12), (sx_, sy_ - r * 0.28)]]), (50, 30, 60), lw=1.4)
    c.stroke(bez((sx_ - r * 0.45, sy_ + r * 0.1), (sx_, sy_ + r * 0.35), (sx_ + r * 0.48, sy_ + r * 0.08), 10), 2.0, INK, taper=(0.2, 0.2))
    for k in range(5):
        xx = sx_ - r * 0.32 + k * r * 0.16
        c.stroke([(xx, sy_ + r * 0.14), (xx, sy_ + r * 0.3)], 1.2, INK, taper=(0, 0))
    return P(0, 100)


def paint_science_hall():
    c, R, rng = std_room(300, back=(230, 240, 1690, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (198, 72, 156)
    DADO = (36, 150, 158)
    TILE_A, TILE_B = (238, 214, 176), (120, 76, 150)

    def ceil(sub):
        w, h = sub.w, sub.h
        sub.ink(rect(0, 0, w, h), (126, 106, 150), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 96 * sub.density
        for x in np.arange(0, w, step):
            sub.stroke([(x, 0), (x, h)], 2.6, (104, 88, 128), taper=(0, 0))
        for y in np.arange(0, h, step * 0.8):
            sub.stroke([(0, y), (w, y)], 2.6, (104, 88, 128), taper=(0, 0))
        for _ in range(9):
            stain(sub, rng.uniform(0, w), rng.uniform(0, h), rng.uniform(30, 70), (120, 80, 40), 0.25, 0, rng.randint(0, 99))
        x, y = sub.ax(980), sub.by(190)
        sub.ink(rect(x, y, x + step, y + step * 0.8), (30, 16, 40), lw=2.4)          # missing tile
        x2, y2 = sub.ax(300), sub.by(320)
        sub.ink(Sh([[(x2, y2), (x2 + step, y2), (x2 + step * 1.1, y2 + step * 0.5), (x2 + step * 0.1, y2 + step * 0.9)]]),
                (150, 130, 170), lw=2.4, shade=0.3)                                    # a sagging tile

    def wall_paint(sub, w, h, seed):
        grunge_wall(sub, w, h, WALL, seed=seed, chips=4, stains=3, floor_y=h)
        y0 = h * 0.62
        # glazed tile dado (science building) with a yellow rail
        sub.ink(rect(-4, y0, w + 4, h), DADO, lw=0, shade=0, hi=0, ao=0, tex=0.12, wob=0)
        tw = 34 * getattr(sub, "density", 1.0)
        for yy in np.arange(y0 + 8, h, tw * 0.7):
            sub.stroke([(0, yy), (w, yy)], 1.6, shade_col(DADO, 0.7), taper=(0, 0), opacity=0.7)
        for k, yy in enumerate(np.arange(y0 + 8, h, tw * 0.7)):
            for xx in np.arange((k % 2) * tw / 2, w, tw):
                sub.stroke([(xx, yy), (xx, yy + tw * 0.7)], 1.4, shade_col(DADO, 0.7), taper=(0, 0), opacity=0.6)
        for _ in range(int(w / 120)):
            xx, yy = rng.uniform(0, w), rng.uniform(y0 + 20, h - 20)
            sub.ink(rect(xx, yy, xx + tw, yy + tw * 0.7), hi_col(DADO, 0.25), lw=0, shade=0, hi=0, ao=0, opacity=0.5)
        for _ in range(2):
            chip(sub, rng.uniform(0, w), rng.uniform(y0 + 30, h - 30), rng.uniform(18, 34), BRICK, MORTAR, DADO,
                 seed=rng.randint(0, 99))
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)
        sub.ink(rect(-4, y0 - 10, w + 4, y0 + 8), (250, 200, 90), lw=2.4, shade=0.4, hi=0.4)
        skirting(sub, w, h, col=(40, 60, 90))

    def left(sub):
        wall_paint(sub, sub.w, sub.h, 31)
        # glass double doors out to the quad (night outside)
        x0, x1 = sub.ax(200), sub.ax(40)
        y0, y1 = sub.by(300), sub.by(0)
        sub.ink(rect(x0 - 22, y0 - 22, x1 + 22, y1), (210, 200, 220), lw=3.0, shade=0.4, sw=10, hi=0.3)
        night_sky(sub, x0, y0, x1, y1, seed=5, top=(30, 20, 80), bot=(120, 60, 140))
        xm = (x0 + x1) / 2
        for xa, xb in ((x0, xm), (xm, x1)):
            sub.ink(rect(xa, y0, xb, y1), (0, 0, 0, 0), lw=0, line_only=True)
            sub.ink(rect(xa + 6, y0 + 6, xb - 6, y1 - 6), (0, 0, 0, 0), lw=10, oc=(170, 160, 190), line_only=True, wob=0.3)
            sub.ink(rect(xa + 10, y0 + (y1 - y0) * 0.55, xb - 10, y0 + (y1 - y0) * 0.6), (200, 196, 210), lw=2.2, shade=0.3)
            sub.stroke([(xa + 20, y1 - 40), (xa + (xb - xa) * 0.6, y0 + 30)], 9, (255, 255, 255), opacity=0.16)
        sub.ink(rect(x0 - 26, y0 - 70, x1 + 26, y0 - 26), (40, 40, 80), lw=2.6, shade=0.3)
        sub.text(xm, y0 - 48, "< TO THE QUAD", 17 * sub.density, (255, 230, 140))
        fire_extinguisher(sub, sub.ax(300), sub.by(40), 90 * sub.density)

    def right(sub):
        wall_paint(sub, sub.w, sub.h, 32)
        # heavy fire door to the roof stairs, with a wired-glass slot
        x0, x1 = sub.ax(40), sub.ax(200)
        y0, y1 = sub.by(300), sub.by(0)
        flat_door(sub, x0, y0, x1, y1, (200, 70, 70), frame=(210, 200, 220), knob="L", window=True, seed=8)
        sub.ink(rect(x0 + (x1 - x0) * 0.08, y0 + (y1 - y0) * 0.6, x1 - (x1 - x0) * 0.08, y0 + (y1 - y0) * 0.66),
                (200, 196, 210), lw=2.4, shade=0.3, hi=0.4)       # push bar
        sub.ink(rect(x0 - 26, y0 - 70, x1 + 26, y0 - 26), (40, 40, 80), lw=2.6, shade=0.3)
        sub.text((x0 + x1) / 2, y0 - 48, "ROOF ^", 18 * sub.density, (255, 230, 140))
        exit_sign(sub, (x0 + x1) / 2, y0 - 110, 120, "EXIT")
        # a trophy case of old science-fair ribbons further forward
        tx0, tx1 = sub.ax(250), sub.ax(330)
        sub.ink(rect(tx0, sub.by(250), tx1, sub.by(70)), (90, 60, 110), lw=3.0, shade=0.3)
        sub.ink(rect(tx0 + 10, sub.by(240), tx1 - 10, sub.by(80)), (60, 120, 140), lw=2.4, shade=0.2)

    def floor(sub):
        tiles(sub, TILE_A, TILE_B, 0, 0, sub.w, sub.h, size=56 * sub.density, seed=37, chipped=0.1)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 80), (60, 30, 50), 0.12, 0, rng.randint(0, 99))
        # scuffed lane down the middle where everyone walks
        sub.soft(rect(-10, sub.by(260), sub.w + 10, sub.by(560)), (40, 10, 40), 0.12, 40)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=300)

    def back(sub):
        wall_paint(sub, sub.w, sub.h, 33)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=33)
    R.ao(0.5)
    R.edges(w=4.0)

    # --- notice board with the MISSING poster (X 40..230, Y 190..330)
    bx0, by0 = P(40, 330)
    bx1, by1 = P(230, 190)
    corkboard(c, bx0, by0, bx1, by1,
              [(bx0 + 112, by0 + 12, 64, 50, (160, 230, 255), ["TUTOR", "$5/HR", "(I CRY)"]),
               (bx0 + 116, by0 + 74, 62, 48, (255, 240, 140), ["LAB", "SAFETY", "QUIZ!"])], seed=6)

    def missing(p, w_, h_):
        p.text(w_ / 2, h_ * 0.12, "MISSING", 15, (210, 40, 60))
        p.ink(ell(w_ / 2, h_ * 0.5, w_ * 0.3, h_ * 0.22), (240, 170, 90), lw=2.0, shade=0.3)
        p.ink(ell(w_ / 2 - w_ * 0.18, h_ * 0.34, w_ * 0.08, h_ * 0.06), (240, 170, 90), lw=1.6)
        p.ink(ell(w_ / 2 + w_ * 0.18, h_ * 0.34, w_ * 0.08, h_ * 0.06), (240, 170, 90), lw=1.6)
        p.ink(ell(w_ / 2 - w_ * 0.1, h_ * 0.47, 2.4, 2.4), INK, lw=0)
        p.ink(ell(w_ / 2 + w_ * 0.1, h_ * 0.47, 2.4, 2.4), INK, lw=0)
        p.ink(Sh([[(w_ * 0.3, h_ * 0.3), (w_ * 0.7, h_ * 0.3), (w_ * 0.5, h_ * 0.22)]]), (40, 40, 60), lw=1.2)
        p.text(w_ / 2, h_ * 0.8, "PROF. NIBBLES", 8, (40, 30, 60), "Black")
        p.text(w_ / 2, h_ * 0.91, "likes tubes + seeds", 6, (90, 60, 70), "Bold")
    poster(c, bx0 + 56, by0 + 68, 92, 118, (252, 248, 236), missing, angle=-3, seed=21)

    # --- basement door (custodial), with polka notes leaking from under it (X 270..420)
    dx0, dy0 = P(270, 280)
    dx1, dy1 = P(420, 0)

    def custodial(cc, cx, cy):
        cc.ink(rrect(cx - 46, cy - 20, cx + 46, cy + 30, 4), (250, 248, 236), lw=2.2, shade=0.2)
        cc.text(cx, cy - 6, "CUSTODIAL", 9.5, (40, 60, 120))
        cc.text(cx, cy + 12, "STAFF ONLY", 9.5, (200, 30, 40))
    flat_door(c, dx0, dy0, dx1, dy1, (120, 90, 80), frame=(210, 200, 220), knob="R", sign=custodial, seed=4)
    c.ink(rrect((dx0 + dx1) / 2 - 70, dy0 - 64, (dx0 + dx1) / 2 + 70, dy0 - 26, 5), (250, 200, 80), lw=2.6, shade=0.3)
    c.text((dx0 + dx1) / 2, dy0 - 45, "BASEMENT v", 15, (60, 30, 40))
    c.glow2((dx0 + dx1) / 2, dy1 - 4, 90, (255, 200, 120), 0.35, sy=0.25)
    for k, (nx, ny) in enumerate(((dx1 + 10, dy1 - 30), (dx1 + 34, dy1 - 58), (dx1 + 18, dy1 - 92))):
        c.stroke([(nx, ny), (nx, ny - 20)], 2.4, (255, 236, 150), taper=(0, 0))
        c.ink(ell(nx - 5, ny, 6, 4.5, -20), (255, 236, 150), lw=1.6)
        if k == 1:
            c.stroke([(nx, ny - 20), (nx + 10, ny - 14)], 2.4, (255, 236, 150), taper=(0, 0))

    # --- air vent low on the wall, screws loose (X 450..550, Y 15..80)
    vx0, vy0 = P(450, 80)
    vx1, vy1 = P(550, 15)
    c.ink(rect(vx0 - 6, vy0 - 6, vx1 + 6, vy1 + 6), (180, 180, 196), lw=2.8, shade=0.35, hi=0.3)
    c.ink(rect(vx0, vy0, vx1, vy1), (30, 20, 40), lw=2.0)
    for yy in np.arange(vy0 + 8, vy1 - 2, 9):
        c.ink(rect(vx0 + 4, yy - 3, vx1 - 4, yy + 2), (170, 170, 190), lw=1.4, shade=0.3)
    for (sx_, sy_) in ((vx0 + 2, vy0 + 2), (vx1 - 2, vy0 + 2), (vx0 + 2, vy1 - 2)):
        c.ink(ell(sx_, sy_, 3, 3), (120, 120, 140), lw=1.2)
    c.ink(ell(vx1 + 12, vy1 + 18, 3, 2), (120, 120, 140), lw=1.2)     # the screw that fell out
    cobweb(c, vx0, vy0, 26, "tl", opacity=0.4)

    # --- Mr. Bones on his stand (X 590..700, Z 40) with a TA ON BREAK sign; his coat is a sprite
    bxx, byy = P(645, 0, 40)
    R.contact(590, 700, 30, 50, 0.45)
    skeleton(c, bxx, byy, 290 * R.k(40))
    sx0, sy0 = P(560, 150)
    c.ink(Sh([rot_pts([(sx0 - 40, sy0 - 20), (sx0 + 40, sy0 - 20), (sx0 + 40, sy0 + 22), (sx0 - 40, sy0 + 22)], -6, sx0, sy0)]),
          (255, 240, 140), lw=2.2, shade=0.2)
    c.text(sx0, sy0 - 6, "TA ON", 9, (60, 40, 70), angle=6)
    c.text(sx0, sy0 + 8, "BREAK", 9, (200, 40, 60), angle=6)
    # coat hook (the coat sprite hangs from it)
    hx_, hy_ = P(765, 250)
    c.ink(rect(hx_ - 22, hy_ - 8, hx_ + 22, hy_ + 4), (140, 90, 60), lw=2.4, shade=0.4, hi=0.3)
    c.stroke([(hx_, hy_ + 2), (hx_ + 2, hy_ + 16), (hx_ + 10, hy_ + 14)], 3.0, (200, 200, 210), taper=(0, 0))

    # --- periodic table poster (X 760..1000, Y 290..430)
    def ptable(p, w_, h_):
        p.ink(rect(0, 0, w_, h_), (40, 50, 90), lw=0)
        p.text(w_ / 2, 14, "PERIODIC TABLE OF SNACKS", 10, (255, 230, 120))
        cols = [(255, 120, 150), (255, 200, 90), (110, 220, 200), (160, 140, 255), (140, 230, 120)]
        cw, ch = (w_ - 16) / 18, (h_ - 40) / 7
        for r_ in range(7):
            for k in range(18):
                if r_ == 0 and 0 < k < 17:
                    continue
                if r_ in (1, 2) and 1 < k < 12:
                    continue
                x_, y_ = 8 + k * cw, 28 + r_ * ch
                p.ink(rect(x_ + 1, y_ + 1, x_ + cw - 1, y_ + ch - 1), cols[(k // 3 + r_) % 5], lw=0.8, shade=0.1, hi=0)
    tx0, ty0 = P(760, 395)
    tx1, ty1 = P(1000, 255)
    poster(c, (tx0 + tx1) / 2, (ty0 + ty1) / 2, tx1 - tx0, ty1 - ty0, (40, 50, 90), ptable, angle=1, seed=22, peel="br")

    # --- Lab 3B door (X 1020..1170): window glowing teal, DARE ROUND star
    lx0, ly0 = P(1020, 280)
    lx1, ly1 = P(1170, 0)

    def lab_sign(cc, cx, cy):
        cc.ink(rrect(cx - 40, cy - 70, cx + 40, cy - 46, 4), (250, 248, 236), lw=2.2, shade=0.2)
        cc.text(cx, cy - 58, "LAB 3B", 13, (40, 60, 120))
    flat_door(c, lx0, ly0, lx1, ly1, (60, 110, 200), frame=(210, 200, 220), knob="L", window=True, sign=lab_sign, seed=5)
    wx0, wy0 = lx0 + (lx1 - lx0) * 0.2, ly0 + (ly1 - ly0) * 0.08
    wx1, wy1 = lx1 - (lx1 - lx0) * 0.2, ly0 + (ly1 - ly0) * 0.38
    c.ink(rect(wx0, wy0, wx1, wy1), ("v", (120, 255, 230), (40, 170, 170)), lw=2.4, shade=0.2)
    c.stroke([(wx0 + 6, wy1 - 8), (wx0 + (wx1 - wx0) * 0.5, wy0 + 6)], 4, (255, 255, 255), opacity=0.45)
    c.glow2((wx0 + wx1) / 2, (wy0 + wy1) / 2, 130, (90, 255, 220), 0.35)
    tx, ty = (lx0 + lx1) / 2, ly0 + (ly1 - ly0) * 0.72
    star = [(tx + math.cos(math.radians(-90 + k * 36)) * (30 if k % 2 == 0 else 13),
             ty + math.sin(math.radians(-90 + k * 36)) * (30 if k % 2 == 0 else 13)) for k in range(10)]
    c.ink(Sh([star]), (255, 90, 170), lw=2.4, shade=0.3, hi=0.4)
    c.text(tx, ty - 2, "DARE", 8, (255, 255, 240))
    c.text(tx, ty + 8, "ROUND", 6.5, (255, 255, 240), "Bold")
    c.ink(Sh([[(tx + 50, ly0 + 60), (tx + 72, ly0 + 98), (tx + 28, ly0 + 98)]]), (255, 220, 60), lw=2.4, shade=0.2)
    c.text(tx + 50, ly0 + 88, "!", 18, INK)
    wall_clock(c, (lx0 + lx1) / 2, ly0 - 80, 30, t=(11, 52))

    # --- faculty lounge door (X 1230..1400): polished wood, brass plaque, angry note
    fx0, fy0 = P(1230, 290)
    fx1, fy1 = P(1400, 0)

    def plaque(cc, cx, cy):
        cc.ink(rrect(cx - 42, cy - 70, cx + 42, cy - 44, 4), (236, 196, 100), lw=2.2, shade=0.3, hi=0.5)
        cc.text(cx, cy - 63, "FACULTY", 9, (96, 56, 20))
        cc.text(cx, cy - 51, "LOUNGE", 8, (96, 56, 20), "Bold")
        note = Sh([rot_pts([(cx - 40, cy - 22), (cx + 40, cy - 22), (cx + 40, cy + 40), (cx - 40, cy + 40)], 4, cx, cy)])
        cc.ink(note, (252, 250, 236), lw=2.0, shade=0.2)
        for k, (t_, col) in enumerate((("NO STUDENTS", (200, 30, 40)), ("NO EXCEPTIONS", INK), ("NO, NOT", INK),
                                       ("EVEN YOU", (200, 30, 40)))):
            cc.text(cx + 1 - k * 1, cy - 10 + k * 13, t_, 7.5, col, "Bold", angle=-4)
    flat_door(c, fx0, fy0, fx1, fy1, (130, 70, 50), frame=(90, 50, 40), knob="L", sign=plaque, seed=6)
    c.glow2((fx0 + fx1) / 2, fy1 - 4, 90, (255, 170, 80), 0.3, sy=0.25)
    # small potted plant + a water fountain between the doors
    potted_plant(c, *P(1205, 0, 20), s=1.0, seed=3)

    # --- ceiling: fluorescent panels, SCIENCE HALL banner, pipes and cables
    lamps = []
    for X0, flick in ((150, False), (620, False), (1090, True)):
        panel_light(c, R, X0, X0 + 220, 110, 210, cone=0.2, flicker=flick)
        lamps.append((R.pt(X0 + 110, Hb - 14, 160), flick))
    pipe(c, [P(0, Hb - 40, 30), P(Wb, Hb - 40, 30)], w=22, col=(110, 170, 180), brackets=[P(300, Hb - 40, 30), P(1100, Hb - 40, 30)])
    pipe(c, [P(0, Hb - 70, 10), P(520, Hb - 70, 10), P(520, Hb - 20, 10)], w=14, col=(200, 120, 90))
    cable(c, P(0, Hb, 240), P(700, Hb, 320), sag=60, w=7, col=(40, 30, 70))
    cable(c, P(700, Hb, 320), P(Wb, Hb, 240), sag=40, w=6, col=(40, 130, 130))
    hanging_cable(c, P(1300, Hb, 260), 120, sway=-14, w=6, col=(40, 30, 70), seed=4)
    # banner hanging from the ceiling nearer the camera
    a, b_ = P(450, Hb, 300), P(1010, Hb, 300)
    ya = P(450, Hb - 30, 300)[1]
    for xx in (a[0] + 40, b_[0] - 40):
        c.stroke([(xx, a[1]), (xx, ya)], 2.4, (60, 60, 80), taper=(0, 0))
    ban = Sh([[(a[0], ya), (b_[0], ya), (b_[0] - 6, ya + 64), ((a[0] + b_[0]) / 2, ya + 74), (a[0] + 6, ya + 64)]])
    c.ink(ban, (60, 60, 180), lw=3.0, shade=0.45, sw=20, hi=0.3, rim=0.2)
    c.ink(Sh([[(a[0] + 12, ya + 8), (b_[0] - 12, ya + 8), (b_[0] - 16, ya + 56), ((a[0] + b_[0]) / 2, ya + 64), (a[0] + 16, ya + 56)]]),
          (0, 0, 0, 0), lw=2.0, oc=(255, 220, 90), line_only=True)
    c.text((a[0] + b_[0]) / 2, ya + 34, "SCIENCE HALL", 34, (255, 220, 90))
    for xx in (a[0] + 34, b_[0] - 34):
        c.ink(ell(xx, ya + 34, 10, 10), (255, 220, 90), lw=2.0)
        c.ink(ell(xx, ya + 34, 4, 4), (60, 60, 180), lw=0)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    stain(c, *P(480, 400), 50, (60, 20, 50), 0.2, 3, 5)
    stain(c, *P(1210, 400), 40, (60, 20, 50), 0.18, 2, 6)

    # floor clutter: a lost goggle strap, crumpled worksheet, a sunflower seed trail toward the vent
    for k in range(9):
        X, Z = 520 - k * 14 + rng.uniform(-6, 6), 30 + k * 26
        x_, y_ = P(X, 0, Z)
        kk = R.k(Z)
        c.ink(ell(x_, y_, 4 * kk, 2.4 * kk, rng.uniform(0, 180)), (60, 50, 60), lw=1.0 * kk, oc=INK, shade=0, hi=0.4, hw=1)
    x_, y_ = P(980, 0, 260)
    c.ink(blob([(x_ - 18, y_), (x_ - 14, y_ - 14), (x_ + 6, y_ - 18), (x_ + 20, y_ - 6), (x_ + 12, y_ + 6)], 1), (250, 248, 236),
          lw=2.2, shade=0.4)

    room_grade(c, lights=[(lamps[0][0][0], 640, 520, 0.4), (lamps[1][0][0], 640, 520, 0.42), (lamps[2][0][0], 640, 420, 0.25),
                          ((wx0 + wx1) / 2, (wy0 + wy1) / 2 + 40, 220, 0.3, (90, 255, 220)),
                          (110, 600, 260, 0.2, (140, 150, 255)), (1800, 520, 220, 0.2, (90, 255, 160))],
               ambient=0.92, vign=0.62, top_dark=0.45, bottom_dark=0.35)
    for (x, y), flick in lamps:
        c.glow2(x, y, 260, (255, 246, 210), 0.25 if flick else 0.5, sy=0.4)
        c.glow2(x, y, 120, (255, 255, 240), 0.3 if flick else 0.6, sy=0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 1890, 1110, 270, seed=17, flip=True)
        # a rolling cart with beaker silhouettes, bottom-left
        sub.ink(rect(-20, 1052, 330, 1072), FG, lw=0, shade=0.2, hi=0.2)
        for k, (x_, h_) in enumerate(((40, 70), (110, 50), (170, 80), (250, 60))):
            sub.ink(blob([(x_ - 22, 1054), (x_ - 26, 1054 - h_ * 0.5), (x_ - 8, 1054 - h_ * 0.7), (x_ - 8, 1054 - h_),
                          (x_ + 8, 1054 - h_), (x_ + 8, 1054 - h_ * 0.7), (x_ + 26, 1054 - h_ * 0.5), (x_ + 22, 1054)], 1),
                    mix(FG, (40, 70, 90), 0.4), lw=0, shade=0.2, hi=0.25, hw=6, ao=0)
        fg_cable(sub, [(500, 1100), (800, 1050), (1200, 1080), (1500, 1110)], 18)
        # a tall bin and a mop handle in the bottom-left corner (left of the walkable area)
        sub.ink(rrect(-60, 830, 40, 1120, 10), FG, lw=0, shade=0.2, hi=0.2, hw=6)
        sub.stroke([(60, 1100), (10, 760)], 12, FG, taper=(0, 0))
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_science_hall.png")


LAYOUT["science_hall"] = dict(
        walk_px=[(60, Y_TOP), (1860, Y_TOP), (1890, 880), (1840, Y_BOT), (80, Y_BOT), (30, 880)],
        hotspots={
            ("Campus", 0): dict(box=(40, 370, 215, 760), stand=(230, 820)),
            ("Notice board", 0): dict(box=(255, 345, 475, 515), stand=(365, 800)),
            ("Basement stairs", 0): dict(box=(490, 340, 665, 695), stand=(575, 800)),
            ("Air vent", 0): dict(box=(670, 600, 790, 685), stand=(730, 800)),
            ("Mr. Bones", 0): dict(box=(810, 390, 940, 705), stand=(870, 800)),
            ("Periodic table", 0): dict(box=(985, 290, 1235, 440), stand=(1110, 800)),
            ("Mr. Bones' coat", 0): dict(sprite="hs_mr_bones_coat", feet=(997, 580), stand=(995, 800)),
            ("Lab door", 0): dict(box=(1240, 395, 1410, 695), stand=(1325, 800)),
            ("Faculty lounge", 0): dict(box=(1450, 395, 1640, 695), stand=(1545, 800)),
            ("Roof stairs", 0): dict(box=(1705, 300, 1885, 760), stand=(1690, 820)),
        },
        entries={"from_campus": (240, 880), "from_lab": (1325, 840), "from_roof": (1680, 880),
                 "from_basement": (575, 840), "from_lounge": (1545, 840)})


# =========================================================================== 2. Lab 3B
def flask(c, x, y, h, liquid, kind="erlenmeyer", level=0.55, glow=0.0, label=None):
    """Glassware standing at (x, y) (bottom centre), h tall, with coloured liquid."""
    w = h * 0.62
    if kind == "erlenmeyer":
        pts = [(x - w * 0.5, y), (x + w * 0.5, y), (x + w * 0.14, y - h * 0.62), (x + w * 0.14, y - h), (x - w * 0.14, y - h),
               (x - w * 0.14, y - h * 0.62)]
    elif kind == "beaker":
        w = h * 0.7
        pts = [(x - w * 0.5, y), (x + w * 0.5, y), (x + w * 0.5, y - h), (x - w * 0.56, y - h - 4), (x - w * 0.5, y - h * 0.9)]
    elif kind == "round":
        pts = ell_pts(x, y - h * 0.32, h * 0.34, h * 0.32, 0, 30) + [(x - h * 0.08, y - h), (x + h * 0.08, y - h)]
        pts = ell_pts(x, y - h * 0.32, h * 0.34, h * 0.32, 0, 30, -60, 240) + [(x - h * 0.08, y - h), (x + h * 0.08, y - h)]
    else:   # test tube
        w = h * 0.22
        pts = [(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y - w / 2), (x, y), (x - w / 2, y - w / 2)]
    sh = Sh([pts])
    c.ink(sh, (210, 236, 250, 90), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0.3)
    ly = y - h * level
    c.ink(rect(x - h, ly, x + h, y + 2), liquid, lw=0, shade=0.35, sw=h * 0.2, hi=0.3, clip=sh, ao=0, wob=0)
    c.ink(ell(x, ly, w * 0.4, 2.5), hi_col(liquid, 0.4), lw=0, shade=0, hi=0, clip=sh, ao=0, wob=0)
    c.ink(sh, (0, 0, 0, 0), lw=2.4, line_only=True, wob=0.3)
    c.stroke([(x - w * 0.22, y - h * 0.1), (x - w * 0.1, y - h * 0.5)], 2.2, (255, 255, 255), opacity=0.55)
    if label:
        c.ink(rect(x - w * 0.3, y - h * 0.42, x + w * 0.3, y - h * 0.18), (250, 248, 236), lw=1.4, shade=0.1, clip=sh)
        c.text(x, y - h * 0.3, label, max(5, h * 0.09), (200, 30, 40), "Bold")
    if glow:
        c.glow2(x, y - h * 0.3, h * 1.6, liquid, glow)
        for k in range(3):
            c.ink(ell(x + (k - 1) * w * 0.12, y - h * (1.08 + k * 0.12), 2.5 + k, 2.5 + k), hi_col(liquid, 0.5), lw=1.2,
                  opacity=0.7)


def paint_lab():
    c, R, rng = std_room(320, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (214, 82, 150)
    TILE = (226, 236, 240)

    def ceil(sub):
        w, h = sub.w, sub.h
        sub.ink(rect(0, 0, w, h), (120, 110, 150), lw=0, shade=0, hi=0, ao=0, tex=0.25, wob=0)
        step = 96 * sub.density
        for x in np.arange(0, w, step):
            sub.stroke([(x, 0), (x, h)], 2.6, (100, 90, 128), taper=(0, 0))
        for y in np.arange(0, h, step * 0.8):
            sub.stroke([(0, y), (w, y)], 2.6, (100, 90, 128), taper=(0, 0))
        for _ in range(8):
            stain(sub, rng.uniform(0, w), rng.uniform(0, h), rng.uniform(30, 70), (120, 80, 40), 0.25, 0, rng.randint(0, 99))
        # the big vent's ceiling duct opening (scorch marks from an old experiment)
        sub.soft(ell(sub.ax(330), sub.by(140), 90 * sub.density, 50 * sub.density), (30, 10, 30), 0.45, 18)

    def wall_paint(sub, w, h, seed):
        grunge_wall(sub, w, h, WALL, seed=seed, chips=4, stains=4, floor_y=h)
        y0 = h * 0.55
        sub.ink(rect(-4, y0, w + 4, h), TILE, lw=0, shade=0, hi=0, ao=0, tex=0.1, wob=0)
        tw = 40 * getattr(sub, "density", 1.0)
        for yy in np.arange(y0, h, tw * 0.6):
            sub.stroke([(0, yy), (w, yy)], 1.6, (150, 170, 190), taper=(0, 0), opacity=0.8)
        for k, yy in enumerate(np.arange(y0, h, tw * 0.6)):
            for xx in np.arange((k % 2) * tw / 2, w, tw):
                sub.stroke([(xx, yy), (xx, yy + tw * 0.6)], 1.4, (150, 170, 190), taper=(0, 0), opacity=0.7)
        for _ in range(int(w / 100)):
            stain(sub, rng.uniform(0, w), rng.uniform(y0 + 10, h), rng.uniform(16, 40), (90, 110, 60), 0.14, rng.randint(0, 2),
                  rng.randint(0, 99))
        for _ in range(2):
            chip(sub, rng.uniform(0, w), rng.uniform(y0 + 30, h - 30), rng.uniform(16, 30), BRICK, MORTAR, TILE, seed=rng.randint(0, 99))
        sub.ink(rect(-4, y0 - 12, w + 4, y0 + 6), (40, 170, 170), lw=2.4, shade=0.4, hi=0.4)
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)
        skirting(sub, w, h, col=(40, 90, 110))

    def left(sub):
        wall_paint(sub, sub.w, sub.h, 41)
        x0, x1, y0, y1 = side_door(sub, 330, 160, 300, (190, 70, 60), window=True, seed=9, knob="R")
        sub.ink(rect(x0 - 26, y0 - 70, x1 + 26, y0 - 26), (40, 40, 80), lw=2.6, shade=0.3)
        sub.text((x0 + x1) / 2, y0 - 48, "< HALL", 18 * sub.density, (255, 230, 140))
        # THINK SAFETY poster further back
        poster(sub, sub.ax(80), sub.by(250), 110 * sub.density, 140 * sub.density, (255, 236, 120),
               lambda p, w_, h_: (p.text(w_ / 2, h_ * 0.2, "THINK", 15 * sub.density, (200, 40, 60)),
                                  p.text(w_ / 2, h_ * 0.4, "SAFETY!", 13 * sub.density, (40, 90, 200)),
                                  p.ink(ell(w_ / 2, h_ * 0.7, w_ * 0.22, h_ * 0.14), (255, 140, 40), lw=2),
                                  p.ink(ell(w_ / 2 - w_ * 0.1, h_ * 0.7, w_ * 0.08, h_ * 0.08), (150, 220, 255), lw=1.6),
                                  p.ink(ell(w_ / 2 + w_ * 0.1, h_ * 0.7, w_ * 0.08, h_ * 0.08), (150, 220, 255), lw=1.6)),
               angle=3, seed=14, peel="br")

    def right(sub):
        wall_paint(sub, sub.w, sub.h, 42)
        # eyewash station sign + a first aid box
        x0 = sub.ax(260)
        sub.ink(rect(x0, sub.by(250), x0 + 90 * sub.density, sub.by(170)), (250, 250, 250), lw=2.6, shade=0.3)
        sub.ink(rect(x0 + 34 * sub.density, sub.by(236), x0 + 56 * sub.density, sub.by(184)), (220, 40, 50), lw=0)
        sub.ink(rect(x0 + 19 * sub.density, sub.by(221), x0 + 71 * sub.density, sub.by(199)), (220, 40, 50), lw=0)

    def floor(sub):
        tiles(sub, (66, 160, 150), (230, 220, 196), 0, 0, sub.w, sub.h, size=60 * sub.density, seed=44, chipped=0.08)
        for _ in range(5):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(30, 70), (60, 90, 40), 0.12, 0, rng.randint(0, 99))
        # drain
        x, y = sub.ax(700), sub.by(380)
        sub.ink(ell(x, y, 30 * sub.density, 20 * sub.density), (110, 110, 130), lw=2.4, shade=0.4)
        for k in range(-2, 3):
            sub.stroke([(x + k * 9 * sub.density, y - 14 * sub.density), (x + k * 9 * sub.density, y + 14 * sub.density)], 2.0,
                       (40, 40, 60), taper=(0, 0))

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=320)

    def back(sub):
        wall_paint(sub, sub.w, sub.h, 43)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=43)
    R.ao(0.5)
    R.edges(w=4.0)

    # --- ceiling: fluorescent panels, duct, cables
    lamps = []
    for X0, flick in ((140, False), (560, True)):
        panel_light(c, R, X0, X0 + 220, 110, 210, cone=0.2, flicker=flick)
        lamps.append((R.pt(X0 + 110, Hb - 14, 160), flick))
    pipe(c, [P(0, Hb - 30, 20), P(Wb, Hb - 30, 20)], w=30, col=(170, 170, 190), brackets=[P(150, Hb - 30, 20), P(900, Hb - 30, 20)])
    cable(c, P(0, Hb, 260), P(700, Hb, 340), sag=60, w=7, col=(40, 30, 70))
    cable(c, P(800, Hb, 300), P(Wb, Hb, 220), sag=50, w=6, col=(40, 130, 130))
    hanging_cable(c, P(820, Hb, 280), 110, sway=12, w=6, col=(200, 60, 90), seed=6)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    stain(c, *P(380, 400), 46, (60, 20, 50), 0.2, 3, 5)


    # --- recycling bin stuffed with paper-towel tubes (X 0..62, Z 30..80)
    R.contact(0, 62, 30, 80, 0.5)
    f = R.ink_box(2, 62, 0, 100, 30, 80, (40, 120, 220), seed=3)
    tx, ty = f["front"][0]
    tw = f["front"][1][0] - tx
    for k, (dx, ang, col) in enumerate(((0.2, -12, (210, 160, 100)), (0.5, 8, (200, 150, 96)), (0.78, 20, (220, 172, 110)))):
        cx_, cy_ = tx + tw * dx, ty - 6
        tube = Sh([rot_pts([(cx_ - 7, cy_ - 34), (cx_ + 7, cy_ - 34), (cx_ + 7, cy_ + 6), (cx_ - 7, cy_ + 6)], ang, cx_, cy_)])
        c.ink(tube, col, lw=2.2, shade=0.4, hi=0.3)
        top = rot_pts([(cx_, cy_ - 34)], ang, cx_, cy_)[0]
        c.ink(ell(top[0], top[1], 7, 3, ang), (90, 60, 40), lw=1.6)
    fx, fy = f["front"][0]
    c.ink(ell(fx + tw / 2, fy + 40, 12, 12), (0, 0, 0, 0), lw=3.0, oc=(250, 250, 250), line_only=True)

    # --- the big vent, grate hanging open on one screw (X 90..220, Y 12..110)
    vx0, vy0 = P(90, 110)
    vx1, vy1 = P(220, 12)
    c.ink(rect(vx0 - 8, vy0 - 8, vx1 + 8, vy1 + 8), (190, 190, 204), lw=3.0, shade=0.35, hi=0.3)
    c.ink(rect(vx0, vy0, vx1, vy1), (24, 14, 34), lw=2.2)
    c.soft(rect(vx0 + 10, vy0 + 10, vx1 - 10, vy1 - 6), (60, 40, 80), 0.5, 10)
    for (ax_, ay_), (bx__, by__) in (((vx0, vy0), (vx0 + 22, vy0 + 18)), ((vx1, vy0), (vx1 - 22, vy0 + 18)),
                                     ((vx0, vy1), (vx0 + 22, vy1 - 14)), ((vx1, vy1), (vx1 - 22, vy1 - 14))):
        c.stroke([(ax_, ay_), (bx__, by__)], 2.0, (90, 80, 110), taper=(0, 0))
    c.ink(rect(vx0 + 22, vy0 + 18, vx1 - 22, vy1 - 14), (0, 0, 0, 0), lw=2.0, oc=(90, 80, 110), line_only=True)
    g = [(vx0 + 6, vy1 + 4), (vx1 - 20, vy1 + 30), (vx1 - 40, vy1 + 64), (vx0 - 14, vy1 + 36)]
    c.ink(Sh([g]), (180, 180, 196), lw=2.6, shade=0.4, hi=0.3)
    for k in range(1, 6):
        a = (g[0][0] + (g[3][0] - g[0][0]) * k / 6, g[0][1] + (g[3][1] - g[0][1]) * k / 6)
        b_ = (g[1][0] + (g[2][0] - g[1][0]) * k / 6, g[1][1] + (g[2][1] - g[1][1]) * k / 6)
        c.stroke([a, b_], 2.0, (90, 90, 110), taper=(0, 0))
    cobweb(c, vx1, vy0, 30, "tr", opacity=0.45)
    # shelves of jars above (X 40..300)
    for k, Y in enumerate((300, 230)):
        sx0, sy_ = P(40 + k * 20, Y)
        sx1 = P(300 - k * 10, Y)[0]
        shelf(c, sx0, sx1, sy_, 16, (140, 90, 70))
        x = sx0 + 12
        while x < sx1 - 26:
            jh = rng.uniform(26, 44)
            col = rng.choice([(140, 230, 120), (255, 120, 170), (120, 200, 255), (255, 210, 80), (190, 140, 255)])
            c.ink(rrect(x, sy_ - jh, x + 24, sy_, 4), (220, 236, 245, 120), lw=2.0, shade=0, hi=0, ao=0)
            c.ink(rrect(x + 2, sy_ - jh * 0.7, x + 22, sy_ - 2, 3), col, lw=0, shade=0.4, hi=0.3)
            c.ink(rect(x - 1, sy_ - jh - 6, x + 25, sy_ - jh), (60, 60, 80), lw=1.6)
            x += 30
    # --- chalkboard: DO HAMSTERS PREFER JAZZ? (X 430..890, Y 200..380)
    cx0, cy0 = P(430, 380)
    cx1, cy1 = P(890, 200)
    c.ink(rect(cx0 - 14, cy0 - 14, cx1 + 14, cy1 + 14), (150, 96, 60), lw=3.0, shade=0.4, hi=0.35)
    c.ink(rect(cx0, cy0, cx1, cy1), (34, 70, 62), lw=2.4, shade=0.25, tex=0.3)
    chalk = (236, 240, 226)
    for _ in range(14):
        xx, yy = rng.uniform(cx0 + 10, cx1 - 30), rng.uniform(cy0 + 10, cy1 - 10)
        c.stroke([(xx, yy), (xx + rng.uniform(30, 90), yy + rng.uniform(-6, 6))], rng.uniform(6, 14), (90, 120, 110), opacity=0.25,
                 blur_px=3)
    c.text((cx0 + cx1) / 2, cy0 + 26, "DO HAMSTERS PREFER JAZZ?", 18, chalk, "Bold")
    gx, gy = cx0 + 40, cy1 - 24
    c.stroke([(gx, cy0 + 50), (gx, gy), (gx + 210, gy)], 2.4, chalk, taper=(0, 0))
    for k, (hgt, lab) in enumerate(((40, "POLKA"), (66, "METAL"), (108, "JAZZ"))):
        bx = gx + 24 + k * 64
        c.ink(rect(bx, gy - hgt, bx + 36, gy), (0, 0, 0, 0), lw=2.2, oc=chalk, line_only=True)
        c.text(bx + 18, gy + 11, lab, 7.5, chalk, "Bold")
    c.text(gx + 186, gy - 104, "+40%!", 11, (255, 230, 120), "Bold")
    c.text(cx1 - 92, cy0 + 70, "wheel speed", 10, chalk, "Bold")
    c.text(cx1 - 92, cy0 + 88, "= jazz²", 11, chalk, "Bold")
    c.text(cx1 - 92, cy0 + 116, "polka: filed", 9, chalk, "Bold")
    c.text(cx1 - 92, cy0 + 130, "a complaint", 9, chalk, "Bold")
    c.ink(rect(cx0 + 20, cy1 + 2, cx0 + 60, cy1 + 10), (250, 250, 240), lw=1.4)

    # --- the lab bench (X 440..880, Z 0..90, 90 tall) with beakers, the cage and the mascot cushion
    R.contact(440, 880, 0, 92, 0.55)
    R.ink_box(440, 880, 0, 82, 4, 88, (40, 120, 150), seed=7)
    for k in range(4):
        q = [P(452 + k * 107, 74, 88), P(540 + k * 107, 74, 88), P(540 + k * 107, 10, 88), P(452 + k * 107, 10, 88)]
        c.ink(Sh([q]), (50, 140, 172), lw=2.2, shade=0.3, hi=0.3)
        hx_, hy_ = P(496 + k * 107, 60, 88)
        c.ink(rrect(hx_ - 12, hy_ - 3, hx_ + 12, hy_ + 3, 2), (220, 220, 230), lw=1.6)
    R.ink_box(432, 888, 82, 92, 0, 94, (40, 40, 56), top=(64, 64, 84), seed=8)      # black epoxy top
    top_y = P(500, 92, 50)[1]
    # beakers (X 460..580): a glowing blue one marked NOT A DRINK
    flask(c, *P(480, 92, 40), 56, (110, 230, 140), "erlenmeyer", 0.45, glow=0.2)
    flask(c, *P(520, 92, 55), 74, (90, 170, 255), "beaker", 0.6, glow=0.35, label="NOT A DRINK")
    flask(c, *P(565, 92, 35), 50, (255, 110, 170), "round", 0.4, glow=0.2)
    rx_, ry_ = P(600, 92, 30)
    c.ink(rect(rx_ - 4, ry_ - 30, rx_ + 34, ry_), (0, 0, 0, 0), lw=0)
    # hamster cage (X 620..760): empty, door open, wheel
    kx0, ky0 = P(620, 200, 40)
    kx1, ky1 = P(760, 92, 40)
    c.ink(rect(kx0, ky1 - 12, kx1, ky1), (230, 120, 60), lw=2.6, shade=0.4, hi=0.3)
    c.ink(rect(kx0 + 4, ky1 - 18, kx1 - 4, ky1 - 12), (240, 220, 160), lw=0)
    for xx in np.arange(kx0 + 6, kx1 - 2, 9):
        c.stroke([(xx, ky0 + 14), (xx, ky1 - 12)], 1.6, (210, 210, 220), taper=(0, 0))
    c.stroke(bez((kx0, ky0 + 16), ((kx0 + kx1) / 2, ky0 - 14), (kx1, ky0 + 16), 20), 2.6, (210, 210, 220), taper=(0, 0))
    c.stroke([(kx0, ky0 + 16), (kx0, ky1 - 12)], 2.6, (190, 190, 200), taper=(0, 0))
    c.stroke([(kx1, ky0 + 16), (kx1, ky1 - 12)], 2.6, (190, 190, 200), taper=(0, 0))
    wx_, wy_ = kx0 + (kx1 - kx0) * 0.35, ky1 - 44
    c.ink(ell(wx_, wy_, 26, 26), (0, 0, 0, 0), lw=3.4, oc=(80, 200, 220), line_only=True)
    for k in range(8):
        a = math.radians(k * 45)
        c.stroke([(wx_, wy_), (wx_ + math.cos(a) * 24, wy_ + math.sin(a) * 24)], 1.4, (80, 200, 220), taper=(0, 0))
    dpts = [(kx1 - 6, ky0 + 40), (kx1 + 26, ky0 + 50), (kx1 + 26, ky1 - 26), (kx1 - 6, ky1 - 18)]
    c.ink(Sh([dpts]), (0, 0, 0, 0), lw=2.4, oc=(200, 200, 214), line_only=True)
    c.ink(ell(kx1 - 30, ky1 - 22, 12, 5), (120, 80, 40), lw=1.6)        # empty food dish
    c.ink(rect(kx0 + 8, ky0 + 28, kx0 + 54, ky0 + 46), (250, 248, 236), lw=1.4, shade=0.1)
    c.text(kx0 + 31, ky0 + 37, "NIBBLES", 6, (90, 50, 30), "Bold")
    # mascot cushion (Nibbles' sprite sits here) at X 790..860
    nx_, ny_ = P(825, 92, 40)
    c.ink(ell(nx_, ny_ - 6, 40, 10), (200, 40, 80), lw=2.4, shade=0.4, hi=0.3)
    c.ink(ell(nx_, ny_ - 10, 34, 7), (230, 70, 110), lw=0, shade=0.2, hi=0.3)
    for (tx_, ty_) in ((nx_ - 38, ny_ - 6), (nx_ + 38, ny_ - 6)):
        c.ink(ell(tx_, ty_, 5, 4), (255, 210, 80), lw=1.4)
    # bunsen burner + test tube rack near the cushion
    bx_, by_ = P(735, 92, 70)
    c.ink(rect(bx_ - 10, by_ - 8, bx_ + 10, by_), (60, 60, 70), lw=2.0)
    c.ink(rect(bx_ - 4, by_ - 40, bx_ + 4, by_ - 8), (170, 170, 186), lw=1.8, shade=0.3)
    c.ink(blob([(bx_ - 5, by_ - 42), (bx_, by_ - 64), (bx_ + 5, by_ - 42)], 1), (110, 170, 255), lw=1.2, opacity=0.8)
    c.glow2(bx_, by_ - 50, 40, (120, 170, 255), 0.4)
    rk = R.box(448, 500, 92, 104, 66, 86)
    for k in range(4):
        flask(c, *P(455 + k * 12, 92, 80), 34, [(255, 220, 80), (140, 230, 120), (255, 120, 170), (120, 200, 255)][k], "tube", 0.5)
    c.ink(Sh([rk["front"]]), (200, 150, 90), lw=2.0, shade=0.3, hi=0.3)

    # --- Dare Round banner for the TV show, hung across the right side (Z 200)
    a, b_ = P(950, Hb, 200), P(1230, Hb, 200)
    ya = P(950, Hb - 50, 200)[1]
    for xx in (a[0] + 26, b_[0] - 26):
        c.stroke([(xx, a[1]), (xx, ya)], 2.4, (60, 60, 80), taper=(0, 0))
    ban = Sh([[(a[0], ya), (b_[0], ya), (b_[0] + 4, ya + 118), (a[0] - 4, ya + 118)]])
    c.ink(ban, (230, 40, 130), lw=3.0, shade=0.45, sw=26, hi=0.35, rim=0.2)
    c.ink(Sh([[(a[0] + 10, ya + 8), (b_[0] - 10, ya + 8), (b_[0] - 8, ya + 110), (a[0] + 8, ya + 110)]]), (0, 0, 0, 0), lw=2.0,
          oc=(255, 220, 120), line_only=True)
    mx = (a[0] + b_[0]) / 2
    c.text(mx, ya + 30, "SPEED DATERS LIVE", 16, (255, 240, 160))
    c.text(mx, ya + 74, "DARE ROUND", 42, (255, 255, 255), "Italic", stroke=3, sc=(120, 10, 80))
    for k in range(12):
        a_ = k / 12 * 2 * math.pi
        sx_ = mx + math.cos(a_) * (b_[0] - a[0]) * 0.52
        sy_ = ya + 60 + math.sin(a_) * 72
        c.ink(ell(sx_, sy_, 5, 5), (255, 236, 140), lw=1.4)
        c.glow2(sx_, sy_, 18, (255, 236, 140), 0.4)
    # stage spotlights on a little truss for the show
    c.stroke([P(900, Hb - 12, 120), P(1260, Hb - 12, 120)], 8, INK, taper=(0, 0))
    c.stroke([P(900, Hb - 12, 120), P(1260, Hb - 12, 120)], 4, (150, 150, 170), taper=(0, 0))
    spots = []
    for X, col in ((960, (255, 90, 190)), (1200, (90, 220, 255))):
        sx_, sy_ = P(X, Hb - 12, 120)
        c.ink(Sh([rot_pts([(sx_ - 14, sy_), (sx_ + 14, sy_), (sx_ + 18, sy_ + 34), (sx_ - 18, sy_ + 34)], 20 if X < 1000 else -20, sx_, sy_)]),
              (50, 50, 64), lw=2.4, shade=0.3)
        spots.append((sx_, sy_ + 30, col))

    # --- safety shower standing in the right corner (X 1180..1240, Z 80..160)
    R.contact(1170, 1250, 90, 170, 0.45)
    px_, py_ = P(1215, 0, 130)
    ptop = P(1215, 300, 130)
    c.stroke([(px_, py_), ptop], 12, INK, taper=(0, 0))
    c.stroke([(px_, py_), ptop], 7, (240, 210, 60), taper=(0, 0))
    hd = P(1150, 300, 130)
    c.stroke([ptop, hd], 10, INK, taper=(0, 0))
    c.stroke([ptop, hd], 6, (240, 210, 60), taper=(0, 0))
    c.ink(Sh([[(hd[0] - 30, hd[1] + 4), (hd[0] + 30, hd[1] + 4), (hd[0] + 20, hd[1] + 22), (hd[0] - 20, hd[1] + 22)]]), (240, 210, 60),
          lw=2.6, shade=0.4, hi=0.4)
    c.stroke([(hd[0] + 10, hd[1] + 6), (hd[0] + 14, hd[1] + 100)], 2.0, (60, 60, 70), taper=(0, 0))
    c.ink(Sh([[(hd[0] + 4, hd[1] + 100), (hd[0] + 24, hd[1] + 100), (hd[0] + 20, hd[1] + 118), (hd[0] + 8, hd[1] + 118)]]),
          (60, 200, 90), lw=2.0, shade=0.3)
    c.ink(ell(px_, py_ - 2, 26, 7), (200, 180, 60), lw=2.4, shade=0.3)
    sgx, sgy = P(1215, 200, 130)
    c.ink(rrect(sgx - 34, sgy - 30, sgx + 34, sgy + 22, 4), (40, 160, 90), lw=2.4, shade=0.3)
    c.text(sgx, sgy - 14, "SAFETY", 10, (255, 255, 240))
    c.text(sgx, sgy + 4, "SHOWER", 10, (255, 255, 240))
    for k in range(5):          # drips from the head
        c.ink(ell(hd[0] - 14 + k * 7, hd[1] + 34 + (k % 3) * 14, 2.2, 3.4), (150, 220, 255), lw=1.0)

    # floor: a few sunflower seeds and paper towels by the vent, cables to the stage lights
    for k in range(7):
        x_, y_ = P(200 + k * 26 + rng.uniform(-8, 8), 0, 40 + k * 18)
        c.ink(ell(x_, y_, 4, 2.4, rng.uniform(0, 180)), (60, 50, 60), lw=1.0, shade=0, hi=0.4, hw=1)
    # yellow / black hazard stripes on the floor in front of the shower
    hz = [P(1120, 0, 200), P(1260, 0, 200), P(1260, 0, 260), P(1120, 0, 260)]
    c.ink(Sh([hz]), (240, 200, 50), lw=2.4, shade=0.1, hi=0, tex=0.3)
    clip_draw(c, Sh([hz]), lambda t: [t.stroke([(x, 700), (x + 60, 900)], 12, (40, 30, 40), taper=(0, 0)) for x in np.arange(1400, 1900, 34)])
    c.ink(Sh([hz]), (0, 0, 0, 0), lw=2.4, line_only=True)

    room_grade(c, lights=[(lamps[0][0][0], 640, 520, 0.42), (lamps[1][0][0], 640, 420, 0.25),
                          (P(520, 120, 55)[0], P(520, 120, 55)[1], 240, 0.35, (90, 170, 255)),
                          (cx1 - 30, cy0 + 40, 260, 0.35),
                          (spots[0][0], 700, 420, 0.35, (255, 90, 190)), (spots[1][0], 700, 380, 0.3, (90, 220, 255))],
               ambient=0.92, vign=0.62, top_dark=0.45, bottom_dark=0.35)
    for (x, y), flick in lamps:
        c.glow2(x, y, 260, (255, 246, 210), 0.25 if flick else 0.5, sy=0.4)
        c.glow2(x, y, 120, (255, 255, 240), 0.3 if flick else 0.6, sy=0.35)
    for sx_, sy_, col in spots:
        c.light_cone((sx_, sy_), (sx_ - 260, 940), (sx_ + 160, 940), col, 0.22, 40)
        c.glow2(sx_, sy_, 60, col, 0.6)
    c.painterly(0.05)

    def fg(sub):
        # lab stool silhouette, bottom-left, and a tangle of hoses bottom-right
        sub.ink(ell(60, 1000, 150, 34), FG, lw=0, shade=0.2, hi=0.2)
        for x_ in (-40, 150):
            sub.ink(rect(x_ - 9, 1000, x_ + 9, 1100), FG, lw=0)
        fg_bottles(sub, 1700, 1100, 4, 0.6, seed=21)
        fg_cable(sub, [(400, 1100), (800, 1060), (1250, 1090), (1600, 1060), (1950, 1080)], 18)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_lab.png")


LAYOUT["lab"] = dict(
        walk_px=[(180, Y_TOP), (1750, Y_TOP), (1830, 880), (1790, Y_BOT), (130, Y_BOT), (70, 880)],
        hotspots={
            ("Hallway", 0): dict(box=(20, 360, 215, 815), stand=(230, 830)),
            ("Recycling bin", 0): dict(box=(270, 580, 380, 715), stand=(330, 800)),
            ("Big vent", 0): dict(box=(405, 570, 560, 740), stand=(480, 800)),
            ("Dr. Mina Volt", 0): dict(npc="hs_dr_mina_volt", feet=(650, NPC_FEET_Y), stand=(840, 935)),
            ("Beakers", 0): dict(box=(780, 520, 940, 615), stand=(860, 800)),
            ("Chalkboard", 0): dict(box=(755, 305, 1225, 495), stand=(990, 800)),
            ("Hamster cage", 0): dict(box=(945, 495, 1110, 615), stand=(1030, 800)),
            ("Professor Nibbles", 0): dict(sprite="hs_professor_nibbles", feet=(1170, 612), stand=(1170, 800)),
            ("Roxy Vale", 0): dict(npc="hs_roxy_vale", feet=(1300, NPC_FEET_Y), stand=(1480, 935)),
            ("Dare Round banner", 0): dict(box=(1360, 250, 1710, 395), stand=(1530, 800)),
            ("Shower puddle", 0): dict(sprite="hs_shower_puddle", feet=(1655, 905), stand=(1500, 900)),
            ("Dot Pruitt", 0): dict(npc="hs_dot_pruitt", feet=(1560, NPC_FEET_Y), stand=(1750, 935)),
            ("Safety shower", 0): dict(box=(1530, 380, 1690, 770), stand=(1650, 830)),
        },
        entries={"from_hall": (240, 880)})


# =========================================================================== 3. Rooftop
def protest_sign(c, x, y, w, h, board, text_lines, tc, angle=0, stick=True, seed=0):
    """Hand-lettered cardboard sign; (x, y) = bottom of the stick (or board bottom)."""
    rng = random.Random(seed)
    sub = Canvas2(int(w + 40), int(h + (90 if stick else 0) + 40), lw=3.0, seed=seed)
    bx0, by0 = 20, 20
    if stick:
        sub.ink(rect(bx0 + w / 2 - 6, by0 + h - 10, bx0 + w / 2 + 6, by0 + h + 88), (170, 120, 70), lw=2.4, shade=0.4, hi=0.3)
    sub.ink(wonky(bx0, by0, bx0 + w, by0 + h, 3, rng), board, lw=3.0, shade=0.3, sw=12, hi=0.25, tex=0.2)
    n = len(text_lines)
    for i, ln in enumerate(text_lines):
        size = min(h * 0.56 / n, w * 0.84 / (len(ln) * 0.7))
        sub.text(bx0 + w / 2 + rng.uniform(-2, 2), by0 + h * (i + 0.6) / (n + 0.2), ln, size, tc)
    im = sub.img.rotate(angle, resample=Image.BICUBIC, expand=True)
    c.img.alpha_composite(im, (int(x * S - im.width / 2), int(y * S - im.height + 10 * S)))


def paint_rooftop():
    c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(0.4, -0.9), lw=3.4, seed=330)
    R = Room(c, (960, vp_for_walk(Y_TOP, Y_BOT)), (-400, 200, 2320, 690), fc=1000)
    rng = random.Random(330)
    P = R.pt
    HOR = 690

    # ---------------- night sky
    c.ink(rect(-10, -10, W_BG + 10, HOR + 10), ("vy", -10, HOR, (26, 16, 70), (196, 70, 140)), lw=0, shade=0, hi=0, ao=0, tex=0.06, wob=0)
    c.soft(rect(-10, 420, W_BG + 10, HOR), (255, 120, 150), 0.35, 60)
    for _ in range(220):
        sx, sy = rng.uniform(0, W_BG), rng.uniform(0, 380)
        r = rng.choice([0.9, 1.2, 1.8, 2.4])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=rng.uniform(0.4, 1))
    mx, my = 520, 150
    c.glow2(mx, my, 320, (220, 210, 255), 0.45)
    c.ink(ell(mx, my, 62, 62), (250, 244, 226), lw=0, shade=0.3, sw=16, scol=(220, 200, 220), hi=0, tex=0.12)
    for (cx_, cy_, rr) in ((500, 136, 10), (540, 170, 7), (556, 128, 5)):
        c.ink(ell(cx_, cy_, rr, rr * 0.8), (226, 214, 222), lw=0, shade=0, hi=0, ao=0, opacity=0.7)
    for (cx_, cy_, w) in ((230, 250, 360), (860, 110, 300), (1400, 210, 460), (1820, 120, 260)):
        cl = blob([(cx_ - w / 2, cy_), (cx_ - w * 0.32, cy_ - 26), (cx_ - w * 0.08, cy_ - 40), (cx_ + w * 0.18, cy_ - 30), (cx_ + w / 2, cy_ - 4),
                   (cx_ + w * 0.3, cy_ + 12), (cx_ - w * 0.3, cy_ + 12)], 2)
        c.ink(cl, (120, 70, 150), lw=0, shade=0.3, sw=14, scol=(70, 40, 110), hi=0.4, hw=6, hcol=(255, 180, 210), tex=0.1, opacity=0.8)

    # ---------------- skyline: campus on the left (dome + clock tower), downtown neon on the right
    def skyline(x0, x1, base, hmin, hmax, col, lit, seed):
        r_ = random.Random(seed)
        x = x0
        while x < x1:
            bw = r_.uniform(50, 120)
            bt = base - r_.uniform(hmin, hmax)
            c.ink(rect(x, bt, x + bw, base + 10), col, lw=2.0, oc=mix(col, INK, 0.5), shade=0.15, hi=0, ao=0, tex=0.05)
            for wy in np.arange(bt + 10, base - 6, 16):
                for wx in np.arange(x + 8, x + bw - 10, 14):
                    if r_.random() < lit:
                        c.ink(rect(wx, wy, wx + 6, wy + 8), r_.choice([(255, 206, 110), (255, 230, 160), (140, 220, 255)]), lw=0,
                              shade=0, hi=0, ao=0)
            x += bw + r_.uniform(-6, 10)
    skyline(-20, 2000, 600, 20, 70, (74, 40, 104), 0.15, 3)
    # campus: dome + clock tower on the left
    c.ink(rect(140, 470, 420, 600), (90, 56, 120), lw=2.4, shade=0.2, hi=0.1)
    c.ink(Sh([ell_pts(280, 470, 110, 90, 0, 30, 180, 360)]), (100, 130, 150), lw=2.6, shade=0.4, hi=0.3)
    c.stroke([(280, 380), (280, 340)], 4, INK, taper=(0, 0))
    for k in range(5):
        c.ink(rect(160 + k * 52, 500, 180 + k * 52, 540), (255, 206, 110), lw=1.4, shade=0, hi=0)
    c.ink(rect(470, 380, 540, 600), (100, 60, 120), lw=2.4, shade=0.2)
    c.ink(Sh([[(462, 382), (548, 382), (505, 320)]]), (80, 50, 100), lw=2.4)
    c.ink(ell(505, 420, 24, 24), (255, 240, 190), lw=2.2)
    c.stroke([(505, 420), (505, 404)], 2.4, INK, taper=(0, 0))
    c.stroke([(505, 420), (517, 424)], 2.0, INK, taper=(0, 0))
    c.glow2(505, 420, 60, (255, 230, 160), 0.4)
    # downtown: taller towers, neon
    skyline(1000, 1960, 600, 80, 230, (66, 36, 100), 0.35, 5)
    c.ink(rect(1520, 300, 1600, 600), (60, 34, 96), lw=2.4, shade=0.2)
    c.stroke([(1560, 300), (1560, 240)], 4, INK, taper=(0, 0))
    c.ink(ell(1560, 238, 5, 5), (255, 60, 80), lw=1.2)
    c.glow2(1560, 238, 30, (255, 60, 80), 0.6)
    c.ink(rrect(1200, 340, 1420, 382, 6), (40, 20, 60), lw=2.4)
    c.stroke([(1230, 382), (1230, 420)], 3, INK, taper=(0, 0))
    c.stroke([(1390, 382), (1390, 420)], 3, INK, taper=(0, 0))
    c.text(1310, 361, "DOWNTOWN", 24, (255, 120, 210))
    c.glow2(1310, 361, 170, (255, 90, 200), 0.45, sy=0.4)
    # the quad's stage lights in the distance
    for k in range(3):
        c.light_cone((760 + k * 60, 560), (700 + k * 60, 300), (740 + k * 60, 300), (255, 220, 160), 0.12, 10)

    # ---------------- roof floor: tar with gravel, seams, puddles
    def floor(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (78, 66, 96), lw=0, shade=0, hi=0, ao=0, tex=0.35, wob=0)
        r_ = random.Random(7)
        for _ in range(int(sub.w * sub.h / 700)):
            x, y = r_.uniform(0, sub.w), r_.uniform(0, sub.h)
            col = r_.choice([(120, 110, 140), (60, 50, 74), (150, 130, 150)])
            sub.ink(ell(x, y, r_.uniform(1.5, 3.5), r_.uniform(1.2, 2.6)), col, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0,
                    opacity=0.7)
        for y in np.arange(120, sub.h, 260 * sub.density):
            sub.stroke([(0, y), (sub.w, y + r_.uniform(-6, 6))], 3.0, (40, 30, 54), taper=(0, 0), opacity=0.6)
        for x in np.arange(40, sub.w, 300 * sub.density):
            sub.stroke([(x, 0), (x + r_.uniform(-8, 8), sub.h)], 3.0, (40, 30, 54), taper=(0, 0), opacity=0.5)
        for _ in range(10):
            stain(sub, r_.uniform(0, sub.w), r_.uniform(0, sub.h), r_.uniform(40, 100), (30, 20, 40), 0.2, 0, r_.randint(0, 99))
        # tar patches
        for _ in range(8):
            x, y = r_.uniform(0, sub.w), r_.uniform(0, sub.h)
            sub.ink(blob([(x + math.cos(a) * r_.uniform(30, 70), y + math.sin(a) * r_.uniform(20, 40)) for a in np.linspace(0, 6.2, 8)], 2),
                    (52, 42, 66), lw=0, shade=0, hi=0.15, hw=4, ao=0, tex=0.3, opacity=0.8)
    R.paint_plane("floor", -900, 3600, 0, 900, floor, density=0.9, seed=4)
    # roof drain + vent caps scattered near the back
    for (X, Z) in ((1450, 150), (2350, 120)):
        x_, y_ = P(X, 0, Z)
        k = R.k(Z)
        c.ink(ell(x_, y_, 28 * k, 8 * k), (60, 56, 70), lw=2.4, shade=0.3)
        c.ink(ell(x_, y_ - 2, 20 * k, 5 * k), (30, 26, 40), lw=1.6)
    for X, Z in ((350, 200), (2500, 260)):
        x_, y_ = P(X, 0, Z)
        k = R.k(Z)
        c.ink(rect(x_ - 12 * k, y_ - 50 * k, x_ + 12 * k, y_), (150, 150, 170), lw=2.4, shade=0.45, hi=0.4)
        c.ink(Sh([[(x_ - 26 * k, y_ - 50 * k), (x_ + 26 * k, y_ - 50 * k), (x_, y_ - 74 * k)]]), (170, 170, 190), lw=2.4, shade=0.4)
    # puddles reflecting the moon / neon
    for (X, Z, rx, col) in ((900, 300, 90, (180, 170, 255)), (1950, 420, 120, (255, 120, 200)), (1300, 520, 70, (180, 170, 255))):
        x_, y_ = P(X, 0, Z)
        k = R.k(Z)
        c.ink(ell(x_, y_, rx * k, rx * k * 0.18), mix((70, 60, 100), col, 0.35), lw=1.6, oc=(50, 40, 70), shade=0, hi=0.4, hw=4,
              hcol=hi_col(col, 0.5))

    # ---------------- parapet (brick, plaster patches) with a teal coping, across the back
    def para(sub):
        grunge_wall(sub, sub.w, sub.h, (196, 70, 130), seed=33, chips=10, stains=6, cracks=4, floor_y=sub.h, top_dark=False)
        r_ = random.Random(9)
        for _ in range(26):
            chip(sub, r_.uniform(0, sub.w), r_.uniform(10, sub.h - 10), r_.uniform(20, 50), BRICK, MORTAR, (196, 70, 130),
                 seed=r_.randint(0, 999))
    R.paint_plane("back", -400, 3200, 0, 110, para, density=1.0, seed=12)
    R.ink_box(-420, 3240, 110, 124, -6, 14, (40, 150, 160), top=(90, 200, 200), seed=13)
    R.ao(0.0)
    c.soft(Sh([[P(-400, 0, 0), P(3200, 0, 0), P(3200, 0, 40), P(-400, 0, 40)]]), (24, 6, 34), 0.5, 12)

    # ---------------- water tower on the right (legs on the roof, X 1900..2160)
    tx0, tx1 = 1900, 2160
    Zt = 40
    legs_x = (tx0 + 20, tx1 - 20)
    for X in legs_x:
        for Z_ in (Zt - 10, Zt + 60):
            c.stroke([P(X, 0, Z_), P(X + (8 if X < 2000 else -8), 300, Z_)], 9, INK, taper=(0, 0))
            c.stroke([P(X, 0, Z_), P(X + (8 if X < 2000 else -8), 300, Z_)], 5, (120, 90, 110), taper=(0, 0))
    for Y in (100, 200):
        c.stroke([P(legs_x[0] + 4, Y, Zt + 60), P(legs_x[1] - 4, Y + 80, Zt + 60)], 3, (120, 90, 110), taper=(0, 0))
        c.stroke([P(legs_x[1] - 4, Y, Zt + 60), P(legs_x[0] + 4, Y + 80, Zt + 60)], 3, (120, 90, 110), taper=(0, 0))
    R.ink_box(tx0 - 10, tx1 + 10, 296, 306, Zt - 20, Zt + 80, (110, 80, 90), seed=14)
    # tank: wooden staves with iron bands, cone roof
    t0, t1 = P(tx0, 470, Zt + 60), P(tx1, 306, Zt + 60)
    tank = Sh([[t0, (t1[0], t0[1]), t1, (t0[0], t1[1])]])
    c.ink(tank, (176, 96, 80), lw=3.2, shade=0.55, sw=60, hi=0.35, rim=0.2, tex=0.2)
    for xx in np.arange(t0[0] + 18, t1[0] - 4, 20):
        c.stroke([(xx, t0[1] + 4), (xx, t1[1] - 4)], 1.6, (120, 60, 60), taper=(0, 0), opacity=0.7)
    for yy in (t0[1] + 30, (t0[1] + t1[1]) / 2, t1[1] - 26):
        c.stroke([(t0[0] - 2, yy), (t1[0] + 2, yy)], 5, INK, taper=(0, 0))
        c.stroke([(t0[0] - 2, yy - 1), (t1[0] + 2, yy - 1)], 2.4, (150, 140, 160), taper=(0, 0))
    roof = Sh([[(t0[0] - 18, t0[1] + 6), (t1[0] + 18, t0[1] + 6), ((t0[0] + t1[0]) / 2, t0[1] - 80)]])
    c.ink(roof, (120, 70, 90), lw=3.2, shade=0.5, sw=30, hi=0.4, tex=0.15)
    c.ink(ell((t0[0] + t1[0]) / 2, t0[1] - 82, 8, 8), (240, 200, 90), lw=2.0)
    c.text((t0[0] + t1[0]) / 2 - 6, (t0[1] + t1[1]) / 2 - 22, "DEX WAS", 22, (255, 250, 230), "Black", angle=3)
    c.text((t0[0] + t1[0]) / 2 + 4, (t0[1] + t1[1]) / 2 + 10, "HERE", 26, (255, 250, 230), "Black", angle=3)
    c.ink(ell((t0[0] + t1[0]) / 2 + 74, (t0[1] + t1[1]) / 2 + 12, 16, 16), (0, 0, 0, 0), lw=3.0, oc=(255, 90, 170), line_only=True)
    # a ladder up the leg
    lxa = P(legs_x[0] - 26, 0, Zt + 66)
    lxb = P(legs_x[0] - 26, 300, Zt + 66)
    for dx in (0, 26):
        c.stroke([(lxa[0] + dx, lxa[1]), (lxb[0] + dx, lxb[1])], 3.4, INK, taper=(0, 0))
    for k in range(10):
        yy = lxa[1] + (lxb[1] - lxa[1]) * (k + 0.5) / 10
        c.stroke([(lxa[0], yy), (lxa[0] + 26, yy)], 2.6, INK, taper=(0, 0))

    # ---------------- coin binoculars at the campus view (X 1590, Z 40)
    bx_, by_ = P(1590, 0, 40)
    k = R.k(40)
    c.ink(rect(bx_ - 8 * k, by_ - 130 * k, bx_ + 8 * k, by_), (60, 150, 160), lw=2.6, shade=0.4, hi=0.3)
    c.ink(ell(bx_, by_, 30 * k, 8 * k), (50, 120, 130), lw=2.4, shade=0.3)
    hx_, hy_ = bx_, by_ - 150 * k
    c.ink(rrect(hx_ - 34 * k, hy_ - 22 * k, hx_ + 34 * k, hy_ + 22 * k, 10), (70, 180, 190), lw=2.8, shade=0.45, hi=0.4)
    for dx in (-22, 22):
        c.ink(ell(hx_ + dx * k + 26 * k, hy_ - 4 * k, 11 * k, 13 * k), (40, 40, 60), lw=2.4, shade=0.2, hi=0.5, hw=3)
    c.ink(rect(hx_ - 12 * k, hy_ + 6 * k, hx_ + 4 * k, hy_ + 14 * k), (240, 200, 90), lw=1.4)

    # ---------------- bird feeder on a pole (X 1300, Z 60): a little house with a red roof
    fx_, fy_ = P(1300, 0, 60)
    ftop = P(1300, 214, 60)
    R.contact(1280, 1320, 50, 70, 0.4)
    c.stroke([(fx_, fy_), ftop], 11, INK, taper=(0, 0))
    c.stroke([(fx_, fy_), ftop], 6, (150, 110, 80), taper=(0, 0))
    c.ink(ell(fx_, fy_, 24, 6), (100, 80, 70), lw=2.2)
    hw = 46
    c.ink(rect(ftop[0] - hw, ftop[1] - 8, ftop[0] + hw, ftop[1] + 6), (170, 120, 80), lw=2.6, shade=0.3, hi=0.3)   # tray
    c.ink(rect(ftop[0] - hw * 0.66, ftop[1] - 60, ftop[0] + hw * 0.66, ftop[1] - 8), (230, 210, 170), lw=2.6, shade=0.4, hi=0.3)
    c.ink(Sh([[(ftop[0] - hw * 0.66 - 10, ftop[1] - 60), (ftop[0] + hw * 0.66 + 10, ftop[1] - 60), (ftop[0], ftop[1] - 98)]]),
          (220, 60, 70), lw=2.8, shade=0.45, hi=0.35)
    for k in range(9):
        c.ink(ell(ftop[0] - 36 + k * 9 + rng.uniform(-2, 2), ftop[1] - 9 + rng.uniform(-2, 1), 3.2, 2.2), (90, 70, 60), lw=0.9)
    c.ink(rect(ftop[0] - 14, ftop[1] - 48, ftop[0] + 14, ftop[1] - 24), (60, 40, 50), lw=1.6)
    c.text(ftop[0], ftop[1] - 18, "FREE", 7, (60, 40, 60), "Bold")

    # ---------------- protest signs leaning on the parapet (X 770..1130)
    protest_sign(c, *P(955, 0, 8), 124, 86, (255, 170, 210), ["HAMSTER", "RIGHTS"], (60, 40, 120), angle=-5, seed=2)
    protest_sign(c, *P(830, 0, 16), 112, 80, (240, 220, 160), ["FREE", "NIBBLES"], (200, 40, 60), angle=7, seed=1)
    protest_sign(c, *P(1075, 0, 24), 96, 70, (160, 220, 255), ["WHEELS", "NOT", "DEALS"], (40, 40, 80), angle=10, seed=3)
    # a megaphone battery box + a thermos by the signs
    R.ink_box(1150, 1210, 0, 34, 30, 74, (220, 90, 60), seed=5)
    lx_, ly_ = P(1180, 34, 52)
    c.ink(rect(lx_ - 9, ly_ - 6, lx_ + 9, ly_), (40, 40, 50), lw=2.0)
    c.ink(rrect(lx_ - 8, ly_ - 34, lx_ + 8, ly_ - 6, 4), (255, 226, 140), lw=2.2, shade=0.2)
    c.ink(rect(lx_ - 10, ly_ - 40, lx_ + 10, ly_ - 33), (40, 40, 50), lw=2.0)
    c.stroke(bez((lx_ - 8, ly_ - 40), (lx_, ly_ - 56), (lx_ + 8, ly_ - 40), 10), 2.0, INK, taper=(0, 0))
    lantern_xy = (lx_, ly_ - 20)
    # Sky's rolled-up sleeping bag and a thermos
    sbx, sby = P(1340, 0, 60)
    c.ink(rrect(sbx - 40, sby - 34, sbx + 40, sby, 16), (60, 150, 200), lw=2.6, shade=0.5, sw=12, hi=0.35)
    c.ink(ell(sbx + 40, sby - 17, 8, 17), (40, 110, 160), lw=2.4, shade=0.3)
    c.stroke([(sbx - 10, sby - 34), (sbx - 10, sby)], 3, (240, 200, 90), taper=(0, 0))
    c.stroke([(sbx + 14, sby - 34), (sbx + 14, sby)], 3, (240, 200, 90), taper=(0, 0))

    # ---------------- stairwell hut on the left: block walls, door, caged bulb, STAIRS sign
    hx0, hx1, hz0, hz1, hh = 470, 726, -40, 120, 330
    R.contact(hx0, hx1, hz0, hz1, 0.5)
    f = R.box(hx0, hx1, 0, hh, hz0, hz1)

    def hut_face(quad, base, door=False):
        q = quad
        c.ink(Sh([q]), base, lw=3.4, shade=0.35, sw=30, hi=0.2, tex=0.18)
        clip = Sh([q])
        x0_, x1_ = min(p[0] for p in q), max(p[0] for p in q)
        y0_, y1_ = min(p[1] for p in q), max(p[1] for p in q)
        def blocks(t):
            for k, yy in enumerate(np.arange(y0_, y1_, 26)):
                t.stroke([(x0_, yy), (x1_, yy)], 1.6, shade_col(base, 0.7), taper=(0, 0), opacity=0.7)
                for xx in np.arange(x0_ + (k % 2) * 30, x1_, 60):
                    t.stroke([(xx, yy), (xx, yy + 26)], 1.4, shade_col(base, 0.7), taper=(0, 0), opacity=0.6)
        clip_draw(c, clip, blocks)
    hut_face(f["right"], shade_col((150, 90, 170), 0.8))
    hut_face(f["front"], (150, 90, 170))
    R.ink_box(hx0 - 12, hx1 + 12, hh, hh + 14, hz0 - 12, hz1 + 12, (40, 150, 160), seed=15)
    d0 = P(530, 250, hz1)
    d1 = P(680, 0, hz1)
    flat_door(c, d0[0], d0[1], d1[0], d1[1], (40, 150, 150), frame=(200, 196, 210), knob="R", window=True, seed=7)
    c.ink(rrect((d0[0] + d1[0]) / 2 - 56, d0[1] - 58, (d0[0] + d1[0]) / 2 + 56, d0[1] - 24, 5), (40, 40, 80), lw=2.6)
    c.text((d0[0] + d1[0]) / 2, d0[1] - 41, "STAIRS", 16, (255, 230, 140))
    bulb_xy = ((d0[0] + d1[0]) / 2, d0[1] - 82)
    caged_light(c, *bulb_xy, 11, strength=0.55, cone_to=780)
    # stickers + a sticker-bombed vent pipe on the hut roof
    pipe(c, [P(520, hh + 14, 20), P(520, hh + 80, 20), P(560, hh + 100, 20)], w=18, col=(150, 150, 170))
    for k, col in enumerate(((255, 90, 170), (90, 230, 210), (255, 220, 90))):
        sx_, sy_ = P(700 - k * 30, 120 + k * 40, hz1)
        c.ink(Sh([rot_pts([(sx_ - 12, sy_ - 9), (sx_ + 12, sy_ - 9), (sx_ + 12, sy_ + 9), (sx_ - 12, sy_ + 9)], k * 15 - 10, sx_, sy_)]), col,
              lw=1.6, shade=0.2)

    # ---------------- string lights from the hut to the water tower
    string_lights2(c, [P(726, hh, hz1), P(1300, 300, 60), P(1900, 330, Zt + 60)], sag=50, seed=9)
    # an antenna on the parapet
    ax_, ay_ = P(1150, 124, 4)
    c.stroke([(ax_, ay_), (ax_, ay_ - 150)], 4, INK, taper=(0, 0))
    for k in range(4):
        c.stroke([(ax_ - 40 + k * 6, ay_ - 140 + k * 26), (ax_ + 40 - k * 6, ay_ - 140 + k * 26)], 3, INK, taper=(0, 0))

    room_grade(c, lights=[(bulb_xy[0], bulb_xy[1] + 80, 360, 0.5), (1310, 500, 520, 0.25, (255, 110, 200)),
                          (lantern_xy[0], lantern_xy[1] + 40, 260, 0.45),
                          (mx, my + 300, 700, 0.15, (180, 170, 255)), (1300, 520, 300, 0.2)],
               ambient=0.92, vign=0.55, top_dark=0.2, bottom_dark=0.4, shadow_tint=(80, 40, 140))
    c.glow2(*bulb_xy, 120, GLOW, 0.5)
    c.glow2(*lantern_xy, 90, GLOW, 0.55)
    floor_pool(c, lantern_xy[0], lantern_xy[1] + 70, 160, 30, GLOW, 0.25)
    c.painterly(0.05)

    def fg(sub):
        # rooftop vent stack + a coil of cable bottom-left, an old chair bottom-right
        sub.ink(rrect(-30, 800, 46, 1120, 14), FG, lw=0, shade=0.2, hi=0.25, hw=6)
        sub.ink(ell(8, 790, 62, 22), FG, lw=0, shade=0.2, hi=0.2)
        sub.ink(ell(8, 770, 40, 26), FG, lw=0)
        fg_cable(sub, [(200, 1100), (420, 1050), (700, 1090), (1000, 1060), (1300, 1100)], 16)
        fg_plant(sub, 1860, 1110, 280, seed=23, flip=True)
        sub.ink(rrect(1700, 1040, 1960, 1120, 12), FG, lw=0)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_rooftop.png")


LAYOUT["rooftop"] = dict(
        walk_px=[(60, Y_TOP), (1860, Y_TOP), (1880, 880), (1840, Y_BOT), (100, Y_BOT), (90, 880)],
        hotspots={
            ("Stairwell door", 0): dict(box=(30, 430, 210, 730), stand=(230, 800)),
            ("Protest signs", 0): dict(box=(370, 490, 715, 690), stand=(520, 800)),
            ("Sky Rivera", 0): dict(npc="hs_sky_rivera", feet=(800, NPC_FEET_Y), stand=(990, 935)),
            ("Bird feeder", 0): dict(box=(840, 455, 960, 730), stand=(900, 800)),
            ("Pigeon", 0): dict(sprite="hs_pigeon", feet=(905, 468), stand=(900, 800)),
            ("Campus view", 0): dict(box=(1000, 380, 1450, 690), stand=(1200, 800)),
            ("Water tower", 0): dict(box=(1490, 140, 1830, 730), stand=(1660, 800)),
        },
        entries={"from_stairs": (240, 880)})


# =========================================================================== 4. Science basement
def block_wall(sub, w, h, base, seed=0, stripe=(240, 200, 60)):
    """Painted cinder-block wall (flat space): blocks, grime, chips, a safety stripe."""
    rng = random.Random(seed)
    plaster_wall(sub, hi_col(base, 0.05), shade_col(base, 0.85), seed=seed, w=w, h=h, streaks=False)
    d = getattr(sub, "density", 1.0)
    bh, bw = 40 * d, 80 * d
    for k, yy in enumerate(np.arange(h, -bh, -bh)):
        sub.stroke([(0, yy), (w, yy)], 2.0, shade_col(base, 0.62), taper=(0, 0), opacity=0.8)
        for xx in np.arange(-(k % 2) * bw / 2, w, bw):
            sub.stroke([(xx, yy - bh), (xx, yy)], 1.8, shade_col(base, 0.62), taper=(0, 0), opacity=0.7)
            if rng.random() < 0.12:
                sub.ink(rect(xx + 3, yy - bh + 3, xx + bw - 3, yy - 3), hi_col(base, 0.12) if rng.random() < 0.5 else shade_col(base, 0.9),
                        lw=0, shade=0, hi=0, ao=0, opacity=0.6)
    for _ in range(int(w / 160)):
        stain(sub, rng.uniform(0, w), rng.uniform(0, h * 0.7), rng.uniform(30, 90), (40, 30, 30), rng.uniform(0.12, 0.22),
              drips=rng.randint(1, 4), seed=rng.randint(0, 999))
    for _ in range(int(w / 260)):
        crack(sub, rng.uniform(0, w), rng.uniform(0, h * 0.4), rng.uniform(60, 140), rng.uniform(60, 120), shade_col(base, 0.4), 2.0,
              seed=rng.randint(0, 999))
    y0 = h * 0.66
    sub.ink(rect(-4, y0 - 8, w + 4, y0 + 8), stripe, lw=2.2, shade=0.3, hi=0.3)
    grime_gradient(sub, 0, w, h, 140, (40, 20, 30), 0.45)
    scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.35, spread=90)


def dial(c, x, y, r, needle, face=(250, 246, 230), red=False, label=None):
    c.ink(ell(x, y, r + 5, r + 5), (90, 90, 110), lw=2.6, shade=0.4, hi=0.4)
    c.ink(ell(x, y, r, r), face, lw=1.8, shade=0.25, hi=0)
    for k in range(7):
        a = math.radians(150 + k * 40)
        c.stroke([(x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72), (x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)],
                 1.4, INK, taper=(0, 0))
    c.ink(Sh([[(x + math.cos(math.radians(330)) * r * 0.9, y + math.sin(math.radians(330)) * r * 0.9),
               (x + math.cos(math.radians(30)) * r * 0.9, y + math.sin(math.radians(30)) * r * 0.9), (x, y)]]), (230, 60, 60),
          lw=0, opacity=0.6, clip=ell(x, y, r * 0.92, r * 0.92))
    a = math.radians(needle)
    c.stroke([(x, y), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)], 2.4, (200, 30, 40) if red else INK, taper=(0, 0.5))
    c.ink(ell(x, y, 3, 3), INK, lw=0)
    if label:
        c.ink(rrect(x - r - 4, y + r + 8, x + r + 4, y + r + 24, 3), (250, 248, 236) if not red else (255, 220, 220), lw=1.6)
        c.text(x, y + r + 16, label, 7.5, (200, 30, 40) if red else INK, "Bold")


def paint_science_basement():
    c, R, rng = std_room(340, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 70, 140)

    def ceil(sub):
        w, h = sub.w, sub.h
        sub.ink(rect(0, 0, w, h), (70, 50, 80), lw=0, shade=0, hi=0, ao=0, tex=0.3, wob=0)
        d = sub.density
        for y in np.arange(20, h, 110 * d):        # joists running across
            sub.ink(rect(-5, y, w + 5, y + 30 * d), (96, 70, 96), lw=2.4, shade=0.4, sw=10, hi=0.3)
        for _ in range(8):
            stain(sub, rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 90), (30, 20, 20), 0.3, 0, rng.randint(0, 99))

    def left(sub):
        block_wall(sub, sub.w, sub.h, mix(WALL, (110, 50, 120), 0.3), seed=51)
        # stairwell opening with steps going up toward the back
        x0, x1 = sub.ax(330), sub.ax(150)
        y0, y1 = sub.by(280), sub.by(0)
        sub.ink(rect(x0 - 20, y0 - 20, x1 + 20, y1), (120, 110, 130), lw=3.0, shade=0.4, sw=10, hi=0.3)
        sub.ink(rect(x0, y0, x1, y1), ("v", (255, 210, 140), (90, 60, 80)), lw=2.6, shade=0.2)
        n = 7
        for k in range(n):
            ty = y1 - (k + 1) * (y1 - y0) * 0.11
            tx0 = x0 + (x1 - x0) * (0.0 + k * 0.08)
            sub.ink(rect(tx0, ty, x1, ty + (y1 - y0) * 0.11), mix((150, 120, 130), (255, 220, 170), k / n), lw=2.2, shade=0.3, hi=0.4)
        sub.stroke([(x0 + 10, y1 - 150 * sub.density), (x1 - 10, y0 + 120 * sub.density)], 5, (240, 200, 60))
        sub.ink(rect(x0 + 10, y0 - 66, x1 - 10, y0 - 26), (40, 40, 80), lw=2.6, shade=0.3)
        sub.text((x0 + x1) / 2, y0 - 46, "UP TO HALL ^", 15 * sub.density, (255, 230, 140))
        pipe(sub, [(0, sub.by(380)), (sub.w, sub.by(380))], w=26 * sub.density, col=(60, 160, 170))

    def right(sub):
        block_wall(sub, sub.w, sub.h, mix(WALL, (110, 50, 120), 0.2), seed=52)
        pipe(sub, [(0, sub.by(360)), (sub.w, sub.by(360))], w=26 * sub.density, col=(60, 160, 170))
        pipe(sub, [(sub.ax(320), sub.by(360)), (sub.ax(320), sub.by(0))], w=22 * sub.density, col=(200, 120, 80))

    def floor(sub):
        sub.ink(rect(0, 0, sub.w, sub.h), (110, 100, 120), lw=0, shade=0, hi=0, ao=0, tex=0.35, wob=0)
        r_ = random.Random(53)
        for _ in range(14):
            stain(sub, r_.uniform(0, sub.w), r_.uniform(0, sub.h), r_.uniform(40, 120), (40, 30, 40), 0.18, 0, r_.randint(0, 99))
        for _ in range(8):
            crack(sub, r_.uniform(0, sub.w), r_.uniform(0, sub.h), r_.uniform(80, 200), r_.uniform(0, 180), (50, 40, 60), 2.2,
                  seed=r_.randint(0, 999), branches=1)
        for x in np.arange(0, sub.w, 300 * sub.density):           # expansion joints
            sub.stroke([(x, 0), (x, sub.h)], 2.2, (70, 60, 80), taper=(0, 0), opacity=0.7)
        sub.stroke([(0, sub.by(260)), (sub.w, sub.by(260))], 2.2, (70, 60, 80), taper=(0, 0), opacity=0.7)
        # yellow safety line
        sub.stroke([(0, sub.by(140)), (sub.w, sub.by(140))], 10 * sub.density, (230, 190, 50), taper=(0, 0), opacity=0.7)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=340)

    def back(sub):
        block_wall(sub, sub.w, sub.h, WALL, seed=54)
        pipe(sub, [(-10, sub.by(380)), (sub.w + 10, sub.by(380))], w=26, col=(60, 160, 170),
             brackets=[(200, sub.by(380)), (700, sub.by(380)), (1150, sub.by(380))])
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=54)
    R.ao(0.6)
    R.edges(w=4.0)

    # --- ceiling: big pipes and the duct from the air handler branching off
    pipe(c, [P(0, Hb - 40, 60), P(Wb, Hb - 40, 60)], w=34, col=(170, 120, 90), brackets=[P(300, Hb - 40, 60), P(900, Hb - 40, 60)])
    pipe(c, [P(0, Hb - 80, 20), P(Wb, Hb - 80, 20)], w=18, col=(120, 160, 200))
    R.ink_box(860, 980, 300, Hb + 1, 30, 110, (170, 176, 190), side=(120, 124, 140), seed=21)       # duct up from the handler
    R.ink_box(0, 980, Hb - 60, Hb + 1, 50, 140, (170, 176, 190), side=(120, 124, 140), seed=22)
    for X, lab in ((120, "LIBRARY"), (430, "HALL"), (700, "LAB 3B")):
        x_, y_ = P(X, Hb - 30, 140)
        c.ink(rrect(x_ - 40, y_ - 4, x_ + 40, y_ + 16, 3), (250, 248, 236) if lab != "LAB 3B" else (255, 210, 210), lw=1.8)
        c.text(x_, y_ + 6, lab, 9, (200, 40, 50) if lab == "LAB 3B" else (40, 60, 120), "Bold")
    ax_, ay_ = P(700, Hb - 80, 140)
    c.ink(Sh([[(ax_ - 14, ay_), (ax_ + 14, ay_), (ax_ + 14, ay_ + 22), (ax_ + 26, ay_ + 22), (ax_, ay_ + 46), (ax_ - 26, ay_ + 22),
               (ax_ - 14, ay_ + 22)]]), (220, 50, 60), lw=2.4, shade=0.3, hi=0.3)
    cable(c, P(0, Hb, 300), P(600, Hb, 360), sag=50, w=7, col=(40, 30, 70))
    hanging_cable(c, P(1100, Hb, 260), 120, sway=-14, w=6, col=(40, 30, 70), seed=4)
    cobweb(c, *P(0, Hb, 0), 130, "tl", opacity=0.6)
    cobweb(c, *P(Wb, Hb, 0), 120, "tr", opacity=0.6)
    hanging_web(c, *P(980, Hb - 60, 110), 60)

    # --- duct map blueprint (X 0..200, Y 220..360)
    mx0, my0 = P(10, 360)
    mx1, my1 = P(200, 220)

    def ductmap(p, w_, h_):
        p.ink(rect(0, 0, w_, h_), (40, 80, 170), lw=0)
        for x in np.arange(0, w_, 12):
            p.stroke([(x, 0), (x, h_)], 0.8, (90, 130, 210), taper=(0, 0), opacity=0.6)
        for y in np.arange(0, h_, 12):
            p.stroke([(0, y), (w_, y)], 0.8, (90, 130, 210), taper=(0, 0), opacity=0.6)
        wc = (240, 248, 255)
        p.stroke([(w_ * 0.5, h_ * 0.86), (w_ * 0.5, h_ * 0.5), (w_ * 0.15, h_ * 0.5), (w_ * 0.15, h_ * 0.2)], 3, wc, taper=(0, 0), smooth=0)
        p.stroke([(w_ * 0.5, h_ * 0.5), (w_ * 0.85, h_ * 0.5), (w_ * 0.85, h_ * 0.2)], 3, wc, taper=(0, 0), smooth=0)
        p.stroke([(w_ * 0.5, h_ * 0.5), (w_ * 0.5, h_ * 0.2)], 3, (255, 120, 120), taper=(0, 0), smooth=0)
        for (x, y, t) in ((0.15, 0.13, "LIB"), (0.5, 0.13, "LAB 3B"), (0.85, 0.13, "HALL"), (0.5, 0.93, "AH")):
            p.text(w_ * x, h_ * y, t, 7, (255, 120, 120) if t == "LAB 3B" else wc, "Bold")
        p.text(w_ * 0.5, h_ * 0.68, "BLOW = OUT", 6, wc, "Bold")
        p.text(w_ * 0.5, h_ * 0.77, "DRAW = IN", 6, wc, "Bold")
    poster(c, (mx0 + mx1) / 2, (my0 + my1) / 2, mx1 - mx0, my1 - my0, (40, 80, 170), ductmap, angle=-2, seed=31, peel="bl")

    # --- roller derby poster + folding chair in Dot's corner (behind where she stands)
    dpx, dpy = P(320, 260)

    def derby(p, w_, h_):
        p.ink(rect(0, 0, w_, h_), ("v", (60, 20, 80), (200, 40, 110)), lw=0)
        p.text(w_ / 2, h_ * 0.12, "ROLLER DERBY", 11, (255, 220, 60))
        p.text(w_ / 2, h_ * 0.22, "REGIONAL FINALS '88", 6.5, (255, 255, 240), "Bold")
        st = [(w_ / 2 + math.cos(math.radians(-90 + k * 36)) * (w_ * (0.3 if k % 2 == 0 else 0.13)),
               h_ * 0.52 + math.sin(math.radians(-90 + k * 36)) * (w_ * (0.3 if k % 2 == 0 else 0.13))) for k in range(10)]
        p.ink(Sh([st]), (255, 220, 60), lw=1.8, shade=0.2)
        p.ink(ell(w_ / 2, h_ * 0.52, w_ * 0.08, w_ * 0.08), (220, 40, 60), lw=1.2)
        p.text(w_ / 2, h_ * 0.82, "DOT THE", 10, (255, 255, 240))
        p.text(w_ / 2, h_ * 0.92, "DESTROYER", 10, (255, 120, 150))
    poster(c, dpx, dpy, 120, 160, (60, 20, 80), derby, angle=3, seed=32, peel="tr")
    chx, chy = P(330, 0, 40)
    c.stroke([(chx - 30, chy), (chx - 20, chy - 70)], 4, INK, taper=(0, 0))
    c.stroke([(chx + 30, chy), (chx + 20, chy - 70)], 4, INK, taper=(0, 0))
    c.ink(rect(chx - 32, chy - 74, chx + 32, chy - 62), (60, 110, 150), lw=2.2, shade=0.3)
    c.ink(rect(chx - 24, chy - 130, chx + 24, chy - 96), (60, 110, 150), lw=2.2, shade=0.3)
    c.stroke([(chx - 22, chy - 96), (chx - 20, chy - 62)], 3.4, INK, taper=(0, 0))
    c.stroke([(chx + 22, chy - 96), (chx + 20, chy - 62)], 3.4, INK, taper=(0, 0))
    lbx, lby = P(380, 0, 60)
    c.ink(rrect(lbx - 22, lby - 26, lbx + 22, lby, 4), (220, 60, 60), lw=2.2, shade=0.4, hi=0.3)        # lunch box
    c.stroke(bez((lbx - 10, lby - 26), (lbx, lby - 40), (lbx + 10, lby - 26), 8), 2.4, INK, taper=(0, 0))

    # --- crate with the polka radio (X 30..130, Z 40..100)
    R.contact(30, 130, 40, 100, 0.5)
    f = R.ink_box(30, 130, 0, 70, 40, 100, (180, 130, 80), seed=23)
    (fx0, fy0), (fx1, _), (_, fy1) = f["front"][0], f["front"][1], f["front"][2]
    for k in (0.33, 0.66):
        c.stroke([(fx0 + 4, fy0 + (fy1 - fy0) * k), (fx1 - 4, fy0 + (fy1 - fy0) * k)], 2.0, (120, 80, 50), taper=(0, 0))
    c.text((fx0 + fx1) / 2, (fy0 + fy1) / 2 + 4, "FRAGILE", 10, (180, 40, 40), angle=-10)
    rf = R.ink_box(42, 118, 70, 122, 54, 84, (210, 70, 60), seed=24)
    (rx0, ry0), (rx1, _), (_, ry1) = rf["front"][0], rf["front"][1], rf["front"][2]
    c.ink(ell(rx0 + (rx1 - rx0) * 0.3, (ry0 + ry1) / 2, (ry1 - ry0) * 0.32, (ry1 - ry0) * 0.32), (60, 40, 50), lw=2.0)
    for k in range(4):
        c.stroke([(rx0 + (rx1 - rx0) * 0.18, ry0 + (ry1 - ry0) * (0.3 + k * 0.12)), (rx0 + (rx1 - rx0) * 0.42, ry0 + (ry1 - ry0) * (0.3 + k * 0.12))],
                 1.4, (120, 100, 110), taper=(0, 0))
    c.ink(rrect(rx0 + (rx1 - rx0) * 0.55, ry0 + 6, rx1 - 6, ry0 + (ry1 - ry0) * 0.45, 3), (255, 220, 120), lw=1.6)
    radio_glow = (rx0 + (rx1 - rx0) * 0.72, ry0 + 14)
    c.stroke([(rx1 - 10, ry0), (rx1 + 10, ry0 - 50)], 2.2, (200, 200, 210), taper=(0, 0.3))
    for k, (nx, ny) in enumerate(((rx1 + 20, ry0 - 20), (rx1 + 44, ry0 - 44), (rx0 - 10, ry0 - 30))):
        c.stroke([(nx, ny), (nx, ny - 18)], 2.4, (255, 236, 150), taper=(0, 0))
        c.ink(ell(nx - 5, ny, 5.5, 4, -20), (255, 236, 150), lw=1.4)

    # --- mop cart (X 520..660, Z 60..120): bucket, wringer, a rack of grey mop heads, CAUTION sign
    R.contact(520, 660, 60, 120, 0.5)
    R.ink_box(520, 660, 10, 26, 60, 120, (240, 200, 50), seed=25)
    for X in (530, 650):
        for Z in (66, 114):
            c.ink(ell(*P(X, 4, Z), 6, 6), (40, 40, 50), lw=1.6)
    bk = R.box(530, 610, 26, 86, 70, 114)
    c.ink(Sh([bk["front"]]), (240, 200, 50), lw=2.6, shade=0.4, hi=0.35)
    if "top" in bk:
        c.ink(Sh([bk["top"]]), (90, 120, 110), lw=2.0, shade=0.2)
    wr = R.box(560, 600, 86, 112, 80, 104)
    c.ink(Sh([wr["front"]]), (170, 170, 186), lw=2.2, shade=0.3, hi=0.3)
    mx_, my_ = P(640, 26, 100)
    c.stroke([(mx_, my_), (mx_ + 18, my_ - 230)], 7, INK, taper=(0, 0))
    c.stroke([(mx_, my_), (mx_ + 18, my_ - 230)], 3.6, (190, 150, 100), taper=(0, 0))
    c.ink(blob([(mx_ - 20, my_ + 2), (mx_ - 12, my_ - 20), (mx_ + 12, my_ - 20), (mx_ + 22, my_ + 2), (mx_, my_ + 8)], 2),
          (210, 206, 196), lw=2.2, shade=0.4)
    # hanging rack of mop heads like sad wigs
    rk0, rk1 = P(540, 150, 64), P(640, 150, 64)
    c.stroke([rk0, rk1], 4, INK, taper=(0, 0))
    c.stroke([P(540, 26, 64), rk0], 3.4, INK, taper=(0, 0))
    for k in range(3):
        hx_ = rk0[0] + (rk1[0] - rk0[0]) * (k + 0.5) / 3
        c.ink(blob([(hx_ - 14, rk0[1]), (hx_ + 14, rk0[1]), (hx_ + 18, rk0[1] + 40), (hx_ + 4, rk0[1] + 46), (hx_ - 10, rk0[1] + 44),
                    (hx_ - 18, rk0[1] + 38)], 2), (170, 170, 180), lw=2.0, shade=0.4, hi=0.2)
        for j in range(4):
            c.stroke([(hx_ - 10 + j * 7, rk0[1] + 8), (hx_ - 12 + j * 7, rk0[1] + 40)], 1.2, (120, 120, 136), taper=(0, 0.3))
    cs = P(500, 0, 130)
    c.ink(Sh([[(cs[0] - 26, cs[1]), (cs[0] - 6, cs[1] - 90), (cs[0] + 6, cs[1] - 90), (cs[0] + 26, cs[1])]]), (250, 210, 40), lw=2.6,
          shade=0.4, hi=0.3)
    c.text(cs[0], cs[1] - 50, "!", 16, INK)
    c.text(cs[0], cs[1] - 26, "CAUTION", 6.5, INK, "Bold")

    # --- the air handler (X 720..1000, Z 0..110, 300 tall)
    R.contact(720, 1000, 0, 110, 0.55)
    f = R.ink_box(720, 1000, 0, 300, 0, 110, (150, 160, 176), side=(100, 106, 124), seed=26)
    (ax0, ay0), (ax1, _), (_, ay1) = f["front"][0], f["front"][1], f["front"][2]
    aw, ah = ax1 - ax0, ay1 - ay0
    for (sx_, sy_) in ((ax0 + 10, ay0 + 10), (ax1 - 10, ay0 + 10), (ax0 + 10, ay1 - 10), (ax1 - 10, ay1 - 10)):
        c.ink(ell(sx_, sy_, 4, 4), (110, 110, 130), lw=1.4)
    c.ink(rrect(ax0 + 20, ay0 + 16, ax1 - 20, ay0 + 52, 4), (40, 40, 60), lw=2.2)
    c.text((ax0 + ax1) / 2, ay0 + 34, "AIR HANDLER - D.P. ONLY", 13, (255, 220, 80))
    for k, (lab, red, ndl) in enumerate((("LIBRARY", False, 240), ("HALL", False, 290), ("LOUNGE", False, 260), ("LAB 3B", True, 340))):
        dial(c, ax0 + aw * (0.14 + k * 0.24), ay0 + ah * 0.33, aw * 0.075, ndl, red=red, label=lab)
    gx0, gy0 = ax0 + aw * 0.08, ay0 + ah * 0.6
    gx1, gy1 = ax0 + aw * 0.66, ay1 - ah * 0.08
    c.ink(rect(gx0, gy0, gx1, gy1), (60, 60, 76), lw=2.4)
    for yy in np.arange(gy0 + 6, gy1 - 2, 9):
        c.ink(rect(gx0 + 4, yy - 2, gx1 - 4, yy + 3), (130, 130, 150), lw=1.2, shade=0.3)
    lv = (ax0 + aw * 0.82, ay0 + ah * 0.78)
    c.ink(rect(lv[0] - 18, lv[1] - 8, lv[0] + 18, lv[1] + 40), (80, 80, 96), lw=2.2)
    c.stroke([lv, (lv[0] + 30, lv[1] - 70)], 8, INK, taper=(0, 0))
    c.stroke([lv, (lv[0] + 30, lv[1] - 70)], 4, (200, 200, 210), taper=(0, 0))
    c.ink(ell(lv[0] + 30, lv[1] - 72, 11, 11), (220, 40, 50), lw=2.2, hi=0.5)
    c.ink(rect(ax1 - aw * 0.3, ay0 + ah * 0.55, ax1 - 14, ay0 + ah * 0.62), (250, 248, 236), lw=1.4)
    c.text(ax1 - aw * 0.3 + (aw * 0.3 - 14) / 2, ay0 + ah * 0.585, "BLOW / DRAW", 6, INK, "Bold")

    # --- the boiler (round tank, X 1060..1240, Z 40..200) with a glowing fire window
    bxc, bz = 1150, 130
    k = R.k(bz)
    bx_, by_ = P(bxc, 0, bz)
    bw_, bh_ = 105 * k, 330 * k
    R.contact(1060, 1240, 50, 210, 0.55)
    body = Sh([[(bx_ - bw_, by_ - bh_ + 30), (bx_ - bw_ * 0.9, by_ - bh_), (bx_ + bw_ * 0.9, by_ - bh_), (bx_ + bw_, by_ - bh_ + 30),
                (bx_ + bw_, by_ - 10), (bx_ - bw_, by_ - 10)]])
    c.ink(body, (210, 100, 60), lw=3.4, shade=0.6, sw=bw_ * 0.7, scol=(120, 40, 50), hi=0.4, hw=bw_ * 0.2, rim=0.25, tex=0.18)
    for yy in (by_ - bh_ + 50, by_ - bh_ * 0.5, by_ - 40):
        c.stroke(ell_pts(bx_, yy, bw_, 10, 0, 30, 0, 180), 3.0, (120, 50, 50), taper=(0, 0))
        for j in range(7):
            a = math.radians(15 + j * 25)
            c.ink(ell(bx_ + math.cos(a) * bw_ * 0.98, yy + math.sin(a) * 10, 2.5, 2.5), (250, 200, 160), lw=0.8)
    c.ink(rect(bx_ - bw_ * 0.6, by_ - 12, bx_ + bw_ * 0.6, by_), (60, 50, 60), lw=2.2)
    fw0, fw1 = (bx_ - 40, by_ - 150), (bx_ + 40, by_ - 70)
    c.ink(rrect(fw0[0] - 10, fw0[1] - 10, fw1[0] + 10, fw1[1] + 10, 8), (70, 60, 70), lw=2.6, shade=0.3)
    c.ink(rrect(fw0[0], fw0[1], fw1[0], fw1[1], 6), ("v", (255, 230, 120), (255, 110, 40)), lw=2.2, shade=0.1)
    for j in range(3):
        fx_ = fw0[0] + 14 + j * 26
        c.ink(blob([(fx_ - 10, fw1[1] - 4), (fx_, fw1[1] - 44 - j % 2 * 10), (fx_ + 10, fw1[1] - 4)], 2), (255, 250, 200), lw=0, opacity=0.8)
    fire = ((fw0[0] + fw1[0]) / 2, (fw0[1] + fw1[1]) / 2)
    dial(c, bx_, by_ - bh_ + 90, 26, 320, red=True)
    c.ink(rect(bx_ - 46, by_ - bh_ + 130, bx_ + 46, by_ - bh_ + 150), (250, 248, 236), lw=1.6, shade=0.2)
    c.text(bx_, by_ - bh_ + 140, "IT'S FINE. -DOT", 7, INK, "Bold")
    pipe(c, [(bx_ - bw_ * 0.4, by_ - bh_ + 4), (bx_ - bw_ * 0.4, P(0, Hb, 0)[1] - 10)], w=30, col=(140, 120, 120))
    for j in range(3):
        c.soft(ell(bx_ + bw_ * 0.6 + j * 16, by_ - bh_ - 20 - j * 30, 18 + j * 6, 14 + j * 4), (230, 220, 240), 0.25, 8)

    # --- caged work lights on the back wall
    lamps = []
    for X in (260, 700, 1060):
        lx_, ly_ = P(X, 330)
        caged_light(c, lx_, ly_, 12, strength=0.5, cone_to=760)
        lamps.append((lx_, ly_))
    # floor: a drain, a puddle under the boiler, a lost sock and gum wrappers
    dx_, dy_ = P(820, 0, 300)
    c.ink(ell(dx_, dy_, 40, 10), (70, 66, 80), lw=2.4, shade=0.3)
    for j in range(-3, 4):
        c.stroke([(dx_ + j * 9, dy_ - 7), (dx_ + j * 9, dy_ + 7)], 1.6, (30, 26, 40), taper=(0, 0))
    pdx, pdy = P(1080, 0, 240)
    c.ink(ell(pdx, pdy, 90, 16), (130, 150, 190), lw=1.6, oc=(60, 60, 90), shade=0, hi=0.5, hw=4, opacity=0.8)

    room_grade(c, lights=[(lamps[0][0], 600, 420, 0.4), (lamps[1][0], 600, 420, 0.4), (lamps[2][0], 600, 380, 0.35),
                          (fire[0], fire[1] + 60, 420, 0.5, (255, 140, 60)), (110, 600, 300, 0.35, (255, 200, 130)),
                          (radio_glow[0], radio_glow[1], 160, 0.3, (255, 220, 120))],
               ambient=0.88, vign=0.65, top_dark=0.5, bottom_dark=0.4)
    for (x, y) in lamps:
        c.glow2(x, y, 90, GLOW, 0.45)
    c.glow2(*fire, 160, (255, 160, 70), 0.45)
    floor_pool(c, fire[0] - 60, P(0, 0, 260)[1], 260, 40, (255, 150, 70), 0.25)
    c.painterly(0.05)

    def fg(sub):
        fg_bottles(sub, 1700, 1090, 5, 1.0, seed=33)
        sub.ink(rect(-30, 740, 50, 1100), FG, lw=0, shade=0.2, hi=0.2, hw=6)     # a pipe riser, bottom-left corner
        sub.ink(rrect(-50, 820, 70, 860, 6), FG, lw=0)
        fg_cable(sub, [(200, 1100), (500, 1050), (900, 1080), (1300, 1050), (1650, 1100)], 18)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_science_basement.png")


LAYOUT["science_basement"] = dict(
        walk_px=[(180, Y_TOP), (1750, Y_TOP), (1830, 880), (1790, Y_BOT), (130, Y_BOT), (70, 880)],
        hotspots={
            ("Stairs up", 0): dict(box=(20, 330, 215, 815), stand=(230, 830)),
            ("Duct map", 0): dict(box=(320, 320, 545, 480), stand=(430, 800)),
            ("Polka radio", 0): dict(box=(285, 560, 415, 730), stand=(350, 800)),
            ("Dot Pruitt", 0): dict(npc="hs_dot_pruitt", feet=(650, NPC_FEET_Y), stand=(840, 935)),
            ("Mop cart", 0): dict(box=(815, 470, 1010, 740), stand=(910, 800)),
            ("Air handler", 0): dict(box=(1050, 370, 1390, 730), stand=(1220, 800)),
            ("Boiler", 0): dict(box=(1435, 300, 1690, 760), stand=(1560, 820)),
        },
        entries={"from_hall": (240, 880)})


# =========================================================================== 5. Faculty lounge
def damask_wall(sub, w, h, base, seed=0, stripe=None):
    """Old striped wallpaper with a faint diamond motif, peeling at a seam (flat space)."""
    rng = random.Random(seed)
    grunge_wall(sub, w, h, base, seed=seed, chips=3, stains=4, cracks=2, floor_y=h)
    d = getattr(sub, "density", 1.0)
    sc = stripe or shade_col(base, 0.86)
    for x in np.arange(0, w, 70 * d):
        sub.ink(rect(x, -5, x + 22 * d, h + 5), sc, lw=0, shade=0, hi=0, ao=0, tex=0.1, wob=0, opacity=0.55)
        for y in np.arange(30 * d, h, 80 * d):
            cx_, cy_ = x + 46 * d, y
            sub.ink(Sh([[(cx_, cy_ - 12 * d), (cx_ + 8 * d, cy_), (cx_, cy_ + 12 * d), (cx_ - 8 * d, cy_)]]), hi_col(base, 0.2), lw=0,
                    shade=0, hi=0, ao=0, opacity=0.45)
    for _ in range(2):         # a peeling seam: a dark gap with a curled strip of paper
        x = rng.uniform(0.1, 0.9) * w
        y = rng.uniform(0.05, 0.3) * h
        sub.ink(rect(x, y, x + 6 * d, y + 90 * d), (50, 20, 50), lw=0, shade=0, hi=0, ao=0, opacity=0.7)
        sub.ink(blob([(x + 6 * d, y), (x + 26 * d, y + 8 * d), (x + 30 * d, y + 40 * d), (x + 12 * d, y + 54 * d), (x + 6 * d, y + 50 * d)], 2),
                hi_col(base, 0.12), lw=1.8, shade=0.5, sw=8, hi=0.2)


def armchair(c, R, X0, X1, Z0, Z1, col=(170, 40, 70), seed=0):
    """Wingback armchair facing the camera (a little sunken), with a doily and a crumb-covered cushion."""
    P = R.pt
    R.contact(X0, X1, Z0, Z1, 0.55)
    dk_ = shade_col(col, 0.72)
    w = X1 - X0
    # back with wings
    bf = R.box(X0 + 14, X1 - 14, 40, 190, Z0, Z0 + 30)
    q = bf["front"]
    back = blob([q[3], (q[3][0] - 6, q[3][1] - 60), (q[0][0] - 10, q[0][1] + 30), (q[0][0] + 10, q[0][1] - 6),
                 ((q[0][0] + q[1][0]) / 2, q[0][1] - 18), (q[1][0] - 10, q[1][1] - 6), (q[1][0] + 10, q[1][1] + 30),
                 (q[2][0] + 6, q[2][1] - 60), q[2]], 2)
    c.ink(back, dk_, lw=3.0, shade=0.45, sw=30, hi=0.3, rim=0.2, tex=0.15)
    for k in range(3):
        for j in range(4):
            bx_ = q[0][0] + (q[1][0] - q[0][0]) * (j + 0.5) / 4
            by_ = q[0][1] + 30 + k * 34
            c.ink(ell(bx_, by_, 3, 3), shade_col(col, 0.5), lw=1.0)
    # seat base + cushion
    R.ink_box(X0 + 8, X1 - 8, 0, 56, Z0 + 20, Z1, col, seed=seed)
    cf = R.box(X0 + 40, X1 - 40, 52, 70, Z0 + 30, Z1 - 4)
    c.ink(blob(cf.get("top", cf["front"]), 2), hi_col(col, 0.12), lw=2.8, shade=0.3, hi=0.35)
    c.ink(blob(cf["front"], 2), col, lw=2.6, shade=0.4, hi=0.2)
    # rolled arms
    for xa, xb in ((X0, X0 + 40), (X1 - 40, X1)):
        f = R.box(xa, xb, 0, 100, Z0 + 18, Z1 + 6)
        for name in ("left", "right"):
            if name in f:
                c.ink(blob(f[name], 2), dk_, lw=2.8, shade=0.3, tex=0.15)
        c.ink(blob(f["front"], 2), col, lw=2.8, shade=0.45, sw=10, hi=0.3, tex=0.15)
        tx_, ty_ = P((xa + xb) / 2, 100, Z1 + 6)
        c.ink(ell(tx_, ty_, (xb - xa) * 0.62, 12), hi_col(col, 0.1), lw=2.6, shade=0.4, hi=0.4)
    # legs
    for X in (X0 + 14, X1 - 14):
        x_, y_ = P(X, 0, Z1)
        c.ink(rect(x_ - 5, y_ - 8, x_ + 5, y_ + 4), (90, 50, 30), lw=1.8)
    # doily on the back, a newspaper on the seat, crumbs
    dx_, dy_ = (q[0][0] + q[1][0]) / 2, q[0][1] - 4
    c.ink(ell(dx_, dy_, 30, 12), (250, 246, 236), lw=1.8, shade=0.2)
    c.ink(ell(dx_, dy_, 18, 7), (0, 0, 0, 0), lw=1.0, oc=(200, 190, 180), line_only=True)
    nx_, ny_ = P(X0 + w * 0.6, 70, (Z0 + Z1) / 2 + 14)
    c.ink(Sh([rot_pts([(nx_ - 34, ny_ - 10), (nx_ + 34, ny_ - 10), (nx_ + 30, ny_ + 6), (nx_ - 30, ny_ + 6)], -8, nx_, ny_)]),
          (236, 232, 220), lw=2.0, shade=0.2)
    for k in range(3):
        c.stroke(rot_pts([(nx_ - 24, ny_ - 5 + k * 4), (nx_ + 20, ny_ - 5 + k * 4)], -8, nx_, ny_), 1.2, (120, 120, 130), taper=(0, 0))
    rng = random.Random(seed)
    for _ in range(10):
        cx_, cy_ = P(X0 + rng.uniform(50, w - 50), 70, rng.uniform(Z0 + 40, Z1 - 10))
        c.ink(ell(cx_, cy_, 2.2, 1.6), (220, 170, 100), lw=0.8)


def paint_faculty_lounge():
    c, R, rng = std_room(350, back=(330, 250, 1590, 690))
    Wb, Hb = R.Wb, R.Hb
    P = R.pt
    WALL = (150, 56, 120)
    WOOD = (40, 120, 120)          # teal-painted wainscot

    def ceil(sub):
        plaster_wall(sub, (110, 60, 100), (80, 40, 80), seed=61, w=sub.w, h=sub.h)
        d = sub.density
        for y in np.arange(0, sub.h, 160 * d):
            sub.ink(rect(-5, y, sub.w + 5, y + 36 * d), (100, 56, 50), lw=2.6, shade=0.4, sw=12, hi=0.3)
        for _ in range(6):
            stain(sub, rng.uniform(0, sub.w), rng.uniform(0, sub.h), rng.uniform(40, 100), (60, 30, 20), 0.25, 0, rng.randint(0, 99))
        # ceiling rose for the chandelier
        x, y = sub.ax(630), sub.by(200)
        sub.ink(ell(x, y, 70 * d, 36 * d), (190, 150, 170), lw=2.4, shade=0.3, hi=0.3)

    def wall(sub, seed):
        w, h = sub.w, sub.h
        damask_wall(sub, w, h, WALL, seed=seed)
        wainscot(sub, -6, w + 6, h * 0.62, h, WOOD, seed=seed, panel_w=150 * getattr(sub, "density", 1.0))
        scuffs(sub, 0, w, h - 10, int(w / 30), seed=seed, opacity=0.3, spread=80)

    def left(sub):
        wall(sub, 61)
        x0, x1, y0, y1 = side_door(sub, 330, 160, 300, (130, 70, 50), frame=(90, 50, 40), seed=11, knob="R")
        sub.ink(rect(x0 - 26, y0 - 70, x1 + 26, y0 - 26), (40, 40, 80), lw=2.6, shade=0.3)
        sub.text((x0 + x1) / 2, y0 - 48, "< HALL", 18 * sub.density, (255, 230, 140))
        # a small framed diploma further back
        fx = sub.ax(80)
        sub.ink(rect(fx - 40 * sub.density, sub.by(300), fx + 40 * sub.density, sub.by(220)), (200, 160, 70), lw=2.6, shade=0.3, hi=0.4)
        sub.ink(rect(fx - 30 * sub.density, sub.by(292), fx + 30 * sub.density, sub.by(228)), (250, 244, 226), lw=1.6)

    def right(sub):
        wall(sub, 62)

    def floor(sub):
        planks(sub, (130, 74, 56), 0, 0, sub.w, sub.h, pw=36 * sub.density, seed=63, vertical=False)

    R.shell(left_fn=left, right_fn=right, floor_fn=floor, ceil_fn=ceil, density=1.4, seed=350)

    def back(sub):
        wall(sub, 64)
    R.paint_plane("back", 0, Wb, 0, Hb, back, density=1.0, seed=64)
    R.ao(0.5)
    R.edges(w=4.0)

    # --- worn oriental-ish rug
    rug = [P(140, 0, 140), P(1120, 0, 140), P(1160, 0, 470), P(100, 0, 470)]
    c.ink(blob(rug, 1), (170, 40, 70), lw=3.0, shade=0.15, hi=0.05, tex=0.3)
    inner = [P(190, 0, 170), P(1070, 0, 170), P(1100, 0, 440), P(160, 0, 440)]
    c.ink(blob(inner, 1), (0, 0, 0, 0), lw=3.0, oc=(240, 190, 80), line_only=True)
    for k in range(5):
        X = 330 + k * 150
        cx_, cy_ = P(X, 0, 300)
        kk = R.k(300)
        c.ink(Sh([[(cx_, cy_ - 22 * kk), (cx_ + 46 * kk, cy_), (cx_, cy_ + 22 * kk), (cx_ - 46 * kk, cy_)]]), (40, 140, 140), lw=2.0,
              shade=0.1, hi=0)
    for X in np.arange(110, 1160, 22):
        a = P(X, 0, 470)
        c.stroke([a, (a[0], a[1] + 10)], 2.0, (240, 220, 180), taper=(0, 0), opacity=0.8)
    c.soft(Sh([[P(500, 0, 250), P(760, 0, 250), P(760, 0, 330), P(500, 0, 330)]]), (40, 10, 30), 0.15, 20)     # a worn patch

    # --- coffee machine on a side table, OUT OF ORDER (X 20..140, Z 30..90)
    R.contact(20, 140, 30, 90, 0.5)
    R.ink_box(20, 140, 74, 84, 30, 90, (120, 70, 50), top=(160, 100, 70), seed=31)
    for X in (28, 132):
        for Z in (36, 84):
            c.stroke([P(X, 74, Z), P(X, 0, Z)], 5, INK, taper=(0, 0))
    m = R.ink_box(40, 120, 84, 190, 40, 80, (70, 70, 84), seed=32)
    (mx0, my0), (mx1, _), (_, my1) = m["front"][0], m["front"][1], m["front"][2]
    c.ink(rect(mx0 + 12, my0 + (my1 - my0) * 0.4, mx1 - 12, my1 - 8), (30, 26, 36), lw=2.0)
    c.ink(rrect(mx0 + 20, my1 - 40, mx1 - 20, my1 - 10, 4), (200, 220, 230, 160), lw=1.8, shade=0.1)        # empty carafe
    c.ink(rect(mx0 + 8, my0 + 8, mx1 - 8, my0 + 30), (180, 180, 196), lw=1.6)
    sg = Sh([rot_pts([(mx0 - 6, my0 + 20), (mx1 + 10, my0 + 20), (mx1 + 10, my0 + 60), (mx0 - 6, my0 + 60)], -8, mx0, my0)])
    c.ink(sg, (252, 250, 236), lw=1.8, shade=0.2)
    c.text((mx0 + mx1) / 2 + 2, my0 + 33, "OUT OF ORDER", 7, (200, 30, 40), "Black", angle=8)
    c.text((mx0 + mx1) / 2, my0 + 44, "SINCE 1994", 6.5, INK, "Bold", angle=8)
    c.text((mx0 + mx1) / 2 - 2, my0 + 54, "DO NOT FIX", 6, (40, 60, 120), "Bold", angle=8)
    for k in range(4):        # a tower of dirty mugs
        cx_, cy_ = P(130, 84 + k * 16, 60)
        c.ink(rrect(cx_ - 10, cy_ - 16, cx_ + 10, cy_, 3), [(240, 240, 230), (230, 90, 90), (90, 170, 220), (250, 210, 80)][k], lw=1.8,
              shade=0.3)

    # --- Crumb's bookshelf against the right wall (X Wb-46..Wb, Z 100..300): all his own books
    BX0, BZ0, BZ1, BH = Wb - 46, 100, 300, 340
    R.contact(BX0, Wb, BZ0, BZ1, 0.5)
    WOODB = (110, 62, 44)
    R.ink_box(BX0, Wb, 0, BH, BZ0, BZ1, WOODB, seed=37)
    Wsave = R.Wb
    R.Wb = BX0

    def shelf_face(sub):
        d = sub.density
        r_ = random.Random(38)
        w, h = sub.w, sub.h
        sub.ink(rect(10 * d, 10 * d, w - 10 * d, h - 6 * d), shade_col(WOODB, 0.45), lw=2.4, shade=0.2, hi=0, ao=0.2)
        n = 5
        hs = (h - 20 * d) / n
        for i in range(n):
            yb = 10 * d + hs * (i + 1)
            cols = [(110, 40, 40), (60, 90, 70), (130, 90, 50), (70, 60, 110), (150, 120, 70)]
            x = 16 * d
            while x < w - 30 * d:
                bw = r_.uniform(10, 18) * d
                bh = hs * r_.uniform(0.62, 0.86)
                col = r_.choice(cols)
                sub.ink(rect(x, yb - 6 * d - bh, x + bw, yb - 6 * d), col, lw=1.8, shade=0.4, sw=bw * 0.3, hi=0.3, ao=0, tex=0.1)
                sub.stroke([(x + 2, yb - 6 * d - bh * 0.75), (x + bw - 2, yb - 6 * d - bh * 0.75)], 1.4, (230, 190, 100), taper=(0, 0))
                x += bw + 0.6
            sub.ink(rect(4 * d, yb - 7 * d, w - 4 * d, yb + 4 * d), hi_col(WOODB, 0.1), lw=2.2, shade=0.3, hi=0.4)
    R.paint_plane("R", BZ0, BZ1, 0, BH, shelf_face, density=1.2, seed=38)
    R.Wb = Wsave
    sx_, sy_ = P(BX0, BH + 10, (BZ0 + BZ1) / 2)
    c.ink(rrect(sx_ - 70, sy_ - 22, sx_ + 70, sy_ + 6, 4), (236, 196, 100), lw=2.2, shade=0.3, hi=0.5)
    c.text(sx_, sy_ - 8, "WORKS OF T. CRUMB", 9, (90, 50, 20), "Bold")

    # --- wall of tenure: brass plaques on a walnut board (X 170..430, Y 190..350)
    tx0, ty0 = P(170, 350)
    tx1, ty1 = P(430, 190)
    c.ink(rect(tx0, ty0, tx1, ty1), (110, 60, 40), lw=3.0, shade=0.45, sw=20, hi=0.3, tex=0.2)
    c.ink(rrect(tx0 + 30, ty0 + 10, tx1 - 30, ty0 + 34, 4), (236, 196, 100), lw=2.0, shade=0.3, hi=0.5)
    c.text((tx0 + tx1) / 2, ty0 + 22, "WALL OF TENURE", 12, (96, 56, 20))
    pw, ph = (tx1 - tx0 - 40) / 4, (ty1 - ty0 - 56) / 3
    for r_ in range(3):
        for k in range(4):
            px0, py0 = tx0 + 20 + k * pw, ty0 + 44 + r_ * ph
            if r_ == 1 and k == 1:
                c.ink(rrect(px0 + 4, py0 + 4, px0 + pw * 2 - 4, py0 + ph - 4, 3), (250, 210, 110), lw=1.8, shade=0.3, hi=0.6, hw=3)
                c.text(px0 + pw, py0 + ph * 0.38, "T. CRUMB", 9, (110, 60, 20))
                c.text(px0 + pw, py0 + ph * 0.7, "NEVER WRONG", 6, (110, 60, 20), "Bold")
                continue
            if r_ == 1 and k == 2:
                continue
            if r_ == 2 and k == 3:
                c.ink(rrect(px0 + 4, py0 + 4, px0 + pw - 4, py0 + ph - 4, 3), (90, 50, 30), lw=1.4)
                c.text(px0 + pw / 2, py0 + ph / 2, "?", 12, (200, 40, 50))
                continue
            c.ink(rrect(px0 + 4, py0 + 4, px0 + pw - 4, py0 + ph - 4, 3), (210, 170, 90), lw=1.6, shade=0.3, hi=0.4)
            c.stroke([(px0 + 10, py0 + ph * 0.45), (px0 + pw - 10, py0 + ph * 0.45)], 1.6, (130, 90, 40), taper=(0, 0))
            c.stroke([(px0 + 14, py0 + ph * 0.65), (px0 + pw - 14, py0 + ph * 0.65)], 1.2, (130, 90, 40), taper=(0, 0))

    # --- fireplace with the founder portrait above (X 720..960)
    R.contact(700, 980, 0, 50, 0.5)
    R.ink_box(700, 980, 0, 180, 0, 34, (200, 170, 160), seed=33)
    (fx0, fy0), (fx1, _), (_, fy1) = R.box(700, 980, 0, 180, 0, 34)["front"][0], R.box(700, 980, 0, 180, 0, 34)["front"][1], \
        R.box(700, 980, 0, 180, 0, 34)["front"][2]
    clip_draw(c, rect(fx0, fy0, fx1, fy1), lambda t: [t.stroke([(fx0, yy), (fx1, yy)], 1.6, (150, 110, 110), taper=(0, 0), opacity=0.7)
                                                       for yy in np.arange(fy0 + 14, fy1, 18)])
    ox0, oy0 = fx0 + (fx1 - fx0) * 0.22, fy0 + (fy1 - fy0) * 0.35
    ox1, oy1 = fx1 - (fx1 - fx0) * 0.22, fy1
    c.ink(Sh([[(ox0, oy1), (ox0, oy0 + 30), ((ox0 + ox1) / 2, oy0), (ox1, oy0 + 30), (ox1, oy1)]]), (30, 14, 26), lw=2.6)
    fire = ((ox0 + ox1) / 2, oy1 - 26)
    for j, (dx, hh, col) in enumerate(((-24, 50, (255, 120, 40)), (0, 70, (255, 170, 60)), (22, 46, (255, 120, 40)),
                                       (-8, 36, (255, 236, 140)), (10, 30, (255, 236, 140)))):
        c.ink(blob([(fire[0] + dx - 16, oy1 - 8), (fire[0] + dx - 6, oy1 - hh * 0.6), (fire[0] + dx + 2, oy1 - hh),
                    (fire[0] + dx + 8, oy1 - hh * 0.5), (fire[0] + dx + 16, oy1 - 8)], 2), col, lw=0, shade=0, hi=0.2, ao=0)
    c.ink(rect(ox0 + 6, oy1 - 10, ox1 - 6, oy1), (90, 50, 30), lw=2.0)
    R.ink_box(690, 990, 180, 194, 0, 46, (120, 70, 50), top=(160, 100, 70), seed=34)          # mantel
    for X in (730, 950):
        cx_, cy_ = P(X, 194, 24)
        c.ink(rect(cx_ - 4, cy_ - 34, cx_ + 4, cy_), (250, 246, 230), lw=1.6)
        c.ink(blob([(cx_ - 4, cy_ - 36), (cx_, cy_ - 50), (cx_ + 4, cy_ - 36)], 1), (255, 220, 100), lw=0)
        c.glow2(cx_, cy_ - 42, 40, GLOW, 0.5)
        c.ink(rect(cx_ - 8, cy_ - 4, cx_ + 8, cy_), (220, 180, 80), lw=1.6)
    # portrait: a stern founder with a magnificent moustache (X 760..920, Y 230..410)
    px0, py0 = P(760, 420)
    px1, py1 = P(920, 220)
    c.ink(rect(px0 - 14, py0 - 14, px1 + 14, py1 + 14), (210, 160, 60), lw=3.2, shade=0.45, sw=12, hi=0.5, hw=5, rim=0.2)
    c.ink(rect(px0, py0, px1, py1), ("v", (60, 80, 70), (30, 40, 40)), lw=2.4, shade=0.2)
    pcx = (px0 + px1) / 2
    c.ink(Sh([[(px0 + 20, py1), (pcx - 40, py1 - 60), (pcx + 40, py1 - 60), (px1 - 20, py1)]]), (40, 40, 60), lw=2.0, shade=0.3)
    c.ink(Sh([[(pcx - 12, py1 - 60), (pcx + 12, py1 - 60), (pcx, py1 - 30)]]), (240, 240, 230), lw=1.6)
    c.ink(ell(pcx, py1 - 104, 34, 42), (230, 190, 160), lw=2.4, shade=0.45, sw=10, hi=0.3)
    c.ink(blob([(pcx - 40, py1 - 92), (pcx - 10, py1 - 100), (pcx, py1 - 94), (pcx + 10, py1 - 100), (pcx + 40, py1 - 92),
                (pcx + 20, py1 - 86), (pcx, py1 - 90), (pcx - 20, py1 - 86)], 2), (240, 240, 240), lw=2.0, shade=0.3)
    c.ink(ell(pcx - 12, py1 - 112, 4, 3), INK, lw=0)
    c.ink(ell(pcx + 12, py1 - 112, 4, 3), INK, lw=0)
    c.stroke([(pcx - 20, py1 - 124), (pcx - 6, py1 - 120)], 2.6, INK)
    c.stroke([(pcx + 6, py1 - 120), (pcx + 20, py1 - 124)], 2.6, INK)
    c.ink(blob([(pcx - 34, py1 - 128), (pcx - 20, py1 - 148), (pcx + 22, py1 - 148), (pcx + 34, py1 - 126), (pcx, py1 - 138)], 2),
          (240, 240, 240), lw=2.0, shade=0.3)
    c.ink(rrect(pcx - 46, py1 + 2, pcx + 46, py1 + 12, 2), (236, 196, 100), lw=1.4)
    c.text(pcx, py1 + 7, "A. PLUMWORTH", 6.5, (90, 50, 20), "Bold")
    c.light_cone((pcx, py0 - 24), (px0 - 30, py1), (px1 + 30, py1), GLOW, 0.2, 14)
    c.ink(rect(pcx - 40, py0 - 30, pcx + 40, py0 - 20), (200, 170, 80), lw=1.8)

    # --- tall window with heavy curtains behind where Crumb stands (X 1060..1220)
    wx0, wy0 = P(1060, 400)
    wx1, wy1 = P(1220, 140)

    tmp = Canvas2(int(wx1 - wx0 + 200), int(wy1 - wy0 + 140), lw=3.0, seed=12)
    window_flat(tmp, 100, 60, tmp.w - 100, tmp.h - 80, frame=(230, 210, 200), seed=12, mullions=1, transoms=2, curtains=(110, 30, 70))
    c.img.alpha_composite(tmp.img, (int((wx0 - 100) * S), int((wy0 - 60) * S)))
    win_glow = ((wx0 + wx1) / 2, (wy0 + wy1) / 2)

    # --- a small table with a green banker's lamp between the armchair and the fireplace
    R.contact(640, 690, 120, 170, 0.4)
    R.ink_box(640, 690, 60, 66, 120, 170, (120, 70, 50), top=(160, 100, 70), seed=35)
    c.stroke([P(665, 60, 145), P(665, 0, 145)], 6, INK, taper=(0, 0))
    lx_, ly_ = P(665, 66, 145)
    banker_lamp(c, lx_, ly_, 1.0)
    lamp_xy = (lx_, ly_ - 40)

    # --- the armchair (X 470..650, Z 40..160)
    armchair(c, R, 440, 630, 40, 160, seed=36)

    # --- ceiling: beams, a slightly crooked chandelier
    chx, chy = P(630, Hb - 120, 200)
    c.stroke([P(630, Hb, 200), (chx, chy - 20)], 3.4, (200, 170, 80), taper=(0, 0))
    c.ink(ell(chx, chy, 90, 18), (210, 170, 70), lw=2.8, shade=0.4, hi=0.5)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        bx_, by_ = chx + math.cos(a) * 84, chy + math.sin(a) * 14
        c.ink(rect(bx_ - 4, by_ - 26, bx_ + 4, by_ - 4), (250, 246, 230), lw=1.4)
        c.ink(blob([(bx_ - 4, by_ - 28), (bx_, by_ - 40), (bx_ + 4, by_ - 28)], 1), (255, 220, 100), lw=0)
        c.glow2(bx_, by_ - 32, 40, GLOW, 0.4)
    for k in range(5):
        c.ink(ell(chx - 60 + k * 30, chy + 22 + (k % 2) * 8, 5, 8), (200, 230, 255), lw=1.2, shade=0.2, hi=0.6)
    cobweb(c, *P(0, Hb, 0), 110, "tl")
    cobweb(c, *P(Wb, Hb, 0), 100, "tr")
    hanging_web(c, chx + 70, chy + 14, 40)
    stain(c, *P(1000, 400), 50, (60, 20, 50), 0.2, 3, 5)

    room_grade(c, lights=[(chx, chy + 220, 620, 0.4), (fire[0], fire[1], 460, 0.55, (255, 140, 60)),
                          (lamp_xy[0], lamp_xy[1], 280, 0.35), (win_glow[0], win_glow[1], 300, 0.3, (130, 150, 255))],
               ambient=0.9, vign=0.62, top_dark=0.45, bottom_dark=0.35)
    c.glow2(chx, chy, 220, GLOW, 0.3)
    c.glow2(fire[0], fire[1] - 20, 180, (255, 150, 60), 0.45)
    floor_pool(c, fire[0], P(0, 0, 120)[1], 280, 50, (255, 150, 70), 0.25)
    c.glow2(*lamp_xy, 120, (255, 236, 160), 0.35)
    c.painterly(0.05)

    def fg(sub):
        fg_plant(sub, 70, 1110, 300, seed=41)
        fg_table_edge(sub, 1250, 1700, 1030, 120)
        sub.ink(Sh([[(1380, 1030), (1420, 960), (1470, 960), (1460, 1030)]]), FG, lw=0)      # a teapot-ish silhouette
        sub.ink(ell(1440, 950, 34, 20), FG, lw=0)
        fg_lamp_top(sub, 1500, 70, 320)
    fg_paint(c, fg, blur_px=3)
    c.save_png("bg_faculty_lounge.png")


LAYOUT["faculty_lounge"] = dict(
        walk_px=[(180, Y_TOP), (1750, Y_TOP), (1830, 880), (1790, Y_BOT), (130, Y_BOT), (70, 880)],
        hotspots={
            ("Hallway door", 0): dict(box=(20, 360, 215, 815), stand=(230, 830)),
            ("Coffee machine", 0): dict(box=(280, 500, 440, 725), stand=(360, 800)),
            ("Wall of tenure", 0): dict(box=(490, 330, 770, 510), stand=(630, 800)),
            ("Armchair", 0): dict(box=(740, 470, 990, 750), stand=(870, 800)),
            ("Founder portrait", 0): dict(box=(1075, 255, 1265, 480), stand=(1170, 800)),
            ("Professor Crumb", 0): dict(npc="hs_professor_crumb", feet=(1480, NPC_FEET_Y), stand=(1290, 935)),
            ("Bookshelf", 0): dict(box=(1600, 280, 1870, 800), stand=(1680, 830)),
        },
        entries={"from_hall": (240, 880)})


# =========================================================================== characters
def npc_height(rel):
    """Crown height (px) for an NPC standing with feet at NPC_FEET_Y (like Act 1)."""
    return round(DEX_H * depth_scale(NPC_FEET_Y, Y_TOP, Y_BOT) * rel)


def megaphone(c, x, y, s=1.0, ang=0, col=(236, 60, 60)):
    """Megaphone with its mouthpiece at (x, y), bell pointing along ang (degrees, 0 = right)."""
    pts = [(0, -5), (14, -6), (54, -22), (58, -22), (58, 22), (54, 22), (14, 6), (0, 5)]
    P_ = rot_pts([(x + px * s, y + py * s) for px, py in pts], ang, x, y)
    c.ink(Sh([P_]), col, lw=2.8, shade=0.5, sw=10 * s, hi=0.45, hw=4 * s, rim=0.2)
    bell = rot_pts([(x + 56 * s, y)], ang, x, y)[0]
    c.ink(ell(bell[0], bell[1], 6 * s, 22 * s, ang), (250, 246, 236), lw=2.4, shade=0.3, sw=4)
    c.ink(ell(bell[0], bell[1], 3 * s, 12 * s, ang), (60, 50, 60), lw=1.4)
    band = rot_pts([(x + 24 * s, y - 11 * s), (x + 32 * s, y - 14 * s), (x + 32 * s, y + 14 * s), (x + 24 * s, y + 11 * s)], ang, x, y)
    c.ink(Sh([band]), (250, 246, 236), lw=1.8, shade=0.2)
    hd = rot_pts([(x + 20 * s, y + 6 * s), (x + 26 * s, y + 6 * s), (x + 24 * s, y + 22 * s), (x + 18 * s, y + 22 * s)], ang, x, y)
    c.ink(Sh([hd]), (50, 50, 60), lw=2.0, shade=0.3)


def paint_mina(height=None, name="hs_dr_mina_volt.png"):
    """Dr. Mina Volt: a frazzled young lab scientist: storm-cloud hair with a pencil in it, goggles pushed up,
    long lab coat over a teal turtleneck, clipboard hugged to her chest. Faces RIGHT (Dex stands to her right)."""
    height = height or npc_height(0.93)
    W, Hc = 380, 620
    skin = (186, 120, 88)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=81)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.86, waist=0.8, hips=0.98, limbs=0.84, head=1.06, legs=1.04, neck=1.05, chest=0.8,
                        hand=0.92, foot=0.92),
             pose=dict(arm_n=24, fore_n=112, arm_f=-6, fore_f=14, leg_n=-6, shin_n=4, leg_f=7, shin_f=-3, lean=-2,
                       head_dx=0.8, head_dy=-0.5), seed=8)
    coat, coat_sh = (244, 244, 250), (176, 172, 214)
    hair, hair_sh, hair_hi = (58, 38, 92), (34, 20, 60), (130, 96, 190)
    teal = (30, 170, 170)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # wild storm-cloud hair behind everything
    rng = random.Random(3)
    puffs = []
    for k in range(13):
        a = math.radians(150 + k * 19)
        rr = r * rng.uniform(0.42, 0.58)
        puffs.append(ell(hx - r * 0.25 + math.cos(a) * r * 1.12, hy - ry * 0.05 + math.sin(a) * ry * 1.05, rr, rr * 0.9))
    puffs.append(ell(hx - r * 0.3, hy + ry * 0.1, r * 1.1, ry * 0.95))
    puffs.append(ell(hx - r * 0.9, hy + ry * 0.9, r * 0.5, r * 0.5))
    cloud = puffs[0]
    for p_ in puffs[1:]:
        cloud = cloud + p_
    c.ink(cloud, hair, lw=3.0, shade=0.55, sw=r * 0.5, scol=hair_sh, hi=0.45, hw=r * 0.25, hcol=hair_hi, rim=0.2,
          rcol=(190, 150, 255), wob=0.6)
    for k in range(7):
        a = math.radians(170 + k * 28)
        c.stroke([(hx - r * 0.2 + math.cos(a) * r * 0.7, hy + math.sin(a) * ry * 0.6),
                  (hx - r * 0.2 + math.cos(a + 0.3) * r * 1.4, hy + math.sin(a + 0.3) * ry * 1.25)], 1.8, hair_hi,
                 taper=(0.3, 0.7), opacity=0.6)
    # far arm, coat sleeve to the wrist, a pencil in the hand
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    wx, wy = b.P(*b.wrist_f)
    c.stroke([(wx - 4, wy + 6), (wx + 14, wy + 30)], 4.0, INK, taper=(0, 0))
    c.stroke([(wx - 4, wy + 6), (wx + 14, wy + 30)], 2.4, (250, 210, 60), taper=(0, 0))
    b.hand(False, "hold", col=shade_col(skin, 0.88))
    c.ink(b.sleeve(False, to_wrist=True, w0=9.0, w1=8.4, cuff=7.6), shade_col(coat, 0.8), lw=2.8, shade=0.4, scol=coat_sh)
    # legs: purple tights + chunky yellow sneakers
    def sneakers(bb, near):
        bb.shoe(near, (255, 214, 60) if near else (220, 180, 50), (250, 246, 236), "sneaker", length=1.0)
    legs(b, (110, 70, 160), w=(7.4, 5.0, 4.0), shoe=sneakers, skin=True)
    # back panel of the coat (behind the near leg), down to the knees
    hem = b.hip_y - 22
    coat_back = Sh([b.Ps([(-6.4, b.hip_y + 6), (5.6, b.hip_y + 6), (6.8, hem + 1), (-1.0, hem - 1.6), (-8.2, hem + 0.6)])])
    c.ink(coat_back, shade_col(coat, 0.86), lw=3.0, shade=0.3, scol=coat_sh)
    # torso: teal turtleneck under the coat
    c.ink(b.neck_shape(0.9), skin, lw=2.8, shade=0.6, sw=7)
    sy, sx = b.shoulder_y, b.lean_dx
    torso = Sh([b.torso_pts(slack=1.4, hem=b.hip_y + 2, flare=0.8, neck_open=1.0)])
    c.ink(torso, teal, lw=3.0, shade=0.5, sw=16, hi=0.3)
    c.ink(Sh([chaikin(b.Ps([(sx - 2.4, sy + 2.6), (sx + 0.4, sy + 1.6), (sx + 3.4, sy + 2.2), (sx + 3.6, sy - 0.6), (sx + 0.4, sy - 1.6),
                            (sx - 2.6, sy - 0.4)]), 1)]), hi_col(teal, 0.1), lw=2.4, shade=0.3)
    for k in range(3):
        yy = sy - 0.2 - k * 0.7
        c.stroke(b.Ps([(sx - 2.2, yy + 1.4), (sx + 3.4, yy + 1.2)]), 1.2, shade_col(teal, 0.6), taper=(0.2, 0.2), opacity=0.6)
    # the lab coat: two long front panels, open over the turtleneck, wide lapels
    back_panel = Sh([b.Ps([(b.sh_n[0] - 0.6, sy - 0.2), (sx - 0.6, sy + 0.4), (sx - 1.2, sy - 8), (sx * 0.4 - 1.6, b.hip_y + 4),
                            (-1.8, hem + 0.4), (-8.6, hem + 0.8), (-7.0, b.hip_y + 4), (b.sh_n[0] - 0.4, sy - 9)])])
    c.ink(back_panel, coat, lw=3.0, shade=0.45, sw=16, scol=coat_sh, hi=0.3, rim=0.15)
    front_panel = Sh([b.Ps([(sx + 2.6, sy + 0.6), (b.sh_f[0] + 0.6, sy - 0.6), (b.sh_f[0] + 1.8, sy - 6), (b.sh_f[0] + 1.6, sy - 12),
                             (sx * 0.6 + 6.4, b.hip_y + 6), (7.4, hem + 1.2), (2.6, hem), (sx * 0.5 + 3.0, b.hip_y + 6),
                             (sx + 3.6, sy - 9)])])
    c.ink(front_panel, coat, lw=3.0, shade=0.4, sw=12, scol=coat_sh, hi=0.35, rim=0.15)
    for pts in ([(sx - 0.6, sy + 0.6), (sx + 0.6, sy - 1.0), (sx - 0.2, sy - 8.6), (sx - 2.4, sy - 5.0)],
                [(sx + 2.6, sy + 0.8), (sx + 4.6, sy - 1.0), (sx + 3.8, sy - 9.0), (sx + 2.8, sy - 7.0)]):
        c.ink(Sh([b.Ps(pts)]), hi_col(coat, 0.1), lw=2.2, shade=0.3, scol=coat_sh)
    # pocket with pens, name badge, coffee stain
    px_, py_ = b.P(sx * 0.5 + 4.6, b.hip_y + 4)
    c.ink(rect(px_ - 16, py_ - 4, px_ + 12, py_ + 22), coat, lw=2.2, shade=0.3, scol=coat_sh)
    bpx, bpy = b.P(sx + 3.2, sy - 6.5)
    for k, col in enumerate(((220, 40, 60), (40, 90, 200), (40, 160, 90))):
        c.stroke([(bpx - 6 + k * 6, bpy + 2), (bpx - 6 + k * 6, bpy - 12)], 3.2, col, taper=(0, 0))
    c.ink(rect(bpx - 12, bpy, bpx + 12, bpy + 10), coat, lw=1.8, shade=0.2, scol=coat_sh)
    c.soft(ell(*b.P(5.2, b.hip_y - 10), 6, 5), (160, 110, 60), 0.4, 2)
    folds(c, [b.Ps([(-4, b.hip_y - 6), (-5, hem + 4)]), b.Ps([(5, b.hip_y - 2), (5.8, hem + 3)])], coat_sh, 1.8, 0.7)
    # head
    head = Sh([b.head_pts(jaw=0.94, chin=0.96, cheek=0.98)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 160, 140))
    fa = b.face_anchor()
    b.cheeks(fa["eye_n"][0] + r * 0.12, fa["eye_n"][1] + ry * 0.42, r * 0.28, (255, 110, 120), 0.35)
    b.eyes(iris=(110, 70, 40), look=(0.42, -0.05), lid=0.02, lower=0.08, lashes=1, size=1.1)
    b.brows(col=hair_sh, lift_n=0.22, lift_f=0.18, tilt_n=0.9, tilt_f=0.7, w=r * 0.12)
    b.nose("round", 0.95)
    b.mouth("worried", fa["mouth"][0], fa["mouth"][1] + ry * 0.02, r * 0.5, r * 0.3)
    b.ear(0.9)
    ex_, ey_ = fa["ear"]
    c.ink(ell(ex_ - r * 0.12, ey_ + r * 0.5, r * 0.09, r * 0.09), (60, 210, 220), lw=1.6, hi=0.5)
    # front hair: a frizzy fringe, a pencil stuck through it, goggles pushed up on top
    fringe = blob([(hx - r * 0.9, hy - ry * 0.1), (hx - r * 0.75, hy - ry * 0.85), (hx - r * 0.1, hy - ry * 1.12),
                   (hx + r * 0.55, hy - ry * 1.02), (hx + r * 1.02, hy - ry * 0.62), (hx + r * 0.95, hy - ry * 0.35),
                   (hx + r * 0.72, hy - ry * 0.5), (hx + r * 0.5, hy - ry * 0.32), (hx + r * 0.3, hy - ry * 0.52),
                   (hx + r * 0.05, hy - ry * 0.3), (hx - r * 0.2, hy - ry * 0.5), (hx - r * 0.45, hy - ry * 0.1)], 2)
    c.ink(fringe, hair, lw=3.0, shade=0.45, sw=r * 0.35, scol=hair_sh, hi=0.5, hw=r * 0.2, hcol=hair_hi)
    c.stroke([(hx - r * 1.3, hy - ry * 1.25), (hx - r * 0.2, hy - ry * 0.75)], 5.0, INK, taper=(0, 0))
    c.stroke([(hx - r * 1.3, hy - ry * 1.25), (hx - r * 0.2, hy - ry * 0.75)], 3.0, (250, 200, 60), taper=(0, 0))
    c.ink(ell(hx - r * 1.32, hy - ry * 1.26, 3.4, 3.4), (240, 120, 150), lw=1.4)
    gy = hy - ry * 0.98
    c.stroke([(hx - r * 1.05, gy + ry * 0.2), (hx - r * 0.2, gy - ry * 0.06), (hx + r * 0.6, gy - ry * 0.02)], r * 0.16, (255, 120, 40),
             taper=(0, 0))
    for gx_, gr in ((hx + r * 0.1, r * 0.3), (hx + r * 0.65, r * 0.22)):
        c.ink(ell(gx_, gy, gr, gr * 0.85), (120, 230, 230), lw=2.6, oc=INK, shade=0.3, hi=0.6, hw=3)
        c.ink(ell(gx_, gy, gr, gr * 0.85), (0, 0, 0, 0), lw=2.0, oc=(255, 120, 40), line_only=True, inner=-0.4)
    # near arm: clipboard hugged against the chest
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    wx, wy = b.P(*b.wrist_n)
    cb = Sh([rot_pts([(wx - 30, wy - 66), (wx + 22, wy - 66), (wx + 22, wy + 12), (wx - 30, wy + 12)], 12, wx, wy)])
    c.ink(cb, (170, 120, 70), lw=2.8, shade=0.4, hi=0.3)
    paper = Sh([rot_pts([(wx - 26, wy - 58), (wx + 18, wy - 58), (wx + 18, wy + 8), (wx - 26, wy + 8)], 12, wx, wy)])
    c.ink(paper, (252, 250, 240), lw=1.8, shade=0.2)
    for k in range(6):
        c.stroke(rot_pts([(wx - 20, wy - 46 + k * 9), (wx + 10 - (k * 7) % 14, wy - 46 + k * 9)], 12, wx, wy), 1.4, (90, 90, 150),
                 taper=(0, 0))
    c.ink(Sh([rot_pts([(wx - 12, wy - 72), (wx + 4, wy - 72), (wx + 4, wy - 62), (wx - 12, wy - 62)], 12, wx, wy)]), (180, 180, 196),
          lw=1.8, shade=0.3)
    c.ink(b.sleeve(True, to_wrist=True, w0=9.2, w1=8.6, cuff=7.8), coat, lw=3.0, shade=0.45, sw=10, scol=coat_sh, hi=0.3)
    b.hand(True, "hold", size=0.95, d=(0.4, -1.0), thumb=-1)
    return finish_sprite(c, name, flip=False)


def paint_sky(height=None, name="hs_sky_rivera.png"):
    """Sky Rivera, campus activist: striped beanie with a pompom, denim jacket covered in buttons, cargo pants,
    boots; one fist in the air, a megaphone in the other hand. Faces RIGHT (Dex stands to her right)."""
    height = height or npc_height(0.92)
    W, Hc = 400, 620
    skin = (226, 168, 128)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=91)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=0.84, hips=0.98, limbs=0.9, head=1.06, legs=1.0, neck=1.0, chest=0.7,
                        hand=0.95, foot=1.0),
             pose=dict(arm_n=10, fore_n=40, arm_f=150, fore_f=20, leg_n=-8, shin_n=3, leg_f=9, shin_f=-4, lean=-3,
                       head_dx=0.6, head_dy=0.4), seed=9)
    denim, denim_sh = (70, 110, 196), (40, 64, 140)
    cargo, cargo_sh = (110, 120, 76), (70, 76, 50)
    hair, hair_sh = (60, 36, 40), (34, 18, 26)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # short hair at the back of the neck
    c.ink(blob([(hx - r * 1.05, hy - ry * 0.2), (hx - r * 0.4, hy - ry * 0.2), (hx - r * 0.3, hy + ry * 0.7), (hx - r * 0.8, hy + ry * 0.95),
                (hx - r * 1.15, hy + ry * 0.6)], 2), hair, lw=3.0, shade=0.4, sw=r * 0.3, scol=hair_sh, hi=0.3)
    # far arm raised in a fist (sleeve to the wrist)
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    b.hand(False, "fist", col=shade_col(skin, 0.88), d=(0.15, -1.0))
    c.ink(b.sleeve(False, to_wrist=True, w0=9.0, w1=8.4, cuff=7.6), shade_col(denim, 0.82), lw=2.8, shade=0.4, scol=denim_sh)
    # legs: baggy cargo pants with pockets + boots
    def boots(bb, near):
        bb.shoe(near, (70, 50, 50) if near else (56, 40, 42), (40, 30, 30), "boot", length=1.0)
        an = bb.ankle_n if near else bb.ankle_f
        for k in range(3):
            c.stroke(bb.Ps([(an[0] - 1.6, an[1] + 2 + k * 2.6), (an[0] + 2.4, an[1] + 2.4 + k * 2.6)]), 1.4, (220, 200, 160), taper=(0.1, 0.1))
    legs(b, cargo, w=(10.0, 7.4, 7.0), scol=cargo_sh, shoe=boots)
    for near in (True,):
        kn = b.knee_n
        c.ink(Sh([b.Ps([(kn[0] - 3.2, kn[1] + 8), (kn[0] + 2.6, kn[1] + 8), (kn[0] + 2.8, kn[1] + 1.6), (kn[0] - 3.0, kn[1] + 1.6)])]), cargo,
              lw=2.2, shade=0.4, scol=cargo_sh)
        c.stroke(b.Ps([(kn[0] - 3.0, kn[1] + 7), (kn[0] + 2.6, kn[1] + 7)]), 1.6, cargo_sh, taper=(0, 0))
    # torso: striped tee under the cropped jacket
    c.ink(b.neck_shape(0.95), skin, lw=2.8, shade=0.6, sw=7)
    sy, sx = b.shoulder_y, b.lean_dx
    tee = Sh([b.torso_pts(slack=0.6, hem=b.hip_y - 2, flare=0.6, neck_open=1.1)])
    c.ink(tee, (250, 246, 236), lw=3.0, shade=0.4, sw=14)
    clip_draw(c, tee, lambda t: [t.stroke([(0, yy), (W, yy)], 4.0, (220, 60, 80), taper=(0, 0)) for yy in np.arange(0, Hc, 11)])
    c.ink(tee, (0, 0, 0, 0), lw=3.0, line_only=True)
    jacket_b = Sh([b.Ps([(b.sh_n[0] - 0.8, sy - 0.4), (sx - 0.4, sy + 0.8), (sx - 0.8, sy - 10), (sx * 0.4 - 1.0, b.hip_y + 2),
                          (-6.4, b.hip_y + 2), (b.sh_n[0] - 0.6, sy - 10)])])
    c.ink(jacket_b, denim, lw=3.0, shade=0.5, sw=14, scol=denim_sh, hi=0.3, tex=0.14)
    jacket_f = Sh([b.Ps([(sx + 3.0, sy + 0.8), (b.sh_f[0] + 0.8, sy - 0.6), (b.sh_f[0] + 1.8, sy - 6), (b.sh_f[0] + 1.6, sy - 12),
                          (sx * 0.6 + 6.0, b.hip_y + 2), (sx * 0.5 + 3.6, b.hip_y + 2), (sx + 3.6, sy - 10)])])
    c.ink(jacket_f, denim, lw=3.0, shade=0.45, sw=10, scol=denim_sh, hi=0.35, tex=0.14)
    for jp in (jacket_b, jacket_f):
        bx0, by0, bx1, by1 = jp.bbox()
        c.ink(rect(bx0 - 4, by1 - 12, bx1 + 4, by1 + 4), shade_col(denim, 0.9), lw=2.2, shade=0.3, clip=jp)
    for pts in ([(sx - 0.4, sy + 0.8), (sx + 0.8, sy - 0.8), (sx + 0.2, sy - 6.6), (sx - 2.0, sy - 4.0)],
                [(sx + 3.0, sy + 0.8), (sx + 5.2, sy - 0.6), (sx + 4.0, sy - 6.8), (sx + 3.0, sy - 5.0)]):
        c.ink(Sh([b.Ps(pts)]), hi_col(denim, 0.15), lw=2.2, shade=0.3, scol=denim_sh)
    rngb = random.Random(5)
    btn_cols = [(255, 220, 60), (255, 90, 160), (90, 230, 200), (250, 250, 240), (160, 110, 255), (255, 140, 60)]
    for k, (ux, uy) in enumerate(((-4.2, sy - 6), (-2.0, sy - 12), (-5.0, sy - 16), (-2.4, sy - 20), (5.6, sy - 5), (6.2, sy - 11),
                                  (4.8, sy - 17), (-4.8, sy - 24))):
        bx_, by_ = b.P(ux + sx * 0.6, uy)
        rr = rngb.uniform(4.0, 6.0)
        col = btn_cols[k % len(btn_cols)]
        c.ink(ell(bx_, by_, rr, rr), col, lw=1.6, shade=0.3, hi=0.6, hw=1.5)
        if k % 3 == 0:
            c.ink(ell(bx_, by_, rr * 0.45, rr * 0.45), (220, 40, 60), lw=0)
        elif k % 3 == 1:
            c.stroke([(bx_ - rr * 0.5, by_), (bx_ + rr * 0.5, by_)], 1.2, INK, taper=(0, 0))
    folds(c, [b.Ps([(-3, b.hip_y + 10), (-1.5, b.hip_y + 4)]), b.Ps([(4.5, b.hip_y + 12), (4, b.hip_y + 5)])], denim_sh, 1.6, 0.6)
    # head
    head = Sh([b.head_pts(jaw=1.0, chin=1.0, cheek=1.0)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 160, 140))
    fa = b.face_anchor()
    rng = random.Random(4)
    ex, ey = fa["eye_n"]
    for _ in range(8):
        c.ink(ell(ex + rng.uniform(-r * 0.2, r * 0.8), ey + ry * rng.uniform(0.3, 0.46), 1.1, 1.1), (180, 100, 70), lw=0, shade=0,
              hi=0, ao=0, tex=0, wob=0)
    b.cheeks(ex + r * 0.12, ey + ry * 0.44, r * 0.28, opacity=0.35)
    b.eyes(iris=(70, 120, 70), look=(0.4, -0.02), lid=0.2, size=1.02, lashes=1)
    b.brows(col=hair_sh, lift_n=0.0, lift_f=0.0, tilt_n=-0.8, tilt_f=-0.7, w=r * 0.14)
    b.nose("button", 1.0)
    b.mouth("open", fa["mouth"][0] + r * 0.02, fa["mouth"][1] + ry * 0.04, r * 0.56, r * 0.44)
    b.ear(0.95)
    ex_, ey_ = fa["ear"]
    for k in range(3):
        c.ink(ell(ex_ - r * 0.25 + k * r * 0.06, ey_ - r * 0.2 + k * r * 0.2, 2.2, 2.2), (250, 220, 90), lw=1.0)
    # bangs + striped beanie with pompom
    c.ink(blob([(hx + r * 0.05, hy - ry * 0.62), (hx + r * 0.95, hy - ry * 0.62), (hx + r * 1.0, hy - ry * 0.3), (hx + r * 0.7, hy - ry * 0.38),
                (hx + r * 0.5, hy - ry * 0.24), (hx + r * 0.3, hy - ry * 0.4)], 2), hair, lw=2.6, shade=0.3, scol=hair_sh, hi=0.3)
    beanie = blob([(hx - r * 1.12, hy - ry * 0.12), (hx - r * 1.08, hy - ry * 0.9), (hx - r * 0.5, hy - ry * 1.42), (hx + r * 0.25, hy - ry * 1.5),
                   (hx + r * 0.9, hy - ry * 1.12), (hx + r * 1.1, hy - ry * 0.55), (hx + r * 0.2, hy - ry * 0.62),
                   (hx - r * 0.5, hy - ry * 0.45)], 2)
    c.ink(beanie, (240, 180, 50), lw=3.0, shade=0.5, sw=r * 0.4, hi=0.35, rim=0.15)
    clip_draw(c, beanie, lambda t: [t.stroke([(hx - r * 2, yy + (hx - r * 2 - hx) * 0.15), (hx + r * 2, yy - r * 0.3)], r * 0.16,
                                             (220, 50, 110), taper=(0, 0)) for yy in np.arange(hy - ry * 1.5, hy - ry * 0.5, r * 0.36)])
    c.ink(beanie, (0, 0, 0, 0), lw=3.0, line_only=True)
    cuff = blob([(hx - r * 1.18, hy - ry * 0.05), (hx - r * 1.12, hy - ry * 0.5), (hx + r * 0.2, hy - ry * 0.78), (hx + r * 1.14, hy - ry * 0.7),
                 (hx + r * 1.12, hy - ry * 0.42), (hx + r * 0.2, hy - ry * 0.48), (hx - r * 0.6, hy - ry * 0.25)], 2)
    c.ink(cuff, (200, 140, 40), lw=2.8, shade=0.4, hi=0.3)
    for k in range(9):
        t = k / 8
        a = (hx - r * 1.1 + t * r * 2.2, hy - ry * (0.3 + t * 0.35))
        c.stroke([a, (a[0], a[1] - ry * 0.25)], 1.2, shade_col((200, 140, 40), 0.6), taper=(0, 0), opacity=0.7)
    pp = ell(hx - r * 0.2, hy - ry * 1.6, r * 0.34, r * 0.32)
    c.ink(pp, (220, 50, 110), lw=2.6, shade=0.4, hi=0.4, wob=1.4)
    # near arm: megaphone held down at the hip, bell forward
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, to_wrist=True, w0=9.4, w1=8.8, cuff=8.0), denim, lw=3.0, shade=0.45, sw=10, scol=denim_sh, hi=0.3)
    wx, wy = b.P(*b.wrist_n)
    megaphone(c, wx - 6, wy + 14, 0.95, ang=8)
    b.hand(True, "fist", size=0.95)
    return finish_sprite(c, name, flip=False)


def reach(b, near, target, bend=1):
    """Re-pose one arm of Body b so its wrist lands on target (body units). Grid IK; bend=+1 elbow below/behind."""
    sh = b.sh_n if near else b.sh_f
    ua, fa = 17.0 * b.b.get("arms", 1.0), 14.6 * b.b.get("arms", 1.0)
    best = None
    for a in range(-40, 181, 2):
        e = b._ang(sh, a, ua)
        for f in range(0, 171, 2):
            w = b._ang(e, a + f * bend, fa)
            d = math.hypot(w[0] - target[0], w[1] - target[1])
            if best is None or d < best[0] - 1e-9:
                best = (d, a, f * bend)
    _, a, f = best
    if near:
        b.p["arm_n"], b.p["fore_n"] = a, f
    else:
        b.p["arm_f"], b.p["fore_f"] = a, f
    b._joints()
    return best[0]


def paint_dot(height=None, name="hs_dot_pruitt.png"):
    """Dot Pruitt, night custodian and retired roller-derby legend: red bandana over grey curls, navy overalls
    with a name patch, rolled sleeves, knee pads, high-tops, a ring of keys, both hands on a mop. Faces RIGHT."""
    height = height or npc_height(0.88)
    W, Hc = 440, 600
    skin = (232, 176, 138)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=101)
    b = Body(c, 170, Hc - 14, height, skin=skin,
             build=dict(shoulders=1.12, waist=1.2, hips=1.18, limbs=1.16, head=1.08, belly=1.8, legs=0.92, neck=0.9, chest=0.8,
                        hand=1.05, foot=1.05),
             pose=dict(arm_n=34, fore_n=64, arm_f=30, fore_f=56, leg_n=-7, shin_n=3, leg_f=8, shin_f=-3, lean=3,
                       head_dx=0.6), seed=10)
    navy, navy_sh = (56, 78, 150), (32, 44, 100)
    shirt = (250, 214, 110)
    grey, grey_sh = (226, 224, 232), (160, 156, 176)
    red = (214, 44, 56)
    MOP_TOP, MOP_BOT = (19.0, 76.0), (33.0, 12.0)
    def on_handle(y):
        t = (MOP_TOP[1] - y) / (MOP_TOP[1] - MOP_BOT[1])
        return (MOP_TOP[0] + (MOP_BOT[0] - MOP_TOP[0]) * t, y)
    reach(b, True, on_handle(64))
    reach(b, False, on_handle(50))
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm (behind the torso)
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    c.ink(b.sleeve(False, 0.5, 9.4, 9.0), shade_col(shirt, 0.82), lw=2.8, shade=0.4)
    # legs: overalls + knee pads + red high-tops
    def hightops(bb, near):
        bb.shoe(near, red if near else shade_col(red, 0.85), (250, 246, 236), "boot", length=1.0)
        an = bb.ankle_n if near else bb.ankle_f
        c.ink(ell(*bb.P(an[0] - 0.6, an[1] + 3), 6, 6), (250, 246, 236), lw=1.6)
    legs(b, navy, w=(10.4, 8.0, 7.4), scol=navy_sh, shoe=hightops)
    for near in (False, True):
        kn = b.knee_n if near else b.knee_f
        c.ink(rrect(*b.P(kn[0] - 4.4, kn[1] + 3.8), *b.P(kn[0] + 4.0, kn[1] - 3.6), 8), (40, 36, 46) if near else (34, 30, 40),
              lw=2.8, shade=0.4, hi=0.5, hw=3)
        c.stroke(b.Ps([(kn[0] - 3.4, kn[1] + 0.2), (kn[0] + 3.2, kn[1] + 0.4)]), 1.6, (90, 90, 110), taper=(0.2, 0.2))
    # torso: yellow work shirt, overall bib + straps, belly
    c.ink(b.neck_shape(1.0), skin, lw=2.8, shade=0.6, sw=7)
    sy, sx = b.shoulder_y, b.lean_dx
    torso = Sh([b.torso_pts(slack=1.2, hem=b.hip_y + 3, flare=1.0, neck_open=1.0)])
    c.ink(torso, shirt, lw=3.0, shade=0.5, sw=18, hi=0.3)
    c.ink(Sh([b.Ps([(sx - 1.6, sy + 1.6), (sx + 3.0, sy + 1.2), (sx + 1.4, sy - 4.0)])]), skin, lw=2.2, shade=0.4)
    for pts in ([(sx - 3.2, sy + 2.0), (sx - 0.2, sy + 0.4), (sx + 1.2, sy - 4.2), (sx - 1.8, sy - 3.0)],
                [(sx + 2.6, sy + 1.2), (sx + 6.0, sy + 0.4), (sx + 5.0, sy - 3.0), (sx + 1.4, sy - 4.4)]):
        c.ink(Sh([b.Ps(pts)]), hi_col(shirt, 0.1), lw=2.2, shade=0.3)
    bib = Sh([chaikin(b.Ps([(sx * 0.7 - 3.4, sy - 9), (sx * 0.7 + 6.0, sy - 9), (sx * 0.5 + 6.8 + 1.4, b.hip_y + 6),
                            (5.6 * b.b["hips"], b.hip_y - 1), (-5.8 * b.b["hips"], b.hip_y - 1), (sx * 0.4 - 6.2, b.hip_y + 6)]), 1)])
    c.ink(bib, navy, lw=3.0, shade=0.5, sw=16, scol=navy_sh, hi=0.3, tex=0.12)
    for (ux, top) in ((sx * 0.7 - 2.6, b.sh_n[0] + 1.6), (sx * 0.7 + 5.2, b.sh_f[0] - 0.4)):
        c.ink(limb(b.Ps([(top, sy + 0.2), (ux, sy - 9.4)]), [2.6 * b.u, 2.4 * b.u], smooth=0), navy, lw=2.6, shade=0.4, scol=navy_sh)
        c.ink(ell(*b.P(ux, sy - 9.2), 4.4, 4.4), (236, 200, 90), lw=1.6, hi=0.6)
    px_, py_ = b.P(sx * 0.6 + 1.6, sy - 14)
    c.ink(rrect(px_ - 20, py_ - 10, px_ + 20, py_ + 10, 5), (250, 246, 236), lw=2.0, shade=0.2)
    c.text(px_, py_, "DOT", 11, red)
    # belt with a big ring of keys
    c.ink(Sh([b.Ps([(-6.4, b.hip_y + 1.2), (6.0 + 0.6, b.hip_y + 1.2), (6.2, b.hip_y - 1.6), (-6.4, b.hip_y - 1.6)])]), (90, 56, 40), lw=2.2)
    kx, ky = b.P(-4.0, b.hip_y - 3.2)
    c.ink(ell(kx, ky, 9, 9), (0, 0, 0, 0), lw=2.6, oc=(200, 200, 210), line_only=True)
    for k, a in enumerate((-40, -10, 20, 50, 80)):
        ar = math.radians(a + 90)
        x2, y2 = kx + math.cos(ar) * 22, ky + math.sin(ar) * 22
        c.stroke([(kx + math.cos(ar) * 8, ky + math.sin(ar) * 8), (x2, y2)], 4.0, INK, taper=(0, 0))
        c.stroke([(kx + math.cos(ar) * 8, ky + math.sin(ar) * 8), (x2, y2)], 2.2, (230, 200, 90) if k % 2 else (200, 200, 214), taper=(0, 0))
    # head: round, weathered, laugh lines, smirk
    head = Sh([b.head_pts(jaw=1.12, chin=1.05, cheek=1.06, cranium=1.02)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.35, rim=0.15, rcol=(255, 160, 140))
    fa = b.face_anchor()
    ex, ey = fa["eye_n"]
    b.cheeks(ex + r * 0.12, ey + ry * 0.42, r * 0.3, (255, 110, 110), 0.4)
    b.eyes(iris=(90, 120, 170), look=(0.38, 0.05), lid=0.36, lower=0.12, size=0.95)
    b.brows(col=(150, 146, 166), lift_n=0.04, lift_f=0.0, tilt_n=-0.3, tilt_f=-0.5, w=r * 0.14)
    for k in range(3):       # crow's feet
        c.stroke([(ex - r * 0.36, ey + k * r * 0.1 - r * 0.06), (ex - r * 0.52, ey + k * r * 0.14 - r * 0.12)], 1.3,
                 shade_col(skin, 0.6), taper=(0.2, 0.2))
    mx, my = fa["mouth"]
    c.stroke([(mx - r * 0.42, my - ry * 0.14), (mx - r * 0.5, my + ry * 0.06)], 1.4, shade_col(skin, 0.6), taper=(0.2, 0.2))
    b.nose("round", 1.1)
    b.mouth("smirk", mx, my + ry * 0.02, r * 0.5, r * 0.32)
    b.ear(1.0)
    # grey curls peeking out + red polka-dot bandana tied at the back
    for k in range(7):
        a = math.radians(160 + k * 18)
        c.ink(ell(hx + math.cos(a) * r * 0.98, hy + math.sin(a) * ry * 0.7 + ry * 0.12, r * 0.2, r * 0.18), grey, lw=2.2, shade=0.4,
              scol=grey_sh, hi=0.3)
    band = blob([(hx - r * 1.08, hy - ry * 0.05), (hx - r * 1.0, hy - ry * 0.8), (hx - r * 0.3, hy - ry * 1.12), (hx + r * 0.6, hy - ry * 1.02),
                 (hx + r * 1.05, hy - ry * 0.55), (hx + r * 0.6, hy - ry * 0.5), (hx, hy - ry * 0.42), (hx - r * 0.6, hy - ry * 0.18)], 2)
    c.ink(band, red, lw=3.0, shade=0.5, sw=r * 0.4, hi=0.35, rim=0.15)
    rngd = random.Random(2)
    bx0, by0, bx1, by1 = band.bbox()
    for _ in range(20):
        c.ink(ell(rngd.uniform(bx0, bx1), rngd.uniform(by0, by1), 2.6, 2.6), (250, 246, 236), lw=0, clip=band)
    c.ink(band, (0, 0, 0, 0), lw=3.0, line_only=True)
    kx_, ky_ = hx - r * 1.05, hy - ry * 0.25
    for (dx, dy) in ((-r * 0.65, r * 0.3), (-r * 0.5, r * 0.75)):
        c.ink(blob([(kx_, ky_ - 4), (kx_ + dx, ky_ + dy - 6), (kx_ + dx * 1.1, ky_ + dy + 6), (kx_, ky_ + 6)], 1), red, lw=2.4, shade=0.4)
    c.ink(ell(kx_, ky_, r * 0.16, r * 0.14), shade_col(red, 0.8), lw=2.2)
    # mop: handle held across the body, head on the floor in front
    mtop = b.P(*MOP_TOP)
    mbot = b.P(*MOP_BOT)
    c.stroke([mtop, mbot], 9, INK, taper=(0, 0))
    c.stroke([mtop, mbot], 5.0, (190, 150, 100), taper=(0, 0))
    mx_, my_ = mbot
    c.ink(rect(mx_ - 16, my_ - 8, mx_ + 16, my_ + 2), (200, 200, 214), lw=2.2, shade=0.3)
    strands = Sh()
    for k in range(9):
        a = math.radians(-70 + k * 18)
        strands = strands + limb([(mx_ - 12 + k * 3, my_), (mx_ + math.sin(a) * 36, my_ + 26 + math.cos(a) * 4)], [7, 6], smooth=0)
    c.ink(strands, (214, 210, 200), lw=2.4, shade=0.45, sw=6, hi=0.3)
    # near arm: rolled sleeve, both hands on the handle
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    c.ink(b.sleeve(True, 0.5, 8.4, 7.8), shirt, lw=3.0, shade=0.45, sw=10, hi=0.3)
    sl = b.sleeve(True, 0.5, 8.4, 7.8)
    bx0, by0, bx1, by1 = sl.bbox()
    el = b.P(*b.elbow_n)
    c.ink(ell((b.P(*b.sh_n)[0] * 0.4 + el[0] * 0.6), (b.P(*b.sh_n)[1] * 0.4 + el[1] * 0.6), 10, 6, 60), hi_col(shirt, 0.1), lw=2.2,
          shade=0.3)
    # tattoo: a tiny roller skate on the forearm
    fx_, fy_ = (el[0] * 0.5 + b.P(*b.wrist_n)[0] * 0.5, el[1] * 0.5 + b.P(*b.wrist_n)[1] * 0.5)
    c.ink(rect(fx_ - 5, fy_ - 4, fx_ + 5, fy_ + 2), (60, 90, 170), lw=0, opacity=0.8)
    for dx in (-4, 4):
        c.ink(ell(fx_ + dx, fy_ + 4, 2, 2), (60, 90, 170), lw=0, opacity=0.8)
    # hands gripping the handle at the wrists
    b.hand(False, "fist", col=shade_col(skin, 0.9), d=(mbot[0] - mtop[0], mbot[1] - mtop[1]))
    b.hand(True, "fist", d=(mbot[0] - mtop[0], mbot[1] - mtop[1]))
    return finish_sprite(c, name, flip=False)


def paint_crumb(height=None, name="hs_professor_crumb.png"):
    """Professor Thaddeus Crumb: tall, stooped, tweed jacket with elbow patches over a mustard sweater vest,
    bow tie, bald dome with white tufts, enormous cloud eyebrows, glasses pushed up on his forehead; a red pen
    raised to make a point and a NO mug. Drawn facing right and flipped to face LEFT (toward Dex)."""
    height = height or npc_height(1.02)
    W, Hc = 380, 640
    skin = (248, 212, 186)
    c = Canvas2(W, Hc, light=(0.42, -0.9), lw=3.0, seed=111)
    b = Body(c, 160, Hc - 14, height, skin=skin,
             build=dict(shoulders=0.92, waist=0.92, hips=0.94, limbs=0.86, head=1.0, belly=0.6, legs=1.08, neck=1.1, chest=0.2,
                        hand=0.95, foot=1.08),
             pose=dict(arm_n=20, fore_n=62, arm_f=96, fore_f=66, leg_n=-3, shin_n=2, leg_f=5, shin_f=-1, lean=6,
                       head_dx=2.0, head_dy=-2.2), seed=11)
    tweed, tweed_sh = (150, 108, 72), (96, 66, 52)
    vest = (226, 176, 60)
    cord, cord_sh = (110, 84, 64), (74, 54, 46)
    grey, grey_sh = (246, 246, 250), (176, 176, 200)
    r, ry = b.r, b.ry
    hx, hy = b.hx, b.hy
    # far arm raised in front of him: red pen pointed at the ceiling to make a point
    c.ink(b.arm_shape(False), shade_col(skin, 0.88), lw=2.8, shade=0.4)
    sl = b.sleeve(False, to_wrist=True, w0=8.6, w1=8.0, cuff=7.2)
    c.ink(sl, shade_col(tweed, 0.82), lw=2.8, shade=0.4, scol=tweed_sh)
    gp = b.hand(False, "fist", col=shade_col(skin, 0.88), size=0.95, d=(0.2, -1.0))
    c.stroke([(gp[0] - 2, gp[1] + 8), (gp[0] + 5, gp[1] - 32)], 5.0, INK, taper=(0, 0))
    c.stroke([(gp[0] - 2, gp[1] + 8), (gp[0] + 5, gp[1] - 32)], 3.0, (220, 40, 50), taper=(0, 0))
    b.hand(False, "fist", col=shade_col(skin, 0.88), size=0.95, d=(0.2, -1.0))
    # legs: corduroy trousers, brogues
    def brogues(bb, near):
        bb.shoe(near, (110, 60, 40) if near else (90, 50, 36), (60, 36, 26), "shoe", length=1.05)
        an = bb.ankle_n if near else bb.ankle_f
        for k in range(4):
            c.ink(ell(*bb.P(an[0] + 3 + k * 1.6, an[1] - 1.6 + k * 0.2), 1.0, 1.0), (200, 150, 110), lw=0)
    legs(b, cord, w=(8.2, 5.8, 5.2), scol=cord_sh, shoe=brogues)
    for near in (False, True):
        sh = b.leg_shape(near, w=(8.2, 5.8, 5.2))
        bx0, by0, bx1, by1 = sh.bbox()
        clip_draw(c, sh, lambda t: [t.stroke([(x, by0), (x + 4, by1)], 1.2, cord_sh, taper=(0, 0), opacity=0.5)
                                    for x in np.arange(bx0, bx1, 6)])
    # torso: cream shirt, mustard vest, tweed jacket, red bow tie
    c.ink(b.neck_shape(0.85), skin, lw=2.8, shade=0.6, sw=7)
    sy, sx = b.shoulder_y, b.lean_dx
    jacket = Sh([b.torso_pts(slack=1.2, hem=b.hip_y - 6, flare=1.4, neck_open=1.1)])
    c.ink(jacket, tweed, lw=3.0, shade=0.5, sw=16, scol=tweed_sh, hi=0.3, tex=0.2)
    rngt = random.Random(6)
    bx0, by0, bx1, by1 = jacket.bbox()
    clip_draw(c, jacket, lambda t: ([t.stroke([(x, by0), (x + 30, by1)], 1.2, tweed_sh, taper=(0, 0), opacity=0.35) for x in np.arange(bx0 - 40, bx1, 7)] +
                                    [t.stroke([(bx0, y), (bx1, y - 20)], 1.2, hi_col(tweed, 0.3), taper=(0, 0), opacity=0.3) for y in np.arange(by0, by1 + 20, 9)]))
    c.ink(jacket, (0, 0, 0, 0), lw=3.0, line_only=True)
    front = Sh([b.Ps([(sx - 1.0, sy + 1.6), (sx + 3.4, sy + 1.2), (sx + 4.2, b.hip_y + 2), (sx * 0.5 + 3.4, b.hip_y - 3), (sx * 0.5 - 0.6, b.hip_y - 3),
                      (sx - 0.2, b.hip_y + 2)])])
    c.ink(front, vest, lw=2.4, shade=0.4, hi=0.3)
    clip_draw(c, front, lambda t: [t.stroke([(x, 0), (x - 30, Hc)], 1.4, shade_col(vest, 0.7), taper=(0, 0), opacity=0.4) for x in np.arange(0, W + 40, 8)])
    c.ink(Sh([b.Ps([(sx - 1.0, sy + 1.6), (sx + 3.4, sy + 1.2), (sx + 1.6, sy - 5)])]), (250, 244, 226), lw=2.2, shade=0.3)
    for k in range(3):
        c.ink(ell(*b.P(sx * 0.7 + 2.4, sy - 8 - k * 4), 1.8, 1.8), (120, 80, 30), lw=1.0)
    for pts in ([(sx - 2.6, sy + 2.0), (sx - 0.4, sy + 0.8), (sx + 0.6, b.hip_y + 4), (sx - 2.2, sy - 6)],
                [(sx + 3.2, sy + 1.6), (sx + 6.0, sy + 0.6), (sx + 4.8, sy - 6), (sx + 4.2, b.hip_y + 4)]):
        c.ink(Sh([b.Ps(pts)]), hi_col(tweed, 0.08), lw=2.2, shade=0.35, scol=tweed_sh)
    bt = b.P(sx + 1.2, sy - 0.6)
    c.ink(Sh([[(bt[0] - 12, bt[1] - 7), (bt[0], bt[1] - 1), (bt[0] - 12, bt[1] + 6)]]), (210, 40, 50), lw=2.2, shade=0.3)
    c.ink(Sh([[(bt[0] + 12, bt[1] - 7), (bt[0], bt[1] - 1), (bt[0] + 12, bt[1] + 6)]]), (210, 40, 50), lw=2.2, shade=0.3)
    c.ink(ell(bt[0], bt[1] - 0.5, 3.4, 3.6), (180, 30, 40), lw=1.8)
    pk = b.P(b.sh_f[0] - 0.4, sy - 8)
    c.ink(Sh([[(pk[0] - 6, pk[1]), (pk[0] + 6, pk[1]), (pk[0] + 3, pk[1] - 8), (pk[0] - 2, pk[1] - 6)]]), (250, 250, 250), lw=1.4)
    folds(c, [b.Ps([(-3.5, b.hip_y + 6), (-2.0, b.hip_y + 1)]), b.Ps([(4.0, b.hip_y + 8), (3.6, b.hip_y + 2)])], tweed_sh, 1.6, 0.6)
    # head: long face, bald dome, white side tufts, long nose
    head = Sh([b.head_pts(jaw=0.92, chin=1.08, cheek=0.94, cranium=1.06, chin_drop=1.12)])
    c.ink(head, skin, lw=3.0, shade=0.5, sw=r * 0.45, scol=shade_col(skin, 0.74), hi=0.4, hw=r * 0.25, rim=0.15, rcol=(255, 170, 160))
    c.ink(ell(hx - r * 0.1, hy - ry * 0.62, r * 0.32, ry * 0.12, -10), (255, 246, 230), lw=0, shade=0, hi=0, ao=0, opacity=0.6)   # shine
    fa = b.face_anchor()
    b.ear(1.0)
    for k, (dx, dy) in enumerate(((-0.95, 0.05), (-1.12, 0.35), (-0.9, 0.62))):
        c.ink(ell(hx + dx * r, hy + dy * ry, r * 0.3, r * 0.22, 20 * k), grey, lw=2.4, shade=0.4, scol=grey_sh, hi=0.4, wob=1.0)
    ex, ey = fa["eye_n"]
    b.cheeks(ex + r * 0.1, ey + ry * 0.44, r * 0.26, (255, 120, 120), 0.3)
    b.eyes(iris=(90, 110, 150), look=(0.45, 0.05), lid=0.46, lower=0.1, size=0.95, tilt=-0.08)
    # enormous cloud eyebrows
    for (bx_, by_, s_) in ((fa["brow_n"][0], fa["brow_n"][1] - ry * 0.06, 1.0), (fa["brow_f"][0], fa["brow_f"][1] - ry * 0.04, 0.72)):
        cl = Sh()
        for k in range(4):
            cl = cl + ell(bx_ - r * 0.28 * s_ + k * r * 0.18 * s_, by_ - (k % 2) * r * 0.06 + (k == 0) * r * 0.06, r * 0.16 * s_, r * 0.13 * s_)
        c.ink(cl, grey, lw=2.4, shade=0.4, scol=grey_sh, hi=0.4, wob=0.8)
    b.nose("long", 1.35)
    b.mouth("frown", fa["mouth"][0] + r * 0.04, fa["mouth"][1] + ry * 0.06, r * 0.42, r * 0.26)
    c.stroke([(fa["mouth"][0] - r * 0.3, fa["mouth"][1] - ry * 0.2), (fa["mouth"][0] - r * 0.36, fa["mouth"][1] + ry * 0.08)], 1.4,
             shade_col(skin, 0.6), taper=(0.2, 0.2))
    # glasses pushed up on the forehead
    gy = hy - ry * 0.62
    for gx_, gr in ((hx + r * 0.22, r * 0.3), (hx + r * 0.8, r * 0.2)):
        c.ink(ell(gx_, gy, gr, gr * 0.8), (220, 236, 250, 120), lw=2.6, oc=(60, 40, 30), shade=0, hi=0.5, hw=2)
    c.stroke([(hx + r * 0.52, gy), (hx + r * 0.6, gy)], 2.4, (60, 40, 30), taper=(0, 0))
    c.stroke([(hx - r * 0.08, gy), (hx - r * 0.5, gy + ry * 0.2)], 2.4, (60, 40, 30), taper=(0, 0))
    # near arm: holding the NO mug in front of his vest, elbow patch
    c.ink(b.arm_shape(True), skin, lw=3.0, shade=0.5)
    sl = b.sleeve(True, to_wrist=True, w0=9.0, w1=8.4, cuff=7.6)
    c.ink(sl, tweed, lw=3.0, shade=0.5, sw=10, scol=tweed_sh, hi=0.3, tex=0.2)
    el = b.P(*b.elbow_n)
    c.ink(ell(el[0], el[1], 9, 12, 30), (110, 76, 50), lw=2.2, shade=0.3)
    wx, wy = b.P(*b.wrist_n)
    wx += 22
    mug = rrect(wx - 4, wy - 14, wx + 34, wy + 28, 5)
    c.ink(mug, (250, 246, 236), lw=2.8, shade=0.4, sw=10, hi=0.3)
    c.ink(ell(wx + 15, wy - 14, 19, 5), (90, 50, 30), lw=2.0)
    c.label(wx + 15, wy + 8, "NO", 13, (200, 30, 40), "Black", mirror=True)
    c.stroke([(wx - 4, wy - 4), (wx - 14, wy + 2), (wx - 14, wy + 14), (wx - 4, wy + 18)], 4.0, INK, taper=(0, 0))
    b.hand(True, "hold", d=(1.0, 0.1))
    return finish_sprite(c, name, flip=True)


# =========================================================================== prop sprites
def paint_pigeon(name="hs_pigeon.png"):
    """A very large, very unimpressed pigeon, puffed up on the feeder. Drawn facing right, flipped to face LEFT."""
    c = Canvas2(150, 120, light=(0.42, -0.9), lw=2.8, seed=121)
    body, body_sh = (150, 150, 176), (96, 94, 128)
    x, y = 70, 104          # feet
    # tail
    c.ink(Sh([[(x - 30, y - 34), (x - 66, y - 28), (x - 64, y - 16), (x - 26, y - 22)]]), shade_col(body, 0.8), lw=2.6, shade=0.3)
    for k in range(2):
        c.stroke([(x - 62, y - 26 + k * 6), (x - 34, y - 28 + k * 4)], 1.4, INK_SOFT, taper=(0.2, 0.2), opacity=0.6)
    # body (puffed chest)
    bd = blob([(x - 38, y - 30), (x - 30, y - 52), (x - 4, y - 62), (x + 24, y - 56), (x + 34, y - 36), (x + 22, y - 14), (x - 2, y - 8),
               (x - 26, y - 14)], 2)
    c.ink(bd, body, lw=2.8, shade=0.5, sw=16, scol=body_sh, hi=0.35, rim=0.2)
    # wing with two dark bars
    wg = blob([(x - 30, y - 44), (x - 4, y - 50), (x + 12, y - 38), (x + 4, y - 24), (x - 22, y - 22), (x - 36, y - 28)], 2)
    c.ink(wg, shade_col(body, 0.88), lw=2.4, shade=0.4, scol=body_sh, hi=0.25)
    for k in range(2):
        c.stroke([(x - 22 + k * 4, y - 40 + k * 8), (x + 2 + k * 2, y - 40 + k * 8)], 3.0, (60, 56, 80), taper=(0.2, 0.3))
    # iridescent neck + head
    nk = blob([(x + 4, y - 56), (x + 26, y - 60), (x + 34, y - 44), (x + 22, y - 38), (x + 8, y - 44)], 2)
    c.ink(nk, (80, 170, 150), lw=2.4, shade=0.4, hi=0.5, hcol=(230, 120, 220), rim=0.3, rcol=(200, 90, 200))
    hd = ell(x + 26, y - 72, 15, 14)
    c.ink(hd, body, lw=2.6, shade=0.45, sw=6, scol=body_sh, hi=0.4)
    # half-lidded, judging eye (orange iris)
    ex, ey = x + 31, y - 75
    c.ink(ell(ex, ey, 5.2, 5.2), (255, 150, 40), lw=1.6)
    c.ink(ell(ex + 1, ey, 2.2, 2.2), INK, lw=0)
    c.ink(Sh([[(ex - 7, ey - 7), (ex + 7, ey - 7), (ex + 7, ey - 0.5), (ex - 7, ey - 1.5)]]), body, lw=0, clip=ell(ex, ey, 5.4, 5.4))
    c.stroke([(ex - 6, ey - 1.5), (ex + 6, ey - 0.4)], 2.0, INK, taper=(0.1, 0.1))
    c.stroke([(ex - 5, ey - 7.5), (ex + 6, ey - 5.5)], 2.0, INK, taper=(0.1, 0.4))        # grumpy brow ridge
    # beak + cere
    c.ink(Sh([[(x + 38, y - 74), (x + 50, y - 69), (x + 38, y - 66)]]), (230, 160, 60), lw=1.8, shade=0.3)
    c.ink(ell(x + 39, y - 74, 3.4, 2.4), (250, 246, 236), lw=1.0)
    # feet
    for dx in (-8, 8):
        c.stroke([(x + dx, y - 10), (x + dx, y - 1)], 3.0, (230, 110, 100), taper=(0, 0))
        for a in (-30, 0, 30):
            ar = math.radians(a)
            c.stroke([(x + dx, y - 1), (x + dx + math.sin(ar) * 7, y - 1 + math.cos(ar) * 1)], 2.2, (230, 110, 100), taper=(0, 0.5))
    sprite_grade(c, 0.9, (0.96, 0.9, 1.0))
    return finish_sprite(c, name, flip=True, margin=2)


def paint_nibbles(name="hs_professor_nibbles.png"):
    """Professor Nibbles, the retired lab-mascot hamster, back on his cushion with a tiny mortarboard.
    Drawn facing right, flipped to face LEFT."""
    c = Canvas2(120, 110, light=(0.42, -0.9), lw=2.6, seed=131)
    fur, fur_sh, belly = (236, 160, 80), (176, 100, 60), (252, 236, 210)
    x, y = 58, 100
    bd = blob([(x - 30, y - 4), (x - 34, y - 26), (x - 20, y - 46), (x + 6, y - 52), (x + 28, y - 40), (x + 32, y - 18), (x + 24, y - 2)], 2)
    c.ink(bd, fur, lw=2.6, shade=0.5, sw=12, scol=fur_sh, hi=0.35, rim=0.2, rcol=(255, 200, 150))
    c.ink(blob([(x - 4, y - 4), (x + 4, y - 30), (x + 22, y - 32), (x + 28, y - 14), (x + 20, y - 2)], 2), belly, lw=2.0, shade=0.3,
          scol=(220, 190, 170))
    # head
    hd = blob([(x - 2, y - 44), (x + 4, y - 64), (x + 26, y - 70), (x + 42, y - 58), (x + 44, y - 42), (x + 30, y - 32), (x + 8, y - 34)], 2)
    c.ink(hd, fur, lw=2.6, shade=0.45, sw=10, scol=fur_sh, hi=0.4)
    c.ink(blob([(x + 22, y - 50), (x + 40, y - 54), (x + 46, y - 42), (x + 34, y - 34), (x + 22, y - 38)], 2), belly, lw=1.8, shade=0.2)
    for ex_ in (x + 6, x + 22):
        c.ink(ell(ex_, y - 68, 6, 6), fur, lw=2.0, shade=0.3)
        c.ink(ell(ex_, y - 68, 3, 3), (250, 150, 160), lw=0)
    c.ink(ell(x + 30, y - 54, 4.4, 4.8), INK, lw=0)
    c.ink(ell(x + 29, y - 56, 1.6, 1.6), (255, 255, 255), lw=0)
    c.ink(ell(x + 45, y - 46, 2.6, 2.2), (240, 120, 140), lw=1.0)
    for k in range(2):
        c.stroke([(x + 44, y - 44 + k * 3), (x + 56, y - 46 + k * 5)], 1.0, INK, taper=(0, 0.5), opacity=0.7)
    c.soft(ell(x + 34, y - 42, 5, 3), (255, 110, 120), 0.4, 2)
    # paws holding a sunflower seed
    c.ink(ell(x + 30, y - 28, 5, 4), (250, 200, 190), lw=1.6)
    c.ink(ell(x + 36, y - 30, 3.2, 5, 20), (60, 50, 60), lw=1.0, hi=0.4)
    # mortarboard with tassel
    cx_, cy_ = x + 16, y - 72
    c.ink(rect(cx_ - 9, cy_ - 4, cx_ + 9, cy_ + 3), (40, 30, 50), lw=1.8)
    c.ink(Sh([[(cx_ - 20, cy_ - 4), (cx_, cy_ - 12), (cx_ + 20, cy_ - 4), (cx_, cy_ + 3)]]), (40, 30, 50), lw=1.8, hi=0.4)
    c.stroke([(cx_, cy_ - 4), (cx_ + 14, cy_ - 2), (cx_ + 16, cy_ + 10)], 1.8, (255, 210, 60), taper=(0, 0))
    c.ink(ell(cx_ + 16, cy_ + 12, 2.6, 3.4), (255, 210, 60), lw=0.8)
    sprite_grade(c, 0.92)
    return finish_sprite(c, name, flip=True, margin=2)


def paint_bones_coat(name="hs_mr_bones_coat.png"):
    """Mr. Bones' lab coat hanging from its hook by the collar loop. Bottom centre = hotspot feet."""
    c = Canvas2(120, 170, light=(-0.3, -0.95), lw=2.6, seed=141)
    coat, coat_sh = (240, 240, 248), (170, 168, 210)
    x, top = 60, 10
    c.stroke([(x - 2, top), (x, top + 12)], 2.4, (120, 120, 136), taper=(0, 0))
    body = blob([(x - 18, top + 10), (x + 18, top + 10), (x + 34, top + 30), (x + 38, top + 140), (x + 14, top + 146), (x, top + 138),
                 (x - 14, top + 146), (x - 38, top + 140), (x - 34, top + 30)], 1)
    c.ink(body, coat, lw=2.8, shade=0.45, sw=14, scol=coat_sh, hi=0.3)
    for sx in (-1, 1):       # sleeves hanging down the sides
        c.ink(blob([(x + sx * 30, top + 28), (x + sx * 42, top + 40), (x + sx * 44, top + 112), (x + sx * 34, top + 116),
                    (x + sx * 30, top + 60)], 1), shade_col(coat, 0.92), lw=2.4, shade=0.4, scol=coat_sh)
    c.ink(Sh([[(x - 16, top + 12), (x, top + 40), (x + 16, top + 12), (x + 6, top + 10), (x, top + 24), (x - 6, top + 10)]]),
          (60, 40, 70), lw=1.8)
    for sx in (-1, 1):
        c.ink(Sh([[(x + sx * 16, top + 12), (x + sx * 2, top + 42), (x + sx * 10, top + 58), (x + sx * 24, top + 26)]]), hi_col(coat, 0.1),
              lw=2.0, shade=0.3, scol=coat_sh)
    c.stroke([(x, top + 40), (x + 2, top + 138)], 1.8, coat_sh, taper=(0, 0))
    for k in range(3):
        c.ink(ell(x + 6, top + 60 + k * 22, 2.4, 2.4), (200, 200, 214), lw=1.0)
    c.ink(rect(x - 30, top + 92, x - 10, top + 112), coat, lw=1.8, shade=0.2, scol=coat_sh)
    c.stroke([(x + 16, top + 44), (x + 16, top + 34)], 3.0, (40, 90, 200), taper=(0, 0))
    c.ink(rrect(x + 10, top + 52, x + 30, top + 62, 2), (250, 248, 236), lw=1.2)
    c.text(x + 20, top + 57, "BONES", 4.5, (40, 60, 120), "Bold")
    sprite_grade(c, 0.9)
    return finish_sprite(c, name, margin=2)


def paint_puddle(name="hs_shower_puddle.png"):
    """The flood from the safety shower, with a WET FLOOR sign. Bottom centre = hotspot feet."""
    c = Canvas2(360, 150, light=(-0.3, -0.95), lw=2.6, seed=151)
    x, y = 180, 140
    rng = random.Random(3)
    pts = []
    for k in range(18):
        a = k / 18 * 2 * math.pi
        rr = rng.uniform(0.8, 1.05)
        pts.append((x + math.cos(a) * 165 * rr, y - 26 + math.sin(a) * 24 * rr))
    pd = blob(pts, 2)
    c.ink(pd, (120, 190, 240, 170), lw=2.0, oc=(40, 70, 120), shade=0.2, sw=10, scol=(70, 110, 200), hi=0.5, hw=6, hcol=(230, 250, 255),
          ao=0, tex=0.05)
    for (dx, dy, w) in ((-90, -30, 40), (30, -22, 70), (110, -34, 30)):
        c.stroke([(x + dx, y + dy), (x + dx + w, y + dy - 2)], 3, (255, 255, 255), opacity=0.6)
    for (dx, dy, rr) in ((-40, -26, 14), (60, -20, 22)):
        c.ink(ell(x + dx, y + dy, rr, rr * 0.3), (0, 0, 0, 0), lw=1.4, oc=(230, 250, 255), line_only=True, opacity=0.7)
    # A-frame WET FLOOR sign standing in it
    sx, sy = x + 100, y - 30
    c.ink(Sh([[(sx - 26, sy), (sx - 8, sy - 92), (sx + 8, sy - 92), (sx + 26, sy)]]), (250, 210, 40), lw=2.8, shade=0.45, sw=10, hi=0.35)
    c.ink(Sh([[(sx + 14, sy - 60), (sx + 30, sy), (sx + 22, sy)]]), (200, 160, 30), lw=2.2)
    c.ink(Sh([[(sx, sy - 80), (sx + 11, sy - 60), (sx - 11, sy - 60)]]), (0, 0, 0, 0), lw=2.0, oc=INK, line_only=True)
    c.text(sx, sy - 66, "!", 9, INK)
    c.text(sx, sy - 44, "WET", 9, INK)
    c.text(sx, sy - 32, "FLOOR", 7, INK, "Bold")
    sprite_grade(c, 0.9)
    return finish_sprite(c, name, margin=2)


ASSETS = {
    "bg_science_hall": paint_science_hall, "bg_lab": paint_lab, "bg_rooftop": paint_rooftop,
    "bg_science_basement": paint_science_basement, "bg_faculty_lounge": paint_faculty_lounge,
    "hs_dr_mina_volt": paint_mina,
    "hs_sky_rivera": paint_sky,
    "hs_dot_pruitt": paint_dot,
    "hs_professor_crumb": paint_crumb,
    "hs_pigeon": paint_pigeon,
    "hs_professor_nibbles": paint_nibbles,
    "hs_mr_bones_coat": paint_bones_coat,
    "hs_shower_puddle": paint_puddle,
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
            if r == "lab":
                composite(r, flags=("a3_lab_flooded", "a3_dot_mopping", "a3_nibbles_home"))
        return
    for name, fn in ASSETS.items():
        if not args or any(w in name for w in args):
            fn()


if __name__ == "__main__":
    main(sys.argv)
