"""Shared helpers for the chapter environment generators (cave, drowned,
rootdark, hearth_env): periodic noise, mask-based shape painting, and the
preview compositors that mimic how the Godot level builder lays things out.
"""
import math

from pix import INK, dith, new, outline, ramp_at, rng, save_preview
from tiles import T, U, R, D, L, mask_at

W, H = 480, 270


# ------------------------------------------------------------------ noise ---

def pnoise2(seed, period=64, cells=8, octaves=2):
    """Smooth 2D value noise that wraps exactly at `period` in x and y (0..1)."""
    layers = []
    r = rng(seed)
    for o in range(octaves):
        n = cells * (2 ** o)
        layers.append((n, [[r.random() for _ in range(n)] for _ in range(n)], 0.5 ** o))
    norm = sum(a for _, _, a in layers)

    def smooth(t):
        return t * t * (3 - 2 * t)

    def f(x, y):
        total = 0.0
        for n, grid, amp in layers:
            fx, fy = x / period * n, y / period * n
            x0, y0 = int(math.floor(fx)), int(math.floor(fy))
            tx, ty = smooth(fx - x0), smooth(fy - y0)
            a = grid[y0 % n][x0 % n]
            b = grid[y0 % n][(x0 + 1) % n]
            c = grid[(y0 + 1) % n][x0 % n]
            d = grid[(y0 + 1) % n][(x0 + 1) % n]
            total += amp * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        return total / norm
    return f


# ------------------------------------------------------------------ masks ---

