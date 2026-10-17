#!/usr/bin/env python3
"""
Big Night Out -- "style 2" painting kit (see Docs/ART_STYLE.md).

A reusable toolbox for the richer, grungier, painterly cartoon look:

  * Canvas2.ink()      filled shape + soft cel shading + rim light + painterly grain + a wobbly,
                       variable-width dark outline (heavier on the shadow side)
  * Canvas2.stroke()   tapered, hand-drawn line (folds, cracks, hair strands, wires)
  * Room               3/4 perspective room shell: back wall, angled side walls, ceiling, deep floor
                       receding to a vanishing point. Flat "wall space" painters are warped onto the
                       side walls / floor / ceiling with a true perspective transform.
  * grunge passes      plaster chips revealing bricks, stains + drips, cracks, scuffs, cobwebs,
                       peeling posters
  * cables / pipes     sagging wires, hanging cables, plugs, exposed pipes
  * lights             pendant lamps, glow, soft light cones, floor pools, colour grade
  * foreground         dark, out-of-focus silhouettes framing the bottom/corners
  * Body               character template (about 6.5 heads tall) with a pose skeleton, tapered limbs,
                       3/4 head, expressive eyes/brows/mouths; outfits and hair are drawn by the caller
                       with the landmark helpers.

Everything is original procedural drawing (Pillow + numpy only). It imports paint.py and leaves it
untouched, so the older act scripts keep working.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint  # noqa: E402
from paint import (S, OUT_DIR, ROOT, Canvas, Sh, bez, cap, chaikin, dk, ell, ell_pts, font, lt, mix, poly,  # noqa: E402,F401
                   rect, rrect, rot_pts, wonky)

W_BG, H_BG = 1920, 1080
INK = (34, 16, 40)            # outline colour: very dark violet
INK_SOFT = (60, 30, 66)
SHADOW = (78, 40, 118)        # cool purple shadow tint
GLOW = (255, 214, 120)        # warm lamp light
TEAL = (40, 200, 196)
MAGENTA = (214, 62, 150)
PX_PER_UNIT = 100


# =========================================================================== numeric helpers
def _box(a, r, axis):
    if r < 1:
        return a
    a = np.moveaxis(a, axis, 0)
    n = a.shape[0]
    pad = np.zeros((r + 1,) + a.shape[1:], np.float32)
    padr = np.zeros((r,) + a.shape[1:], np.float32)
    c = np.cumsum(np.concatenate([pad, a, padr], 0), 0, dtype=np.float32)
    out = (c[2 * r + 1:2 * r + 1 + n] - c[:n]) / (2 * r + 1)
    return np.moveaxis(out, 0, axis)


def blur(a, sigma):
    """Fast approximate gaussian blur of a float array (3 box passes per axis, zero padding)."""
    if sigma < 0.5:
        return a
    w = math.sqrt(12 * sigma * sigma / 3 + 1)
    r = max(1, int(round((w - 1) / 2)))
    for _ in range(3):
        a = _box(a, r, 0)
        a = _box(a, r, 1)
    return a


def shift(a, dx, dy):
    """Shift a 2-D array by whole pixels, filling with zeros."""
    dx, dy = int(round(dx)), int(round(dy))
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


_ERF_D = np.linspace(-4.5, 4.5, 2001).astype(np.float32)
_ERF_V = np.array([0.5 * math.erfc(d / math.sqrt(2)) for d in _ERF_D], np.float32)


def _dist_from_blur(v, sigma):
    """Signed distance (positive outside) estimated from a gaussian-blurred binary mask."""
    return np.interp(v, _ERF_V[::-1], _ERF_D[::-1]).astype(np.float32) * sigma


_NOISE = {}


def value_noise(W, H, cell, seed=0):
    """Smooth value noise in 0..1, feature size ~cell pixels."""
    key = (W, H, cell, seed)
    if key in _NOISE:
        return _NOISE[key]
    rng = np.random.default_rng(seed)
    gw, gh = max(2, int(W / cell) + 3), max(2, int(H / cell) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray(g, "F").resize((int(gw * cell), int(gh * cell)), Image.BICUBIC)
    arr = np.asarray(im, np.float32)[:H, :W]
    if arr.shape != (H, W):
        arr = np.pad(arr, ((0, H - arr.shape[0]), (0, W - arr.shape[1])), mode="edge")
    arr = np.clip(arr, 0, 1)
    _NOISE[key] = arr
    return arr


def fbm(W, H, cells=(6, 18, 60, 180), weights=(0.15, 0.25, 0.3, 0.3), seed=0):
    out = np.zeros((H, W), np.float32)
    for k, (c, w) in enumerate(zip(cells, weights)):
        out += value_noise(W, H, c, seed + k * 101) * w
    return out / sum(weights)


def lerp_col(a, b, t):
    return mix(a, b, max(0.0, min(1.0, t)))


def tint(c, f=1.0, toward=None, t=0.0):
    c = tuple(int(max(0, min(255, v * f))) for v in c[:3])
    return mix(c, toward, t) if toward else c


def shade_col(c, f=0.62):
    """Cool purple shadow tone of colour c (multiply-ish + violet)."""
    r, g, b = c[:3]
    return (int(r * f * 0.82 + SHADOW[0] * (1 - f) * 0.5), int(g * f * 0.72 + SHADOW[1] * (1 - f) * 0.4),
            int(min(255, b * f * 0.95 + SHADOW[2] * (1 - f) * 0.75)))


def hi_col(c, f=0.4):
    """Warm highlight tone of colour c."""
    return mix(c, (255, 246, 214), f)


# =========================================================================== geometry helpers
def resample(pts, step, closed=False):
    """Points every ~step pixels along a polyline."""
    P = list(pts) + ([pts[0]] if closed else [])
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        L = math.dist(p, q)
        k = max(1, int(L / step))
        for j in range(1, k + 1):
            t = j / k
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    if closed:
        out = out[:-1]
    return out


def jitter(pts, amt, seed=0, freq=0.08, closed=True):
    """Low-frequency hand-drawn wobble: displace points by smooth noise."""
    if amt <= 0:
        return list(pts)
    rng = random.Random(seed)
    ph = [rng.uniform(0, 6.28) for _ in range(4)]
    out = []
    n = len(pts)
    acc = 0.0
    for i, (x, y) in enumerate(pts):
        if i:
            acc += math.dist(pts[i - 1], pts[i])
        dx = math.sin(acc * freq + ph[0]) * 0.6 + math.sin(acc * freq * 2.7 + ph[1]) * 0.4
        dy = math.sin(acc * freq * 1.3 + ph[2]) * 0.6 + math.sin(acc * freq * 3.1 + ph[3]) * 0.4
        out.append((x + dx * amt, y + dy * amt))
    return out


def blob(pts, smooth=2, closed=True):
    """Smooth closed polygon through roughly the given points (Sh)."""
    return Sh([chaikin(list(pts), smooth, closed)])


def limb(path, widths, smooth=2, ends=True):
    """Tapered limb / tube along a polyline. widths: one per path point (full width)."""
    path = list(path)
    if len(path) > 2 and smooth:
        # smooth the path and interpolate widths along it
        P = chaikin(path, smooth, closed=False)
    else:
        P = path
    # widths by arc length
    def arclen(ps):
        L = [0.0]
        for a, b in zip(ps, ps[1:]):
            L.append(L[-1] + math.dist(a, b))
        return L
    La, Lp = arclen(path), arclen(P)
    tot_a, tot_p = max(La[-1], 1e-6), max(Lp[-1], 1e-6)
    W = [float(np.interp(l / tot_p * tot_a, La, widths)) for l in Lp]
    P = resample_keep(P, W)
    P, W = P
    left, right = [], []
    for i, (x, y) in enumerate(P):
        a = P[max(0, i - 1)]
        b = P[min(len(P) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = W[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    pts = left
    if ends:
        # round caps
        x, y = P[-1]
        a = P[-2]
        ang = math.atan2(y - a[1], x - a[0])
        r = W[-1] / 2
        pts += [(x + r * math.cos(ang + math.pi / 2 - k * math.pi / 8), y + r * math.sin(ang + math.pi / 2 - k * math.pi / 8))
                for k in range(1, 8)]
    pts += right[::-1]
    if ends:
        x, y = P[0]
        b = P[1]
        ang = math.atan2(y - b[1], x - b[0])
        r = W[0] / 2
        pts += [(x + r * math.cos(ang + math.pi / 2 - k * math.pi / 8), y + r * math.sin(ang + math.pi / 2 - k * math.pi / 8))
                for k in range(1, 8)]
    return Sh([pts])


def resample_keep(P, W, step=3.0):
    outP, outW = [P[0]], [W[0]]
    for i in range(len(P) - 1):
        p, q = P[i], P[i + 1]
        L = math.dist(p, q)
        k = max(1, int(L / step))
        for j in range(1, k + 1):
            t = j / k
            outP.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
            outW.append(W[i] + (W[i + 1] - W[i]) * t)
    return outP, outW


def quad_pts(q, u, v):
    """Bilinear point in quad q=[p00 (u0,v0), p10, p11, p01]."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    a = (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
    b = (x3 + (x2 - x3) * u, y3 + (y2 - y3) * u)
    return (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)


def homography(src, dst):
    """3x3 matrix H with dst ~ H * src (4 point pairs)."""
    A, B = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B.append(v)
    h = np.linalg.solve(np.array(A, float), np.array(B, float))
    return np.array([[h[0], h[1], h[2]], [h[3], h[4], h[5]], [h[6], h[7], 1.0]])


def hmap(Hm, x, y):
    v = Hm @ np.array([x, y, 1.0])
    return (v[0] / v[2], v[1] / v[2])


