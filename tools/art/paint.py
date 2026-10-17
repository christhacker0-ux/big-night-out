#!/usr/bin/env python3
"""
Big Night Out -- procedural cartoon painter.

All art produced by this script is ORIGINAL and is generated entirely by the
code below (Pillow drawing primitives; no external images, fonts aside from
system fonts used for lettering). Style: bold dark-brown outlines, saturated
warm palette, one shadow + one highlight cel tone per surface, wonky shapes.

Everything is drawn at 2x (S) and downscaled with LANCZOS for anti-aliasing.

Usage:  python3 tools/art/paint.py            # paint everything
        python3 tools/art/paint.py dex lemon  # paint assets whose name contains these words
Output: Assets/_Project/Art/Painted/*.png
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

S = 2  # supersampling factor
OUT = (30, 20, 16)  # outline color #1e1410
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "Assets", "_Project", "Art", "Painted")
FONT_DIR = "/usr/share/fonts/opentype/inter"


# --------------------------------------------------------------------------- colors
def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def dk(c, f=0.7):
    """Cel shadow tone: darker, nudged toward violet."""
    return (int(c[0] * f * 0.97), int(c[1] * f * 0.9), int(min(255, c[2] * f * 1.12 + 10)))


def lt(c, f=0.35):
    """Cel highlight tone: lighter, nudged toward warm yellow."""
    return mix(c, (255, 250, 225), f)


def font(size, kind="Black"):
    names = {"Black": "Inter-Black.otf", "Bold": "Inter-Bold.otf", "Italic": "InterDisplay-BlackItalic.otf",
             "Semi": "Inter-SemiBold.otf", "Display": "InterDisplay-Black.otf"}
    path = os.path.join(FONT_DIR, names[kind])
    try:
        return ImageFont.truetype(path, int(size * S))
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * S))


# --------------------------------------------------------------------------- geometry
def chaikin(pts, n=2, closed=True):
    for _ in range(n):
        out = []
        m = len(pts) if closed else len(pts) - 1
        for i in range(m):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out.append((p[0] * 0.75 + q[0] * 0.25, p[1] * 0.75 + q[1] * 0.25))
            out.append((p[0] * 0.25 + q[0] * 0.75, p[1] * 0.25 + q[1] * 0.75))
        if not closed:
            out = [pts[0]] + out + [pts[-1]]
        pts = out
    return pts


def ell_pts(cx, cy, rx, ry, rot=0, n=56, a0=0, a1=360):
    r = math.radians(rot)
    out = []
    full = (a1 - a0) >= 360
    cnt = n if full else n + 1
    for i in range(cnt):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def rot_pts(pts, ang, cx, cy):
    r = math.radians(ang)
    c, s = math.cos(r), math.sin(r)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def wobble(pts, amt, rng):
    return [(x + rng.uniform(-amt, amt), y + rng.uniform(-amt, amt)) for x, y in pts]


def bez(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


class Sh:
    """A shape = union of filled polygons and round-capped thick polylines (capsules)."""

    def __init__(self, polys=(), caps=()):
        self.polys = [list(p) for p in polys]
        self.caps = list(caps)

    def __add__(self, o):
        return Sh(self.polys + o.polys, self.caps + o.caps)

    def bbox(self):
        xs, ys = [], []
        for p in self.polys:
            xs += [q[0] for q in p]
            ys += [q[1] for q in p]
        for pts, w in self.caps:
            xs += [q[0] - w / 2 for q in pts] + [q[0] + w / 2 for q in pts]
            ys += [q[1] - w / 2 for q in pts] + [q[1] + w / 2 for q in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def render(self, d, ox, oy, grow=0.0):
        for p in self.polys:
            P = [(x * S - ox, y * S - oy) for x, y in p]
            if len(P) < 3:
                continue
            d.polygon(P, fill=255)
            if grow > 0:
                d.line(P + [P[0]], fill=255, width=max(1, int(round(2 * grow))), joint="curve")
                for x, y in P[:: max(1, len(P) // 24)] + [P[0]]:
                    d.ellipse([x - grow, y - grow, x + grow, y + grow], fill=255)
        for pts, w in self.caps:
            P = [(x * S - ox, y * S - oy) for x, y in pts]
            r = w * S / 2 + grow
            if len(P) > 1:
                d.line(P, fill=255, width=max(1, int(round(2 * r))), joint="curve")
            for x, y in (P[0], P[-1]):
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)


def subdiv(pts, k=3):
    out = []
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        for j in range(k):
            out.append((p[0] + (q[0] - p[0]) * j / k, p[1] + (q[1] - p[1]) * j / k))
    return out


def poly(pts, smooth=0, blob=False):
    """Polygon; smooth>0 softens corners (blob=True rounds the whole outline instead)."""
    if smooth:
        pts = chaikin(pts if blob else subdiv(pts), smooth)
    return Sh([pts])


def ell(cx, cy, rx, ry, rot=0):
    return Sh([ell_pts(cx, cy, rx, ry, rot)])


def rect(x0, y0, x1, y1):
    return Sh([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]])


def rrect(x0, y0, x1, y1, r):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += ell_pts(cx, cy, r, r, 0, 8, a, a + 90)
    return Sh([pts])


def wonky(x0, y0, x1, y1, amt=3, rng=None, smooth=2, corner=None):
    """A slightly crooked rectangle with softened corners (hand-drawn feel)."""
    rng = rng or random.Random(int(x0 * 7 + y0 * 13 + x1))
    corners = wobble([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], amt, rng)
    seg = corner or max(4.0, min(x1 - x0, y1 - y0) * 0.12)
    pts = []
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        L = math.dist(p, q)
        k = max(2, int(L // seg))
        for j in range(k):
            t = j / k
            pts.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return poly(pts, smooth)


def cap(pts, w):
    return Sh(caps=[(list(pts), w)])


# --------------------------------------------------------------------------- canvas
class Pen:
    """Draws in canvas coordinates onto a (possibly cropped) supersampled layer."""

    def __init__(self, img, ox=0, oy=0):
        self.img, self.d, self.ox, self.oy = img, ImageDraw.Draw(img), ox, oy

    def P(self, pts):
        return [(x * S - self.ox, y * S - self.oy) for x, y in pts]

    def poly(self, pts, fill):
        self.d.polygon(self.P(pts), fill=fill)

    def ell(self, cx, cy, rx, ry, fill, rot=0):
        self.d.polygon(self.P(ell_pts(cx, cy, rx, ry, rot)), fill=fill)

    def line(self, pts, w, fill):
        P = self.P(pts)
        self.d.line(P, fill=fill, width=max(1, int(round(w * S))), joint="curve")
        r = w * S / 2
        for x, y in (P[0], P[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def rect(self, x0, y0, x1, y1, fill):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill)


def _solid(W, H, c):
    c = tuple(c)
    return Image.new("RGBA", (W, H), c if len(c) == 4 else c + (255,))


def _grad_col(W, H, ts, c1, c2):
    a = np.clip(np.array(ts, dtype=np.float32), 0, 1)
    c1, c2 = np.array(c1[:3], np.float32), np.array(c2[:3], np.float32)
    col = (c1[None, :] * (1 - a[:, None]) + c2[None, :] * a[:, None]).astype(np.uint8)
    return col


class Canvas:
    def __init__(self, w, h, ow=4, bg=(0, 0, 0, 0)):
        self.w, self.h, self.ow = w, h, ow
        self.img = Image.new("RGBA", (w * S, h * S), tuple(bg) if len(bg) == 4 else tuple(bg) + (255,))

    # -- low level
    def _comp(self, layer, x, y):
        W, H = self.img.size
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + layer.width), min(H, y + layer.height)
        if x1 <= x0 or y1 <= y0:
            return
        part = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y))
        self.img.alpha_composite(part, (x0, y0))

    def _fill_layer(self, fill, W, H, ox, oy, bb):
        if isinstance(fill, tuple) and isinstance(fill[0], str):
            kind = fill[0]
            if kind in ("v", "h", "vy", "hx"):
                if kind == "v":
                    a0, a1, c1, c2 = bb[1], bb[3], fill[1], fill[2]
                elif kind == "h":
                    a0, a1, c1, c2 = bb[0], bb[2], fill[1], fill[2]
                else:
                    a0, a1, c1, c2 = fill[1], fill[2], fill[3], fill[4]
                vertical = kind in ("v", "vy")
                n = H if vertical else W
                o = oy if vertical else ox
                ts = [((i + o) / S - a0) / max(1e-6, (a1 - a0)) for i in range(n)]
                col = _grad_col(W, H, ts, c1, c2)
                if vertical:
                    arr = np.repeat(col[:, None, :], W, axis=1)
                else:
                    arr = np.repeat(col[None, :, :], H, axis=0)
                arr = np.concatenate([arr, np.full(arr.shape[:2] + (1,), 255, np.uint8)], axis=2)
                return Image.fromarray(arr, "RGBA")
            if kind == "r":  # ('r', cx, cy, r, c_in, c_out)
                _, cx, cy, r, c1, c2 = fill
                ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
                dd = np.sqrt(((xs + ox) / S - cx) ** 2 + ((ys + oy) / S - cy) ** 2) / r
                t = np.clip(dd, 0, 1)
                c1a, c2a = np.array(c1[:3], np.float32), np.array(c2[:3], np.float32)
                arr = (c1a * (1 - t[..., None]) + c2a * t[..., None]).astype(np.uint8)
                arr = np.concatenate([arr, np.full((H, W, 1), 255, np.uint8)], axis=2)
                return Image.fromarray(arr, "RGBA")
        return _solid(W, H, fill)

    def paint(self, sh, fill, ow=None, oc=OUT, shade=None, hi=None, pattern=None, clip=None, opacity=1.0):
        """Fill a shape with a bold outline, optional cel shadow / highlight crescents and pattern.

        shade=(dx, dy[, color]) : shadow band on the side away from the light (offset trick)
        hi=(dx, dy[, color[, inset]]): highlight band on the lit side
        pattern(pen)             : extra drawing clipped to the shape
        clip=Sh                  : additionally clip everything to another shape
        """
        ow = self.ow if ow is None else ow
        bx0, by0, bx1, by1 = sh.bbox()
        pad = ow + 6
        for spec in (shade, hi):
            if spec:
                pad += abs(spec[0]) + abs(spec[1]) + (spec[3] if len(spec) > 3 else 0)
        ox, oy = int(math.floor((bx0 - pad) * S)), int(math.floor((by0 - pad) * S))
        W = int(math.ceil((bx1 + pad) * S)) - ox
        H = int(math.ceil((by1 + pad) * S)) - oy
        if W <= 0 or H <= 0:
            return
        m = Image.new("L", (W, H), 0)
        sh.render(ImageDraw.Draw(m), ox, oy, 0)
        cm = None
        if clip is not None:
            cm = Image.new("L", (W, H), 0)
            clip.render(ImageDraw.Draw(cm), ox, oy, 0)
            m = ImageChops.multiply(m, cm)
        if ow > 0:
            mo = Image.new("L", (W, H), 0)
            sh.render(ImageDraw.Draw(mo), ox, oy, ow * S)
            if cm is not None:
                mo = ImageChops.multiply(mo, cm)
            if not isinstance(fill[0], str) and len(fill) == 4 and fill[3] == 0:
                mo = ImageChops.subtract(mo, m)  # stroke only
            if opacity < 1:
                mo = mo.point(lambda v: int(v * opacity))
            ol = _solid(W, H, oc)
            ol.putalpha(mo)
            self._comp(ol, ox, oy)
        fl = self._fill_layer(fill, W, H, ox, oy, (bx0, by0, bx1, by1))
        if len(fill) == 4 and not isinstance(fill[0], str):
            base_alpha = fill[3] / 255.0
        else:
            base_alpha = 1.0
        if pattern:
            pattern(Pen(fl, ox, oy))
        if shade:
            dx, dy = shade[0] * S, shade[1] * S
            sm = ImageChops.subtract(m, ImageChops.offset(m, int(-dx), int(-dy)))
            if len(shade) > 2 and shade[2] is not None:
                sl = _solid(W, H, shade[2])
            else:
                sl = ImageChops.multiply(fl, _solid(W, H, (190, 160, 200)))
            fl = Image.composite(sl, fl, sm)
        if hi:
            dx, dy = hi[0] * S, hi[1] * S
            inset = (hi[3] if len(hi) > 3 else 0) * S
            if inset:
                ins = (dx / (abs(dx) + abs(dy) + 1e-6) * inset, dy / (abs(dx) + abs(dy) + 1e-6) * inset)
                a = ImageChops.multiply(m, ImageChops.offset(m, int(ins[0]), int(ins[1])))
            else:
                a = m
            hm = ImageChops.subtract(a, ImageChops.offset(a, int(dx), int(dy)))
            hc = hi[2] if len(hi) > 2 and hi[2] is not None else None
            hl = _solid(W, H, hc) if hc else ImageChops.screen(fl, _solid(W, H, (110, 95, 70)))
            fl = Image.composite(hl, fl, hm)
        a = m
        if base_alpha * opacity < 1:
            a = m.point(lambda v: int(v * base_alpha * opacity))
        fl.putalpha(a)
        self._comp(fl, ox, oy)

    def line(self, pts, w, color=OUT, opacity=1.0):
        self.paint(cap(pts, w), color, ow=0, opacity=opacity)

    def curve(self, p0, p1, p2, w, color=OUT, opacity=1.0):
        self.line(bez(p0, p1, p2), w, color, opacity)

    def text(self, x, y, s, size, fill, kind="Black", stroke=0, sc=OUT, anchor="mm", angle=0, spacing=0):
        f = font(size, kind)
        if angle == 0 and spacing == 0:
            d = ImageDraw.Draw(self.img)
            d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor, stroke_width=int(stroke * S),
                   stroke_fill=sc)
            return
        # rotated / tracked text: render to a temp layer
        tmp = Image.new("RGBA", (int(len(s) * size * 1.2 * S + 40 * S), int(size * 2.2 * S + 20 * S)), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        if spacing:
            cx = 10 * S + stroke * S
            for ch in s:
                d.text((cx, tmp.height / 2), ch, font=f, fill=fill, anchor="lm", stroke_width=int(stroke * S),
                       stroke_fill=sc)
                cx += d.textlength(ch, font=f) + spacing * S
        else:
            d.text((10 * S + stroke * S, tmp.height / 2), s, font=f, fill=fill, anchor="lm",
                   stroke_width=int(stroke * S), stroke_fill=sc)
        bb = tmp.getbbox()
        if not bb:
            return
        tmp = tmp.crop(bb)
        tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
        self._comp(tmp, int(x * S - tmp.width / 2), int(y * S - tmp.height / 2))

    def glow(self, cx, cy, r, color, strength=0.6, power=2.0):
        """Additive-ish (screen) radial light."""
        x0, y0 = int((cx - r) * S), int((cy - r) * S)
        n = int(2 * r * S)
        ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
        dd = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
        a = np.clip(1 - dd, 0, 1) ** power * strength
        W, H = self.img.size
        sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(W, x0 + n), min(H, y0 + n)
        if sx1 <= sx0 or sy1 <= sy0:
            return
        a = a[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]
        reg = np.asarray(self.img.crop((sx0, sy0, sx1, sy1))).astype(np.float32)
        light = np.array(color[:3], np.float32)[None, None, :] * a[..., None]
        rgb = 255 - (255 - reg[..., :3]) * (255 - light) / 255
        reg[..., :3] = rgb
        self.img.paste(Image.fromarray(reg.astype(np.uint8), "RGBA"), (sx0, sy0))

    def shade_map(self, fn):
        """Multiply the whole canvas RGB by a per-pixel factor array fn(xs, ys) (canvas coords) -> (H,W,3)."""
        W, H = self.img.size
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32) / S
        f = fn(xs, ys)
        arr = np.asarray(self.img).astype(np.float32)
        arr[..., :3] *= f
        self.img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    def stamp(self, sub, cx, cy, angle=0):
        im = sub.img
        if angle:
            im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        self._comp(im, int(cx * S - im.width / 2), int(cy * S - im.height / 2))

    def shadow(self, cx, cy, rx, ry, opacity=0.35, color=(20, 8, 30)):
        """Soft contact shadow on the floor."""
        n = 3
        for i in range(n):
            k = 1 - i * 0.18
            self.paint(ell(cx, cy, rx * (1.15 - 0.15 * i), ry * (1.15 - 0.15 * i)), color, ow=0,
                       opacity=opacity / n * (1 + i * 0.3) * k)

    def fit(self, margin=3, feet=True, fill=None):
        """Normalise a sprite/icon: scale content to fit inside `margin` (or to `fill` px max side) and
        centre it; with feet=True the feet sit on the bottom margin, centred horizontally."""
        W, H = self.img.size
        a = np.asarray(self.img.getchannel("A"))
        ys, xs = np.nonzero(a > 16)
        if len(xs) == 0:
            return
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        m = margin * S
        if fill:
            k = fill * S / max(x1 - x0, y1 - y0)
        else:
            k = min((H - 2 * m) / (y1 - y0), (W - 2 * m) / (x1 - x0))
        part = self.img.crop((x0, y0, x1, y1))
        part = part.resize((max(1, int(round(part.width * k))), max(1, int(round(part.height * k)))), Image.LANCZOS)
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if feet:
            band = ys > y1 - (y1 - y0) * 0.05
            fx = (xs[band].min() + xs[band].max()) / 2
            px = int(round(W / 2 - (fx - x0) * k))
            px = max(m, min(W - m - part.width, px))
            py = H - m - part.height
        else:
            px, py = (W - part.width) // 2, (H - part.height) // 2
        out.alpha_composite(part, (px, py))
        self.img = out

    def result(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)

    def save(self, name):
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, name)
        self.result().save(path, optimize=True)
        print("wrote", os.path.relpath(path, ROOT), "%dx%d" % (self.w, self.h))


# =========================================================================== scenery helpers
W_BG, H_BG = 1920, 1080
WALL_Y = 790  # where the back wall meets the floor


def block_wall(c, x0, y0, x1, y1, top, bot, bw=120, bh=60, mortar=0.22, seed=1):
    """Painted cinder-block wall with a vertical gradient."""
    c.paint(rect(x0, y0, x1, y1), ("vy", y0, y1, top, bot), ow=0)
    rng = random.Random(seed)
    row = 0
    y = y1 - bh
    while y > y0 - bh:
        c.line([(x0, y), (x1, y)], 2.2, (20, 10, 25), opacity=mortar)
        c.line([(x0, y + 3), (x1, y + 3)], 1.5, (255, 240, 210), opacity=mortar * 0.5)
        off = (bw / 2) * (row % 2)
        x = x0 - off
        while x < x1:
            c.line([(x, y), (x, y + bh)], 2.2, (20, 10, 25), opacity=mortar)
            if rng.random() < 0.12:  # scuffs
                c.paint(ell(x + rng.uniform(20, bw - 20), y + bh / 2, rng.uniform(6, 16), rng.uniform(2, 5)),
                        (40, 20, 30), ow=0, opacity=0.08)
            x += bw
        y -= bh
        row += 1


def plank_floor(c, base, vp=(960, 360), y0=WALL_Y, step=110, seed=2):
    c.paint(rect(0, y0, W_BG, H_BG), ("vy", y0, H_BG, mix(base, (255, 220, 160), 0.12), dk(base, 0.8)), ow=0)
    rng = random.Random(seed)
    xs = list(range(-1600, W_BG + 1700, step))
    t0 = (y0 - vp[1])
    edges = []
    for xb in xs:
        # point at bottom edge xb, line toward vp
        xa = vp[0] + (xb - vp[0]) * t0 / (H_BG - vp[1])
        edges.append((xa, xb))
        c.line([(xa, y0), (xb, H_BG)], 2.4, (60, 25, 15), opacity=0.55)
    # staggered plank ends + grain
    for i in range(len(edges) - 1):
        ya = y0
        while ya < H_BG:
            depth = (ya - vp[1]) / (H_BG - vp[1])
            ya += rng.uniform(70, 160) * depth
            if ya >= H_BG:
                break
            t = (ya - vp[1]) / (H_BG - vp[1])
            xl = vp[0] + (xs[i] - vp[0]) * t
            xr = vp[0] + (xs[i + 1] - vp[0]) * t
            c.line([(xl, ya), (xr, ya)], 2.0, (60, 25, 15), opacity=0.45)
            if rng.random() < 0.5:
                gx = xl + (xr - xl) * rng.uniform(0.3, 0.7)
                c.line([(gx - 12 * t, ya + 8 * t), (gx + 14 * t, ya + 10 * t)], 1.4, (255, 220, 170), opacity=0.25)


def baseboard(c, y=WALL_Y, h=22, color=(92, 52, 40)):
    c.paint(rect(-10, y - h, W_BG + 10, y + 4), color, ow=3, hi=(0, 4, lt(color, 0.3)))


def night_window(c, x0, y0, x1, y1, seed=3, frame=(236, 214, 178), mull=True):
    rng = random.Random(seed)
    # frame
    c.paint(wonky(x0 - 16, y0 - 16, x1 + 16, y1 + 16, 2, rng), frame, shade=(-5, -5, dk(frame, 0.75)))

    def sky(p):
        for _ in range(60):
            sx, sy = rng.uniform(x0, x1), rng.uniform(y0, y0 + (y1 - y0) * 0.7)
            r = rng.choice([1.2, 1.6, 2.2])
            p.ell(sx, sy, r, r, (255, 250, 220))
        mx, my = x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.22
        p.ell(mx, my, 30, 30, (255, 246, 200))
        p.ell(mx + 12, my - 8, 26, 26, (52, 40, 112))
        # campus skyline
        bx = x0 - 10
        while bx < x1:
            bwid = rng.uniform(40, 90)
            bt = y1 - rng.uniform(50, 140)
            p.rect(bx, bt, bx + bwid, y1 + 5, (38, 26, 66))
            if rng.random() < 0.4:
                p.poly([(bx, bt), (bx + bwid / 2, bt - 30), (bx + bwid, bt)], (38, 26, 66))
            for wy in np.arange(bt + 12, y1 - 6, 22):
                for wx in np.arange(bx + 8, bx + bwid - 10, 18):
                    if rng.random() < 0.45:
                        p.rect(wx, wy, wx + 8, wy + 11, (255, 206, 92))
            bx += bwid + rng.uniform(-6, 10)
        p.rect(x0 - 5, y1 - 26, x1 + 5, y1 + 5, (28, 20, 48))
    c.paint(rect(x0, y0, x1, y1), ("vy", y0, y1, (30, 26, 84), (122, 54, 120)), ow=3, pattern=sky)
    if mull:
        mx = (x0 + x1) / 2
        c.paint(rect(mx - 6, y0, mx + 6, y1), frame, ow=3)
        my = y0 + (y1 - y0) * 0.45
        c.paint(rect(x0, my - 6, x1, my + 6), frame, ow=3)
    # glass sheen
    c.paint(poly([(x0 + 14, y1 - 30), (x0 + 60, y0 + 10), (x0 + 84, y0 + 10), (x0 + 38, y1 - 30)]),
            (255, 255, 255), ow=0, opacity=0.10)
    # sill
    c.paint(wonky(x0 - 30, y1 + 10, x1 + 30, y1 + 30, 2, rng), frame, shade=(0, -6, dk(frame, 0.72)))


def curtain(c, x0, x1, y0, y1, color, side="L", seed=4):
    rng = random.Random(seed)
    # top edge straight, bottom wavy, gathered toward the side
    n = 5
    hem = [(x1 - (x1 - x0) * i / n, y1 + (8 if i % 2 else -4)) for i in range(n + 1)]
    if side == "L":  # gathered toward the left edge
        pts = [(x0, y0), (x1, y0), (x1 - 10, y0 + (y1 - y0) * 0.45), (x1 - 4, y1)] + hem
    else:
        pts = [(x0, y0), (x1, y0)] + hem + [(x0 + 4, y1), (x0 + 10, y0 + (y1 - y0) * 0.45)]
    sh = poly(pts, 1)

    def folds(p):
        for i in range(1, 4):
            fx = x0 + (x1 - x0) * i / 4
            p.line([(fx, y0 + 6), (fx + rng.uniform(-6, 6), y1)], 3.5, dk(color, 0.72))
            p.line([(fx + 6, y0 + 6), (fx + 8 + rng.uniform(-4, 4), y1)], 2.2, lt(color, 0.3))
    c.paint(sh, color, pattern=folds, shade=(4 if side == "L" else -4, 0))


def string_lights(c, anchors, colors, spacing=46, sag=40, seed=5):
    rng = random.Random(seed)
    bulbs = []
    for (ax, ay), (bx, by) in zip(anchors, anchors[1:]):
        mid = ((ax + bx) / 2, max(ay, by) + sag)
        pts = bez((ax, ay), (mid[0], mid[1] + sag * 0.6), (bx, by), 30)
        c.line(pts, 3, (40, 46, 34))
        L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        k = int(L // spacing)
        for j in range(1, k + 1):
            t = j / (k + 1)
            q = bez((ax, ay), (mid[0], mid[1] + sag * 0.6), (bx, by), 1000)[int(t * 1000)]
            bulbs.append(q)
    for i, (x, y) in enumerate(bulbs):
        col = colors[i % len(colors)]
        c.paint(rect(x - 3, y - 2, x + 3, y + 5), (60, 66, 50), ow=2)
        c.paint(ell(x + rng.uniform(-1, 1), y + 13, 6, 9), col, ow=2.5, hi=(-2, -2, (255, 255, 240)))
    return [(x, y + 13, colors[i % len(colors)]) for i, (x, y) in enumerate(bulbs)]


def door(c, x0, y0, x1, y1, color, knob="L", panels=True, casing=(232, 206, 168)):
    c.paint(rect(x0 - 14, y0 - 14, x1 + 14, y1 + 2), casing, shade=(-4, 0, dk(casing, 0.78)))
    c.paint(rect(x0, y0, x1, y1), ("v", lt(color, 0.12), dk(color, 0.88)), ow=3,
            shade=(-6, 0, dk(color, 0.8)))
    if panels:
        for (py0, py1) in ((y0 + 24, y0 + (y1 - y0) * 0.46), (y0 + (y1 - y0) * 0.54, y1 - 24)):
            c.paint(rrect(x0 + 18, py0, x1 - 18, py1, 4), color, ow=2.5,
                    shade=(0, -4, dk(color, 0.78)), hi=(0, 3, lt(color, 0.3)))
    kx = x0 + 18 if knob == "L" else x1 - 18
    ky = y0 + (y1 - y0) * 0.55
    c.paint(rrect(kx - 6, ky - 22, kx + 6, ky + 14, 4), (196, 160, 70), ow=2.5)
    c.paint(ell(kx, ky - 4, 8, 8), (240, 196, 80), ow=3, hi=(-2, -2, (255, 245, 190)), shade=(3, 3))


def poster(w, h, bgc, draw_fn, angle=0, tape=(240, 232, 200)):
    sub = Canvas(w + 40, h + 40, ow=4)
    sub.paint(wonky(20, 20, 20 + w, 20 + h, 2.5, random.Random(w * h)), bgc, pattern=lambda p: draw_fn(p, 20, 20))
    for tx, ty in ((24, 22), (16 + w, 22)):
        sub.paint(rect(tx - 9, ty - 6, tx + 9, ty + 6), tape, ow=0, opacity=0.85)
    return sub


def light_pass(c, ambient, lights, vign=0.45, front=0.3):
    """Night lighting: dim everything, add warm pools around lamps, darken corners."""
    def fn(xs, ys):
        cx, cy = W_BG / 2, H_BG * 0.55
        d = np.sqrt(((xs - cx) / (W_BG * 0.62)) ** 2 + ((ys - cy) / (H_BG * 0.7)) ** 2)
        base = ambient * (1 - vign * np.clip(d, 0, 1.4) ** 2) * (1 - front * np.clip((ys - 880) / 200, 0, 1))
        F = np.repeat(base[..., None], 3, axis=2)
        for (lx, ly, r, s, col) in lights:
            dd = np.sqrt((xs - lx) ** 2 + (ys - ly) ** 2) / r
            fall = np.clip(1 - dd, 0, 1) ** 1.6 * s
            F += fall[..., None] * (np.array(col, np.float32) / 255.0)[None, None, :]
        return np.clip(F, 0, 1.35)
    c.shade_map(fn)


# =========================================================================== 1. Dex's dorm room
def paint_dex_room():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(214)
    wall_top, wall_bot = (96, 64, 112), (168, 104, 128)
    block_wall(c, 0, 0, W_BG, WALL_Y, wall_top, wall_bot, seed=11)
    # ceiling shadow band + trim
    c.paint(rect(0, 0, W_BG, 46), (70, 44, 82), ow=0)
    c.paint(rect(-10, 40, W_BG + 10, 54), (220, 190, 160), ow=3, shade=(0, -4))
    plank_floor(c, (178, 100, 54), seed=12)
    baseboard(c)

    # --- rug (in front, keep flat so it reads as floor)
    c.paint(ell(1010, 940, 420, 70), (196, 70, 60), ow=4, shade=(0, -8, (150, 46, 50)),
            pattern=lambda p: [p.ell(1010, 940, 420 - k, 70 - k * 70 / 420, col) for k, col in
                               ((40, (242, 170, 60)), (70, (196, 70, 60)), (110, (60, 150, 150)), (140, (196, 70, 60)))])

    # --- window over the bed + curtains
    night_window(c, 330, 250, 530, 520, seed=7)
    c.paint(cap([(270, 232), (590, 232)], 8), (130, 84, 50))
    curtain(c, 278, 352, 232, 560, (232, 120, 54), "L", seed=8)
    curtain(c, 508, 582, 232, 560, (232, 120, 54), "R", seed=9)
    # cactus on sill
    c.paint(rrect(406, 516, 446, 538, 4), (206, 96, 60), shade=(-3, 0))
    c.paint(poly([(414, 518), (412, 476), (426, 462), (438, 476), (436, 518)], 2), (90, 168, 80), shade=(-4, 0))
    c.paint(cap([(414, 492), (402, 486), (402, 474)], 7), (90, 168, 80), ow=3)

    # --- band poster (original band)
    def band(p, ox, oy):
        p.rect(ox, oy, ox + 150, oy + 210, (34, 24, 52))
        for k in range(10):
            a = math.radians(k * 36 + 10)
            p.poly([(ox + 75, oy + 96), (ox + 75 + 160 * math.cos(a), oy + 96 + 160 * math.sin(a)),
                    (ox + 75 + 160 * math.cos(a + 0.25), oy + 96 + 160 * math.sin(a + 0.25))], (64, 40, 90))
        # toaster mascot
        p.d.rounded_rectangle([ (ox + 38) * S - p.ox, (oy + 70) * S - p.oy, (ox + 112) * S - p.ox,
                               (oy + 128) * S - p.oy], radius=14 * S, fill=OUT)
        p.d.rounded_rectangle([ (ox + 42) * S - p.ox, (oy + 74) * S - p.oy, (ox + 108) * S - p.ox,
                               (oy + 124) * S - p.oy], radius=12 * S, fill=(250, 196, 70))
        p.rect(ox + 54, oy + 66, ox + 66, oy + 76, (240, 160, 90))
        p.rect(ox + 84, oy + 66, ox + 96, oy + 76, (240, 160, 90))
        for ex in (60, 90):
            p.ell(ox + ex, oy + 96, 6, 7, (255, 255, 255))
            p.ell(ox + ex + 1, oy + 98, 3, 3, OUT)
        p.line([(ox + 62, oy + 112), (ox + 75, oy + 107), (ox + 88, oy + 113)], 3, OUT)
    bp = poster(150, 210, (34, 24, 52), band)
    bp.text(95, 52, "THE GRUMPY", 17, (255, 120, 170), stroke=1.5)
    bp.text(95, 74, "TOASTERS", 22, (255, 120, 170), stroke=1.5)
    bp.text(95, 172, "LIVE & CRISPY", 13, (250, 196, 70), "Bold")
    bp.text(95, 194, "FALL TOUR", 11, (200, 200, 230), "Bold")
    c.stamp(bp, 690, 360, angle=3)

    # --- SPRING BREAK pennant
    pen = Canvas(380, 150, ow=4)
    pen.paint(cap([(20, 20), (20, 130)], 10), (150, 96, 56), ow=3)
    pen.paint(poly([(26, 26), (360, 74), (26, 124)]), (214, 40, 60), shade=(0, -6, (160, 24, 50)),
              hi=(0, 5, (240, 90, 100), 6))
    pen.text(160, 76, "SPRING BREAK", 26, (255, 214, 70), stroke=2.5, angle=0)
    c.stamp(pen, 1070, 330, angle=-4)

    # --- cross-stitch sampler over the dresser
    def stitch(p, ox, oy):
        p.rect(ox, oy, ox + 120, oy + 96, (246, 236, 214))
        for i in range(0, 120, 12):
            p.ell(ox + 6 + i, oy + 8, 3, 3, (220, 90, 110))
            p.ell(ox + 6 + i, oy + 88, 3, 3, (220, 90, 110))
    sp = poster(120, 96, (246, 236, 214), stitch, tape=(160, 110, 70))
    sp.text(80, 54, "HOME SWEET", 13, (70, 120, 160), "Bold")
    sp.text(80, 72, "DORM", 18, (220, 90, 110))
    sp.text(80, 92, "love, mom", 10, (90, 90, 90), "Semi")
    c.stamp(sp, 128, 420, angle=-2)

    # --- dresser (left)
    c.shadow(130, 800, 120, 14)
    dc = (188, 120, 70)
    c.paint(wonky(30, 590, 228, 800, 2, rng), dc, shade=(-8, 0, dk(dc, 0.78)), hi=(0, 5, lt(dc, 0.25)))
    for i in range(3):
        y = 610 + i * 62
        c.paint(wonky(44, y, 214, y + 52, 1.5, rng), mix(dc, (220, 150, 90), 0.4), ow=3, shade=(-4, -4))
        c.paint(ell(129, y + 26, 10, 5), (240, 196, 80), ow=2.5)
    # sock + shirt sleeve spilling out of a drawer
    c.paint(poly([(70, 660), (98, 660), (100, 700), (86, 716), (70, 708)], 1), (250, 246, 236), ow=3,
            shade=(-3, -2))
    c.paint(rect(70, 666, 99, 674), (220, 60, 60), ow=0)
    c.paint(poly([(150, 724), (196, 724), (204, 760), (176, 770), (160, 752)], 1), (90, 160, 210), ow=3,
            shade=(-3, -2))
    # goldfish bowl
    c.paint(ell(84, 556, 38, 34), (170, 220, 240, 170), ow=4, hi=(-4, -4, (240, 252, 255), 4))
    c.paint(ell(84, 570, 32, 18), (90, 170, 220, 170), ow=0)
    c.paint(ell(90, 562, 10, 6), (255, 140, 40), ow=2)
    c.paint(poly([(98, 562), (108, 554), (108, 570)]), (255, 140, 40), ow=2)
    c.paint(rrect(56, 520, 112, 528, 3), (170, 220, 240), ow=3)
    # trophy
    c.paint(rect(156, 574, 196, 590), (120, 70, 40), shade=(-3, 0))
    c.paint(rect(170, 556, 182, 576), (240, 196, 80), ow=3)
    c.paint(poly([(156, 520), (196, 520), (190, 548), (176, 558), (162, 548)], 1), (240, 196, 80),
            shade=(-4, 0), hi=(4, 0, (255, 240, 170), 3))
    c.text(176, 584, "#9", 8, (255, 230, 150), "Bold")

    # --- bed (x 260-560, y 760-880), headboard + pillow on the left
    c.shadow(415, 878, 170, 16, 0.5)
    frame = (120, 70, 46)
    c.paint(wonky(262, 752, 296, 880, 2, rng), frame, shade=(-5, 0, dk(frame, 0.75)))  # headboard
    c.paint(rect(276, 844, 556, 864), frame, shade=(0, -4, dk(frame, 0.75)))  # side rail
    for lx in (284, 544):
        c.paint(rect(lx - 7, 860, lx + 7, 880), dk(frame, 0.85), ow=3)
    c.paint(wonky(536, 790, 558, 864, 1.5, rng), frame, shade=(-4, 0, dk(frame, 0.75)))  # footboard
    c.paint(wonky(286, 794, 546, 846, 1.5, rng), (240, 236, 226), shade=(0, -6))  # mattress/sheet
    # rumpled blanket
    bl = (64, 112, 196)
    bpts = [(336, 794), (360, 778), (392, 788), (420, 772), (452, 786), (486, 770), (520, 784),
            (548, 792), (552, 838), (530, 852), (500, 842), (470, 856), (430, 846), (396, 858), (350, 846),
            (330, 830)]

    def plaid(p):
        for x in range(300, 560, 26):
            p.line([(x, 760), (x - 6, 870)], 5, (90, 140, 220))
        for y in range(780, 870, 22):
            p.line([(320, y), (560, y + 4)], 4, (44, 80, 160))
        p.line([(420, 780), (430, 850)], 3, dk(bl, 0.6))
        p.line([(486, 776), (476, 846)], 3, dk(bl, 0.6))
    c.paint(poly(bpts, 2, True), bl, pattern=plaid, shade=(-4, -7, None), hi=(3, 5, None, 2))
    # pillow (left end)
    c.paint(poly([(292, 780), (322, 768), (352, 772), (366, 792), (350, 812), (318, 814), (296, 804)], 2, True),
            (252, 250, 244), shade=(-3, -4, (214, 208, 226)))
    c.curve((318, 790), (326, 786), (334, 792), 2.2)
    # sock on blanket
    c.paint(poly([(456, 790), (470, 788), (474, 806), (488, 812), (486, 820), (462, 818)], 1),
            (250, 246, 236), ow=3)
    # pizza box poking from under the bed
    c.paint(poly([(388, 866), (462, 862), (470, 878), (380, 880)]), (226, 186, 130), ow=3, shade=(0, -3))

    # --- laundry pile on floor
    lp = [(590, 870), (602, 838), (626, 826), (648, 834), (666, 828), (684, 846), (690, 874)]
    c.shadow(640, 872, 60, 9)
    c.paint(poly(lp, 2, True), (150, 90, 160), shade=(-4, -4),
            pattern=lambda p: (p.poly([(606, 846), (640, 836), (650, 860), (612, 866)], (240, 200, 70)),
                               p.poly([(650, 840), (680, 850), (676, 870), (650, 866)], (90, 170, 120))))

    # --- mirror (x 790-890, y 500-660)
    mf = (214, 150, 74)
    c.paint(rrect(790, 500, 890, 660, 20), mf, shade=(-5, -5, dk(mf, 0.72)), hi=(4, 4, lt(mf, 0.4), 2))

    def glass(p):
        p.poly([(800, 640), (850, 520), (866, 520), (816, 640)], (236, 246, 255))
        p.poly([(826, 640), (870, 536), (876, 548), (836, 640)], (236, 246, 255))
    c.paint(rrect(802, 512, 878, 648, 14), ("v", (176, 206, 230), (120, 140, 196)), ow=3, pattern=glass)
    c.paint(rect(850, 600, 884, 632), (255, 236, 110), ow=2.5, shade=(-3, -3))
    c.text(867, 611, "U GOT", 7, (60, 60, 120), "Bold")
    c.text(867, 622, "THIS!", 7, (200, 40, 70), "Black")

    # --- mini fridge + lava lamp
    c.shadow(985, 800, 64, 10)
    fr = (226, 226, 214)
    c.paint(wonky(932, 696, 1040, 802, 2, rng), fr, shade=(-8, 0, dk(fr, 0.8)), hi=(0, 4, (250, 250, 245)))
    c.line([(934, 724), (1038, 724)], 3)
    c.paint(rrect(1020, 734, 1028, 776, 3), (160, 160, 170), ow=2.5)
    for mx, my, col in ((956, 748, (240, 80, 80)), (978, 762, (80, 170, 230)), (964, 778, (250, 200, 60))):
        c.paint(ell(mx, my, 7, 7), col, ow=2.5)
    c.paint(poly([(964, 694), (1006, 694), (996, 684), (974, 684)]), (110, 110, 130), ow=3)
    c.paint(poly([(974, 684), (996, 684), (1004, 636), (994, 610), (976, 610), (966, 636)], 1), (250, 110, 150),
            hi=(-3, 0, (255, 190, 210), 2),
            pattern=lambda p: (p.ell(983, 668, 8, 9, (255, 200, 80)), p.ell(990, 640, 6, 7, (255, 200, 80))))
    c.paint(poly([(978, 610), (992, 610), (988, 596), (982, 596)]), (110, 110, 130), ow=3)

    # --- shelf above desk
    c.paint(rect(1074, 560, 1296, 574), (150, 92, 56), shade=(0, -4))
    bx = 1086
    for wdt, hgt, col in ((18, 70, (210, 60, 60)), (14, 62, (70, 130, 200)), (22, 74, (240, 190, 60)),
                          (16, 58, (100, 170, 110)), (20, 66, (160, 90, 170))):
        c.paint(rect(bx, 560 - hgt, bx + wdt, 560), col, ow=3, shade=(-4, 0))
        bx += wdt + 2
    c.paint(poly([(bx + 4, 560), (bx + 10, 500), (bx + 30, 494), (bx + 24, 560)]), (240, 140, 60), ow=3,
            shade=(-4, 0))  # leaning book
    c.paint(rrect(1236, 528, 1270, 560, 5), (206, 96, 60), shade=(-3, 0))
    for a in (-40, -10, 20, 50):
        r = math.radians(a - 90)
        c.paint(ell(1253 + 22 * math.cos(r), 520 + 18 * math.sin(r), 8, 16, a), (90, 168, 80), ow=3)

    # --- desk (x 1080-1280, y 680-820)
    c.shadow(1180, 820, 120, 14, 0.45)
    dw = (176, 104, 60)
    c.paint(rect(1094, 736, 1268, 812), dk(dw, 0.5), ow=3)  # dark back
    c.paint(wonky(1086, 734, 1104, 820, 1.2, rng), dw, shade=(-4, 0, dk(dw, 0.75)))  # left leg
    c.paint(wonky(1196, 734, 1276, 820, 1.5, rng), dw, shade=(-6, 0, dk(dw, 0.75)))
    for y in (746, 782):
        c.paint(rect(1204, y, 1268, y + 28), lt(dw, 0.15), ow=2.5, shade=(-3, -3))
        c.paint(rrect(1226, y + 11, 1246, y + 17, 3), (240, 196, 80), ow=2)
    c.paint(wonky(1078, 720, 1284, 738, 1.2, rng), lt(dw, 0.1), hi=(0, 4, lt(dw, 0.4)), shade=(0, -4))
    # laptop
    c.paint(poly([(1104, 683), (1172, 681), (1168, 716), (1108, 717)]), (70, 74, 90), ow=3)

    def screen(p):
        p.rect(1110, 688, 1166, 694, (90, 110, 200))
        for i, y in enumerate((700, 706)):
            p.rect(1114, y, 1150 - i * 10, y + 3, (150, 170, 220))
        p.ell(1156, 704, 4, 4, (240, 100, 140))
    c.paint(poly([(1110, 687), (1166, 686), (1163, 712), (1112, 713)]), ("v", (220, 236, 255), (150, 190, 240)),
            ow=2, pattern=screen)
    c.paint(poly([(1098, 716), (1178, 716), (1186, 724), (1092, 724)]), (150, 154, 170), ow=3)
    # the letter (propped up)
    c.paint(poly([(1192, 722), (1196, 692), (1236, 690), (1234, 722)]), (250, 240, 214), ow=3,
            shade=(-4, 0, (220, 200, 170)))
    c.line([(1197, 694), (1215, 708), (1235, 692)], 2.5)
    c.paint(ell(1215, 709, 6, 5), (220, 40, 70), ow=2)
    # pen mug
    c.paint(rrect(1240, 700, 1260, 722, 3), (240, 120, 60), ow=3, shade=(-3, 0))
    c.line([(1246, 700), (1242, 686)], 3, (60, 120, 220))
    c.line([(1254, 700), (1258, 688)], 3, (240, 196, 60))
    # gooseneck desk lamp
    c.paint(ell(1270, 720, 13, 4.5), (60, 120, 110), ow=3)
    c.paint(cap([(1270, 718), (1278, 700), (1270, 690)], 4.5), (60, 120, 110), ow=2.5)
    c.paint(ell(1253, 702, 10, 4, -30), (255, 246, 190), ow=2.5)  # bulb
    c.paint(poly([(1276, 684), (1262, 680), (1240, 696), (1262, 708)], 1), (60, 170, 140), ow=3,
            shade=(3, -2), hi=(-2, 2, (140, 220, 190)))
    # rolling chair tucked at the right of the desk
    ch = (200, 70, 60)
    c.shadow(1330, 830, 50, 8)
    c.paint(rrect(1300, 700, 1362, 770, 16), ch, shade=(-6, -4, dk(ch, 0.72)), hi=(4, 4, lt(ch, 0.3), 3))
    c.paint(rrect(1296, 772, 1366, 790, 8), ch, shade=(0, -4, dk(ch, 0.72)))
    c.line([(1331, 790), (1331, 816)], 6, (70, 70, 80))
    c.line([(1300, 822), (1362, 822)], 6, (70, 70, 80))
    for wx in (1302, 1360):
        c.paint(ell(wx, 828, 6, 6), (40, 40, 48), ow=2)

    # --- small photo strip / calendar near door
    def cal(p, ox, oy):
        p.rect(ox, oy, ox + 90, oy + 24, (220, 60, 60))
        for i in range(4):
            for j in range(5):
                p.rect(ox + 6 + j * 17, oy + 32 + i * 18, ox + 18 + j * 17, oy + 44 + i * 18, (220, 214, 200))
        p.line([(ox + 40, oy + 62), (ox + 56, oy + 76)], 3, (220, 40, 40))
        p.line([(ox + 56, oy + 62), (ox + 40, oy + 76)], 3, (220, 40, 40))
    cp = poster(90, 106, (250, 246, 236), cal, tape=(200, 180, 140))
    cp.text(65, 32, "SEPT", 12, (255, 255, 255))
    c.stamp(cp, 1500, 420, angle=2)

    # --- cork board with photos
    c.paint(wonky(1290, 228, 1420, 330, 2, rng), (196, 150, 96), oc=(120, 76, 46),
            pattern=lambda p: [p.ell(1290 + rng.uniform(10, 120), 228 + rng.uniform(10, 92), 1.5, 1.5,
                                     (150, 100, 60)) for _ in range(60)])
    for px, py, a, col in ((1318, 270, -8, (120, 190, 230)), (1360, 262, 6, (250, 170, 120)),
                           (1394, 292, -4, (170, 220, 140))):
        ph = Canvas(48, 54, ow=2.5)
        ph.paint(rect(4, 4, 44, 50), (250, 248, 240))
        ph.paint(rect(9, 9, 39, 38), col, ow=0)
        ph.paint(ell(24, 30, 7, 9), dk(col, 0.6), ow=0)
        c.stamp(ph, px, py, a)
        c.paint(ell(px, py - 22, 4, 4), (230, 50, 60), ow=2)
    # --- wall clock above the door (it is late!)
    c.paint(ell(1720, 410, 36, 36), (240, 196, 80), shade=(-4, -4), hi=(3, 3, (255, 236, 160), 2))
    c.paint(ell(1720, 410, 27, 27), (252, 248, 236), ow=3)
    for k in range(12):
        a = math.radians(k * 30)
        c.line([(1720 + 21 * math.cos(a), 410 + 21 * math.sin(a)), (1720 + 24 * math.cos(a), 410 + 24 * math.sin(a))], 2)
    c.line([(1720, 410), (1720, 392)], 3.5)
    c.line([(1720, 410), (1734, 404)], 3.5)

    # --- door to hallway (x 1650-1790, y 500-800), knob on the left
    door(c, 1650, 500, 1790, 800, (186, 108, 58), knob="L")
    c.paint(rect(1704, 538, 1760, 590), (255, 236, 110), ow=2.5, shade=(-3, -3))
    c.text(1732, 556, "KNOCK", 9, (200, 40, 70))
    c.text(1732, 572, "FIRST!!", 9, (60, 60, 120))
    c.paint(ell(1736, 650, 14, 14), (250, 248, 240), ow=3)  # hook + towel
    c.paint(poly([(1724, 650), (1748, 650), (1754, 730), (1718, 734)], 1), (90, 190, 170), ow=3,
            shade=(-4, 0), pattern=lambda p: p.rect(1716, 700, 1756, 708, (250, 240, 200)))

    # --- string lights across the top
    bulbs = string_lights(c, [(10, 70), (480, 120), (960, 74), (1440, 120), (1910, 70)],
                          [(255, 210, 90), (255, 120, 150), (120, 220, 255), (255, 160, 70), (170, 255, 140)], sag=26)

    # --- lighting
    lights = [(1250, 700, 700, 0.75, (255, 196, 120)),  # desk lamp
              (985, 640, 360, 0.45, (255, 120, 170)),  # lava lamp
              (1138, 700, 220, 0.35, (150, 190, 255)),  # laptop
              (430, 390, 420, 0.30, (140, 150, 255)),  # moonlight
              (960, 100, 1100, 0.20, (255, 200, 150))]  # string lights wash
    light_pass(c, 0.62, lights, vign=0.5)
    c.glow(1250, 704, 170, (255, 200, 120), 0.45)
    c.glow(985, 648, 90, (255, 120, 170), 0.5)
    c.glow(1138, 700, 60, (160, 200, 255), 0.35)
    for x, y, col in bulbs:
        c.glow(x, y, 30, col, 0.55)
    c.save("bg_dex_room.png")


# =========================================================================== 2. dorm hallway
def drop_ceiling(c, y1, color, vp=(960, 520), panels=()):
    c.paint(rect(0, 0, W_BG, y1), ("vy", 0, y1, dk(color, 0.8), color), ow=0)
    for y in (26, 62, 104):
        if y < y1:
            c.line([(0, y), (W_BG, y)], 2.5, dk(color, 0.65), opacity=0.8)
    for xb in range(-1200, W_BG + 1300, 160):
        xa = vp[0] + (xb - vp[0]) * (vp[1] - y1) / vp[1]
        c.line([(xb, 0), (xa, y1)], 2.5, dk(color, 0.65), opacity=0.8)
    for cx in panels:
        k = (cx - vp[0])
        c.paint(poly([(cx - 96, 28), (cx + 96, 28), (cx + 86 - k * 0.04, 92), (cx - 86 - k * 0.04, 92)]),
                (250, 250, 236), ow=3, pattern=lambda p, cx=cx: [p.line([(cx - 80 + i * 40, 34), (cx - 74 + i * 38, 88)],
                                                                         2, (215, 225, 220)) for i in range(5)])
    c.line([(0, y1), (W_BG, y1)], 4)


def carpet(c, base, y0=WALL_Y, seed=21):
    c.paint(rect(0, y0, W_BG, H_BG), ("vy", y0, H_BG, lt(base, 0.08), dk(base, 0.85)), ow=0)
    # worn path down the middle
    c.paint(ell(960, 900, 980, 70), lt(base, 0.18), ow=0, opacity=0.5)
    rng = random.Random(seed)
    vp = (960, 380)
    rows = [y0 + (H_BG - y0) * ((i / 9) ** 1.5) for i in range(10)]
    for ri, y in enumerate(rows[1:-1]):
        t = (y - vp[1]) / (H_BG - vp[1])
        step = 120 * t
        off = (ri % 2) * step / 2
        x = vp[0] - 1300 * t + off
        while x < W_BG + 40:
            sz = 10 * t + 2
            c.paint(poly([(x, y - sz * 0.5), (x + sz, y), (x, y + sz * 0.5), (x - sz, y)]), (220, 170, 70), ow=0,
                    opacity=0.45)
            x += step
    for _ in range(9):  # stains
        sx, sy = rng.uniform(80, 1840), rng.uniform(820, 1060)
        c.paint(ell(sx, sy, rng.uniform(16, 40), rng.uniform(5, 11)), dk(base, 0.7), ow=0, opacity=0.5)


def bunting(c, x0, x1, y, letters, colors, sag=30):
    pts = bez((x0, y), ((x0 + x1) / 2, y + sag * 2), (x1, y), 60)
    c.line(pts, 3, (60, 40, 30))
    n = len(letters)
    for i, ch in enumerate(letters):
        q = pts[int((i + 0.5) / n * 60)]
        col = colors[i % len(colors)]
        c.paint(poly([(q[0] - 26, q[1]), (q[0] + 26, q[1]), (q[0], q[1] + 60)]), col, ow=3,
                shade=(-4, 0))
        if ch.strip():
            c.text(q[0], q[1] + 20, ch, 22, (255, 250, 230), stroke=2)


def paint_dorm_hallway():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(1999)
    upper, lower = (234, 178, 92), (44, 128, 124)
    c.paint(rect(0, 0, W_BG, 560), ("vy", 120, 560, (214, 150, 76), upper), ow=0)
    # subtle vertical paint streaks
    for x in range(0, W_BG, 44):
        c.line([(x + rng.uniform(-4, 4), 130), (x + rng.uniform(-4, 4), 556)], 6, (255, 220, 160),
               opacity=0.06)
    block_wall(c, 0, 560, W_BG, WALL_Y, lower, dk(lower, 0.9), bw=120, bh=46, mortar=0.25, seed=22)
    c.paint(rect(-10, 552, W_BG + 10, 570), (150, 92, 56), ow=3, hi=(0, 4, (196, 130, 80)), shade=(0, -4))
    drop_ceiling(c, 130, (210, 200, 180), panels=(330, 960, 1590))
    carpet(c, (150, 44, 56))
    baseboard(c, color=(60, 40, 36))

    # --- party bunting + streamers
    for (a, b, col) in ((0, 640, (240, 70, 120)), (600, 1300, (70, 190, 230)), (1260, 1920, (250, 200, 50))):
        c.line(bez((a, 140), ((a + b) / 2, 210), (b, 140), 30), 6, col)
        c.line(bez((a, 146), ((a + b) / 2, 196), (b, 146), 30), 3, lt(col, 0.4))
    bunting(c, 620, 1340, 168, list("PARTY!!"), [(230, 60, 80), (250, 170, 40), (60, 170, 120), (80, 120, 220),
                                                 (200, 80, 200)], sag=18)

    # --- room 214 door (x 80-200, y 500-800)
    door(c, 80, 500, 200, 790, (70, 110, 190), knob="R")
    c.paint(rrect(112, 524, 168, 552, 6), (240, 196, 80), shade=(-3, -3), hi=(3, 3, (255, 236, 160), 2))
    c.text(140, 538, "214", 17, OUT)
    c.paint(rect(100, 580, 180, 640), (250, 250, 246), ow=3, shade=(-3, -3, (220, 220, 230)))
    c.text(140, 600, "DEX +", 12, (40, 80, 200), "Bold")
    c.text(140, 620, "GIL", 12, (200, 40, 60), "Bold")
    c.line([(160, 598), (170, 590)], 2, (200, 40, 60))

    # --- lounge doorway (x 380-540, y 500-800)
    cas = (236, 210, 170)
    c.paint(rect(366, 486, 554, 792), cas, shade=(-5, 0, dk(cas, 0.75)))

    def lounge_peek(p):
        p.rect(380, 500, 540, 800, (176, 70, 84))
        for x in range(392, 540, 40):
            p.poly([(x, 540), (x + 7, 548), (x, 556), (x - 7, 548)], (220, 150, 80))
            p.poly([(x + 20, 590), (x + 27, 598), (x + 20, 606), (x + 13, 598)], (220, 150, 80))
        p.rect(380, 630, 540, 712, (126, 74, 44))
        for x in range(380, 540, 24):
            p.line([(x, 632), (x, 712)], 1.5, (90, 52, 34))
        p.rect(380, 626, 540, 634, (90, 52, 34))
        for r in range(3):
            for k in range(8):
                col = (228, 210, 170) if (r + k) % 2 else (178, 70, 60)
                p.rect(380 + k * 22 - r * 4, 712 + r * 26, 402 + k * 22 - r * 4, 738 + r * 26, col)
        # couch glimpse (avocado couch inside the lounge)
        for (a, b, cc, dd2, col) in ((452, 636, 560, 690, (120, 150, 60)), (440, 684, 560, 722, (140, 172, 70)),
                                      (432, 664, 462, 728, (110, 140, 56))):
            p.d.rounded_rectangle([a * S - p.ox, b * S - p.oy, cc * S - p.ox, dd2 * S - p.oy], radius=10 * S,
                                  fill=OUT)
            p.d.rounded_rectangle([(a + 4) * S - p.ox, (b + 4) * S - p.oy, (cc - 4) * S - p.ox,
                                   (dd2 - 4) * S - p.oy], radius=8 * S, fill=col)
        # far lamp
        p.poly([(400, 560), (430, 560), (440, 600), (390, 600)], (255, 230, 150))
        p.line([(415, 600), (415, 700)], 4, OUT)
        # shadow at the door edge (depth)
        p.poly([(380, 500), (400, 500), (400, 800), (380, 800)], (120, 60, 40))
        p.poly([(380, 500), (540, 500), (540, 516), (380, 516)], (120, 60, 40))
    c.paint(rect(380, 500, 540, 790), (230, 140, 70), ow=3, pattern=lounge_peek)
    # LOUNGE sign above doorway
    c.paint(cap([(410, 432), (426, 446)], 3), (80, 80, 90), ow=0)
    c.paint(cap([(510, 432), (494, 446)], 3), (80, 80, 90), ow=0)
    c.paint(rrect(390, 440, 530, 478, 8), (60, 60, 120), shade=(-4, -4), hi=(3, 3, (110, 110, 180), 2))
    c.text(460, 460, "LOUNGE", 21, (255, 214, 70), stroke=0)
    # fire extinguisher (outside the clear zone)
    c.paint(rect(588, 610, 640, 618), (90, 90, 96), ow=3)
    c.paint(rrect(600, 626, 628, 706, 10), (220, 40, 40), shade=(-5, 0), hi=(4, 0, (255, 120, 110), 3))
    c.paint(rect(606, 612, 622, 628), (60, 60, 66), ow=3)
    c.line([(622, 618), (640, 640), (634, 680)], 4)

    # --- bulletin board with flyers
    c.paint(wonky(890, 330, 1330, 590, 2, rng), (164, 110, 64), shade=(-6, -6, (120, 80, 46)))
    c.paint(wonky(904, 344, 1316, 576, 1.5, rng), (206, 160, 104), ow=3,
            pattern=lambda p: [p.ell(rng.uniform(904, 1316), rng.uniform(344, 576), 1.6, 1.6, (160, 116, 70))
                               for _ in range(260)])
    flyers = [(950, 400, 76, 92, (250, 240, 120), -5, ["LOST:", "MY", "DIGNITY"], (60, 60, 60)),
              (1046, 392, 84, 70, (255, 160, 190), 4, ["BAND", "TRYOUTS"], (120, 30, 80)),
              (1140, 410, 80, 100, (150, 220, 250), -3, ["FREE", "PIZZA*", "*maybe"], (30, 60, 120)),
              (1240, 400, 80, 84, (250, 250, 246), 6, ["QUIET", "HOURS", "LOL"], (180, 40, 40)),
              (990, 506, 96, 76, (190, 240, 160), 3, ["SPEED", "DATING", "TONIGHT"], (40, 100, 60)),
              (1108, 516, 70, 70, (255, 200, 120), -6, ["CAT", "SITTER?"], (110, 60, 20)),
              (1220, 514, 104, 72, (220, 190, 255), 2, ["STUDY", "GROUP", "(nap club)"], (80, 40, 140))]
    for fx, fy, fw, fh, col, ang, lines, tc in flyers:
        sub = Canvas(fw + 20, fh + 20, ow=2.5)
        sub.paint(rect(10, 10, 10 + fw, 10 + fh), col, shade=(-3, -3))
        n = len(lines)
        tabs = fh > 80
        th = fh - (18 if tabs else 0)
        for i, ln in enumerate(lines):
            size = 14 if i == 0 else (13 if not ln.startswith("*") and not ln.startswith("(") else 9)
            sub.text(10 + fw / 2, 10 + th * (i + 0.7) / (n + 0.4), ln, size, tc, "Black" if i < 2 else "Bold")
        # tear-off tabs on some
        if tabs:
            for k in range(5):
                sub.line([(16 + k * (fw - 12) / 5, 10 + fh - 14), (16 + k * (fw - 12) / 5, 10 + fh)], 1.5)
        c.stamp(sub, fx, fy, ang)
        c.paint(ell(fx, fy - fh / 2 + 4, 5, 5), rng.choice([(230, 50, 60), (50, 120, 230), (40, 170, 80)]), ow=2)

    # --- water fountain + balloons
    c.paint(rect(1290, 660, 1370, 680), (190, 196, 204), shade=(0, -4))
    c.paint(poly([(1280, 640), (1380, 640), (1372, 664), (1288, 664)]), (210, 216, 224), shade=(0, -5),
            hi=(0, 4, (245, 248, 252)))
    c.paint(rect(1322, 680, 1338, 790), (150, 156, 166), shade=(-3, 0))
    c.line([(1316, 648), (1322, 640), (1334, 642)], 3.5, (150, 156, 166))
    c.paint(rrect(1352, 646, 1364, 656, 3), (160, 160, 170), ow=2.5)
    for bx, by, col in ((1318, 470, (240, 60, 100)), (1356, 446, (250, 200, 50)), (1386, 486, (70, 170, 240))):
        c.curve((bx, by + 40), (bx + 10, by + 110), (1330, 640), 2, (60, 60, 60))
        c.paint(ell(bx, by, 26, 32), col, shade=(-5, -6), hi=(5, 5, lt(col, 0.6), 4))
        c.paint(poly([(bx - 5, by + 36), (bx + 5, by + 36), (bx, by + 30)]), col, ow=2.5)

    # --- drinks table (x 1000-1220, y 770-870)
    c.shadow(1110, 870, 128, 14, 0.5)
    for lx in (1024, 1196):
        c.line([(lx - 10, 816), (lx + 8, 868)], 6, (90, 90, 100))
        c.line([(lx + 10, 816), (lx - 8, 868)], 6, (70, 70, 80))
    c.paint(poly([(1004, 806), (1216, 806), (1220, 816), (1000, 816)]), (236, 236, 228), ow=3)
    # plastic tablecloth with scalloped edge
    scal = [(1000, 806), (1220, 806), (1222, 830)]
    for i in range(11):
        x = 1222 - i * 20
        scal += [(x - 10, 842), (x - 20, 830)]
    c.paint(poly(scal, 1), (230, 60, 70), shade=(-4, 0), hi=(0, 3, (255, 130, 130)),
            pattern=lambda p: [p.rect(x, 806, x + 10, 844, (250, 240, 236)) for x in range(1006, 1220, 20)])
    # stack of red cups
    for i, cx in enumerate((1016, 1034)):
        c.paint(poly([(cx - 8, 806), (cx + 8, 806), (cx + 10, 778), (cx - 10, 778)]), (220, 40, 50),
                shade=(-3, 0), hi=(0, 4, (250, 250, 250)))
    c.paint(poly([(1025, 778), (1041, 778), (1043, 770), (1023, 770)]), (220, 40, 50), ow=3)
    # bottles
    for bx, col, lab, h in ((1064, (60, 160, 80), (250, 220, 80), 40), (1092, (240, 130, 30), (250, 250, 240), 34),
                            (1176, (120, 50, 40), (220, 40, 50), 42)):
        top = 806 - h
        sh = poly([(bx - 9, 806), (bx + 9, 806), (bx + 9, top + 18), (bx + 4, top + 8), (bx + 3, top),
                   (bx - 3, top), (bx - 4, top + 8), (bx - 9, top + 18)], 1)
        c.paint(sh, col, shade=(-3, 0), hi=(3, 0, lt(col, 0.5), 2))
        c.paint(rect(bx - 9, top + 22, bx + 9, top + 32), lab, ow=2)
        c.paint(rect(bx - 4, top - 3, bx + 4, top + 2), (230, 230, 230), ow=2)
    # lemon
    c.paint(ell(1128, 796, 15, 11, -10), (255, 222, 50), shade=(-3, -3, (230, 170, 30)),
            hi=(3, 3, (255, 250, 170), 3))
    c.paint(ell(1142, 792, 4, 3), (255, 222, 50), ow=2.5)
    # ice bucket
    c.paint(poly([(1146, 806), (1158, 806), (1160, 790), (1144, 790)]), (180, 220, 240), ow=2.5)

    # --- vending machine (x 1650-1790, y 500-800)
    c.shadow(1720, 800, 86, 12, 0.5)
    vm = (200, 40, 50)
    c.paint(wonky(1650, 500, 1790, 800, 1.5, rng), vm, shade=(-8, 0, dk(vm, 0.72)), hi=(0, 6, (240, 90, 90)))
    c.paint(rrect(1660, 508, 1780, 538, 6), (250, 220, 60), ow=3)
    c.text(1720, 523, "SNAX!", 22, vm)

    def snacks(p):
        cols = [(250, 90, 90), (90, 200, 120), (250, 200, 60), (90, 140, 240), (240, 130, 220), (250, 150, 50)]
        for r in range(5):
            y = 556 + r * 34
            p.rect(1664, y + 22, 1746, y + 26, (150, 160, 170))
            for k in range(4):
                p.d.rounded_rectangle([(1668 + k * 20) * S - p.ox, (y + 2) * S - p.oy, (1682 + k * 20) * S - p.ox,
                                       (y + 22) * S - p.oy], radius=3 * S, fill=cols[(r * 2 + k) % 6])
        p.poly([(1668, 720), (1700, 548), (1716, 548), (1684, 720)], (255, 255, 255, 60))
    c.paint(rect(1662, 548, 1750, 730), ("v", (190, 230, 250), (120, 170, 210)), ow=3, pattern=snacks)
    c.paint(rect(1756, 556, 1780, 640), (60, 60, 70), ow=3,
            pattern=lambda p: [p.rect(1760, 562 + i * 12, 1776, 570 + i * 12, (250, 220, 90)) for i in range(6)])
    c.paint(rect(1760, 650, 1776, 666), (40, 40, 46), ow=2.5)
    c.paint(rect(1670, 744, 1750, 778), (40, 30, 40), ow=3)
    # trash can at hall end
    c.shadow(1860, 800, 34, 6)
    c.paint(poly([(1832, 720), (1888, 720), (1882, 800), (1838, 800)]), (90, 120, 150), shade=(-5, 0),
            pattern=lambda p: [p.line([(1844 + i * 10, 724), (1846 + i * 9, 796)], 2, (70, 96, 124)) for i in range(5)])
    c.paint(poly([(1840, 720), (1852, 702), (1868, 708), (1880, 720)], 1), (250, 248, 240), ow=3)
    c.paint(ell(1864, 712, 9, 7), (220, 40, 50), ow=2.5)
    # EXIT sign
    c.paint(rrect(1806, 300, 1906, 340, 4), (30, 30, 30), ow=3)
    c.text(1856, 320, "EXIT", 22, (255, 70, 60))

    lights = [(330, 120, 640, 0.35, (230, 245, 255)), (960, 120, 700, 0.40, (230, 245, 255)),
              (1590, 120, 640, 0.35, (230, 245, 255)),
              (460, 650, 300, 0.50, (255, 170, 90)), (1710, 640, 320, 0.45, (150, 220, 255)),
              (1856, 320, 120, 0.4, (255, 60, 60))]
    light_pass(c, 0.72, lights, vign=0.5)
    c.glow(460, 640, 160, (255, 170, 90), 0.35)
    c.glow(1706, 640, 150, (160, 220, 255), 0.30)
    for cx in (330, 960, 1590):
        c.glow(cx, 60, 140, (240, 250, 255), 0.45)
    c.glow(1856, 320, 70, (255, 60, 60), 0.4)
    c.save("bg_dorm_hallway.png")


# =========================================================================== 3. lounge
def checker_floor(c, c1, c2, vp=(960, 260), y0=WALL_Y, cols=110, rows=7):
    ys = [y0 + (H_BG - y0) * ((i / rows) ** 1.45) for i in range(rows + 1)]
    xs = list(range(-2400, W_BG + 2400, cols))

    def X(xb, y):
        return vp[0] + (xb - vp[0]) * (y - vp[1]) / (H_BG - vp[1])
    for r in range(rows):
        ya, yb = ys[r], ys[r + 1]
        for k in range(len(xs) - 1):
            col = c1 if (r + k) % 2 == 0 else c2
            q = [(X(xs[k], ya), ya), (X(xs[k + 1], ya), ya), (X(xs[k + 1], yb), yb), (X(xs[k], yb), yb)]
            if q[1][0] < -50 or q[0][0] > W_BG + 50:
                if q[2][0] < -50 or q[3][0] > W_BG + 50:
                    continue
            c.paint(poly(q), col, ow=0)
    for y in ys[1:]:
        c.line([(0, y), (W_BG, y)], 1.6, (60, 30, 30), opacity=0.35)
    for xb in xs:
        c.line([(X(xb, y0), y0), (X(xb, H_BG), H_BG)], 1.6, (60, 30, 30), opacity=0.35)
    # floor sheen
    c.paint(ell(1150, 900, 600, 60), (255, 250, 230), ow=0, opacity=0.08)


def paint_lounge():
    c = Canvas(W_BG, H_BG, ow=4, bg=(0, 0, 0))
    rng = random.Random(77)
    wp = (176, 70, 84)

    def wallpaper(p):
        for x in range(0, W_BG + 60, 60):
            p.rect(x, 0, x + 26, 560, dk(wp, 0.9))
            for y in range(40, 560, 70):
                yy = y + (35 if (x // 60) % 2 else 0)
                p.poly([(x + 43, yy - 10), (x + 51, yy), (x + 43, yy + 10), (x + 35, yy)], (220, 150, 80))
    c.paint(rect(0, 0, W_BG, 560), ("vy", 0, 560, dk(wp, 0.8), wp), ow=0, pattern=wallpaper)
    # wood paneling
    pan = (126, 74, 44)

    def boards(p):
        for x in range(0, W_BG, 48):
            p.line([(x, 566), (x, WALL_Y)], 2.5, dk(pan, 0.6))
            p.line([(x + 4, 566), (x + 4, WALL_Y)], 1.5, lt(pan, 0.25))
            p.line([(x + 22 + rng.uniform(-6, 6), 590), (x + 22 + rng.uniform(-6, 6), 760)], 1.5, dk(pan, 0.82))
    c.paint(rect(0, 560, W_BG, WALL_Y), ("vy", 560, WALL_Y, lt(pan, 0.08), dk(pan, 0.9)), ow=0, pattern=boards)
    c.paint(rect(-10, 552, W_BG + 10, 570), (90, 52, 34), ow=3, hi=(0, 4, (150, 96, 60)), shade=(0, -4))
    c.paint(rect(0, 0, W_BG, 44), (96, 40, 54), ow=0)
    c.paint(rect(-10, 38, W_BG + 10, 54), (236, 210, 170), ow=3, shade=(0, -4))
    checker_floor(c, (228, 210, 170), (178, 70, 60))
    baseboard(c, color=(80, 46, 30))

    # --- exit doorway to hallway (x 80-200, y 500-800)
    cas = (236, 210, 170)
    c.paint(rect(66, 486, 214, 792), cas, shade=(-5, 0, dk(cas, 0.75)))

    def hall_peek(p):
        p.rect(80, 500, 200, 800, (234, 178, 92))
        p.rect(80, 650, 200, 760, (44, 128, 124))
        p.rect(80, 646, 200, 654, (150, 92, 56))
        p.rect(80, 740, 200, 800, (150, 44, 56))
        p.rect(80, 735, 200, 742, (60, 40, 36))
        p.rect(130, 560, 170, 600, (255, 160, 190))  # a flyer across the hall
        p.poly([(80, 500), (96, 500), (96, 800), (80, 800)], (120, 80, 50))
        p.poly([(80, 500), (200, 500), (200, 514), (80, 514)], (120, 80, 50))
    c.paint(rect(80, 500, 200, 790), (234, 178, 92), ow=3, pattern=hall_peek)
    c.paint(rrect(84, 436, 196, 472, 6), (40, 120, 70), shade=(-3, -3), hi=(3, 3, (90, 180, 120), 2))
    c.text(150, 454, "HALL", 17, (255, 255, 240))
    c.paint(poly([(96, 454), (116, 442), (116, 466)]), (255, 255, 240), ow=0)

    # --- window with half-open blinds
    night_window(c, 270, 230, 490, 470, seed=31, frame=(236, 214, 178))

    def blinds(p):
        for y in range(232, 352, 12):
            p.rect(270, y, 490, y + 9, (236, 226, 196))
            p.line([(270, y + 9), (490, y + 9)], 1.5, (160, 140, 110))
    c.paint(rect(270, 230, 490, 352), (236, 226, 196), ow=3, pattern=blinds)
    c.line([(470, 352), (474, 420)], 2, (200, 190, 160))

    # --- soda + snack posters (original brands)
    def fizz(p, ox, oy):
        p.rect(ox, oy, ox + 130, oy + 180, (40, 150, 200))
        for k in range(12):
            a = math.radians(k * 30)
            p.poly([(ox + 65, oy + 110), (ox + 65 + 140 * math.cos(a), oy + 110 + 140 * math.sin(a)),
                    (ox + 65 + 140 * math.cos(a + 0.26), oy + 110 + 140 * math.sin(a + 0.26))], (70, 180, 220))
        # bottle
        p.poly([(ox + 50, oy + 168), (ox + 80, oy + 168), (ox + 80, oy + 110), (ox + 72, oy + 92), (ox + 72, oy + 72),
                (ox + 58, oy + 72), (ox + 58, oy + 92), (ox + 50, oy + 110)], OUT)
        p.poly([(ox + 54, oy + 164), (ox + 76, oy + 164), (ox + 76, oy + 112), (ox + 68, oy + 94), (ox + 68, oy + 76),
                (ox + 62, oy + 76), (ox + 62, oy + 94), (ox + 54, oy + 112)], (240, 120, 40))
        p.rect(ox + 54, oy + 124, ox + 76, oy + 140, (255, 240, 200))
        for bx, by in ((40, 90), (92, 80), (30, 140), (100, 130), (86, 100)):
            p.ell(ox + bx, oy + by, 5, 5, (220, 245, 255))
    fp = poster(130, 180, (40, 150, 200), fizz)
    fp.text(85, 48, "FIZZ-O", 26, (255, 230, 80), stroke=2.5)
    fp.text(85, 180, "TASTES LIKE ORANGE-ISH!", 8, (255, 255, 255), "Bold")
    c.stamp(fp, 690, 380, angle=-3)

    def zing(p, ox, oy):
        p.rect(ox, oy, ox + 120, oy + 150, (250, 200, 50))
        p.poly([(ox + 20, oy + 140), (ox + 60, oy + 60), (ox + 100, oy + 140)], (230, 60, 50))
        p.ell(ox + 60, oy + 112, 20, 14, (255, 236, 150))
    zp = poster(120, 150, (250, 200, 50), zing)
    zp.text(80, 50, "ZING!", 28, (200, 40, 50), "Italic", stroke=2, sc=(255, 250, 230))
    zp.text(80, 76, "CHEEZ CURLS", 11, OUT, "Black")
    c.stamp(zp, 1420, 340, angle=4)

    # --- pendant lamp over the couch
    c.line([(760, 54), (760, 150)], 3)
    c.paint(poly([(716, 196), (804, 196), (788, 150), (732, 150)], 1), (240, 130, 50), shade=(-5, 0),
            hi=(4, 0, (255, 190, 110), 3))
    c.paint(ell(760, 198, 18, 8), (255, 240, 170), ow=3)

    # --- floor lamp left of the couch
    c.shadow(556, 790, 34, 6)
    c.paint(ell(556, 786, 26, 6), (60, 60, 70), ow=3)
    c.line([(556, 786), (556, 560)], 5, (70, 70, 80))
    c.paint(poly([(520, 560), (592, 560), (580, 504), (532, 504)], 1), (250, 230, 170), shade=(-5, 0),
            hi=(4, 0, (255, 250, 220), 3))

    # --- couch (x 610-910, y 760-880)
    c.shadow(760, 878, 170, 14, 0.5)
    cc = (120, 158, 58)
    c.paint(wonky(626, 760, 894, 830, 2, rng), dk(cc, 0.9), shade=(0, -6, dk(cc, 0.7)))  # back
    for x0 in (636, 724, 812):
        c.paint(wonky(x0, 770, x0 + 82, 826, 2, rng), cc, ow=3.5, shade=(-4, -5), hi=(3, 4, lt(cc, 0.35), 2))
    c.paint(wonky(632, 818, 888, 862, 2, rng), dk(cc, 0.82), shade=(0, -5, dk(cc, 0.62)))  # base
    for x0 in (642, 728, 814):
        c.paint(wonky(x0, 812, x0 + 82, 840, 2, rng), lt(cc, 0.1), ow=3.5, shade=(0, -4), hi=(0, 3, lt(cc, 0.4), 1))
    for ax in (610, 868):
        c.paint(wonky(ax, 788, ax + 42, 868, 2, rng), cc, shade=(-5, -5), hi=(3, 3, lt(cc, 0.35), 2))
        c.paint(ell(ax + 21, 792, 22, 9), lt(cc, 0.15), ow=3.5)
    for fx in (630, 890):
        c.paint(poly([(fx - 8, 866), (fx + 8, 866), (fx + 5, 880), (fx - 5, 880)]), (70, 40, 30), ow=3)
    # throw pillow + pizza slice on the couch
    c.paint(poly([(650, 790), (690, 782), (700, 818), (656, 822)], 1), (240, 120, 160), shade=(-4, -4),
            pattern=lambda p: p.line([(660, 800), (690, 796)], 3, (255, 220, 120)))
    c.paint(poly([(820, 834), (868, 826), (846, 846)]), (250, 200, 80), ow=3,
            pattern=lambda p: [p.ell(840, 832, 4, 3, (210, 60, 50)), p.ell(852, 834, 3, 2, (210, 60, 50))])
    c.paint(cap([(820, 834), (868, 826)], 5), (200, 130, 60), ow=2.5)

    # --- pizza boxes stacked on the floor
    c.shadow(966, 880, 54, 8)
    for i, (y, dx) in enumerate(((862, 0), (848, 6), (834, -4))):
        c.paint(poly([(920 + dx, y), (1010 + dx, y), (1014 + dx, y + 16), (916 + dx, y + 16)]), (226, 186, 130),
                ow=3, shade=(0, -3, (190, 150, 100)))
        c.text(964 + dx, y + 9, "PIZZA" if i == 1 else "", 8, (200, 50, 40))
    c.paint(poly([(918, 834), (1012, 834), (1004, 806), (926, 806)]), (236, 200, 150), ow=3)  # open lid
    c.paint(poly([(930, 832), (962, 822), (950, 812)]), (250, 200, 80), ow=2.5)

    # --- TV stand + CRT TV (TV at x 1040-1280, y 540-700)
    c.shadow(1160, 800, 140, 12, 0.5)
    st = (150, 88, 50)
    c.paint(wonky(1030, 700, 1290, 794, 1.5, rng), st, shade=(-7, 0, dk(st, 0.72)), hi=(0, 5, lt(st, 0.3)))
    c.paint(rect(1046, 716, 1150, 780), dk(st, 0.55), ow=3)
    c.paint(rrect(1056, 724, 1140, 742, 3), (50, 50, 56), ow=2.5,
            pattern=lambda p: [p.rect(1066, 731, 1096, 735, (100, 255, 140)), p.ell(1128, 733, 3, 3, (255, 80, 60))])
    c.paint(rrect(1064, 752, 1128, 776, 6), (90, 70, 140), ow=2.5,
            pattern=lambda p: p.ell(1078, 764, 5, 5, (255, 220, 80)))
    c.line([(1128, 770), (1160, 790), (1190, 786)], 2.5, (40, 40, 40))
    c.paint(ell(1200, 786, 14, 6), (200, 60, 60), ow=2.5)
    c.paint(rect(1164, 716, 1274, 780), lt(st, 0.1), ow=3, shade=(-4, -4))
    c.paint(ell(1176, 748, 5, 5), (240, 196, 80), ow=2)
    # antenna
    c.line([(1150, 540), (1100, 470)], 3, (170, 170, 180))
    c.line([(1170, 540), (1226, 476)], 3, (170, 170, 180))
    c.paint(ell(1100, 470, 5, 5), (170, 170, 180), ow=2.5)
    c.paint(ell(1226, 476, 5, 5), (170, 170, 180), ow=2.5)
    c.paint(ell(1160, 544, 22, 10, 0), (80, 80, 90), ow=3)
    tv = (166, 96, 52)
    c.paint(wonky(1040, 540, 1280, 700, 1.5, rng, corner=12), tv, shade=(-8, -6, dk(tv, 0.7)),
            hi=(5, 5, lt(tv, 0.3), 3))
    c.paint(rrect(1052, 552, 1212, 688, 22), (40, 36, 40), ow=3)

    def show(p):
        ox, oy = 1060, 560
        p.rect(ox - 10, oy - 10, ox + 160, oy + 140, (90, 30, 140))
        for k in range(16):
            a = math.radians(k * 22.5)
            p.poly([(ox + 72, oy + 60), (ox + 72 + 200 * math.cos(a), oy + 60 + 200 * math.sin(a)),
                    (ox + 72 + 200 * math.cos(a + 0.2), oy + 60 + 200 * math.sin(a + 0.2))], (150, 40, 170))
        # heart
        hx, hy = ox + 72, oy + 52
        p.ell(hx - 18, hy - 8, 22, 21, OUT)
        p.ell(hx + 18, hy - 8, 22, 21, OUT)
        p.poly([(hx - 40, hy), (hx + 40, hy), (hx, hy + 44)], OUT)
        p.ell(hx - 18, hy - 8, 18, 17, (240, 50, 90))
        p.ell(hx + 18, hy - 8, 18, 17, (240, 50, 90))
        p.poly([(hx - 35, hy), (hx + 35, hy), (hx, hy + 38)], (240, 50, 90))
        p.ell(hx - 24, hy - 14, 6, 5, (255, 170, 190))
    c.paint(rrect(1058, 558, 1206, 682, 18), (90, 30, 140), ow=2, pattern=show)
    c.text(1132, 586, "SPEED", 25, (255, 230, 60), "Italic", stroke=2.5, sc=(200, 30, 60), angle=6)
    c.text(1132, 616, "DATERS", 25, (255, 230, 60), "Italic", stroke=2.5, sc=(200, 30, 60), angle=6)
    c.paint(rrect(1100, 640, 1166, 664, 8), (230, 40, 50), ow=3, hi=(0, 3, (255, 120, 120)))
    c.text(1133, 652, "LIVE!", 15, (255, 255, 255))
    # scanlines + glass shine
    for y in range(560, 682, 4):
        c.line([(1058, y), (1206, y)], 0.8, (0, 0, 0), opacity=0.12)
    c.paint(poly([(1066, 600), (1090, 566), (1120, 566), (1072, 630)], 2), (255, 255, 255), ow=0, opacity=0.12)
    # control panel
    c.paint(rect(1220, 556, 1270, 688), dk(tv, 0.75), ow=3,
            pattern=lambda p: [p.line([(1226, 630 + i * 8), (1264, 630 + i * 8)], 2.5, OUT) for i in range(7)])
    for ky in (576, 606):
        c.paint(ell(1245, ky, 11, 11), (220, 210, 190), shade=(-2, -2), hi=(2, 2, (255, 255, 250), 1))
        c.line([(1245, ky), (1252, ky - 6)], 2.5)

    # --- sign-up clipboard (x 1520-1600, y 440-540) + card above it
    c.paint(rect(1514, 382, 1606, 428), (255, 250, 236), ow=3, shade=(-3, -3, (230, 220, 200)))
    c.text(1560, 396, "CONTESTANT", 9.5, (200, 30, 60), "Black")
    c.text(1560, 414, "SIGN-UP \u2193", 12, (60, 40, 120), "Black")
    c.paint(ell(1560, 384, 5, 5), (40, 120, 230), ow=2)
    c.paint(wonky(1522, 450, 1598, 540, 1.5, rng, corner=6), (186, 130, 72), shade=(-4, -4),
            hi=(3, 3, (220, 170, 110), 2))

    def sheet(p):
        for i in range(7):
            y = 476 + i * 8.5
            p.line([(1534, y), (1586, y)], 1.4, (150, 170, 210))
        p.line([(1536, 476), (1562, 474)], 1.8, (40, 60, 160))
        p.line([(1536, 485), (1556, 484)], 1.8, (200, 40, 80))
    c.paint(rect(1530, 462, 1590, 534), (250, 250, 244), ow=2.5, pattern=sheet)
    c.paint(rrect(1544, 440, 1576, 466, 4), (170, 176, 186), ow=3, hi=(0, 3, (230, 236, 240)))
    c.paint(ell(1560, 448, 4, 4), (60, 60, 66), ow=0)
    c.line([(1592, 510), (1612, 556)], 3, (220, 200, 60))  # pen on a string
    c.paint(cap([(1610, 552), (1622, 590)], 6), (40, 120, 230), ow=2.5)

    # --- plants
    def plant(x, base_y, h, pot):
        c.shadow(x, base_y, 40, 6)
        c.paint(poly([(x - 28, base_y - 46), (x + 28, base_y - 46), (x + 22, base_y), (x - 22, base_y)]), pot,
                shade=(-5, 0), hi=(4, 0, lt(pot, 0.3), 3))
        c.paint(rect(x - 32, base_y - 54, x + 32, base_y - 42), dk(pot, 0.85), ow=3)
        r2 = random.Random(x)
        leaves = []
        for k in range(13):
            a = -90 + (k - 6) * 13 + r2.uniform(-6, 6)
            L = h * r2.uniform(0.45, 0.8) * (1 - abs(k - 6) * 0.04)
            ex = x + L * math.cos(math.radians(a))
            ey = base_y - 50 + L * math.sin(math.radians(a))
            leaves.append((L, a, ex, ey))
        for L, a, ex, ey in sorted(leaves):
            c.curve((x, base_y - 50), ((x + ex) / 2, ey + (base_y - 50 - ey) * 0.5), (ex, ey), 4, (60, 110, 50))
        for L, a, ex, ey in sorted(leaves, key=lambda q: -q[0]):
            c.paint(ell(ex, ey, 26, 13, a), (70, 160, 70), ow=3, shade=(0, 4, (50, 120, 60)),
                    hi=(0, -3, (140, 210, 110), 2))
            c.line([(ex - 18 * math.cos(math.radians(a)), ey - 18 * math.sin(math.radians(a))),
                    (ex + 16 * math.cos(math.radians(a)), ey + 16 * math.sin(math.radians(a)))], 1.6, (40, 110, 50))
    plant(1392, 792, 120, (220, 110, 60))
    plant(1856, 792, 150, (60, 120, 190))
    # beanbag
    c.shadow(1700, 868, 90, 12, 0.45)
    c.paint(poly([(1620, 864), (1622, 820), (1660, 790), (1720, 784), (1772, 800), (1790, 840), (1782, 868)], 2, True),
            (250, 150, 40), shade=(-7, -6), hi=(5, 5, (255, 210, 120), 3))
    c.line([(1660, 824), (1700, 836), (1740, 826)], 3)
    # dartboard
    for r, col in ((40, (40, 40, 40)), (32, (230, 60, 60)), (22, (250, 240, 220)), (12, (40, 160, 90)),
                   (5, (230, 60, 60))):
        c.paint(ell(1740, 320, r, r), col, ow=3 if r == 40 else 2)
    c.line([(1758, 304), (1784, 286)], 3, (240, 196, 80))

    lights = [(760, 220, 620, 0.55, (255, 190, 110)), (556, 540, 420, 0.5, (255, 214, 140)),
              (1132, 620, 380, 0.45, (220, 120, 255)), (380, 360, 330, 0.25, (140, 150, 255)),
              (140, 640, 200, 0.25, (255, 200, 120))]
    light_pass(c, 0.62, lights, vign=0.5)
    c.glow(760, 210, 150, (255, 200, 120), 0.5)
    c.glow(556, 540, 120, (255, 220, 150), 0.45)
    c.glow(1132, 620, 160, (230, 120, 255), 0.30)
    c.save("bg_lounge.png")


# =========================================================================== character helpers
def eye(c, cx, cy, rx, ry, px, py, pr, lid=0.0, lid_tilt=0.0, skin=(255, 210, 170), lashes=0, iris=None,
        ow=2.2, rot=0):
    """Big cartoon eye. (px, py) = pupil centre, lid = fraction of the eye covered by the upper lid."""
    shape = ell(cx, cy, rx, ry, rot)
    c.paint(shape, (255, 255, 255), ow=ow, shade=(0, -1.6, (214, 214, 236)))
    if iris:
        c.paint(ell(px, py, pr * 1.75, pr * 1.9), iris, ow=0, clip=shape)
    c.paint(ell(px, py, pr, pr * 1.1), (24, 16, 14), ow=0, clip=shape)
    c.paint(ell(px - pr * 0.45, py - pr * 0.55, pr * 0.45, pr * 0.45), (255, 255, 255), ow=0, clip=shape)
    if lid > 0:
        ly = cy - ry + 2 * ry * lid
        lidsh = poly([(cx - rx - 3, cy - ry - 3), (cx + rx + 3, cy - ry - 3), (cx + rx + 3, ly + lid_tilt),
                      (cx - rx - 3, ly - lid_tilt)])
        c.paint(lidsh, skin, ow=0, clip=shape)
        c.line([(cx - rx - 0.5, ly - lid_tilt), (cx + rx + 0.5, ly + lid_tilt)], 2.4)
    if lashes:
        sgn = lashes  # +1 lashes on the right, -1 on the left
        bx = cx + sgn * rx * 0.85
        by = cy - ry * 0.45 + (2 * ry * lid if lid else 0) * 0.5
        for k in range(3):
            c.line([(bx - sgn * k * 2.2, by - k * 2.2), (bx + sgn * (4 - k * 0.5), by - 4 - k * 3)], 1.6)


def hibiscus(p, x, y, r, col, center=(255, 236, 90)):
    for k in range(5):
        a = math.radians(k * 72 + x * 7)
        p.ell(x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a), r * 0.55, r * 0.42, col, rot=k * 72 + x * 7)
    p.ell(x, y, r * 0.25, r * 0.25, center)


def leaf(p, x, y, L, ang, col):
    p.ell(x, y, L, L * 0.38, col, rot=ang)
    p.line([(x - L * 0.8 * math.cos(math.radians(ang)), y - L * 0.8 * math.sin(math.radians(ang))),
            (x + L * 0.8 * math.cos(math.radians(ang)), y + L * 0.8 * math.sin(math.radians(ang)))], 0.8,
           dk(col, 0.7))


def shoe_shape(x_heel, x_toe, y_top, y_bot, toe_h=0.55, pointy=False):
    d = 1 if x_toe > x_heel else -1
    L = abs(x_toe - x_heel)
    h = y_bot - y_top
    if pointy:
        pts = [(x_heel, y_top), (x_heel + d * L * 0.4, y_top + h * 0.15), (x_heel + d * L * 0.8, y_top + h * 0.55),
               (x_toe, y_bot - 2), (x_toe - d * 4, y_bot), (x_heel - d * 2, y_bot), (x_heel - d * 3, y_top + h * 0.4)]
    else:
        pts = [(x_heel, y_top), (x_heel + d * L * 0.42, y_top - 1), (x_heel + d * L * 0.6, y_top + h * (1 - toe_h)),
               (x_toe - d * 5, y_top + h * (1 - toe_h) + 1), (x_toe, y_bot - h * 0.3), (x_toe - d * 2, y_bot),
               (x_heel - d * 2, y_bot), (x_heel - d * 4, y_top + h * 0.4)]
    return poly(pts, 2)


# =========================================================================== 4. Dex Dooley
SKIN_DEX = (255, 212, 172)
SKIN_DEX_SH = (232, 156, 128)


def paint_player_dex():
    c = Canvas(120, 260, ow=3)
    hair, hair_sh, hair_hi = (242, 118, 36), (196, 72, 30), (255, 178, 90)
    shirt = (24, 186, 196)
    khaki, khaki_sh = (220, 188, 124), (176, 140, 96)

    def shirt_print(p):
        for (x, y, r, col) in ((50, 112, 9, (255, 86, 140)), (78, 136, 10, (255, 214, 50)), (42, 148, 8, (255, 214, 50)),
                               (84, 104, 7, (255, 86, 140)), (64, 156, 7, (255, 86, 140)), (30, 96, 8, (255, 214, 50)),
                               (22, 76, 7, (255, 86, 140)), (90, 118, 7, (255, 86, 140)), (60, 126, 6, (250, 250, 240))):
            leaf(p, x + r * 0.9, y + r * 0.7, r * 0.9, 35, (60, 170, 70))
            leaf(p, x - r * 0.8, y + r * 0.8, r * 0.8, -40, (40, 140, 70))
            hibiscus(p, x, y, r, col)

    # far arm: hand scratching the back of his head (drawn first, behind everything)
    c.paint(cap([(42, 100), (19, 74), (36, 26)], 8.5), SKIN_DEX, shade=(-2.5, 0, SKIN_DEX_SH))
    c.paint(ell(38, 22, 8, 7, -30) + cap([(32, 16), (36, 9)], 4) + cap([(40, 15), (45, 9)], 4), SKIN_DEX,
            shade=(-2, 2, SKIN_DEX_SH))
    c.paint(cap([(44, 100), (32, 86)], 16), shirt, pattern=shirt_print, shade=(-3, 0))

    # legs (knock-kneed, nervous)
    c.paint(cap([(52, 150), (56, 196), (42, 234)], 16), khaki, shade=(-3, 0, khaki_sh))
    c.paint(cap([(68, 150), (63, 196), (79, 236)], 17), khaki, shade=(-3, 0, khaki_sh))
    c.line([(60, 188), (57, 200)], 1.6)
    c.paint(poly([(34, 228), (52, 228), (53, 240), (33, 240)]), khaki, ow=2.6, shade=(-2, 0, khaki_sh))
    c.paint(poly([(70, 230), (89, 230), (90, 243), (69, 243)]), khaki, ow=2.6, shade=(-2, 0, khaki_sh))
    # sneakers (pointing right)
    for xh, xt, yt, yb in ((28, 62, 236, 252), (64, 104, 239, 256)):
        sh = shoe_shape(xh, xt, yt, yb)
        c.paint(sh, (246, 244, 236), shade=(0, -2, (206, 204, 214)),
                pattern=lambda pn, xh=xh, xt=xt, yt=yt, yb=yb: (
                    pn.ell(xt - 7, yb - 5, 8, 6, (226, 50, 56)),
                    pn.rect(xh - 4, yt - 2, xh + 5, yb - 4, (226, 50, 56))))
        c.paint(rect(xh - 6, yb - 4.5, xt + 2, yb + 2), (250, 236, 200), ow=0, clip=sh)
        c.line([(xh - 2, yb - 4.5), (xt - 1, yb - 4.5)], 1.6)
        for k in range(3):
            c.line([(xh + 13 + k * 4, yt + 1 + k * 1.2), (xh + 15 + k * 4, yt + 4 + k * 1.2)], 1.4)

    # neck
    c.paint(cap([(64, 72), (64, 96)], 10.5), SKIN_DEX, shade=(-2.5, 0, SKIN_DEX_SH))
    c.paint(ell(66, 76, 7, 5), SKIN_DEX_SH, ow=0, clip=cap([(64, 72), (64, 96)], 10.5))
    c.paint(ell(68, 86, 2.6, 3), SKIN_DEX, ow=1.6)  # Adam's apple

    # torso: loud Hawaiian shirt, untucked, hem flaring
    torso = poly([(42, 93), (60, 89), (80, 92), (86, 104), (85, 132), (90, 160), (74, 164), (60, 160),
                  (46, 165), (32, 160), (37, 132), (35, 106)], 2)
    c.paint(torso, shirt, pattern=shirt_print, shade=(-5, -2, None))
    c.paint(poly([(57, 90), (72, 90), (66, 110)]), SKIN_DEX, ow=2.2)
    c.paint(poly([(52, 88), (64, 96), (60, 108), (50, 98)], 1), lt(shirt, 0.25), ow=2.2)
    c.paint(poly([(66, 96), (77, 87), (82, 97), (71, 108)], 1), lt(shirt, 0.25), ow=2.2)
    c.line([(67, 110), (70, 162)], 1.6)
    for by in (122, 138, 152):
        c.paint(ell(72, by, 1.8, 1.8), (250, 246, 230), ow=1.2)
    c.line([(46, 140), (52, 146)], 1.4)  # wrinkle

    # near arm: hanging, fidgety hand
    c.paint(cap([(82, 100), (86, 128), (94, 150)], 8.5), SKIN_DEX, shade=(-2.5, 0, SKIN_DEX_SH))
    c.paint(cap([(80, 100), (86, 114)], 16.5), shirt, pattern=shirt_print, shade=(-3, 0))
    hand = ell(96, 154, 7.5, 8.5, -15) + cap([(100, 158), (103, 165)], 3.6) + cap([(96, 160), (98, 167)], 3.6) + \
        cap([(102, 150), (106, 150)], 3.6)
    c.paint(hand, SKIN_DEX, shade=(-2, 2, SKIN_DEX_SH))

    # ---- head
    head = ell(61, 43, 27, 29) + poly([(42, 58), (56, 76), (74, 80), (86, 70), (88, 50)], 2) + ell(90, 52, 9.5, 8.5)
    c.paint(head, SKIN_DEX, shade=(-4, 3, SKIN_DEX_SH), hi=(4, 4, (255, 232, 206), 3))
    c.curve((88, 56), (92, 58), (95, 55), 1.6)  # nostril
    # cheeks + freckles
    c.paint(ell(76, 59, 6, 3.6), (255, 140, 130), ow=0, opacity=0.55)
    for fx, fy in ((72, 56), (76, 58), (80, 56), (74, 61), (79, 61)):
        c.paint(ell(fx, fy, 0.95, 0.95), (200, 110, 70), ow=0)
    # eyes: wide, tiny pupils glancing right
    eye(c, 66, 42, 8.5, 10.5, 70.5, 42, 2.6, skin=SKIN_DEX)
    eye(c, 83, 41, 6, 9.8, 86, 41, 2.3, skin=SKIN_DEX)
    # worried brows (inner ends raised)
    c.line([(57, 29), (63, 26.5), (71, 23.5)], 2.6, hair_sh)
    c.line([(79, 23.5), (85, 25.5), (89, 29)], 2.4, hair_sh)
    # nervous toothy grin
    grin = poly([(68, 64), (78, 64.5), (89, 62), (86, 69), (77, 70.5), (71, 69)], 1)
    c.paint(grin, (255, 255, 255), ow=2)
    c.line([(68.5, 66.5), (78, 67), (87.5, 65.5)], 1.2)
    for tx in (73, 78, 83):
        c.line([(tx, 64.6), (tx, 69.6)], 1.0)
    c.curve((66, 62), (65.5, 65), (68, 66), 1.6)
    # sweat drop
    c.paint(poly([(96, 22), (99, 29), (98, 33), (94, 33), (93, 29)], 2), (170, 220, 255), ow=1.8,
            hi=(-1, -1, (255, 255, 255)))

    # messy hair (spikes pointing back/up)
    hair_pts = [(36, 52), (30, 40), (21, 34), (30, 27), (22, 14), (36, 15), (36, 3), (50, 10), (60, 0), (66, 10),
                (80, 4), (80, 14), (95, 14), (86, 21), (92, 27), (80, 25), (74, 22), (68, 26), (60, 22), (52, 26),
                (48, 34), (44, 46)]
    c.paint(poly(hair_pts, 1), hair, shade=(-3, 3, hair_sh), hi=(3, 4, hair_hi, 2))
    c.line([(46, 18), (56, 12)], 1.4, hair_sh)
    c.line([(60, 16), (70, 10)], 1.4, hair_sh)
    c.line([(36, 28), (44, 24)], 1.4, hair_sh)
    # big jug ear, on top of the hair edge
    c.paint(ell(34, 50, 10.5, 14.5, -12), SKIN_DEX, shade=(-2.5, 2, SKIN_DEX_SH))
    c.curve((30, 42), (38, 44), (36, 58), 1.8)
    c.curve((33, 46), (37, 50), (35, 55), 1.2, SKIN_DEX_SH)
    c.fit(margin=3)
    c.save("player_dex.png")


# =========================================================================== shared props
def cowboy_hat(c, cx, cy, scale=1.0, rot=0.0, col=(150, 86, 42)):
    """Brown cowboy hat; (cx, cy) = middle of the brim. Used by Lacey Rae and the inventory icon."""
    sh_col, hi_col, band = dk(col, 0.72), lt(col, 0.35), (70, 40, 26)

    def T(pts):
        return rot_pts([(cx + x * scale, cy + y * scale) for x, y in pts], rot, cx, cy)
    crown = T([(-26, 0), (-28, -18), (-23, -31), (-10, -27), (0, -32), (10, -27), (23, -31), (28, -18), (26, 0)])
    c.paint(poly(crown, 2), col, shade=(4 * scale, 0, sh_col), hi=(-3 * scale, 3 * scale, hi_col, 2 * scale))
    c.paint(poly(T([(-26.5, -9), (26.5, -9), (26, -1), (-26, -1)])), band, ow=2 * scale ** 0.5)
    c.paint(ell(*T([(-12, -5)])[0], 3.2 * scale, 3.2 * scale), (220, 220, 230), ow=1.6 * scale ** 0.5)
    c.line(T([(0, -31), (1, -15)]), 1.6 * scale ** 0.5, sh_col)
    brim = T([(-50, -14), (-44, -4), (-28, 2), (0, 4), (28, 2), (44, -4), (50, -14), (52, -6), (40, 6), (20, 11),
              (0, 12), (-20, 11), (-40, 6), (-52, -6)])
    c.paint(poly(brim, 2), col, shade=(0, -3 * scale, sh_col), hi=(0, 2.5 * scale, hi_col, 1.5 * scale))
    c.paint(poly(T([(-26, -1), (0, 1.5), (26, -1), (26, 3), (0, 6), (-26, 3)]), 1), sh_col, ow=0)


# =========================================================================== 5. Lacey Rae
def paint_lacey_rae():
    c = Canvas(110, 260, ow=3)
    skin, skin_sh = (234, 172, 128), (196, 124, 96)
    hair, hair_sh, hair_hi = (250, 198, 92), (212, 140, 56), (255, 232, 160)
    denim, denim_sh, denim_hi = (66, 108, 190), (44, 72, 146), (130, 168, 232)
    pink, pink_sh = (255, 112, 168), (214, 64, 128)
    boot, boot_sh = (138, 74, 40), (98, 50, 30)

    # long hair behind the body
    c.paint(poly([(40, 44), (82, 38), (94, 60), (90, 80), (98, 98), (92, 116), (98, 132), (84, 136), (78, 124),
                  (68, 132), (62, 118), (54, 104), (44, 84)], 2, True), hair, shade=(4, 0, hair_sh),
            pattern=lambda p: [p.line(bez((70, 50), (92, 90 + k * 6), (78 + k * 6, 128)), 1.2, hair_sh)
                               for k in range(3)])
    # far arm: fist on hip, elbow out the back
    c.paint(cap([(72, 98), (90, 118), (72, 136)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(ell(70, 136, 6.5, 6), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(70, 98), (82, 108)], 14), pink, shade=(3, 2, pink_sh))
    c.paint(ell(83, 110, 3.5, 7, 50), (255, 246, 248), ow=2.2)  # rolled cuff
    # legs (jeans) - weight on the near leg, far leg cocked
    c.paint(cap([(66, 146), (70, 186), (66, 214)], 15.5), denim, shade=(3, 0, denim_sh))
    c.paint(cap([(48, 146), (43, 186), (42, 216)], 16.5), denim, shade=(3, 0, denim_sh), hi=(-2, 0, denim_hi))
    c.line([(46, 160), (44, 210)], 1.0, denim_hi)
    # cowboy boots, pointing left
    for xh, xt, yt, yb, top in ((80, 50, 238, 252, 206), (60, 20, 242, 256, 208)):
        shaft = poly([(xh - 18, top), (xh - 1, top - 2), (xh, yt + 2), (xh - 20, yt + 4)], 1)
        foot = shoe_shape(xh, xt, yt, yb, pointy=True)
        c.paint(shaft + foot, boot, shade=(3, -2, boot_sh), hi=(-2, 2, lt(boot, 0.3), 1.5))
        c.paint(rect(xh - 6, yb - 6, xh + 1, yb + 2), (70, 40, 26), ow=0, clip=foot)  # heel
        c.line([(xh - 15, top + 8), (xh - 9, top + 16), (xh - 3, top + 8)], 1.2, (230, 190, 120))
        c.line([(xh - 2, top - 1), (xh - 18, top + 1)], 1.6)
    # belt + buckle
    hips = poly([(39, 132), (75, 132), (78, 152), (36, 152)], 1)
    c.paint(hips, denim, shade=(3, 0, denim_sh))
    c.paint(rect(38, 132, 76, 139), (110, 58, 32), ow=2.2)
    c.paint(ell(48, 136, 6, 4.4), (244, 200, 80), ow=2, hi=(-1, -1, (255, 248, 200)))
    c.line([(57, 140), (57, 150)], 1.2, denim_hi)
    # neck
    c.paint(cap([(56, 80), (56, 96)], 9.5), skin, shade=(3, 0, skin_sh))
    # pink western shirt, knotted at the waist
    torso = poly([(38, 95), (54, 91), (72, 94), (76, 104), (72, 124), (72, 134), (42, 134), (36, 116), (33, 104)], 2)
    c.paint(torso, pink, shade=(4, 2, pink_sh), hi=(-3, 3, (255, 170, 205), 2))
    c.line([(36, 104), (44, 99), (56, 101), (70, 99), (75, 103)], 1.6, (255, 236, 240))  # yoke piping
    c.paint(poly([(48, 91), (63, 91), (56, 104)]), skin, ow=2.0)
    c.paint(poly([(46, 89), (55, 97), (50, 104), (42, 96)], 1), (255, 246, 248), ow=2)
    c.paint(poly([(58, 97), (66, 89), (71, 96), (62, 104)], 1), (255, 246, 248), ow=2)
    c.paint(ell(58, 130, 6, 4.5, -10), pink, ow=2.2, shade=(2, 2, pink_sh))  # knot
    c.line([(52, 128), (56, 130)], 1.2, pink_sh)
    for by in (108, 118):
        c.paint(ell(55, by, 1.6, 1.6), (255, 246, 248), ow=1.2)
    # near arm: thumb hooked in the belt
    c.paint(cap([(38, 100), (31, 120), (38, 138)], 8), skin, shade=(3, 2, skin_sh))
    c.paint(ell(40, 140, 5.5, 6.5, 20) + cap([(43, 135), (47, 134)], 3), skin, shade=(2, 2, skin_sh))
    c.paint(cap([(38, 98), (33, 110)], 14), pink, shade=(3, 2, pink_sh))
    c.paint(ell(33, 112, 7, 3.5, -10), (255, 246, 248), ow=2.2)
    # bracelet
    c.line([(35, 131), (40, 128)], 2.2, (60, 200, 200))

    # ---- head (3/4, facing left)
    head = ell(58, 56, 23.5, 26) + poly([(36, 60), (40, 78), (50, 87), (62, 84), (76, 70)], 2) + ell(33.5, 62, 5.2, 5)
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (250, 206, 170), 2.5))
    c.paint(ell(78, 62, 5.5, 8), skin, shade=(2, 2, skin_sh))  # ear
    c.curve((34, 65), (31, 66), (30, 63), 1.4)  # nostril
    c.paint(ell(51, 70, 6, 3.4), (255, 120, 130), ow=0, opacity=0.5)
    c.paint(ell(37, 69, 3.5, 2.6), (255, 120, 130), ow=0, opacity=0.45)
    # eyes: big, green, confident half-lids + lashes
    eye(c, 54, 58, 8, 10, 50.5, 60, 2.4, lid=0.32, lid_tilt=-1.0, skin=skin, lashes=1, iris=(60, 170, 100))
    eye(c, 38.5, 57.5, 5.6, 9.4, 36, 59.5, 2.1, lid=0.32, lid_tilt=1.0, skin=skin, lashes=-1, iris=(60, 170, 100))
    # brows: one cocked up
    c.line([(46, 45), (54, 42), (62, 44)], 2.2, (130, 76, 40))
    c.line([(34, 48), (40, 46.5)], 2.0, (130, 76, 40))
    # smirk with lipstick
    c.paint(poly([(39, 75), (45, 76.5), (53, 73), (56, 70.5), (52, 77.5), (44, 79.5)], 1), (214, 52, 92), ow=1.8)
    c.line([(40, 75.5), (46, 76.8), (55.5, 71)], 1.3)
    c.paint(ell(61, 76, 0.9, 0.9), OUT, ow=0)  # beauty mark
    # earring + front hair framing the face
    c.paint(poly([(60, 40), (82, 38), (88, 52), (85, 62), (91, 74), (85, 86), (88, 98), (79, 95), (76, 82),
                  (72, 68), (70, 54), (62, 49), (50, 49), (40, 51), (34, 47)], 2, True), hair,
            shade=(3, 2, hair_sh), hi=(-2, 3, hair_hi, 1.5))
    c.curve((76, 56), (82, 72), (80, 90), 1.3, hair_sh)
    c.curve((40, 50), (36, 54), (35, 58), 2.4, hair)  # wispy strand over the far cheek
    c.paint(ell(78, 74, 3.2, 4), (0, 0, 0, 0), ow=1.6, oc=(244, 200, 80))
    # the (very important) brown cowboy hat
    cowboy_hat(c, 57, 40, 0.9, -6)
    c.fit(margin=3)
    c.save("hs_lacey_rae.png")


# =========================================================================== 6. Gil
def paint_gil():
    c = Canvas(110, 240, ow=3)
    skin, skin_sh = (178, 118, 82), (138, 84, 62)
    hair, hair_sh = (56, 38, 34), (32, 22, 22)
    robe, robe_sh, robe_tr = (178, 58, 66), (130, 36, 54), (240, 200, 150)
    pj, pj2 = (120, 160, 230), (240, 244, 255)

    def plaid(p):
        for x in range(0, 120, 12):
            p.line([(x, 80), (x - 4, 200)], 2.5, (150, 40, 56))
        for y in range(90, 200, 12):
            p.line([(0, y), (110, y + 2)], 2.0, (205, 90, 92))

    # far arm, hanging limp (wide robe sleeve)
    c.paint(ell(80, 160, 5.5, 6.5), skin, shade=(2, 2, skin_sh))
    c.paint(poly([(66, 100), (80, 104), (86, 154), (72, 156)], 1), robe, pattern=plaid, shade=(3, 0, robe_sh))
    c.paint(poly([(72, 150), (86, 148), (88, 156), (72, 158)], 1), robe_tr, ow=2.2)
    # pajama legs + slippers
    stripes = lambda p: [p.line([(x, 160), (x - 3, 230)], 2.6, pj2) for x in range(30, 80, 6)]
    c.paint(cap([(62, 170), (66, 222)], 16), pj, pattern=stripes, shade=(3, 0))
    c.paint(cap([(46, 170), (40, 224)], 17), pj, pattern=stripes, shade=(3, 0))
    for sx, sy, rx in ((68, 229, 16), (36, 231, 19)):
        c.paint(ell(sx, sy, rx, 7.5), (176, 170, 160), shade=(2, -2, (140, 132, 130)),
                hi=(-2, 2, (220, 216, 206), 1.5))
        c.paint(ell(sx - rx * 0.5, sy - 2.5, 4, 2.4), (130, 124, 120), ow=0)
    # robe body (slouchy, belly pooch at the front)
    body = poly([(36, 100), (56, 96), (74, 100), (78, 130), (82, 184), (56, 188), (26, 184), (24, 160),
                 (26, 136), (30, 112)], 2)
    c.paint(body, robe, pattern=plaid, shade=(5, 0, robe_sh))
    # undershirt in the open V (with a coffee stain)
    c.paint(poly([(44, 98), (60, 98), (54, 136), (46, 136)], 1), (240, 240, 232), ow=2.2,
            pattern=lambda p: p.ell(51, 118, 4, 3, (176, 130, 90)))
    # lapels
    c.paint(poly([(40, 98), (48, 98), (54, 140), (46, 146), (36, 120)], 1), robe_tr, ow=2.2, shade=(2, 0))
    c.paint(poly([(58, 98), (66, 98), (64, 120), (56, 140)], 1), robe_tr, ow=2.2, shade=(2, 0))
    # belt with dangling ends
    belt = (140, 34, 50)
    c.paint(poly([(25, 140), (79, 138), (80, 146), (25, 148)], 1), belt, ow=2.2, hi=(0, 1.5, (190, 70, 80)))
    c.paint(cap([(33, 146), (30, 160), (33, 172)], 4.5), belt, ow=2.2)
    c.paint(cap([(37, 146), (41, 158), (40, 168)], 4.5), belt, ow=2.2)
    c.paint(ell(35, 144, 5, 4), belt, ow=2.2, hi=(-1, 1, (190, 70, 80)))
    # neck
    c.paint(cap([(55, 84), (54, 98)], 13), skin, shade=(3, 0, skin_sh))
    # big headphones resting around the neck
    c.curve((40, 104), (56, 116), (72, 102), 4.5, (40, 40, 46))
    c.paint(ell(70, 98, 6, 8, 15), (220, 50, 50), ow=2.4, shade=(2, 2, (160, 30, 40)))
    c.paint(ell(41, 101, 7.5, 9.5, -15), (230, 60, 56), ow=2.6, shade=(2, 2, (170, 30, 40)),
            hi=(-1.5, -1.5, (255, 140, 120), 1))
    c.paint(ell(39, 101, 3.5, 5, -15), (40, 40, 46), ow=0)
    # near arm holding a mug at chest height
    c.paint(poly([(30, 102), (46, 106), (44, 128), (24, 132), (20, 118)], 1), robe, pattern=plaid,
            shade=(3, 2, robe_sh))
    c.paint(poly([(16, 116), (26, 112), (30, 132), (18, 134)], 1), robe_tr, ow=2.2)
    mug = rrect(4, 106, 18, 126, 2)
    c.paint(mug, (240, 236, 220), shade=(3, 0, (200, 196, 190)),
            pattern=lambda p: p.rect(4, 113, 18, 117, (60, 130, 200)))
    c.paint(ell(11, 106, 7, 2.2), (110, 60, 30), ow=1.6)
    c.paint(ell(19, 122, 5.5, 6.5), skin, shade=(2, 2, skin_sh))
    for sx in (8, 14):
        c.curve((sx, 102), (sx - 3, 96), (sx + 1, 90), 1.4, (240, 240, 250), 0.85)

    # ---- head (3/4, facing left, drooping forward)
    head = ell(54, 48, 25, 26) + poly([(30, 54), (32, 74), (44, 84), (62, 82), (76, 66)], 2) + ell(28, 56, 8, 8.5)
    stub = lambda p: [p.ell(rx_, ry_, 0.75, 0.75, (110, 70, 54)) for rx_, ry_ in
                      ((36, 74), (40, 77), (44, 79), (48, 78), (52, 79), (56, 77), (60, 76), (64, 73), (38, 70),
                       (46, 74), (54, 74), (62, 70), (68, 66), (50, 82), (42, 81))]
    c.paint(head, skin, shade=(4, 3, skin_sh), hi=(-3, 4, (204, 146, 104), 2.5), pattern=stub)
    c.paint(ell(78, 52, 6, 9), skin, shade=(2, 2, skin_sh))
    c.curve((80, 47), (75, 51), (78, 58), 1.4)
    c.curve((26, 60), (22, 62), (22, 58), 1.4)  # nostril
    # dark circles
    for ex, ey, rx in ((50, 56, 8), (35, 55.5, 5.6)):
        c.paint(ell(ex, ey, rx, 3), (120, 70, 110), ow=0, opacity=0.6)
    # heavy-lidded sleepy eyes
    eye(c, 50, 47, 8, 9, 47.5, 51, 2.3, lid=0.56, lid_tilt=0.6, skin=skin)
    eye(c, 35, 46.5, 5.6, 8.4, 33.5, 50.5, 2.0, lid=0.56, lid_tilt=-0.4, skin=skin)
    # droopy brows
    c.line([(43, 36), (51, 35.5), (59, 38)], 2.4, hair)
    c.line([(30, 37), (38, 36)], 2.2, hair)
    # mid-yawn
    c.paint(ell(41, 71, 5.5, 5), (110, 30, 40), ow=2,
            pattern=lambda p: p.ell(41, 75, 3.5, 2, (230, 110, 110)))
    # bed-head hair with a giant cowlick
    hp = [(30, 34), (32, 24), (42, 16), (56, 14), (62, 4), (66, 14), (72, 8), (74, 18), (82, 26), (84, 46),
          (80, 56), (76, 46), (72, 38), (62, 32), (50, 30), (40, 32)]
    c.paint(poly(hp, 1), hair, shade=(3, 2, hair_sh), hi=(-2, 3, (110, 80, 70), 1.5))
    c.line([(46, 22), (56, 20)], 1.3, hair_sh)
    c.line([(66, 22), (74, 30)], 1.3, hair_sh)
    c.fit(margin=3)
    c.save("hs_gil.png")


# =========================================================================== 7. inventory icons (128x128)
def icon(name, angle, draw):
    c = Canvas(128, 128, ow=5)
    draw(c)
    if angle:
        c.img = c.img.rotate(angle, resample=Image.BICUBIC, center=(64 * S, 64 * S))
    c.fit(feet=False, fill=112)
    c.save(name)


def paint_icon_earplugs():
    org, org_sh, org_hi = (255, 146, 40), (214, 92, 30), (255, 206, 120)

    def plug(c, a, b):
        sh = cap([a, b], 30)
        pores = lambda p: [p.ell(a[0] + (b[0] - a[0]) * t + ox, a[1] + (b[1] - a[1]) * t + oy, 1.4, 1.4, org_sh)
                           for t, ox, oy in ((0.2, -6, 3), (0.4, 5, -4), (0.6, -3, 6), (0.75, 7, 2), (0.35, -8, -6))]
        c.paint(sh, org, shade=(4, 4, org_sh), hi=(-4, -4, org_hi, 3), pattern=pores)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        c.paint(ell(b[0], b[1], 7, 14, ang), lt(org, 0.25), ow=3, shade=(2, 2, org))
    def draw(c):
        c.curve((40, 76), (60, 120), (92, 76), 3.5, (60, 120, 220))
        plug(c, (34, 34), (44, 76))
        plug(c, (100, 46), (86, 80))
    icon("icon_earplugs.png", -6, draw)


def paint_icon_dance_album():
    def draw(c):
        # vinyl peeking out of the sleeve
        grooves = lambda p: [p.ell(84, 60, r, r, (40, 36, 44) if r % 6 else (70, 66, 80)) for r in range(42, 14, -3)]
        c.paint(ell(84, 60, 42, 42), (30, 28, 34), pattern=grooves, hi=(-3, -3, (110, 104, 120), 4))
        c.paint(ell(84, 60, 13, 13), (230, 60, 70), ow=2.5)
        c.paint(ell(84, 60, 2.5, 2.5), (250, 240, 220), ow=1.5)

        def art(p):
            for k in range(14):
                a = math.radians(k * 360 / 14)
                p.poly([(56, 86), (56 + 120 * math.cos(a), 86 + 120 * math.sin(a)),
                        (56 + 120 * math.cos(a + 0.22), 86 + 120 * math.sin(a + 0.22))], (250, 140, 40))
            # crooner silhouette with a mic
            p.ell(70, 70, 9, 10, (60, 20, 70))
            p.poly([(56, 112), (60, 86), (70, 80), (82, 86), (86, 112)], (60, 20, 70))
            p.poly([(58, 50), (86, 50), (80, 62), (64, 62)], (60, 20, 70))  # hat
            p.ell(72, 51, 20, 3, (60, 20, 70))
            p.line([(46, 86), (54, 98)], 3, (60, 20, 70))
            p.ell(45, 84, 4, 5, (200, 200, 210))
        c.paint(wonky(12, 16, 104, 112, 1.5, random.Random(3), corner=6), (120, 40, 140), pattern=art,
                shade=(4, 4, None))
        c.text(58, 28, "HANK", 15, (255, 240, 200), stroke=1.6)
        c.text(58, 44, "HOLLISTER", 11.5, (255, 240, 200), stroke=1.6)
        c.text(32, 98, "LIVE!", 16, (255, 226, 60), "Italic", stroke=2, angle=10)
    icon("icon_dance_album.png", 7, draw)


def paint_icon_lemon():
    y, ysh, yhi = (255, 222, 46), (232, 162, 26), (255, 250, 180)

    def draw(c):
        body = ell(62, 70, 40, 30) + ell(22, 72, 8, 7) + ell(102, 68, 8, 7)
        pores = lambda p: [p.ell(36 + (k * 37) % 56, 54 + (k * 23) % 34, 1.3, 1.3, (236, 186, 40)) for k in range(16)]
        c.paint(body, y, shade=(5, 5, ysh), hi=(-5, -5, yhi, 5), pattern=pores)
        c.line([(84, 44), (90, 36)], 4, (110, 70, 40))
        c.paint(ell(78, 30, 16, 7, -25), (90, 180, 70), shade=(0, 3, (60, 140, 60)), hi=(0, -2, (150, 220, 110)))
        c.line([(68, 34), (88, 25)], 1.8, (50, 120, 50))
        c.paint(ell(46, 60, 8, 4, -25), (255, 255, 240), ow=0, opacity=0.8)
    icon("icon_lemon.png", -10, draw)


def paint_icon_soda():
    def draw(c):
        glass = (140, 220, 200)
        bottle = poly([(48, 118), (80, 118), (82, 64), (72, 42), (71, 22), (57, 22), (56, 42), (46, 64)], 2)
        c.paint(bottle, (190, 236, 226))
        liquid = poly([(46, 56), (82, 56), (82, 118), (46, 118)])
        c.paint(liquid, (242, 120, 34), ow=0, clip=bottle, shade=(5, 0, (196, 76, 30)))
        for bx, by, r in ((56, 96, 2.4), (66, 84, 1.8), (60, 72, 2), (72, 104, 2.2), (54, 62, 1.6)):
            c.paint(ell(bx, by, r, r), (255, 214, 140), ow=1.2)
        c.paint(rect(46, 78, 82, 100), (250, 248, 238), ow=3, clip=bottle)
        c.text(64, 89, "FIZZ-O", 8.5, (40, 150, 200))
        c.line([(52, 66), (56, 112)], 4, (255, 255, 255), opacity=0.55)
        c.paint(rrect(54, 12, 74, 24, 3), (226, 46, 54), ow=3.5, hi=(0, 2, (255, 130, 120)))
        for k in range(5):
            c.line([(56 + k * 4, 13), (56 + k * 4, 23)], 1.2, (170, 30, 40))
    icon("icon_soda.png", 12, draw)


def paint_icon_hallway_hooch():
    red, red_sh, red_hi = (222, 40, 50), (160, 24, 44), (255, 110, 110)

    def draw(c):
        # bubbles + fumes
        for bx, by, r in ((44, 22, 4), (58, 12, 3), (74, 20, 5), (88, 10, 3), (64, 28, 3.5)):
            c.paint(ell(bx, by, r, r), (220, 255, 200), ow=2.2, hi=(-1, -1, (255, 255, 255)))
        cup = poly([(28, 40), (100, 40), (90, 120), (38, 120)], 1)
        c.paint(cup, red, shade=(6, 0, red_sh), hi=(-5, 0, red_hi, 4))
        c.paint(rect(20, 38, 108, 54), (250, 250, 250), ow=0, clip=cup)
        c.line([(29, 54), (99, 54)], 2.5)
        for y in (78, 90):
            c.line([(33 + (y - 40) * 0.12, y), (95 - (y - 40) * 0.12, y)], 2, red_sh)
        # murky liquid surface
        c.paint(ell(64, 41, 35, 7), (186, 214, 60), ow=4,
                pattern=lambda p: [p.ell(50, 40, 3, 2, (220, 240, 120)), p.ell(72, 42, 2, 1.5, (220, 240, 120))])
        # straw
        c.line([(70, 40), (82, 14), (92, 12)], 6, OUT)
        c.line([(70, 40), (82, 14), (92, 12)], 3, (60, 200, 230))
        # lemon slice on the rim
        sl = ell(32, 38, 16, 16)
        c.paint(sl, (255, 226, 60), ow=4)
        c.paint(ell(32, 38, 11, 11), (255, 246, 170), ow=0,
                pattern=lambda p: [p.line([(32, 38), (32 + 11 * math.cos(math.radians(a)),
                                                      38 + 11 * math.sin(math.radians(a)))], 1.4, (240, 200, 60))
                                   for a in range(0, 360, 45)])
    icon("icon_hallway_hooch.png", -8, draw)


def paint_icon_cowboy_hat():
    def draw(c):
        cowboy_hat(c, 64, 80, scale=1.1, rot=-9)
    icon("icon_cowboy_hat.png", 0, draw)


def paint_icon_dollar():
    g, gsh, ghi, gdk = (150, 206, 120), (104, 166, 90), (200, 236, 170), (50, 120, 66)

    def draw(c):
        outline = [(14, 40), (40, 30), (62, 38), (88, 26), (114, 36), (108, 64), (116, 90), (88, 98), (64, 92),
                   (38, 102), (12, 92), (20, 66)]
        bill = poly(outline)
        c.paint(bill, g)
        # crumpled facets
        cx, cy = 64, 64
        for i in range(len(outline)):
            a, b = outline[i], outline[(i + 1) % len(outline)]
            col = [gsh, ghi, g][i % 3]
            c.paint(poly([(cx + (i % 2) * 4 - 2, cy + (i % 3) - 1), a, b]), col, ow=0, clip=bill, opacity=0.75)
        c.paint(poly([(24, 44), (104, 40), (104, 88), (24, 90)], 1), (0, 0, 0, 0), ow=2, oc=gdk)
        c.paint(ell(64, 64, 18, 20), (196, 232, 170), ow=2.5, oc=gdk)
        c.text(64, 64, "$", 30, gdk)
        for tx, ty in ((32, 50), (96, 48), (32, 82), (96, 80)):
            c.text(tx, ty, "1", 12, gdk)
        for a, b in (((40, 30), (64, 92)), ((88, 26), (70, 64)), ((116, 90), (64, 64)), ((14, 40), (60, 62))):
            c.line([a, ((a[0] + b[0]) / 2 + 3, (a[1] + b[1]) / 2)], 1.6, gdk, opacity=0.6)
        # redraw the bold outer outline on top
        c.paint(bill, (0, 0, 0, 0), ow=4.5)
    icon("icon_dollar.png", -12, draw)


ASSETS = {"bg_dex_room": paint_dex_room, "bg_dorm_hallway": paint_dorm_hallway,
          "bg_lounge": paint_lounge,
          "player_dex": paint_player_dex,
          "hs_lacey_rae": paint_lacey_rae, "hs_gil": paint_gil,
          "icon_earplugs": paint_icon_earplugs, "icon_dance_album": paint_icon_dance_album,
          "icon_lemon": paint_icon_lemon, "icon_soda": paint_icon_soda,
          "icon_hallway_hooch": paint_icon_hallway_hooch, "icon_cowboy_hat": paint_icon_cowboy_hat,
          "icon_dollar": paint_icon_dollar}


def main(argv):
    want = [a.lower() for a in argv[1:]]
    for name, fn in ASSETS.items():
        if not want or any(w in name for w in want):
            fn()


if __name__ == "__main__":
    main(sys.argv)