class Mask:
    """Boolean canvas for building silhouettes out of simple primitives."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.m = [[False] * w for _ in range(h)]

    def set(self, x, y, v=True):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.m[y][x] = v

    def get(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.m[y][x]

    def rect(self, x0, y0, x1, y1, v=True):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.set(x, y, v)

    def ellipse(self, cx, cy, rx, ry, v=True):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, v)

    def poly(self, pts, v=True):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            yc = y + 0.5
            xs = []
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b))):
                    self.set(x, y, v)

    def line(self, x0, y0, x1, y1, width=1, v=True):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dy in range(width):
                for dx in range(width):
                    self.set(x - width / 2 + dx + 0.5, y - width / 2 + dy + 0.5, v)


def shade_mask(mask, ramp, lo=0.15, hi=0.85, vertical=0.0, seam=0.0):
    """Paint a mask lit from the left: each horizontal run is shaded from
    `hi` (left edge) to `lo` (right edge) along `ramp`, dithered."""
    img = new(mask.w, mask.h)
    p = img.load()
    for y in range(mask.h):
        x = 0
        while x < mask.w:
            if not mask.m[y][x]:
                x += 1
                continue
            x0 = x
            while x < mask.w and mask.m[y][x]:
                x += 1
            x1 = x - 1
            span = max(1, x1 - x0)
            for xx in range(x0, x1 + 1):
                k = (xx - x0) / span
                t = hi + (lo - hi) * k - vertical * (y / mask.h)
                if xx == x0 and span > 1:
                    t += seam
                p[xx, y] = ramp_at(ramp, t, xx, y)
    return img


def flush_top(img, color):
    """Replace the outline on row 0 so a ceiling prop sits flush."""
    p = img.load()
    for x in range(img.width):
        if p[x, 0] == INK or (p[x, 0][3] and p[x, 0] == color):
            p[x, 0] = color
    return img


# -------------------------------------------------------------- backdrops ---

def vgrad(img, ramp, stops):
    p = img.load()
    for y in range(img.height):
        t = 0.0
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                y0, t0 = stops[i]
                y1, t1 = stops[i + 1]
                t = t0 + (t1 - t0) * (y - y0) / max(1, y1 - y0)
                break
        for x in range(img.width):
            p[x, y] = ramp_at(ramp, t, x, y)


def rim_light(img, rim, below=None, w=None, right=True):
    """Light the open-facing edge of a silhouette layer."""
    w = w or img.width
    q = img.copy().load()
    p = img.load()
    for x in range(w):
        for y in range(img.height):
            if q[x, y][3] == 0:
                continue
            right_open = right and q[(x + 1) % w, y][3] == 0
            below_open = y + 1 < img.height and q[x, y + 1][3] == 0
            above_open = y > 0 and q[x, y - 1][3] == 0
            if below is not None and below_open:
                p[x, y] = below
            elif right_open or (above_open and dith(x, y, 0.35)) or (below_open and dith(x, y, 0.5)):
                p[x, y] = rim


def compose_backdrop(layers, scroll=0, order=(("far", 0.25), ("mid", 0.5), ("near", 1.0))):
    comp = layers["base"].copy()
    for name, k in order:
        if name not in layers:
            continue
        img = layers[name]
        x = int(scroll * k) % img.width
        strip = new(W, H)
        strip.alpha_composite(img.crop((x, 0, min(img.width, x + W), H)), (0, 0))
        if x + W > img.width:
            strip.alpha_composite(img.crop((0, 0, x + W - img.width, H)), (img.width - x, 0))
        comp.alpha_composite(strip)
    return comp


# ---------------------------------------------------------------- preview ---

def is_wall(grid, x, y):
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return False
    return grid[y][x] in "w#"


def compose_scene(ground, wall, backdrop, rows, props=(), wall_mod=(0.52, 0.47, 0.62)):
    h, w = len(rows), len(rows[0])
    img = backdrop.crop((0, 0, w * T, h * T)).copy() if backdrop.width >= w * T else new(w * T, h * T)
    if img.size != (w * T, h * T):
        tmp = new(w * T, h * T, (0, 0, 0, 255))
        tmp.alpha_composite(backdrop.resize((w * T, h * T)))
        img = tmp

    def tile(atlas, col, row):
        return atlas.crop((col * T, row * T, col * T + T, row * T + T))

    def wmask(x, y):
        m = 0
        for bit, (dx, dy) in ((U, (0, -1)), (R, (1, 0)), (D, (0, 1)), (L, (-1, 0))):
            if not is_wall(rows, x + dx, y + dy) and 0 <= y + dy < h and 0 <= x + dx < w:
                m |= bit
        return m

    # wall layer, modulated like level.gd does
    wl = new(w * T, h * T)
    for y in range(h):
        for x in range(w):
            if rows[y][x] == "w":
                wl.alpha_composite(tile(wall, (y % 4) * 4 + x % 4, wmask(x, y)), (x * T, y * T))
    wp = wl.load()
    for y in range(wl.height):
        for x in range(wl.width):
            c = wp[x, y]
            if c[3]:
                wp[x, y] = (int(c[0] * wall_mod[0]), int(c[1] * wall_mod[1]), int(c[2] * wall_mod[2]), c[3])
    img.alpha_composite(wl)
    for (pimg, px, py, top) in props:
        if top:
            img.alpha_composite(pimg, (px * T + 8 - pimg.width // 2, py * T))
        else:
            img.alpha_composite(pimg, (px * T + 8 - pimg.width // 2, (py + 1) * T - pimg.height))
    for y in range(h):
        for x in range(w):
            c = rows[y][x]
            if c == "#":
                m = mask_at(rows, x, y)
                img.alpha_composite(tile(ground, (y % 4) * 4 + x % 4, m), (x * T, y * T))
                if m & U and y > 0:
                    img.alpha_composite(tile(ground, x % 4, 16), (x * T, (y - 1) * T))
                    if m & L and x > 0 and rows[y][x - 1] in ".w":
                        img.alpha_composite(tile(ground, 8, 16), ((x - 1) * T, y * T))
                    if m & R and x < w - 1 and rows[y][x + 1] in ".w":
                        img.alpha_composite(tile(ground, 9, 16), ((x + 1) * T, y * T))
                if m & D and y < h - 1 and rows[y + 1][x] in ".w" and (x * 7 + y) % 3 == 0:
                    img.alpha_composite(tile(ground, 4 + x % 4, 16), (x * T, (y + 1) * T))
            elif c == "=":
                left = rows[y][x - 1] != "="
                right = rows[y][x + 1] != "="
                img.alpha_composite(tile(ground, 0 if left else (3 if right else 1 + x % 2), 17), (x * T, y * T))
    return img


def ingame(img, lights, ambient=(0.42, 0.46, 0.62)):
    """Rough CanvasModulate + additive PointLight2D approximation."""
    out = img.copy()
    p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = p[x, y]
            add = [0.0, 0.0, 0.0]
            for (lx, ly, rad, col, energy) in lights:
                d = math.hypot(x - lx, y - ly) / rad
                if d < 1:
                    a = 1.0 if d < 0.32 else (0.72 if d < 0.55 else (0.45 if d < 0.78 else 0.2))
                    for i in range(3):
                        add[i] += a * col[i] * energy
            p[x, y] = tuple(min(255, int(c[i] * (ambient[i] + add[i]))) for i in range(3)) + (c[3],)
    return out


def scene_backdrop(layers, width, order=(("far", 0.25), ("mid", 0.5), ("near", 1.0))):
    bd = new(width, H, (0, 0, 0, 255))
    bd.alpha_composite(compose_backdrop(layers, 40, order), (0, 0))
    if width > W:
        bd.alpha_composite(compose_backdrop(layers, 520, order).crop((0, 0, width - W, H)), (W, 0))
    return bd


def props_sheet(items, name, height=None, scale=4):
    height = height or max(i.height for i in items) + 4
    sheet_img = new(sum(i.width + 4 for i in items) + 4, height)
    x = 2
    for img in items:
        sheet_img.alpha_composite(img, (x, height - 2 - img.height))
        x += img.width + 4
    save_preview(sheet_img, name, scale)


def deco_rows_preview(atlas, name):
    row = atlas.crop((0, 15 * T, 256, 18 * T))
    save_preview(row, name, 4)


def pad_rows(rows, fill="#"):
    tw = max(len(r) for r in rows)
    return [r.ljust(tw, fill) for r in rows]