# =========================================================================== canvas
class Canvas2(Canvas):
    """paint.Canvas plus the style-2 inking methods. Coordinates are final pixels (supersampled by S)."""

    def __init__(self, w, h, bg=(0, 0, 0, 0), light=(-0.45, -0.89), lw=3.2, seed=0):
        super().__init__(w, h, ow=0, bg=bg)
        self.light = light
        self.lw = lw
        self.seed = seed
        W, H = self.img.size
        self._grain = None
        self._wnoise = None

    # ---- global noise maps (supersampled resolution)
    def grain(self):
        if self._grain is None:
            W, H = self.img.size
            self._grain = fbm(W, H, cells=(3 * S, 9 * S, 30 * S, 110 * S), weights=(0.2, 0.3, 0.3, 0.2),
                              seed=self.seed + 7)
        return self._grain

    def wnoise(self):
        if self._wnoise is None:
            W, H = self.img.size
            self._wnoise = value_noise(W, H, 22 * S, self.seed + 3)
        return self._wnoise

    def _crop_box(self, sh, pad):
        bx0, by0, bx1, by1 = sh.bbox()
        W, H = self.img.size
        ox, oy = int(math.floor((bx0 - pad) * S)), int(math.floor((by0 - pad) * S))
        ex, ey = int(math.ceil((bx1 + pad) * S)), int(math.ceil((by1 + pad) * S))
        return ox, oy, ex, ey

    def _mask(self, sh, ox, oy, w, h):
        m = Image.new("L", (w, h), 0)
        sh.render(ImageDraw.Draw(m), ox, oy, 0)
        return np.asarray(m, np.float32) / 255.0

    def _composite(self, rgb, alpha, ox, oy):
        """Composite float rgb (h,w,3 0..255) with alpha (h,w 0..1) at supersampled offset."""
        W, H = self.img.size
        h, w = alpha.shape
        x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ox + w), min(H, oy + h)
        if x1 <= x0 or y1 <= y0:
            return
        a = alpha[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
        c = rgb[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
        dst = np.asarray(self.img.crop((x0, y0, x1, y1)), np.float32)
        da = dst[..., 3:4] / 255.0
        sa = a[..., None]
        oa = sa + da * (1 - sa)
        orgb = (c * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
        out = np.concatenate([orgb, oa * 255.0], axis=2)
        self.img.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), (x0, y0))

    # ---- the main painter
    def ink(self, sh, fill, lw=None, oc=INK, shade=0.55, sw=None, scol=None, hi=0.35, hw=None, hcol=None,
            rim=0.0, rcol=(200, 180, 255), ao=0.18, tex=0.06, wob=0.9, lwvar=0.6, opacity=1.0, clip=None,
            light=None, line_only=False, inner=0.4, seed=None, hard=0.5, atop=False):
        """Paint shape `sh` (paint.Sh or point list).

        fill   colour or paint gradient spec (('v', c1, c2), ('vy', y0, y1, c1, c2), ('r', ...))
        lw     outline width in px (0 = none); varies along the line by lwvar, heavier on the shadow side
        shade  strength of the soft cel shadow on the side away from the light; sw its width (px)
        hi     strength of the soft highlight on the lit side; hw its width
        rim    strength of a thin cool reflected-light rim inside the shadow-side edge
        ao     soft darkening just inside the edge (gives volume)
        tex    painterly grain strength
        wob    hand-drawn wobble applied to the shape outline (px)
        clip   additional Sh to clip to; atop=True clips to what is already painted (alpha)
        """
        if isinstance(sh, list):
            sh = Sh([sh])
        seed = self.seed if seed is None else seed
        if wob:
            sh = Sh([jitter(resample(p, 4, True), wob, seed + int(p[0][0] * 3 + p[0][1] * 7)) for p in sh.polys
                     if len(p) >= 3], [(jitter(resample(p, 4), wob * 0.6, seed + 5, closed=False), w) for p, w in sh.caps])
        lw = self.lw if lw is None else lw
        lx, ly = light or self.light
        bx0, by0, bx1, by1 = sh.bbox()
        size = max(4.0, min(bx1 - bx0, by1 - by0))
        sw = sw if sw is not None else max(2.0, min(70.0, size * 0.32))
        hw = hw if hw is not None else max(1.5, min(40.0, size * 0.16))
        pad = lw * 2 + 4
        ox, oy, ex, ey = self._crop_box(sh, pad)
        w, h = ex - ox, ey - oy
        if w <= 2 or h <= 2:
            return
        m = self._mask(sh, ox, oy, w, h)
        if clip is not None:
            m = m * self._mask(clip, ox, oy, w, h)
        if atop:
            W, H = self.img.size
            cur = np.zeros((h, w), np.float32)
            x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ex), min(H, ey)
            if x1 > x0 and y1 > y0:
                cur[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = np.asarray(self.img.crop((x0, y0, x1, y1)).getchannel("A"),
                                                                    np.float32) / 255.0
            m = m * cur
        if m.max() <= 0:
            return
        if not line_only:
            fl = np.asarray(self._fill_layer(fill if not (isinstance(fill, tuple) and len(fill) == 4 and not isinstance(fill[0], str)) else fill[:3],
                                             w, h, ox, oy, (bx0, by0, bx1, by1)), np.float32)[..., :3].copy()
            base_alpha = (fill[3] / 255.0) if (not isinstance(fill[0], str) and len(fill) == 4) else 1.0
            Ssw = sw * S
            if shade > 0:
                lit = blur(shift(m, lx * Ssw, ly * Ssw), Ssw * (0.25 + 0.4 * (1 - hard)))
                band = np.clip(m - lit, 0, 1)
                band = smoothstep(0.1, 0.1 + 0.8 * (1 - hard) + 0.05, band) * m
                sc = np.array(scol if scol else shade_col(fill if not isinstance(fill[0], str) else fill[-1]),
                              np.float32)
                if isinstance(fill[0], str):
                    sc_full = fl * (sc / np.maximum(np.array(fill[-1][:3], np.float32), 1))
                    sc_full = np.clip(sc_full, 0, 255)
                else:
                    sc_full = fl * (sc / np.maximum(np.array(fill[:3], np.float32), 1))[None, None, :]
                k = (band * shade)[..., None]
                fl = fl * (1 - k) + sc_full * k
            if hi > 0:
                Shw = hw * S
                dark = blur(shift(m, -lx * Shw, -ly * Shw), Shw * 0.5)
                band = np.clip(m - dark, 0, 1) * m
                hc = np.array(hcol, np.float32) if hcol else None
                k = (smoothstep(0.05, 0.7, band) * hi)[..., None]
                if hc is None:
                    hc_full = 255 - (255 - fl) * 0.45
                    hc_full = hc_full * np.array([1.0, 0.97, 0.88], np.float32) + np.array([0, 2, 10], np.float32)
                else:
                    hc_full = hc[None, None, :]
                fl = fl * (1 - k) + hc_full * k
            if rim > 0:
                rw = max(1.5, lw * 0.9) * S
                inner_edge = np.clip(m - shift(m, lx * rw, ly * rw), 0, 1)
                inner_edge = blur(inner_edge, 0.8) * m
                k = (inner_edge * rim)[..., None]
                fl = fl * (1 - k) + np.array(rcol, np.float32)[None, None, :] * k
            if ao > 0:
                e = m - blur(m, max(2.0, size * 0.06) * S)
                e = np.clip(e, 0, 1)
                k = (smoothstep(0.0, 0.5, e) * ao)[..., None] * m[..., None]
                fl = fl * (1 - k * 0.55)
            if tex > 0:
                W, H = self.img.size
                g = np.full((h, w), 0.5, np.float32)
                x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ex), min(H, ey)
                if x1 > x0 and y1 > y0:
                    g[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = self.grain()[y0:y1, x0:x1]
                fl = fl * (1 + (g[..., None] - 0.5) * tex * 2.2)
            a = m * base_alpha * opacity
            # fill slightly inset under the line so the outline sits half in, half out
            self._composite(np.clip(fl, 0, 255), a, ox, oy)
        if lw > 0:
            self._outline(m, lw, oc, ox, oy, lwvar, (lx, ly), opacity, inner)

    def _outline(self, m, lw, oc, ox, oy, lwvar, light, opacity, inner=0.4):
        Slw = lw * S
        sigma = max(1.0, Slw * 0.7)
        v = blur(m, sigma)
        d = _dist_from_blur(np.clip(v, 1e-6, 1 - 1e-6), sigma)
        h, w = m.shape
        W, H = self.img.size
        n = np.full((h, w), 0.5, np.float32)
        x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ox + w), min(H, oy + h)
        if x1 > x0 and y1 > y0:
            n[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = self.wnoise()[y0:y1, x0:x1]
        lx, ly = light
        tow = blur(shift(m, -lx * Slw * 2, -ly * Slw * 2), Slw)
        away = blur(shift(m, lx * Slw * 2, ly * Slw * 2), Slw)
        side = np.clip(tow - away, -1, 1)  # >0 on the shadow side
        wmap = Slw * (1 - lwvar * 0.5 + lwvar * n) * (1 + 0.35 * side)
        wmap = np.maximum(wmap, Slw * 0.35)
        lo = -wmap * inner
        hi_ = wmap * (1 - inner)
        a = np.clip(np.minimum(d - lo, hi_ - d) + 0.5, 0, 1) * opacity
        rgb = np.empty((h, w, 3), np.float32)
        rgb[...] = np.array(oc[:3], np.float32)
        self._composite(rgb, a, ox, oy)

    # ---- lines
    def stroke(self, pts, w, color=INK, taper=(0.25, 0.25), wob=0.5, opacity=1.0, seed=None, closed=False,
               smooth=1, var=0.35, blur_px=0):
        """Tapered hand-drawn line. taper = fraction of the length used for the thin start / end."""
        pts = list(pts)
        if len(pts) < 2:
            return
        seed = self.seed if seed is None else seed
        if smooth and len(pts) > 2:
            pts = chaikin(pts, smooth, closed=closed)
        P = resample(pts, 2.0, closed)
        if closed:
            P = P + [P[0]]
        P = jitter(P, wob, seed + len(P), closed=False)
        L = [0.0]
        for a, b in zip(P, P[1:]):
            L.append(L[-1] + math.dist(a, b))
        tot = max(L[-1], 1e-6)
        rng = random.Random(seed)
        ph = rng.uniform(0, 6.28)
        Ws = []
        for l in L:
            t = l / tot
            k = 1.0
            if taper[0] > 0 and t < taper[0]:
                k = 0.25 + 0.75 * math.sin(t / taper[0] * math.pi / 2)
            if taper[1] > 0 and t > 1 - taper[1]:
                k = min(k, 0.25 + 0.75 * math.sin((1 - t) / taper[1] * math.pi / 2))
            k *= 1 + var * math.sin(l * 0.05 + ph) * 0.6
            Ws.append(max(0.3, w * k))
        xs = [p[0] for p in P]
        ys = [p[1] for p in P]
        pad = w + 4 + blur_px * 3
        ox, oy = int(math.floor((min(xs) - pad) * S)), int(math.floor((min(ys) - pad) * S))
        ex, ey = int(math.ceil((max(xs) + pad) * S)), int(math.ceil((max(ys) + pad) * S))
        mw, mh = ex - ox, ey - oy
        if mw <= 0 or mh <= 0:
            return
        mi = Image.new("L", (mw, mh), 0)
        d = ImageDraw.Draw(mi)
        for i in range(len(P) - 1):
            (x0, y0), (x1, y1) = P[i], P[i + 1]
            w0, w1 = Ws[i] * S / 2, Ws[i + 1] * S / 2
            dx, dy = x1 - x0, y1 - y0
            Ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / Ln, dx / Ln
            X0, Y0, X1, Y1 = x0 * S - ox, y0 * S - oy, x1 * S - ox, y1 * S - oy
            d.polygon([(X0 + nx * w0, Y0 + ny * w0), (X1 + nx * w1, Y1 + ny * w1), (X1 - nx * w1, Y1 - ny * w1),
                       (X0 - nx * w0, Y0 - ny * w0)], fill=255)
            d.ellipse([X1 - w1, Y1 - w1, X1 + w1, Y1 + w1], fill=255)
        a = np.asarray(mi, np.float32) / 255.0
        if blur_px:
            a = blur(a, blur_px * S)
        rgb = np.empty((mh, mw, 3), np.float32)
        rgb[...] = np.array(color[:3], np.float32)
        self._composite(rgb, a * opacity, ox, oy)

    def curve2(self, p0, p1, p2, w, color=INK, **kw):
        self.stroke(bez(p0, p1, p2, 20), w, color, smooth=0, **kw)

    # ---- soft paint (no outline): blurred blobs for stains, glows, shadows
    def soft(self, sh, color, opacity=0.5, blur_px=6.0, mode="normal", clip=None):
        if isinstance(sh, list):
            sh = Sh([sh])
        pad = blur_px * 3 + 2
        ox, oy, ex, ey = self._crop_box(sh, pad)
        w, h = ex - ox, ey - oy
        if w <= 0 or h <= 0:
            return
        m = self._mask(sh, ox, oy, w, h)
        m = blur(m, blur_px * S) if blur_px > 0 else m
        if clip is not None:
            m = m * self._mask(clip, ox, oy, w, h)
        if mode == "normal":
            rgb = np.empty((h, w, 3), np.float32)
            rgb[...] = np.array(color[:3], np.float32)
            self._composite(rgb, m * opacity, ox, oy)
        else:
            self._blend(m * opacity, color, ox, oy, mode)

    def _blend(self, a, color, ox, oy, mode):
        W, H = self.img.size
        h, w = a.shape
        x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ox + w), min(H, oy + h)
        if x1 <= x0 or y1 <= y0:
            return
        a = a[y0 - oy:y1 - oy, x0 - ox:x1 - ox][..., None]
        dst = np.asarray(self.img.crop((x0, y0, x1, y1)), np.float32)
        rgb = dst[..., :3]
        col = np.array(color[:3], np.float32)[None, None, :]
        if mode == "add":
            out = rgb + col * a
        elif mode == "screen":
            out = 255 - (255 - rgb) * (255 - col * a) / 255
        elif mode == "multiply":
            out = rgb * (1 - a + a * col / 255)
        elif mode == "overlay":
            o = np.where(rgb < 128, 2 * rgb * col / 255, 255 - 2 * (255 - rgb) * (255 - col) / 255)
            out = rgb * (1 - a) + o * a
        else:
            out = rgb
        dst[..., :3] = np.clip(out, 0, 255)
        self.img.paste(Image.fromarray(dst.astype(np.uint8), "RGBA"), (x0, y0))

    def light_cone(self, apex, left, right, color=GLOW, strength=0.45, blur_px=26, falloff=1.2):
        """Soft additive cone of light from apex (lamp) spreading to the segment left..right."""
        sh = Sh([[apex, left, right]])
        pad = blur_px * 3
        ox, oy, ex, ey = self._crop_box(sh, pad)
        w, h = ex - ox, ey - oy
        m = self._mask(sh, ox, oy, w, h)
        m = blur(m, blur_px * S)
        ys = (np.arange(h, dtype=np.float32) + oy) / S
        y0, y1 = apex[1], max(left[1], right[1])
        t = np.clip((ys - y0) / max(1, y1 - y0), 0, 1)
        fall = (1 - t * 0.75) ** falloff
        self._blend(m * fall[:, None] * strength, color, ox, oy, "screen")

    def glow2(self, cx, cy, r, color=GLOW, strength=0.6, mode="screen", sx=1.0, sy=1.0):
        """Radial glow (screen / add) with an elliptical footprint."""
        W, H = self.img.size
        x0, y0 = int((cx - r * sx) * S), int((cy - r * sy) * S)
        x1, y1 = int((cx + r * sx) * S), int((cy + r * sy) * S)
        if x1 <= x0 or y1 <= y0:
            return
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dd = np.sqrt(((xs / S - cx) / (r * sx)) ** 2 + ((ys / S - cy) / (r * sy)) ** 2)
        a = np.clip(1 - dd, 0, 1) ** 2 * strength
        self._blend(a, color, x0, y0, mode)

    def grade(self, fn):
        """Per-pixel colour transform of the whole canvas: fn(rgb float HxWx3, xs, ys in px) -> rgb."""
        W, H = self.img.size
        arr = np.asarray(self.img, np.float32)
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32) / S
        arr[..., :3] = np.clip(fn(arr[..., :3], xs, ys), 0, 255)
        self.img = Image.fromarray(arr.astype(np.uint8), "RGBA")

    def painterly(self, amount=0.06, strokes=True, seed=11):
        """Painterly texture over the whole canvas: grain + faint directional brush streaks."""
        W, H = self.img.size
        arr = np.asarray(self.img, np.float32)
        g = fbm(W, H, cells=(2 * S, 6 * S, 24 * S), weights=(0.35, 0.35, 0.3), seed=seed)
        if strokes:
            st = value_noise(W, H, 5 * S, seed + 9)
            st2 = np.asarray(Image.fromarray((st * 255).astype(np.uint8)).resize((W // 6, H)).resize((W, H), Image.BICUBIC),
                             np.float32) / 255.0
            g = g * 0.6 + st2 * 0.4
        arr[..., :3] *= (1 + (g[..., None] - 0.5) * amount * 2)
        self.img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    def defocus(self, layer_fn, blur_px=5, opacity=1.0):
        """Draw something on a separate layer with layer_fn(c2) and composite it blurred (out of focus)."""
        tmp = Canvas2(self.w, self.h, light=self.light, lw=self.lw, seed=self.seed + 99)
        layer_fn(tmp)
        im = tmp.img.filter(ImageFilter.GaussianBlur(blur_px * S)) if blur_px else tmp.img
        if opacity < 1:
            a = im.getchannel("A").point(lambda v: int(v * opacity))
            im.putalpha(a)
        self.img.alpha_composite(im)

    def warp_in(self, sub, quad, opacity=1.0):
        """Perspective-warp Canvas `sub` (flat painting) so its corners land on quad
        [top-left, top-right, bottom-right, bottom-left] (canvas px)."""
        src = [(0, 0), (sub.img.width, 0), (sub.img.width, sub.img.height), (0, sub.img.height)]
        dst = [(x * S, y * S) for x, y in quad]
        Hm = homography(dst, src)  # maps output -> input
        coeffs = (Hm / Hm[2, 2]).flatten()[:8]
        W, H = self.img.size
        xs = [p[0] for p in dst]
        ys = [p[1] for p in dst]
        x0, y0 = max(0, int(min(xs)) - 2), max(0, int(min(ys)) - 2)
        x1, y1 = min(W, int(max(xs)) + 2), min(H, int(max(ys)) + 2)
        if x1 <= x0 or y1 <= y0:
            return
        T = np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1]], float)
        Hc = Hm @ T
        Hc = Hc / Hc[2, 2]
        out = sub.img.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(Hc.flatten()[:8]), Image.BICUBIC)
        if opacity < 1:
            out.putalpha(out.getchannel("A").point(lambda v: int(v * opacity)))
        self.img.alpha_composite(out, (x0, y0))

    def label(self, x, y, s, size, fill, kind="Black", angle=0, mirror=False, stroke=0, sc=INK):
        """Text that survives a horizontal flip of the finished sprite (mirror=True pre-mirrors it)."""
        sub = Canvas(int(len(s) * size * 0.9 + 40), int(size * 2.4 + 20), ow=0)
        sub.text(sub.w / 2, sub.h / 2, s, size, fill, kind, stroke=stroke, sc=sc, angle=angle)
        im = sub.img
        if mirror:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        self.img.alpha_composite(im, (int(x * S - im.width / 2), int(y * S - im.height / 2)))

    def save_png(self, name, flip=False):
        im = self.result()
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, name)
        im.save(path, optimize=True)
        print("wrote", os.path.relpath(path, ROOT), "%dx%d" % im.size)
        return im


# =========================================================================== perspective room shell
class Room:
    """A 3/4 perspective box room with a simple 3-D coordinate system.

    vp     vanishing point (px) = the camera's eye line. For characters to scale correctly with the
           game's depth scale (1.0 at the bottom of the walkable area -> 0.6 at its top) put
           vp_y = y_top - 1.5 * (y_bot - y_top)  (see vp_for_walk()).
    back   (x0, y0, x1, y1) back wall rectangle in px; y1 is where it meets the floor.
    fc     focal length in px (how deep the room feels: smaller = more wide-angle).

    3-D space ("back px" units: 1 unit = 1 px on the back wall):
        X across from the back wall's left edge (0 .. Wb), Y up from the floor (0 .. Hb),
        Z toward the camera from the back wall (0 .. ~fc). room.pt(X, Y, Z) -> screen px.
    The left wall is X = 0, the right wall X = Wb, floor Y = 0, ceiling Y = Hb.
    """

    def __init__(self, c, vp, back, fc=1000.0, W=W_BG, H=H_BG):
        self.c, self.vp, self.back, self.fc, self.W, self.H = c, vp, back, fc, W, H
        x0, y0, x1, y1 = back
        self.Wb, self.Hb = x1 - x0, y1 - y0
        self.eye = y1 - vp[1]                 # camera height above the floor (back px)
        self.cam_x = vp[0] - x0               # camera X
        self.bl, self.br, self.tl, self.tr = (x0, y1), (x1, y1), (x0, y0), (x1, y0)

    # ---- projection
    def k(self, Z):
        return self.fc / max(1e-3, self.fc - Z)

    def pt(self, X, Y, Z=0.0):
        k = self.k(Z)
        x0, y0, x1, y1 = self.back
        return (self.vp[0] + (x0 + X - self.vp[0]) * k, self.vp[1] + (y1 - Y - self.vp[1]) * k)

    def pts(self, xyz):
        return [self.pt(*p) for p in xyz]

    def scale_at_y(self, y):
        """Perspective scale (1 = back wall) of something standing on the floor at screen y."""
        return (y - self.vp[1]) / (self.back[3] - self.vp[1])

    def z_at_y(self, y):
        """Depth Z of the floor at screen y."""
        k = self.scale_at_y(y)
        return self.fc * (1 - 1 / k)

    def x_at(self, sx, y):
        """3-D X of screen x on the floor at screen y."""
        k = self.scale_at_y(y)
        return (sx - self.vp[0]) / k + self.vp[0] - self.back[0]

    def floor_at(self, sx, sy):
        """Screen point on the floor -> (X, Z)."""
        return self.x_at(sx, sy), self.z_at_y(sy)

    def z_at_screen_x(self, X, sx):
        """Depth where the vertical line X (e.g. a side wall) reaches screen x."""
        x0 = self.back[0]
        k = (sx - self.vp[0]) / (x0 + X - self.vp[0])
        return self.fc * (1 - 1 / k)

    def z_front(self, margin=60):
        """Depth at which the floor centre reaches the bottom of the screen (+ margin px)."""
        return self.z_at_y(self.H + margin)

    # ---- planes
    def quad(self, plane, a0, a1, b0, b1):
        """Screen quad [p00, p10, p11, p01] of a rectangle on a plane:
        'back' (a=X, b=Y at Z=0), 'L'/'R' (a=Z, b=Y), 'floor' (a=X, b=Z), 'ceil' (a=X, b=Z)."""
        if plane == "back":
            f = lambda a, b: self.pt(a, b, 0)
        elif plane == "L":
            f = lambda a, b: self.pt(0, b, a)
        elif plane == "R":
            f = lambda a, b: self.pt(self.Wb, b, a)
        elif plane == "floor":
            f = lambda a, b: self.pt(a, 0, b)
        else:
            f = lambda a, b: self.pt(a, self.Hb, b)
        return [f(a0, b0), f(a1, b0), f(a1, b1), f(a0, b1)]

    def paint_plane(self, plane, a0, a1, b0, b1, painter, density=1.6, seed=0, opacity=1.0):
        """Paint a flat rectangle of the given plane with painter(sub) and warp it into place.

        The flat canvas is (a1-a0) x (b1-b0) back-px scaled by `density`; draw on it in its own
        pixel coordinates (use sub.ax(a) / sub.by(b) to convert plane coordinates). Orientation:
        'L': flat x = near (Z=a1) on the left -> back on the right, flat y = top (Y=b1) down.
        'R': flat x = back on the left -> near on the right.   'floor': flat x = X, flat y = Z (back at top).
        'ceil': flat x = X, flat y = near at the top -> back at the bottom.   'back': x = X, y = top down."""
        w, h = (a1 - a0) * density, (b1 - b0) * density
        sub = Canvas2(max(4, int(w)), max(4, int(h)), light=self.c.light, lw=self.c.lw, seed=seed)
        if plane == "L":
            sub.ax = lambda a: (a1 - a) * density
            sub.by = lambda b: (b1 - b) * density
            corners = [self.pt(0, b1, a1), self.pt(0, b1, a0), self.pt(0, b0, a0), self.pt(0, b0, a1)]
        elif plane == "R":
            sub.ax = lambda a: (a - a0) * density
            sub.by = lambda b: (b1 - b) * density
            corners = [self.pt(self.Wb, b1, a0), self.pt(self.Wb, b1, a1), self.pt(self.Wb, b0, a1), self.pt(self.Wb, b0, a0)]
        elif plane == "floor":
            sub.ax = lambda a: (a - a0) * density
            sub.by = lambda b: (b - b0) * density
            corners = [self.pt(a0, 0, b0), self.pt(a1, 0, b0), self.pt(a1, 0, b1), self.pt(a0, 0, b1)]
        elif plane == "ceil":
            sub.ax = lambda a: (a - a0) * density
            sub.by = lambda b: (b1 - b) * density
            corners = [self.pt(a0, self.Hb, b1), self.pt(a1, self.Hb, b1), self.pt(a1, self.Hb, b0), self.pt(a0, self.Hb, b0)]
        else:
            sub.ax = lambda a: (a - a0) * density
            sub.by = lambda b: (b1 - b) * density
            corners = [self.pt(a0, b1, 0), self.pt(a1, b1, 0), self.pt(a1, b0, 0), self.pt(a0, b0, 0)]
        sub.density = density
        painter(sub)
        self.c.warp_in(sub, corners, opacity)
        return sub

    def side_depth(self, side, margin=80):
        """Depth Z where a side wall leaves the screen (plus a margin)."""
        X = 0 if side == "L" else self.Wb
        sx = -margin if side == "L" else self.W + margin
        z1 = self.z_at_screen_x(X, sx)
        return min(self.fc * 0.92, max(10.0, z1))

    # ---- 3-D boxes (furniture)
    def box(self, X0, X1, Y0, Y1, Z0, Z1):
        """Visible faces of an axis-aligned box as dict of screen polygons: top, front, left, right, bottom."""
        P = lambda X, Y, Z: self.pt(X, Y, Z)
        faces = {"front": [P(X0, Y1, Z1), P(X1, Y1, Z1), P(X1, Y0, Z1), P(X0, Y0, Z1)]}
        if Y1 < self.eye:
            faces["top"] = [P(X0, Y1, Z0), P(X1, Y1, Z0), P(X1, Y1, Z1), P(X0, Y1, Z1)]
        elif Y0 > self.eye:
            faces["bottom"] = [P(X0, Y0, Z0), P(X1, Y0, Z0), P(X1, Y0, Z1), P(X0, Y0, Z1)]
        if X0 > self.cam_x:
            faces["left"] = [P(X0, Y1, Z0), P(X0, Y1, Z1), P(X0, Y0, Z1), P(X0, Y0, Z0)]
        if X1 < self.cam_x:
            faces["right"] = [P(X1, Y1, Z1), P(X1, Y1, Z0), P(X1, Y0, Z0), P(X1, Y0, Z1)]
        return faces

    def ink_box(self, X0, X1, Y0, Y1, Z0, Z1, col, top=None, side=None, lw=None, tex=0.08, wob=0.8, shade=0.25,
                seed=0):
        """Ink a box: front in col, top lighter, sides darker. Returns the faces dict."""
        c = self.c
        f = self.box(X0, X1, Y0, Y1, Z0, Z1)
        sidec = side or shade_col(col, 0.72)
        topc = top or hi_col(col, 0.25)
        for name in ("left", "right", "bottom"):
            if name in f:
                c.ink(Sh([f[name]]), sidec, lw=lw, shade=shade, hi=0.1, tex=tex, wob=wob, seed=seed)
        if "top" in f:
            c.ink(Sh([f["top"]]), topc, lw=lw, shade=0.1, hi=0.25, tex=tex, wob=wob, seed=seed)
        c.ink(Sh([f["front"]]), col, lw=lw, shade=shade, hi=0.2, tex=tex, wob=wob, seed=seed)
        return f

    # ---- the shell
    def shell(self, back_fn=None, left_fn=None, right_fn=None, floor_fn=None, ceil_fn=None, density=1.5, seed=0):
        """Paint ceiling, side walls, floor (each a flat painter warped into perspective, see
        paint_plane) then back_fn(c, room) directly in screen space."""
        zl, zr = self.side_depth("L"), self.side_depth("R")
        zf = min(self.fc * 0.92, self.z_front(120))
        zc = min(self.fc * 0.92, max(zl, zr, self.z_at_ceiling_top()))
        self.zl, self.zr, self.zf, self.zc = zl, zr, zf, zc
        if ceil_fn:
            self.paint_plane("ceil", min(0, self.x_at(-200, self.H)), max(self.Wb, self.x_at(self.W + 200, self.H)),
                             0, zc, ceil_fn, density * 0.8, seed + 1)
        if floor_fn:
            self.paint_plane("floor", min(0, self.x_at(-200, self.H + 120)), max(self.Wb, self.x_at(self.W + 200, self.H + 120)),
                             0, zf, floor_fn, density, seed + 4)
        if left_fn and self.back[0] > 0:
            self.paint_plane("L", 0, zl, 0, self.Hb, left_fn, density, seed + 2)
        if right_fn and self.back[2] < self.W:
            self.paint_plane("R", 0, zr, 0, self.Hb, right_fn, density, seed + 3)
        if back_fn:
            back_fn(self.c, self)

    def z_at_ceiling_top(self, margin=80):
        y0 = self.back[1]
        k = (self.vp[1] - (-margin)) / (self.vp[1] - y0)
        return self.fc * (1 - 1 / k)

    def edges(self, w=4.2, color=INK, opacity=0.9):
        """Ink the room's corner edges where the planes meet."""
        c = self.c
        zl, zr = getattr(self, "zl", 600), getattr(self, "zr", 600)
        Hb, Wb = self.Hb, self.Wb
        if self.back[0] > 0:
            c.stroke([self.pt(0, Hb, 0), self.pt(0, 0, 0)], w, color, taper=(0.02, 0.02), opacity=opacity, smooth=0)
            c.stroke([self.pt(0, 0, 0), self.pt(0, 0, zl)], w * 1.2, color, taper=(0, 0), opacity=opacity, smooth=0)
            c.stroke([self.pt(0, Hb, 0), self.pt(0, Hb, zl)], w * 1.2, color, taper=(0, 0), opacity=opacity, smooth=0)
        if self.back[2] < self.W:
            c.stroke([self.pt(Wb, Hb, 0), self.pt(Wb, 0, 0)], w, color, taper=(0.02, 0.02), opacity=opacity, smooth=0)
            c.stroke([self.pt(Wb, 0, 0), self.pt(Wb, 0, zr)], w * 1.2, color, taper=(0, 0), opacity=opacity, smooth=0)
            c.stroke([self.pt(Wb, Hb, 0), self.pt(Wb, Hb, zr)], w * 1.2, color, taper=(0, 0), opacity=opacity, smooth=0)
        c.stroke([self.pt(0, 0, 0), self.pt(Wb, 0, 0)], w * 0.9, color, taper=(0.01, 0.01), opacity=opacity, smooth=0)
        c.stroke([self.pt(0, Hb, 0), self.pt(Wb, Hb, 0)], w * 0.9, color, taper=(0.01, 0.01), opacity=opacity, smooth=0)

    # ---- ambient occlusion / contact shadows
    def ao(self, strength=0.4, width=34):
        """Soft dark bands where floor meets walls and in the vertical corners."""
        c = self.c
        Wb, Hb = self.Wb, self.Hb
        zl, zr = getattr(self, "zl", 600), getattr(self, "zr", 600)
        col = (24, 6, 34)
        c.soft(Sh([[self.pt(-5, 0, 0), self.pt(Wb + 5, 0, 0), self.pt(Wb, 0, width * 1.6), self.pt(0, 0, width * 1.6)]]),
               col, strength, 12)
        c.soft(Sh([[self.pt(0, -2, 0), self.pt(Wb, -2, 0), self.pt(Wb, width, 0), self.pt(0, width, 0)]]), col,
               strength * 0.6, 14)
        if self.back[0] > 0:
            c.soft(Sh([[self.pt(0, 0, 0), self.pt(width, 0, 0), self.pt(width, 0, zl), self.pt(0, 0, zl)]]), col, strength, 12)
            c.soft(Sh([[self.pt(0, 0, 0), self.pt(0, Hb, 0), self.pt(0, Hb, width), self.pt(0, 0, width)]]), col, strength * 0.5, 16)
            c.soft(Sh([[self.pt(0, 0, 0), self.pt(0, Hb, 0), self.pt(width * 0.8, Hb, 0), self.pt(width * 0.8, 0, 0)]]), col,
                   strength * 0.5, 16)
        if self.back[2] < self.W:
            c.soft(Sh([[self.pt(Wb - width, 0, 0), self.pt(Wb, 0, 0), self.pt(Wb, 0, zr), self.pt(Wb - width, 0, zr)]]), col,
                   strength, 12)
            c.soft(Sh([[self.pt(Wb, 0, 0), self.pt(Wb, Hb, 0), self.pt(Wb, Hb, width), self.pt(Wb, 0, width)]]), col,
                   strength * 0.5, 16)
            c.soft(Sh([[self.pt(Wb - width * 0.8, 0, 0), self.pt(Wb - width * 0.8, Hb, 0), self.pt(Wb, Hb, 0), self.pt(Wb, 0, 0)]]),
                   col, strength * 0.5, 16)
        c.soft(Sh([[self.pt(0, Hb, 0), self.pt(Wb, Hb, 0), self.pt(Wb, Hb, width * 2), self.pt(0, Hb, width * 2)]]), col,
               strength * 0.7, 18)

    def contact(self, X0, X1, Z0, Z1, strength=0.5, grow=12, blur_px=10):
        """Soft contact shadow on the floor under a box footprint."""
        self.c.soft(Sh([[self.pt(X0 - grow, 0, Z0 - grow * 0.5), self.pt(X1 + grow, 0, Z0 - grow * 0.5),
                         self.pt(X1 + grow, 0, Z1 + grow), self.pt(X0 - grow, 0, Z1 + grow)]]), (24, 6, 34), strength,
                    blur_px)

    # ---- walkable area
    def floor_poly(self, pts_xz):
        """Screen polygon of floor points given in (X, Z)."""
        return [self.pt(X, 0, Z) for X, Z in pts_xz]


def vp_for_walk(y_top, y_bot):
    """Eye-line y that makes perspective agree with the game's linear depth scale (0.6 .. 1.0)."""
    return y_top - 1.5 * (y_bot - y_top)


def depth_scale(y, y_top, y_bot):
    """The game's character scale at screen y for a walkable area spanning y_top..y_bot (px)."""
    t = (y_bot - y) / (y_bot - y_top)
    return 1.0 - 0.4 * max(0.0, min(1.0, t))


def px_to_world(x, y):
    return (round(x / 100 - 9.6, 2), round(5.4 - y / 100, 2))


def world_to_px(x, y):
    return ((x + 9.6) * 100, (5.4 - y) * 100)


# =========================================================================== surface painters (flat space)
def plaster_wall(c, col_top, col_bot, seed=1, streaks=True, w=None, h=None):
    """Painted plaster with mottled, streaky paint: fills the whole flat canvas."""
    w = w or c.w
    h = h or c.h
    c.ink(rect(-5, -5, w + 5, h + 5), ("vy", 0, h, col_top, col_bot), lw=0, shade=0, hi=0, ao=0, tex=0.0, wob=0)
    rng = random.Random(seed)
    # mottled paint: large soft lighter / darker patches
    for _ in range(int(w * h / 26000)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(30, 120)
        col = hi_col(col_top, 0.25) if rng.random() < 0.5 else shade_col(col_bot, 0.8)
        c.soft(ell(x, y, r, r * rng.uniform(0.4, 1.0), rng.uniform(0, 180)), col, rng.uniform(0.06, 0.16), r * 0.4)
    if streaks:
        # roller / brush streaks
        for _ in range(int(w / 9)):
            x = rng.uniform(0, w)
            y0 = rng.uniform(-20, h * 0.6)
            L = rng.uniform(60, 260)
            col = hi_col(col_top, 0.3) if rng.random() < 0.5 else shade_col(col_top, 0.85)
            c.stroke([(x, y0), (x + rng.uniform(-6, 6), y0 + L)], rng.uniform(4, 12), col, wob=1.5,
                     opacity=rng.uniform(0.04, 0.09), taper=(0.4, 0.4), blur_px=1.5)


def chip(c, x, y, r, brick=(170, 70, 80), mortar=(96, 40, 70), wall=(200, 90, 150), seed=0, bw=40, bh=18):
    """An irregular chunk of missing plaster at (x, y) radius r showing bricks, with a lit lower lip."""
    rng = random.Random(seed)
    n = 11
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * rng.uniform(0.55, 1.15)
        pts.append((x + math.cos(a) * rr * 1.35, y + math.sin(a) * rr * 0.85))
    sh = blob(pts, 1)
    # plaster lip highlight (just outside the hole, lower edge) and a dark rim
    c.ink(blob([(px + (px - x) * 0.14, py + (py - y) * 0.2 + 3) for px, py in pts], 1), hi_col(wall, 0.35), lw=0,
          shade=0, hi=0, ao=0, tex=0.1, wob=0.6, opacity=0.9)
    rngb = random.Random(seed + 1)
    c.ink(sh, mortar, lw=0, shade=0, hi=0, ao=0, tex=0.2, wob=0.6)
    bx0, by0, bx1, by1 = sh.bbox()
    row = int(by0 // bh) - 1
    yy = row * bh
    while yy < by1 + bh:
        off = (bw / 2) * (row % 2)
        xx = math.floor(bx0 / bw) * bw - bw - off
        while xx < bx1 + bw:
            col = mix(brick, (255, 170, 150) if rngb.random() < 0.5 else (80, 30, 60), rngb.uniform(0.0, 0.3))
            c.ink(wonky(xx + 2, yy + 2, xx + bw - 2, yy + bh - 2, 1.0, rngb, 1), col, lw=1.4, oc=dk(mortar, 0.55),
                  shade=0.5, sw=4, hi=0.4, hw=2.5, ao=0, tex=0.3, wob=0.3, clip=sh)
            xx += bw
        yy += bh
        row += 1
    # shadow of the plaster lip on the bricks (top of the hole)
    c.soft(Sh([[(px, py - 6) for px, py in pts]]), (30, 6, 40), 0.0, 0)
    c.soft(Sh([pts]), (30, 6, 40), 0.3, 3, clip=sh)
    c.ink(sh, (0, 0, 0, 0), lw=2.4, oc=INK, line_only=True, wob=0.5, lwvar=0.8)


def stain(c, x, y, r, col=(60, 20, 50), opacity=0.18, drips=0, seed=0):
    """Water/grime stain with a darker ring and optional drips running down."""
    rng = random.Random(seed)
    pts = [(x + math.cos(a) * r * rng.uniform(0.7, 1.2), y + math.sin(a) * r * rng.uniform(0.5, 0.9))
           for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
    c.soft(blob(pts, 2), col, opacity, r * 0.18)
    c.stroke(chaikin(pts, 2) + [chaikin(pts, 2)[0]], 2.0, col, opacity=opacity * 0.7, wob=1.0, taper=(0, 0),
             blur_px=1.2)
    for _ in range(drips):
        dx = x + rng.uniform(-r * 0.7, r * 0.7)
        L = rng.uniform(r * 0.6, r * 2.4)
        c.stroke([(dx, y + r * 0.3), (dx + rng.uniform(-3, 3), y + r * 0.3 + L)], rng.uniform(3, 6), col,
                 opacity=opacity * 1.1, taper=(0.1, 0.6), wob=0.8, blur_px=0.6)
        c.soft(ell(dx, y + r * 0.3 + L, 3.5, 4.5), col, opacity * 1.2, 0.6)


def crack(c, x, y, L, ang=90, col=INK, w=2.2, seed=0, branches=2, opacity=0.8):
    """Jagged branching crack starting at (x, y)."""
    rng = random.Random(seed)
    pts = [(x, y)]
    a = math.radians(ang)
    seg = L / 7
    for _ in range(7):
        a += rng.uniform(-0.6, 0.6)
        px, py = pts[-1]
        pts.append((px + math.cos(a) * seg, py + math.sin(a) * seg))
    c.stroke(pts, w, col, taper=(0.05, 0.8), smooth=0, wob=0.3, opacity=opacity)
    # light edge below for depth
    c.stroke([(px + 1.2, py + 1.5) for px, py in pts], w * 0.5, (255, 220, 240), taper=(0.05, 0.8), smooth=0,
             wob=0.3, opacity=opacity * 0.25)
    for b in range(branches):
        i = rng.randint(1, 5)
        bx, by = pts[i]
        crack(c, bx, by, L * 0.4, math.degrees(a) + rng.choice([-50, 50]), col, w * 0.7, seed + b + 7, 0, opacity)


def scuffs(c, x0, x1, y, n=12, col=(40, 16, 40), seed=0, opacity=0.18, spread=40):
    """Shoe / furniture scuffs: short soft horizontal strokes near the floor."""
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.uniform(x0, x1)
        yy = y - rng.uniform(0, spread)
        L = rng.uniform(14, 60)
        c.stroke([(x, yy), (x + L, yy + rng.uniform(-4, 4))], rng.uniform(2, 5), col, opacity=rng.uniform(0.3, 1) * opacity,
                 taper=(0.3, 0.5), wob=0.8, blur_px=0.8)


def grime_gradient(c, x0, x1, y_floor, h=120, col=(40, 14, 40), opacity=0.35):
    """Dirt build-up near the floor and in corners."""
    c.ink(rect(x0, y_floor - h, x1, y_floor + 2), ("vy", y_floor - h, y_floor, col + (0,), col), lw=0, shade=0, hi=0,
          ao=0, tex=0.3, wob=0, opacity=opacity)


def cobweb(c, x, y, r, corner="tl", col=(236, 226, 255), opacity=0.55, seed=0):
    """Corner cobweb: radial threads + sagging rings. corner says which way it opens (tl, tr, bl, br,
    or 'hang' for a free-hanging tatter)."""
    rng = random.Random(seed)
    sx = 1 if corner in ("tl", "bl") else -1
    sy = 1 if corner in ("tl", "tr") else -1
    angs = np.linspace(0, 90, 6)
    rays = []
    for a in angs:
        ar = math.radians(a + rng.uniform(-6, 6))
        L = r * rng.uniform(0.75, 1.1)
        end = (x + sx * math.cos(ar) * L, y + sy * math.sin(ar) * L)
        rays.append(end)
        c.stroke([(x, y), end], 1.3, col, opacity=opacity, taper=(0, 0.5), wob=0.4, smooth=0)
    for k in (0.3, 0.52, 0.74, 0.95):
        pts = []
        for i in range(len(rays) - 1):
            a = (x + (rays[i][0] - x) * k, y + (rays[i][1] - y) * k)
            b = (x + (rays[i + 1][0] - x) * k, y + (rays[i + 1][1] - y) * k)
            mid = ((a[0] + b[0]) / 2 - sx * 4 * k, (a[1] + b[1]) / 2 - sy * 4 * k)
            pts += bez(a, mid, b, 6)
        c.stroke(pts, 1.0, col, opacity=opacity * 0.85, taper=(0.1, 0.1), wob=0.4, smooth=0)
    # a loose strand hanging down
    hx = x + sx * r * 0.55
    hy = y + sy * r * 0.3
    c.stroke([(hx, hy), (hx + rng.uniform(-6, 6), hy + r * 0.5 * (1 if sy > 0 else 0.4))], 1.0, col,
             opacity=opacity * 0.7, taper=(0, 0.7))


def hanging_web(c, x, y, L, col=(236, 226, 255), opacity=0.5, seed=0):
    rng = random.Random(seed)
    for k in range(3):
        dx = rng.uniform(-14, 14)
        c.stroke([(x + dx * 0.2, y), (x + dx, y + L * rng.uniform(0.5, 1.0))], 1.1, col, opacity=opacity,
                 taper=(0, 0.8), wob=1.2)


# =========================================================================== props: cables, pipes, lamps
def cable(c, a, b, sag=60, w=7, col=(40, 30, 60), hi=None, seed=0, outline=True):
    """Sagging cable between a and b (catenary-ish), inked with a highlight."""
    mid = ((a[0] + b[0]) / 2, max(a[1], b[1]) + sag)
    pts = bez(a, (mid[0], mid[1] + sag * 0.5), b, 40)
    if outline:
        c.stroke(pts, w + 3.2, INK, taper=(0, 0), wob=0.3, smooth=0, seed=seed)
    c.stroke(pts, w, col, taper=(0, 0), wob=0.3, smooth=0, seed=seed)
    c.stroke([(x, y - w * 0.22) for x, y in pts], w * 0.28, hi or hi_col(col, 0.45), taper=(0.1, 0.1), wob=0.3,
             smooth=0, opacity=0.8, seed=seed)
    return pts


def hanging_cable(c, top, L, sway=20, w=6, col=(40, 30, 60), plug=True, seed=0):
    """A cable hanging down from the ceiling, ending in a plug or frayed end."""
    rng = random.Random(seed)
    x, y = top
    pts = bez((x, y), (x + sway, y + L * 0.6), (x + sway * 0.4 + rng.uniform(-8, 8), y + L), 30)
    c.stroke(pts, w + 3, INK, taper=(0, 0), wob=0.3, smooth=0)
    c.stroke(pts, w, col, taper=(0, 0), wob=0.3, smooth=0)
    c.stroke([(px - w * 0.2, py) for px, py in pts], w * 0.28, hi_col(col, 0.45), taper=(0.1, 0.1), opacity=0.8,
             smooth=0)
    ex, ey = pts[-1]
    if plug:
        c.ink(rrect(ex - w * 0.9, ey - 2, ex + w * 0.9, ey + w * 2.2, 3), (60, 56, 74), lw=2.2, sw=4)
        for dx in (-w * 0.4, w * 0.4):
            c.stroke([(ex + dx, ey + w * 2.2), (ex + dx, ey + w * 3.2)], 1.8, (220, 200, 120), taper=(0, 0))
    return pts


def pipe(c, pts, w=26, col=(120, 90, 160), seed=0, joints=True, brackets=()):
    """Exposed pipe along a polyline with joints, highlight and shadow."""
    sh = limb(pts, [w] * len(pts), smooth=0, ends=False)
    c.ink(sh, col, lw=3.2, shade=0.6, sw=w * 0.45, hi=0.45, hw=w * 0.22, rim=0.25, tex=0.15, seed=seed)
    if joints:
        for p in pts[1:-1]:
            c.ink(ell(p[0], p[1], w * 0.7, w * 0.7), dk(col, 0.92), lw=2.8, shade=0.5, sw=w * 0.3, hi=0.4)
    for (x, y) in brackets:
        c.ink(rrect(x - w * 0.45, y - w * 0.75, x + w * 0.45, y + w * 0.75, 3), (150, 150, 170), lw=2.4, sw=5)


def pendant_lamp(c, x, y_ceil, y_lamp, w=120, col=(214, 62, 120), seed=0, glow=True, cone_to=None, cone_w=None,
                 cone_strength=0.32):
    """Hanging dome lamp with cord, glowing bulb and an optional cone of light down to y=cone_to."""
    c.stroke([(x, y_ceil), (x + 2, y_lamp - w * 0.28)], 4.5, INK, taper=(0, 0))
    c.stroke([(x, y_ceil), (x + 2, y_lamp - w * 0.28)], 2.2, (70, 60, 80), taper=(0, 0))
    hw = w / 2
    shade_pts = [(x - hw * 0.22, y_lamp - w * 0.3), (x + hw * 0.22, y_lamp - w * 0.3), (x + hw * 0.55, y_lamp - w * 0.16),
                 (x + hw * 0.92, y_lamp + w * 0.08), (x + hw, y_lamp + w * 0.16), (x - hw, y_lamp + w * 0.16),
                 (x - hw * 0.92, y_lamp + w * 0.08), (x - hw * 0.55, y_lamp - w * 0.16)]
    if cone_to:
        cw = cone_w or w * 3.2
        c.light_cone((x, y_lamp + w * 0.1), (x - cw, cone_to), (x + cw, cone_to), strength=cone_strength, blur_px=30)
    c.ink(blob(shade_pts, 2), col, lw=3.6, shade=0.55, sw=w * 0.25, hi=0.45, hw=w * 0.12, rim=0.2, tex=0.18,
          light=(-0.6, -0.8))
    # inside of the shade (lit) + bulb
    c.ink(ell(x, y_lamp + w * 0.16, hw * 0.98, w * 0.07), (255, 236, 170), lw=2.4, shade=0, hi=0, ao=0)
    c.ink(ell(x, y_lamp + w * 0.2, w * 0.13, w * 0.12), (255, 250, 220), lw=2.2, shade=0, hi=0, ao=0)
    if glow:
        c.glow2(x, y_lamp + w * 0.22, w * 1.4, GLOW, 0.6)
        c.glow2(x, y_lamp + w * 0.2, w * 0.45, (255, 250, 220), 0.7, mode="screen")
    # scuffs on the shade
    rng = random.Random(seed)
    for _ in range(3):
        sx = x + rng.uniform(-hw * 0.6, hw * 0.6)
        sy = y_lamp + rng.uniform(-w * 0.12, w * 0.08)
        c.ink(ell(sx, sy, rng.uniform(4, 9), rng.uniform(3, 6)), dk(col, 0.75), lw=0, shade=0, hi=0, ao=0,
              opacity=0.6, atop=True)


def bulb(c, x, y, r=9, col=(255, 240, 180), strength=0.55, cord_from=None):
    if cord_from:
        c.stroke([cord_from, (x, y - r)], 3.5, INK, taper=(0, 0))
    c.ink(rrect(x - r * 0.45, y - r * 1.6, x + r * 0.45, y - r * 0.7, 2), (90, 86, 100), lw=2, sw=3)
    c.ink(ell(x, y, r, r * 1.1), col, lw=2.2, shade=0, hi=0, ao=0)
    c.glow2(x, y, r * 9, GLOW, strength)
    c.glow2(x, y, r * 2.5, (255, 255, 230), 0.7)


def floor_pool(c, cx, cy, rx, ry, color=GLOW, strength=0.35):
    c.glow2(cx, cy, rx, color, strength, sy=ry / rx)


def contact_shadow(c, cx, cy, rx, ry, opacity=0.45, col=(30, 8, 40)):
    c.soft(ell(cx, cy, rx, ry), col, opacity, ry * 0.6)


# =========================================================================== foreground silhouettes
FG = (20, 10, 36)
FG_RIM = (120, 70, 190)


def fg_paint(c, fn, blur_px=4.0, rim=True):
    """Draw a dark foreground silhouette group with fn(sub) (shapes in canvas coords) and composite it
    slightly out of focus with a faint rim light."""
    def layer(sub):
        fn(sub)
    tmp = Canvas2(c.w, c.h, seed=c.seed + 77)
    fn(tmp)
    im = tmp.img
    if rim:
        a = np.asarray(im.getchannel("A"), np.float32) / 255
        sh_ = shift(a, 3 * S, 4 * S)
        edge = np.clip(a - sh_, 0, 1)
        arr = np.asarray(im, np.float32).copy()
        rc = np.array(FG_RIM, np.float32)
        arr[..., :3] = arr[..., :3] * (1 - edge[..., None] * 0.55) + rc * edge[..., None] * 0.55
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    if blur_px:
        im = im.filter(ImageFilter.GaussianBlur(blur_px * S))
    c.img.alpha_composite(im)


def fg_chair_back(c, x, y, w=300, h=260, col=FG):
    """Round-backed chair seen from behind, bottom edge off-screen."""
    c.ink(blob([(x - w / 2, y + h), (x - w * 0.52, y + h * 0.35), (x - w * 0.35, y + h * 0.05), (x, y),
                (x + w * 0.35, y + h * 0.05), (x + w * 0.52, y + h * 0.35), (x + w / 2, y + h)], 2), col, lw=0,
          shade=0.3, hi=0.15, ao=0, tex=0.08)
    for k in (-0.22, 0.0, 0.22):
        c.stroke([(x + w * k, y + h * 0.25), (x + w * k * 1.05, y + h)], 5, mix(col, (90, 60, 120), 0.4), opacity=0.6)


def fg_bottles(c, x, y_base, n=5, scale=1.0, col=FG, seed=0):
    rng = random.Random(seed)
    xx = x
    for i in range(n):
        h = rng.uniform(150, 230) * scale
        w = rng.uniform(46, 64) * scale
        neck = w * 0.32
        pts = [(xx - w / 2, y_base), (xx - w / 2, y_base - h * 0.6), (xx - neck / 2, y_base - h * 0.78),
               (xx - neck / 2, y_base - h), (xx + neck / 2, y_base - h), (xx + neck / 2, y_base - h * 0.78),
               (xx + w / 2, y_base - h * 0.6), (xx + w / 2, y_base)]
        c.ink(blob(pts, 1), mix(col, (60, 30, 90), rng.uniform(0, 0.4)), lw=0, shade=0.2, hi=0.25, hw=6, ao=0)
        xx += w * rng.uniform(0.7, 0.95)


def fg_plant(c, x, y_base, size=260, col=FG, seed=0, flip=False):
    rng = random.Random(seed)
    sgn = -1 if flip else 1
    for k in range(9):
        a = math.radians(-90 + sgn * rng.uniform(-70, 70))
        L = size * rng.uniform(0.6, 1.0)
        tip = (x + math.cos(a) * L, y_base + math.sin(a) * L)
        mid = (x + math.cos(a) * L * 0.5 + rng.uniform(-30, 30), y_base + math.sin(a) * L * 0.5)
        spine = bez((x, y_base), mid, tip, 16)
        wv = [size * 0.02] + [size * 0.16 * math.sin(math.pi * i / 16) + 2 for i in range(1, 16)] + [2]
        c.ink(limb(spine, wv, smooth=0), mix(col, (40, 60, 70), rng.uniform(0, 0.5)), lw=0, shade=0.25, hi=0.2, ao=0)
    c.ink(rrect(x - size * 0.28, y_base - size * 0.05, x + size * 0.28, y_base + size * 0.5, 10), col, lw=0, shade=0.2,
          hi=0.1)


def fg_cable(c, pts, w=16, col=FG):
    c.stroke(pts, w, col, taper=(0, 0), smooth=2)


def fg_table_edge(c, x0, x1, y, h=200, col=FG):
    c.ink(poly([(x0, y + 20), (x1, y), (x1 + 30, y + h), (x0 - 30, y + h)]), col, lw=0, shade=0.2, hi=0.2, hw=6)


def fg_lamp_top(c, x, y, w=420, col=FG):
    """Big dark lampshade hanging into the top of frame (out of focus). (x, y) = bottom-centre of the rim."""
    c.ink(blob([(x - w / 2, y), (x - w * 0.44, y - w * 0.2), (x - w * 0.24, y - w * 0.36), (x + w * 0.24, y - w * 0.36),
                (x + w * 0.44, y - w * 0.2), (x + w / 2, y)], 2), col, lw=0, shade=0.0, hi=0.0, ao=0, tex=0)
    c.ink(ell(x, y, w / 2, w * 0.05), mix(col, (120, 70, 40), 0.5), lw=0, shade=0, hi=0, ao=0, tex=0)
    c.stroke([(x, y - w * 0.36), (x, -50)], 8, col, taper=(0, 0))


# =========================================================================== lighting / grading
def room_grade(c, lights=(), ambient=1.0, vign=0.42, shadow_tint=(70, 36, 120), top_dark=0.25, bottom_dark=0.3,
               warm=(255, 200, 120), sat=1.12, corners=0.0):
    """Colour grade a finished background: cool violet vignette + darker ceiling / bottom edge,
    warm light pools, a little extra saturation.

    lights: (x, y, radius, strength[, colour]) pools of light (brighten + warm tint)."""
    tint_ = np.array(shadow_tint, np.float32) / 255.0
    tint_ = tint_ / tint_.max()

    def fn(rgb, xs, ys):
        Wc, Hc = W_BG, H_BG
        d = np.sqrt(((xs - Wc / 2) / (Wc * 0.62)) ** 2 + ((ys - Hc * 0.52) / (Hc * 0.7)) ** 2)
        dark = np.clip(d, 0, 1.4) ** 2.2 * vign
        dark += top_dark * np.clip((Hc * 0.24 - ys) / (Hc * 0.24), 0, 1) ** 1.3
        dark += bottom_dark * np.clip((ys - Hc * 0.84) / (Hc * 0.16), 0, 1)
        dark = np.clip(dark, 0, 0.88)[..., None]
        # darken toward violet: multiply by (1 - dark * (1 - tint))... then overall darken
        out = rgb * (1 - dark * (1 - tint_[None, None, :] * 0.55)) * ambient
        lum = out.mean(axis=2, keepdims=True)
        out = lum + (out - lum) * sat
        for L in lights:
            lx, ly, r, s = L[:4]
            col = np.array(L[4] if len(L) > 4 else warm, np.float32) / 255.0
            dd = np.sqrt((xs - lx) ** 2 + (ys - ly) ** 2) / r
            fall = (np.clip(1 - dd, 0, 1) ** 1.7 * s)[..., None]
            out = out * (1 + fall * col[None, None, :] * 0.9) + fall * col[None, None, :] * 30
        return out
    c.grade(fn)


# =========================================================================== characters
class Body:
    """Character template: about 6 heads tall, slim, long legs, drawn facing RIGHT in 3/4 view
    (flip the finished sprite for a left-facing character: finish_sprite(..., flip=True)).

    Body units: u = height / 100 (feet at y=0, crown at y=100, x = 0 between the hips, +x = the way the
    character faces). b.P(x, y) converts body units to canvas px; heads and faces work in canvas px
    (b.hx, b.hy = head centre, b.r = head half-width, b.ry = 1.2 * b.r).

    build: multipliers - shoulders, waist, hips, limbs (thickness), head, belly (extra belly, units),
           chest (units), legs (length), neck, hand, foot.
    pose:  joint angles in degrees, 0 = straight down, + = swung forward (toward the facing side):
           arm_n / fore_n (near arm, drawn in front of the torso), arm_f / fore_f (far arm, behind),
           leg_n / shin_n, leg_f / shin_f, lean (torso, + = forward), head_dx / head_dy (units).
    Paint order for a typical outfit: far arm, far leg, near leg, shoes, neck, torso, head, hair,
    near arm. The caller decides colours, clothes and hair; helpers return Sh shapes to ink().
    """

    def __init__(self, c, fx, fy, height, build=None, pose=None, skin=(250, 200, 160), seed=0):
        self.c, self.fx, self.fy, self.H = c, fx, fy, height
        self.u = height / 100.0
        self.b = dict(shoulders=1.0, waist=1.0, hips=1.0, limbs=1.0, head=1.0, belly=0.0, legs=1.0, neck=1.0,
                      chest=0.0, hand=1.0, foot=1.0)
        self.b.update(build or {})
        self.p = dict(arm_n=4, fore_n=10, arm_f=-4, fore_f=8, leg_n=-3, shin_n=2, leg_f=4, shin_f=-1, lean=0,
                      head_dx=0, head_dy=0)
        self.p.update(pose or {})
        self.skin = skin
        self.skin_sh = shade_col(skin, 0.74)
        self.seed = seed
        self._joints()

    # ---- coordinates
    def P(self, x, y):
        return (self.fx + x * self.u, self.fy - y * self.u)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def _ang(self, origin, ang, L):
        a = math.radians(ang)
        return (origin[0] + math.sin(a) * L, origin[1] - math.cos(a) * L)

    def _joints(self):
        b, p = self.b, self.p
        legL = b["legs"]
        self.head_h = 17.0 * b["head"]
        self.hip_y = 48.0 * legL
        knee_y = self.hip_y * 0.53
        lean = p["lean"]
        self.hip_n = (-2.6 * b["hips"], self.hip_y)
        self.hip_f = (2.6 * b["hips"], self.hip_y + 0.4)
        self.knee_n = self._ang(self.hip_n, p["leg_n"], self.hip_y - knee_y)
        self.ankle_n = self._ang(self.knee_n, p["leg_n"] + p["shin_n"], knee_y - 4.4)
        self.knee_f = self._ang(self.hip_f, p["leg_f"], self.hip_y - knee_y)
        self.ankle_f = self._ang(self.knee_f, p["leg_f"] + p["shin_f"], knee_y - 4.4)
        top = 100 - self.head_h
        self.shoulder_y = top - 2.6 * b["neck"]
        sx = math.sin(math.radians(lean)) * (self.shoulder_y - self.hip_y)
        self.lean_dx = sx
        self.waist = (sx * 0.45, self.hip_y + 10)
        self.chest = (sx * 0.8 + 1.0, self.shoulder_y - 7)
        self.sh_n = (-7.0 * b["shoulders"] + sx, self.shoulder_y - 1.2)
        self.sh_f = (5.6 * b["shoulders"] + sx, self.shoulder_y - 0.8)
        self.neck_base = (0.4 + sx, self.shoulder_y + 0.6)
        # head (canvas px)
        self.r = 7.0 * self.u * b["head"]
        self.ry = 1.2 * self.r
        cx, cy = self.P(1.6 + sx * 1.1 + p["head_dx"], 100 + p["head_dy"])
        self.hx, self.hy = cx, cy + 0.95 * self.ry
        ua, fa = 17.0 * b.get("arms", 1.0), 14.6 * b.get("arms", 1.0)
        self.elbow_n = self._ang(self.sh_n, p["arm_n"], ua)
        self.wrist_n = self._ang(self.elbow_n, p["arm_n"] + p["fore_n"], fa)
        self.elbow_f = self._ang(self.sh_f, p["arm_f"], ua)
        self.wrist_f = self._ang(self.elbow_f, p["arm_f"] + p["fore_f"], fa)

    # ---- body parts (Sh shapes in canvas px)
    def arm_shape(self, near=True, w=None):
        sh, el, wr = (self.sh_n, self.elbow_n, self.wrist_n) if near else (self.sh_f, self.elbow_f, self.wrist_f)
        k = self.b["limbs"] if w is None else w
        return limb(self.Ps([sh, el, wr]), [5.0 * k * self.u, 3.6 * k * self.u, 2.9 * k * self.u], smooth=1)

    def sleeve(self, near=True, length=0.55, w0=7.4, w1=6.6, to_wrist=False, cuff=None):
        """Sleeve along the upper arm (length = fraction of the upper arm) or down to the wrist."""
        sh, el, wr = (self.sh_n, self.elbow_n, self.wrist_n) if near else (self.sh_f, self.elbow_f, self.wrist_f)
        k = self.b["limbs"]
        if to_wrist:
            end = (wr[0] + (el[0] - wr[0]) * 0.08, wr[1] + (el[1] - wr[1]) * 0.08)
            return limb(self.Ps([(sh[0], sh[1] + 0.6), el, end]),
                        [w0 * k * self.u, w1 * k * 0.86 * self.u, (cuff or w1 * 0.72) * k * self.u], smooth=1)
        end = (sh[0] + (el[0] - sh[0]) * length, sh[1] + (el[1] - sh[1]) * length)
        return limb(self.Ps([(sh[0] + 0.5, sh[1] - 0.2), end]), [w0 * k * self.u, w1 * k * self.u], smooth=0)

    def leg_shape(self, near=True, w=(8.0, 5.2, 3.8)):
        hp, kn, an = (self.hip_n, self.knee_n, self.ankle_n) if near else (self.hip_f, self.knee_f, self.ankle_f)
        k = self.b["limbs"]
        mid = ((hp[0] + kn[0]) / 2 + 0.6, (hp[1] + kn[1]) / 2)
        mid2 = ((kn[0] + an[0]) / 2 - 0.4, (kn[1] + an[1]) / 2 + 2)
        return limb(self.Ps([hp, mid, kn, mid2, an]),
                    [w[0] * k * self.u, w[0] * 0.86 * k * self.u, w[1] * k * self.u, w[1] * 1.02 * k * self.u,
                     w[2] * k * self.u], smooth=1)

    def segment(self, a, b, wa, wb):
        return limb(self.Ps([a, b]), [wa * self.u, wb * self.u], smooth=0)

    def torso_pts(self, slack=0.0, hem=None, flare=0.0, neck_open=1.0):
        """Torso / top outline (canvas px). hem = y (units) of the bottom edge."""
        b = self.b
        sx = self.lean_dx
        hem = self.hip_y - 1 if hem is None else hem
        s = slack
        sy = self.shoulder_y
        bl = b["belly"]
        pts = [
            (sx - 1.8 * neck_open, sy + 1.6),
            (sx + 2.6 * neck_open, sy + 1.2),
            (self.sh_f[0] + 0.4 + s * 0.5, sy - 0.6),
            (self.sh_f[0] + 1.5 + s + b["chest"], sy - 5.0),
            (self.sh_f[0] + 1.2 + s + b["chest"] * 0.8, sy - 9.0),
            (sx * 0.62 + 4.4 * b["waist"] + s + bl * 0.8, self.hip_y + 13),
            (sx * 0.45 + 4.3 * b["waist"] + s + bl, self.hip_y + 6),
            (4.9 * b["hips"] + s + flare + bl * 0.5, hem),
            (-5.3 * b["hips"] - s - flare, hem),
            (sx * 0.4 - 5.0 * b["hips"] - s, self.hip_y + 5),
            (sx * 0.6 - 4.6 * b["waist"] - s - bl * 0.2, self.hip_y + 12),
            (self.sh_n[0] + 1.0 - s * 0.6, sy - 9.0),
            (self.sh_n[0] - 0.8 - s, sy - 3.0),
            (self.sh_n[0] + 1.0 - s * 0.5, sy + 0.4),
        ]
        return chaikin(self.Ps(pts), 1)

    def neck_shape(self, w=1.0):
        top = (self.hx - 0.05 * self.r, self.hy + 0.55 * self.ry)
        base = self.P(*self.neck_base)
        k = self.b["neck"] * w
        return limb([base, top], [5.4 * k * self.u, 4.4 * k * self.u], smooth=0)

    def head_pts(self, jaw=1.0, chin=1.0, cranium=1.0, cheek=1.0, chin_drop=1.0):
        """3/4 head facing right (canvas px): round cranium at the back, jaw and chin forward."""
        hx, hy, r, ry = self.hx, self.hy, self.r, self.ry
        pts = []
        for a in np.linspace(-38, -228, 16):
            ar = math.radians(a)
            pts.append((hx + math.cos(ar) * r * cranium, hy + math.sin(ar) * ry * 0.95))
        pts += [
            (hx - 0.42 * r * jaw, hy + 0.80 * ry),
            (hx - 0.02 * r * jaw, hy + 0.98 * ry * chin_drop),
            (hx + 0.42 * r * chin, hy + 1.10 * ry * chin_drop),
            (hx + 0.74 * r * chin, hy + 1.04 * ry * chin_drop),
            (hx + 0.90 * r * cheek, hy + 0.80 * ry),
            (hx + 0.98 * r * cheek, hy + 0.52 * ry),
            (hx + 1.02 * r, hy + 0.20 * ry),
            (hx + 1.04 * r, hy - 0.08 * ry),
            (hx + 0.94 * r, hy - 0.45 * ry),
        ]
        return chaikin(pts, 2)

    def face_anchor(self):
        """Face landmarks (canvas px)."""
        hx, hy, r, ry = self.hx, self.hy, self.r, self.ry
        return dict(
            eye_n=(hx + 0.24 * r, hy + 0.10 * ry),
            eye_f=(hx + 0.80 * r, hy + 0.09 * ry),
            brow_n=(hx + 0.24 * r, hy - 0.30 * ry),
            brow_f=(hx + 0.84 * r, hy - 0.29 * ry),
            nose=(hx + 1.04 * r, hy + 0.42 * ry),
            mouth=(hx + 0.64 * r, hy + 0.78 * ry),
            ear=(hx - 0.40 * r, hy + 0.26 * ry),
            top=(hx, hy - 0.95 * ry),
            back=(hx - r, hy),
            chin=(hx + 0.5 * r, hy + 1.08 * ry),
            r=r, ry=ry, c=(hx, hy),
        )

    # ---- standard face parts
    def nose(self, kind="long", size=1.0, col=None):
        c = self.c
        r = self.r * size
        nx, ny = self.face_anchor()["nose"]
        col = col or self.skin
        if kind == "button":
            sh = ell(nx + r * 0.02, ny - r * 0.02, r * 0.17, r * 0.14)
        elif kind == "round":
            sh = blob([(nx - r * 0.18, ny - r * 0.34), (nx + r * 0.1, ny - r * 0.14), (nx + r * 0.24, ny + r * 0.04),
                       (nx + r * 0.12, ny + r * 0.16), (nx - r * 0.2, ny + r * 0.12)], 2)
        elif kind == "hook":
            sh = blob([(nx - r * 0.25, ny - r * 0.5), (nx + r * 0.12, ny - r * 0.24), (nx + r * 0.3, ny + r * 0.05),
                       (nx + r * 0.16, ny + r * 0.16), (nx - r * 0.2, ny + r * 0.12)], 2)
        else:  # long, pointy
            sh = blob([(nx - r * 0.24, ny - r * 0.46), (nx + r * 0.18, ny - r * 0.08), (nx + r * 0.36, ny + r * 0.08),
                       (nx + r * 0.1, ny + r * 0.17), (nx - r * 0.22, ny + r * 0.13)], 2)
        c.ink(sh, col, lw=c.lw * 0.8, shade=0.45, sw=r * 0.12, hi=0.35, hw=r * 0.06, ao=0)
        c.stroke([(nx - r * 0.06, ny + r * 0.08), (nx + r * 0.05, ny + r * 0.11)], max(1.4, r * 0.05), INK,
                 taper=(0.2, 0.2), smooth=0)

    def ear(self, size=1.0, col=None, jug=0.0):
        c = self.c
        ex, ey = self.face_anchor()["ear"]
        r = self.r * size
        col = col or self.skin
        sh = blob([(ex + r * 0.12, ey - r * 0.3), (ex - r * (0.18 + jug * 0.2), ey - r * (0.48 + jug * 0.1)),
                   (ex - r * (0.42 + jug * 0.35), ey - r * 0.25), (ex - r * (0.4 + jug * 0.3), ey + r * 0.22),
                   (ex - r * 0.16, ey + r * 0.4), (ex + r * 0.12, ey + r * 0.24)], 2)
        c.ink(sh, col, lw=c.lw * 0.85, shade=0.45, sw=r * 0.14, hi=0.3, rim=0.2, rcol=(255, 150, 140))
        c.stroke([(ex - r * 0.02, ey - r * 0.22), (ex - r * (0.25 + jug * 0.25), ey - r * 0.16),
                  (ex - r * (0.24 + jug * 0.2), ey + r * 0.14), (ex - r * 0.05, ey + r * 0.2)], max(1.4, r * 0.05),
                 shade_col(col, 0.7), taper=(0.2, 0.4))

    def eyes(self, iris=(70, 130, 200), look=(0.3, 0.05), lid=0.1, lower=0.0, lashes=0, size=1.0, closed=False,
             tilt=0.0, far=1.0):
        fa = self.face_anchor()
        r = self.r * size
        ex, ey = fa["eye_n"]
        self.eye(ex, ey, r * 0.30, r * 0.40, look=look, lid=lid, lower=lower, iris=iris, lashes=lashes,
                 lid_tilt=tilt, closed=closed, lw=max(1.8, self.c.lw * 0.72))
        fx, fy = fa["eye_f"]
        self.eye(fx, fy, r * 0.20 * far, r * 0.37, look=(look[0] * 0.8, look[1]), lid=lid, lower=lower, iris=iris,
                 lashes=lashes, lid_tilt=-tilt, closed=closed, lw=max(1.6, self.c.lw * 0.64))

    def brows(self, col=INK, w=None, lift_n=0.0, lift_f=0.0, tilt_n=0.0, tilt_f=0.0, arch=0.06):
        """Eyebrows. tilt > 0 raises the inner (nose-side) end: worried; < 0: angry."""
        fa = self.face_anchor()
        r = self.r
        w = w or max(2.6, self.r * 0.12)
        bx, by = fa["brow_n"]
        by -= lift_n * r
        self.brow((bx - r * 0.3, by + r * 0.02 + tilt_n * r * 0.12), (bx + r * 0.26, by - tilt_n * r * 0.12),
                  mid_lift=r * arch, w=w, col=col)
        bx, by = fa["brow_f"]
        by -= lift_f * r
        self.brow((bx - r * 0.12, by - tilt_f * r * 0.1), (bx + r * 0.2, by + r * 0.02 + tilt_f * r * 0.06),
                  mid_lift=r * arch * 0.7, w=w * 0.85, col=col)

    # ---- face primitives
    def eye(self, cx, cy, rx, ry, look=(0.35, 0.0), lid=0.18, lower=0.0, iris=(70, 130, 200), lashes=0,
            lid_tilt=0.0, rot=0, pupil=0.48, lw=2.0, closed=False, glint=True):
        """Big expressive eye (canvas px). look = pupil offset in eye radii, lid = upper lid cover 0..1."""
        c = self.c
        if closed:
            c.stroke(bez((cx - rx * 1.05, cy + ry * 0.05), (cx, cy + ry * 0.55), (cx + rx * 1.05, cy), 12), lw * 1.4,
                     INK, taper=(0.2, 0.2), smooth=0)
            if lashes:
                for k in range(2):
                    xx = cx + lashes * rx * (0.8 + k * 0.25)
                    c.stroke([(xx, cy + k * 2), (xx + lashes * rx * 0.35, cy - ry * 0.25 + k * 3)], lw, INK,
                             taper=(0, 0.6))
            return
        white = ell(cx, cy, rx, ry, rot)
        c.ink(white, (252, 250, 246), lw=lw, shade=0.3, sw=ry * 0.45, scol=(196, 190, 226), hi=0, ao=0.0, tex=0,
              wob=0.15, light=(0.0, 1.0), inner=0.55)
        px, py = cx + look[0] * rx, cy + look[1] * ry
        ir = min(rx * 0.95, ry * 0.72)
        c.ink(ell(px, py, ir * 0.9, ir), iris, lw=0, shade=0.55, sw=ir * 0.6, hi=0.45, hw=ir * 0.35,
              light=(0.1, 0.99), clip=white, ao=0, tex=0, wob=0)
        c.ink(ell(px, py, ir * 0.9, ir), (0, 0, 0, 0), lw=1.0, oc=dk(iris, 0.45), line_only=True, clip=white, wob=0)
        c.ink(ell(px + ir * 0.05, py, ir * pupil, ir * pupil * 1.08), (18, 10, 22), lw=0, shade=0, hi=0, clip=white,
              ao=0, tex=0, wob=0)
        if glint:
            c.ink(ell(px - ir * 0.3, py - ir * 0.38, ir * 0.26, ir * 0.24), (255, 255, 255), lw=0, shade=0, hi=0,
                  clip=white, ao=0, tex=0, wob=0)
            c.ink(ell(px + ir * 0.32, py + ir * 0.36, ir * 0.11, ir * 0.11), (255, 255, 255), lw=0, shade=0, hi=0,
                  clip=white, ao=0, tex=0, wob=0, opacity=0.85)
        if lid > 0:
            ly = cy - ry + 2 * ry * lid
            lidsh = Sh([[(cx - rx * 1.5, cy - ry * 1.6), (cx + rx * 1.5, cy - ry * 1.6), (cx + rx * 1.5, ly + lid_tilt * ry),
                         (cx - rx * 1.5, ly - lid_tilt * ry)]])
            c.ink(lidsh, self.skin, lw=0, shade=0.0, hi=0, ao=0, tex=0, wob=0, clip=white)
            c.ink(lidsh, self.skin_sh, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=white, opacity=0.4)
            # lid line follows the eye width at that height
            def half_w(yy):
                t = max(-1.0, min(1.0, (yy - cy) / ry))
                return rx * math.sqrt(max(0.0, 1 - t * t))
            y_l, y_r = ly - lid_tilt * ry, ly + lid_tilt * ry
            c.stroke([(cx - half_w(y_l) - lw * 0.4, y_l), (cx, ly - ry * 0.05), (cx + half_w(y_r) + lw * 0.4, y_r)],
                     lw * 1.5, INK, taper=(0.15, 0.15), smooth=1)
        else:
            c.stroke(ell_pts(cx, cy, rx, ry, rot, 30, 200, 340), lw * 1.5, INK, taper=(0.25, 0.25), smooth=0)
        if lower > 0:
            ly = cy + ry - 2 * ry * lower
            c.ink(Sh([[(cx - rx * 1.5, cy + ry * 1.6), (cx + rx * 1.5, cy + ry * 1.6), (cx + rx * 1.5, ly),
                       (cx - rx * 1.5, ly)]]), self.skin, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=white)
            c.stroke([(cx - rx * 0.85, ly + ry * 0.04), (cx, ly - ry * 0.04), (cx + rx * 0.85, ly + ry * 0.04)], lw * 0.8,
                     INK, taper=(0.3, 0.3), smooth=1)
        if lashes:
            bx = cx + lashes * rx * 0.96
            by = cy - ry * 0.25 + (2 * ry * lid if lid else 0) * 0.5
            for k in range(3):
                c.stroke([(bx - lashes * k * rx * 0.22, by - k * ry * 0.2),
                          (bx + lashes * (rx * 0.5 - k * rx * 0.08), by - ry * 0.32 - k * ry * 0.24)],
                         lw * 0.95, INK, taper=(0, 0.7), smooth=0)

    def brow(self, a, b, mid_lift=0.0, w=3.0, col=None):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - mid_lift)
        self.c.stroke(bez(a, mid, b, 12), w, col or INK, taper=(0.15, 0.55), smooth=0)

    def mouth(self, kind, cx=None, cy=None, w=None, h=None, open_col=(110, 26, 48), lip=None, teeth=True):
        """Mouths: smile, grin, teeth, open, o, flat, frown, smirk, worried."""
        c = self.c
        fa = self.face_anchor()
        cx = fa["mouth"][0] if cx is None else cx
        cy = fa["mouth"][1] if cy is None else cy
        w = w or self.r * 0.62
        h = h or w * 0.5
        lwm = max(1.8, self.r * 0.07)
        if kind in ("smile", "smirk", "flat", "frown", "worried"):
            if kind == "smile":
                pts = bez((cx - w / 2, cy - h * 0.25), (cx, cy + h * 0.6), (cx + w / 2, cy - h * 0.4), 14)
            elif kind == "smirk":
                pts = bez((cx - w / 2, cy + h * 0.1), (cx + w * 0.1, cy + h * 0.25), (cx + w / 2, cy - h * 0.4), 14)
            elif kind == "flat":
                pts = bez((cx - w / 2, cy), (cx, cy + h * 0.08), (cx + w / 2, cy - h * 0.04), 10)
            elif kind == "frown":
                pts = bez((cx - w / 2, cy + h * 0.3), (cx, cy - h * 0.35), (cx + w / 2, cy + h * 0.25), 14)
            else:
                pts = [(cx - w / 2, cy + h * 0.2), (cx - w * 0.2, cy - h * 0.1), (cx + w * 0.1, cy + h * 0.15),
                       (cx + w / 2, cy - h * 0.05)]
            if lip:
                lower = [(x, y + h * 0.32 * math.sin(math.pi * i / max(1, len(pts) - 1)))
                         for i, (x, y) in enumerate(pts)]
                c.ink(Sh([pts + lower[::-1]]), lip, lw=lwm * 0.7, shade=0.3, sw=h * 0.2, hi=0.4, hw=h * 0.1, ao=0,
                      tex=0, wob=0)
            c.stroke(pts, lwm, INK, taper=(0.3, 0.3), smooth=1)
            for end in (pts[0], pts[-1]):
                c.stroke([(end[0] - w * 0.05, end[1] - h * 0.12), (end[0] + w * 0.03, end[1] + h * 0.12)], lwm * 0.6, INK,
                         taper=(0.3, 0.3), smooth=0, opacity=0.7)
            return
        if kind in ("grin", "teeth"):
            top = bez((cx - w / 2, cy - h * 0.3), (cx, cy - h * 0.05), (cx + w / 2, cy - h * 0.45), 12)
            bot = bez((cx + w / 2, cy - h * 0.45), (cx + w * 0.05, cy + h * 1.0), (cx - w / 2, cy - h * 0.3), 14)
            sh = Sh([top + bot])
            c.ink(sh, open_col, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
            c.ink(Sh([[(x, y - h) for x, y in top] + [(x, y + h * 0.28) for x, y in top[::-1]]]), (252, 250, 240), lw=0,
                  shade=0.25, sw=h * 0.2, hi=0, ao=0, tex=0, wob=0, clip=sh)
            if kind == "teeth":
                for k in (-0.22, 0.04, 0.28):
                    xx = cx + w * k
                    c.stroke([(xx, cy - h * 0.3), (xx, cy - h * 0.0)], 1.1, INK_SOFT, taper=(0, 0), smooth=0, opacity=0.55)
            c.ink(ell(cx + w * 0.05, cy + h * 0.55, w * 0.22, h * 0.2), (226, 96, 116), lw=0, shade=0, hi=0, ao=0, tex=0,
                  wob=0, clip=sh)
            c.ink(sh, (0, 0, 0, 0), lw=lwm, line_only=True, wob=0.2)
            return
        if kind == "o":
            sh = ell(cx, cy, w * 0.26, h * 0.42)
        else:
            sh = blob([(cx - w / 2, cy - h * 0.2), (cx, cy - h * 0.12), (cx + w / 2, cy - h * 0.32),
                       (cx + w * 0.25, cy + h * 0.6), (cx - w * 0.2, cy + h * 0.55)], 2)
        c.ink(sh, open_col, lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
        bx0, by0, bx1, by1 = sh.bbox()
        c.ink(ell((bx0 + bx1) / 2, by1, (bx1 - bx0) * 0.32, (by1 - by0) * 0.32), (226, 96, 116), lw=0, shade=0, hi=0,
              ao=0, tex=0, wob=0, clip=sh)
        if teeth and kind == "open":
            c.ink(rect(bx0, by0 - 2, bx1, by0 + (by1 - by0) * 0.24), (252, 250, 240), lw=0, shade=0, hi=0, ao=0, tex=0,
                  wob=0, clip=sh)
        c.ink(sh, (0, 0, 0, 0), lw=lwm, line_only=True, wob=0.2)

    def cheeks(self, x, y, r, col=(255, 120, 130), opacity=0.35):
        self.c.soft(ell(x, y, r, r * 0.6), col, opacity, r * 0.35)

    # ---- hands / feet
    def hand(self, near=True, kind="relaxed", col=None, size=1.0, d=None, thumb=1, lw=None):
        """Cartoon hand at the wrist. kind: relaxed, fist, open, point, hold, flat.
        d: optional screen direction (dx, dy) of the hand (default: along the forearm).
        thumb: +1 thumb on the facing side when the arm hangs down. Returns the grip point (px)."""
        c = self.c
        col = col or self.skin
        el, wr = (self.elbow_n, self.wrist_n) if near else (self.elbow_f, self.wrist_f)
        E, Wp = self.P(*el), self.P(*wr)
        if d is None:
            dx, dy = Wp[0] - E[0], Wp[1] - E[1]
        else:
            dx, dy = d
        Ln = math.hypot(dx, dy) or 1
        dx, dy = dx / Ln, dy / Ln
        nx, ny = dy * thumb, -dx * thumb   # thumb side normal (facing side when the arm hangs)
        u = self.u * size * self.b["hand"]
        L = 7.4 * u
        lw = lw or c.lw * 0.8
        P0 = (Wp[0] - dx * u * 0.6, Wp[1] - dy * u * 0.6)

        def at(a, b):   # a along the hand, b across (toward the thumb)
            return (P0[0] + dx * a * L + nx * b * L, P0[1] + dy * a * L + ny * b * L)
        if kind == "fist":
            sh = blob([at(0.1, -0.28), at(0.62, -0.32), at(0.78, -0.05), at(0.68, 0.3), at(0.25, 0.34), at(0.05, 0.1)], 2)
            c.ink(sh, col, lw=lw, shade=0.5, sw=u * 1.6, hi=0.3, ao=0.05)
            for k in (-0.18, 0.0, 0.18):
                c.stroke([at(0.5, k), at(0.72, k + 0.02)], max(1.2, lw * 0.45), INK_SOFT, taper=(0.3, 0.3), smooth=0)
            c.ink(blob([at(0.25, 0.3), at(0.5, 0.38), at(0.62, 0.15), at(0.4, 0.12)], 2), col, lw=lw * 0.8, shade=0.3)
            return at(0.45, 0.0)
        if kind == "flat":   # flat palm / mitten (waving, gesturing)
            fingers_len = 1.0
        else:
            fingers_len = {"relaxed": 0.9, "open": 1.05, "point": 0.55, "hold": 0.62}.get(kind, 0.9)
        palm = blob([at(0.0, -0.26), at(0.5, -0.32), at(0.56, 0.22), at(0.08, 0.3)], 2)
        fingers = Sh()
        spread = 0.2 if kind in ("open", "flat") else 0.05
        spines = []
        for i, k in enumerate((-0.24, -0.08, 0.08, 0.24)):
            base = at(0.46, k)
            ln = fingers_len * (0.5 if abs(k) > 0.2 else 0.6)
            if kind == "point" and i == 3:
                ln = 0.85
            ang_k = (k * spread * 4)
            ddx = dx + nx * ang_k
            ddy = dy + ny * ang_k
            curl = 0.3 if kind in ("relaxed", "hold") else 0.0
            if kind == "point" and i == 3:
                curl = 0.0
            tip = (base[0] + (ddx - nx * curl) * ln * L, base[1] + (ddy - ny * curl) * ln * L)
            mid = (base[0] + ddx * ln * L * 0.55, base[1] + ddy * ln * L * 0.55)
            spines.append((base, mid, tip))
            fingers = fingers + limb([base, mid, tip], [0.19 * L, 0.18 * L, 0.15 * L], smooth=0)
        c.ink(palm + fingers, col, lw=lw, shade=0.45, sw=u * 1.5, hi=0.3, ao=0.05, wob=0.3)
        for (a0, a1, a2), (b0, b1, b2) in zip(spines, spines[1:]):
            m0 = ((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2)
            m1 = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2)
            m2 = ((a2[0] * 0.6 + b2[0] * 0.4), (a2[1] * 0.6 + b2[1] * 0.4))
            c.stroke([((m0[0] + m1[0]) / 2, (m0[1] + m1[1]) / 2), m1, ((m1[0] + m2[0]) / 2, (m1[1] + m2[1]) / 2)],
                     max(1.1, lw * 0.5), INK, taper=(0.5, 0.3), smooth=0, opacity=0.85)
        tb = at(0.2, 0.24)
        tt = at(0.5, 0.48) if kind not in ("hold",) else at(0.55, 0.36)
        tm = at(0.38, 0.42)
        c.ink(limb([tb, tm, tt], [0.26 * L, 0.21 * L, 0.16 * L], smooth=0), col, lw=lw * 0.9, shade=0.4, sw=u, hi=0.3,
              ao=0, wob=0.2)
        return at(0.62, 0.0)

    def shoe(self, near=True, col=(240, 240, 236), sole=(250, 246, 236), kind="sneaker", heel_col=None, length=1.0):
        """Shoe at the ankle, pointing right (the facing direction)."""
        an = self.ankle_n if near else self.ankle_f
        x, y = an
        L = 10.5 * self.b["foot"] * length
        u = self.u
        c = self.c
        if kind == "heel":
            pts = [(x - 1.8, y + 2.4), (x + 1.8, y + 2.8), (x + L * 0.62, y - 1.4), (x + L * 0.92, y - 3.4),
                   (x + L * 0.96, y - 4.3), (x + L * 0.35, y - 4.3), (x - 0.2, y - 1.6), (x - 1.6, y - 1.2)]
            sh = blob(self.Ps(pts), 1)
            c.ink(sh, col, lw=c.lw * 0.85, shade=0.5, sw=u * 1.4, hi=0.45, hw=u * 0.6)
            c.ink(Sh([self.Ps([(x - 1.5, y - 1.0), (x - 0.3, y - 1.3), (x - 0.5, y - 4.3), (x - 1.3, y - 4.3)])]),
                  heel_col or dk(col, 0.6), lw=c.lw * 0.7, shade=0.3)
            return sh
        if kind == "boot":
            pts = [(x - 2.6, y + 12), (x + 2.8, y + 12), (x + 2.8, y + 2.4), (x + L * 0.6, y + 0.6), (x + L * 0.96, y - 1.4),
                   (x + L * 1.04, y - 3.4), (x + L * 0.88, y - 4.3), (x - 1.6, y - 4.3), (x - 2.8, y - 2.8)]
        elif kind == "slipper":
            pts = [(x - 3.2, y + 1.0), (x + 1.0, y + 2.2), (x + L * 0.6, y + 1.0), (x + L * 1.05, y - 1.4),
                   (x + L * 1.0, y - 4.3), (x - 3.4, y - 4.3), (x - 4.0, y - 1.8)]
        else:
            pts = [(x - 2.8, y + 2.4), (x + 2.0, y + 2.8), (x + L * 0.55, y + 0.8), (x + L * 0.95, y - 1.0),
                   (x + L * 1.05, y - 3.0), (x + L * 0.92, y - 4.3), (x - 2.6, y - 4.3), (x - 3.2, y - 2.0)]
        sh = blob(self.Ps(pts), 1)
        c.ink(sh, col, lw=c.lw * 0.9, shade=0.5, sw=u * 1.6, hi=0.45, hw=u * 0.8)
        if kind in ("sneaker", "boot", "shoe"):
            sole_sh = Sh([self.Ps([(x - 3.6, y - 2.9), (x + L * 1.12, y - 2.9), (x + L * 1.12, y - 4.8), (x - 3.6, y - 4.8)])])
            c.ink(sole_sh, sole, lw=0, shade=0.3, hi=0, clip=sh, ao=0)
            c.stroke(self.Ps([(x - 2.8, y - 2.95), (x + L * 1.0, y - 2.95)]), 1.3, INK, taper=(0.1, 0.1), smooth=0,
                     opacity=0.8)
            c.ink(sh, (0, 0, 0, 0), lw=c.lw * 0.9, line_only=True)
        return sh

    def ground_shadow(self, rx=None, opacity=0.35):
        rx = rx or 16 * self.u
        x = self.fx + ((self.ankle_n[0] + self.ankle_f[0]) / 2 + 4) * self.u
        self.c.soft(ell(x, self.fy - 1, rx, rx * 0.18), (30, 8, 40), opacity, rx * 0.1)


def finish_sprite(c, name, flip=False, margin=4, post=None, scale_to=None):
    """Crop a character / prop canvas to its content keeping the feet (bottom centre) anchored.

    The saved sprite's bottom-centre is the feet (the game's pivot). Returns (w, h)."""
    im = c.result()
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.nonzero(a > 8)
    if len(xs) == 0:
        return
    y1 = ys.max() + 1
    y0 = ys.min()
    # feet x: centre of the bottom 3% band
    band = ys > y1 - max(3, (y1 - y0) * 0.03)
    fx = (xs[band].min() + xs[band].max()) / 2
    half = max(fx - xs.min(), xs.max() + 1 - fx) + margin
    x0 = int(round(fx - half))
    x1 = int(round(fx + half))
    out = Image.new("RGBA", (x1 - x0, y1 - y0 + margin), (0, 0, 0, 0))
    out.alpha_composite(im.crop((max(0, x0), y0, min(im.width, x1), y1)), (max(0, -x0), margin))
    if flip:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    if post:
        out = post(out)
    if scale_to:
        k = scale_to / out.height
        out = out.resize((max(1, int(round(out.width * k))), scale_to), Image.LANCZOS)
    path = os.path.join(OUT_DIR, name)
    out.save(path, optimize=True)
    print("wrote", os.path.relpath(path, ROOT), "%dx%d" % out.size)
    return out.size


# =========================================================================== flat surface painters
def planks(c, col, x0, y0, x1, y1, pw=60, seed=0, vertical=True, gap_col=None, lw=2.4, wear=True):
    """Wooden planks filling a rectangle (flat space). vertical=True: boards run along y."""
    rng = random.Random(seed)
    gap_col = gap_col or shade_col(col, 0.45)
    c.ink(rect(x0, y0, x1, y1), col, lw=0, shade=0, hi=0, ao=0, tex=0.0, wob=0)
    a0, a1 = (x0, x1) if vertical else (y0, y1)
    b0, b1 = (y0, y1) if vertical else (x0, x1)
    a = a0
    while a < a1:
        w = pw * rng.uniform(0.9, 1.1)
        tone = mix(col, (255, 220, 170) if rng.random() < 0.5 else (60, 20, 50), rng.uniform(0.0, 0.18))
        b = b0 - rng.uniform(0, 300)
        while b < b1:
            L = rng.uniform(260, 520)
            R = (a + 1, b + 1, a + w - 1, b + L - 1) if vertical else (b + 1, a + 1, b + L - 1, a + w - 1)
            c.ink(rect(*R), mix(tone, col, rng.uniform(0, 0.5)), lw=0, shade=0.25, sw=w * 0.25, hi=0.2, hw=w * 0.12,
                  ao=0, tex=0.18, wob=0)
            # grain
            for _ in range(3):
                if vertical:
                    gx = a + rng.uniform(6, w - 6)
                    c.stroke([(gx, b + rng.uniform(0, L * 0.3)), (gx + rng.uniform(-3, 3), b + rng.uniform(L * 0.6, L))],
                             1.2, shade_col(tone, 0.75), opacity=0.35, taper=(0.3, 0.3), wob=0.8)
                else:
                    gy = a + rng.uniform(6, w - 6)
                    c.stroke([(b + rng.uniform(0, L * 0.3), gy), (b + rng.uniform(L * 0.6, L), gy + rng.uniform(-3, 3))],
                             1.2, shade_col(tone, 0.75), opacity=0.35, taper=(0.3, 0.3), wob=0.8)
            if rng.random() < 0.25:   # knot
                kx, ky = (a + w * rng.uniform(0.3, 0.7), b + L * rng.uniform(0.2, 0.8))
                if not vertical:
                    kx, ky = ky, kx
                c.ink(ell(kx, ky, 5, 3.5 if vertical else 6, 90 if vertical else 0), shade_col(tone, 0.6), lw=1.2,
                      oc=shade_col(tone, 0.4), shade=0, hi=0, ao=0, tex=0, wob=0.3)
            end = (a, b + L, a + w, b + L) if vertical else (b + L, a, b + L, a + w)
            c.stroke([(end[0], end[1]), (end[2], end[3])], lw, gap_col, taper=(0, 0), wob=0.3, opacity=0.9)
            # nail heads
            for nk in (0.25, 0.75):
                nx_, ny_ = ((a + w * nk, b + L - 10) if vertical else (b + L - 10, a + w * nk))
                c.ink(ell(nx_, ny_, 2.2, 2.2), shade_col(tone, 0.5), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0)
            b += L
        line = [(a, b0), (a, b1)] if vertical else [(b0, a), (b1, a)]
        c.stroke(line, lw, gap_col, taper=(0, 0), wob=0.4, opacity=0.95)
        a += w
    if wear:
        for _ in range(int((x1 - x0) * (y1 - y0) / 40000)):
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
            c.soft(ell(x, y, rng.uniform(20, 70), rng.uniform(8, 30)), (40, 10, 40), rng.uniform(0.05, 0.14), 10)


def tiles(c, c1, c2, x0, y0, x1, y1, size=80, seed=0, grout=None, chipped=0.08):
    """Checker / plain tiles with grout lines, dirt and a few chipped tiles (flat space)."""
    rng = random.Random(seed)
    grout = grout or shade_col(mix(c1, c2, 0.5), 0.5)
    c.ink(rect(x0, y0, x1, y1), grout, lw=0, shade=0, hi=0, ao=0, tex=0.1, wob=0)
    j = 0
    y = y0
    while y < y1:
        i = 0
        x = x0
        while x < x1:
            col = c1 if (i + j) % 2 == 0 else c2
            col = mix(col, (60, 20, 60), rng.uniform(0, 0.12))
            c.ink(rrect(x + 2.5, y + 2.5, x + size - 2.5, y + size - 2.5, 4), col, lw=0, shade=0.3, sw=size * 0.2, hi=0.35,
                  hw=size * 0.1, ao=0.05, tex=0.15, wob=0.4)
            if rng.random() < chipped:
                cx_, cy_ = x + rng.choice([6, size - 6]), y + rng.choice([6, size - 6])
                c.ink(blob([(cx_ + rng.uniform(-14, 14), cy_ + rng.uniform(-14, 14)) for _ in range(5)], 1), grout,
                      lw=1.4, shade=0, hi=0, ao=0)
            if rng.random() < 0.06:
                crack(c, x + rng.uniform(10, size - 10), y + 4, size * 0.9, rng.uniform(60, 120), shade_col(col, 0.4), 1.4,
                      seed=rng.randint(0, 999), branches=1, opacity=0.6)
            x += size
            i += 1
        y += size
        j += 1
    for _ in range(int((x1 - x0) * (y1 - y0) / 30000)):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.soft(ell(x, y, rng.uniform(20, 80), rng.uniform(10, 40)), (40, 10, 40), rng.uniform(0.05, 0.14), 12)


def carpet(c, col, x0, y0, x1, y1, seed=0, pattern=None):
    """Worn carpet: mottled pile texture, stains and an optional pattern(c) drawn on top."""
    rng = random.Random(seed)
    c.ink(rect(x0, y0, x1, y1), col, lw=0, shade=0, hi=0, ao=0, tex=0.3, wob=0)
    if pattern:
        pattern(c)
    for _ in range(int((x1 - x0) * (y1 - y0) / 1800)):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        cc = hi_col(col, 0.2) if rng.random() < 0.5 else shade_col(col, 0.8)
        c.stroke([(x, y), (x + rng.uniform(-5, 5), y + rng.uniform(3, 8))], 2.0, cc, opacity=0.25, taper=(0.3, 0.3))
    for _ in range(int((x1 - x0) * (y1 - y0) / 60000) + 2):
        stain(c, rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(20, 60), (50, 20, 40), 0.14, 0, rng.randint(0, 99))


def wainscot(c, x0, x1, y_top, y_bot, col, seed=0, panel_w=150):
    """Wooden wainscot / dado panelling with a rail (flat space)."""
    rng = random.Random(seed)
    c.ink(rect(x0, y_top, x1, y_bot), col, lw=2.6, shade=0.15, hi=0.1, ao=0, tex=0.12, wob=0.5)
    x = x0 + 10
    while x < x1 - 20:
        w = panel_w
        c.ink(rrect(x + 10, y_top + 28, x + w - 10, y_bot - 26, 6), shade_col(col, 0.86), lw=2.0, shade=0.0, hi=0.35,
              hw=4, light=(0.45, 0.89), ao=0.1, tex=0.12, wob=0.6)
        if rng.random() < 0.4:
            scuffs(c, x + 10, x + w - 10, y_bot - 30, 4, seed=rng.randint(0, 999), opacity=0.25, spread=50)
        x += w
    c.ink(rect(x0 - 4, y_top - 14, x1 + 4, y_top + 6), hi_col(col, 0.15), lw=2.6, shade=0.5, sw=6, hi=0.5, hw=3, wob=0.4)
    c.ink(rect(x0 - 4, y_bot - 16, x1 + 4, y_bot), shade_col(col, 0.8), lw=2.4, shade=0.3, hi=0.3, wob=0.4)


def poster(c, x, y, w, h, bg, draw=None, angle=0.0, seed=0, peel=None, tape=(236, 230, 200), torn=0.3):
    """Poster centred at (x, y): wonky paper, content via draw(sub, w, h) in local coords
    (0..w, 0..h), tape, optional curled peeling corner ('tl','tr','bl','br'), folds."""
    rng = random.Random(seed)
    sub = Canvas2(int(w + 40), int(h + 40), lw=c.lw, seed=seed)
    paper = wonky(20, 20, 20 + w, 20 + h, 2.0, rng, 2)
    sub.ink(paper, bg, lw=2.6, shade=0.15, hi=0.15, ao=0.1, tex=0.15, wob=0.6)
    if draw:
        tmp = Canvas2(int(w), int(h), lw=c.lw * 0.8, seed=seed)
        draw(tmp, w, h)
        sub.img.alpha_composite(tmp.img, (20 * S, 20 * S))
        sub.ink(paper, (0, 0, 0, 0), lw=2.6, line_only=True, wob=0.6)
    # fold creases + grime
    sub.stroke([(20 + w * 0.5, 22), (20 + w * 0.5 + rng.uniform(-4, 4), 18 + h)], 1.2, (255, 255, 255), opacity=0.25)
    sub.stroke([(22, 20 + h * 0.5), (18 + w, 20 + h * 0.5 + rng.uniform(-4, 4))], 1.2, (40, 20, 40), opacity=0.18)
    sub.soft(ell(20 + w * rng.uniform(0.2, 0.8), 20 + h * rng.uniform(0.5, 0.9), w * 0.3, h * 0.15), (60, 30, 20), 0.12, 8,
             clip=paper)
    if peel:
        px_ = 20 if "l" in peel else 20 + w
        py_ = 20 if "t" in peel else 20 + h
        sx = 1 if "l" in peel else -1
        sy = 1 if "t" in peel else -1
        s_ = min(w, h) * 0.28
        # cut away the corner and draw it curled
        sub.ink(Sh([[(px_ - sx * 4, py_ - sy * 4), (px_ + sx * s_, py_ - sy * 4), (px_ - sx * 4, py_ + sy * s_)]]),
                (0, 0, 0), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, opacity=1.0)
        sub.img = _erase_corner(sub.img, px_, py_, sx, sy, s_)
        sub.ink(Sh([[(px_ + sx * s_, py_), (px_ + sx * s_ * 0.55, py_ + sy * s_ * 0.55), (px_, py_ + sy * s_)]]),
                hi_col(bg, 0.25), lw=2.2, shade=0.3, sw=6, hi=0.3)
        sub.ink(Sh([[(px_ + sx * s_, py_), (px_ + sx * s_ * 0.55, py_ + sy * s_ * 0.55), (px_ + sx * s_ * 0.95, py_ + sy * s_ * 0.6)]]),
                (236, 228, 214), lw=2.0, shade=0.4, sw=4)
    for tx, ty in ((20 + w * 0.5, 20), ):
        sub.ink(Sh([rot_pts([(tx - 14, ty - 7), (tx + 14, ty - 7), (tx + 14, ty + 7), (tx - 14, ty + 7)], rng.uniform(-12, 12), tx, ty)]),
                tape + (200,), lw=0, shade=0, hi=0, ao=0, tex=0.1, wob=0.5)
    im = sub.img
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    # drop shadow
    a = np.asarray(im.getchannel("A"), np.float32) / 255
    shd = Image.fromarray((blur(a, 4 * S) * 0.35 * 255).astype(np.uint8))
    sh_im = Image.new("RGBA", im.size, (20, 6, 30, 0))
    sh_im.putalpha(shd)
    c.img.alpha_composite(sh_im, (int(x * S - im.width / 2 + 5 * S), int(y * S - im.height / 2 + 7 * S)))
    c.img.alpha_composite(im, (int(x * S - im.width / 2), int(y * S - im.height / 2)))


def _erase_corner(im, px, py, sx, sy, s):
    m = Image.new("L", im.size, 255)
    d = ImageDraw.Draw(m)
    P = [((px - sx * 6) * S, (py - sy * 6) * S), ((px + sx * s) * S, (py - sy * 6) * S), ((px + sx * s) * S, py * S),
         (px * S, (py + sy * s) * S), ((px - sx * 6) * S, (py + sy * s) * S)]
    d.polygon(P, fill=0)
    a = ImageChops_multiply(im.getchannel("A"), m)
    im = im.copy()
    im.putalpha(a)
    return im


def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def night_sky(c, x0, y0, x1, y1, seed=0, top=(30, 18, 70), bot=(150, 50, 130), skyline=True, moon=True):
    """Night sky + city / campus skyline inside a rectangle (for windows)."""
    rng = random.Random(seed)
    clip = rect(x0, y0, x1, y1)
    c.ink(clip, ("vy", y0, y1, top, bot), lw=0, shade=0, hi=0, ao=0, tex=0.05, wob=0)
    for _ in range(int((x1 - x0) * (y1 - y0) / 900)):
        sx, sy = rng.uniform(x0, x1), rng.uniform(y0, y0 + (y1 - y0) * 0.6)
        r = rng.choice([0.9, 1.2, 1.8])
        c.ink(ell(sx, sy, r, r), (255, 250, 220), lw=0, shade=0, hi=0, ao=0, tex=0, wob=0, clip=clip)
    if moon:
        mx, my = x0 + (x1 - x0) * 0.7, y0 + (y1 - y0) * 0.24
        c.glow2(mx, my, (x1 - x0) * 0.4, (255, 220, 255), 0.35)
        c.ink(ell(mx, my, 20, 20), (255, 246, 214), lw=0, shade=0.3, sw=8, scol=(230, 200, 200), hi=0, clip=clip)
        c.ink(ell(mx + 9, my - 6, 17, 17), top, lw=0, shade=0, hi=0, ao=0, clip=clip, tex=0)
    if skyline:
        bx = x0 - 10
        while bx < x1:
            bw = rng.uniform(30, 80)
            bt = y1 - rng.uniform(30, (y1 - y0) * 0.45)
            col = mix((40, 20, 70), bot, 0.15)
            c.ink(rect(bx, bt, bx + bw, y1 + 5), col, lw=0, shade=0, hi=0, ao=0, clip=clip, tex=0)
            if rng.random() < 0.4:
                c.ink(Sh([[(bx, bt), (bx + bw / 2, bt - 22), (bx + bw, bt)]]), col, lw=0, shade=0, hi=0, ao=0, clip=clip, tex=0)
            for wy in np.arange(bt + 8, y1 - 4, 16):
                for wx in np.arange(bx + 6, bx + bw - 8, 13):
                    if rng.random() < 0.4:
                        c.ink(rect(wx, wy, wx + 6, wy + 8), (255, 206, 100), lw=0, shade=0, hi=0, ao=0, clip=clip, tex=0)
            bx += bw + rng.uniform(-4, 8)


def string_lights2(c, pts_list, colors=((255, 90, 150), (255, 220, 90), (60, 220, 210), (180, 120, 255)), spacing=48,
                   sag=40, glow=True, seed=0):
    """Fairy lights strung along sagging wires between consecutive anchor points."""
    rng = random.Random(seed)
    bulbs = []
    for a, b in zip(pts_list, pts_list[1:]):
        p = cable(c, a, b, sag=sag, w=2.4, col=(40, 50, 40), outline=False)
        L = sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))
        n = int(L / spacing)
        for j in range(1, n + 1):
            q = p[int(j / (n + 1) * (len(p) - 1))]
            bulbs.append(q)
    for i, (x, y) in enumerate(bulbs):
        col = colors[i % len(colors)]
        c.ink(rect(x - 2.5, y - 1, x + 2.5, y + 5), (60, 66, 50), lw=1.6, shade=0, hi=0, ao=0)
        c.ink(ell(x + rng.uniform(-1, 1), y + 11, 5, 7.5), col, lw=1.8, shade=0.2, hi=0.5, hw=2, hcol=(255, 255, 240))
        if glow:
            c.glow2(x, y + 11, 34, col, 0.35)
    return bulbs


def book_row(c, x0, x1, y_base, hmin, hmax, rng, cols, lean_last=True, lw=2.0):
    x = x0
    while x < x1 - 8:
        w = rng.uniform(9, 18)
        h = rng.uniform(hmin, hmax)
        col = rng.choice(cols)
        if x + w > x1:
            break
        if lean_last and rng.random() < 0.08 and x + h < x1:
            pts = rot_pts([(x, y_base - h), (x + w, y_base - h), (x + w, y_base), (x, y_base)], 18, x + w, y_base)
            c.ink(Sh([pts]), col, lw=lw, shade=0.4, sw=4, hi=0.3, hw=2, ao=0)
            x += h * 0.32 + w
            continue
        c.ink(rect(x, y_base - h, x + w, y_base), col, lw=lw, shade=0.45, sw=w * 0.35, hi=0.35, hw=w * 0.15, ao=0,
              tex=0.1, wob=0.3)
        if rng.random() < 0.6:
            c.stroke([(x + 2, y_base - h * 0.78), (x + w - 2, y_base - h * 0.78)], 1.4, hi_col(col, 0.5), taper=(0, 0),
                     opacity=0.8)
            c.stroke([(x + 2, y_base - h * 0.25), (x + w - 2, y_base - h * 0.25)], 1.4, hi_col(col, 0.5), taper=(0, 0),
                     opacity=0.8)
        x += w + 0.5


BOOK_COLS = [(200, 60, 90), (60, 160, 170), (230, 170, 60), (120, 70, 160), (70, 110, 190), (220, 110, 70),
             (90, 150, 90), (240, 220, 190)]


def flat_door(c, x0, y0, x1, y1, col, frame=(80, 40, 70), knob="R", window=False, sign=None, seed=0, panels=True):
    """A battered door (flat space, frame included)."""
    rng = random.Random(seed)
    fw = (x1 - x0) * 0.09
    c.ink(rect(x0 - fw, y0 - fw, x1 + fw, y1), frame, lw=2.8, shade=0.4, sw=fw, hi=0.3, tex=0.12)
    c.ink(rect(x0, y0, x1, y1), col, lw=2.8, shade=0.35, sw=(x1 - x0) * 0.25, hi=0.25, tex=0.14)
    if panels:
        for (py0, py1) in ((y0 + (y1 - y0) * 0.06, y0 + (y1 - y0) * 0.44), (y0 + (y1 - y0) * 0.52, y1 - (y1 - y0) * 0.05)):
            if window and py0 < y0 + (y1 - y0) * 0.2:
                continue
            c.ink(rrect(x0 + (x1 - x0) * 0.14, py0, x1 - (x1 - x0) * 0.14, py1, 5), shade_col(col, 0.9), lw=2.0,
                  shade=0.0, hi=0.4, hw=4, light=(0.45, 0.89), ao=0.1)
    if window:
        wx0, wy0, wx1, wy1 = x0 + (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.08, x1 - (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.38
        c.ink(rect(wx0, wy0, wx1, wy1), (120, 200, 210), lw=2.4, shade=0.3, hi=0.4)
        c.stroke([(wx0 + 6, wy1 - 8), (wx0 + (wx1 - wx0) * 0.5, wy0 + 6)], 4, (255, 255, 255), opacity=0.4)
    kx = x1 - (x1 - x0) * 0.12 if knob == "R" else x0 + (x1 - x0) * 0.12
    ky = y0 + (y1 - y0) * 0.55
    c.ink(rrect(kx - 6, ky - 24, kx + 6, ky + 18, 4), (180, 150, 80), lw=2.2, shade=0.4)
    c.ink(ell(kx, ky, 8, 8), (236, 196, 90), lw=2.2, shade=0.4, hi=0.6, hw=3)
    # kick scuffs + scratches
    scuffs(c, x0 + 10, x1 - 30, y1 - 6, 6, seed=seed, opacity=0.3, spread=70)
    for _ in range(4):
        sx_ = rng.uniform(x0 + 10, x1 - 10)
        sy_ = rng.uniform(y0 + 20, y1 - 40)
        c.stroke([(sx_, sy_), (sx_ + rng.uniform(-14, 14), sy_ + rng.uniform(4, 16))], 1.2, hi_col(col, 0.5), opacity=0.5)
    if sign:
        sign(c, (x0 + x1) / 2, y0 + (y1 - y0) * 0.25)


def shelf(c, x0, x1, y, depth=16, col=(130, 80, 60), brackets=True):
    c.ink(rect(x0, y, x1, y + depth * 0.7), col, lw=2.6, shade=0.4, sw=5, hi=0.4, hw=3)
    c.ink(rect(x0 + 3, y - 4, x1 - 3, y + 1), hi_col(col, 0.3), lw=1.8, shade=0, hi=0, ao=0)
    if brackets:
        for bx in (x0 + 20, x1 - 20):
            c.ink(Sh([[(bx - 4, y + depth * 0.7), (bx + 4, y + depth * 0.7), (bx + 4, y + depth * 2.2), (bx - 4, y + depth * 0.9)]]),
                  (90, 90, 100), lw=2.0, shade=0.3)
